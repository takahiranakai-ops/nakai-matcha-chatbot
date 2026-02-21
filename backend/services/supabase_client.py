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


def _init():
    global _HEADERS, _BASE_URL
    if _HEADERS:
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
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{_BASE_URL}/conversations",
                headers=_HEADERS,
                json=payload,
            )
            resp.raise_for_status()
            rows = resp.json()
            return rows[0] if rows else None
    except Exception as e:
        logger.warning(f"Failed to create conversation: {e}")
        return None


async def get_conversation_by_session(
    session_id: str, source: str = "pwa"
) -> Optional[dict]:
    if not _is_configured():
        return None
    _init()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
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
        logger.warning(f"Failed to get conversation: {e}")
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
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{_BASE_URL}/messages",
                headers=_HEADERS,
                json=payload,
            )
            resp.raise_for_status()
            rows = resp.json()
            return rows[0] if rows else None
    except Exception as e:
        logger.warning(f"Failed to log message: {e}")
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
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{_BASE_URL}/knowledge_articles",
                headers=_HEADERS,
                params=params,
            )
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.warning(f"Failed to list articles: {e}")
        return []


async def get_article(article_id: str) -> Optional[dict]:
    if not _is_configured():
        return None
    _init()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{_BASE_URL}/knowledge_articles",
                headers=_HEADERS,
                params={"id": f"eq.{article_id}", "limit": "1"},
            )
            resp.raise_for_status()
            rows = resp.json()
            return rows[0] if rows else None
    except Exception as e:
        logger.warning(f"Failed to get article: {e}")
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
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{_BASE_URL}/knowledge_articles",
                headers=_HEADERS,
                json=payload,
            )
            resp.raise_for_status()
            rows = resp.json()
            return rows[0] if rows else None
    except Exception as e:
        logger.warning(f"Failed to create article: {e}")
        return None


async def update_article(article_id: str, updates: dict) -> Optional[dict]:
    if not _is_configured():
        return None
    _init()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
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
        logger.warning(f"Failed to update article: {e}")
        return None


async def delete_article(article_id: str) -> bool:
    if not _is_configured():
        return False
    _init()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.delete(
                f"{_BASE_URL}/knowledge_articles",
                headers=_HEADERS,
                params={"id": f"eq.{article_id}"},
            )
            resp.raise_for_status()
            return True
    except Exception as e:
        logger.warning(f"Failed to delete article: {e}")
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
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{_BASE_URL}/conversations",
                headers=_HEADERS,
                params=params,
            )
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.warning(f"Failed to list conversations: {e}")
        return []


async def get_conversation_messages(conversation_id: str) -> list[dict]:
    if not _is_configured():
        return []
    _init()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
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
        logger.warning(f"Failed to get messages: {e}")
        return []


async def get_analytics_summary() -> dict:
    if not _is_configured():
        return {}
    _init()
    summary: dict = {}
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
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
        logger.warning(f"Analytics summary failed: {e}")
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
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{_BASE_URL}/wholesale_leads",
                headers={**_HEADERS, "Prefer": "return=representation,resolution=ignore-duplicates"},
                json={"email": email, "session_id": session_id},
            )
            resp.raise_for_status()
            rows = resp.json()
            return rows[0] if rows else None
    except Exception as e:
        logger.warning(f"Failed to create wholesale lead: {e}")
        return None


async def list_wholesale_leads() -> list[dict]:
    if not _is_configured():
        return []
    _init()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{_BASE_URL}/wholesale_leads",
                headers=_HEADERS,
                params={"order": "created_at.desc", "limit": "500"},
            )
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.warning(f"Failed to list wholesale leads: {e}")
        return []


async def delete_wholesale_lead(lead_id: str) -> bool:
    if not _is_configured():
        return False
    _init()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.delete(
                f"{_BASE_URL}/wholesale_leads",
                headers=_HEADERS,
                params={"id": f"eq.{lead_id}"},
            )
            resp.raise_for_status()
            return True
    except Exception as e:
        logger.warning(f"Failed to delete wholesale lead: {e}")
        return False
