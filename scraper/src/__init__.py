"""
Job Crawler Scraper

A Python package for crawling job postings from company career pages.
"""

from .models import Job, Company
from .scrapers import BambooHRScraper, create_scraper
from .main import run_crawler

__version__ = "0.1.0"

__all__ = [
    "Job",
    "Company",
    "BambooHRScraper",
    "create_scraper",
    "run_crawler",
]
