"""
Configuration management using environment variables.
All secrets and settings are loaded from .env file.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""
    
    # AI Mode Configuration
    AI_MODE: str = os.getenv("AI_MODE", "api")  # 'api' or 'local'
    
    # OpenRouter Configuration
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Crawler Settings
    MAX_CRAWL_DEPTH: int = int(os.getenv("MAX_CRAWL_DEPTH", "2"))
    MAX_PAGES_PER_SITE: int = int(os.getenv("MAX_PAGES_PER_SITE", "50"))
    CRAWL_DELAY_SECONDS: float = float(os.getenv("CRAWL_DELAY_SECONDS", "1.0"))
    
    # RAG Settings
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "400"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", "5"))
    
    # Model Settings (OpenRouter format: provider/model:variant)
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "openai/text-embedding-3-small")
    CHAT_MODEL: str = os.getenv("CHAT_MODEL", "meta-llama/llama-3.1-8b-instruct:free")
    
    # Local Model Settings (for AI_MODE=local)
    LOCAL_LLM_MODEL: str = os.getenv("LOCAL_LLM_MODEL", "google/flan-t5-large")
    LOCAL_EMBEDDING_MODEL: str = os.getenv("LOCAL_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    # Storage Paths
    VECTOR_STORE_PATH: Path = Path(os.getenv("VECTOR_STORE_PATH", "./storage/vector_stores"))
    SESSION_STORE_PATH: Path = Path(os.getenv("SESSION_STORE_PATH", "./storage/sessions"))
    
    def __init__(self):
        """Ensure storage directories exist."""
        self.VECTOR_STORE_PATH.mkdir(parents=True, exist_ok=True)
        self.SESSION_STORE_PATH.mkdir(parents=True, exist_ok=True)
        
        # Validate critical settings based on AI mode
        if self.AI_MODE == "api":
            if not self.OPENROUTER_API_KEY:
                raise ValueError("OPENROUTER_API_KEY must be set in .env file when AI_MODE=api")

# Global settings instance
settings = Settings()
