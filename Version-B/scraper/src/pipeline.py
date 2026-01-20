import asyncio
import logging
from typing import List, Set
from .models import Job, Company, CrawlResult
from .filters import PreFilter
from .database import Database, JobRepository
from .scrapers.base import BaseScraper
from .config import get_settings
from .ai.service import AIService

logger = logging.getLogger(__name__)

class Pipeline:
    """
    Orchestrates the crawling process:
    Scrape -> PreFilter -> Detail Fetch -> AI Analysis -> DB Save
    """
    
    def __init__(self, scraper: BaseScraper):
        self.scraper = scraper
        self.settings = get_settings()
        self.db = Database()
        self.ai_service = AIService()
        
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
            # Semaphores:
            # - Fetching: Limit based on config to be polite
            # - AI: Limit to 1 concurrent task to respect rate limiter smoothly
            fetch_sem = asyncio.Semaphore(self.settings.MAX_CONCURRENT_FETCHES)
            ai_sem = asyncio.Semaphore(1) 
            
            async def process_job(job: Job):
                # 2a. Pre-filter
                PreFilter.filter(job)
                if job.prefilter_rejected:
                    logger.debug(f"Skipped {job.title}: {job.prefilter_reason}")
                    return job

                # 2b. Fetch Details
                async with fetch_sem:
                    try:
                        async with self.scraper: 
                            await self.scraper.fetch_job_detail(job)
                    except Exception as e:
                        logger.error(f"Failed to fetch details for {job.title}: {e}")
                        # Don't fail completely, just skip AI
                        job.analysis_status = 'failed'
                        return job

                # 2c. AI Analysis (if details exist)
                if job.raw_description_text:
                    async with ai_sem:
                        try:
                            await self.ai_service.analyze_job(job)
                        except Exception as e:
                            logger.error(f"AI step failed for {job.title}: {e}")
                            job.analysis_status = 'failed'
                
                return job

            # Run processing concurrently
            # Note: We process all jobs found. In a real large-scale system, 
            # we might want to batch this or use a proper queue.
            processed_jobs = await asyncio.gather(*[process_job(job) for job in jobs])
            
            # 3. Save to Database
            # We save ALL jobs, even rejected ones, to avoid re-crawling them
            repo = JobRepository()
            jobs_added = await repo.upsert_jobs(processed_jobs)
            result.jobs_added = jobs_added
            
            # Calculate stats
            result.pages_crawled = 1 # TODO: Update scraper to return page count
            
            logger.info(f"Crawl finished for {self.scraper.company.name}. Added {jobs_added} jobs.")
            
        except Exception as e:
            logger.error(f"Crawl failed for {self.scraper.company.name}: {e}")
            result.status = 'failed'
            result.error_message = str(e)
            
        return result
