import logging
import asyncio
from aiohttp import web
from .pipeline import Pipeline
from .scrapers.greenhouse import GreenhouseScraper
from .models import Company
from .database import Database, CompanyRepository

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global lock to prevent concurrent crawls
CRAWL_LOCK = asyncio.Lock()

async def handle_crawl(request):
    """
    Trigger a crawl for all active companies.
    """
    if CRAWL_LOCK.locked():
        return web.json_response({'status': 'error', 'message': 'Crawl already in progress'}, status=409)

    # Start crawl in background task
    asyncio.create_task(run_background_crawl())
    
    return web.json_response({'status': 'accepted', 'message': 'Crawl started'}, status=202)

async def run_background_crawl():
    """
    Orchestrate the crawl process for all companies.
    """
    async with CRAWL_LOCK:
        logger.info("Starting background crawl...")
        try:
            # Initialize DB pool
            await Database.get_pool()
            
            # Get active companies
            companies = await CompanyRepository.get_active_companies()
            logger.info(f"Found {len(companies)} active companies to crawl.")
            
            for company in companies:
                logger.info(f"Processing company: {company.name}")
                
                # Select scraper strategy based on company config
                # Currently only Greenhouse is fully implemented in V2
                if company.strategy == 'greenhouse' or 'greenhouse.io' in company.careers_url:
                    scraper = GreenhouseScraper(company)
                    pipeline = Pipeline(scraper)
                    await pipeline.run()
                else:
                    logger.warning(f"No V2 scraper strategy for {company.name} ({company.strategy}). Skipping.")
            
            logger.info("Background crawl completed successfully.")
            
        except Exception as e:
            logger.error(f"Background crawl failed: {e}")
        finally:
            # Don't close the pool here if we want the server to keep running
            # But maybe good practice to keep connections healthy
            pass

async def health_check(request):
    return web.Response(text="OK")

async def init_app():
    app = web.Application()
    app.add_routes([
        web.post('/crawl', handle_crawl),
        web.get('/health', health_check)
    ])
    return app

def main():
    """
    Entry point to run the server.
    """
    app = init_app()
    web.run_app(app, port=8000)

if __name__ == '__main__':
    main()
