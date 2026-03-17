"""Email marketing API endpoints."""

import asyncio
import csv
import io
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Header, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from api.admin_routes import verify_admin
from api.middleware import limiter
from config import settings
from services import supabase_client
from services import resend_client
from services.email_ai import generate_email_design, extract_editable_blocks, apply_editable_text, apply_editable_links, NEWSLETTER_TEMPLATES

logger = logging.getLogger(__name__)

email_router = APIRouter(prefix="/api/email", tags=["Email Marketing"])

BASE_URL = "https://matcha-sensei.onrender.com"


# ── Models ────────────────────────────────────────────────────

class BrandAssetsUpdate(BaseModel):
    logo_url: Optional[str] = None
    colors: Optional[dict] = None
    font_family: Optional[str] = None
    footer_text: Optional[str] = None
    photos: Optional[list] = None


class SubscriberCreate(BaseModel):
    email: str = Field(..., min_length=3, max_length=320)
    name: str = Field(default="", max_length=200)
    tags: list[str] = Field(default_factory=list)
    language: str = Field(default="en", max_length=5)


class SubscriberUpdate(BaseModel):
    name: Optional[str] = None
    tags: Optional[list[str]] = None
    language: Optional[str] = None
    is_active: Optional[bool] = None


class CampaignCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    target_tags: list[str] = Field(default_factory=list)
    target_language: str = Field(default="", max_length=5)
    campaign_photos: list[str] = Field(default_factory=list)


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    html_content: Optional[str] = None
    text_content: Optional[str] = None
    target_tags: Optional[list[str]] = None
    target_language: Optional[str] = None
    edits: Optional[dict[str, str]] = None  # {block_name: new_text}
    link_edits: Optional[dict[str, str]] = None  # {link_name: new_url}


class SendTestRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=320)


# ── Brand Assets ──────────────────────────────────────────────

@email_router.get("/brand-assets")
async def get_brand_assets(_auth: bool = Depends(verify_admin)):
    assets = await supabase_client.get_email_brand_assets()
    if not assets:
        return {
            "logo_url": "",
            "colors": {"primary": "#406546", "secondary": "#F9F0E2", "accent": "#FFFFFF", "text": "#1a1a1a"},
            "font_family": "Work Sans, Helvetica, Arial, sans-serif",
            "footer_text": "NAKAI Matcha | Kagoshima, Japan",
            "photos": [],
        }
    return assets


@email_router.post("/brand-assets")
async def update_brand_assets(body: BrandAssetsUpdate, _auth: bool = Depends(verify_admin)):
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    result = await supabase_client.upsert_email_brand_assets(data)
    if not result:
        raise HTTPException(500, "Failed to save brand assets")
    return result


@email_router.post("/brand-assets/photo")
async def upload_brand_photo(
    file: UploadFile = File(...),
    label: str = Form(default=""),
    _auth: bool = Depends(verify_admin),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "Only image files allowed")
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(400, "File too large (max 5MB)")

    # Upload to Supabase Storage
    import uuid
    ext = file.filename.rsplit(".", 1)[-1] if file.filename and "." in file.filename else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"

    try:
        import httpx
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{settings.supabase_url}/storage/v1/object/email-assets/{filename}",
                headers={
                    "Authorization": f"Bearer {settings.supabase_service_key}",
                    "Content-Type": file.content_type or "image/jpeg",
                },
                content=content,
            )
            resp.raise_for_status()
    except Exception as e:
        logger.error(f"Photo upload failed: {e}")
        raise HTTPException(500, "Failed to upload photo")

    photo_url = f"{settings.supabase_url}/storage/v1/object/public/email-assets/{filename}"

    # Add to brand assets photos array
    assets = await supabase_client.get_email_brand_assets()
    photos = assets.get("photos", []) if assets else []
    photos.append({"url": photo_url, "label": label or file.filename, "uploaded_at": datetime.now(timezone.utc).isoformat()})
    await supabase_client.upsert_email_brand_assets({"photos": photos})

    return {"url": photo_url, "label": label or file.filename}


