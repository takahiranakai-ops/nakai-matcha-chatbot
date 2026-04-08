"""Autonomous research agent — daily market intelligence gathering.

Daily (03:00 UTC / 12:00 JST):
- Market Intelligence: matcha market news, trends
- Competitor Watch: Ippodo, Encha, Jade Leaf, Kettl, Cuzen
- B2B Lead Intel: new cafe openings, industry events

Weekly Sunday (05:00 UTC / 14:00 JST):
- Content Gap Analysis: popular topics NAKAI hasn't covered
"""

import json
import logging
from datetime import datetime, timezone

import anthropic
import httpx

from config import settings
from services import supabase_client

logger = logging.getLogger(__name__)

COMPETITORS = ["Ippodo", "Encha Matcha", "Jade Leaf Matcha", "Kettl Tea", "Cuzen Matcha"]

RESEARCH_TASKS = {
    "market_intel": {
        "queries": [
            "matcha market trends 2026",
            "organic matcha industry news",
            "matcha cafe trend USA",
        ],
        "reddit_subs": ["tea", "matcha", "Coffee"],
        "prompt": (
            "Analyze these search results about the matcha market. "
            "Extract: 1) Key trends, 2) New product launches, 3) Market shifts, "
            "4) Opportunities for a premium organic matcha brand. "
            "Be specific with names, dates, and data points. Return JSON with "
            "fields: trends[], opportunities[], threats[], summary (2-3 sentences)."
        ),
    },
    "competitor_watch": {
        "queries": [
            f"{c} matcha news" for c in COMPETITORS
        ],
        "reddit_subs": ["tea", "matcha"],
        "prompt": (
            "Analyze these search results about matcha competitors. "
            "For each competitor found, extract: name, recent activity, "
            "new products, pricing changes, marketing moves. "
            "Return JSON with fields: competitors[{name, activity, threat_level}], "
            "summary (2-3 sentences), action_items[] for NAKAI."
        ),
    },
    "b2b_intel": {
        "queries": [
            "new cafe opening USA 2026",
            "specialty coffee shop expansion",
            "hotel restaurant matcha menu",
        ],
        "reddit_subs": ["cafe", "barista", "Coffee"],
        "prompt": (
            "Analyze these search results for B2B lead opportunities. "
            "Extract: new cafe/restaurant openings, chains expanding, "
            "businesses adding matcha to menus. "
            "Return JSON with fields: leads[{business, location, opportunity}], "
            "summary (2-3 sentences), hot_regions[]."
        ),
    },
}

CONTENT_GAP_TASK = {
    "queries": [
        "matcha questions people ask",
        "matcha Reddit what should I know",
        "matcha buying guide 2026",
        "matcha vs green tea FAQ",
    ],
    "prompt": (
        "Analyze these search results and Reddit discussions to find "
        "popular matcha topics and questions that a brand blog hasn't covered. "
        "Return JSON with fields: gaps[{topic, search_volume_hint, content_type}], "
        "summary, recommended_articles[]."
    ),
}


