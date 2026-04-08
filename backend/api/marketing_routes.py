"""Marketing Intelligence API — Shopify analytics, SEO, AI citations."""

import logging

from fastapi import APIRouter, Depends, Request, HTTPException

from config import settings

logger = logging.getLogger(__name__)
marketing_router = APIRouter(prefix="/api/marketing", tags=["marketing"])


def _verify_admin(request: Request):
    token = request.cookies.get("nakai_session")
    if token:
        from main import validate_session_token
        if validate_session_token(token):
            return
    pw = (
        request.headers.get("X-Admin-Password")
        or request.query_params.get("pw")
    )
    if pw and pw == settings.admin_password:
        return
    raise HTTPException(status_code=401, detail="Unauthorized")


@marketing_router.get("/shopify-stats")
async def shopify_stats(days: int = 30, _=Depends(_verify_admin)):
    """Get Shopify order analytics summary."""
    from services.shopify_analytics import get_analytics_summary
    return await get_analytics_summary(days)


@marketing_router.get("/products")
async def product_list(_=Depends(_verify_admin)):
    """Get product catalog from Shopify."""
    from services.shopify_client import fetch_products
    products = await fetch_products()
    return {"count": len(products), "products": products}


@marketing_router.get("/collections")
async def collection_list(_=Depends(_verify_admin)):
    """Get collections from Shopify."""
    from services.shopify_client import fetch_collections
    collections = await fetch_collections()
    return {"count": len(collections), "collections": collections}
