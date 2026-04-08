import re
from typing import Literal, List

from pydantic import BaseModel, Field, field_validator


class HistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., max_length=2000)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: List[HistoryMessage] = Field(default_factory=list, max_length=20)
    language: Literal["en", "ja"] = "en"
    session_id: str = Field(default="", max_length=100)
    source: Literal["pwa", "widget", "wholesale"] = "pwa"

    @field_validator("session_id")
    @classmethod
    def validate_session_id(cls, v: str) -> str:
        if v and not re.fullmatch(r'[a-zA-Z0-9_-]{1,100}', v):
            raise ValueError("Invalid session_id format")
        return v


class ChatResponse(BaseModel):
    response: str
    sources: list[str] = []
    suggestions: list[str] = []


class RefreshResponse(BaseModel):
    status: str
    documents_indexed: int
