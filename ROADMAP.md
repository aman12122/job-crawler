# Job Crawler - Project Roadmap

> A tool to track new grad and associate-level job postings from specific company career pages.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Problem Statement](#problem-statement)
3. [User Stories](#user-stories)
4. [Technical Architecture](#technical-architecture)
5. [MVP Specification](#mvp-specification)
6. [Phased Roadmap](#phased-roadmap)
7. [Future Enhancements](#future-enhancements)
8. [Risks & Considerations](#risks--considerations)
9. [Development Log](#development-log)

---

## Project Overview

| Attribute | Value |
|-----------|-------|
| **Project Name** | job-crawler |
| **Author** | Aman |
| **Created** | January 2026 |
| **Status** | Phase 1: Scraper MVP |

### Goals

- Automatically crawl company career pages for new job postings
- Filter for new grad / associate / entry-level roles (0-3 years experience)
- Store job data with 7-day retention
- Send daily email digest of new postings at 12:00 PM EST
- Provide a simple web UI to browse and sort jobs

### Target Job Categories

- Software Engineering
- Data Science
- Finance
- Consulting

### Initial Scope

- 1 test company (d1g1t via BambooHR)
- Expand to ~20 companies after MVP validation

---

## Problem Statement

### Pain Points

1. **Missing time-sensitive postings**: New grad roles often fill within 24-48 hours. Manually checking career sites daily is impractical.

2. **Tedious manual process**: Visiting 20+ individual career pages is time-consuming for a busy student.

3. **Existing tools fall short**: LinkedIn job alerts are noisy, surface irrelevant senior roles, and don't allow focusing on specific target companies.

### Solution

An automated crawler that:
- Monitors specific company career pages (user-provided URLs)
- Identifies new grad/associate roles via keyword matching
- Sends a daily digest highlighting new postings
- Provides a simple web interface for browsing all tracked jobs

---

## User Stories

### Core User Stories (MVP)

| ID | Story | Priority |
|----|-------|----------|
| US-01 | As a job seeker, I want the system to automatically check career pages daily so I don't have to manually visit each site | High |
| US-02 | As a job seeker, I want to receive an email digest of new jobs at noon so I can review them during lunch | High |
| US-03 | As a job seeker, I want each job in the email to have a clickable link so I can quickly apply | High |
| US-04 | As a job seeker, I want to view all jobs on a web page sorted by date, company, or category | High |
| US-05 | As a job seeker, I want jobs older than 7 days to be automatically removed to keep the list relevant | Medium |

### Future User Stories

| ID | Story | Priority |
|----|-------|----------|
| US-06 | As a job seeker, I want to add new companies to track via the web UI | Medium |
| US-07 | As a job seeker, I want to exclude jobs with certain keywords (e.g., "Senior", "5+ years") | Medium |
| US-08 | As a job seeker, I want to configure which job categories to track | Low |
| US-09 | As a job seeker, I want to subscribe multiple email addresses to the digest | Low |

---

## Technical Architecture

### System Diagram

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Career Sites   │────▶│  Python Scraper  │────▶│   PostgreSQL    │
│  (BambooHR,     │     │  (Cloud Run Job) │     │   (Cloud SQL)   │
│   Greenhouse,   │     └──────────────────┘     └────────┬────────┘
│   etc.)         │                                       │
└─────────────────┘                                       │
                                                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   User Email    │◀────│   Email Service  │◀────│   Next.js App   │
│   (Gmail)       │     │   (Gmail API)    │     │   (Cloud Run)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                          │
                              ┌────────────────────────────
                              ▼
                        ┌─────────────────┐
                        │  Cloud Scheduler│
                        │  (12 PM EST)    │
                        └─────────────────┘
```

### Tech Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Scraper** | Python 3.11+ | Best ecosystem for web scraping (requests, BeautifulSoup, Playwright) |
| **Database** | PostgreSQL 15 (Cloud SQL) | Scalable, reliable, excellent free tier on GCP |
| **Frontend** | Next.js 14 (TypeScript) | Full-stack framework, handles API routes, easy deployment |
| **Hosting** | Google Cloud Platform | Free tier available, integrates with Gmail |
| **Scheduler** | Cloud Scheduler | Managed cron jobs, triggers Cloud Run |
| **Email** | Gmail API | User's preferred email provider |

### Database Schema (Initial)

```sql
-- Companies to track
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    careers_url TEXT NOT NULL,
    platform VARCHAR(50), -- 'bamboohr', 'greenhouse', 'lever', 'custom'
    created_at TIMESTAMP DEFAULT NOW(),
    last_crawled_at TIMESTAMP
);

-- Job postings
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    external_id VARCHAR(255), -- ID from the career site
    title VARCHAR(500) NOT NULL,
    category VARCHAR(100),
    location VARCHAR(255),
    url TEXT NOT NULL,
    posted_at TIMESTAMP,
    first_seen_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(company_id, external_id)
);

-- Index for cleanup job
CREATE INDEX idx_jobs_first_seen ON jobs(first_seen_at);
```

---

## MVP Specification

### MVP Scope

The minimum viable product will:

1. **Crawl one career site** (d1g1t BambooHR page)
2. **Store jobs** in PostgreSQL with deduplication
3. **Display jobs** on a simple web page with sorting
4. **Send daily email** at 12 PM EST with new jobs
5. **Auto-cleanup** jobs older than 7 days

### MVP Exclusions

The MVP will NOT include:
- Web UI for adding companies (config file only)
- Keyword exclusion filters
- Multiple email recipients
- Mobile-responsive design
- Job board integrations (LinkedIn, Indeed)

### Test Career Site

- **Company**: d1g1t
- **URL**: https://d1g1t.bamboohr.com/careers
- **Platform**: BambooHR (standardized structure)

### Email Digest Format

```
Subject: Job Crawler Daily Digest - [Date]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Summary: 3 new jobs found today

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Software Engineer, New Grad          [Apply]
• Data Analyst I                       [Apply]  
• Junior Consultant                    [Apply]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

View all jobs: https://your-app-url.run.app
```

### Web UI Wireframe

```
┌────────────────────────────────────────────────────────────┐
│  Job Crawler                                               │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Sort by: [Company ▼]  [Category ▼]  [Date ▼]              │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Software Engineer, New Grad                          │  │
│  │ d1g1t · Engineering · Posted Jan 18, 2026   [View →] │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Data Analyst I                                       │  │
│  │ d1g1t · Data · Posted Jan 17, 2026          [View →] │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## Phased Roadmap

### Phase 0: Project Setup ✅
**Goal**: Initialize repository and development environment

- [x] Create GitHub repository
- [x] Set up project structure (monorepo: `/scraper`, `/web`)
- [x] Initialize Python environment (pyproject.toml, venv)
- [x] Initialize Next.js app with TypeScript
- [ ] Create GCP project and enable required APIs *(deferred to Phase 5)*
- [x] Document local development setup in README

### Phase 1: Scraper MVP ✅
**Goal**: Fetch jobs from d1g1t and print to console

- [x] Research BambooHR API/page structure
- [x] Create Python scraper for BambooHR sites
- [x] Parse job listings (title, category, location, URL)
- [x] Implement new grad/associate keyword detection
- [x] Add rate limiting and polite crawling (respect robots.txt)
- [x] Write unit tests for parser

### Phase 2: Database Integration ✅
**Goal**: Persist jobs to PostgreSQL

- [x] Set up local PostgreSQL for development
- [x] Implement database schema (companies, jobs tables)
- [x] Add job deduplication logic (external_id)
- [x] Create cleanup job for 7-day retention
- [ ] Set up Cloud SQL instance on GCP *(deferred to Phase 5)*
- [x] Test database operations

### Phase 3: Web UI MVP ✅
**Goal**: Display jobs on a web page with sorting

- [x] Create Next.js API routes for fetching jobs
- [x] Build job listing page with sorting controls
- [x] Style with basic CSS (clean, functional)
- [x] Add clickable links to original postings
- [x] Test locally with database

### Phase 4: Email Digest
**Goal**: Send daily email with new jobs

- [ ] Set up Gmail API credentials
- [ ] Create email template (HTML)
- [ ] Implement email sending logic
- [ ] Track "new" jobs (first_seen_at within 24 hours)
- [ ] Test email delivery

### Phase 5: Deployment
**Goal**: Deploy to GCP and run automatically

- [ ] Dockerize scraper (Python)
- [ ] Dockerize web app (Next.js)
- [ ] Deploy to Cloud Run
- [ ] Configure Cloud Scheduler for 12 PM EST
- [ ] Set up environment variables and secrets
- [ ] Configure Cloud SQL connection
- [ ] Test end-to-end in production

### Phase 6: Multi-Company Expansion
**Goal**: Add more career sites

- [ ] Add 5-10 additional companies to config
- [ ] Test scraper with different BambooHR sites
- [ ] Research and add support for Greenhouse platform
- [ ] Research and add support for Lever platform
- [ ] Document how to add new companies

---

## Future Enhancements

### Backlog (Post-MVP)

| Feature | Description | Priority |
|---------|-------------|----------|
| **Web UI for adding companies** | Form to add new career page URLs | High |
| **Keyword exclusions** | Filter out jobs containing "Senior", "Staff", "Manager", "5+ years", etc. | High |
| **Greenhouse support** | Parser for Greenhouse-hosted career pages | Medium |
| **Lever support** | Parser for Lever-hosted career pages | Medium |
| **Workday support** | Parser for Workday-hosted career pages | Medium |
| **Custom site support** | Generic scraper with configurable selectors | Medium |
| **Multiple recipients** | Allow multiple email addresses for digest | Low |
| **Mobile-friendly UI** | Responsive design for phone access | Low |
| **Job board APIs** | Integrate LinkedIn, Indeed, Glassdoor APIs | Low |
| **Application tracking** | Mark jobs as "applied", "interested", "rejected" | Low |
| **Export to CSV** | Download job list as spreadsheet | Low |

---

## Risks & Considerations

### Legal & Ethical

| Risk | Mitigation |
|------|------------|
| **Terms of Service violations** | Review each site's ToS before scraping; use APIs when available |
| **Rate limiting / IP blocking** | Implement polite crawling: 1-2 requests per second, respect robots.txt |
| **CAPTCHA / bot detection** | Start with API-friendly sites (BambooHR); escalate to Playwright if needed |

### Technical

| Risk | Mitigation |
|------|------------|
| **Site structure changes** | Build modular parsers; add health checks to detect parsing failures |
| **Database costs** | Use Cloud SQL free tier; implement strict 7-day retention |
| **Email deliverability** | Use Gmail API properly; avoid spam triggers |

### Operational

| Risk | Mitigation |
|------|------------|
| **Missing new jobs** | Run crawler multiple times daily in future phases |
| **Scraper failures** | Add error logging and alerting; send failure notifications |

---

## Development Log

> Document significant decisions, learnings, and progress here.

### January 19, 2026

#### Phase 0 Completed
- **Project initiated**: Created roadmap document after requirements gathering session
- **Test site selected**: d1g1t BambooHR careers page (https://d1g1t.bamboohr.com/careers)
- **Key discovery**: BambooHR sites use a standardized structure, likely with JSON API endpoints for job data
- **Decision**: Start with BambooHR parser as it can support multiple companies using the same platform
- **GitHub repo created**: https://github.com/aman12122/job-crawler
- **Project structure established**: `/scraper` (Python), `/web` (Next.js)

#### Phase 1 Started: Scraper MVP

**Objective**: Build a working scraper that fetches jobs from d1g1t's BambooHR careers page

**User Stories Being Addressed**:
- **US-01**: *"As a job seeker, I want the system to automatically check career pages daily so I don't have to manually visit each site"*

**Pain Points Being Solved**:
- **Tedious manual process**: This scraper eliminates the need to manually visit career pages
- **Missing time-sensitive postings**: Automated crawling ensures no new postings are missed

**Progress**:

1. **Discovered BambooHR JSON API** - The `/careers/list` endpoint returns structured JSON data, eliminating the need for HTML parsing. This is more reliable and less likely to break.

2. **Created data models** (`src/models.py`):
   - `Job` dataclass with fields: title, url, external_id, company_name, category, location, employment_type, is_entry_level
   - `Company` dataclass for future database integration

3. **Built BambooHR scraper** (`src/scrapers.py`):
   - `BambooHRScraper` class that fetches from `/careers/list` endpoint
   - Rate limiting (1 request/second) to respect the site
   - Polite User-Agent header identifying the crawler
   - Location parsing from multiple possible fields
   - Entry-level detection via keyword matching

4. **Implemented entry-level keyword detection**:
   - Keywords: "new grad", "junior", "associate", "entry level", "analyst i", "intern", etc.
   - Case-insensitive matching
   - Checks both job title and department

5. **Created CLI tool** (`src/main.py`):
   - Runs crawler and prints formatted output
   - `--entry-level-only` flag to filter results
   - `--url` flag to test custom career pages

6. **Wrote comprehensive unit tests** (20 tests, all passing):
   - Scraper initialization tests
   - Entry-level detection tests
   - Location parsing tests
   - API response parsing tests
   - Job model tests

**Test Results**:
```
$ python -m pytest tests/ -v
========================= 20 passed in 0.08s =========================
```

**Live Test Output**:
```
Fetching jobs from d1g1t...
============================================================
  D1G1T - 2 job(s) found
============================================================
  OTHER ROLES (2):
  - Senior Director - Channel Sales | Sales, US
  - Senior Sales Executive | Sales | United States

  Total jobs found: 2
  Entry-level jobs: 0
```

**Key Technical Decisions**:
- Used `requests` library instead of `aiohttp` for simplicity (can upgrade later if needed)
- Used dataclasses instead of Pydantic for lightweight models
- Factory pattern (`create_scraper()`) to support multiple platforms in the future

#### Phase 1 Completed

---

#### Phase 2 Started: Database Integration

**Objective**: Persist jobs to PostgreSQL with deduplication and automatic cleanup

**User Stories Being Addressed**:
- **US-01**: *"As a job seeker, I want the system to automatically check career pages daily"* - Database enables tracking what's new vs. already seen
- **US-05**: *"As a job seeker, I want jobs older than 7 days to be automatically removed"* - Cleanup job implementation

**Pain Points Being Solved**:
- **Missing time-sensitive postings**: Database tracks `first_seen_at` to identify new jobs within 24 hours
- **Information overload**: 7-day retention keeps the list focused on recent, relevant postings

**Technical Approach**:
- PostgreSQL for reliability and scalability
- Repository pattern for clean separation of concerns
- Upsert logic for deduplication (avoid duplicate job entries)
- Scheduled cleanup for 7-day retention

**Progress**:

1. **Docker-based PostgreSQL setup**:
   - Created `docker-compose.yml` for local development
   - PostgreSQL 15 running on port 5434
   - Auto-initialization with schema on first run

2. **Database schema** (`scraper/sql/001_init.sql`):
   - `companies` table: tracks career pages to crawl
   - `jobs` table: stores job postings with deduplication
   - Unique constraint on `(company_id, external_id)` prevents duplicates
   - `first_seen_at` timestamp for "new job" detection
   - Auto-updating `updated_at` triggers
   - Seed data includes d1g1t company

3. **Configuration layer** (`src/config.py`):
   - Environment-based configuration
   - Supports both individual vars and DATABASE_URL format
   - `.env.example` template provided

4. **Database layer** (`src/database.py`):
   - `Database` class: connection manager with context manager support
   - `CompanyRepository`: CRUD for companies
   - `JobRepository`: CRUD for jobs with upsert (deduplication) logic
   - `get_new_jobs()`: finds jobs from last 24 hours
   - `delete_old_jobs()`: removes jobs older than N days

5. **Cleanup job** (`src/cleanup.py`):
   - CLI tool for removing old jobs
   - `--dry-run` flag for safe testing
   - Configurable retention period (default: 7 days)

6. **Updated main crawler** (`src/main.py`):
   - Now reads companies from database
   - Saves jobs with deduplication
   - Reports new vs. existing jobs
   - `--no-save` flag for dry-run mode

7. **Integration tests** (12 new tests, 32 total):
   - Database connection tests
   - Company repository tests
   - Job repository tests (upsert, deduplication, cleanup)

**Test Results**:
```
$ python -m pytest tests/ -v
========================= 32 passed in 1.74s =========================
```

**Live Test Output**:
```
# First run - jobs added to database:
  D1G1T - 2 job(s) found
  NEW: 2 job(s) added to database

# Second run - deduplication works:
  D1G1T - 2 job(s) found
  New jobs added: 0
```

**Database Verification**:
```sql
SELECT title, category, first_seen_at FROM jobs;
              title              | category  |         first_seen_at         
---------------------------------+-----------+-------------------------------
 Senior Sales Executive          | Sales     | 2026-01-19 21:08:34.232186+00
 Senior Director - Channel Sales | Sales, US | 2026-01-19 21:08:33.821375+00
```

**Key Technical Decisions**:
- Used Docker Compose for reproducible local development
- Repository pattern for testable data access
- Upsert pattern for idempotent job insertion
- Timestamps with timezone for proper date handling

#### Phase 2 Completed

---

#### Phase 3 Started: Web UI MVP

**Objective**: Build a simple web interface to browse, sort, and filter jobs.

**User Stories Being Addressed**:
- **US-04**: *"As a job seeker, I want to view all jobs on a web page sorted by date, company, or category"*

**Technical Approach**:
- **Next.js App Router**: Modern React framework for server-side rendering and API routes.
- **PostgreSQL Connection**: Used `pg` pool in Next.js to connect to the same Docker database.
- **Client-Side Filtering**: Simple state-based filtering for the MVP (fetching filtered data from API).
- **Tailwind CSS**: Rapid UI development with clean, dark-mode compatible styles.

**Progress**:

1. **Environment Setup**:
   - Configured `.env.local` for Next.js to connect to `localhost:5434`.
   - Installed `pg` driver and utility libraries (`date-fns`, `clsx`).

2. **Backend (API Routes)**:
   - Created `src/lib/db.ts`: Singleton database connection pool.
   - Created `src/app/api/jobs/route.ts`:
     - GET endpoint supporting query parameters: `entryLevel=true`, `company=...`, `sort=date|company`.
     - Secure parameterized SQL queries to prevent injection.

3. **Frontend Components**:
   - `JobCard.tsx`: Reusable component displaying job details, "Entry Level" badge, relative time (e.g., "2 hours ago"), and direct apply link.
   - `page.tsx`: Main dashboard with:
     - Header with filters (Entry Level checkbox, Sort dropdown).
     - Loading state skeleton.
     - Grid layout for job cards.

4. **Styling**:
   - Implemented a clean, minimalist design using Tailwind CSS.
   - Added Dark Mode support (automatic based on system preference).

**Test Results**:
- API Endpoint (`curl http://localhost:3001/api/jobs`) returns JSON data correctly.
- Database connection verification script confirmed access to the 2 existing jobs.

#### Phase 3 Completed
