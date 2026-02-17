import asyncio
import logging

from fastapi import APIRouter, HTTPException, Header, Request
from api.models import ChatRequest, ChatResponse, RefreshResponse
from api.middleware import limiter
from services.rag_engine import RAGEngine
from services.vector_store import VectorStore
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


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("20/minute")
async def chat(request: Request, body: ChatRequest):
    try:
        result = await rag_engine.answer(
            user_message=body.message,
            conversation_history=body.history,
            language=body.language,
        )
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
