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

### Phase 2: Database Integration
**Goal**: Persist jobs to PostgreSQL

- [ ] Set up local PostgreSQL for development
- [ ] Implement database schema (companies, jobs tables)
- [ ] Add job deduplication logic (external_id)
- [ ] Create cleanup job for 7-day retention
- [ ] Set up Cloud SQL instance on GCP
- [ ] Test database operations

### Phase 3: Web UI MVP
**Goal**: Display jobs on a web page with sorting

- [ ] Create Next.js API routes for fetching jobs
- [ ] Build job listing page with sorting controls
- [ ] Style with basic CSS (clean, functional)
- [ ] Add clickable links to original postings
- [ ] Test locally with database

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
