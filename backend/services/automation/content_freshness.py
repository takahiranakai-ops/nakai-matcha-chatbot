"""WS38: Content Freshness Manager — Weekly content regeneration.

Refreshes AI-facing content to maintain freshness signals:
1. Re-fetches product data from Shopify
2. Regenerates llms.txt / llms-full.txt cached content
3. Re-indexes vector store
4. Ensures Perplexity's extreme freshness bias is satisfied

Runs weekly (Wednesday 3am) + on webhook trigger.
"""

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


async def refresh_ai_content():
    """Refresh all AI-facing content from Shopify source data."""
    logger.info("Content freshness refresh starting...")

    # 1. Re-ingest knowledge base
    try:
        from api.routes import vector_store
        from scripts.ingest import run_ingestion
        count = await run_ingestion(vector_store)
        logger.info(f"Knowledge re-ingestion: {count} documents")
    except Exception as e:
        logger.error(f"Knowledge re-ingestion failed: {e}")

    # 2. Ping sitemaps to notify search engines of updates
    try:
        from services.automation.sitemap_ping import ping_all
        await ping_all()
    except Exception as e:
        logger.error(f"Sitemap ping failed: {e}")

    logger.info(
        f"Content freshness refresh complete at "
        f"{datetime.now(timezone.utc).isoformat()}"
    )
