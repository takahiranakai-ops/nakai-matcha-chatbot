"""AI Ops Chat API — POST /api/ops/chat."""

import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from api.admin_routes import verify_admin

logger = logging.getLogger(__name__)

ops_chat_router = APIRouter(prefix="/api/ops", tags=["ops-chat"])


class OpsChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str = Field(default="")
    history: list[dict] = Field(default_factory=list)


@ops_chat_router.post("/chat")
async def ops_chat(body: OpsChatRequest, _auth: bool = Depends(verify_admin)):
    """Process an ops chat message through the Claude tool-use agent."""
    from services.ops_agent import run_ops_chat

    events = []
    response_text = ""
    messages_out = []

    async for event in run_ops_chat(message=body.message, history=body.history):
        events.append(event)
        if event["type"] == "done":
            response_text = event.get("response", "")
            messages_out = event.get("messages", [])

    # Serialize messages for client (convert Anthropic objects to dicts)
    serialized = _serialize_messages(messages_out)

    return {
        "response": response_text,
        "events": [e for e in events if e["type"] != "done"],
        "messages": serialized,
    }


def _serialize_messages(messages: list) -> list[dict]:
    """Convert Claude API message objects to JSON-serializable dicts."""
    out = []
    for msg in messages:
        if isinstance(msg, dict):
            content = msg.get("content")
            # Handle tool_result lists (already dicts)
            if isinstance(content, list) and content and isinstance(content[0], dict):
                out.append(msg)
                continue
            # Handle Anthropic ContentBlock lists
            if isinstance(content, list):
                blocks = []
                for block in content:
                    if hasattr(block, "type"):
                        if block.type == "text":
                            blocks.append({"type": "text", "text": block.text})
                        elif block.type == "tool_use":
                            blocks.append({
                                "type": "tool_use",
                                "id": block.id,
                                "name": block.name,
                                "input": block.input,
                            })
                    else:
                        blocks.append(block)
                out.append({"role": msg["role"], "content": blocks})
            else:
                out.append(msg)
        else:
            out.append(msg)
    return out
