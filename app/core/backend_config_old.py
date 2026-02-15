"""
Configuration settings for the AI Educational Document Reasoning System
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "AI Educational Document Reasoning System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/sqlite.db"
    
    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:14b"
    OLLAMA_TEMPERATURE: float = 0.7
    OLLAMA_TOP_P: float = 0.9
    OLLAMA_MAX_TOKENS: int = 2048
    
    # Embedding Model
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DEVICE: str = "cuda"  # or "cpu"
    
    # ChromaDB
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma_db"
    CHROMA_COLLECTION_NAME: str = "educational_documents"
    
    # Document Processing
    MAX_UPLOAD_SIZE_MB: int = 50
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    SUPPORTED_FORMATS: str = "pdf,docx,txt"
    UPLOAD_DIRECTORY: str = "./data/uploads"
    
    # Retrieval Settings
    TOP_K_RETRIEVAL: int = 10
    SIMILARITY_THRESHOLD: float = 0.7
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


# Ensure required directories exist
def create_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        "data",
        "data/uploads",
        "data/chroma_db",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Directory ensured: {directory}")


if __name__ == "__main__":
    create_directories()
    print("\n✅ All directories created successfully!")
    print(f"\n📋 Configuration Summary:")
    print(f"   - Ollama Model: {settings.OLLAMA_MODEL}")
    print(f"   - Embedding Device: {settings.EMBEDDING_DEVICE}")
    print(f"   - Database: {settings.DATABASE_URL}")
    print(f"   - ChromaDB: {settings.CHROMA_PERSIST_DIRECTORY}")
