"""NAKAI Automation Scheduler — Orchestrates all background jobs.

6-Slot Content System:
- Slot 1  00:00 UTC (09:00 JST): Twitter — 抹茶豆知識
- Slot 2  04:00 UTC (13:00 JST): Reddit #1 — 教育的投稿
-         06:00 UTC (15:00 JST): Video script generation
- Slot 3  08:00 UTC (17:00 JST): Blog — SEO最適化記事
- Slot 4  12:00 UTC (21:00 JST): Threads — 会話型コンテンツ
- Slot 5  16:00 UTC (01:00 JST): Reddit #2 — コミュニティ
- Slot 6  20:00 UTC (05:00 JST): LINE + Twitter #2

Automation Jobs:
- Every 6 hours: Social mention monitor (WS39)
- Daily 00:00 UTC: AI citation monitor (WS35)
- Daily 01:00 UTC: Review aggregator (WS37)
- Daily 02:00 UTC: SEO ranking tracker (WS40)
- Daily 04:00 UTC: Matcha research pipeline
- Daily 14:00 UTC: B2B Sales Pipeline
- Bi-weekly Wed/Sat 03:00 UTC: Content freshness refresh (WS38)
- Weekly Mon 06:00 UTC: Competitor monitor (WS36)
- Every 10 min: Newsletter schedule check

Realtime (webhook-driven):
- WS34: Product sync → /webhooks/shopify/product-update
- WS41: Sitemap ping → triggered by WS34 and WS38
"""

import asyncio
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Track running state to avoid overlapping jobs
_running_jobs: set[str] = set()


async def _safe_run(name: str, coro):
    """Run a job safely with logging and overlap prevention."""
    if name in _running_jobs:
        logger.warning(f"Job '{name}' already running — skipping")
        return

    _running_jobs.add(name)
    start = datetime.now(timezone.utc)
    logger.info(f"[SCHEDULER] Starting: {name}")

    try:
        await coro
    except Exception as e:
        logger.error(f"[SCHEDULER] {name} failed: {e}", exc_info=True)
    finally:
        _running_jobs.discard(name)
        elapsed = (datetime.now(timezone.utc) - start).total_seconds()
        logger.info(f"[SCHEDULER] Finished: {name} ({elapsed:.1f}s)")


async def run_citation_monitor():
    """WS35: Daily AI citation check."""
    from services.automation.citation_monitor import check_ai_citations
    await _safe_run("citation_monitor", check_ai_citations())


async def run_review_aggregator():
    """WS37: Daily review aggregation."""
    from services.automation.review_aggregator import aggregate_reviews
    await _safe_run("review_aggregator", aggregate_reviews())


async def run_seo_tracker():
    """WS40: Daily SEO ranking check."""
    from services.automation.seo_tracker import track_seo_rankings
    await _safe_run("seo_tracker", track_seo_rankings())


async def run_content_freshness():
    """WS38: Weekly content refresh."""
    from services.automation.content_freshness import refresh_ai_content
    await _safe_run("content_freshness", refresh_ai_content())


async def run_competitor_monitor():
    """WS36: Weekly competitor analysis."""
    from services.automation.competitor_monitor import monitor_competitors
    await _safe_run("competitor_monitor", monitor_competitors())


async def run_social_monitor():
    """WS39: Social mention scan every 6 hours."""
    from services.automation.social_monitor import monitor_social_mentions
    await _safe_run("social_monitor", monitor_social_mentions())


async def run_daily_tips():
    """Daily matcha content auto-post to Twitter/Threads/LINE (legacy wrapper)."""
    from services.daily_content import generate_daily_tips
    from services.social_poster import post_all

    async def _generate_and_post():
        content = await generate_daily_tips()
        await post_all(content)

    await _safe_run("daily_tips", _generate_and_post())


