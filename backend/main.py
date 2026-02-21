import asyncio
import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router, vector_store, rag_engine
from api.widget import widget_router
from api.pwa import pwa_router
from api.admin_routes import admin_api_router
from api.admin_page import admin_page_router
from api.wholesale import wholesale_router
from api.middleware import setup_rate_limiting
from config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-ingest data on startup if vector store is empty
    if vector_store.count() == 0:
        logger.info("Vector store empty — starting auto-ingestion...")
        asyncio.create_task(_auto_ingest())
    yield


async def _auto_ingest():
    try:
        from scripts.ingest import run_ingestion
        count = await run_ingestion(vector_store)
        logger.info(f"Auto-ingestion complete: {count} documents")
    except Exception as e:
        logger.error(f"Auto-ingestion failed: {e}")


app = FastAPI(title="NAKAI Matcha Chatbot API", version="1.0.0", lifespan=lifespan)

logging.basicConfig(level=logging.INFO)
logger.info("NAKAI Matcha Chatbot starting up...")

origins = [origin.strip() for origin in settings.allowed_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["POST", "GET", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "X-Refresh-Secret", "X-Admin-Password"],
)

setup_rate_limiting(app)

app.include_router(router, prefix="/api")
app.include_router(admin_api_router)
app.include_router(admin_page_router)
app.include_router(widget_router)
app.include_router(pwa_router)
app.include_router(wholesale_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
