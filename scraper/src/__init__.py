"""
Job Crawler Scraper

A Python package for crawling job postings from company career pages.
"""

from .models import Job, Company
from .scrapers import BambooHRScraper, create_scraper
from .database import Database, CompanyRepository, JobRepository
from .config import Config, get_config
from .main import run_crawler, run_crawler_for_url
from .cleanup import cleanup_old_jobs

__version__ = "0.2.0"

__all__ = [
    # Models
    "Job",
    "Company",
    # Scrapers
    "BambooHRScraper",
    "create_scraper",
    # Database
    "Database",
    "CompanyRepository",
    "JobRepository",
    # Config
    "Config",
    "get_config",
    # Main functions
    "run_crawler",
    "run_crawler_for_url",
    "cleanup_old_jobs",
]
