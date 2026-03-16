"""B2B Sales Automation API endpoints."""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File
from pydantic import BaseModel, Field

from api.admin_routes import verify_admin
from config import settings
from services import supabase_client

logger = logging.getLogger(__name__)

b2b_router = APIRouter(prefix="/api/b2b", tags=["B2B Sales"])


# ── Models ────────────────────────────────────────────────────

class LeadUpdate(BaseModel):
    status: str | None = None
    lead_score: int | None = None
    notes: str | None = None
    cafe_type: str | None = None


# ── Stats ─────────────────────────────────────────────────────

@b2b_router.get("/stats")
async def get_stats(_auth: bool = Depends(verify_admin)):
    from services.b2b.analytics import get_dashboard_stats
    return await get_dashboard_stats()


# ── Leads CRUD ────────────────────────────────────────────────

@b2b_router.get("/leads")
async def list_leads(
    region: str = "",
    status: str = "",
    search: str = "",
    limit: int = 100,
    offset: int = 0,
    _auth: bool = Depends(verify_admin),
):
    if not supabase_client._is_configured():
        raise HTTPException(503, "Supabase not configured")
    supabase_client._init()

    params: dict = {
        "order": "created_at.desc",
        "limit": str(min(limit, 500)),
        "offset": str(offset),
    }
    if region:
        params["region"] = f"eq.{region}"
    if status:
        params["status"] = f"eq.{status}"
    if search:
        params["or"] = f"(name.ilike.%{search}%,city.ilike.%{search}%)"

    try:
        client = supabase_client._get_client()
        resp = await client.get(
            f"{supabase_client._BASE_URL}/b2b_leads",
            headers={**supabase_client._HEADERS, "Prefer": "count=exact"},
            params=params,
        )
        resp.raise_for_status()
        total = int(resp.headers.get("content-range", "0/0").split("/")[-1])
        return {"leads": resp.json(), "total": total}
    except Exception as e:
        raise HTTPException(500, str(e))


