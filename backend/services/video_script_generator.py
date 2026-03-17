"""TikTok/Reels Video Script Generator — structured short-form video scripts.

Daily pipeline:
1. Research trending matcha videos on YouTube via SerpAPI
2. Pick a topic inspired by what's performing well
3. Generate a NAKAI-branded script via Claude
4. Store in Supabase video_scripts table
"""

import json
import logging
from datetime import datetime, timezone

import httpx

from config import settings

logger = logging.getLogger(__name__)

SCRIPT_SYSTEM_PROMPT = """You are a short-form video script writer for NAKAI Matcha.
Create engaging 30-60 second video scripts about matcha.

Output format (JSON):
{
  "hook": "Attention-grabbing opening line (0-3 seconds)",
  "content": "Main educational content with specific details (3-30 seconds)",
  "cta": "Call to action driving to nakaimatcha.com (30-60 seconds)",
  "text_overlays": ["Text overlay 1", "Text overlay 2", "Text overlay 3"],
  "visual_cues": ["B-roll suggestion 1", "B-roll suggestion 2"],
  "hashtags": ["#matcha", "#tag2", "#tag3", "#tag4", "#tag5"],
  "estimated_duration": "45 seconds",
  "platform_notes": "Best for TikTok/Instagram Reels"
}

Rules:
- Hook must grab attention in the first 2 seconds
- Content must be genuinely educational (specific numbers, facts, techniques)
- Mention NAKAI only naturally, not as hard sell
- Visual cues should be filmable with basic equipment
- Include 5-7 relevant hashtags
- Keep language conversational and energetic"""


# ---------------------------------------------------------------------------
# YouTube trend research
# ---------------------------------------------------------------------------

async def _research_trending_videos() -> list[dict]:
    """Fetch trending matcha videos from YouTube via SerpAPI."""
    if not settings.serp_api_key:
        logger.warning("[VIDEO] SerpAPI key not set — skipping YouTube research")
        return []

    queries = ["matcha", "matcha recipe", "matcha latte", "抹茶"]
    videos: list[dict] = []

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            for q in queries:
                resp = await client.get(
                    "https://serpapi.com/search.json",
                    params={
                        "engine": "youtube",
                        "search_query": q,
                        "api_key": settings.serp_api_key,
                    },
                )
                if resp.status_code != 200:
                    continue
                data = resp.json()
                for item in (data.get("video_results") or [])[:5]:
                    videos.append({
                        "title": item.get("title", ""),
                        "channel": item.get("channel", {}).get("name", ""),
                        "views": item.get("views", 0),
                        "published": item.get("published_date", ""),
                        "description": (item.get("description") or "")[:200],
                        "link": item.get("link", ""),
                    })
        logger.info(f"[VIDEO] Found {len(videos)} trending YouTube videos")
    except Exception as e:
        logger.error(f"[VIDEO] YouTube research failed: {e}")

    return videos


async def _pick_topic(trending: list[dict]) -> str:
    """Use Claude to pick a compelling topic based on trending videos."""
    if not settings.anthropic_api_key:
        return "matcha preparation techniques"

    video_list = "\n".join(
        f"- {v['title']} ({v['channel']}, {v['views']} views)"
        for v in trending[:15]
    )

    try:
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": f"""Based on these trending matcha videos on YouTube, suggest ONE specific
video topic for NAKAI Matcha (a premium Japanese matcha brand).
The topic should be educational, filmable, and likely to perform well.

Trending videos:
{video_list}

