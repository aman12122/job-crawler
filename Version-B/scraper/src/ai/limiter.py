import logging
import asyncio
from aiolimiter import AsyncLimiter
from ..config import get_settings

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Manages API quota for Google Gemini.
    Default: 15 requests per minute (Free Tier).
    """
    
    _instance = None
    
    def __init__(self):
        settings = get_settings()
        # 15 requests per 60 seconds
        self.limit = settings.AI_REQUESTS_PER_MINUTE
        self.limiter = AsyncLimiter(self.limit, 60)
        logger.info(f"AI Rate Limiter initialized: {self.limit} RPM")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = RateLimiter()
        return cls._instance

    async def acquire(self):
        """
        Wait until a token is available.
        """
        await self.limiter.acquire()