@email_router.delete("/brand-assets/photo/{idx}")
async def delete_brand_photo(idx: int, _auth: bool = Depends(verify_admin)):
    assets = await supabase_client.get_email_brand_assets()
    if not assets:
        raise HTTPException(404, "No brand assets found")
    photos = assets.get("photos", [])
    if idx < 0 or idx >= len(photos):
        raise HTTPException(404, "Photo index out of range")
    photos.pop(idx)
    await supabase_client.upsert_email_brand_assets({"photos": photos})
    return {"ok": True}


# ── Campaign Photo Upload ─────────────────────────────────────

@email_router.post("/campaign-photo")
async def upload_campaign_photo(
    file: UploadFile = File(...),
    _auth: bool = Depends(verify_admin),
):
    """Upload a photo for use in a campaign email design."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "Only image files allowed")
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(400, "File too large (max 5MB)")

    import uuid
    ext = file.filename.rsplit(".", 1)[-1] if file.filename and "." in file.filename else "jpg"
    filename = f"campaign-{uuid.uuid4().hex}.{ext}"

    try:
        import httpx
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{settings.supabase_url}/storage/v1/object/email-assets/{filename}",
                headers={
                    "Authorization": f"Bearer {settings.supabase_service_key}",
                    "Content-Type": file.content_type or "image/jpeg",
                },
                content=content,
            )
            resp.raise_for_status()
    except Exception as e:
        logger.error(f"Campaign photo upload failed: {e}")
        raise HTTPException(500, "Failed to upload photo")

    photo_url = f"{settings.supabase_url}/storage/v1/object/public/email-assets/{filename}"
    return {"url": photo_url}


# ── Subscribers ───────────────────────────────────────────────

@email_router.get("/subscribers")
async def list_subscribers(
    tag: Optional[str] = None,
    language: Optional[str] = None,
    _auth: bool = Depends(verify_admin),
):
    return await supabase_client.list_email_subscribers(tag=tag, language=language)


@email_router.post("/subscribers")
async def create_subscriber(body: SubscriberCreate, _auth: bool = Depends(verify_admin)):
    result = await supabase_client.create_email_subscriber(
        email=body.email, name=body.name, tags=body.tags, language=body.language,
    )
    if not result:
        raise HTTPException(500, "Failed to create subscriber (may already exist)")
    return result


@email_router.post("/subscribers/import")
async def import_subscribers(
    file: UploadFile = File(...),
    _auth: bool = Depends(verify_admin),
):
    """Import subscribers from CSV (columns: email, name, tags, language)."""
    content = await file.read()
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))

    imported = 0
    errors = []
    for i, row in enumerate(reader):
        email = row.get("email", "").strip()
        if not email or "@" not in email:
            errors.append(f"Row {i+2}: invalid email")
            continue
        name = row.get("name", "").strip()
        tags_str = row.get("tags", "").strip()
        tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []
        language = row.get("language", "en").strip() or "en"

        result = await supabase_client.create_email_subscriber(
            email=email, name=name, tags=tags, language=language,
        )
        if result:
            imported += 1

    return {"imported": imported, "errors": errors}


@email_router.post("/subscribers/sync-shopify")
async def sync_shopify_customers(_auth: bool = Depends(verify_admin)):
    """Sync customers from Shopify Admin API into email subscribers."""
    from services import shopify_client

    try:
        customers = await shopify_client.fetch_customers()
    except Exception as e:
        raise HTTPException(500, f"Shopify API error: {e}") from e

    if not customers:
        return {"synced": 0, "skipped": 0, "total_shopify": 0}

    synced = 0
    skipped = 0

    for c in customers:
        email = (c.get("email") or "").strip().lower()
        if not email or "@" not in email:
            continue

        name = f"{c.get('first_name', '')} {c.get('last_name', '')}".strip()
        shopify_tags = [t.strip().lower() for t in (c.get("tags") or "").split(",") if t.strip()]

        segment = "wholesale" if "wholesale" in shopify_tags else "retail"
        tags = [segment, "shopify"]

        result = await supabase_client.create_email_subscriber(
            email=email, name=name, tags=tags, language="en",
        )
        if result:
            synced += 1
        else:
            skipped += 1

    return {"synced": synced, "skipped": skipped, "total_shopify": len(customers)}


@email_router.patch("/subscribers/{sub_id}")
async def update_subscriber(sub_id: str, body: SubscriberUpdate, _auth: bool = Depends(verify_admin)):
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    result = await supabase_client.update_email_subscriber(sub_id, data)
    if not result:
        raise HTTPException(404, "Subscriber not found")
    return result


@email_router.delete("/subscribers/{sub_id}")
async def delete_subscriber(sub_id: str, _auth: bool = Depends(verify_admin)):
    ok = await supabase_client.delete_email_subscriber(sub_id)
    if not ok:
        raise HTTPException(404, "Subscriber not found")
    return {"ok": True}


# ── Campaigns ─────────────────────────────────────────────────

@email_router.get("/campaigns")
async def list_campaigns(_auth: bool = Depends(verify_admin)):
    return await supabase_client.list_email_campaigns()


@email_router.post("/campaigns")
async def create_campaign(body: CampaignCreate, _auth: bool = Depends(verify_admin)):
    """Create campaign and generate AI email design."""
    # Save draft
    campaign = await supabase_client.create_email_campaign({
        "name": body.name,
        "description": body.description,
        "status": "generating",
        "target_tags": body.target_tags,
        "target_language": body.target_language,
    })
    if not campaign:
        raise HTTPException(500, "Failed to create campaign")

    # Generate design with AI
    brand_assets = await supabase_client.get_email_brand_assets()
    if not brand_assets:
        brand_assets = {
            "logo_url": "",
            "colors": {"primary": "#406546", "secondary": "#F9F0E2", "accent": "#FFFFFF", "text": "#1a1a1a"},
            "font_family": "Work Sans, Helvetica, Arial, sans-serif",
            "photos": [],
        }

    html = await generate_email_design(
        description=body.description,
        brand_assets=brand_assets,
        language=body.target_language or "en",
        campaign_photos=body.campaign_photos or None,
    )

    blocks = extract_editable_blocks(html)

    update_data = {"html_content": html, "status": "ready"}
    if body.campaign_photos:
        update_data["campaign_photos"] = body.campaign_photos
    await supabase_client.update_email_campaign(campaign["id"], update_data)

    campaign["html_content"] = html
    campaign["status"] = "ready"
    campaign["editable_blocks"] = blocks
    return campaign


@email_router.get("/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str, _auth: bool = Depends(verify_admin)):
    campaign = await supabase_client.get_email_campaign(campaign_id)
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    campaign["editable_blocks"] = extract_editable_blocks(campaign.get("html_content", ""))
    return campaign


@email_router.patch("/campaigns/{campaign_id}")
async def update_campaign(campaign_id: str, body: CampaignUpdate, _auth: bool = Depends(verify_admin)):
    campaign = await supabase_client.get_email_campaign(campaign_id)
    if not campaign:
        raise HTTPException(404, "Campaign not found")

    data = {k: v for k, v in body.model_dump().items() if v is not None and k not in ("edits", "link_edits")}
    data["updated_at"] = datetime.now(timezone.utc).isoformat()

    # Apply text edits to HTML
    html = campaign.get("html_content", "")
    if body.edits and html:
        html = apply_editable_text(html, body.edits)
    if body.link_edits and html:
        html = apply_editable_links(html, body.link_edits)
    if body.edits or body.link_edits:
        data["html_content"] = html

    result = await supabase_client.update_email_campaign(campaign_id, data)
    if not result:
        raise HTTPException(500, "Failed to update campaign")
    result["editable_blocks"] = extract_editable_blocks(result.get("html_content", ""))
    return result


@email_router.delete("/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: str, _auth: bool = Depends(verify_admin)):
    ok = await supabase_client.delete_email_campaign(campaign_id)
    if not ok:
        raise HTTPException(404, "Campaign not found")
    return {"ok": True}


@email_router.post("/campaigns/{campaign_id}/regenerate")
async def regenerate_campaign(campaign_id: str, _auth: bool = Depends(verify_admin)):
    """Re-generate email design with AI."""
    campaign = await supabase_client.get_email_campaign(campaign_id)
    if not campaign:
        raise HTTPException(404, "Campaign not found")

    await supabase_client.update_email_campaign(campaign_id, {"status": "generating"})

    brand_assets = await supabase_client.get_email_brand_assets() or {
        "logo_url": "",
        "colors": {"primary": "#406546", "secondary": "#F9F0E2", "accent": "#FFFFFF", "text": "#1a1a1a"},
        "font_family": "Work Sans, Helvetica, Arial, sans-serif",
        "photos": [],
    }

    html = await generate_email_design(
        description=campaign["description"],
        brand_assets=brand_assets,
        language=campaign.get("target_language") or "en",
        campaign_photos=campaign.get("campaign_photos") or None,
    )

    result = await supabase_client.update_email_campaign(campaign_id, {
        "html_content": html,
        "status": "ready",
    })
    if result:
        result["editable_blocks"] = extract_editable_blocks(html)
    return result


@email_router.post("/campaigns/{campaign_id}/send-test")
async def send_test_email(
    campaign_id: str,
    body: SendTestRequest,
    _auth: bool = Depends(verify_admin),
):
    campaign = await supabase_client.get_email_campaign(campaign_id)
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    if not campaign.get("html_content"):
        raise HTTPException(400, "Campaign has no email content")

    subject = campaign.get("subject") or f"[TEST] {campaign['name']}"
    html = campaign["html_content"].replace(
        "{{unsubscribe_url}}", f"{BASE_URL}/api/email/unsubscribe?token=test"
    )

    result = await resend_client.send_email(
        to=body.email,
        subject=f"[TEST] {subject}",
        html=html,
    )
    if not result:
        raise HTTPException(500, "Failed to send test email")
    return {"ok": True, "resend_id": result.get("id")}


@email_router.post("/campaigns/{campaign_id}/send")
@limiter.limit("5/minute")
async def send_campaign(
    request: Request,
    campaign_id: str,
    _auth: bool = Depends(verify_admin),
):
    """Execute bulk send to all matching subscribers."""
    campaign = await supabase_client.get_email_campaign(campaign_id)
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    if not campaign.get("html_content") or not campaign.get("subject"):
        raise HTTPException(400, "Campaign needs content and subject before sending")
    if campaign.get("status") in ("sending", "sent"):
        raise HTTPException(400, f"Campaign already {campaign['status']}")

    # Start background send
    asyncio.create_task(_execute_bulk_send(campaign_id))
    return {"ok": True, "status": "sending"}


async def _execute_bulk_send(campaign_id: str):
    """Background task: send campaign to matching subscribers."""
    try:
        campaign = await supabase_client.get_email_campaign(campaign_id)
        if not campaign:
            return

        subscribers = await supabase_client.list_email_subscribers(
            tag=campaign["target_tags"][0] if campaign.get("target_tags") else None,
            language=campaign.get("target_language") or None,
        )

        if not subscribers:
            await supabase_client.update_email_campaign(campaign_id, {
                "status": "sent",
                "sent_at": datetime.now(timezone.utc).isoformat(),
                "stats": {"total": 0, "sent": 0, "failed": 0},
            })
            return

        await supabase_client.update_email_campaign(campaign_id, {"status": "sending"})

        sent = 0
        failed = 0
        batch = []

        for sub in subscribers:
            html = campaign["html_content"].replace(
                "{{unsubscribe_url}}",
                f"{BASE_URL}/api/email/unsubscribe?token={sub.get('unsubscribe_token', '')}"
            )

            batch.append({
                "from": "NAKAI Matcha <hello@nakaimatcha.com>",
                "to": [sub["email"]],
                "subject": campaign["subject"],
                "html": html,
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

        await supabase_client.update_email_campaign(campaign_id, {
            "status": "sent",
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "stats": {"total": len(subscribers), "sent": sent, "failed": failed},
        })

    except Exception as e:
        logger.error(f"Bulk send failed for campaign {campaign_id}: {e}")
        await supabase_client.update_email_campaign(campaign_id, {"status": "failed"})


# ── Unsubscribe (Public) ─────────────────────────────────────

@email_router.get("/unsubscribe", response_class=HTMLResponse)
async def unsubscribe_page(token: str = ""):
    if not token:
        return HTMLResponse("<h1>Invalid unsubscribe link</h1>", status_code=400)
    return HTMLResponse(f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Unsubscribe - NAKAI Matcha</title>
<style>
body{{font-family:Work Sans,Helvetica,sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0;background:#F9F0E2;color:#1a1a1a}}
.card{{background:#fff;padding:48px;border-radius:16px;text-align:center;max-width:400px;box-shadow:0 4px 24px rgba(0,0,0,.06)}}
h1{{color:#406546;font-size:24px;margin:0 0 16px}}
p{{font-size:16px;line-height:1.5;margin:0 0 24px;color:#666}}
button{{background:#406546;color:#fff;border:none;padding:14px 32px;border-radius:8px;font-size:16px;cursor:pointer;font-family:inherit}}
button:hover{{background:#345538}}
.done{{color:#406546}}
</style></head>
<body><div class="card" id="card">
<h1>Unsubscribe</h1>
<p>Are you sure you want to unsubscribe from NAKAI Matcha emails?</p>
<button onclick="doUnsub()">Unsubscribe</button>
</div>
<script>
async function doUnsub(){{
  try{{
    const r=await fetch('/api/email/unsubscribe',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{token:'{token}'}})}});
    const d=await r.json();
    document.getElementById('card').innerHTML=d.ok
      ?'<h1 class="done">Unsubscribed</h1><p>You have been successfully unsubscribed.</p>'
      :'<h1>Error</h1><p>Could not process your request. The link may have expired.</p>';
  }}catch(e){{document.getElementById('card').innerHTML='<h1>Error</h1><p>Something went wrong.</p>';}}
}}
</script></body></html>""")


