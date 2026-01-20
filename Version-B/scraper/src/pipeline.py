import asyncio
import logging
from typing import List, Set
from .models import Job, Company, CrawlResult
from .filters import PreFilter
from .database import Database, JobRepository
from .scrapers.base import BaseScraper
from .config import get_settings

logger = logging.getLogger(__name__)

class Pipeline:
    """
    Orchestrates the crawling process:
    Scrape -> PreFilter -> Detail Fetch -> DB Save
    """
    
    def __init__(self, scraper: BaseScraper):
        self.scraper = scraper
        self.settings = get_settings()
        self.db = Database()
        
    async def run(self) -> CrawlResult:
        """
        Executes the full pipeline for a company.
        """
        result = CrawlResult(company_id=self.scraper.company.id)
        
        try:
            # 1. Scrape all jobs (Discovery Phase)
            logger.info(f"Starting crawl for {self.scraper.company.name}")
            async with self.scraper:
                jobs = await self.scraper.scrape()
                
            result.jobs_found = len(jobs)
            logger.info(f"Found {len(jobs)} jobs for {self.scraper.company.name}")
            
            # 2. Process jobs
            # We use a semaphore to limit concurrent detail fetching
            sem = asyncio.Semaphore(self.settings.MAX_CONCURRENT_FETCHES)
            
            async def process_job(job: Job):
                # 2a. Pre-filter
                PreFilter.filter(job)
                if job.prefilter_rejected:
                    logger.debug(f"Skipped {job.title}: {job.prefilter_reason}")
                    return job

                # 2b. Fetch Details (if not skipped)
                async with sem:
                    try:
                        # Re-open session if needed, but here we assume scraper session is closed
                        # Ideally scraper handles its own session context.
                        # For now, we'll open a temporary session for details or refactor.
                        # Refactor: We should keep scraper session open or create new one.
                        # Let's assume we re-enter context for each fetch if needed, 
                        # or better, just use a new session for the detail fetcher.
                        async with self.scraper: # Re-enter context to get a session
                            await self.scraper.fetch_job_detail(job)
                    except Exception as e:
                        logger.error(f"Failed to fetch details for {job.title}: {e}")
                        # Don't fail the whole crawl, just this job
                        pass
                
                return job

            # Run processing concurrently
            processed_jobs = await asyncio.gather(*[process_job(job) for job in jobs])
            
            # 3. Save to Database
            # We save ALL jobs, even rejected ones, to avoid re-crawling them
            repo = JobRepository()
            jobs_added = await repo.upsert_jobs(processed_jobs)
            result.jobs_added = jobs_added
            
            logger.info(f"Crawl finished for {self.scraper.company.name}. Added {jobs_added} jobs.")
            
        except Exception as e:
            logger.error(f"Crawl failed for {self.scraper.company.name}: {e}")
            result.status = 'failed'
            result.error_message = str(e)
            
        return result
