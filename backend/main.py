from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from api.middleware import setup_rate_limiting
from config import settings

app = FastAPI(title="NAKAI Matcha Chatbot API", version="1.0.0")

origins = [origin.strip() for origin in settings.allowed_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type", "X-Refresh-Secret"],
)

setup_rate_limiting(app)

app.include_router(router, prefix="/api")