@b2b_router.patch("/leads/{lead_id}")
async def update_lead(
    lead_id: str,
    body: LeadUpdate,
    _auth: bool = Depends(verify_admin),
):
    if not supabase_client._is_configured():
        raise HTTPException(503, "Supabase not configured")
    supabase_client._init()

    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()

    try:
        client = supabase_client._get_client()
        resp = await client.patch(
            f"{supabase_client._BASE_URL}/b2b_leads",
            headers={**supabase_client._HEADERS, "Prefer": "return=representation"},
            params={"id": f"eq.{lead_id}"},
            json=updates,
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else {}
    except Exception as e:
        raise HTTPException(500, str(e))


@b2b_router.delete("/leads/{lead_id}")
async def delete_lead(lead_id: str, _auth: bool = Depends(verify_admin)):
    if not supabase_client._is_configured():
        raise HTTPException(503, "Supabase not configured")
    supabase_client._init()
    try:
        client = supabase_client._get_client()
        await client.delete(
            f"{supabase_client._BASE_URL}/b2b_leads",
            headers=supabase_client._HEADERS,
            params={"id": f"eq.{lead_id}"},
        )
        return {"ok": True}
    except Exception as e:
        raise HTTPException(500, str(e))


# ── Contacts ──────────────────────────────────────────────────

@b2b_router.get("/leads/{lead_id}/contacts")
async def get_contacts(lead_id: str, _auth: bool = Depends(verify_admin)):
    if not supabase_client._is_configured():
        raise HTTPException(503, "Supabase not configured")
    supabase_client._init()
    try:
        client = supabase_client._get_client()
        resp = await client.get(
            f"{supabase_client._BASE_URL}/b2b_contacts",
            headers=supabase_client._HEADERS,
            params={"lead_id": f"eq.{lead_id}", "order": "created_at.desc"},
        )
        return resp.json()
    except Exception as e:
        raise HTTPException(500, str(e))


# ── Outreach ──────────────────────────────────────────────────

@b2b_router.get("/outreach")
async def list_outreach(
    status: str = "",
    limit: int = 100,
    _auth: bool = Depends(verify_admin),
):
    if not supabase_client._is_configured():
        raise HTTPException(503, "Supabase not configured")
    supabase_client._init()

    params: dict = {"order": "created_at.desc", "limit": str(min(limit, 500))}
    if status:
        params["status"] = f"eq.{status}"

    try:
        client = supabase_client._get_client()
        resp = await client.get(
            f"{supabase_client._BASE_URL}/b2b_outreach",
            headers=supabase_client._HEADERS,
            params=params,
        )
        return resp.json()
    except Exception as e:
        raise HTTPException(500, str(e))


# ── Import ────────────────────────────────────────────────────

@b2b_router.post("/import")
async def import_file(
    file: UploadFile = File(...),
    _auth: bool = Depends(verify_admin),
):
    content = await file.read()
    filename = file.filename or ""

    if filename.endswith(".xlsx"):
        from services.b2b.lead_importer import import_excel
        result = await import_excel(content, filename)
    elif filename.endswith(".csv"):
        from services.b2b.lead_importer import import_csv
        result = await import_csv(content)
    else:
        raise HTTPException(400, "Unsupported file type. Use .xlsx or .csv")

    return result


# ── Pipeline ──────────────────────────────────────────────────

@b2b_router.post("/pipeline/test")
async def test_pipeline(
    lead_id: str = "",
    _auth: bool = Depends(verify_admin),
):
    """Run test pipeline for a single lead (doesn't send email)."""
    from services.b2b.pipeline import run_test_pipeline
    return await run_test_pipeline(lead_id or None)


@b2b_router.post("/pipeline/run")
async def run_pipeline(_auth: bool = Depends(verify_admin)):
    """Manually trigger the full daily pipeline."""
    import asyncio
    from services.b2b.pipeline import run_daily_pipeline
    asyncio.create_task(run_daily_pipeline())
    return {"status": "started"}


# ── Discovery ─────────────────────────────────────────────────

@b2b_router.post("/discover")
async def discover_cafes(
    region: str = "",
    city: str = "",
    _auth: bool = Depends(verify_admin),
):
    """Manually trigger café discovery for a region or city."""
    from services.b2b.lead_researcher import search_region, search_cafes_in_city, SEARCH_KEYWORDS
    import asyncio

    if city:
        results = await search_cafes_in_city(city, SEARCH_KEYWORDS[0], region or "us_west")
        return {"found": len(results)}

    if region:
        results = await search_region(region, max_cities=3)
        return {"found": len(results)}

    return {"error": "Provide region or city parameter"}


# ── Webhook (Resend) ──────────────────────────────────────────

@b2b_router.post("/webhook/resend")
async def resend_webhook(request: Request):
    """Handle Resend webhook events for email tracking."""
    try:
        body = await request.json()
        event_type = body.get("type", "")
        data = body.get("data", {})

        from services.b2b.outreach_executor import handle_webhook_event
        await handle_webhook_event(event_type, data)

        return {"ok": True}
    except Exception as e:
        logger.error(f"[B2B] Webhook error: {e}")
        return {"ok": False}


# ── Unsubscribe (public) ─────────────────────────────────────

@b2b_router.get("/unsubscribe")
async def unsubscribe(email: str = ""):
    """CAN-SPAM unsubscribe endpoint."""
    if not email or "@" not in email:
        raise HTTPException(400, "Invalid email")

    if not supabase_client._is_configured():
        raise HTTPException(503)
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

    return HTMLResponse("""<!DOCTYPE html>
<html><head><title>Unsubscribed</title>
<style>body{font-family:Work Sans,system-ui,sans-serif;display:flex;align-items:center;
justify-content:center;min-height:100vh;background:#F9F0E2;color:#333;}
.box{text-align:center;padding:48px;background:#fff;border-radius:16px;
box-shadow:0 4px 24px rgba(0,0,0,.08);max-width:400px;}
h2{color:#406546;font-weight:500;margin-bottom:12px;}
p{color:#666;font-size:.9rem;}</style></head>
<body><div class="box"><h2>Unsubscribed</h2>
<p>You've been removed from our mailing list. We're sorry to see you go.</p>
</div></body></html>""")
