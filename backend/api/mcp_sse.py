"""MCP SSE Transport — Authenticated MCP server for OpenFang and AI agents.

Exposes NAKAI's 8 tools + 11 resources via standard MCP SSE protocol.
Security: Bearer token authentication, rate limiting, request logging.
"""

import hmac
import json
import logging
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request, Response
from starlette.responses import StreamingResponse

from config import settings
from mcp_server import (
    get_mcp_tools,
    get_mcp_resources,
    handle_mcp_tool_call,
    read_mcp_resource,
)

logger = logging.getLogger(__name__)

mcp_sse_router = APIRouter(tags=["MCP SSE"])

# Active SSE sessions: session_id -> message queue
_sessions: dict[str, list] = {}

# Rate limiting: track requests per IP
_request_counts: dict[str, list[float]] = {}
_MAX_REQUESTS_PER_MINUTE = 60


def _verify_auth(request: Request) -> Optional[str]:
    """Verify Bearer token authentication. Returns error message or None."""
    if not settings.mcp_api_key:
        logger.warning("MCP_API_KEY not set — MCP SSE endpoint is DISABLED")
        return "MCP endpoint not configured"

    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        return "Missing Bearer token"

    token = auth_header[7:]
    if not hmac.compare_digest(token, settings.mcp_api_key):
        return "Invalid API key"

    return None


def _rate_limit(request: Request) -> Optional[str]:
    """Simple rate limiting. Returns error message or None."""
    import time

    client_ip = request.client.host if request.client else "unknown"
    now = time.time()

    if client_ip not in _request_counts:
        _request_counts[client_ip] = []

    # Remove entries older than 60 seconds
    _request_counts[client_ip] = [
        t for t in _request_counts[client_ip] if now - t < 60
    ]

    if len(_request_counts[client_ip]) >= _MAX_REQUESTS_PER_MINUTE:
        return "Rate limit exceeded"

    _request_counts[client_ip].append(now)
    return None


def _jsonrpc_response(id: Optional[str], result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": id, "result": result}


def _jsonrpc_error(id: Optional[str], code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": id, "error": {"code": code, "message": message}}


@mcp_sse_router.get("/mcp/sse")
async def mcp_sse_connect(request: Request):
    """SSE endpoint — clients connect here to receive MCP messages."""
    # Auth check
    auth_error = _verify_auth(request)
    if auth_error:
        logger.warning(f"MCP SSE auth failed: {auth_error} from {request.client.host if request.client else 'unknown'}")
        return Response(
            content=json.dumps({"error": auth_error}),
            status_code=401,
            media_type="application/json",
        )

    # Rate limit
    rate_error = _rate_limit(request)
    if rate_error:
        return Response(
            content=json.dumps({"error": rate_error}),
            status_code=429,
            media_type="application/json",
        )

    session_id = str(uuid.uuid4())
    _sessions[session_id] = []

    logger.info(f"MCP SSE session opened: {session_id}")

    async def event_stream():
        import asyncio

        # Send endpoint URL for the client to POST messages to
        messages_url = f"/mcp/messages?session_id={session_id}"
        yield f"event: endpoint\ndata: {messages_url}\n\n"

        try:
            while True:
                if await request.is_disconnected():
                    break

                # Check for queued messages
                if session_id in _sessions and _sessions[session_id]:
                    msg = _sessions[session_id].pop(0)
                    yield f"event: message\ndata: {json.dumps(msg)}\n\n"
                else:
                    await asyncio.sleep(0.1)
        finally:
            _sessions.pop(session_id, None)
            logger.info(f"MCP SSE session closed: {session_id}")

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@mcp_sse_router.post("/mcp/messages")
async def mcp_messages(request: Request):
    """Handle MCP JSON-RPC messages from clients."""
    # Auth check
    auth_error = _verify_auth(request)
    if auth_error:
        return Response(
            content=json.dumps({"error": auth_error}),
            status_code=401,
            media_type="application/json",
        )

    # Rate limit
    rate_error = _rate_limit(request)
    if rate_error:
        return Response(
            content=json.dumps({"error": rate_error}),
            status_code=429,
            media_type="application/json",
        )

    session_id = request.query_params.get("session_id")
    if not session_id or session_id not in _sessions:
        return Response(
            content=json.dumps({"error": "Invalid or expired session"}),
            status_code=400,
            media_type="application/json",
        )

    try:
        body = await request.json()
    except Exception:
        return Response(
            content=json.dumps({"error": "Invalid JSON"}),
            status_code=400,
            media_type="application/json",
        )

    method = body.get("method", "")
    msg_id = body.get("id")
    params = body.get("params", {})

    logger.info(f"MCP request: {method} (session: {session_id[:8]}...)")

    # Handle MCP JSON-RPC methods
    if method == "initialize":
        response = _jsonrpc_response(msg_id, {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {"listChanged": False},
                "resources": {"subscribe": False, "listChanged": False},
            },
            "serverInfo": {
                "name": "nakai-matcha-mcp",
                "version": "3.0.0",
            },
        })

    elif method == "notifications/initialized":
        # Client acknowledgment — no response needed
        return Response(status_code=204)

    elif method == "tools/list":
        tools = get_mcp_tools()
        response = _jsonrpc_response(msg_id, {"tools": tools})

    elif method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        logger.info(f"MCP tool call: {tool_name}({json.dumps(arguments)[:200]})")
        try:
            result_text = handle_mcp_tool_call(tool_name, arguments)
            response = _jsonrpc_response(msg_id, {
                "content": [{"type": "text", "text": result_text}],
            })
        except Exception as e:
            logger.error(f"MCP tool call failed: {e}")
            response = _jsonrpc_error(msg_id, -32000, str(e))

    elif method == "resources/list":
        resources = get_mcp_resources()
        response = _jsonrpc_response(msg_id, {"resources": resources})

    elif method == "resources/read":
        uri = params.get("uri", "")
        logger.info(f"MCP resource read: {uri}")
        try:
            content = read_mcp_resource(uri)
            response = _jsonrpc_response(msg_id, {
                "contents": [{
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": content,
                }],
            })
        except Exception as e:
            logger.error(f"MCP resource read failed: {e}")
            response = _jsonrpc_error(msg_id, -32000, str(e))

    elif method == "ping":
        response = _jsonrpc_response(msg_id, {})

    else:
        response = _jsonrpc_error(msg_id, -32601, f"Method not found: {method}")

    # Queue the response for SSE delivery
    _sessions[session_id].append(response)

    return Response(status_code=202)
