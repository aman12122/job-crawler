"""
Job Crawler - Database Layer

Handles database connections and CRUD operations for jobs and companies.
Uses the Repository pattern for clean separation of concerns.
"""

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Generator, Optional

import psycopg2
from psycopg2.extras import RealDictCursor

from .config import get_config, DatabaseConfig
from .models import Job, Company


class Database:
    """Database connection manager."""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        """
        Initialize database connection.
        
        Args:
            config: Database configuration. Uses environment if not provided.
        """
        self.config = config or get_config().database
        self._connection: Optional[psycopg2.extensions.connection] = None
    
    def connect(self) -> psycopg2.extensions.connection:
        """Get or create database connection."""
        if self._connection is None or self._connection.closed:
            self._connection = psycopg2.connect(
                host=self.config.host,
                port=self.config.port,
                dbname=self.config.name,
                user=self.config.user,
                password=self.config.password,
            )
        return self._connection
    
    def close(self) -> None:
        """Close database connection."""
        if self._connection and not self._connection.closed:
            self._connection.close()
            self._connection = None
    
    @contextmanager
    def cursor(self, commit: bool = True) -> Generator[RealDictCursor, None, None]:
        """
        Context manager for database cursor.
        
        Args:
            commit: Whether to commit after the block (default True)
            
        Yields:
            Database cursor with dict-like row access
        """
        conn = self.connect()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cur
            if commit:
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
    
    def __enter__(self) -> "Database":
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()


class CompanyRepository:
    """Repository for company CRUD operations."""
    
    def __init__(self, db: Database):
        self.db = db
    
    def get_all_active(self) -> list[Company]:
        """Get all active companies."""
        with self.db.cursor(commit=False) as cur:
            cur.execute("""
                SELECT id, name, careers_url, platform, created_at, last_crawled_at
                FROM companies
                WHERE is_active = TRUE
                ORDER BY name
            """)
            rows = cur.fetchall()
            return [
                Company(
                    id=row["id"],
                    name=row["name"],
                    careers_url=row["careers_url"],
                    platform=row["platform"],
                    created_at=row["created_at"],
                    last_crawled_at=row["last_crawled_at"],
                )
                for row in rows
            ]
    
    def get_by_url(self, careers_url: str) -> Optional[Company]:
        """Get company by careers URL."""
        with self.db.cursor(commit=False) as cur:
            cur.execute("""
                SELECT id, name, careers_url, platform, created_at, last_crawled_at
                FROM companies
                WHERE careers_url = %s
            """, (careers_url,))
            row = cur.fetchone()
            if row:
                return Company(
                    id=row["id"],
                    name=row["name"],
                    careers_url=row["careers_url"],
                    platform=row["platform"],
                    created_at=row["created_at"],
                    last_crawled_at=row["last_crawled_at"],
                )
            return None
    
    def create(self, company: Company) -> Company:
        """Create a new company."""
        with self.db.cursor() as cur:
            cur.execute("""
                INSERT INTO companies (name, careers_url, platform)
                VALUES (%s, %s, %s)
                RETURNING id, created_at
            """, (company.name, company.careers_url, company.platform))
            row = cur.fetchone()
            company.id = row["id"]
            company.created_at = row["created_at"]
            return company
    
    def update_last_crawled(self, company_id: int) -> None:
        """Update the last_crawled_at timestamp for a company."""
        with self.db.cursor() as cur:
            cur.execute("""
                UPDATE companies
                SET last_crawled_at = NOW()
                WHERE id = %s
            """, (company_id,))