Reply with ONLY the topic (one line, no quotes).""",
            }],
        )
        topic = response.content[0].text.strip().split("\n")[0]
        logger.info(f"[VIDEO] Selected topic: {topic}")
        return topic

    except Exception as e:
        logger.error(f"[VIDEO] Topic selection failed: {e}")
        return "how to make the perfect matcha latte"


# ---------------------------------------------------------------------------
# Script generation (existing, enhanced with trending context)
# ---------------------------------------------------------------------------

async def generate_video_script(topic: str, trending: list[dict] | None = None) -> dict:
    """Generate a structured video script for a matcha topic."""
    if not settings.anthropic_api_key:
        logger.warning("[VIDEO] Anthropic API key not set")
        return _fallback_script(topic)

    try:
        import anthropic

        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

        # Build context from trending videos if available
        context = ""
        if trending:
            top = trending[:5]
            context = "\n\nTrending matcha videos for reference:\n" + "\n".join(
                f"- {v['title']} ({v['views']} views)" for v in top
            )

        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=SCRIPT_SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": f"Create a video script about: {topic}{context}",
            }],
            temperature=0.8,
        )

        text = response.content[0].text.strip()

        try:
            start = text.index("{")
            end = text.rindex("}") + 1
            script = json.loads(text[start:end])
            script["topic"] = topic
            logger.info(f"[VIDEO] Generated script for: {topic}")
            return script
        except (ValueError, json.JSONDecodeError):
            logger.warning("[VIDEO] Could not parse JSON, returning raw text")
            return {"topic": topic, "raw_script": text}

    except Exception as e:
        logger.error(f"[VIDEO] Script generation failed: {e}")
        return _fallback_script(topic)


def _fallback_script(topic: str) -> dict:
    """Fallback script when API is unavailable."""
    return {
        "topic": topic,
        "hook": f"Did you know this about matcha? {topic}",
        "content": "Most people don't realize this key detail about matcha...",
        "cta": "Learn more at nakaimatcha.com - link in bio",
        "text_overlays": [topic, "NAKAI Matcha", "Link in bio"],
        "visual_cues": ["Close-up of matcha powder", "Whisking matcha in chawan"],
        "hashtags": ["#matcha", "#matchalatte", "#japanesetea", "#NAKAImatcha", "#greentea"],
        "estimated_duration": "30 seconds",
        "platform_notes": "Fallback script - API unavailable",
    }


# ---------------------------------------------------------------------------
# Supabase storage
# ---------------------------------------------------------------------------

async def _store_script(script: dict, trending: list[dict]):
    """Save video script to Supabase video_scripts table."""
    if not settings.supabase_url or not settings.supabase_service_key:
        return

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(
                f"{settings.supabase_url}/rest/v1/video_scripts",
                headers={
                    "apikey": settings.supabase_service_key,
                    "Authorization": f"Bearer {settings.supabase_service_key}",
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal",
                },
                json={
                    "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    "topic": script.get("topic", ""),
                    "trending_videos": trending[:5] if trending else [],
                    "hook": script.get("hook", ""),
                    "content": script.get("content", ""),
                    "cta": script.get("cta", ""),
                    "text_overlays": script.get("text_overlays", []),
                    "visual_cues": script.get("visual_cues", []),
                    "hashtags": script.get("hashtags", []),
                    "estimated_duration": script.get("estimated_duration", ""),
                },
            )
            logger.info("[VIDEO] Script saved to Supabase")
    except Exception as e:
        logger.warning(f"[VIDEO] Supabase save failed (non-critical): {e}")


# ---------------------------------------------------------------------------
# Daily pipeline (called by scheduler)
# ---------------------------------------------------------------------------

async def run_daily_video_script() -> dict:
    """Full daily pipeline: research → topic → script → store."""
    logger.info("[VIDEO] Starting daily video script pipeline...")

    # 1. Research trending matcha videos
    trending = await _research_trending_videos()

    # 2. Pick a topic
    topic = await _pick_topic(trending) if trending else "matcha preparation tips and techniques"

    # 3. Generate script with trending context
    script = await generate_video_script(topic, trending=trending)

    # 4. Store to Supabase
    await _store_script(script, trending)

    logger.info(f"[VIDEO] Daily pipeline complete — topic: {topic}")
    return script
