import asyncpg
import logging
from typing import Optional
from contextlib import asynccontextmanager
from .config import get_settings

logger = logging.getLogger(__name__)

class Database:
    """
    Manages the asyncpg connection pool for the application.
    Singleton pattern ensures only one pool is created.
    """
    _pool: Optional[asyncpg.Pool] = None

    @classmethod
    async def get_pool(cls) -> asyncpg.Pool:
        """
        Get the existing connection pool or create a new one.
        """
        if cls._pool is None:
            settings = get_settings()
            try:
                cls._pool = await asyncpg.create_pool(
                    dsn=settings.database_url,
                    min_size=1,
                    max_size=10,
                    command_timeout=60
                )
                logger.info("Database connection pool initialized.")
            except Exception as e:
                logger.error(f"Failed to create database pool: {e}")
                raise

        return cls._pool

    @classmethod
    async def close(cls):
        """Close the connection pool."""
        if cls._pool:
            await cls._pool.close()
            cls._pool = None
            logger.info("Database connection pool closed.")

    @classmethod
    @asynccontextmanager
    async def connection(cls):
        """
        Context manager for acquiring a connection from the pool.
        Usage:
            async with Database.connection() as conn:
                await conn.fetch(...)
        """
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            yield conn

    @classmethod
    async def init_schema(cls, schema_path: str = "sql/001_v2_init.sql"):
        """
        Initialize the database schema from a SQL file.
        """
        try:
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            async with cls.connection() as conn:
                # asyncpg doesn't support multiple commands in one execute,
                # but it supports it in execute() if separated by semicolons
                # or we can split it manually.
                # However, asyncpg's execute() often handles scripts fine if they are simple.
                # If complex, we might need to split.
                await conn.execute(schema_sql)
                logger.info(f"Schema initialized from {schema_path}")
        except FileNotFoundError:
            logger.error(f"Schema file not found: {schema_path}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize schema: {e}")
            raise
