"""
Job Crawler - Configuration

Loads configuration from environment variables.
"""

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


# Load .env file if present
load_dotenv()


@dataclass
class DatabaseConfig:
    """Database connection configuration."""
    
    host: str
    port: int
    name: str
    user: str
    password: str
    
    @property
    def connection_url(self) -> str:
        """Get the database connection URL."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
    
    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Load configuration from environment variables."""
        # Try DATABASE_URL first (common in cloud environments)
        url = os.getenv("DATABASE_URL")
        if url:
            # Parse URL: postgresql://user:password@host:port/database
            # Simple parsing - could use urllib.parse for robustness
            import re
            pattern = r"postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)"
            match = re.match(pattern, url)
            if match:
                return cls(
                    user=match.group(1),
                    password=match.group(2),
                    host=match.group(3),
                    port=int(match.group(4)),
                    name=match.group(5),
                )
        
        # Fall back to individual variables
        return cls(
            host=os.getenv("DATABASE_HOST", "localhost"),
            port=int(os.getenv("DATABASE_PORT", "5434")),
            name=os.getenv("DATABASE_NAME", "job_crawler"),
            user=os.getenv("DATABASE_USER", "jobcrawler"),
            password=os.getenv("DATABASE_PASSWORD", "jobcrawler_dev"),
        )


@dataclass
class Config:
    """Application configuration."""
    
    database: DatabaseConfig
    
    # Crawler settings
    rate_limit_seconds: float = 1.0
    job_retention_days: int = 7
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load full configuration from environment."""
        return cls(
            database=DatabaseConfig.from_env(),
            rate_limit_seconds=float(os.getenv("RATE_LIMIT_SECONDS", "1.0")),
            job_retention_days=int(os.getenv("JOB_RETENTION_DAYS", "7")),
        )


# Global config instance (lazy loaded)
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the application configuration (singleton)."""
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config
