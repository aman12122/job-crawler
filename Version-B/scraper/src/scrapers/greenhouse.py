from typing import List, Dict, Any, Tuple, Optional
from bs4 import BeautifulSoup
from ..models import Job
from .base import BaseScraper
from .strategies import OffsetPagination

class GreenhouseScraper(BaseScraper):
    """
    Scraper for Greenhouse-powered career pages.
    Uses OffsetPagination strategy.
    """
    
    def __init__(self, company, page_size: int = 100):
        super().__init__(company)
        self.pagination = OffsetPagination(self, limit_param='per_page', offset_param='offset', page_size=page_size)

    async def scrape(self) -> List[Job]:
        """
        Delegates crawling to the pagination strategy.
        """
        return await self.pagination.fetch_all_jobs()

    def parse_jobs(self, data: Any) -> List[Job]:
        """
        Parses the JSON response from Greenhouse API.
        """
        # Greenhouse often returns JSON like: { "jobs": [ ... ], "meta": { ... } }
        # Or sometimes just a list if it's a specific endpoint
        
        jobs_data = []
        if isinstance(data, dict):
            jobs_data = data.get('jobs', [])
        elif isinstance(data, list):
            jobs_data = data
            
        jobs = []
        for item in jobs_data:
            job = Job(
                company_id=self.company.id,
                external_id=str(item.get('id')),
                title=item.get('title', 'Unknown'),
                url=item.get('absolute_url', ''),
                location=item.get('location', {}).get('name'),
                department=item.get('departments', [{}])[0].get('name'),
                first_seen_at=None  # Will be set by DB
            )
            jobs.append(job)
            
        return jobs

    async def fetch_job_detail(self, job: Job) -> Job:
        """
        Fetches the full HTML description.
        """
        html = await self.fetch(job.url)
        
        # Parse HTML to get clean text
        soup = BeautifulSoup(html, 'lxml')
        content_div = soup.find('div', id='content') or soup.find('div', id='app_body')
        
        if content_div:
            # Remove scripts and styles
            for script in content_div(["script", "style"]):
                script.decompose()
                
            job.raw_description_html = str(content_div)
            job.raw_description_text = content_div.get_text(separator='\n').strip()
        else:
            # Fallback to whole body if specific div not found
            job.raw_description_text = soup.get_text(separator='\n').strip()
            
        return job
