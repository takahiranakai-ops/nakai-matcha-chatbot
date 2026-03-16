"""B2B Daily Pipeline — Orchestrates the full outreach cycle.

Runs daily via scheduler. Coordinates all 32 virtual team members.
"""

import logging
from datetime import datetime, timezone

from services import supabase_client

logger = logging.getLogger(__name__)


async def run_daily_pipeline() -> dict:
    """Execute the full daily B2B pipeline.

    Steps:
    1. Discover new cafés (Lead Researchers #1-8)
    2. Find emails for researched leads (Email Hunters #9-12)
    3. Verify unverified emails (Verifiers #13-14)
    4. Generate outreach emails (Copywriters #15-20)
    5. Send emails (Executors #21-24)
    6. Record daily stats (Analytics #25-27)

    Returns summary dict.
    """
    from config import settings
    if not settings.b2b_enabled:
        logger.info("[B2B] Pipeline disabled (b2b_enabled=false)")
        return {"status": "disabled"}

    logger.info("[B2B] === Daily Pipeline Started ===")
    stats = {
        "leads_added": 0,
        "emails_found": 0,
        "emails_verified": 0,
        "emails_generated": 0,
        "emails_sent": 0,
    }

    # Step 1: Discover new cafés
    try:
        from services.b2b.lead_researcher import search_region, REGIONS

        day = datetime.now(timezone.utc).timetuple().tm_yday
        region_keys = list(REGIONS.keys())
        # Rotate: 2 regions per day
        r1 = region_keys[day % len(region_keys)]
        r2 = region_keys[(day + 1) % len(region_keys)]

        for region_key in (r1, r2):
            results = await search_region(region_key, max_cities=2)
            stats["leads_added"] += len(results)
            logger.info(f"[B2B] Region {region_key}: {len(results)} new leads")

    except Exception as e:
        logger.error(f"[B2B] Lead discovery failed: {e}", exc_info=True)

    # Step 2: Find emails for leads without contacts
    try:
        from services.b2b.email_hunter import find_emails_for_lead

        leads_needing_emails = await _get_leads_without_contacts(limit=20)
        for lead in leads_needing_emails:
            contacts = await find_emails_for_lead(lead)
            stats["emails_found"] += len(contacts)

    except Exception as e:
        logger.error(f"[B2B] Email hunting failed: {e}", exc_info=True)

    # Step 3: Verify unverified emails
    try:
        from services.b2b.email_verifier import verify_batch
        verified = await verify_batch(max_contacts=50)
        stats["emails_verified"] = verified
    except Exception as e:
        logger.error(f"[B2B] Email verification failed: {e}", exc_info=True)

    # Step 4 & 5: Generate and send outreach
    try:
        from services.b2b.outreach_writer import generate_outreach_email
        from services.b2b.outreach_executor import send_outreach

        # Get leads ready for outreach (have verified contacts, not yet contacted)
        ready_leads = await _get_leads_ready_for_outreach(limit=settings.b2b_daily_send_limit)

        for lead, contact, step in ready_leads:
            email = await generate_outreach_email(lead, step)
            stats["emails_generated"] += 1

            result = await send_outreach(
                lead=lead,
                contact=contact,
                subject=email["subject"],
                html=email["html"],
                sequence_step=step,
            )
            if result:
                stats["emails_sent"] += 1

    except Exception as e:
        logger.error(f"[B2B] Outreach failed: {e}", exc_info=True)

    # Step 6: Record daily stats
    try:
        from services.b2b.analytics import record_daily_stats
        await record_daily_stats(stats)
    except Exception as e:
        logger.error(f"[B2B] Stats recording failed: {e}", exc_info=True)

    logger.info(f"[B2B] === Pipeline Complete: {stats} ===")
    return stats


