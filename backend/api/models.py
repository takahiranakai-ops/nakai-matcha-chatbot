from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: list[dict] = Field(default_factory=list, max_length=20)
    language: str = Field(default="en", max_length=5)


class ChatResponse(BaseModel):
    response: str
    sources: list[str] = []


class RefreshResponse(BaseModel):
    status: str
    documents_indexed: int
