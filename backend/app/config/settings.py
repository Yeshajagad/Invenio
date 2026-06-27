from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "Invenio"
    app_version: str = "1.0.0"
    debug: bool = True
    secret_key: str = "change-me"

    # Database
    database_url: str

    # Qdrant
    qdrant_url: str
    qdrant_api_key: str
    qdrant_collection: str = "invenio_docs"

    # Redis
    redis_url: str

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3"

    # Embeddings
    embedding_model: str = "BAAI/bge-small-en-v1.5"

    # Files
    max_file_size_mb: int = 50
    upload_dir: str = "./uploads"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()