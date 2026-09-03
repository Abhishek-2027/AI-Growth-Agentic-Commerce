from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    # App
    project_name: str = "AgentCart — Safe Agentic Commerce Platform"
    debug: bool = True
    frontend_url: str = "http://localhost:5173"
    secret_key: str = "change-me-in-production"
    jwt_secret_key: str = "change-me-in-production"

    # MongoDB
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_uri: str = ""
    mongodb_database: str = "agentcart"

    # LLM
    google_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    groq_api_key: str = ""
    default_llm_provider: str = "gemini"

    # Razorpay
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""

    # Commerce Safety Policy
    default_max_budget: int = 50000
    max_quantity_per_order: int = 5
    allowed_currency: str = "INR"
    require_approval_for_all_purchases: bool = True
    enable_safety_guardrails: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def effective_mongodb_uri(self) -> str:
        """Return the most specific MongoDB URI available."""
        if self.mongodb_uri:
            return self.mongodb_uri
        return self.mongodb_url


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