async def run_test_pipeline(lead_id: str | None = None) -> dict:
    """Run pipeline for a single lead (testing)."""
    if not supabase_client._is_configured():
        return {"error": "Supabase not configured"}
    supabase_client._init()

    try:
        client = supabase_client._get_client()

        # Get a lead
        params = {"limit": "1", "order": "created_at.desc"}
        if lead_id:
            params["id"] = f"eq.{lead_id}"
        resp = await client.get(
            f"{supabase_client._BASE_URL}/b2b_leads",
            headers=supabase_client._HEADERS,
            params=params,
        )
        leads = resp.json()
        if not leads:
            return {"error": "No leads found"}

        lead = leads[0]
        result = {"lead": lead["name"]}

        # Find emails
        from services.b2b.email_hunter import find_emails_for_lead
        contacts = await find_emails_for_lead(lead)
        result["contacts_found"] = len(contacts)

        # Generate email (don't send)
        if contacts:
            from services.b2b.outreach_writer import generate_outreach_email
            email = await generate_outreach_email(lead, step=1)
            result["generated_subject"] = email["subject"]
            result["generated_html_length"] = len(email["html"])

        return result

    except Exception as e:
        return {"error": str(e)}


async def _get_leads_without_contacts(limit: int = 20) -> list[dict]:
    """Get leads that have no contacts yet."""
    if not supabase_client._is_configured():
        return []
    supabase_client._init()
    try:
        client = supabase_client._get_client()
        # Get leads
        resp = await client.get(
            f"{supabase_client._BASE_URL}/b2b_leads",
            headers=supabase_client._HEADERS,
            params={
                "status": "eq.new",
                "website": "neq.",
                "order": "created_at.desc",
                "limit": str(limit),
            },
        )
        leads = resp.json()

        # Filter out those that already have contacts
        result = []
        for lead in leads:
            resp2 = await client.get(
                f"{supabase_client._BASE_URL}/b2b_contacts",
                headers={**supabase_client._HEADERS, "Prefer": "count=exact"},
                params={"lead_id": f"eq.{lead['id']}", "select": "id", "limit": "0"},
            )
            count = int(resp2.headers.get("content-range", "0/0").split("/")[-1])
            if count == 0:
                result.append(lead)

        return result
    except Exception as e:
        logger.error(f"[B2B] Failed to get leads without contacts: {e}")
        return []


async def _get_leads_ready_for_outreach(limit: int = 50) -> list[tuple[dict, dict, int]]:
    """Get leads ready for outreach: have verified contacts, determine next step.

    Returns list of (lead, contact, step_number).
    """
    if not supabase_client._is_configured():
        return []
    supabase_client._init()

    try:
        client = supabase_client._get_client()

        # Leads with verified contacts that haven't been fully sequenced
        resp = await client.get(
            f"{supabase_client._BASE_URL}/b2b_contacts",
            headers=supabase_client._HEADERS,
            params={
                "verified": "eq.true",
                "order": "created_at.asc",
                "limit": str(limit * 2),
                "select": "id,lead_id,email",
            },
        )
        contacts = resp.json()

        results = []
        seen_leads = set()

        for contact in contacts:
            lead_id = contact.get("lead_id")
            if not lead_id or lead_id in seen_leads:
                continue

            # Get lead
            resp2 = await client.get(
                f"{supabase_client._BASE_URL}/b2b_leads",
                headers=supabase_client._HEADERS,
                params={"id": f"eq.{lead_id}", "limit": "1"},
            )
            leads = resp2.json()
            if not leads:
                continue
            lead = leads[0]

            # Skip if won/lost
            if lead.get("status") in ("won", "lost"):
                continue

            # Determine next step
            resp3 = await client.get(
                f"{supabase_client._BASE_URL}/b2b_outreach",
                headers=supabase_client._HEADERS,
                params={
                    "contact_id": f"eq.{contact['id']}",
                    "order": "sequence_step.desc",
                    "limit": "1",
                },
            )
            outreach_records = resp3.json()

            if not outreach_records:
                next_step = 1
            else:
                last = outreach_records[0]
                last_step = last.get("sequence_step", 0)
                if last_step >= 3:
                    continue  # Fully sequenced
                # Check delay (5 days for step 2, 12 for step 3)
                from datetime import datetime, timezone, timedelta
                sent_at = last.get("sent_at", "")
                if sent_at:
                    sent_dt = datetime.fromisoformat(sent_at.replace("Z", "+00:00"))
                    delay = 5 if last_step == 1 else 7
                    if datetime.now(timezone.utc) - sent_dt < timedelta(days=delay):
                        continue  # Too soon
                next_step = last_step + 1

            seen_leads.add(lead_id)
            results.append((lead, contact, next_step))

            if len(results) >= limit:
                break

        return results

    except Exception as e:
        logger.error(f"[B2B] Failed to get ready leads: {e}")
        return []
