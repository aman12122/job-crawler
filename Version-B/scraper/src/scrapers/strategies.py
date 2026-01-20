import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict
from ..models import Job
from .base import BaseScraper

logger = logging.getLogger(__name__)

class PaginationStrategy(ABC):
    """
    Abstract base for pagination logic.
    """
    def __init__(self, scraper: BaseScraper):
        self.scraper = scraper

    @abstractmethod
    async def fetch_all_jobs(self) -> List[Job]:
        pass

class OffsetPagination(PaginationStrategy):
    """
    Handles offset-based pagination (e.g., ?limit=100&offset=0).
    Common in Greenhouse APIs.
    """
    def __init__(self, scraper: BaseScraper, limit_param: str = 'limit', offset_param: str = 'offset', page_size: int = 100):
        super().__init__(scraper)
        self.limit_param = limit_param
        self.offset_param = offset_param
        self.page_size = page_size

    async def fetch_all_jobs(self) -> List[Job]:
        all_jobs = []
        offset = 0
        
        while True:
            params = {self.limit_param: self.page_size, self.offset_param: offset}
            logger.info(f"Fetching page with offset {offset} for {self.scraper.company.name}")
            
            try:
                response_data = await self.scraper.fetch(self.scraper.company.careers_url, params=params)
                jobs = self.scraper.parse_jobs(response_data)
                
                if not jobs:
                    break
                    
                all_jobs.extend(jobs)
                
                if len(jobs) < self.page_size:
                    # Last page reached
                    break
                    
                offset += self.page_size
                
            except Exception as e:
                logger.error(f"Pagination failed at offset {offset}: {e}")
                break
                
        return all_jobs

class TokenPagination(PaginationStrategy):
    """
    Handles cursor/token-based pagination (e.g., ?next=TOKEN).
    Common in Lever and Workday.
    """
    def __init__(self, scraper: BaseScraper, cursor_param: str = 'cursor'):
        super().__init__(scraper)
        self.cursor_param = cursor_param

    async def fetch_all_jobs(self) -> List[Job]:
        all_jobs = []
        cursor = None
        
        while True:
            params = {}
            if cursor:
                params[self.cursor_param] = cursor
                
            logger.info(f"Fetching page with cursor {cursor} for {self.scraper.company.name}")
            
            try:
                response_data = await self.scraper.fetch(self.scraper.company.careers_url, params=params)
                jobs, next_cursor = self.scraper.parse_jobs_with_cursor(response_data)
                
                if jobs:
                    all_jobs.extend(jobs)
                
                if not next_cursor or next_cursor == cursor:
                    break
                    
                cursor = next_cursor
                
            except Exception as e:
                logger.error(f"Pagination failed at cursor {cursor}: {e}")
                break
                
        return all_jobs
