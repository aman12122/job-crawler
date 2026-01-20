from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    """
    Application configuration using Pydantic Settings.
    Reads from environment variables and .env file.
    """
    
    # Database Configuration
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "job_crawler"
    DATABASE_USER: str = "jobcrawler"
    DATABASE_PASSWORD: str
    
    # Google Gemini AI Configuration
    GEMINI_API_KEY: str
    AI_REQUESTS_PER_MINUTE: int = 15  # Default to free tier limit
    
    # Scraper Configuration
    MAX_CONCURRENT_FETCHES: int = 5
    REQUEST_DELAY: float = 1.0  # Seconds
    REQUEST_TIMEOUT: int = 30   # Seconds
    USER_AGENT: str = "JobCrawler/2.0 (Entry Level Job Finder; +http://localhost)"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def database_url(self) -> str:
        """Constructs the asyncpg connection string."""
        return f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached instance of the settings.
    This ensures we only read environment variables once.
    """
    return Settings()
