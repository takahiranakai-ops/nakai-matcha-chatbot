"""WS41: Sitemap Ping + IndexNow — Instant indexing.

Pings search engines and IndexNow API when content changes:
- Google Sitemap Ping
- Bing Sitemap Ping
- IndexNow API (Bing, Yandex, Naver instant crawl)

Triggered by WS34 (webhook) + WS38 (weekly refresh).
"""

import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

SITEMAP_URL = "https://nakaimatcha.com/sitemap.xml"
SITE_HOST = "nakaimatcha.com"


async def _ping_google():
    """Ping Google with updated sitemap."""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://www.google.com/ping",
                params={"sitemap": SITEMAP_URL},
            )
            logger.info(f"Google ping: {resp.status_code}")
    except Exception as e:
        logger.error(f"Google ping failed: {e}")


async def _ping_bing():
    """Ping Bing with updated sitemap."""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://www.bing.com/ping",
                params={"sitemap": SITEMAP_URL},
            )
            logger.info(f"Bing ping: {resp.status_code}")
    except Exception as e:
        logger.error(f"Bing ping failed: {e}")


async def _indexnow(urls: Optional[list[str]] = None, api_key: Optional[str] = None):
    """Submit URLs via IndexNow for instant indexing on Bing, Yandex, Naver."""
    if not api_key:
        from config import settings
        api_key = getattr(settings, "indexnow_api_key", "")

    if not api_key:
        logger.info("INDEXNOW_API_KEY not set — skipping IndexNow")
        return

    if not urls:
        urls = [
            f"https://{SITE_HOST}/",
            f"https://{SITE_HOST}/collections/all",
            f"https://{SITE_HOST}/pages/about",
        ]

    payload = {
        "host": SITE_HOST,
        "key": api_key,
        "urlList": urls[:10000],  # IndexNow max 10k per request
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                "https://api.indexnow.org/IndexNow",
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            logger.info(f"IndexNow submission: {resp.status_code} ({len(urls)} URLs)")
    except Exception as e:
        logger.error(f"IndexNow submission failed: {e}")


async def ping_all(urls: Optional[list[str]] = None):
    """Ping all search engines and IndexNow."""
    logger.info("Sitemap ping starting...")
    await _ping_google()
    await _ping_bing()
    await _indexnow(urls)
    logger.info("Sitemap ping complete")
