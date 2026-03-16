"""B2B Outreach Executor — Sends emails via Resend with rate limiting.

Virtual Team Members #21-24: Outreach Executors.
Handles sending, tracking, and CAN-SPAM compliance.
"""

import asyncio
import logging
import random
from datetime import datetime, timezone

from config import settings
from services import resend_client, supabase_client

logger = logging.getLogger(__name__)

BASE_URL = "https://matcha.ai"


async def send_outreach(
    lead: dict,
    contact: dict,
    subject: str,
    html: str,
    sequence_step: int = 1,
) -> dict | None:
    """Send a single outreach email and record it.

    Returns the outreach record or None on failure.
    """
    email = contact.get("email", "")
    if not email:
        return None

    # Check daily send limit
    today_count = await _get_today_send_count()
    if today_count >= settings.b2b_daily_send_limit:
        logger.warning(f"[B2B] Daily send limit ({settings.b2b_daily_send_limit}) reached")
        return None

    # Check unsubscribe list
    if await _is_unsubscribed(email):
        logger.debug(f"[B2B] Skipping unsubscribed: {email}")
        return None

    # Add unsubscribe link
    unsub_url = f"{BASE_URL}/api/b2b/unsubscribe?email={email}"
    html_with_unsub = html.replace("{{unsubscribe_link}}", unsub_url)

    # Get PDF attachment if available
    from api.b2b_routes import _get_active_attachment
    attachments = await _get_active_attachment()

    # Send via Resend
    from_email = f"Takahiro from NAKAI <{settings.b2b_from_email}>"
    result = await resend_client.send_email(
        to=email,
        subject=subject,
        html=html_with_unsub,
        from_email=from_email,
        reply_to=settings.b2b_reply_to,
        attachments=attachments,
    )

    if not result:
        logger.error(f"[B2B] Failed to send to {email}")
        return None

    resend_id = result.get("id", "")

    # Record outreach
    outreach = await _record_outreach(
        lead_id=lead["id"],
        contact_id=contact["id"],
        sequence_step=sequence_step,
        subject=subject,
        html=html_with_unsub,
        resend_email_id=resend_id,
    )

    # Update lead status
    if lead.get("status") == "new" or lead.get("status") == "researched":
        await _update_lead_status(lead["id"], "contacted")

    logger.info(f"[B2B] Sent step {sequence_step} to {email} (resend: {resend_id})")
    return outreach


async def send_batch(
    items: list[dict],
) -> int:
    """Send a batch of outreach emails with random delays.

    Each item: {"lead": dict, "contact": dict, "subject": str, "html": str, "step": int}
    Returns count of successfully sent emails.
    """
    sent = 0
    for item in items:
        result = await send_outreach(
            lead=item["lead"],
            contact=item["contact"],
            subject=item["subject"],
            html=item["html"],
            sequence_step=item.get("step", 1),
        )
        if result:
            sent += 1

        # Random delay between sends (30-90 seconds)
        delay = random.uniform(30, 90)
        await asyncio.sleep(delay)

    return sent


async def handle_webhook_event(event_type: str, data: dict) -> bool:
    """Handle Resend webhook events for tracking.

    Event types: email.opened, email.clicked, email.bounced, email.complained
    """
    resend_id = data.get("email_id", "")
    if not resend_id:
        return False

    if not supabase_client._is_configured():
        return False
    supabase_client._init()

    now = datetime.now(timezone.utc).isoformat()
    updates = {}

    if event_type == "email.opened":
        updates = {"opened_at": now, "status": "opened"}
    elif event_type == "email.clicked":
        updates = {"clicked_at": now, "status": "clicked"}
    elif event_type == "email.bounced":
        updates = {"bounced_at": now, "status": "bounced"}
    elif event_type == "email.complained":
        updates = {"status": "unsubscribed"}
        # Also add to unsubscribe list
        email_addr = data.get("to", [""])[0] if data.get("to") else ""
        if email_addr:
            await _add_unsubscribe(email_addr)

    if not updates:
        return False

    try:
        client = supabase_client._get_client()
        resp = await client.patch(
            f"{supabase_client._BASE_URL}/b2b_outreach",
            headers={**supabase_client._HEADERS, "Prefer": "return=minimal"},
            params={"resend_email_id": f"eq.{resend_id}"},
            json=updates,
        )
        resp.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"[B2B] Webhook update failed: {e}")
        return False


async def _record_outreach(
    lead_id: str, contact_id: str, sequence_step: int,
    subject: str, html: str, resend_email_id: str,
) -> dict | None:
    if not supabase_client._is_configured():
        return None
    supabase_client._init()
    try:
        client = supabase_client._get_client()
        resp = await client.post(
            f"{supabase_client._BASE_URL}/b2b_outreach",
            headers={**supabase_client._HEADERS, "Prefer": "return=representation"},
            json={
                "lead_id": lead_id,
                "contact_id": contact_id,
                "sequence_step": sequence_step,
                "subject": subject,
                "html_content": html,
                "resend_email_id": resend_email_id,
                "status": "sent",
                "sent_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else None
    except Exception as e:
        logger.error(f"[B2B] Outreach record failed: {e}")
        return None


async def _update_lead_status(lead_id: str, status: str) -> None:
    if not supabase_client._is_configured():
        return
    supabase_client._init()
    try:
        client = supabase_client._get_client()
        await client.patch(
            f"{supabase_client._BASE_URL}/b2b_leads",
            headers={**supabase_client._HEADERS, "Prefer": "return=minimal"},
            params={"id": f"eq.{lead_id}"},
            json={"status": status, "updated_at": datetime.now(timezone.utc).isoformat()},
        )
    except Exception:
        pass


async def _get_today_send_count() -> int:
    if not supabase_client._is_configured():
        return 0
    supabase_client._init()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    try:
        client = supabase_client._get_client()
        resp = await client.get(
            f"{supabase_client._BASE_URL}/b2b_outreach",
            headers={**supabase_client._HEADERS, "Prefer": "count=exact"},
            params={
                "select": "id",
                "sent_at": f"gte.{today}T00:00:00Z",
                "limit": "0",
            },
        )
        return int(resp.headers.get("content-range", "0/0").split("/")[-1])
    except Exception:
        return 0


async def _is_unsubscribed(email: str) -> bool:
    if not supabase_client._is_configured():
        return False
    supabase_client._init()
    try:
        client = supabase_client._get_client()
        resp = await client.get(
            f"{supabase_client._BASE_URL}/b2b_unsubscribes",
            headers=supabase_client._HEADERS,
            params={"email": f"eq.{email}", "limit": "1"},
        )
        return bool(resp.json())
    except Exception:
        return False


async def _add_unsubscribe(email: str) -> None:
    if not supabase_client._is_configured():
        return
    supabase_client._init()
    try:
        client = supabase_client._get_client()
        await client.post(
            f"{supabase_client._BASE_URL}/b2b_unsubscribes",
            headers={
                **supabase_client._HEADERS,
                "Prefer": "return=minimal,resolution=ignore-duplicates",
            },
            json={"email": email},
        )
    except Exception:
        pass
