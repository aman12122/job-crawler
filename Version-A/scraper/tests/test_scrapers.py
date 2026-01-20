"""
Tests for the BambooHR scraper.
"""

import pytest
from unittest.mock import Mock, patch

from src.models import Job
from src.scrapers import BambooHRScraper, ENTRY_LEVEL_KEYWORDS


class TestBambooHRScraper:
    """Tests for BambooHRScraper class."""
    
    def test_init_extracts_company_subdomain(self):
        """Test that the scraper correctly extracts the company subdomain."""
        scraper = BambooHRScraper("https://d1g1t.bamboohr.com/careers")
        assert scraper.company_subdomain == "d1g1t"
    
    def test_init_builds_correct_api_url(self):
        """Test that the API URL is correctly constructed."""
        scraper = BambooHRScraper("https://d1g1t.bamboohr.com/careers")
        assert scraper.api_url == "https://d1g1t.bamboohr.com/careers/list"
    
    def test_init_strips_trailing_slash(self):
        """Test that trailing slashes are stripped from the URL."""
        scraper = BambooHRScraper("https://d1g1t.bamboohr.com/careers/")
        assert scraper.careers_url == "https://d1g1t.bamboohr.com/careers"
    
    def test_build_job_url(self):
        """Test that job URLs are correctly constructed."""
        scraper = BambooHRScraper("https://d1g1t.bamboohr.com/careers")
        url = scraper._build_job_url("123")
        assert url == "https://d1g1t.bamboohr.com/careers/123"
    

class TestEntryLevelDetection:
    """Tests for entry-level job detection."""
    
    def test_detects_new_grad_in_title(self):
        """Test that 'new grad' in title is detected."""
        scraper = BambooHRScraper("https://test.bamboohr.com/careers")
        assert scraper._is_entry_level("Software Engineer, New Grad") is True
    
    def test_detects_junior_in_title(self):
        """Test that 'junior' in title is detected."""
        scraper = BambooHRScraper("https://test.bamboohr.com/careers")
        assert scraper._is_entry_level("Junior Data Analyst") is True
    
    def test_detects_associate_in_title(self):
        """Test that 'associate' in title is detected."""
        scraper = BambooHRScraper("https://test.bamboohr.com/careers")
        assert scraper._is_entry_level("Associate Consultant") is True
    
    def test_detects_entry_level_in_title(self):
        """Test that 'entry level' in title is detected."""
        scraper = BambooHRScraper("https://test.bamboohr.com/careers")
        assert scraper._is_entry_level("Entry Level Software Developer") is True
    
    def test_detects_analyst_i(self):
        """Test that 'Analyst I' is detected as entry-level."""
        scraper = BambooHRScraper("https://test.bamboohr.com/careers")
        assert scraper._is_entry_level("Financial Analyst I") is True
    
    def test_rejects_senior_roles(self):
        """Test that senior roles are not flagged as entry-level."""
        scraper = BambooHRScraper("https://test.bamboohr.com/careers")
        assert scraper._is_entry_level("Senior Software Engineer") is False
    
    def test_rejects_director_roles(self):
        """Test that director roles are not flagged as entry-level."""
        scraper = BambooHRScraper("https://test.bamboohr.com/careers")
        assert scraper._is_entry_level("Director of Engineering") is False
    
    def test_case_insensitive(self):
        """Test that detection is case-insensitive."""
        scraper = BambooHRScraper("https://test.bamboohr.com/careers")
        assert scraper._is_entry_level("SOFTWARE ENGINEER, NEW GRAD") is True
        assert scraper._is_entry_level("JUNIOR developer") is True


