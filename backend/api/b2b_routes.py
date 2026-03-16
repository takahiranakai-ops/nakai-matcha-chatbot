"""B2B Sales Automation API endpoints."""

import base64
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


class SequenceUpdate(BaseModel):
    subject_template: str = ""
    body_template: str = ""


class TestSendRequest(BaseModel):
    to_email: str
    step: int = 1
    cafe_name: str = "Sample Cafe"
    city: str = "Portland"
    cafe_type: str = "specialty"


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


# ── Sequences (Template CRUD) ────────────────────────────────

@b2b_router.get("/sequences")
async def list_sequences(_auth: bool = Depends(verify_admin)):
    """Get all email sequence templates."""
    if not supabase_client._is_configured():
        raise HTTPException(503, "Supabase not configured")
    supabase_client._init()
    try:
        client = supabase_client._get_client()
        resp = await client.get(
            f"{supabase_client._BASE_URL}/b2b_sequences",
            headers=supabase_client._HEADERS,
            params={"order": "step_number.asc"},
        )
        return resp.json()
    except Exception as e:
        raise HTTPException(500, str(e))


@b2b_router.put("/sequences/{step_number}")
async def update_sequence(
    step_number: int,
    body: SequenceUpdate,
    _auth: bool = Depends(verify_admin),
):
    """Update email template for a specific step."""
    if not supabase_client._is_configured():
        raise HTTPException(503, "Supabase not configured")
    supabase_client._init()
    try:
        client = supabase_client._get_client()
        resp = await client.patch(
            f"{supabase_client._BASE_URL}/b2b_sequences",
            headers={**supabase_client._HEADERS, "Prefer": "return=representation"},
            params={"step_number": f"eq.{step_number}", "name": "eq.Default"},
            json={
                "subject_template": body.subject_template,
                "body_template": body.body_template,
            },
        )
        resp.raise_for_status()
        rows = resp.json()
        return rows[0] if rows else {}
    except Exception as e:
        raise HTTPException(500, str(e))


# ── Test Send ─────────────────────────────────────────────────

