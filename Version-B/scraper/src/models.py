from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, HttpUrl

class Company(BaseModel):
    """
    Represents a company being tracked.
    Matches v2_companies table.
    """
    id: Optional[int] = None
    name: str
    careers_url: str
    strategy: Literal['auto', 'bamboohr', 'greenhouse', 'lever', 'workday', 'custom'] = 'auto'
    pagination_type: Literal['auto', 'offset', 'token', 'link', 'none'] = 'auto'
    custom_config: Optional[dict] = None
    is_active: bool = True
    last_crawled_at: Optional[datetime] = None

class Job(BaseModel):
    """
    Represents a job posting.
    Matches v2_jobs table.
    """
    id: Optional[int] = None
    company_id: int
    external_id: str
    title: str
    url: str
    
    # Metadata
    location: Optional[str] = None
    department: Optional[str] = None
    employment_type: Optional[str] = None
    
    # Content
    raw_description_text: Optional[str] = None
    raw_description_html: Optional[str] = None
    
    # AI Analysis Fields
    analysis_status: Literal['pending', 'analyzed', 'failed', 'skipped'] = 'pending'
    ai_is_entry_level: Optional[bool] = None
    ai_confidence_score: Optional[int] = None
    ai_years_required: Optional[int] = None
    ai_reasoning: Optional[str] = None
    
    # Pre-filter
    prefilter_rejected: bool = False
    prefilter_reason: Optional[str] = None
    
    first_seen_at: Optional[datetime] = None
    
class CrawlResult(BaseModel):
    """
    Summary of a crawl operation.
    """
    company_id: int
    jobs_found: int = 0
    jobs_added: int = 0
    pages_crawled: int = 0
    status: Literal['success', 'failed'] = 'success'
    error_message: Optional[str] = None
