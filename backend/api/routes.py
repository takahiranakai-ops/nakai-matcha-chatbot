import asyncio
import logging
import time

from fastapi import APIRouter, HTTPException, Header, Request
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
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "model": settings.nvidia_chat_model,
        "documents": vector_store.count(),
        "refresh_running": _refresh_running,
    }


@router.post("/refresh", response_model=RefreshResponse)
@limiter.limit("5/hour")
async def refresh(
    request: Request,
    x_refresh_secret: str = Header(...),
):
    global _refresh_running

    if x_refresh_secret != settings.refresh_secret:
        raise HTTPException(status_code=403, detail="Invalid refresh secret")

    if _refresh_running:
        return RefreshResponse(status="already_running", documents_indexed=vector_store.count())

    _refresh_running = True
    asyncio.create_task(_run_ingestion_background())

    return RefreshResponse(status="started", documents_indexed=vector_store.count())
