from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ngc_api_key: str = ""
    shopify_store_url: str = "nakaimatcha.com"
    shopify_storefront_token: str = ""
    shopify_admin_token: str = ""
    refresh_secret: str = "change-me"
    allowed_origins: str = "https://nakaimatcha.com,https://www.nakaimatcha.com"
    nvidia_chat_model: str = "qwen/qwen2.5-7b-instruct"
    nvidia_embed_model: str = "nvidia/nv-embedqa-e5-v5"
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    chroma_persist_dir: str = "./data/chroma_db"
    max_context_chunks: int = 5
    chunk_size: int = 500
    chunk_overlap: int = 50

    class Config:
        env_file = ".env"


settings = Settings()
