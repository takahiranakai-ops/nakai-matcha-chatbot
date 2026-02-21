"""Admin API endpoints for knowledge management and analytics."""

import asyncio
import logging
from typing import Optional

import io

from fastapi import (
    APIRouter, HTTPException, Header, Depends, Request,
    UploadFile, File, Form,
)
from pydantic import BaseModel, Field

from config import settings
from services import supabase_client

logger = logging.getLogger(__name__)

admin_api_router = APIRouter(prefix="/api/admin")


async def verify_admin(x_admin_password: str = Header(...)):
    if x_admin_password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Invalid admin password")
    return True


class ArticleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    language: str = Field(default="en", max_length=5)
    category: str = Field(default="general", max_length=50)


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    language: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class AdminLoginRequest(BaseModel):
    password: str


@admin_api_router.post("/login")
async def admin_login(body: AdminLoginRequest):
    if body.password == settings.admin_password:
        return {"authenticated": True}
    raise HTTPException(status_code=401, detail="Invalid password")


class WholesaleLoginRequest(BaseModel):
    password: str


@admin_api_router.post("/wholesale/login")
async def wholesale_login(body: WholesaleLoginRequest):
    if body.password == settings.wholesale_password:
        return {"authenticated": True}
    raise HTTPException(status_code=401, detail="Invalid password")


@admin_api_router.get("/articles")
async def list_articles(
    language: str = None,
    category: str = None,
    _auth: bool = Depends(verify_admin),
):
    articles = await supabase_client.list_articles(
        active_only=False,
        language=language,
        category=category,
    )
    return {"articles": articles}


@admin_api_router.get("/articles/{article_id}")
async def get_article(article_id: str, _auth: bool = Depends(verify_admin)):
    article = await supabase_client.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@admin_api_router.post("/articles")
async def create_article(body: ArticleCreate, _auth: bool = Depends(verify_admin)):
    article = await supabase_client.create_article(
        title=body.title,
        content=body.content,
        language=body.language,
        category=body.category,
    )
    if not article:
        raise HTTPException(status_code=500, detail="Failed to create article")
    return article


def _extract_pdf_text(pdf_bytes: bytes) -> str:
    """Extract text from PDF bytes using pypdf."""
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(pdf_bytes))
    pages_text = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            pages_text.append(page_text)
    return "\n\n".join(pages_text)


@admin_api_router.post("/articles/upload")
async def upload_article(
    file: UploadFile = File(...),
    title: str = Form(""),
    language: str = Form("en"),
    category: str = Form("general"),
    x_admin_password: str = Header(...),
):
    if x_admin_password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Invalid admin password")

    filename = file.filename or ""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ("txt", "pdf"):
        raise HTTPException(status_code=400, detail="Only .txt and .pdf files are supported")

    MAX_SIZE = 5 * 1024 * 1024
    content_bytes = await file.read()
    if len(content_bytes) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 5 MB.")

    try:
        if ext == "txt":
            text = content_bytes.decode("utf-8")
        else:
            text = _extract_pdf_text(content_bytes)
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="Could not decode text file. Ensure it is UTF-8 encoded.") from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to extract text from file: {exc}") from exc

    text = text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="File contains no extractable text")

    if not title.strip():
        title = filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()

    article = await supabase_client.create_article(
        title=title,
        content=text,
        language=language,
        category=category,
    )
    if not article:
        raise HTTPException(status_code=500, detail="Failed to create article")
    return article


@admin_api_router.patch("/articles/{article_id}")
async def update_article(
    article_id: str,
    body: ArticleUpdate,
    _auth: bool = Depends(verify_admin),
):
    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    article = await supabase_client.update_article(article_id, updates)
    if not article:
        raise HTTPException(status_code=500, detail="Failed to update article")
    return article


@admin_api_router.delete("/articles/{article_id}")
async def delete_article(article_id: str, _auth: bool = Depends(verify_admin)):
    success = await supabase_client.delete_article(article_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete article")
    return {"deleted": True}


@admin_api_router.post("/reingest")
async def trigger_reingest(_auth: bool = Depends(verify_admin)):
    import api.routes as routes_module
    if routes_module._refresh_running:
        return {"status": "already_running"}
    routes_module._refresh_running = True
    asyncio.create_task(routes_module._run_ingestion_background())
    return {"status": "started"}


@admin_api_router.get("/conversations")
async def list_conversations(
    limit: int = 50,
    offset: int = 0,
    source: str = None,
    language: str = None,
    _auth: bool = Depends(verify_admin),
):
    convs = await supabase_client.get_conversations_list(
        limit=limit, offset=offset, source=source, language=language
    )
    return {"conversations": convs}


@admin_api_router.get("/conversations/{conversation_id}/messages")
async def get_messages(conversation_id: str, _auth: bool = Depends(verify_admin)):
    messages = await supabase_client.get_conversation_messages(conversation_id)
    return {"messages": messages}


@admin_api_router.get("/analytics")
async def get_analytics(_auth: bool = Depends(verify_admin)):
    summary = await supabase_client.get_analytics_summary()
    return summary
