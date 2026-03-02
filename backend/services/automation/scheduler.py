"""NAKAI Automation Scheduler — Orchestrates all background jobs.

Schedule:
- Every 6 hours: Social mention monitor (WS39)
- Daily 00:00 UTC: AI citation monitor (WS35)
- Daily 01:00 UTC: Review aggregator (WS37)
- Daily 02:00 UTC: SEO ranking tracker (WS40)
- Weekly Wed 03:00 UTC: Content freshness refresh (WS38)
- Weekly Mon 06:00 UTC: Competitor monitor (WS36)

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


# ---------------------------------------------------------------------------
# Simple asyncio-based scheduler (no external dependency needed)
# ---------------------------------------------------------------------------

_scheduler_task = None


async def _scheduler_loop():
    """Main scheduler loop using simple time-based checks."""
    logger.info("[SCHEDULER] Starting automation scheduler...")

    last_run = {
        "social": 0,       # every 6h
        "citation": 0,     # daily
        "reviews": 0,      # daily
        "seo": 0,          # daily
        "freshness": 0,    # weekly
        "competitor": 0,   # weekly
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

            # Weekly Wednesday 03:xx UTC: Content freshness
            if weekday == 2 and hour == 3 and (now.timestamp() - last_run["freshness"]) >= 6 * 24 * 3600:
                last_run["freshness"] = now.timestamp()
                asyncio.create_task(run_content_freshness())

            # Weekly Monday 06:xx UTC: Competitor monitor
            if weekday == 0 and hour == 6 and (now.timestamp() - last_run["competitor"]) >= 6 * 24 * 3600:
                last_run["competitor"] = now.timestamp()
                asyncio.create_task(run_competitor_monitor())

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
