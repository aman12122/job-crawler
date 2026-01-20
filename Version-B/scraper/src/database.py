import asyncpg
import logging
from typing import Optional, List
from contextlib import asynccontextmanager
from .config import get_settings
from .models import Job, Company

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
                await conn.execute(schema_sql)
                logger.info(f"Schema initialized from {schema_path}")
        except FileNotFoundError:
            logger.error(f"Schema file not found: {schema_path}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize schema: {e}")
            raise

class CompanyRepository:
    """Data access for Company objects."""
    
    @staticmethod
    async def get_active_companies() -> List[Company]:
        async with Database.connection() as conn:
            rows = await conn.fetch("""
                SELECT * FROM v2_companies 
                WHERE is_active = TRUE
            """)
            return [Company(**dict(row)) for row in rows]

    @staticmethod
    async def get_by_id(company_id: int) -> Optional[Company]:
        async with Database.connection() as conn:
            row = await conn.fetchrow("""
                SELECT * FROM v2_companies WHERE id = $1
            """, company_id)
            if row:
                return Company(**dict(row))
            return None

class JobRepository:
    """Data access for Job objects."""
    
    @staticmethod
    async def upsert_jobs(jobs: List[Job]) -> int:
        """
        Insert or update jobs. Returns number of new jobs inserted.
        """
        if not jobs:
            return 0
            
        async with Database.connection() as conn:
            # Prepare data for bulk insert
            values = []
            for job in jobs:
                values.append((
                    job.company_id,
                    job.external_id,
                    job.title,
                    job.url,
                    job.location,
                    job.department,
                    job.employment_type,
                    job.raw_description_text,
                    job.raw_description_html,
                    job.analysis_status,
                    job.prefilter_rejected,
                    job.prefilter_reason
                ))
            
            # Using execute_many for bulk upsert is complex with ON CONFLICT
            # So we loop or construct a large query. For simplicity and robustness with <1000 jobs, 
            # we can use executemany with a smart query or loop.
            # Here we'll use a loop with a prepared statement for simplicity, or executemany.
            # Since we need to know how many were *new*, normal executemany doesn't tell us easily.
            # We'll stick to a loop for now or simple "INSERT ... ON CONFLICT DO NOTHING" count.
            
            # Let's count insertions
            inserted_count = 0
            
            stmt = await conn.prepare("""
                INSERT INTO v2_jobs (
                    company_id, external_id, title, url, 
                    location, department, employment_type,
                    raw_description_text, raw_description_html,
                    analysis_status, prefilter_rejected, prefilter_reason,
                    last_seen_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, NOW())
                ON CONFLICT (company_id, external_id) 
                DO UPDATE SET
                    title = EXCLUDED.title,
                    url = EXCLUDED.url,
                    last_seen_at = NOW(),
                    -- Only update content if it was null
                    raw_description_text = COALESCE(v2_jobs.raw_description_text, EXCLUDED.raw_description_text),
                    analysis_status = CASE 
                        WHEN v2_jobs.analysis_status = 'pending' THEN EXCLUDED.analysis_status
                        ELSE v2_jobs.analysis_status 
                    END
                RETURNING (xmax = 0) AS is_new
            """)
            
            for val in values:
                try:
                    is_new = await stmt.fetchval(*val)
                    if is_new:
                        inserted_count += 1
                except Exception as e:
                    logger.error(f"Failed to upsert job {val[2]}: {e}")
            
            return inserted_count
