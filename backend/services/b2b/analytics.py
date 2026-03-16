"""B2B Analytics — Tracks and aggregates outreach performance.

Virtual Team Members #25-27: Analytics Trackers.
"""

import logging
from datetime import datetime, timezone

from services import supabase_client

logger = logging.getLogger(__name__)


async def record_daily_stats(pipeline_stats: dict) -> dict | None:
    """Record daily pipeline stats."""
    if not supabase_client._is_configured():
        return None
    supabase_client._init()

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Get open/click/reply/bounce counts for today
    engagement = await _get_today_engagement()

    data = {
        "date": today,
        "leads_added": pipeline_stats.get("leads_added", 0),
        "emails_found": pipeline_stats.get("emails_found", 0),
        "emails_sent": pipeline_stats.get("emails_sent", 0),
        "opens": engagement.get("opens", 0),
        "clicks": engagement.get("clicks", 0),
        "replies": engagement.get("replies", 0),
        "bounces": engagement.get("bounces", 0),
    }

    try:
        client = supabase_client._get_client()
        resp = await client.post(
            f"{supabase_client._BASE_URL}/b2b_daily_stats",
            headers={
                **supabase_client._HEADERS,
                "Prefer": "return=representation,resolution=merge-duplicates",
            },
            json=data,
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.error(f"[B2B] Stats record failed: {e}")
        return None


async def get_dashboard_stats() -> dict:
    """Get comprehensive stats for the dashboard."""
    if not supabase_client._is_configured():
        return {}
    supabase_client._init()

    stats: dict = {}
    client = supabase_client._get_client()

    try:
        # Total leads
        resp = await client.get(
            f"{supabase_client._BASE_URL}/b2b_leads",
            headers={**supabase_client._HEADERS, "Prefer": "count=exact"},
            params={"select": "id", "limit": "0"},
        )
        stats["total_leads"] = int(resp.headers.get("content-range", "0/0").split("/")[-1])

        # Leads by status
        resp = await client.get(
            f"{supabase_client._BASE_URL}/b2b_leads",
            headers=supabase_client._HEADERS,
            params={"select": "status", "limit": "10000"},
        )
        status_counts: dict[str, int] = {}
        for row in resp.json():
            s = row.get("status", "unknown")
            status_counts[s] = status_counts.get(s, 0) + 1
        stats["leads_by_status"] = status_counts

        # Leads by region
        resp = await client.get(
            f"{supabase_client._BASE_URL}/b2b_leads",
            headers=supabase_client._HEADERS,
            params={"select": "region", "limit": "10000"},
        )
        region_counts: dict[str, int] = {}
        for row in resp.json():
            r = row.get("region", "unknown")
            region_counts[r] = region_counts.get(r, 0) + 1
        stats["leads_by_region"] = region_counts

        # Total contacts
        resp = await client.get(
            f"{supabase_client._BASE_URL}/b2b_contacts",
            headers={**supabase_client._HEADERS, "Prefer": "count=exact"},
            params={"select": "id", "limit": "0"},
        )
        stats["total_contacts"] = int(resp.headers.get("content-range", "0/0").split("/")[-1])

        # Verified contacts
        resp = await client.get(
            f"{supabase_client._BASE_URL}/b2b_contacts",
            headers={**supabase_client._HEADERS, "Prefer": "count=exact"},
            params={"select": "id", "verified": "eq.true", "limit": "0"},
        )
        stats["verified_contacts"] = int(resp.headers.get("content-range", "0/0").split("/")[-1])

        # Outreach stats
        resp = await client.get(
            f"{supabase_client._BASE_URL}/b2b_outreach",
            headers=supabase_client._HEADERS,
            params={"select": "status", "limit": "50000"},
        )
        outreach_statuses: dict[str, int] = {}
        for row in resp.json():
            s = row.get("status", "unknown")
            outreach_statuses[s] = outreach_statuses.get(s, 0) + 1
        stats["outreach_by_status"] = outreach_statuses

        total_sent = sum(outreach_statuses.values())
        opens = outreach_statuses.get("opened", 0) + outreach_statuses.get("clicked", 0) + outreach_statuses.get("replied", 0)
        stats["total_sent"] = total_sent
        stats["total_opens"] = opens
        stats["open_rate"] = round(opens / total_sent * 100, 1) if total_sent else 0
        stats["reply_rate"] = round(outreach_statuses.get("replied", 0) / total_sent * 100, 1) if total_sent else 0

        # Daily trend (last 30 days)
        resp = await client.get(
            f"{supabase_client._BASE_URL}/b2b_daily_stats",
            headers=supabase_client._HEADERS,
            params={"order": "date.desc", "limit": "30"},
        )
        stats["daily_trend"] = list(reversed(resp.json()))

        # Recent leads
        resp = await client.get(
            f"{supabase_client._BASE_URL}/b2b_leads",
            headers=supabase_client._HEADERS,
            params={"order": "created_at.desc", "limit": "10"},
        )
        stats["recent_leads"] = resp.json()

    except Exception as e:
        logger.error(f"[B2B] Dashboard stats failed: {e}", exc_info=True)

    return stats


async def _get_today_engagement() -> dict:
    """Count today's email engagement events."""
    if not supabase_client._is_configured():
        return {}
    supabase_client._init()

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    result = {"opens": 0, "clicks": 0, "replies": 0, "bounces": 0}

    client = supabase_client._get_client()

    for field, key in [
        ("opened_at", "opens"),
        ("clicked_at", "clicks"),
        ("replied_at", "replies"),
        ("bounced_at", "bounces"),
    ]:
        try:
            resp = await client.get(
                f"{supabase_client._BASE_URL}/b2b_outreach",
                headers={**supabase_client._HEADERS, "Prefer": "count=exact"},
                params={"select": "id", field: f"gte.{today}T00:00:00Z", "limit": "0"},
            )
            result[key] = int(resp.headers.get("content-range", "0/0").split("/")[-1])
        except Exception:
            pass

    return result
