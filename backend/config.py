from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ngc_api_key: str = ""
    shopify_store_url: str = "nakaimatcha.com"
    shopify_storefront_token: str = ""
    shopify_admin_token: str = ""
    refresh_secret: str = "change-me"
    allowed_origins: str = "https://nakaimatcha.com,https://www.nakaimatcha.com,https://nakai-matcha-chat.onrender.com"
    nvidia_chat_model: str = "nvidia/llama-3.3-nemotron-super-49b-v1.5"
    nvidia_embed_model: str = "nvidia/nv-embedqa-e5-v5"
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    chroma_persist_dir: str = "./data/chroma_db"
    max_context_chunks: int = 5
    chunk_size: int = 500
    chunk_overlap: int = 50
    supabase_url: str = ""
    supabase_service_key: str = ""
    admin_password: str = "change-me-admin"
    wholesale_password: str = "change-me-wholesale"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    # MCP SSE transport (OpenFang / external agents)
    mcp_api_key: str = ""  # Bearer token for authenticated MCP access
    # OpenFang Agent OS
    openfang_base_url: str = "http://localhost:50051"
    # WS34-41: Automation
    shopify_webhook_secret: str = ""
    serp_api_key: str = ""
    indexnow_api_key: str = ""
    enable_scheduler: bool = True
    # Email Marketing
    resend_api_key: str = ""
    anthropic_api_key: str = ""
    # Daily AI Tips auto-posting
    twitter_api_key: str = ""
    twitter_api_secret: str = ""
    twitter_access_token: str = ""
    twitter_access_secret: str = ""
    threads_access_token: str = ""
    threads_user_id: str = ""
    line_channel_access_token: str = ""
    daily_tips_hour_utc: int = 23  # 23:00 UTC = 08:00 JST
    # B2B Sales Automation
    google_places_api_key: str = ""
    hunter_io_api_key: str = ""
    b2b_daily_send_limit: int = 333
    b2b_from_email: str = "wholesale@nakaimatcha.com"
    b2b_reply_to: str = "wholesale@nakaimatcha.com"
    b2b_enabled: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
