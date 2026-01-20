# Job Crawler - Scraper

Python web scraper for tracking job postings from company career pages.

## Prerequisites

- Python 3.11+
- Docker (for PostgreSQL database)

## Setup

### 1. Start the Database

From the project root:

```bash
docker compose up -d
```

This starts PostgreSQL on port 5434 with:
- Database: `job_crawler`
- User: `jobcrawler`
- Password: `jobcrawler_dev`

### 2. Set Up Python Environment

```bash
cd scraper

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment config
cp .env.example .env
```

## Usage

### Run the Crawler

```bash
# Crawl all active companies and save to database
python -m src.main

# Only show entry-level positions
python -m src.main --entry-level-only

# Dry run (don't save to database)
python -m src.main --no-save

# Crawl a specific URL (bypasses database)
python -m src.main --url https://example.bamboohr.com/careers
```

### Clean Up Old Jobs

```bash
# Remove jobs older than 7 days
python -m src.cleanup

# Preview what would be deleted
python -m src.cleanup --dry-run

# Custom retention period
python -m src.cleanup --days 14
```

## Project Structure

```
scraper/
├── src/
│   ├── __init__.py      # Package exports
│   ├── main.py          # CLI entry point
│   ├── scrapers.py      # BambooHR scraper
│   ├── models.py        # Job and Company dataclasses
│   ├── database.py      # PostgreSQL repositories
│   ├── config.py        # Environment configuration
│   └── cleanup.py       # Job retention cleanup
├── tests/
│   ├── test_scrapers.py # Scraper unit tests
│   └── test_database.py # Database integration tests
├── sql/
│   └── 001_init.sql     # Database schema
├── pyproject.toml       # Python dependencies
└── .env.example         # Environment template
```

## Development

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Lint code
ruff check src/

# Type check
mypy src/
```

## Database Schema

### Companies Table

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| name | VARCHAR(255) | Company name |
| careers_url | TEXT | Career page URL |
| platform | VARCHAR(50) | Platform type (bamboohr, greenhouse, etc.) |
| is_active | BOOLEAN | Whether to crawl this company |
| last_crawled_at | TIMESTAMP | Last successful crawl time |

### Jobs Table

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| company_id | INTEGER | Foreign key to companies |
| external_id | VARCHAR(255) | Job ID from source site |
| title | VARCHAR(500) | Job title |
| category | VARCHAR(255) | Department/category |
| location | VARCHAR(255) | Job location |
| url | TEXT | Link to job posting |
| is_entry_level | BOOLEAN | Matches entry-level criteria |
| first_seen_at | TIMESTAMP | When job was first discovered |

## Supported Platforms

- [x] BambooHR (`*.bamboohr.com/careers`)
- [ ] Greenhouse (coming soon)
- [ ] Lever (coming soon)
- [ ] Workday (coming soon)
