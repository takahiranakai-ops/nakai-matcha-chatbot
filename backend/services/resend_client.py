"""Resend API wrapper for bulk email sending."""

import logging
from typing import Optional

import httpx

from config import settings

logger = logging.getLogger(__name__)

RESEND_API = "https://api.resend.com"
FROM_EMAIL = "NAKAI Matcha <hello@nakaimatcha.com>"
REPLY_TO = "contact@nakaiinfo.com"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.resend_api_key}",
        "Content-Type": "application/json",
    }


async def send_email(
    to: str,
    subject: str,
    html: str,
    from_email: str = FROM_EMAIL,
    reply_to: str = REPLY_TO,
    extra_headers: Optional[dict] = None,
) -> Optional[dict]:
    """Send a single email via Resend API."""
    if not settings.resend_api_key:
        logger.warning("Resend API key not configured")
        return None
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{RESEND_API}/emails",
                headers=_headers(),
                json={
                    "from": from_email,
                    "to": [to],
                    "subject": subject,
                    "html": html,
                    "reply_to": reply_to,
                    "headers": extra_headers or {},
                },
            )
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.error(f"Resend send failed: {e}")
        return None


async def send_batch(emails: list[dict]) -> list[dict]:
    """Send batch via Resend batch API (up to 100 per call).

    Each item: {"from", "to" (list), "subject", "html", "reply_to", "headers"}
    """
    if not settings.resend_api_key:
        logger.warning("Resend API key not configured")
        return []
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{RESEND_API}/emails/batch",
                headers=_headers(),
                json=emails,
            )
            resp.raise_for_status()
            return resp.json().get("data", [])
    except Exception as e:
        logger.error(f"Resend batch send failed: {e}")
        return []
