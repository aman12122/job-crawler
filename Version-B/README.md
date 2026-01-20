# Job Crawler Version B

## Overview
An AI-powered evolution of the job crawler, designed to find 100% of open jobs using pagination and filter them intelligently using Google Gemini.

## 🏗 Development Log

### Phase 1: Foundation (Current)
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
