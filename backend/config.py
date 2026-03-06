from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ngc_api_key: str = ""
    shopify_store_url: str = "nakaimatcha.com"
    shopify_storefront_token: str = ""
    shopify_admin_token: str = ""
    refresh_secret: str = "change-me"
    allowed_origins: str = "https://nakaimatcha.com,https://www.nakaimatcha.com"
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

    class Config:
        env_file = ".env"


settings = Settings()
