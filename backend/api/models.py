from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: list[dict] = Field(default_factory=list, max_length=20)
    language: Literal["en", "ja"] = "en"
    session_id: str = Field(default="", max_length=100)
    source: Literal["pwa", "widget", "wholesale"] = "pwa"


class ChatResponse(BaseModel):
    response: str
    sources: list[str] = []
    suggestions: list[str] = []


class RefreshResponse(BaseModel):
    status: str
    documents_indexed: int
