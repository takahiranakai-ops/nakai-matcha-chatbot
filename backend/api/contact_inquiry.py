"""NAKAI Contact Inquiry — Receives form data from Shopify contact page via sendBeacon."""
import logging
import re
from typing import Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from api.middleware import limiter
from services import supabase_client

logger = logging.getLogger(__name__)

contact_inquiry_router = APIRouter()


class ContactInquiryBody(BaseModel):
    inquiry_type: str = Field(default="General", max_length=100)
    name: str = Field(default="", max_length=200)
    email: str = Field(default="", max_length=254)
    company: str = Field(default="", max_length=200)
    phone: str = Field(default="", max_length=50)
    business_type: str = Field(default="", max_length=100)
    monthly_volume: str = Field(default="", max_length=100)
    preferred_dates: Optional[list[str]] = None
    message: str = Field(default="", max_length=5000)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if v and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", v):
            raise ValueError("Invalid email format")
        return v


@contact_inquiry_router.post("/api/contact-inquiry")
@limiter.limit("10/minute")
async def submit_contact_inquiry(request: Request):
    """Store contact inquiry in Supabase. Accepts JSON via sendBeacon (text/plain or application/json)."""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"status": "error", "detail": "Invalid JSON"}, status_code=400)

    inquiry = ContactInquiryBody(**body)

    stored = False
    emailed = False

    try:
        await supabase_client.create_contact_inquiry(
            inquiry_type=inquiry.inquiry_type,
            name=inquiry.name,
            email=inquiry.email,
            company=inquiry.company,
            phone=inquiry.phone,
            business_type=inquiry.business_type,
            monthly_volume=inquiry.monthly_volume,
            preferred_dates=inquiry.preferred_dates,
            message=inquiry.message,
        )
        stored = True
    except Exception as e:
        logger.error(f"Failed to store contact inquiry: {e}")

    try:
        from services.email_client import send_contact_inquiry_notification
        emailed = await send_contact_inquiry_notification(inquiry)
    except Exception as e:
        logger.warning(f"Contact email notification skipped: {e}")

    if not stored and not emailed:
        return JSONResponse({"status": "error"}, status_code=500)

    return JSONResponse({"status": "ok"})