@email_router.post("/unsubscribe")
async def process_unsubscribe(request: Request):
    body = await request.json()
    token = body.get("token", "")
    if not token:
        raise HTTPException(400, "Missing token")
    ok = await supabase_client.unsubscribe_by_token(token)
    return {"ok": ok}


# ── Newsletter Templates ─────────────────────────────────────

@email_router.get("/newsletter-templates")
async def list_newsletter_templates(_auth: bool = Depends(verify_admin)):
    """Return available newsletter content templates."""
    return {k: {"name_ja": v["name_ja"], "name_en": v["name_en"], "subject_prefix": v["subject_prefix"]} for k, v in NEWSLETTER_TEMPLATES.items()}


# ── Newsletter Schedules ─────────────────────────────────────

class ScheduleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    template_key: str = Field(default="", max_length=50)
    custom_prompt: str = Field(default="", max_length=2000)
    target_tags: list[str] = Field(default_factory=list)
    target_language: str = Field(default="en", max_length=5)
    days_of_week: list[int] = Field(default=[1, 4])  # Mon=1, Thu=4 (JS convention)
    send_time_utc: str = Field(default="14:00", max_length=5)
    is_active: bool = Field(default=False)


class ScheduleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    template_key: Optional[str] = None
    custom_prompt: Optional[str] = None
    target_tags: Optional[list[str]] = None
    target_language: Optional[str] = None
    days_of_week: Optional[list[int]] = None
    send_time_utc: Optional[str] = None
    is_active: Optional[bool] = None


