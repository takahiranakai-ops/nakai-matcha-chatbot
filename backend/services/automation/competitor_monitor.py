"""WS36: Competitor Monitor — Weekly competitive intelligence.

Tracks competitor pricing, product changes, and AI citation counts.
Target competitors: Ippodo, Marukyu Koyamaen, Kettl, Matchabar, Encha.
Runs weekly on Mondays.
"""

import logging
from datetime import datetime, timezone

import httpx

logger = logging.getLogger(__name__)

COMPETITORS = {
    "ippodo": {
        "name": "Ippodo Tea",
        "domain": "ippodo-tea.co.jp",
        "store_url": "https://ippodotea.com",
    },
    "marukyu": {
        "name": "Marukyu Koyamaen",
        "domain": "marukyu-koyamaen.co.jp",
        "store_url": "https://www.marukyu-koyamaen.co.jp/english/",
    },
    "kettl": {
        "name": "Kettl",
        "domain": "kettl.co",
        "store_url": "https://kettl.co",
    },
    "matchabar": {
        "name": "MatchaBar",
        "domain": "matchabarnyc.com",
        "store_url": "https://matchabarnyc.com",
    },
    "encha": {
        "name": "Encha",
        "domain": "encha.com",
        "store_url": "https://www.encha.com",
    },
}


async def _check_competitor_serp(competitor: dict, serp_api_key: str) -> dict:
    """Check a competitor's visibility in Google SERPs + AI Overviews."""
    result = {
        "competitor": competitor["name"],
        "ai_citations": 0,
        "organic_appearances": 0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    test_queries = [
        "best ceremonial matcha",
        "best organic matcha",
        "matcha wholesale supplier",
    ]

    if not serp_api_key:
        return result

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            for query in test_queries:
                resp = await client.get(
                    "https://serpapi.com/search.json",
                    params={
                        "q": query,
                        "api_key": serp_api_key,
                        "engine": "google",
                        "gl": "us",
                    },
                )
                data = resp.json()

                # Check AI Overview
                ai_text = str(data.get("ai_overview", {})).lower()
                if competitor["name"].lower() in ai_text:
                    result["ai_citations"] += 1

                # Check organic results
                for item in data.get("organic_results", []):
                    if competitor["domain"] in item.get("link", ""):
                        result["organic_appearances"] += 1
    except Exception as e:
        logger.error(f"Competitor check failed for {competitor['name']}: {e}")

    return result


async def monitor_competitors() -> list[dict]:
    """Run weekly competitor analysis. Returns list of results."""
    from config import settings

    serp_key = getattr(settings, "serp_api_key", "")
    results = []

    for key, comp in COMPETITORS.items():
        result = await _check_competitor_serp(comp, serp_key)
        results.append(result)

    # Store in Supabase
    try:
        from services import supabase_client
        for r in results:
            await supabase_client.store_competitor_data(r)
    except Exception as e:
        logger.error(f"Failed to store competitor data: {e}")

    logger.info(f"Competitor monitor complete: {len(results)} competitors tracked")
    return results
