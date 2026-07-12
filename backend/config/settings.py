"""
Centralized application configuration.
All values are loaded from environment variables (see .env.example).
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=True)
model_config = SettingsConfigDict(
    # env_file=str(BASE_DIR / ".env"),
    # env_file_encoding="utf-8",
    # case_sensitive=True,
    extra="ignore",
)
class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "NexusAI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # --- Security / JWT ---
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24h

    # --- CORS ---
    CORS_ORIGINS: str = "http://localhost:5173"

    # --- Database (PostgreSQL) ---
    DATABASE_URL: str = (
        "postgresql+asyncpg://nexus:nexus@localhost:5432/nexusai"
    )

    # --- Redis ---
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- Qdrant ---
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION_NAME: str = "nexus_documents"
    EMBEDDING_DIM: int = 384  # bge-small-en-v1.5 output dimension

    # --- Embeddings ---
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-small-en-v1.5"

    # --- LLM (RAG answer generation) ---
    # Provider is pluggable; default to Groq (fast, cheap, LLaMA-3 access).
    LLM_PROVIDER: str = "groq"
    GROQ_API_KEY: str = ""
    GROQ_MODEL_NAME: str = "llama-3.3-70b-versatile"

    # --- File uploads ---
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 20

    # --- Chunking ---
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100

    # --- Logging ---
    LOG_LEVEL: str = "INFO"

    # model_config = SettingsConfigDict(
    #     env_file=".env",
    #     env_file_encoding="utf-8",
    #     case_sensitive=True,
    #     extra="ignore",
    # )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor so we don't re-parse env vars on every call."""
    return Settings()


settings = get_settings()

