from fastapi import APIRouter, HTTPException, Header, Request
from api.models import ChatRequest, ChatResponse, RefreshResponse
from api.middleware import limiter
from services.rag_engine import RAGEngine
from services.vector_store import VectorStore
from config import settings

router = APIRouter()

vector_store = VectorStore(settings.chroma_persist_dir)
rag_engine = RAGEngine(vector_store)


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
    }


@router.post("/refresh", response_model=RefreshResponse)
@limiter.limit("1/hour")
async def refresh(
    request: Request,
    x_refresh_secret: str = Header(...),
):
    if x_refresh_secret != settings.refresh_secret:
        raise HTTPException(status_code=403, detail="Invalid refresh secret")

    from scripts.ingest import run_ingestion

    count = await run_ingestion(vector_store)
    return RefreshResponse(status="ok", documents_indexed=count)