class JobRepository:
    """Repository for job CRUD operations."""
    
    def __init__(self, db: Database):
        self.db = db
    
    def upsert(self, job: Job, company_id: int) -> tuple[int, bool]:
        """
        Insert or update a job (upsert).
        
        Uses external_id for deduplication. If job exists, updates it.
        If job is new, inserts it.
        
        Args:
            job: The job to upsert
            company_id: The company ID
            
        Returns:
            Tuple of (job_id, is_new) where is_new indicates if this was an insert
        """
        with self.db.cursor() as cur:
            # Try to find existing job
            cur.execute("""
                SELECT id, first_seen_at FROM jobs
                WHERE company_id = %s AND external_id = %s
            """, (company_id, job.external_id))
            existing = cur.fetchone()
            
            if existing:
                # Update existing job (title/location might have changed)
                cur.execute("""
                    UPDATE jobs
                    SET title = %s,
                        category = %s,
                        location = %s,
                        employment_type = %s,
                        url = %s,
                        is_entry_level = %s
                    WHERE id = %s
                """, (
                    job.title,
                    job.category,
                    job.location,
                    job.employment_type,
                    job.url,
                    job.is_entry_level,
                    existing["id"],
                ))
                return existing["id"], False
            else:
                # Insert new job
                cur.execute("""
                    INSERT INTO jobs (
                        company_id, external_id, title, category, location,
                        employment_type, url, is_entry_level, posted_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    company_id,
                    job.external_id,
                    job.title,
                    job.category,
                    job.location,
                    job.employment_type,
                    job.url,
                    job.is_entry_level,
                    job.posted_at,
                ))
                row = cur.fetchone()
                return row["id"], True
    
    def get_all(
        self,
        entry_level_only: bool = False,
        company_id: Optional[int] = None,
        limit: int = 100,
    ) -> list[dict]:
        """
        Get jobs with optional filtering.
        
        Args:
            entry_level_only: Only return entry-level jobs
            company_id: Filter by company ID
            limit: Maximum number of jobs to return
            
        Returns:
            List of job dictionaries with company info
        """
        with self.db.cursor(commit=False) as cur:
            query = """
                SELECT 
                    j.id, j.title, j.category, j.location, j.employment_type,
                    j.url, j.is_entry_level, j.first_seen_at, j.created_at,
                    c.name as company_name, c.id as company_id
                FROM jobs j
                JOIN companies c ON j.company_id = c.id
                WHERE 1=1
            """
            params: list = []
            
            if entry_level_only:
                query += " AND j.is_entry_level = TRUE"
            
            if company_id is not None:
                query += " AND j.company_id = %s"
                params.append(company_id)
            
            query += " ORDER BY j.first_seen_at DESC LIMIT %s"
            params.append(limit)
            
            cur.execute(query, params)
            return list(cur.fetchall())
    
    def get_new_jobs(self, hours: int = 24) -> list[dict]:
        """
        Get jobs first seen within the last N hours.
        
        Args:
            hours: Number of hours to look back (default 24)
            
        Returns:
            List of new job dictionaries with company info
        """
        with self.db.cursor(commit=False) as cur:
            cur.execute("""
                SELECT 
                    j.id, j.title, j.category, j.location, j.employment_type,
                    j.url, j.is_entry_level, j.first_seen_at,
                    c.name as company_name
                FROM jobs j
                JOIN companies c ON j.company_id = c.id
                WHERE j.first_seen_at >= NOW() - INTERVAL '%s hours'
                ORDER BY j.first_seen_at DESC
            """, (hours,))
            return list(cur.fetchall())
    
    def delete_old_jobs(self, days: int = 7) -> int:
        """
        Delete jobs older than N days.
        
        Args:
            days: Number of days after which to delete jobs
            
        Returns:
            Number of jobs deleted
        """
        with self.db.cursor() as cur:
            cur.execute("""
                DELETE FROM jobs
                WHERE first_seen_at < NOW() - INTERVAL '%s days'
            """, (days,))
            return cur.rowcount
    
    def count(self, entry_level_only: bool = False) -> int:
        """Get total job count."""
        with self.db.cursor(commit=False) as cur:
            if entry_level_only:
                cur.execute("SELECT COUNT(*) as count FROM jobs WHERE is_entry_level = TRUE")
            else:
                cur.execute("SELECT COUNT(*) as count FROM jobs")
            row = cur.fetchone()
            return row["count"] if row else 0