@email_router.get("/schedules")
async def list_schedules(_auth: bool = Depends(verify_admin)):
    return await supabase_client.list_newsletter_schedules()


@email_router.post("/schedules")
async def create_schedule(body: ScheduleCreate, _auth: bool = Depends(verify_admin)):
    data = body.model_dump()
    result = await supabase_client.create_newsletter_schedule(data)
    if not result:
        raise HTTPException(500, "Failed to create schedule")
    return result


@email_router.patch("/schedules/{schedule_id}")
async def update_schedule(schedule_id: str, body: ScheduleUpdate, _auth: bool = Depends(verify_admin)):
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    result = await supabase_client.update_newsletter_schedule(schedule_id, data)
    if not result:
        raise HTTPException(404, "Schedule not found")
    return result


@email_router.delete("/schedules/{schedule_id}")
async def delete_schedule(schedule_id: str, _auth: bool = Depends(verify_admin)):
    ok = await supabase_client.delete_newsletter_schedule(schedule_id)
    if not ok:
        raise HTTPException(404, "Schedule not found")
    return {"ok": True}


@email_router.get("/newsletter/reload-schema")
@email_router.post("/newsletter/reload-schema")
async def reload_postgrest_schema(_auth: bool = Depends(verify_admin)):
    """Reload PostgREST schema cache via direct PostgreSQL NOTIFY. v3

    Auto-derives connection from SUPABASE_URL + SUPABASE_SERVICE_KEY if
    DATABASE_URL is not set. Tries direct DB and multiple pooler regions.
    """
    import asyncpg
    import re

    async def _try_connect(dsn: str, label: str) -> dict:
        """Attempt connection and NOTIFY."""
        try:
            conn = await asyncpg.connect(dsn, timeout=10, ssl="require")
            try:
                await conn.execute("NOTIFY pgrst, 'reload schema'")
                await conn.execute("""
                    CREATE OR REPLACE FUNCTION public.reload_schema_cache()
                    RETURNS void LANGUAGE plpgsql SECURITY DEFINER AS $$
                    BEGIN
                        NOTIFY pgrst, 'reload schema';
                    END;
                    $$;
                """)
                table_exists = await conn.fetchval(
                    "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
                    "WHERE table_schema='public' AND table_name='newsletter_schedules')"
                )
                return {"ok": True, "method": label, "table_exists": table_exists, "rpc_created": True}
            finally:
                await conn.close()
        except Exception as e:
            return {"ok": False, "method": label, "error": str(e)[:200]}

    # 1) If DATABASE_URL is set, use it directly
    if settings.database_url:
        return await _try_connect(settings.database_url, "database_url")

    # 2) Auto-derive from SUPABASE_URL + SUPABASE_SERVICE_KEY
    if not settings.supabase_url or not settings.supabase_service_key:
        return {"ok": False, "error": "Need DATABASE_URL or SUPABASE_URL+SUPABASE_SERVICE_KEY"}

    m = re.match(r"https://([^.]+)\.supabase\.co", settings.supabase_url)
    if not m:
        return {"ok": False, "error": f"Cannot parse project ref from: {settings.supabase_url}"}
    ref = m.group(1)
    key = settings.supabase_service_key

    # Method A: Try Supabase Management API (execute SQL directly)
    import httpx
    mgmt_headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    mgmt_results = {}
    async with httpx.AsyncClient(timeout=15) as client:
        # Try Management API SQL execution
        try:
            r = await client.post(
                f"https://api.supabase.com/v1/projects/{ref}/database/query",
                headers=mgmt_headers,
                json={"query": "NOTIFY pgrst, 'reload schema'"},
            )
            mgmt_results["mgmt_query"] = {"status": r.status_code, "body": r.text[:300]}
            if r.status_code < 400:
                return {"ok": True, "method": "management_api", "ref": ref}
        except Exception as e:
            mgmt_results["mgmt_query"] = {"error": str(e)[:200]}

        # Try Management API PostgREST restart
        try:
            r2 = await client.patch(
                f"https://api.supabase.com/v1/projects/{ref}/postgrest",
                headers=mgmt_headers,
                json={"db_schema": "public,extensions"},
            )
            mgmt_results["mgmt_postgrest"] = {"status": r2.status_code, "body": r2.text[:300]}
        except Exception as e:
            mgmt_results["mgmt_postgrest"] = {"error": str(e)[:200]}

    # Method B: Try direct PostgreSQL connections
    attempts = [
        (f"postgresql://postgres.{ref}:{key}@db.{ref}.supabase.co:5432/postgres", "direct_jwt"),
    ]
    for region in ["us-east-1", "us-west-1", "ap-northeast-1", "eu-west-1"]:
        attempts.append((
            f"postgresql://postgres.{ref}:{key}@aws-0-{region}.pooler.supabase.com:6543/postgres",
            f"pooler_{region}",
        ))

    errors = []
    for dsn, label in attempts:
        result = await _try_connect(dsn, label)
        if result.get("ok"):
            return result
        errors.append({"method": label, "error": result.get("error", "")[:100]})

    return {
        "ok": False,
        "ref": ref,
        "mgmt_api": mgmt_results,
        "db_errors": errors,
        "hint": "Set DATABASE_URL in Render. Get it from Supabase Dashboard > Settings > Database > Connection string (URI)",
    }


