"""Central application settings sourced from the environment."""
from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    app_name: str = "ComicCraft"
    default_ai_provider: str = "gemini"
    gemini_api_key: str = ""
    groq_api_key: str = ""
    gemini_models: str = "gemini-3.8-flash,gemini-3.7-flash"
    groq_models: str = "qwen/qwen3.8-27b,llama-3.3-70b-versatile"
    default_gemini_model: str = "gemini-3.8-flash"
    default_groq_model: str = "qwen/qwen3.8-27b"
    image_provider: str = "huggingface"
    image_api_key: str = ""
    hf_api_key: str = ""
    image_model: str = "black-forest-labs/FLUX.1-schnell"
    image_timeout_seconds: int = 90
    ai_timeout_seconds: int = 90
    max_prompt_length: int = 2000
    max_panels: int = 9
    storage_dir: Path = ROOT_DIR / "storage"

    @field_validator("default_ai_provider")
    @classmethod
    def normalize_provider(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in {"gemini", "groq"}:
            raise ValueError("DEFAULT_AI_PROVIDER must be gemini or groq")
        return value

    def models_for(self, provider: str) -> list[str]:
        raw = self.gemini_models if provider.lower() == "gemini" else self.groq_models
        return [item.strip() for item in raw.split(",") if item.strip()]

    def default_model_for(self, provider: str) -> str:
        return self.default_gemini_model if provider.lower() == "gemini" else self.default_groq_model

    def key_for(self, provider: str) -> str:
        return self.gemini_api_key if provider.lower() == "gemini" else self.groq_api_key

    @property
    def effective_image_key(self) -> str:
        return self.image_api_key or self.hf_api_key


@lru_cache
def get_settings() -> Settings:
    return Settings()
