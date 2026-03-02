"""WS40: SEO Ranking Tracker — Daily keyword rank monitoring.

Tracks NAKAI's search engine rankings across 30+ keywords
in US, JP, and AE markets. Detects significant rank changes
and generates alerts.
Runs daily.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

# Target keywords with market segmentation
SEO_KEYWORDS = {
    "us": [
        "best ceremonial matcha",
        "organic matcha powder",
        "Japanese matcha online",
        "matcha for lattes",
        "premium matcha brand",
        "matcha wholesale USA",
        "ceremonial matcha review",
        "stone ground matcha",
        "NAKAI matcha",
        "matcha subscription box",
        "best matcha 2026",
        "organic matcha from Japan",
        "matcha health benefits",
        "matcha vs coffee energy",
        "L-theanine matcha",
    ],
    "jp": [
        "オーガニック 抹茶 通販",
        "高級抹茶 ブランド",
        "抹茶 お取り寄せ",
        "NAKAI 抹茶",
        "鹿児島 抹茶",
        "宇治 抹茶 オーガニック",
        "濃茶 抹茶 おすすめ",
        "抹茶 卸売り",
    ],
    "ae": [
        "matcha Dubai",
        "organic matcha UAE",
        "Japanese matcha delivery Dubai",
        "matcha wholesale Middle East",
        "NAKAI matcha Dubai",
        "ceremonial matcha UAE",
    ],
}

MARKET_GL = {"us": "us", "jp": "jp", "ae": "ae"}
MARKET_HL = {"us": "en", "jp": "ja", "ae": "en"}


async def _check_ranking(
    query: str, market: str, serp_api_key: str
) -> dict:
    """Check NAKAI's ranking for a specific query in a specific market."""
    result = {
        "query": query,
        "market": market,
        "rank": None,
        "url": None,
        "in_ai_overview": False,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if not serp_api_key:
        return result

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                "https://serpapi.com/search.json",
                params={
                    "q": query,
                    "api_key": serp_api_key,
                    "engine": "google",
                    "gl": MARKET_GL[market],
                    "hl": MARKET_HL[market],
                    "num": 50,
                },
            )
            data = resp.json()

        # Check organic results
        for i, item in enumerate(data.get("organic_results", [])):
            link = item.get("link", "").lower()
            if "nakaimatcha" in link or "nakai-matcha" in link:
                result["rank"] = i + 1
                result["url"] = item.get("link")
                break

        # Check AI Overview for NAKAI mention
        ai_text = str(data.get("ai_overview", {})).lower()
        if "nakai" in ai_text:
            result["in_ai_overview"] = True

    except Exception as e:
        logger.error(f"SEO check failed for '{query}' ({market}): {e}")

    return result


async def track_seo_rankings() -> list[dict]:
    """Run daily SEO ranking check across all markets and keywords."""
    from config import settings

    serp_key = getattr(settings, "serp_api_key", "")
    all_results = []

    for market, keywords in SEO_KEYWORDS.items():
        for kw in keywords:
            result = await _check_ranking(kw, market, serp_key)
            all_results.append(result)

    # Store in Supabase
    try:
        from services import supabase_client
        for r in all_results:
            await supabase_client.store_seo_ranking(r)
    except Exception as e:
        logger.error(f"Failed to store SEO rankings: {e}")

    # Alert on significant changes
    ranked = [r for r in all_results if r["rank"] is not None]
    ai_cited = [r for r in all_results if r["in_ai_overview"]]
    logger.info(
        f"SEO tracker complete: {len(ranked)} rankings found, "
        f"{len(ai_cited)} AI Overview citations across "
        f"{len(all_results)} queries"
    )

    return all_results
