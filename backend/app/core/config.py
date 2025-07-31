from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # LLM Configuration
    google_api_key: str
    google_proyect_id: Optional[str] = None
    default_llm_model: str = "gemini-1.5-pro"
    fallback_llm_model: str = "gemini-1.5-flash"
    
    # Database Configuration
    database_url: str = "postgresql://user:password@postgres:5432/agents_db"
    redis_url: str = "redis://redis:6379/0"
    
    # Vector Store Configuration
    chroma_url: str = "http://chromadb:8000"
    chroma_persist_directory: str = "./chroma_db"
    
    # App Configuration
    debug: bool = True
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings() 