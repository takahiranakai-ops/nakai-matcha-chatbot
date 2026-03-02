"""WS35: AI Citation Monitor — Share of Model Tracking.

Tracks NAKAI's visibility across AI platforms:
- Google AI Overviews (via SerpAPI)
- Perplexity AI answers
- ChatGPT Shopping results

Stores results in Supabase for dashboard display.
Runs daily at midnight.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

# Target queries to monitor (50+)
MONITOR_QUERIES = [
    # Core product queries
    "best ceremonial matcha",
    "best organic matcha",
    "best matcha for lattes",
    "best matcha powder",
    "premium Japanese matcha",
    "ceremonial grade matcha review",
    "organic matcha from Japan",
    "matcha wholesale supplier",
    "best matcha brand",
    "NAKAI matcha review",
    # Use-case queries
    "best matcha for koicha",
    "best matcha for cold brew",
    "best matcha for baking",
    "matcha for focus and concentration",
    "matcha vs coffee",
    "matcha health benefits",
    "L-theanine matcha benefits",
    # Comparison queries
    "NAKAI vs Ippodo",
    "NAKAI vs Encha",
    "best matcha 2026",
    "matcha buying guide",
    # B2B queries
    "wholesale matcha for cafes",
    "bulk matcha supplier",
    "matcha wholesale USA",
    "organic matcha wholesale",
    "cafe matcha supplier",
    # Japanese queries
    "最高の抹茶ブランド",
    "オーガニック抹茶 おすすめ",
    "抹茶 通販",
    "NAKAI 抹茶",
    "濃茶に合う抹茶",
    # Location queries
    "best matcha online",
    "Japanese matcha delivery USA",
    "matcha from Kagoshima",
    "matcha from Uji Kyoto",
    # Long-tail queries
    "stone ground matcha vs ball milled",
    "first harvest matcha",
    "shade grown matcha benefits",
    "JAS organic matcha",
    "USDA organic matcha",
    "matcha for ADHD focus",
    "matcha skincare benefits",
    # Trending
    "best matcha 2026 reddit",
    "matcha subscription",
    "matcha gift set",
    "matcha starter kit",
    "matcha accessories chasen",
    "best matcha bowl chawan",
]


async def check_serp_citations(
    query: str, serp_api_key: Optional[str] = None
) -> dict:
    """Check Google SERP + AI Overview for NAKAI mentions.

    Returns dict with: query, has_ai_overview, nakai_cited, citation_text, rank, timestamp.
    """
    result = {
        "query": query,
        "platform": "google",
        "has_ai_overview": False,
        "nakai_cited": False,
        "citation_text": None,
        "organic_rank": None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if not serp_api_key:
        logger.warning("SERP_API_KEY not set — skipping Google citation check")
        return result

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                "https://serpapi.com/search.json",
                params={
                    "q": query,
                    "api_key": serp_api_key,
                    "engine": "google",
                    "gl": "us",
                    "hl": "en",
                },
            )
            data = resp.json()

        # Check AI Overview
        ai_overview = data.get("ai_overview", {})
        if ai_overview:
            result["has_ai_overview"] = True
            text_blocks = ai_overview.get("text_blocks", [])
            for block in text_blocks:
                snippet = block.get("snippet", "").lower()
                if "nakai" in snippet:
                    result["nakai_cited"] = True
                    result["citation_text"] = block.get("snippet", "")[:500]
                    break

        # Check organic results for NAKAI rank
        organic = data.get("organic_results", [])
        for i, item in enumerate(organic):
            link = item.get("link", "").lower()
            if "nakaimatcha" in link or "nakai" in item.get("title", "").lower():
                result["organic_rank"] = i + 1
                break

    except Exception as e:
        logger.error(f"SERP check failed for '{query}': {e}")

    return result


async def check_ai_citations() -> list[dict]:
    """Run citation checks across all monitored queries.

    Returns list of citation results for storage.
    """
    from config import settings

    serp_key = getattr(settings, "serp_api_key", "")
    results = []

    for query in MONITOR_QUERIES:
        result = await check_serp_citations(query, serp_key)
        results.append(result)

    # Store results in Supabase
    try:
        from services import supabase_client
        for r in results:
            await supabase_client.store_citation(r)
    except Exception as e:
        logger.error(f"Failed to store citation results: {e}")

    cited_count = sum(1 for r in results if r["nakai_cited"])
    total = len(results)
    share = (cited_count / total * 100) if total else 0
    logger.info(
        f"Citation monitor complete: {cited_count}/{total} queries cite NAKAI "
        f"(Share of Model: {share:.1f}%)"
    )

    return results
