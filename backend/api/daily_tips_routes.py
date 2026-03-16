"""Daily AI Tips management API — preview, force-post, history."""

import logging

from fastapi import APIRouter, Header, HTTPException

from config import settings

logger = logging.getLogger(__name__)

tips_router = APIRouter(prefix="/api/tips", tags=["daily-tips"])


@tips_router.get("/today")
async def preview_today():
    """Preview today's AI tips without posting."""
    from services.daily_content import generate_daily_tips
    content = await generate_daily_tips()
    return {"preview": True, "content": content}


@tips_router.post("/force-post")
async def force_post(x_admin_password: str = Header(None)):
    """Force-post today's tips to all platforms (requires admin password)."""
    if x_admin_password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Invalid admin password")

    from services.daily_content import generate_daily_tips
    from services.social_poster import post_all

    content = await generate_daily_tips()
    results = await post_all(content)
    return {"posted": True, "results": results, "content": content}


@tips_router.get("/history")
async def get_history(x_admin_password: str = Header(None), limit: int = 30):
    """Get posting history from Supabase."""
    if x_admin_password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Invalid admin password")

    if not settings.supabase_url or not settings.supabase_service_key:
        return {"history": [], "note": "Supabase not configured"}

    try:
        import httpx
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{settings.supabase_url}/rest/v1/daily_tips_log",
                headers={
                    "apikey": settings.supabase_service_key,
                    "Authorization": f"Bearer {settings.supabase_service_key}",
                },
                params={
                    "select": "*",
                    "order": "posted_at.desc",
                    "limit": str(limit),
                },
            )
            resp.raise_for_status()
            return {"history": resp.json()}
    except Exception as e:
        logger.error(f"[TIPS_HISTORY] Failed: {e}")
        return {"history": [], "error": str(e)}
