import aiohttp
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Any
from ..models import Job, Company
from ..config import get_settings

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """
    Abstract base class for all company scrapers.
    Handles HTTP sessions, rate limiting, and common logic.
    """
    
    def __init__(self, company: Company):
        self.company = company
        self.settings = get_settings()
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=self.settings.REQUEST_TIMEOUT)
        self.session = aiohttp.ClientSession(
            headers={"User-Agent": self.settings.USER_AGENT},
            timeout=timeout
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def fetch(self, url: str, params: Optional[dict] = None) -> str:
        """
        Fetch a URL with rate limiting and error handling.
        Returns the response text (HTML or JSON).
        """
        if not self.session:
            raise RuntimeError("Scraper session not initialized. Use 'async with scraper:'")
            
        # Basic rate limiting (per scraper instance)
        await asyncio.sleep(self.settings.REQUEST_DELAY)
        
        try:
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                # Determine content type to return correct format
                content_type = response.headers.get('Content-Type', '')
                if 'application/json' in content_type:
                    return await response.json()
                return await response.text()
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            raise

    @abstractmethod
    async def scrape(self) -> List[Job]:
        """
        Main entry point. Scrapes all jobs using the configured strategy.
        Must handle pagination internally.
        """
        pass

    @abstractmethod
    async def fetch_job_detail(self, job: Job) -> Job:
        """
        Fetches the full description for a specific job.
        Updates the job object in place.
        """
        pass
