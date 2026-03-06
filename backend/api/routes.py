import asyncio
import hmac
import json
import logging
import time

import httpx
from fastapi import APIRouter, HTTPException, Header, Request
from fastapi.responses import StreamingResponse
from api.models import ChatRequest, ChatResponse, RefreshResponse
from api.middleware import limiter
from services.rag_engine import RAGEngine
from services.vector_store import VectorStore
from services import supabase_client
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

vector_store = VectorStore(settings.chroma_persist_dir)
rag_engine = RAGEngine(vector_store)

_refresh_running = False
_refresh_lock = asyncio.Lock()


async def _run_ingestion_background():
    global _refresh_running
    try:
        from scripts.ingest import run_ingestion
        count = await run_ingestion(vector_store)
        logger.info(f"Ingestion complete: {count} documents")
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
    finally:
        _refresh_running = False


async def _log_chat_exchange(
    session_id: str,
    source: str,
    language: str,
    user_agent: str,
    referrer: str,
    user_message: str,
    assistant_response: str,
    sources: list[str],
    context_chunks: int,
    response_time_ms: int,
):
    """Non-blocking task to log a chat exchange to Supabase."""
    try:
        conv = await supabase_client.get_conversation_by_session(session_id, source)
        if not conv:
            conv = await supabase_client.create_conversation(
                session_id=session_id,
                source=source,
                language=language,
                user_agent=user_agent,
                referrer=referrer,
            )
        if not conv:
            return

        conv_id = conv["id"]
        await supabase_client.log_message(
            conversation_id=conv_id,
            role="user",
            content=user_message,
            language=language,
        )
        await supabase_client.log_message(
            conversation_id=conv_id,
            role="assistant",
            content=assistant_response,
            language=language,
            sources=sources,
            context_chunks=context_chunks,
            response_time_ms=response_time_ms,
        )
    except Exception as e:
        logger.warning(f"Chat logging failed (non-critical): {e}")


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("20/minute")
async def chat(request: Request, body: ChatRequest):
    try:
        start_time = time.time()

        result = await rag_engine.answer(
            user_message=body.message,
            conversation_history=body.history,
            language=body.language,
            source=body.source,
        )

        elapsed_ms = int((time.time() - start_time) * 1000)

        # Non-blocking: fire-and-forget logging to Supabase
        if body.session_id:
            asyncio.create_task(_log_chat_exchange(
                session_id=body.session_id,
                source=body.source,
                language=body.language,
                user_agent=request.headers.get("user-agent", ""),
                referrer=request.headers.get("referer", ""),
                user_message=body.message,
                assistant_response=result["response"],
                sources=result["sources"],
                context_chunks=result.get("context_chunks", 0),
                response_time_ms=elapsed_ms,
            ))

        return ChatResponse(
            response=result["response"],
            sources=result["sources"],
            suggestions=result.get("suggestions", []),
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Something went wrong. Please try again.")


@router.post("/chat/stream")
@limiter.limit("20/minute")
async def chat_stream(request: Request, body: ChatRequest):
    start_time = time.time()

    async def event_generator():
        full_response = []
        final_meta = {}
        try:
            async for event_type, data in rag_engine.answer_stream(
                user_message=body.message,
                conversation_history=body.history,
                language=body.language,
                source=body.source,
            ):
                if event_type == "text":
                    full_response.append(data)
                    yield f"data: {json.dumps({'type': 'text', 'content': data})}\n\n"
                elif event_type == "done":
                    final_meta = data
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'content': 'Something went wrong. Please try again.'})}\n\n"

        yield f"data: {json.dumps({'type': 'done', 'sources': final_meta.get('sources', []), 'suggestions': final_meta.get('suggestions', [])})}\n\n"

        # Non-blocking logging
        elapsed_ms = int((time.time() - start_time) * 1000)
        response_text = "".join(full_response)
        if body.session_id:
            asyncio.create_task(_log_chat_exchange(
                session_id=body.session_id,
                source=body.source,
                language=body.language,
                user_agent=request.headers.get("user-agent", ""),
                referrer=request.headers.get("referer", ""),
                user_message=body.message,
                assistant_response=response_text,
                sources=final_meta.get("sources", []),
                context_chunks=0,
                response_time_ms=elapsed_ms,
            ))

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "model": settings.nvidia_chat_model,
        "documents": vector_store.count(),
        "refresh_running": _refresh_running,
    }


@router.get("/health/nvidia")
@limiter.limit("10/minute")
async def health_nvidia(request: Request):
    """Diagnose NVIDIA NIM API connectivity — tests embedding + chat."""
    diag: dict = {"api_key_set": bool(settings.ngc_api_key)}
    headers = {"Authorization": f"Bearer {settings.ngc_api_key}", "Content-Type": "application/json"}

    # Test embedding
    try:
        async with httpx.AsyncClient(timeout=15.0) as c:
            r = await c.post(
                f"{settings.nvidia_base_url}/embeddings",
                headers=headers,
                json={"model": settings.nvidia_embed_model, "input": ["test"], "input_type": "query", "encoding_format": "float", "truncate": "END"},
            )
            diag["embedding_status"] = r.status_code
            if r.status_code != 200:
                logger.error(f"NVIDIA embedding error: {r.text[:500]}")
                diag["embedding_error"] = f"HTTP {r.status_code}"
            else:
                diag["embedding_ok"] = True
    except Exception as e:
        diag["embedding_error"] = str(e)

    # Test chat completion
    try:
        async with httpx.AsyncClient(timeout=30.0) as c:
            r = await c.post(
                f"{settings.nvidia_base_url}/chat/completions",
                headers=headers,
                json={"model": settings.nvidia_chat_model, "messages": [{"role": "user", "content": "Say hello in one word"}], "max_tokens": 10, "stream": False},
            )
            diag["chat_status"] = r.status_code
            if r.status_code != 200:
                logger.error(f"NVIDIA chat error: {r.text[:500]}")
                diag["chat_error"] = f"HTTP {r.status_code}"
            else:
                diag["chat_ok"] = True
                diag["chat_response"] = r.json().get("choices", [{}])[0].get("message", {}).get("content", "")[:100]
    except Exception as e:
        diag["chat_error"] = str(e)

    return diag


@router.post("/refresh", response_model=RefreshResponse)
@limiter.limit("5/hour")
async def refresh(
    request: Request,
    x_refresh_secret: str = Header(...),
):
    global _refresh_running

    if not hmac.compare_digest(x_refresh_secret, settings.refresh_secret):
        raise HTTPException(status_code=403, detail="Invalid refresh secret")

    async with _refresh_lock:
        if _refresh_running:
            return RefreshResponse(status="already_running", documents_indexed=vector_store.count())
        _refresh_running = True
        asyncio.create_task(_run_ingestion_background())
    return RefreshResponse(status="started", documents_indexed=vector_store.count())
