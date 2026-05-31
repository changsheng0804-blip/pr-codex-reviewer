"""
Configuration module for PR Codex Reviewer
"""
import os
from typing import Optional


class Config:
    """Application configuration"""
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
    
    # GitHub Configuration
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")
    GITHUB_WEBHOOK_SECRET: Optional[str] = os.getenv("GITHUB_WEBHOOK_SECRET")
    
    # Review Configuration
    MAX_FILES_PER_REVIEW: int = int(os.getenv("MAX_FILES_PER_REVIEW", "10"))
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "100000"))  # 100KB
    SUPPORTED_LANGUAGES: list = [
        "python", "javascript", "typescript", "java", "go", "rust", "cpp", "c"
    ]
    
    # Server Configuration
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        required_vars = ["OPENAI_API_KEY", "GITHUB_TOKEN"]
        missing = [var for var in required_vars if not getattr(cls, var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        return True