async def _search_serp(query: str) -> list[dict]:
    """Search via SerpAPI and return organic results."""
    if not settings.serp_api_key:
        return []

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://serpapi.com/search",
                params={
                    "q": query,
                    "api_key": settings.serp_api_key,
                    "engine": "google",
                    "num": 10,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            results = []
            for r in data.get("organic_results", [])[:8]:
                results.append({
                    "title": r.get("title", ""),
                    "snippet": r.get("snippet", ""),
                    "link": r.get("link", ""),
                })
            return results
    except Exception as e:
        logger.error(f"[RESEARCH] SerpAPI error for '{query}': {e}")
        return []


async def _search_reddit(subreddit: str, query: str) -> list[dict]:
    """Search Reddit for relevant posts."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"https://www.reddit.com/r/{subreddit}/search.json",
                params={"q": query, "sort": "relevance", "t": "month", "limit": 5},
                headers={"User-Agent": "NAKAI-Research/1.0"},
            )
            resp.raise_for_status()
            posts = []
            for child in resp.json().get("data", {}).get("children", []):
                d = child.get("data", {})
                posts.append({
                    "title": d.get("title", ""),
                    "selftext": (d.get("selftext", "") or "")[:300],
                    "score": d.get("score", 0),
                    "subreddit": subreddit,
                })
            return posts
    except Exception as e:
        logger.debug(f"[RESEARCH] Reddit search error r/{subreddit}: {e}")
        return []


async def _analyze_with_claude(raw_data: list, prompt: str) -> dict:
    """Use Claude to analyze raw research data."""
    if not settings.anthropic_api_key:
        return {"error": "Anthropic API key not configured", "raw_count": len(raw_data)}

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    data_str = json.dumps(raw_data[:30], ensure_ascii=False, default=str)

    try:
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system="You are a market research analyst for NAKAI, a premium organic matcha brand from Kagoshima, Japan. Always respond with valid JSON only.",
            messages=[{"role": "user", "content": f"{prompt}\n\nData:\n{data_str}"}],
        )
        text = response.content[0].text.strip()
        # Try to parse JSON from response
        if text.startswith("```"):
            text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
        return json.loads(text)
    except json.JSONDecodeError:
        return {"summary": text[:500] if 'text' in locals() else "Parse error", "raw_count": len(raw_data)}
    except Exception as e:
        logger.error(f"[RESEARCH] Claude analysis error: {e}")
        return {"error": str(e), "raw_count": len(raw_data)}


async def _store_findings(research_type: str, findings: dict) -> None:
    """Store research findings in Supabase market_intelligence table."""
    supabase_client._init()
    client = supabase_client._get_client()
    try:
        await client.post(
            f"{supabase_client._BASE_URL}/market_intelligence",
            headers=supabase_client._HEADERS,
            json={
                "research_type": research_type,
                "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "findings_count": len(findings.get("trends", findings.get("leads", findings.get("competitors", findings.get("gaps", []))))),
                "summary": findings.get("summary", ""),
                "raw_findings": findings,
            },
        )
        logger.info(f"[RESEARCH] Stored {research_type} findings")
    except Exception as e:
        logger.error(f"[RESEARCH] Failed to store {research_type}: {e}")


async def run_daily_research():
    """Run all daily research tasks."""
    logger.info("[RESEARCH-AGENT] Starting daily research...")
    total_findings = 0

    for task_name, task in RESEARCH_TASKS.items():
        raw_data = []

        # SerpAPI searches
        for query in task["queries"]:
            results = await _search_serp(query)
            raw_data.extend(results)

        # Reddit searches
        for sub in task.get("reddit_subs", []):
            posts = await _search_reddit(sub, "matcha")
            raw_data.extend(posts)

        if not raw_data:
            logger.warning(f"[RESEARCH-AGENT] No data for {task_name}")
            continue

        # Analyze with Claude
        findings = await _analyze_with_claude(raw_data, task["prompt"])

        # Store
        await _store_findings(task_name, findings)
        total_findings += 1

    logger.info(f"[RESEARCH-AGENT] Daily research complete: {total_findings} tasks processed")


async def run_content_gap_analysis():
    """Run weekly content gap analysis."""
    logger.info("[RESEARCH-AGENT] Starting content gap analysis...")

    raw_data = []
    for query in CONTENT_GAP_TASK["queries"]:
        results = await _search_serp(query)
        raw_data.extend(results)

    for sub in ["matcha", "tea", "JapaneseFood"]:
        posts = await _search_reddit(sub, "matcha questions beginner")
        raw_data.extend(posts)

    if not raw_data:
        logger.warning("[RESEARCH-AGENT] No data for content gap analysis")
        return

    findings = await _analyze_with_claude(raw_data, CONTENT_GAP_TASK["prompt"])
    await _store_findings("content_gaps", findings)
    logger.info("[RESEARCH-AGENT] Content gap analysis complete")