@email_router.post("/newsletter/init-table")
async def init_newsletter_table(_auth: bool = Depends(verify_admin)):
    """Create newsletter_schedules table if it doesn't exist."""
    import httpx
    sql = """
    CREATE TABLE IF NOT EXISTS newsletter_schedules (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT DEFAULT '',
        template_key TEXT DEFAULT '',
        custom_prompt TEXT DEFAULT '',
        target_tags TEXT[] DEFAULT '{}',
        target_language TEXT DEFAULT 'en',
        is_active BOOLEAN DEFAULT FALSE,
        days_of_week INT[] DEFAULT '{1,4}',
        send_time_utc TEXT DEFAULT '14:00',
        last_sent_at TIMESTAMPTZ,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );
    """
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{settings.supabase_url}/rest/v1/rpc/exec_sql",
                headers={
                    "apikey": settings.supabase_service_key,
                    "Authorization": f"Bearer {settings.supabase_service_key}",
                    "Content-Type": "application/json",
                },
                json={"query": sql},
            )
            if resp.status_code >= 400:
                # Try raw SQL via pg endpoint
                resp2 = await client.post(
                    f"{settings.supabase_url}/pg",
                    headers={
                        "apikey": settings.supabase_service_key,
                        "Authorization": f"Bearer {settings.supabase_service_key}",
                        "Content-Type": "application/json",
                    },
                    json={"query": sql},
                )
                return {"ok": True, "method": "pg", "note": "Table creation attempted. If this fails, run SQL manually in Supabase dashboard.", "sql": sql.strip()}
            return {"ok": True, "method": "rpc"}
    except Exception as e:
        return {"ok": False, "error": str(e), "sql": sql.strip()}


@email_router.post("/schedules/{schedule_id}/trigger")
async def trigger_schedule(schedule_id: str, _auth: bool = Depends(verify_admin)):
    """Manually trigger a newsletter send right now."""
    schedule = await supabase_client.get_newsletter_schedule(schedule_id)
    if not schedule:
        raise HTTPException(404, "Schedule not found")

    from services.newsletter_sender import _generate_and_send
    asyncio.create_task(_generate_and_send(schedule))
    return {"ok": True, "status": "sending"}
