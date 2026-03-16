"""B2B Daily Pipeline — Orchestrates the full outreach cycle.

Runs daily via scheduler. Coordinates all 32 virtual team members.
"""

import logging
from datetime import datetime, timezone, timedelta

from services import supabase_client

logger = logging.getLogger(__name__)


async def run_daily_pipeline() -> dict:
    """Execute the full daily B2B pipeline.

    Steps:
    1. Discover new cafes (Lead Researchers #1-8)
    2. Find emails for researched leads (Email Hunters #9-12)
    3. Verify unverified emails (Verifiers #13-14)
    4. Generate outreach emails (Copywriters #15-20)
    5. Send emails via batch API (Executors #21-24)
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

    # Step 1: Discover new cafes
    try:
        from services.b2b.lead_researcher import search_region, REGIONS

        day = datetime.now(timezone.utc).timetuple().tm_yday
        region_keys = list(REGIONS.keys())
        # Rotate: 3 regions/day, 3 cities each, ~100+ leads/day
        indices = [(day + i) % len(region_keys) for i in range(3)]
        daily_regions = [region_keys[i] for i in indices]

        for region_key in daily_regions:
            results = await search_region(region_key, max_cities=3)
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

    # Step 4 & 5: Generate and send outreach (BATCH optimized)
    try:
        from services.b2b.outreach_writer import generate_outreach_email
        from services.b2b.outreach_executor import send_batch_optimized

        ready_leads = await _get_leads_ready_for_outreach(limit=settings.b2b_daily_send_limit)

        batch_items = []
        for lead, contact, step in ready_leads:
            email = await generate_outreach_email(lead, step)
            stats["emails_generated"] += 1
            batch_items.append({
                "lead": lead,
                "contact": contact,
                "subject": email["subject"],
                "html": email["html"],
                "step": step,
            })

        if batch_items:
            sent_count = await send_batch_optimized(batch_items)
            stats["emails_sent"] = sent_count

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
    """Get leads that have no contacts yet (batch query: 2 requests instead of N+1)."""
    if not supabase_client._is_configured():
        return []
    supabase_client._init()
    try:
        client = supabase_client._get_client()
        # Get candidate leads (fetch more than needed since some will have contacts)
        resp = await client.get(
            f"{supabase_client._BASE_URL}/b2b_leads",
            headers=supabase_client._HEADERS,
            params={
                "status": "eq.new",
                "website": "neq.",
                "order": "created_at.desc",
                "limit": str(limit * 3),
            },
        )
        leads = resp.json()
        if not leads:
            return []

        # Batch: get all contacts for these lead IDs in ONE query
        lead_ids = [l["id"] for l in leads]
        ids_str = ",".join(lead_ids)
        resp2 = await client.get(
            f"{supabase_client._BASE_URL}/b2b_contacts",
            headers=supabase_client._HEADERS,
            params={
                "lead_id": f"in.({ids_str})",
                "select": "lead_id",
                "limit": "10000",
            },
        )
        leads_with_contacts = {c["lead_id"] for c in resp2.json()}

        # Filter: only leads without contacts
        result = [l for l in leads if l["id"] not in leads_with_contacts]
        return result[:limit]
    except Exception as e:
        logger.error(f"[B2B] Failed to get leads without contacts: {e}")
        return []


async def _get_leads_ready_for_outreach(limit: int = 50) -> list[tuple[dict, dict, int]]:
    """Get leads ready for outreach (batch query: 3 requests instead of N*2+1).

    Returns list of (lead, contact, step_number).
    """
    if not supabase_client._is_configured():
        return []
    supabase_client._init()

    try:
        client = supabase_client._get_client()

        # Step 1: Get verified contacts (1 request)
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
        if not contacts:
            return []

        # Step 2: Batch-fetch all referenced leads (1 request)
        lead_ids = list({c["lead_id"] for c in contacts if c.get("lead_id")})
        if not lead_ids:
            return []
        ids_str = ",".join(lead_ids)
        resp2 = await client.get(
            f"{supabase_client._BASE_URL}/b2b_leads",
            headers=supabase_client._HEADERS,
            params={"id": f"in.({ids_str})", "limit": str(len(lead_ids))},
        )
        leads_map = {l["id"]: l for l in resp2.json()}

        # Step 3: Batch-fetch all outreach for these contacts (1 request)
        contact_ids = [c["id"] for c in contacts]
        cids_str = ",".join(contact_ids)
        resp3 = await client.get(
            f"{supabase_client._BASE_URL}/b2b_outreach",
            headers=supabase_client._HEADERS,
            params={
                "contact_id": f"in.({cids_str})",
                "order": "sequence_step.desc",
                "limit": "10000",
            },
        )
        outreach_by_contact = {}
        for o in resp3.json():
            cid = o.get("contact_id")
            if cid not in outreach_by_contact:
                outreach_by_contact[cid] = o  # Only keep latest (desc order)

        # Step 4: Assemble results in-memory (0 requests)
        results = []
        seen_leads = set()

        for contact in contacts:
            lead_id = contact.get("lead_id")
            if not lead_id or lead_id in seen_leads:
                continue

            lead = leads_map.get(lead_id)
            if not lead or lead.get("status") in ("won", "lost"):
                continue

            # Determine next step from outreach history
            last_outreach = outreach_by_contact.get(contact["id"])
            if not last_outreach:
                next_step = 1
            else:
                last_step = last_outreach.get("sequence_step", 0)
                if last_step >= 3:
                    continue  # Fully sequenced
                # Check delay (5 days for step 2, 7 for step 3)
                sent_at = last_outreach.get("sent_at", "")
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
