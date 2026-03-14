"""
ResearchHub AI – Application Configuration
Loads environment variables using pydantic-settings.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Central configuration loaded from .env file."""

    # ── Ollama (local LLM) ──────────────────────
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3:8b"

    # ── PostgreSQL ──────────────────────────────
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/researchhub"

    # ── Qdrant ──────────────────────────────────
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection_name: str = "research_papers"

    # ── Model Config ───────────────────────────
    # Embedding model: runs LOCALLY via sentence-transformers equivalent (ONNX)
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