@b2b_router.post("/test-send")
async def test_send(
    body: TestSendRequest,
    _auth: bool = Depends(verify_admin),
):
    """Send a test email to a specified address."""
    import httpx

    try:
        from services.b2b.outreach_writer import generate_outreach_email

        lead = {
            "name": body.cafe_name,
            "city": body.city,
            "cafe_type": body.cafe_type,
        }
        email = await generate_outreach_email(lead, step=body.step)

        if not settings.resend_api_key:
            return {"ok": False, "error": "RESEND_API_KEY が未設定です"}

        # Get PDF attachment if exists
        attachments = await _get_active_attachment()

        from_email = f"Takahiro from NAKAI <{settings.b2b_from_email}>"
        payload = {
            "from": from_email,
            "to": [body.to_email],
            "subject": f"[TEST] {email['subject']}",
            "html": email["html"],
            "reply_to": settings.b2b_reply_to,
        }
        if attachments:
            payload["attachments"] = attachments

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {settings.resend_api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

        if resp.status_code >= 400:
            return {"ok": False, "error": f"Resend API {resp.status_code}: {resp.text}"}

        data = resp.json()
        return {"ok": True, "subject": email["subject"], "resend_id": data.get("id")}
    except Exception as e:
        logger.error(f"[B2B] Test send failed: {e}")
        return {"ok": False, "error": str(e)}


# ── PDF Attachment ────────────────────────────────────────────

@b2b_router.post("/attachment/upload")
async def upload_attachment(
    file: UploadFile = File(...),
    _auth: bool = Depends(verify_admin),
):
    """Upload a PDF to attach to outreach emails."""
    filename = file.filename or "attachment.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(400, "PDF files only")

    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(400, "File too large (max 5MB)")

    content_b64 = base64.b64encode(content).decode("utf-8")

    if not supabase_client._is_configured():
        raise HTTPException(503, "Supabase not configured")
    supabase_client._init()

    try:
        client = supabase_client._get_client()
        # Deactivate existing attachments
        await client.patch(
            f"{supabase_client._BASE_URL}/b2b_attachments",
            headers={**supabase_client._HEADERS, "Prefer": "return=minimal"},
            params={"is_active": "eq.true"},
            json={"is_active": False},
        )
        # Insert new
        resp = await client.post(
            f"{supabase_client._BASE_URL}/b2b_attachments",
            headers={**supabase_client._HEADERS, "Prefer": "return=minimal"},
            json={
                "filename": filename,
                "content_base64": content_b64,
                "content_type": "application/pdf",
                "is_active": True,
            },
        )
        resp.raise_for_status()
        return {"ok": True, "filename": filename, "size_kb": len(content) // 1024}
    except Exception as e:
        raise HTTPException(500, str(e))


@b2b_router.get("/attachment")
async def get_attachment(_auth: bool = Depends(verify_admin)):
    """Get current active attachment info."""
    if not supabase_client._is_configured():
        return {"filename": None}
    supabase_client._init()
    try:
        client = supabase_client._get_client()
        resp = await client.get(
            f"{supabase_client._BASE_URL}/b2b_attachments",
            headers=supabase_client._HEADERS,
            params={"is_active": "eq.true", "select": "filename,created_at", "limit": "1"},
        )
        rows = resp.json()
        if rows:
            return {"filename": rows[0]["filename"], "uploaded_at": rows[0]["created_at"]}
        return {"filename": None}
    except Exception:
        return {"filename": None}


@b2b_router.delete("/attachment")
async def delete_attachment(_auth: bool = Depends(verify_admin)):
    """Remove the active PDF attachment."""
    if not supabase_client._is_configured():
        raise HTTPException(503)
    supabase_client._init()
    try:
        client = supabase_client._get_client()
        await client.patch(
            f"{supabase_client._BASE_URL}/b2b_attachments",
            headers={**supabase_client._HEADERS, "Prefer": "return=minimal"},
            params={"is_active": "eq.true"},
            json={"is_active": False},
        )
        return {"ok": True}
    except Exception as e:
        raise HTTPException(500, str(e))


async def _get_active_attachment() -> list[dict] | None:
    """Get active PDF attachment for email sending."""
    if not supabase_client._is_configured():
        return None
    supabase_client._init()
    try:
        client = supabase_client._get_client()
        resp = await client.get(
            f"{supabase_client._BASE_URL}/b2b_attachments",
            headers=supabase_client._HEADERS,
            params={"is_active": "eq.true", "limit": "1"},
        )
        rows = resp.json()
        if rows:
            return [{
                "filename": rows[0]["filename"],
                "content": rows[0]["content_base64"],
            }]
    except Exception:
        pass
    return None


# ── Export ────────────────────────────────────────────────────

@b2b_router.get("/export")
async def export_leads(
    region: str = "",
    status: str = "",
    _auth: bool = Depends(verify_admin),
):
    """Export all leads (with contacts) as Excel file."""
    from fastapi.responses import Response
    import io
    from openpyxl import Workbook

    if not supabase_client._is_configured():
        raise HTTPException(503, "Supabase not configured")
    supabase_client._init()

    try:
        client = supabase_client._get_client()
        params: dict = {"order": "created_at.desc", "limit": "10000"}
        if region:
            params["region"] = f"eq.{region}"
        if status:
            params["status"] = f"eq.{status}"

        resp = await client.get(
            f"{supabase_client._BASE_URL}/b2b_leads",
            headers=supabase_client._HEADERS,
            params=params,
        )
        leads = resp.json()

        # Get all contacts
        contact_resp = await client.get(
            f"{supabase_client._BASE_URL}/b2b_contacts",
            headers=supabase_client._HEADERS,
            params={"order": "created_at.desc", "limit": "50000"},
        )
        contacts = contact_resp.json()
        contacts_by_lead = {}
        for c in contacts:
            lid = c.get("lead_id", "")
            if lid not in contacts_by_lead:
                contacts_by_lead[lid] = []
            contacts_by_lead[lid].append(c)

        wb = Workbook()
        ws = wb.active
        ws.title = "Leads"
        ws.append([
            "Name", "City", "State", "Country", "Region",
            "Type", "Status", "Score", "Website", "Phone",
            "Email 1", "Email 2", "Source", "Created",
        ])

        for lead in leads:
            lid = lead.get("id", "")
            lead_contacts = contacts_by_lead.get(lid, [])
            email1 = lead_contacts[0]["email"] if len(lead_contacts) > 0 else ""
            email2 = lead_contacts[1]["email"] if len(lead_contacts) > 1 else ""
            ws.append([
                lead.get("name", ""),
                lead.get("city", ""),
                lead.get("state", ""),
                lead.get("country", ""),
                lead.get("region", ""),
                lead.get("cafe_type", ""),
                lead.get("status", ""),
                lead.get("lead_score", 0),
                lead.get("website", ""),
                lead.get("phone", ""),
                email1,
                email2,
                lead.get("source", ""),
                lead.get("created_at", "")[:10] if lead.get("created_at") else "",
            ])

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return Response(
            content=buf.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="NAKAI_B2B_Leads_{today}.xlsx"'},
        )

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
    """Manually trigger cafe discovery for a region or city."""
    from services.b2b.lead_researcher import search_region, search_cafes_in_city, SEARCH_KEYWORDS

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
    from fastapi.responses import HTMLResponse

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
