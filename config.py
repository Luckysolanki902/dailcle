"""
Configuration management using Pydantic Settings.
Loads environment variables from .env file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"  # Cost-effective model for personal use
    
    # Notion Configuration
    notion_api_key: str
    notion_parent_page_id: str
    notion_parent_url: str = "https://www.notion.so/luckysolanki-personal/Daily-articles-2bbe80b58b6a8017854ce39c2109eedb"
    
    # Email Configuration
    smtp_host: str
    smtp_port: int = 587
    smtp_user: str
    smtp_password: str
    email_from: str
    email_from_name: str = "Lucky's Daily Mentor"
    email_to: str
    
    # Server Configuration
    environment: str = "production"
    timezone: str = "Asia/Kolkata"
    cron_schedule: str = "0 6 * * *"  # Daily at 6:00 AM IST
    max_tokens: int = 16000
    temperature: float = 0.3
    
    # Optional: Cloud Storage
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    s3_bucket_name: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
