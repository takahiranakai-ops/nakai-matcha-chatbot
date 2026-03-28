"""Supabase client for chat logging and knowledge management.

Uses httpx directly (no supabase-py dependency) to keep requirements
lightweight. All operations use the service_role key for full access.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

import httpx

from config import settings

logger = logging.getLogger(__name__)

_HEADERS: dict = {}
_BASE_URL: str = ""

# ── Shared HTTP client ──────────────────────────────────────
_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(timeout=15.0)
    return _client


async def close():
    global _client
    if _client and not _client.is_closed:
        await _client.aclose()
        _client = None


_config_warned = False


def _init():
    global _HEADERS, _BASE_URL, _config_warned
    if _HEADERS:
        return
    if not _is_configured():
        if not _config_warned:
            logger.error("Supabase not configured: SUPABASE_URL or SUPABASE_SERVICE_KEY missing")
            _config_warned = True
        return
    _BASE_URL = f"{settings.supabase_url}/rest/v1"
    _HEADERS = {
        "apikey": settings.supabase_service_key,
        "Authorization": f"Bearer {settings.supabase_service_key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def _is_configured() -> bool:
    return bool(settings.supabase_url and settings.supabase_service_key)


# ----------------------------------------------------------------
# CONVERSATIONS
# ----------------------------------------------------------------

async def create_conversation(
    session_id: str,
    source: str = "pwa",
    language: str = "en",
    user_agent: str = "",
    referrer: str = "",
) -> Optional[dict]:
    if not _is_configured():
        return None
    _init()
    payload = {
        "session_id": session_id,
        "source": source,
        "language": language,
        "user_agent": user_agent or "",
        "referrer": referrer or "",
    }
    try:
        client = _get_client()
        resp = await client.post(
            f"{_BASE_URL}/conversations",
            headers=_HEADERS,
            json=payload,
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.warning(f"Failed to create conversation: {e}", exc_info=True)
        return None


async def get_conversation_by_session(
    session_id: str, source: str = "pwa"
) -> Optional[dict]:
    if not _is_configured():
        return None
    _init()
    try:
        client = _get_client()
        resp = await client.get(
            f"{_BASE_URL}/conversations",
            headers=_HEADERS,
            params={
                "session_id": f"eq.{session_id}",
                "source": f"eq.{source}",
                "order": "started_at.desc",
                "limit": "1",
            },
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.warning(f"Failed to get conversation: {e}", exc_info=True)
        return None


# ----------------------------------------------------------------
# MESSAGES
# ----------------------------------------------------------------

async def log_message(
    conversation_id: str,
    role: str,
    content: str,
    language: str = "en",
    sources: list[str] | None = None,
    context_chunks: int = 0,
    response_time_ms: int | None = None,
) -> Optional[dict]:
    if not _is_configured():
        return None
    _init()
    payload = {
        "conversation_id": conversation_id,
        "role": role,
        "content": content,
        "language": language,
        "sources": sources or [],
        "context_chunks": context_chunks,
    }
    if response_time_ms is not None:
        payload["response_time_ms"] = response_time_ms
    try:
        client = _get_client()
        resp = await client.post(
            f"{_BASE_URL}/messages",
            headers=_HEADERS,
            json=payload,
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.warning(f"Failed to log message: {e}", exc_info=True)
        return None


# ----------------------------------------------------------------
# KNOWLEDGE ARTICLES
# ----------------------------------------------------------------

async def list_articles(
    active_only: bool = True,
    language: str | None = None,
    category: str | None = None,
) -> list[dict]:
    if not _is_configured():
        return []
    _init()
    params: dict = {"order": "sort_order.asc,created_at.desc"}
    if active_only:
        params["is_active"] = "eq.true"
    if language:
        params["language"] = f"eq.{language}"
    if category:
        params["category"] = f"eq.{category}"
    try:
        client = _get_client()
        resp = await client.get(
            f"{_BASE_URL}/knowledge_articles",
            headers=_HEADERS,
            params=params,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.warning(f"Failed to list articles: {e}", exc_info=True)
        return []


async def get_article(article_id: str) -> Optional[dict]:
    if not _is_configured():
        return None
    _init()
    try:
        client = _get_client()
        resp = await client.get(
            f"{_BASE_URL}/knowledge_articles",
            headers=_HEADERS,
            params={"id": f"eq.{article_id}", "limit": "1"},
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.warning(f"Failed to get article: {e}", exc_info=True)
        return None


async def create_article(
    title: str,
    content: str,
    language: str = "en",
    category: str = "general",
    slug: str = "",
) -> Optional[dict]:
    if not _is_configured():
        return None
    _init()
    if not slug:
        slug = title.lower().replace(" ", "-").replace("/", "-")
        slug = "".join(c for c in slug if c.isalnum() or c == "-")
    payload = {
        "title": title,
        "slug": slug,
        "content": content,
        "language": language,
        "category": category,
        "is_active": True,
    }
    try:
        client = _get_client()
        resp = await client.post(
            f"{_BASE_URL}/knowledge_articles",
            headers=_HEADERS,
            json=payload,
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.warning(f"Failed to create article: {e}", exc_info=True)
        return None


async def update_article(article_id: str, updates: dict) -> Optional[dict]:
    if not _is_configured():
        return None
    _init()
    try:
        client = _get_client()
        resp = await client.patch(
            f"{_BASE_URL}/knowledge_articles",
            headers={**_HEADERS, "Prefer": "return=representation"},
            params={"id": f"eq.{article_id}"},
            json=updates,
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.warning(f"Failed to update article: {e}", exc_info=True)
        return None


async def delete_article(article_id: str) -> bool:
    if not _is_configured():
        return False
    _init()
    try:
        client = _get_client()
        resp = await client.delete(
            f"{_BASE_URL}/knowledge_articles",
            headers=_HEADERS,
            params={"id": f"eq.{article_id}"},
        )
        resp.raise_for_status()
        return True
    except Exception as e:
        logger.warning(f"Failed to delete article: {e}", exc_info=True)
        return False


# ----------------------------------------------------------------
# ANALYTICS
# ----------------------------------------------------------------

async def get_conversations_list(
    limit: int = 50,
    offset: int = 0,
    source: str | None = None,
    language: str | None = None,
) -> list[dict]:
    if not _is_configured():
        return []
    _init()
    params: dict = {
        "order": "last_message_at.desc",
        "limit": str(limit),
        "offset": str(offset),
    }
    if source:
        params["source"] = f"eq.{source}"
    if language:
        params["language"] = f"eq.{language}"
    try:
        client = _get_client()
        resp = await client.get(
            f"{_BASE_URL}/conversations",
            headers=_HEADERS,
            params=params,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.warning(f"Failed to list conversations: {e}", exc_info=True)
        return []


async def get_conversation_messages(conversation_id: str) -> list[dict]:
    if not _is_configured():
        return []
    _init()
    try:
        client = _get_client()
        resp = await client.get(
            f"{_BASE_URL}/messages",
            headers=_HEADERS,
            params={
                "conversation_id": f"eq.{conversation_id}",
                "order": "created_at.asc",
            },
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.warning(f"Failed to get messages: {e}", exc_info=True)
        return []


async def get_analytics_summary() -> dict:
    if not _is_configured():
        return {}
    _init()
    summary: dict = {}
    try:
        client = _get_client()

        # Total conversations
        resp = await client.get(
            f"{_BASE_URL}/conversations",
            headers={**_HEADERS, "Prefer": "count=exact"},
            params={"select": "id", "limit": "0"},
        )
        summary["total_conversations"] = int(
            resp.headers.get("content-range", "0/0").split("/")[-1]
        )

        # Total messages
        resp = await client.get(
            f"{_BASE_URL}/messages",
            headers={**_HEADERS, "Prefer": "count=exact"},
            params={"select": "id", "limit": "0"},
        )
        summary["total_messages"] = int(
            resp.headers.get("content-range", "0/0").split("/")[-1]
        )

        # By source
        resp = await client.get(
            f"{_BASE_URL}/conversations",
            headers=_HEADERS,
            params={"select": "source", "limit": "10000"},
        )
        sources: dict = {}
        for row in resp.json():
            s = row.get("source", "unknown")
            sources[s] = sources.get(s, 0) + 1
        summary["by_source"] = sources

        # By language
        resp = await client.get(
            f"{_BASE_URL}/conversations",
            headers=_HEADERS,
            params={"select": "language", "limit": "10000"},
        )
        langs: dict = {}
        for row in resp.json():
            la = row.get("language", "unknown")
            langs[la] = langs.get(la, 0) + 1
        summary["by_language"] = langs

        # Last 7 days daily
        seven_days_ago = (
            datetime.now(timezone.utc) - timedelta(days=7)
        ).isoformat()
        resp = await client.get(
            f"{_BASE_URL}/conversations",
            headers=_HEADERS,
            params={
                "select": "started_at",
                "started_at": f"gte.{seven_days_ago}",
                "order": "started_at.asc",
                "limit": "10000",
            },
        )
        daily: dict = {}
        for row in resp.json():
            day = row["started_at"][:10]
            daily[day] = daily.get(day, 0) + 1
        summary["daily_last_7"] = daily

    except Exception as e:
        logger.warning(f"Analytics summary failed: {e}", exc_info=True)
    return summary


# ----------------------------------------------------------------
# WHOLESALE LEADS
# ----------------------------------------------------------------

async def create_wholesale_lead(email: str, session_id: str = "") -> Optional[dict]:
    """Insert a wholesale lead. Duplicate emails are silently ignored."""
    if not _is_configured():
        return None
    _init()
    try:
        client = _get_client()
        resp = await client.post(
            f"{_BASE_URL}/wholesale_leads",
            headers={**_HEADERS, "Prefer": "return=representation,resolution=ignore-duplicates"},
            json={"email": email, "session_id": session_id},
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.warning(f"Failed to create wholesale lead: {e}", exc_info=True)
        return None


async def list_wholesale_leads() -> list[dict]:
    if not _is_configured():
        return []
    _init()
    try:
        client = _get_client()
        resp = await client.get(
            f"{_BASE_URL}/wholesale_leads",
            headers=_HEADERS,
            params={"order": "created_at.desc", "limit": "500"},
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.warning(f"Failed to list wholesale leads: {e}", exc_info=True)
        return []


async def delete_wholesale_lead(lead_id: str) -> bool:
    if not _is_configured():
        return False
    _init()
    try:
        client = _get_client()
        resp = await client.delete(
            f"{_BASE_URL}/wholesale_leads",
            headers=_HEADERS,
            params={"id": f"eq.{lead_id}"},
        )
        resp.raise_for_status()
        return True
    except Exception as e:
        logger.warning(f"Failed to delete wholesale lead: {e}", exc_info=True)
        return False


# ----------------------------------------------------------------
# WHOLESALE INQUIRIES (bulk order form)
# ----------------------------------------------------------------

async def create_wholesale_inquiry(
    company: str, name: str, email: str,
    phone: str = "", country: str = "", quantity: str = "",
    use_case: str = "", message: str = "", language: str = "en",
) -> Optional[dict]:
    """Insert a wholesale inquiry from the bulk order form."""
    if not _is_configured():
        return None
    _init()
    try:
        client = _get_client()
        resp = await client.post(
            f"{_BASE_URL}/wholesale_inquiries",
            headers={**_HEADERS, "Prefer": "return=representation"},
            json={
                "company": company, "name": name, "email": email,
                "phone": phone, "country": country, "quantity": quantity,
                "use_case": use_case, "message": message, "language": language,
            },
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.warning(f"Failed to create wholesale inquiry: {e}", exc_info=True)
        return None


async def get_wholesale_inquiries_by_age(days: int) -> list[dict]:
    """Return wholesale inquiries created approximately *days* ago (same UTC date)."""
    if not _is_configured():
        return []
    _init()
    try:
        target = datetime.now(timezone.utc) - timedelta(days=days)
        date_str = target.strftime("%Y-%m-%d")
        client = _get_client()
        resp = await client.get(
            f"{_BASE_URL}/wholesale_inquiries"
            f"?created_at=gte.{date_str}T00:00:00Z"
            f"&created_at=lt.{date_str}T23:59:59Z"
            f"&select=*",
            headers=_HEADERS,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.warning(f"Failed to fetch wholesale inquiries (age={days}d): {e}")
        return []


async def mark_followup_sent(inquiry_id: str, stage: str) -> bool:
    """Mark a follow-up stage as sent by patching the inquiry row.

    Sets followup_day2_sent or followup_day7_sent to current timestamp.
    """
    if not _is_configured():
        return False
    _init()
    column = f"followup_{stage}_sent"
    try:
        client = _get_client()
        resp = await client.patch(
            f"{_BASE_URL}/wholesale_inquiries",
            headers={**_HEADERS, "Prefer": "return=minimal"},
            params={"id": f"eq.{inquiry_id}"},
            json={column: datetime.now(timezone.utc).isoformat()},
        )
        resp.raise_for_status()
        return True
    except Exception as e:
        logger.warning(f"Failed to mark followup {stage} for {inquiry_id}: {e}")
        return False


# ----------------------------------------------------------------
# CONTACT INQUIRIES (Shopify contact page)
# ----------------------------------------------------------------

async def create_contact_inquiry(
    inquiry_type: str, name: str, email: str,
    company: str = "", phone: str = "",
    business_type: str = "", monthly_volume: str = "",
    preferred_dates: list[str] | None = None,
    message: str = "", language: str = "en",
) -> Optional[dict]:
    """Insert a contact inquiry from the Shopify contact page."""
    if not _is_configured():
        return None
    _init()
    try:
        client = _get_client()
        resp = await client.post(
            f"{_BASE_URL}/contact_inquiries",
            headers={**_HEADERS, "Prefer": "return=representation"},
            json={
                "inquiry_type": inquiry_type, "name": name, "email": email,
                "company": company, "phone": phone,
                "business_type": business_type, "monthly_volume": monthly_volume,
                "preferred_dates": preferred_dates or [],
                "message": message, "language": language,
            },
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.warning(f"Failed to create contact inquiry: {e}", exc_info=True)
        return None


# ----------------------------------------------------------------
# AUTOMATION DATA (WS34-41)
# ----------------------------------------------------------------

async def _upsert_automation(table: str, payload: dict) -> Optional[dict]:
    """Generic upsert to an automation table. Silently skips if unconfigured."""
    if not _is_configured():
        return None
    _init()
    try:
        client = _get_client()
        resp = await client.post(
            f"{_BASE_URL}/{table}",
            headers={**_HEADERS, "Prefer": "return=representation,resolution=merge-duplicates"},
            json=payload,
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.debug(f"Automation upsert to {table} failed: {e}")
        return None


async def store_citation(data: dict) -> Optional[dict]:
    """WS35: Store AI citation monitoring result."""
    return await _upsert_automation("citation_logs", data)


async def store_competitor_data(data: dict) -> Optional[dict]:
    """WS36: Store competitor monitoring result."""
    return await _upsert_automation("competitor_data", data)


async def store_social_mention(data: dict) -> Optional[dict]:
    """WS39: Store social media mention."""
    return await _upsert_automation("social_mentions", data)


async def store_seo_ranking(data: dict) -> Optional[dict]:
    """WS40: Store SEO ranking result."""
    return await _upsert_automation("seo_rankings", data)


async def get_automation_stats() -> dict:
    """Get automation summary stats for admin dashboard."""
    if not _is_configured():
        return {}
    _init()
    stats: dict = {}
    client = _get_client()

    for table, key in [
        ("citation_logs", "citations"),
        ("social_mentions", "social_mentions"),
        ("seo_rankings", "seo_rankings"),
        ("competitor_data", "competitor_checks"),
    ]:
        try:
            resp = await client.get(
                f"{_BASE_URL}/{table}",
                headers={**_HEADERS, "Prefer": "count=exact"},
                params={"select": "id", "limit": "0"},
            )
            count = int(resp.headers.get("content-range", "0/0").split("/")[-1])
            stats[key] = count
        except Exception as e:
            logger.warning(f"Failed to fetch {key} count: {e}")
            stats[key] = 0

    # Share of Model: % of citations where nakai_cited=true
    try:
        resp = await client.get(
            f"{_BASE_URL}/citation_logs",
            headers={**_HEADERS, "Prefer": "count=exact"},
            params={"select": "id", "nakai_cited": "eq.true", "limit": "0"},
        )
        cited = int(resp.headers.get("content-range", "0/0").split("/")[-1])
        total = stats.get("citations", 0)
        stats["share_of_model"] = round(cited / total * 100, 1) if total else 0
        stats["nakai_cited"] = cited
    except Exception as e:
        logger.warning(f"Failed to fetch share_of_model: {e}")
        stats["share_of_model"] = 0
        stats["nakai_cited"] = 0

    # Latest social mentions
    try:
        resp = await client.get(
            f"{_BASE_URL}/social_mentions",
            headers=_HEADERS,
            params={"order": "timestamp.desc", "limit": "5"},
        )
        stats["recent_mentions"] = resp.json()
    except Exception as e:
        logger.warning(f"Failed to fetch recent_mentions: {e}")
        stats["recent_mentions"] = []

    # Citation trend: daily counts for last 30 days
    try:
        resp = await client.get(
            f"{_BASE_URL}/citation_logs",
            headers=_HEADERS,
            params={
                "select": "checked_at,nakai_cited",
                "order": "checked_at.desc",
                "limit": "500",
            },
        )
        rows = resp.json()
        daily_cited: dict = {}
        daily_total: dict = {}
        for row in rows:
            day = str(row.get("checked_at", ""))[:10]
            if not day:
                continue
            daily_total[day] = daily_total.get(day, 0) + 1
            if row.get("nakai_cited"):
                daily_cited[day] = daily_cited.get(day, 0) + 1
        # Build trend as list of {date, cited, total, pct}
        trend = []
        for day in sorted(daily_total.keys())[-30:]:
            c = daily_cited.get(day, 0)
            t = daily_total.get(day, 0)
            trend.append({
                "date": day,
                "cited": c,
                "total": t,
                "pct": round(c / t * 100, 1) if t else 0,
            })
        stats["citation_trend"] = trend
    except Exception as e:
        logger.warning(f"Failed to fetch citation_trend: {e}")
        stats["citation_trend"] = []

    # Top cited queries
    try:
        resp = await client.get(
            f"{_BASE_URL}/citation_logs",
            headers=_HEADERS,
            params={
                "select": "query,nakai_cited",
                "nakai_cited": "eq.true",
                "order": "checked_at.desc",
                "limit": "20",
            },
        )
        rows = resp.json()
        query_counts: dict = {}
        for row in rows:
            q = row.get("query", "unknown")
            query_counts[q] = query_counts.get(q, 0) + 1
        top_queries = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        stats["top_cited_queries"] = [{"query": q, "count": c} for q, c in top_queries]
    except Exception as e:
        logger.warning(f"Failed to fetch top_cited_queries: {e}")
        stats["top_cited_queries"] = []

    return stats


# ----------------------------------------------------------------
# EMAIL MARKETING: BRAND ASSETS
# ----------------------------------------------------------------

async def get_email_brand_assets() -> Optional[dict]:
    """Get the single NAKAI brand assets row."""
    if not _is_configured():
        return None
    _init()
    try:
        client = _get_client()
        resp = await client.get(
            f"{_BASE_URL}/email_brand_assets",
            headers=_HEADERS,
            params={"limit": "1"},
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.warning(f"Failed to get brand assets: {e}")
        return None


async def upsert_email_brand_assets(data: dict) -> Optional[dict]:
    """Create or update brand assets (single row)."""
    if not _is_configured():
        return None
    _init()
    try:
        client = _get_client()
        existing = await get_email_brand_assets()
        if existing:
            resp = await client.patch(
                f"{_BASE_URL}/email_brand_assets",
                headers={**_HEADERS, "Prefer": "return=representation"},
                params={"id": f"eq.{existing['id']}"},
                json=data,
            )
        else:
            resp = await client.post(
                f"{_BASE_URL}/email_brand_assets",
                headers=_HEADERS,
                json=data,
            )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.warning(f"Failed to upsert brand assets: {e}")
        return None


# ----------------------------------------------------------------
# EMAIL MARKETING: SUBSCRIBERS
# ----------------------------------------------------------------

async def list_email_subscribers(
    tag: str | None = None,
    language: str | None = None,
    active_only: bool = True,
) -> list[dict]:
    if not _is_configured():
        return []
    _init()
    params: dict = {"order": "created_at.desc", "limit": "5000"}
    if active_only:
        params["is_active"] = "eq.true"
    if language:
        params["language"] = f"eq.{language}"
    if tag:
        params["tags"] = f"cs.{{{tag}}}"
    try:
        client = _get_client()
        resp = await client.get(
            f"{_BASE_URL}/email_subscribers",
            headers=_HEADERS,
            params=params,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.warning(f"Failed to list subscribers: {e}")
        return []


async def create_email_subscriber(
    email: str, name: str = "", tags: list[str] | None = None, language: str = "en"
) -> Optional[dict]:
    if not _is_configured():
        return None
    _init()
    try:
        client = _get_client()
        resp = await client.post(
            f"{_BASE_URL}/email_subscribers",
            headers={**_HEADERS, "Prefer": "return=representation,resolution=ignore-duplicates"},
            json={"email": email, "name": name, "tags": tags or [], "language": language},
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.warning(f"Failed to create subscriber: {e}")
        return None


async def update_email_subscriber(sub_id: str, updates: dict) -> Optional[dict]:
    if not _is_configured():
        return None
    _init()
    try:
        client = _get_client()
        resp = await client.patch(
            f"{_BASE_URL}/email_subscribers",
            headers={**_HEADERS, "Prefer": "return=representation"},
            params={"id": f"eq.{sub_id}"},
            json=updates,
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.warning(f"Failed to update subscriber: {e}")
        return None


async def delete_email_subscriber(sub_id: str) -> bool:
    if not _is_configured():
        return False
    _init()
    try:
        client = _get_client()
        resp = await client.delete(
            f"{_BASE_URL}/email_subscribers",
            headers=_HEADERS,
            params={"id": f"eq.{sub_id}"},
        )
        resp.raise_for_status()
        return True
    except Exception as e:
        logger.warning(f"Failed to delete subscriber: {e}")
        return False


async def unsubscribe_by_token(token: str) -> bool:
    """Unsubscribe via token (public endpoint)."""
    if not _is_configured():
        return False
    _init()
    try:
        client = _get_client()
        resp = await client.patch(
            f"{_BASE_URL}/email_subscribers",
            headers={**_HEADERS, "Prefer": "return=representation"},
            params={"unsubscribe_token": f"eq.{token}", "is_active": "eq.true"},
            json={"is_active": False, "unsubscribed_at": datetime.now(timezone.utc).isoformat()},
        )
        resp.raise_for_status()
        rows = resp.json()
        return len(rows) > 0
    except Exception as e:
        logger.warning(f"Failed to unsubscribe: {e}")
        return False


# ----------------------------------------------------------------
# EMAIL MARKETING: CAMPAIGNS
# ----------------------------------------------------------------

async def list_email_campaigns() -> list[dict]:
    if not _is_configured():
        return []
    _init()
    try:
        client = _get_client()
        resp = await client.get(
            f"{_BASE_URL}/email_campaigns",
            headers=_HEADERS,
            params={"order": "created_at.desc", "limit": "100"},
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.warning(f"Failed to list campaigns: {e}")
        return []


async def get_email_campaign(campaign_id: str) -> Optional[dict]:
    if not _is_configured():
        return None
    _init()
    try:
        client = _get_client()
        resp = await client.get(
            f"{_BASE_URL}/email_campaigns",
            headers=_HEADERS,
            params={"id": f"eq.{campaign_id}", "limit": "1"},
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.warning(f"Failed to get campaign: {e}")
        return None


async def create_email_campaign(data: dict) -> Optional[dict]:
    if not _is_configured():
        return None
    _init()
    try:
        client = _get_client()
        resp = await client.post(
            f"{_BASE_URL}/email_campaigns",
            headers=_HEADERS,
            json=data,
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.warning(f"Failed to create campaign: {e}")
        return None


async def update_email_campaign(campaign_id: str, updates: dict) -> Optional[dict]:
    if not _is_configured():
        return None
    _init()
    try:
        client = _get_client()
        resp = await client.patch(
            f"{_BASE_URL}/email_campaigns",
            headers={**_HEADERS, "Prefer": "return=representation"},
            params={"id": f"eq.{campaign_id}"},
            json=updates,
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.warning(f"Failed to update campaign: {e}")
        return None


async def delete_email_campaign(campaign_id: str) -> bool:
    if not _is_configured():
        return False
    _init()
    try:
        client = _get_client()
        resp = await client.delete(
            f"{_BASE_URL}/email_campaigns",
            headers=_HEADERS,
            params={"id": f"eq.{campaign_id}"},
        )
        resp.raise_for_status()
        return True
    except Exception as e:
        logger.warning(f"Failed to delete campaign: {e}")
        return False


# ----------------------------------------------------------------
# EMAIL MARKETING: NEWSLETTER SCHEDULES
# ----------------------------------------------------------------

async def list_newsletter_schedules(active_only: bool = False) -> list[dict]:
    if not _is_configured():
        return []
    _init()
    params: dict = {"order": "created_at.desc", "limit": "100"}
    if active_only:
        params["is_active"] = "eq.true"
    try:
        client = _get_client()
        resp = await client.get(
            f"{_BASE_URL}/newsletter_schedules",
            headers=_HEADERS,
            params=params,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.warning(f"Failed to list newsletter schedules: {e}")
        return []


async def get_newsletter_schedule(schedule_id: str) -> Optional[dict]:
    if not _is_configured():
        return None
    _init()
    try:
        client = _get_client()
        resp = await client.get(
            f"{_BASE_URL}/newsletter_schedules",
            headers=_HEADERS,
            params={"id": f"eq.{schedule_id}", "limit": "1"},
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.warning(f"Failed to get newsletter schedule: {e}")
        return None


async def create_newsletter_schedule(data: dict) -> Optional[dict]:
    if not _is_configured():
        return None
    _init()
    try:
        client = _get_client()
        resp = await client.post(
            f"{_BASE_URL}/newsletter_schedules",
            headers=_HEADERS,
            json=data,
        )
        if resp.status_code >= 400:
            logger.error(f"Supabase newsletter_schedules POST {resp.status_code}: {resp.text}")
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.warning(f"Failed to create newsletter schedule: {e}")
        return None


async def update_newsletter_schedule(schedule_id: str, updates: dict) -> Optional[dict]:
    if not _is_configured():
        return None
    _init()
    try:
        client = _get_client()
        resp = await client.patch(
            f"{_BASE_URL}/newsletter_schedules",
            headers={**_HEADERS, "Prefer": "return=representation"},
            params={"id": f"eq.{schedule_id}"},
            json=updates,
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.warning(f"Failed to update newsletter schedule: {e}")
        return None


async def delete_newsletter_schedule(schedule_id: str) -> bool:
    if not _is_configured():
        return False
    _init()
    try:
        client = _get_client()
        resp = await client.delete(
            f"{_BASE_URL}/newsletter_schedules",
            headers=_HEADERS,
            params={"id": f"eq.{schedule_id}"},
        )
        resp.raise_for_status()
        return True
    except Exception as e:
        logger.warning(f"Failed to delete newsletter schedule: {e}")
        return False


# ----------------------------------------------------------------
# CONTENT SOURCES (brand elements for content generation)
# ----------------------------------------------------------------

async def list_content_sources(active_only: bool = True) -> list[dict]:
    """List content sources, ordered by priority."""
    if not _is_configured():
        return []
    _init()
    params: dict = {"order": "priority.desc,created_at.desc", "limit": "200"}
    if active_only:
        params["is_active"] = "eq.true"
    try:
        client = _get_client()
        resp = await client.get(
            f"{_BASE_URL}/content_sources",
            headers=_HEADERS,
            params=params,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.warning(f"Failed to list content sources: {e}")
        return []


async def create_content_source(data: dict) -> Optional[dict]:
    if not _is_configured():
        return None
    _init()
    try:
        client = _get_client()
        resp = await client.post(
            f"{_BASE_URL}/content_sources",
            headers=_HEADERS,
            json=data,
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.warning(f"Failed to create content source: {e}")
        return None


async def update_content_source(source_id: str, updates: dict) -> Optional[dict]:
    if not _is_configured():
        return None
    _init()
    try:
        client = _get_client()
        resp = await client.patch(
            f"{_BASE_URL}/content_sources",
            headers={**_HEADERS, "Prefer": "return=representation"},
            params={"id": f"eq.{source_id}"},
            json=updates,
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.warning(f"Failed to update content source: {e}")
        return None


async def delete_content_source(source_id: str) -> bool:
    if not _is_configured():
        return False
    _init()
    try:
        client = _get_client()
        resp = await client.delete(
            f"{_BASE_URL}/content_sources",
            headers=_HEADERS,
            params={"id": f"eq.{source_id}"},
        )
        resp.raise_for_status()
        return True
    except Exception as e:
        logger.warning(f"Failed to delete content source: {e}")
        return False


# ----------------------------------------------------------------
# VIDEO SCRIPTS
# ----------------------------------------------------------------

async def list_video_scripts(limit: int = 30) -> list[dict]:
    if not _is_configured():
        return []
    _init()
    try:
        client = _get_client()
        resp = await client.get(
            f"{_BASE_URL}/video_scripts",
            headers=_HEADERS,
            params={"order": "created_at.desc", "limit": str(limit)},
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.warning(f"Failed to list video scripts: {e}")
        return []
