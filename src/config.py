"""
Configuration Module - PR Codex Reviewer

This module manages all application configurations, including:
- OpenAI API config (model selection, token limits, etc.)
- GitHub API config (authentication, webhook secrets, etc.)
- Code review config (supported languages, file size limits, etc.)
- Server config (port, host, debug mode, etc.)

Usage:
    from src.config import Config
    
    # Validate configuration
    Config.validate()
    
    # Access config values
    print(Config.OPENAI_MODEL)  # Output: gpt-4

Environment Variables:
    All configs can be set via environment variables. See .env.example file.
"""

import os
from typing import Optional


class Config:
    """
    Application Configuration
    
    Uses class attributes for all configs, allowing global access.
    All configs have defaults, but environment variables are recommended.
    
    Attributes:
        OPENAI_API_KEY: OpenAI API key for GPT-4/Codex
        OPENAI_MODEL: AI model to use, default: gpt-4
        OPENAI_MAX_TOKENS: Max tokens per request, default: 2000
        GITHUB_TOKEN: GitHub Personal Access Token
        GITHUB_WEBHOOK_SECRET: GitHub Webhook secret (optional)
        MAX_FILES_PER_REVIEW: Max files per review to prevent token overflow
        MAX_FILE_SIZE: Max file size in bytes
        SUPPORTED_LANGUAGES: List of supported programming languages
        PORT: Server port, default: 8000
        HOST: Server host, default: 0.0.0.0
        DEBUG: Debug mode, default: False
    """
    
    # ==================== OpenAI Config ====================
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    """OpenAI API Key - Required for AI model access"""
    
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    """AI Model - Optional, default: gpt-4, can use gpt-3.5-turbo to reduce cost"""
    
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
    """Max tokens per request - Controls response length and cost"""
    
    # ==================== GitHub Config ====================
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")
    """GitHub Personal Access Token - Required for repository access and posting comments"""
    
    GITHUB_WEBHOOK_SECRET: Optional[str] = os.getenv("GITHUB_WEBHOOK_SECRET")
    """GitHub Webhook Secret - Optional, for verifying webhook request authenticity"""
    
    # ==================== Review Config ====================
    MAX_FILES_PER_REVIEW: int = int(os.getenv("MAX_FILES_PER_REVIEW", "10"))
    """Max files per review - Prevents exceeding token limits"""
    
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "50000"))
    """Max file size in bytes - Filters out oversized files"""
    
    SUPPORTED_LANGUAGES: list = [
        "py", "js", "ts", "jsx", "tsx",
        "java", "kt", "scala",
        "go", "rs",
        "cpp", "c", "h", "hpp",
        "rb", "php",
        "swift", "m",
        "cs", "fs",
        "r", "m", "matlab",
        "sql",
    ]
    """Supported programming language extensions"""
    
    # ==================== Server Config ====================
    PORT: int = int(os.getenv("PORT", "8000"))
    """Server port - Default: 8000"""
    
    HOST: str = os.getenv("HOST", "0.0.0.0")
    """Server host - Default: 0.0.0.0 (listen on all interfaces)"""
    
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    """Debug mode - Default: False, set to True for detailed error messages"""
    
    @classmethod
    def validate(cls) -> None:
        """
        Validate required configuration.
        
        Checks if all required environment variables are set.
        Raises ValueError if any required config is missing.
        
        Required configs:
            - OPENAI_API_KEY
            - GITHUB_TOKEN
        
        Example:
            try:
                Config.validate()
                print("Configuration valid!")
            except ValueError as e:
                print(f"Configuration error: {e}")
        """
        required = ["OPENAI_API_KEY", "GITHUB_TOKEN"]
        missing = [key for key in required if not getattr(cls, key)]
        
        if missing:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing)}\n"
                f"Please copy .env.example to .env and fill in the values."
            )
