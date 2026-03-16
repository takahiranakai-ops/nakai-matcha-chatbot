"""WS38: Content Freshness Manager — Bi-weekly content regeneration.

Refreshes AI-facing content to maintain freshness signals:
1. Re-indexes vector store with latest knowledge
2. Updates feed timestamps for AI crawlers
3. Warms AI discovery endpoint caches
4. Pings sitemaps to trigger re-crawling

Runs bi-weekly (Wednesday + Saturday 03:00 UTC) + on webhook trigger.
Perplexity's extreme freshness bias requires updates every 2-3 days for
competitive topics.
"""

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

_BASE = "https://nakai-matcha-chat.onrender.com"

# AI discovery endpoints to warm after refresh
_WARM_PATHS = [
    "/llms.txt",
    "/llms-full.txt",
    "/api/products/feed",
    "/api/products/google-feed.xml",
    "/api/products/catalog",
    "/api/products/catalog.json",
]


async def refresh_ai_content():
    """Refresh all AI-facing content from source data."""
    logger.info("Content freshness refresh starting...")

    # 1. Re-ingest knowledge base
    try:
        from api.routes import vector_store
        from scripts.ingest import run_ingestion
        count = await run_ingestion(vector_store)
        logger.info(f"Knowledge re-ingestion: {count} documents")
    except Exception as e:
        logger.error(f"Knowledge re-ingestion failed: {e}")

    # 2. Warm AI discovery endpoint caches
    try:
        import httpx
        async with httpx.AsyncClient(timeout=30) as client:
            for path in _WARM_PATHS:
                try:
                    resp = await client.get(f"{_BASE}{path}")
                    logger.info(f"Cache warm {path}: {resp.status_code}")
                except Exception as e:
                    logger.warning(f"Cache warm {path} failed: {e}")
    except ImportError:
        logger.warning("httpx not available — skipping cache warming")
    except Exception as e:
        logger.error(f"Cache warming failed: {e}")

    # 3. Ping sitemaps to notify search engines of updates
    try:
        from services.automation.sitemap_ping import ping_all
        await ping_all()
    except Exception as e:
        logger.error(f"Sitemap ping failed: {e}")

    logger.info(
        f"Content freshness refresh complete at "
        f"{datetime.now(timezone.utc).isoformat()}"
    )
