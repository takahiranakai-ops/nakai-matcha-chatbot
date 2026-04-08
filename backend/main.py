import asyncio
import hashlib
import logging
import secrets
import time

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response as StarletteResponse

from api.routes import router, vector_store, rag_engine
from api.widget import widget_router
from api.pwa import pwa_router
from api.admin_routes import admin_api_router
from api.admin_page import admin_page_router
from api.wholesale import wholesale_router
from api.wholesale_inquiry import inquiry_router
from api.contact_inquiry import contact_inquiry_router
from api.ai_discovery import ai_router, LLMS_TXT
from api.matcha_intelligence import intelligence_router
from api.matcha_guide import guide_router
from api.webhooks import webhook_router
from api.mcp_sse import mcp_sse_router
from api.command_center import command_center_router
from api.email_routes import email_router
from api.email_page import email_page_router
from api.daily_tips_routes import tips_router
from api.b2b_routes import b2b_router
from api.b2b_page import b2b_page_router
from api.operations import operations_router
from api.marketing_routes import marketing_router
from api.design_routes import design_router
from api.dashboard import dashboard_router
from api.ops_chat_routes import ops_chat_router
from api.middleware import setup_rate_limiting
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Session token store (in-memory, server-side only) ──
_SESSION_TOKENS: dict[str, float] = {}  # token -> expiry timestamp
_TOKEN_TTL = 86400  # 24 hours


def create_session_token(password: str) -> str:
    """Create a signed session token from admin password."""
    raw = f"{password}:{secrets.token_hex(16)}:{time.time()}"
    token = hashlib.sha256(raw.encode()).hexdigest()
    _SESSION_TOKENS[token] = time.time() + _TOKEN_TTL
    # Cleanup expired tokens
    now = time.time()
    expired = [t for t, exp in _SESSION_TOKENS.items() if exp < now]
    for t in expired:
        _SESSION_TOKENS.pop(t, None)
    return token


def validate_session_token(token: str) -> bool:
    """Check if a session token is valid and not expired."""
    expiry = _SESSION_TOKENS.get(token)
    if not expiry:
        return False
    if time.time() > expiry:
        _SESSION_TOKENS.pop(token, None)
        return False
    return True


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Security: refuse default passwords in production
    _defaults = {
        "admin_password": "change-me-admin",
        "wholesale_password": "change-me-wholesale",
        "refresh_secret": "change-me",
    }
    insecure = [k for k, v in _defaults.items() if getattr(settings, k, None) == v]
    if insecure:
        if settings.debug:
            logger.warning("Default credentials in use: %s — change via environment variables", ", ".join(insecure))
        else:
            raise RuntimeError(
                f"CRITICAL: Default credentials detected: {', '.join(insecure)}. "
                "Set secure passwords via environment variables before running in production."
            )

    # Validate critical settings on startup
    if not settings.ngc_api_key:
        logger.error("CRITICAL: NVIDIA NGC API key not set — chat will fail")
    if not settings.supabase_url:
        logger.warning("Supabase not configured — analytics disabled")
    if not settings.mcp_api_key:
        logger.warning("MCP_API_KEY not set — MCP SSE endpoint disabled (OpenFang cannot connect)")
    else:
        logger.info("MCP SSE endpoint enabled — OpenFang/agents can connect via /mcp/sse")

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
        "- `GET /guide` — Matcha Encyclopedia (16 SEO-optimized HTML guides)\n"
        "- `GET /guide/sitemap.xml` — Encyclopedia sitemap\n"
        "- `GET /mcp/sse` — MCP SSE transport (Bearer auth required)\n"
    ),
    contact={"name": "NAKAI", "email": "contact@nakaiinfo.com", "url": "https://nakaimatcha.com"},
    license_info={"name": "Proprietary"},
    lifespan=lifespan,
)

logger.info("NAKAI Matcha Chatbot v3.0 starting up...")

origins = [origin.strip() for origin in settings.allowed_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET", "PATCH", "DELETE"],
    allow_headers=[
        "Content-Type",
        "X-Refresh-Secret",
        "X-Admin-Password",
        "X-Shopify-Hmac-Sha256",
        "X-Shopify-Topic",
        "Authorization",
    ],
)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.resend.com https://*.supabase.co; "
            "frame-ancestors 'none'"
        )
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


app.add_middleware(SecurityHeadersMiddleware)

setup_rate_limiting(app)


@app.middleware("http")
async def well_known_llms_middleware(request, call_next):
    """Serve /.well-known/llms.txt via middleware (FastAPI routing fails for this path)."""
    if request.url.path == "/.well-known/llms.txt":
        return PlainTextResponse(
            content=LLMS_TXT,
            media_type="text/plain; charset=utf-8",
            headers={"Cache-Control": "public, max-age=86400", "X-Robots-Tag": "all"},
        )
    return await call_next(request)


app.include_router(router, prefix="/api")
app.include_router(admin_api_router)
app.include_router(admin_page_router)
app.include_router(widget_router)
app.include_router(pwa_router)
app.include_router(wholesale_router)
app.include_router(inquiry_router)
app.include_router(contact_inquiry_router)
app.include_router(ai_router)
app.include_router(intelligence_router)
app.include_router(guide_router)
app.include_router(webhook_router)
app.include_router(mcp_sse_router)
app.include_router(command_center_router)
app.include_router(email_router)
app.include_router(email_page_router)
app.include_router(tips_router)
app.include_router(b2b_router)
app.include_router(b2b_page_router)
app.include_router(operations_router)
app.include_router(marketing_router)
app.include_router(design_router)
app.include_router(dashboard_router)
app.include_router(ops_chat_router)


@app.get("/")
async def root_redirect():
    """Redirect root to Barista Hub (wholesale portal)."""
    return RedirectResponse(url="/wholesale", status_code=302)


@app.get("/health")
async def health_check():
    return {"status": "ok", "v": "3.0.1"}
