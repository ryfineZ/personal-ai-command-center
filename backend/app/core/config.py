"""
Personal AI Command Center - Configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # App
    APP_NAME: str = "Personal AI Command Center"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./command_center.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ENCRYPTION_KEY: str = "your-encryption-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # AI
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OPENAI_API_KEY: Optional[str] = None
    DEFAULT_MODEL: str = "llama3"
    
    # Email
    IMAP_SERVER: str = "imap.gmail.com"
    SMTP_SERVER: str = "smtp.gmail.com"
    IMAP_PORT: int = 993
    SMTP_PORT: int = 587
    EMAIL_ADDRESS: Optional[str] = None
    EMAIL_PASSWORD: Optional[str] = None
    
    # Social Media
    TWITTER_API_KEY: Optional[str] = None
    TWITTER_API_SECRET: Optional[str] = None
    TWITTER_ACCESS_TOKEN: Optional[str] = None
    TWITTER_ACCESS_SECRET: Optional[str] = None
    LINKEDIN_CLIENT_ID: Optional[str] = None
    LINKEDIN_CLIENT_SECRET: Optional[str] = None
    
    # Smart Home
    HOME_ASSISTANT_URL: Optional[str] = None
    HOME_ASSISTANT_TOKEN: Optional[str] = None
    
    # Browser Automation
    PLAYWRIGHT_HEADLESS: bool = True
    BROWSER_TIMEOUT: int = 30000  # 30 seconds
    
    # HITL (Human-in-the-Loop)
    HITL_ENABLED: bool = True
    HITL_TIMEOUT: int = 300  # 5 minutes
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
