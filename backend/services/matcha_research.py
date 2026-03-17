"""Global Matcha Research Pipeline — daily matcha industry intelligence."""

import logging
from datetime import datetime, timezone

import httpx

from config import settings

logger = logging.getLogger(__name__)


async def run_daily_research() -> dict:
    """Run daily matcha research: news, trends, Reddit mentions.

    Returns:
        Dict with research brief sections.
    """
    brief = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "news": [],
        "reddit_trends": [],
        "insights": "",
    }

    # 1. Google News via SerpAPI
    if settings.serp_api_key:
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                resp = await client.get(
                    "https://serpapi.com/search.json",
                    params={
                        "engine": "google_news",
                        "q": "matcha",
                        "api_key": settings.serp_api_key,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                for item in (data.get("news_results") or [])[:10]:
                    brief["news"].append({
                        "title": item.get("title", ""),
                        "source": item.get("source", {}).get("name", ""),
                        "link": item.get("link", ""),
                        "date": item.get("date", ""),
                    })
                logger.info(f"[RESEARCH] Found {len(brief['news'])} news articles")
        except Exception as e:
            logger.error(f"[RESEARCH] News fetch failed: {e}")

    # 2. Reddit mentions (via existing social monitor data or direct search)
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            for sub in ["Matcha", "tea", "JapaneseFood"]:
                resp = await client.get(
                    f"https://www.reddit.com/r/{sub}/search.json",
                    params={"q": "matcha", "sort": "new", "limit": 5, "t": "day"},
                    headers={"User-Agent": "NAKAI-Research/1.0"},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    for post in (data.get("data", {}).get("children") or []):
                        pd = post.get("data", {})
                        brief["reddit_trends"].append({
                            "subreddit": sub,
                            "title": pd.get("title", ""),
                            "score": pd.get("score", 0),
                            "comments": pd.get("num_comments", 0),
                            "url": f"https://reddit.com{pd.get('permalink', '')}",
                        })
        logger.info(f"[RESEARCH] Found {len(brief['reddit_trends'])} Reddit posts")
    except Exception as e:
        logger.error(f"[RESEARCH] Reddit fetch failed: {e}")

    # 3. Generate insights summary via Claude
    if settings.anthropic_api_key and (brief["news"] or brief["reddit_trends"]):
        try:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

            news_text = "\n".join(
                f"- {n['title']} ({n['source']})" for n in brief["news"][:5]
            )
            reddit_text = "\n".join(
                f"- r/{r['subreddit']}: {r['title']} (score:{r['score']})"
                for r in brief["reddit_trends"][:5]
            )

            response = await client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=512,
                messages=[{
                    "role": "user",
                    "content": f"""Summarize today's matcha industry intelligence in 3-4 bullet points.
Focus on trends, opportunities for NAKAI Matcha brand, and content ideas.

News:
{news_text}

Reddit discussions:
{reddit_text}

Be concise and actionable.""",
                }],
            )
            brief["insights"] = response.content[0].text.strip()
            logger.info("[RESEARCH] Generated insights summary")
        except Exception as e:
            logger.error(f"[RESEARCH] Insights generation failed: {e}")

    # 4. Log to Supabase
    await _log_research(brief)

    return brief


async def _log_research(brief: dict):
    """Log research brief to Supabase."""
    if not settings.supabase_url or not settings.supabase_service_key:
        return

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(
                f"{settings.supabase_url}/rest/v1/matcha_research_briefs",
                headers={
                    "apikey": settings.supabase_service_key,
                    "Authorization": f"Bearer {settings.supabase_service_key}",
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal",
                },
                json={
                    "date": brief["date"],
                    "news_count": len(brief["news"]),
                    "reddit_count": len(brief["reddit_trends"]),
                    "insights": brief["insights"],
                    "raw_data": brief,
                },
            )
    except Exception as e:
        logger.warning(f"[RESEARCH] Supabase log failed (non-critical): {e}")
