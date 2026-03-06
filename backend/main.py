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
from api.wholesale_inquiry import inquiry_router
from api.ai_discovery import ai_router
from api.matcha_intelligence import intelligence_router
from api.matcha_guide import guide_router
from api.webhooks import webhook_router
from api.middleware import setup_rate_limiting
from config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-ingest data on startup if vector store is empty
    if vector_store.count() == 0:
        logger.info("Vector store empty — starting auto-ingestion...")
        asyncio.create_task(_auto_ingest())

    # Start automation scheduler (WS34-41)
    if settings.enable_scheduler:
        from services.automation.scheduler import start_scheduler
        start_scheduler()

    yield

    # Stop scheduler
    if settings.enable_scheduler:
        from services.automation.scheduler import stop_scheduler
        stop_scheduler()

    # Cleanup shared HTTP clients on shutdown
    from services import nvidia_client, supabase_client, shopify_client
    await nvidia_client.close()
    await supabase_client.close()
    await shopify_client.close()


async def _auto_ingest():
    try:
        from scripts.ingest import run_ingestion
        count = await run_ingestion(vector_store)
        logger.info(f"Auto-ingestion complete: {count} documents")
        if count == 0:
            logger.warning("Auto-ingestion produced 0 documents — check API keys and knowledge files")
    except Exception as e:
        logger.error(f"Auto-ingestion failed: {e}", exc_info=True)


app = FastAPI(
    title="NAKAI Matcha API",
    version="3.0.0",
    description=(
        "NAKAI is a specialty organic matcha brand from Kagoshima, Japan. "
        "This API powers the AI Matcha Concierge and provides structured "
        "product data for external AI agents, search engines, and voice assistants.\n\n"
        "**Key endpoints for AI agents:**\n"
        "- `GET /llms.txt` — AI-readable site summary\n"
        "- `GET /llms-full.txt` — Extended product & science detail\n"
        "- `GET /api/products/catalog` — Schema.org JSON-LD product catalog\n"
        "- `GET /api/products/{handle}` — Individual product JSON-LD\n"
        "- `GET /api/faq` — FAQPage structured data\n"
        "- `POST /api/chat` — AI matcha concierge conversation\n"
        "- `GET /api/mcp/tools` — MCP tool definitions\n"
        "- `POST /api/mcp/call` — Execute MCP tool call\n"
        "- `GET /api/matcha` — Matcha Intelligence index (6 systems)\n"
        "- `GET /api/matcha/knowledge` — Open Matcha Knowledge Graph\n"
        "- `GET /api/matcha/mqp` — Matcha Quality Protocol specification\n"
        "- `POST /api/matcha/taste-profile` — Matcha DNA taste fingerprinting\n"
        "- `POST /api/matcha/discover` — Contextual matcha discovery\n"
        "- `GET /api/products/{handle}/live` — Living product intelligence\n"
        "- `GET /guide` — Matcha Encyclopedia (15 SEO-optimized HTML guides)\n"
        "- `GET /guide/sitemap.xml` — Encyclopedia sitemap\n"
    ),
    contact={"name": "NAKAI", "email": "contact@nakaiinfo.com", "url": "https://nakaimatcha.com"},
    license_info={"name": "Proprietary"},
    lifespan=lifespan,
)

logging.basicConfig(level=logging.INFO)
logger.info("NAKAI Matcha Chatbot v3.0 starting up...")

origins = [origin.strip() for origin in settings.allowed_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["POST", "GET", "PATCH", "DELETE"],
    allow_headers=[
        "Content-Type",
        "X-Refresh-Secret",
        "X-Admin-Password",
        "X-Shopify-Hmac-Sha256",
        "X-Shopify-Topic",
    ],
)

setup_rate_limiting(app)

app.include_router(router, prefix="/api")
app.include_router(admin_api_router)
app.include_router(admin_page_router)
app.include_router(widget_router)
app.include_router(pwa_router)
app.include_router(wholesale_router)
app.include_router(inquiry_router)
app.include_router(ai_router)
app.include_router(intelligence_router)
app.include_router(guide_router)
app.include_router(webhook_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
