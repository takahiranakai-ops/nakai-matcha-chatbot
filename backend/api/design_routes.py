"""Design Management API — Brand guidelines, content validation, templates."""

import logging

from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel

from config import settings

logger = logging.getLogger(__name__)
design_router = APIRouter(prefix="/api/design", tags=["design"])


def _verify_admin(request: Request):
    pw = (
        request.headers.get("X-Admin-Password")
        or request.query_params.get("pw")
        or request.cookies.get("nakai_admin")
    )
    if pw != settings.admin_password:
        raise HTTPException(status_code=401, detail="Unauthorized")


@design_router.get("/guidelines")
async def brand_guidelines(_=Depends(_verify_admin)):
    """Get full NAKAI brand guidelines."""
    from services.design_manager import get_brand_guidelines
    return get_brand_guidelines()


@design_router.get("/templates")
async def content_templates(_=Depends(_verify_admin)):
    """Get all approved content templates."""
    from services.design_manager import get_content_templates
    return get_content_templates()


@design_router.get("/templates/{content_type}")
async def content_template(content_type: str, _=Depends(_verify_admin)):
    """Get template for a specific content type."""
    from services.design_manager import get_template
    result = get_template(content_type)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


class ReviewRequest(BaseModel):
    content_type: str
    text: str = ""
    colors: list[str] = []


@design_router.post("/review")
async def review_content(req: ReviewRequest, _=Depends(_verify_admin)):
    """AI review content against brand guidelines."""
    from services.design_manager import validate_content
    return await validate_content(
        req.content_type,
        {"text": req.text, "colors": req.colors},
    )
