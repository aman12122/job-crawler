"""
Job Crawler - Data Models

Defines the core data structures for jobs and companies.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Company:
    """Represents a company being tracked."""
    
    name: str
    careers_url: str
    platform: str  # 'bamboohr', 'greenhouse', 'lever', 'custom'
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    last_crawled_at: Optional[datetime] = None


@dataclass
class Job:
    """Represents a job posting."""
    
    title: str
    url: str
    external_id: str
    company_name: str
    category: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    posted_at: Optional[datetime] = None
    first_seen_at: datetime = field(default_factory=datetime.now)
    is_entry_level: bool = False
    
    def __str__(self) -> str:
        location_str = f" ({self.location})" if self.location else ""
        return f"{self.title} at {self.company_name}{location_str}"
