"""Application configuration via Pydantic Settings."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db_name: str = "whatsapp_ai"
    groq_api_key: str = ""
    whatsapp_token: str = ""
    phone_number_id: str = ""
    verify_token: str = "whatsapp_verify_token"
    port: int = 8000
    default_tenant_id: str = "tenantA"
    groq_model: str = "llama-3.3-70b-versatile"
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