class TestLocationParsing:
    """Tests for location string building."""
    
    def test_builds_location_from_ats_location(self):
        """Test building location from atsLocation field."""
        scraper = BambooHRScraper("https://test.bamboohr.com/careers")
        job_data = {
            "atsLocation": {
                "city": "Toronto",
                "province": "Ontario",
                "country": "Canada",
            }
        }
        location = scraper._build_location_string(job_data)
        assert location == "Toronto, Ontario, Canada"
    
    def test_builds_location_from_basic_location(self):
        """Test building location from basic location field."""
        scraper = BambooHRScraper("https://test.bamboohr.com/careers")
        job_data = {
            "location": {
                "city": "New York",
                "state": "NY",
            },
            "atsLocation": {},
        }
        location = scraper._build_location_string(job_data)
        assert location == "New York, NY"
    
    def test_returns_none_for_empty_location(self):
        """Test that None is returned when no location data exists."""
        scraper = BambooHRScraper("https://test.bamboohr.com/careers")
        job_data = {"location": {}, "atsLocation": {}}
        location = scraper._build_location_string(job_data)
        assert location is None
    
    def test_returns_remote_when_flagged(self):
        """Test that 'Remote' is returned when isRemote is True."""
        scraper = BambooHRScraper("https://test.bamboohr.com/careers")
        job_data = {"isRemote": True, "location": {}, "atsLocation": {}}
        location = scraper._build_location_string(job_data)
        assert location == "Remote"


class TestFetchJobs:
    """Tests for the fetch_jobs method."""
    
    @patch("src.scrapers.requests.Session.get")
    def test_fetch_jobs_parses_response(self, mock_get):
        """Test that fetch_jobs correctly parses the API response."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "meta": {"totalCount": 2},
            "result": [
                {
                    "id": "1",
                    "jobOpeningName": "Software Engineer, New Grad",
                    "departmentLabel": "Engineering",
                    "employmentStatusLabel": "Full-Time",
                    "location": {"city": "Toronto", "state": None},
                    "atsLocation": {},
                    "isRemote": False,
                },
                {
                    "id": "2",
                    "jobOpeningName": "Senior Manager",
                    "departmentLabel": "Operations",
                    "employmentStatusLabel": "Full-Time",
                    "location": {},
                    "atsLocation": {"country": "Canada"},
                    "isRemote": False,
                },
            ],
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        scraper = BambooHRScraper("https://test.bamboohr.com/careers")
        jobs = scraper.fetch_jobs()
        
        assert len(jobs) == 2
        
        # First job should be entry-level
        assert jobs[0].title == "Software Engineer, New Grad"
        assert jobs[0].is_entry_level is True
        assert jobs[0].category == "Engineering"
        assert jobs[0].url == "https://test.bamboohr.com/careers/1"
        
        # Second job should not be entry-level
        assert jobs[1].title == "Senior Manager"
        assert jobs[1].is_entry_level is False
    
    @patch("src.scrapers.requests.Session.get")
    def test_fetch_entry_level_jobs_filters(self, mock_get):
        """Test that fetch_entry_level_jobs only returns entry-level jobs."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "meta": {"totalCount": 2},
            "result": [
                {
                    "id": "1",
                    "jobOpeningName": "Junior Developer",
                    "departmentLabel": "Engineering",
                    "employmentStatusLabel": "Full-Time",
                    "location": {},
                    "atsLocation": {},
                    "isRemote": False,
                },
                {
                    "id": "2",
                    "jobOpeningName": "Senior Director",
                    "departmentLabel": "Leadership",
                    "employmentStatusLabel": "Full-Time",
                    "location": {},
                    "atsLocation": {},
                    "isRemote": False,
                },
            ],
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        scraper = BambooHRScraper("https://test.bamboohr.com/careers")
        jobs = scraper.fetch_entry_level_jobs()
        
        assert len(jobs) == 1
        assert jobs[0].title == "Junior Developer"


class TestJobModel:
    """Tests for the Job model."""
    
    def test_job_str_representation(self):
        """Test the string representation of a Job."""
        job = Job(
            title="Software Engineer",
            url="https://example.com/job/1",
            external_id="1",
            company_name="TestCo",
            location="Toronto",
        )
        assert str(job) == "Software Engineer at TestCo (Toronto)"
    
    def test_job_str_without_location(self):
        """Test string representation without location."""
        job = Job(
            title="Data Analyst",
            url="https://example.com/job/2",
            external_id="2",
            company_name="TestCo",
        )
        assert str(job) == "Data Analyst at TestCo"
