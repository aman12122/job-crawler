# Job Crawler Version B

## Overview
An AI-powered evolution of the job crawler, designed to find 100% of open jobs using pagination and filter them intelligently using Google Gemini.

## 🏗 Development Log

### Phase 3: AI Integration (Completed)
**Goal**: Connect the pipeline to Google Gemini Flash for intelligent job analysis.

#### 3.1 Rate Limiter (`src/ai/limiter.py`)
- Implemented a Token Bucket algorithm using `aiolimiter`.
- **Reasoning**: Strictly enforces the 15 Request Per Minute (RPM) limit of the Gemini Free Tier. This prevents "Quota Exceeded" errors and ensures long-running stability.

#### 3.2 AI Service (`src/ai/service.py`)
- Created `AIService` to wrap `google-generativeai` SDK calls.
- **Key Feature**: Requests JSON output from the model (`response_mime_type: application/json`) for reliable parsing.
- **Error Handling**: Gracefully handles API failures by marking jobs as `failed` (analysis status) rather than crashing the pipeline.

#### 3.3 Prompt Design
- **Prompt**: "You are a strict recruiter filtering jobs for a New Graduate (0-2 years)..."
- **Reasoning**: Explicitly instructs the model to ignore "Preferred" qualifications and focus on "Required" experience.
- **Output**: Returns `{ is_entry_level, confidence, min_years_experience, reasoning }`.

#### 3.4 Pipeline Integration (`src/pipeline.py`)
- Wired `AIService` into the async flow.
- **Optimization**: Added a dedicated `asyncio.Semaphore(1)` for the AI step to ensure requests are processed serially (matching the rate limiter) while other tasks (like fetching HTML) can happen in parallel.

### Phase 2: Scraper Engine (Completed)
**Goal**: Build the async scraping engine with pagination support and efficient queuing.

#### 2.1 Data Models (`src/models.py`)
- Defined strict Pydantic models for `Company`, `Job`, and `CrawlResult`.
- **Reasoning**: Ensures consistent data structure across the entire pipeline.

#### 2.2 Base Scraper (`src/scrapers/base.py`)
- Implemented the abstract `BaseScraper` class.
- **Key Feature**: Handles `aiohttp` sessions and basic rate limiting automatically.

#### 2.3 Pagination Strategies (`src/scrapers/strategies.py`)
- Implemented `OffsetPagination` (for APIs like Greenhouse) and `TokenPagination`.
- **Reasoning**: Decoupling pagination logic from the scraper allows us to mix-and-match strategies (e.g., a custom site might still use offset pagination).
- **Greenhouse Scraper**: Implemented the first concrete scraper (`src/scrapers/greenhouse.py`) using the offset strategy.

#### 2.4 Async Pipeline (`src/pipeline.py`)
- Implemented the `Pipeline` class to orchestrate: Scrape -> Pre-Filter -> Detail Fetch -> DB Save.
- **Concurrency**: Uses `asyncio.Semaphore` to limit concurrent detail fetches (default 5) to be polite to target servers.
- **Optimization**: Skips detail fetching for jobs rejected by the pre-filter.

#### 2.5 Filters (`src/filters.py`)
- Implemented `PreFilter` with a keyword rejection list ("Senior", "Staff", "Director").
- **Cost Saving**: This step runs *before* expensive operations (detail fetching & AI), saving bandwidth and eventual API costs.

### Phase 1: Foundation (Completed)
**Goal**: Establish the project structure, database schema, and core configuration.

#### 1.1 Directory Structure
- Created `scraper/src/` for Python modules and `scraper/sql/` for database scripts.
- **Reasoning**: Kept the structure similar to Version-A for familiarity, but introduced a proper Python package structure (`src/`) for better import handling and testing.

#### 1.2 Python Project Setup
- Created `pyproject.toml` instead of `requirements.txt`.
- **Reasoning**: Modern Python tooling (ruff, mypy, pytest) is better configured in a single TOML file.
- **Dependencies**: Added `asyncpg` (for speed), `aiohttp` (for async scraping), and `google-generativeai` (for Gemini).

#### 1.3 Database Schema (V2)
- Created `sql/001_v2_init.sql`.
- **Key Decision**: Added `v2_` prefix to all new tables.
- **Reasoning**: Allows running V1 and V2 side-by-side during the migration phase without data corruption.
- **New Fields**: Added `ai_reasoning`, `ai_confidence_score`, and `raw_description_text` to support transparency and re-analysis.

#### 1.4 Configuration Management
- Implemented `src/config.py` using `pydantic-settings`.
- **Reasoning**: Type safety for environment variables is critical when dealing with API keys and database credentials. It prevents runtime errors due to missing config.

#### 1.5 Async Database Module
- Implemented `src/database.py` using `asyncpg` with connection pooling.
- **Reasoning**: A singleton connection pool prevents opening too many connections to Postgres (crucial for the `e2-micro` VM which has limited resources).

#### 1.6 Documentation
- Added `scraper/README.md` with a guide on obtaining a free Google Gemini API key.

#### 1.7 Docker Environment
- Created `docker-compose.yml` for Version B.
- **Reasoning**: Provides an isolated local development environment with the V2 database schema mounted.

## 🚀 Getting Started

1.  **Get a Gemini API Key**: Follow instructions in [scraper/README.md](scraper/README.md).
2.  **Configure**: Copy `.env.example` to `.env` in `scraper/`.
3.  **Start DB**: `docker compose up -d db`
