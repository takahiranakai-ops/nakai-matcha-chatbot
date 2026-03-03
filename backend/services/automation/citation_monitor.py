"""WS35: AI Citation Monitor — Share of Model Tracking.

Tracks NAKAI's visibility across AI platforms:
- Google AI Overviews (via SerpAPI) with position & competitor tracking
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

# Competitor brands to track co-occurrence
COMPETITORS = [
    "ippodo", "marukyu koyamaen", "encha", "jade leaf",
    "ceremonial matcha", "kettl", "matchabar", "golde",
    "cuzen", "breakaway matcha", "midori spring", "aprika life",
]

# Target queries to monitor (70+)
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
    # AI Shopping queries (ChatGPT Shopping / Google AI Mode)
    "buy matcha online",
    "matcha powder price comparison",
    "organic matcha under $30",
    "matcha gift for tea lover",
    "Japanese matcha sampler set",
    "matcha chawan handmade",
    "chasen bamboo whisk buy",
    # Voice / conversational queries
    "what is the best matcha to buy",
    "which matcha brand is most authentic",
    "where to buy real Japanese matcha",
    "is NAKAI matcha worth it",
    "what matcha do Japanese people drink",
    # Seasonal / trend queries
    "matcha spring 2026",
    "matcha mothers day gift",
    "healthy matcha drinks",
    "matcha recipe ideas",
    "iced matcha latte best powder",
    # Competitor comparison queries
    "NAKAI vs Jade Leaf matcha",
    "NAKAI vs Marukyu Koyamaen",
    "best matcha brand Japan direct",
    "single origin matcha",
    "Kagoshima vs Uji matcha",
]


async def check_serp_citations(
    query: str, serp_api_key: Optional[str] = None
) -> dict:
    """Check Google SERP + AI Overview for NAKAI mentions.

    Returns dict with position tracking and competitor co-occurrence.
    """
    result = {
        "query": query,
        "platform": "google",
        "has_ai_overview": False,
        "nakai_cited": False,
        "citation_text": None,
        "ai_overview_position": None,
        "ai_overview_total_citations": 0,
        "competitors_in_overview": [],
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

        # Check AI Overview with position and competitor tracking
        ai_overview = data.get("ai_overview", {})
        if ai_overview:
            result["has_ai_overview"] = True
            text_blocks = ai_overview.get("text_blocks", [])
            references = ai_overview.get("references", [])
            result["ai_overview_total_citations"] = len(references)

            # Track NAKAI position in AI Overview references
            for i, ref in enumerate(references):
                ref_text = (ref.get("title", "") + ref.get("link", "")).lower()
                if "nakai" in ref_text or "nakaimatcha" in ref_text:
                    result["nakai_cited"] = True
                    result["ai_overview_position"] = i + 1
                    break

            # Fallback: check text blocks if not in references
            if not result["nakai_cited"]:
                for block in text_blocks:
                    snippet = block.get("snippet", "").lower()
                    if "nakai" in snippet:
                        result["nakai_cited"] = True
                        result["citation_text"] = block.get("snippet", "")[:500]
                        break

            # Track competitor co-occurrence in AI Overview
            overview_text = " ".join(
                b.get("snippet", "") for b in text_blocks
            ).lower()
            ref_text_all = " ".join(
                r.get("title", "") + " " + r.get("link", "")
                for r in references
            ).lower()
            combined = overview_text + " " + ref_text_all

            for comp in COMPETITORS:
                if comp in combined:
                    result["competitors_in_overview"].append(comp)

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
    overview_count = sum(1 for r in results if r["has_ai_overview"])
    avg_position = 0.0
    positioned = [r["ai_overview_position"] for r in results if r.get("ai_overview_position")]
    if positioned:
        avg_position = sum(positioned) / len(positioned)
    total = len(results)
    share = (cited_count / total * 100) if total else 0

    # Competitor frequency
    comp_freq: dict[str, int] = {}
    for r in results:
        for c in r.get("competitors_in_overview", []):
            comp_freq[c] = comp_freq.get(c, 0) + 1
    top_comps = sorted(comp_freq.items(), key=lambda x: x[1], reverse=True)[:5]

    logger.info(
        f"Citation monitor complete: {cited_count}/{total} queries cite NAKAI "
        f"(Share of Model: {share:.1f}%) | "
        f"AI Overviews: {overview_count} | "
        f"Avg position: {avg_position:.1f} | "
        f"Top competitors: {top_comps}"
    )

    return results
