"""
Tests for database operations.

These are integration tests that require a running PostgreSQL database.
Run with: pytest tests/test_database.py -v
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

from src.models import Job, Company
from src.database import Database, CompanyRepository, JobRepository
from src.config import DatabaseConfig


# Test configuration - uses test database
TEST_DB_CONFIG = DatabaseConfig(
    host="localhost",
    port=5434,
    name="job_crawler",
    user="jobcrawler",
    password="jobcrawler_dev",
)


class TestDatabaseConnection:
    """Tests for Database connection class."""
    
    def test_connection_url_property(self):
        """Test that connection URL is correctly formatted."""
        config = DatabaseConfig(
            host="localhost",
            port=5432,
            name="test_db",
            user="test_user",
            password="test_pass",
        )
        expected = "postgresql://test_user:test_pass@localhost:5432/test_db"
        assert config.connection_url == expected
    
    def test_database_context_manager(self):
        """Test that database can be used as context manager."""
        with Database(TEST_DB_CONFIG) as db:
            assert db._connection is not None
            assert not db._connection.closed
        # After context, connection should be closed
        assert db._connection is None or db._connection.closed
    
    def test_cursor_context_manager(self):
        """Test that cursor context manager works."""
        with Database(TEST_DB_CONFIG) as db:
            with db.cursor(commit=False) as cur:
                cur.execute("SELECT 1 as value")
                row = cur.fetchone()
                assert row["value"] == 1


class TestCompanyRepository:
    """Tests for CompanyRepository class."""
    
    def test_get_all_active_returns_companies(self):
        """Test that get_all_active returns the seeded company."""
        with Database(TEST_DB_CONFIG) as db:
            repo = CompanyRepository(db)
            companies = repo.get_all_active()
            
            assert len(companies) >= 1
            # d1g1t should be in the list (seeded)
            d1g1t = next((c for c in companies if c.name == "d1g1t"), None)
            assert d1g1t is not None
            assert d1g1t.careers_url == "https://d1g1t.bamboohr.com/careers"
            assert d1g1t.platform == "bamboohr"
    
    def test_get_by_url_returns_company(self):
        """Test that get_by_url finds the correct company."""
        with Database(TEST_DB_CONFIG) as db:
            repo = CompanyRepository(db)
            company = repo.get_by_url("https://d1g1t.bamboohr.com/careers")
            
            assert company is not None
            assert company.name == "d1g1t"
    
    def test_get_by_url_returns_none_for_unknown(self):
        """Test that get_by_url returns None for unknown URL."""
        with Database(TEST_DB_CONFIG) as db:
            repo = CompanyRepository(db)
            company = repo.get_by_url("https://unknown.example.com/careers")
            
            assert company is None


class TestJobRepository:
    """Tests for JobRepository class."""
    
    @pytest.fixture
    def db(self):
        """Provide a database connection."""
        with Database(TEST_DB_CONFIG) as db:
            yield db
    
    @pytest.fixture
    def company_id(self, db):
        """Get the d1g1t company ID for testing."""
        repo = CompanyRepository(db)
        company = repo.get_by_url("https://d1g1t.bamboohr.com/careers")
        assert company is not None
        return company.id
    
    def test_upsert_creates_new_job(self, db, company_id):
        """Test that upsert creates a new job."""
        repo = JobRepository(db)
        
        # Create a test job with unique external_id
        test_id = f"test_{datetime.now().timestamp()}"
        job = Job(
            title="Test Engineer",
            url=f"https://example.com/jobs/{test_id}",
            external_id=test_id,
            company_name="d1g1t",
            category="Engineering",
            location="Toronto",
            is_entry_level=True,
        )
        
        job_id, is_new = repo.upsert(job, company_id)
        
        assert job_id > 0
        assert is_new is True
        
        # Clean up
        with db.cursor() as cur:
            cur.execute("DELETE FROM jobs WHERE external_id = %s", (test_id,))
    
    def test_upsert_updates_existing_job(self, db, company_id):
        """Test that upsert updates an existing job."""
        repo = JobRepository(db)
        
        # Create a test job
        test_id = f"test_update_{datetime.now().timestamp()}"
        job = Job(
            title="Original Title",
            url=f"https://example.com/jobs/{test_id}",
            external_id=test_id,
            company_name="d1g1t",
            is_entry_level=False,
        )
        
        # Insert
        job_id_1, is_new_1 = repo.upsert(job, company_id)
        assert is_new_1 is True
        
        # Update with new title
        job.title = "Updated Title"
        job.is_entry_level = True
        job_id_2, is_new_2 = repo.upsert(job, company_id)
        
        assert job_id_2 == job_id_1  # Same job ID
        assert is_new_2 is False  # Not a new insert
        
        # Verify update
        with db.cursor(commit=False) as cur:
            cur.execute("SELECT title, is_entry_level FROM jobs WHERE id = %s", (job_id_1,))
            row = cur.fetchone()
            assert row["title"] == "Updated Title"
            assert row["is_entry_level"] is True
        
        # Clean up
        with db.cursor() as cur:
            cur.execute("DELETE FROM jobs WHERE external_id = %s", (test_id,))
    
    def test_get_all_returns_jobs(self, db, company_id):
        """Test that get_all returns jobs."""
        repo = JobRepository(db)
        
        # Insert a test job
        test_id = f"test_getall_{datetime.now().timestamp()}"
        job = Job(
            title="Test Job for Get All",
            url=f"https://example.com/jobs/{test_id}",
            external_id=test_id,
            company_name="d1g1t",
            is_entry_level=True,
        )
        repo.upsert(job, company_id)
        
        # Get all jobs
        jobs = repo.get_all(limit=100)
        assert len(jobs) >= 1
        
        # Verify our test job is in the list
        test_job = next((j for j in jobs if j["title"] == "Test Job for Get All"), None)
        assert test_job is not None
        
        # Clean up
        with db.cursor() as cur:
            cur.execute("DELETE FROM jobs WHERE external_id = %s", (test_id,))
    
    def test_get_all_entry_level_filter(self, db, company_id):
        """Test that get_all filters by entry_level."""
        repo = JobRepository(db)
        
        # Insert entry-level job
        test_id_1 = f"test_entry_{datetime.now().timestamp()}"
        job1 = Job(
            title="Junior Developer",
            url=f"https://example.com/jobs/{test_id_1}",
            external_id=test_id_1,
            company_name="d1g1t",
            is_entry_level=True,
        )
        repo.upsert(job1, company_id)
        
        # Insert senior job
        test_id_2 = f"test_senior_{datetime.now().timestamp()}"
        job2 = Job(
            title="Senior Developer",
            url=f"https://example.com/jobs/{test_id_2}",
            external_id=test_id_2,
            company_name="d1g1t",
            is_entry_level=False,
        )
        repo.upsert(job2, company_id)
        
        # Get only entry-level
        entry_jobs = repo.get_all(entry_level_only=True)
        
        # All returned jobs should be entry-level
        for job in entry_jobs:
            assert job["is_entry_level"] is True
        
        # Clean up
        with db.cursor() as cur:
            cur.execute("DELETE FROM jobs WHERE external_id IN (%s, %s)", (test_id_1, test_id_2))
    
    def test_delete_old_jobs(self, db, company_id):
        """Test that delete_old_jobs removes old entries."""
        repo = JobRepository(db)
        
        # Insert a job with old first_seen_at
        test_id = f"test_old_{datetime.now().timestamp()}"
        with db.cursor() as cur:
            cur.execute("""
                INSERT INTO jobs (company_id, external_id, title, url, is_entry_level, first_seen_at)
                VALUES (%s, %s, %s, %s, %s, NOW() - INTERVAL '10 days')
                RETURNING id
            """, (company_id, test_id, "Old Job", "https://example.com/old", False))
            old_job_id = cur.fetchone()["id"]
        
        # Delete jobs older than 7 days
        deleted_count = repo.delete_old_jobs(days=7)
        
        assert deleted_count >= 1
        
        # Verify the old job is gone
        with db.cursor(commit=False) as cur:
            cur.execute("SELECT id FROM jobs WHERE id = %s", (old_job_id,))
            assert cur.fetchone() is None
    
    def test_count(self, db, company_id):
        """Test that count returns correct counts."""
        repo = JobRepository(db)
        
        total = repo.count()
        entry_level = repo.count(entry_level_only=True)
        
        assert isinstance(total, int)
        assert isinstance(entry_level, int)
        assert entry_level <= total
