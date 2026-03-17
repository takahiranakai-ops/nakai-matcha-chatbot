"""Newsletter scheduler — checks due schedules and sends AI-generated content."""

import asyncio
import logging
from datetime import datetime, timezone

from services import supabase_client, resend_client
from services.email_ai import generate_email_design, NEWSLETTER_TEMPLATES

logger = logging.getLogger(__name__)

BASE_URL = "https://nakai-matcha-chat.onrender.com"


def _is_due(schedule: dict, now: datetime) -> bool:
    """Check if a newsletter schedule should fire now."""
    if not schedule.get("is_active"):
        return False

    weekday_js = (now.weekday() + 1) % 7  # Python Mon=0 -> JS Sun=0
    days = schedule.get("days_of_week") or []
    if weekday_js not in days:
        return False

    send_time = schedule.get("send_time_utc", "14:00")
    try:
        target_hour, target_min = int(send_time.split(":")[0]), int(send_time.split(":")[1])
    except (ValueError, IndexError):
        target_hour, target_min = 14, 0

    # Must be within the target hour (scheduler runs every 10 min)
    if now.hour != target_hour:
        return False

    # Prevent double-send: must be >20 hours since last send
    last_sent = schedule.get("last_sent_at")
    if last_sent:
        if isinstance(last_sent, str):
            try:
                last_sent = datetime.fromisoformat(last_sent.replace("Z", "+00:00"))
            except ValueError:
                last_sent = None
        if last_sent and (now - last_sent).total_seconds() < 20 * 3600:
            return False

    return True


async def _generate_and_send(schedule: dict):
    """Generate AI content from template and send to matching subscribers."""
    schedule_id = schedule["id"]
    template_key = schedule.get("template_key", "")
    custom_prompt = schedule.get("custom_prompt", "")
    target_tags = schedule.get("target_tags") or []
    language = schedule.get("target_language", "en")

    # Build the prompt
    template = NEWSLETTER_TEMPLATES.get(template_key)
    if template:
        prompt = template["prompt"]
        subject_prefix = template.get("subject_prefix", "NAKAI Matcha")
    elif custom_prompt:
        prompt = custom_prompt
        subject_prefix = schedule.get("name", "NAKAI Matcha")
    else:
        logger.warning(f"[NEWSLETTER] Schedule {schedule_id} has no template or custom prompt")
        return

    # Add date context for variety
    now = datetime.now(timezone.utc)
    date_hint = now.strftime("%B %d, %Y")
    prompt += f"\n\nToday is {date_hint}. Make this edition unique and fresh."

    # Get brand assets
    brand_assets = await supabase_client.get_email_brand_assets() or {
        "logo_url": "",
        "colors": {"primary": "#406546", "secondary": "#F9F0E2", "text": "#1a1a1a"},
        "font_family": "Work Sans, Helvetica, Arial, sans-serif",
        "photos": [],
    }

    # Generate HTML
    html = await generate_email_design(
        description=prompt,
        brand_assets=brand_assets,
        language=language,
    )

    subject = f"{subject_prefix} — {now.strftime('%b %d')}"

    # Record as campaign for history
    campaign = await supabase_client.create_email_campaign({
        "name": f"[Auto] {schedule.get('name', 'Newsletter')} — {date_hint}",
        "description": prompt[:500],
        "subject": subject,
        "html_content": html,
        "status": "sending",
        "target_tags": target_tags,
        "target_language": language,
    })

    # Fetch subscribers
    tag = target_tags[0] if target_tags else None
    subscribers = await supabase_client.list_email_subscribers(
        tag=tag, language=language if language else None,
    )

    if not subscribers:
        logger.info(f"[NEWSLETTER] No subscribers for schedule {schedule_id}")
        if campaign:
            await supabase_client.update_email_campaign(campaign["id"], {
                "status": "sent",
                "sent_at": now.isoformat(),
                "stats": {"total": 0, "sent": 0, "failed": 0},
            })
        await supabase_client.update_newsletter_schedule(schedule_id, {
            "last_sent_at": now.isoformat(),
        })
        return

    # Bulk send (reusing same pattern as _execute_bulk_send)
    sent = 0
    failed = 0
    batch = []

    for sub in subscribers:
        sub_html = html.replace(
            "{{unsubscribe_url}}",
            f"{BASE_URL}/api/email/unsubscribe?token={sub.get('unsubscribe_token', '')}"
        )
        batch.append({
            "from": "NAKAI Matcha <hello@nakaimatcha.com>",
            "to": [sub["email"]],
            "subject": subject,
            "html": sub_html,
            "reply_to": "contact@nakaiinfo.com",
            "headers": {
                "List-Unsubscribe": f"<{BASE_URL}/api/email/unsubscribe?token={sub.get('unsubscribe_token', '')}>",
                "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
            },
        })

        if len(batch) >= 50:
            results = await resend_client.send_batch(batch)
            sent += len(results)
            if len(results) < len(batch):
                failed += len(batch) - len(results)
            batch = []
            await asyncio.sleep(1)

    if batch:
        results = await resend_client.send_batch(batch)
        sent += len(results)
        if len(results) < len(batch):
            failed += len(batch) - len(results)

    # Update campaign record
    if campaign:
        await supabase_client.update_email_campaign(campaign["id"], {
            "status": "sent",
            "sent_at": now.isoformat(),
            "stats": {"total": len(subscribers), "sent": sent, "failed": failed},
        })

    # Update schedule last_sent_at
    await supabase_client.update_newsletter_schedule(schedule_id, {
        "last_sent_at": now.isoformat(),
    })

    logger.info(f"[NEWSLETTER] Sent '{schedule.get('name')}' to {sent}/{len(subscribers)} subscribers")


async def check_and_send_due_newsletters():
    """Main entry point: check all active schedules and send if due."""
    schedules = await supabase_client.list_newsletter_schedules(active_only=True)
    if not schedules:
        return

    now = datetime.now(timezone.utc)

    for schedule in schedules:
        if _is_due(schedule, now):
            try:
                logger.info(f"[NEWSLETTER] Triggering: {schedule.get('name')}")
                await _generate_and_send(schedule)
            except Exception as e:
                logger.error(f"[NEWSLETTER] Failed to send {schedule.get('name')}: {e}", exc_info=True)