async def run_content_slot(slot: int, platform: str):
    """Generic content slot runner — generates and posts for one platform."""
    from services.daily_content import generate_daily_content
    from services.social_poster import post_to_twitter, post_to_threads, post_to_line, post_to_reddit
    from services.blog_poster import publish_blog_article

    async def _generate_and_post():
        actual_platform = "reddit" if platform == "reddit_community" else platform
        content = await generate_daily_content([platform], slot=slot)
        text = content.get(platform, "")
        if not text:
            return

        if actual_platform == "twitter":
            await post_to_twitter(text)
        elif actual_platform == "threads":
            await post_to_threads(text)
        elif actual_platform == "reddit":
            await post_to_reddit(text)
        elif actual_platform == "blog":
            await publish_blog_article(text)
        elif actual_platform == "line":
            await post_to_line(text)

    await _safe_run(f"slot_{slot}_{platform}", _generate_and_post())


async def run_video_script():
    """Daily video script generation."""
    from services.video_script_generator import run_daily_video_script
    await _safe_run("video_script", run_daily_video_script())


async def run_matcha_research():
    """Daily global matcha research pipeline."""
    from services.matcha_research import run_daily_research
    await _safe_run("matcha_research", run_daily_research())


async def run_b2b_pipeline():
    """Daily B2B sales pipeline — discover, hunt emails, send outreach."""
    from services.b2b.pipeline import run_daily_pipeline
    await _safe_run("b2b_pipeline", run_daily_pipeline())


async def run_newsletter_check():
    """Check and send due newsletter schedules."""
    from services.newsletter_sender import check_and_send_due_newsletters
    await _safe_run("newsletter", check_and_send_due_newsletters())


# ---------------------------------------------------------------------------
# Simple asyncio-based scheduler (no external dependency needed)
# ---------------------------------------------------------------------------

_scheduler_task = None


