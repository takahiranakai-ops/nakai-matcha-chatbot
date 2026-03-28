"""Resend API wrapper for bulk email sending with retry."""

import asyncio
import logging
from typing import Optional

import httpx

from config import settings

logger = logging.getLogger(__name__)

RESEND_API = "https://api.resend.com"
FROM_EMAIL = "NAKAI Matcha <wholesale@nakaiinfo.com>"
REPLY_TO = "contact@nakaiinfo.com"

MAX_RETRIES = 3
RETRY_DELAYS = [2, 5, 15]


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
    attachments: Optional[list[dict]] = None,
) -> Optional[dict]:
    """Send a single email via Resend API with retry on transient errors.

    attachments: list of {"filename": str, "content": str (base64)}
    """
    if not settings.resend_api_key:
        logger.warning("Resend API key not configured")
        return None

    payload = {
        "from": from_email,
        "to": [to],
        "subject": subject,
        "html": html,
        "reply_to": reply_to,
        "headers": extra_headers or {},
    }
    if attachments:
        payload["attachments"] = attachments

    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{RESEND_API}/emails",
                    headers=_headers(),
                    json=payload,
                )
                if resp.status_code < 400:
                    return resp.json()
                # Retry on rate limit and server errors
                if resp.status_code in (429, 500, 502, 503) and attempt < MAX_RETRIES - 1:
                    delay = RETRY_DELAYS[attempt]
                    logger.warning(f"Resend {resp.status_code}, retry {attempt+1} in {delay}s")
                    await asyncio.sleep(delay)
                    continue
                logger.error(f"Resend API {resp.status_code}: {resp.text}")
                return None
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_DELAYS[attempt]
                logger.warning(f"Resend network error, retry {attempt+1} in {delay}s: {e}")
                await asyncio.sleep(delay)
                continue
            logger.error(f"Resend send failed after {MAX_RETRIES} attempts: {e}")
            return None
        except Exception as e:
            logger.error(f"Resend send failed: {e}")
            return None
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
