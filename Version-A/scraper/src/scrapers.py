"""
Job Crawler - BambooHR Scraper

Fetches job listings from BambooHR-hosted career pages.
BambooHR provides a JSON API at /careers/list which makes scraping reliable.
"""

import time
import re
from typing import Optional
from urllib.parse import urlparse

import requests

from .models import Job


# Keywords that indicate entry-level / new grad positions
ENTRY_LEVEL_KEYWORDS = [
    "new grad",
    "new graduate",
    "entry level",
    "entry-level",
    "junior",
    "associate",
    "analyst i",
    "analyst 1",
    "engineer i",
    "engineer 1",
    "level i",
    "level 1",
    "intern",
    "internship",
    "graduate",
    "early career",
    "0-2 years",
    "0-3 years",
    "1-2 years",
    "1-3 years",
]


class BambooHRScraper:
    """
    Scraper for BambooHR-hosted career pages.
    
    BambooHR uses a standard structure:
    - List endpoint: https://{company}.bamboohr.com/careers/list
    - Job detail page: https://{company}.bamboohr.com/careers/{job_id}
    """
    
    def __init__(self, careers_url: str, rate_limit_seconds: float = 1.0):
        """
        Initialize the scraper.
        
        Args:
            careers_url: The company's BambooHR careers page URL
                        (e.g., https://d1g1t.bamboohr.com/careers)
            rate_limit_seconds: Minimum seconds between requests (default: 1.0)
        """
        self.careers_url = careers_url.rstrip("/")
        self.rate_limit_seconds = rate_limit_seconds
        self.last_request_time: Optional[float] = None
        
        # Extract company subdomain for naming
        parsed = urlparse(self.careers_url)
        self.company_subdomain = parsed.netloc.split(".")[0]
        
        # Build API endpoint
        self.api_url = f"{self.careers_url}/list"
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "JobCrawler/1.0 (Educational Project)",
            "Accept": "application/json",
        })
    
    def _respect_rate_limit(self) -> None:
        """Wait if necessary to respect rate limiting."""
        if self.last_request_time is not None:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.rate_limit_seconds:
                time.sleep(self.rate_limit_seconds - elapsed)
        self.last_request_time = time.time()
    
    def _is_entry_level(self, job_title: str, department: str = "") -> bool:
        """
        Check if a job appears to be entry-level based on title and department.
        
        Args:
            job_title: The job title
            department: The department name (optional)
            
        Returns:
            True if the job appears to be entry-level
        """
        text_to_check = f"{job_title} {department}".lower()
        
        for keyword in ENTRY_LEVEL_KEYWORDS:
            if keyword in text_to_check:
                return True
        
        return False
    
    def _build_job_url(self, job_id: str) -> str:
        """Build the URL for a specific job posting."""
        return f"{self.careers_url}/{job_id}"
    
    def _build_location_string(self, job_data: dict) -> Optional[str]:
        """
        Build a human-readable location string from job data.
        
        Args:
            job_data: Raw job data from the API
            
        Returns:
            Location string or None if no location data
        """
        # Try atsLocation first (more detailed)
        ats_loc = job_data.get("atsLocation", {})
        if ats_loc:
            parts = []
            if ats_loc.get("city"):
                parts.append(ats_loc["city"])
            if ats_loc.get("state"):
                parts.append(ats_loc["state"])
            elif ats_loc.get("province"):
                parts.append(ats_loc["province"])
            if ats_loc.get("country"):
                parts.append(ats_loc["country"])
            if parts:
                return ", ".join(parts)
        
        # Fall back to basic location
        loc = job_data.get("location", {})
        if loc:
            parts = []
            if loc.get("city"):
                parts.append(loc["city"])
            if loc.get("state"):
                parts.append(loc["state"])
            if parts:
                return ", ".join(parts)
        
        # Check if remote
        if job_data.get("isRemote"):
            return "Remote"
        
        return None
    
    def fetch_jobs(self) -> list[Job]:
        """
        Fetch all job listings from the career page.
        
        Returns:
            List of Job objects
            
        Raises:
            requests.RequestException: If the request fails
        """
        self._respect_rate_limit()
        
        response = self.session.get(self.api_url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        jobs: list[Job] = []
        
        for job_data in data.get("result", []):
            job_id = str(job_data.get("id", ""))
            title = job_data.get("jobOpeningName", "Unknown Title")
            department = job_data.get("departmentLabel", "")
            employment_type = job_data.get("employmentStatusLabel")
            location = self._build_location_string(job_data)
            
            job = Job(
                title=title,
                url=self._build_job_url(job_id),
                external_id=job_id,
                company_name=self.company_subdomain,
                category=department if department else None,
                location=location,
                employment_type=employment_type,
                is_entry_level=self._is_entry_level(title, department),
            )
            jobs.append(job)
        
        return jobs
    
    def fetch_entry_level_jobs(self) -> list[Job]:
        """
        Fetch only entry-level job listings.
        
        Returns:
            List of Job objects that appear to be entry-level
        """
        all_jobs = self.fetch_jobs()
        return [job for job in all_jobs if job.is_entry_level]


def create_scraper(careers_url: str) -> BambooHRScraper:
    """
    Factory function to create the appropriate scraper for a careers URL.
    
    Currently only supports BambooHR. Future versions will detect
    the platform and return the appropriate scraper.
    
    Args:
        careers_url: The company's careers page URL
        
    Returns:
        A scraper instance
        
    Raises:
        ValueError: If the platform is not supported
    """
    if "bamboohr.com" in careers_url:
        return BambooHRScraper(careers_url)
    
    raise ValueError(f"Unsupported career page platform: {careers_url}")