async def _scheduler_loop():
    """Main scheduler loop using simple time-based checks."""
    logger.info("[SCHEDULER] Starting automation scheduler...")

    last_run: dict[str, float] = {
        "social": 0,       # every 6h
        "citation": 0,     # daily
        "reviews": 0,      # daily
        "seo": 0,          # daily
        "slot_1": 0,       # 00:00 UTC — Twitter
        "slot_2": 0,       # 04:00 UTC — Reddit #1 (educational)
        "slot_3": 0,       # 08:00 UTC — Blog
        "slot_4": 0,       # 12:00 UTC — Threads
        "slot_5": 0,       # 16:00 UTC — Reddit #2 (community)
        "slot_6": 0,       # 20:00 UTC — LINE + Twitter #2
        "video_script": 0, # 06:00 UTC — Video script
        "research": 0,     # daily 04:00 UTC
        "b2b": 0,          # daily 14:00 UTC
        "freshness": 0,    # weekly
        "competitor": 0,   # weekly
        "newsletter": 0,   # every 10 min
    }

    while True:
        try:
            now = datetime.now(timezone.utc)
            hour = now.hour
            weekday = now.weekday()  # 0=Monday

            # Every 6 hours: Social monitor
            if (now.timestamp() - last_run["social"]) >= 6 * 3600:
                last_run["social"] = now.timestamp()
                asyncio.create_task(run_social_monitor())

            # Daily at 00:xx UTC: Citation monitor
            if hour == 0 and (now.timestamp() - last_run["citation"]) >= 23 * 3600:
                last_run["citation"] = now.timestamp()
                asyncio.create_task(run_citation_monitor())

            # Daily at 01:xx UTC: Review aggregator
            if hour == 1 and (now.timestamp() - last_run["reviews"]) >= 23 * 3600:
                last_run["reviews"] = now.timestamp()
                asyncio.create_task(run_review_aggregator())

            # Daily at 02:xx UTC: SEO tracker
            if hour == 2 and (now.timestamp() - last_run["seo"]) >= 23 * 3600:
                last_run["seo"] = now.timestamp()
                asyncio.create_task(run_seo_tracker())

            # Bi-weekly Wed + Sat 03:xx UTC: Content freshness
            if weekday in (2, 5) and hour == 3 and (now.timestamp() - last_run["freshness"]) >= 3 * 24 * 3600:
                last_run["freshness"] = now.timestamp()
                asyncio.create_task(run_content_freshness())

            # Weekly Monday 06:xx UTC: Competitor monitor
            if weekday == 0 and hour == 6 and (now.timestamp() - last_run["competitor"]) >= 6 * 24 * 3600:
                last_run["competitor"] = now.timestamp()
                asyncio.create_task(run_competitor_monitor())

            # Daily at 04:xx UTC: Matcha research pipeline
            if hour == 4 and (now.timestamp() - last_run["research"]) >= 23 * 3600:
                last_run["research"] = now.timestamp()
                asyncio.create_task(run_matcha_research())

            # === 6-SLOT CONTENT SYSTEM ===

            # Slot 1: 00:xx UTC (09:00 JST) — Twitter matcha tip
            if hour == 0 and (now.timestamp() - last_run["slot_1"]) >= 23 * 3600:
                last_run["slot_1"] = now.timestamp()
                asyncio.create_task(run_content_slot(1, "twitter"))

            # Slot 2: 04:xx UTC (13:00 JST) — Reddit #1 educational
            if hour == 4 and (now.timestamp() - last_run["slot_2"]) >= 23 * 3600:
                last_run["slot_2"] = now.timestamp()
                asyncio.create_task(run_content_slot(2, "reddit"))

            # Daily at 06:xx UTC: Video script generation
            if hour == 6 and (now.timestamp() - last_run["video_script"]) >= 23 * 3600:
                last_run["video_script"] = now.timestamp()
                asyncio.create_task(run_video_script())

            # Slot 3: 08:xx UTC (17:00 JST) — Blog article
            if hour == 8 and (now.timestamp() - last_run["slot_3"]) >= 23 * 3600:
                last_run["slot_3"] = now.timestamp()
                asyncio.create_task(run_content_slot(3, "blog"))

            # Slot 4: 12:xx UTC (21:00 JST) — Threads
            if hour == 12 and (now.timestamp() - last_run["slot_4"]) >= 23 * 3600:
                last_run["slot_4"] = now.timestamp()
                asyncio.create_task(run_content_slot(4, "threads"))

            # Daily at 14:xx UTC (06:00 PST): B2B Sales Pipeline
            if hour == 14 and (now.timestamp() - last_run["b2b"]) >= 23 * 3600:
                last_run["b2b"] = now.timestamp()
                asyncio.create_task(run_b2b_pipeline())

            # Slot 5: 16:xx UTC (01:00 JST) — Reddit #2 community
            if hour == 16 and (now.timestamp() - last_run["slot_5"]) >= 23 * 3600:
                last_run["slot_5"] = now.timestamp()
                asyncio.create_task(run_content_slot(5, "reddit_community"))

            # Slot 6: 20:xx UTC (05:00 JST) — LINE + Twitter #2
            if hour == 20 and (now.timestamp() - last_run["slot_6"]) >= 23 * 3600:
                last_run["slot_6"] = now.timestamp()
                asyncio.create_task(run_content_slot(6, "line"))
                asyncio.create_task(run_content_slot(6, "twitter"))

            # Every 10 min: Newsletter schedule check
            if (now.timestamp() - last_run["newsletter"]) >= 600:
                last_run["newsletter"] = now.timestamp()
                asyncio.create_task(run_newsletter_check())

        except Exception as e:
            logger.error(f"[SCHEDULER] Loop error: {e}")

        # Check every 10 minutes
        await asyncio.sleep(600)


def start_scheduler():
    """Start the background scheduler. Call from FastAPI lifespan."""
    global _scheduler_task
    if _scheduler_task is None or _scheduler_task.done():
        _scheduler_task = asyncio.create_task(_scheduler_loop())
        logger.info("[SCHEDULER] Background automation scheduler started")


def stop_scheduler():
    """Stop the background scheduler."""
    global _scheduler_task
    if _scheduler_task and not _scheduler_task.done():
        _scheduler_task.cancel()
        logger.info("[SCHEDULER] Background automation scheduler stopped")
