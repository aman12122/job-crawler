# Technical Specifications (Version B)

## 🏗 System Architecture

### 1. The "Funnel" Architecture
To balance Cost vs. Quality, Version B uses a funnel approach:

1.  **Broad Scrape** (Low Cost): Fetch all job titles/links via Pagination.
2.  **Heuristic Pre-Filter** (Zero Cost): Discard obvious "Senior", "Principal", "Staff" roles based on title keywords.
3.  **Detail Fetch** (Bandwidth Cost): Download full HTML description for survivors.
4.  **AI Analysis** (API Cost): Send text to Gemini Flash for final classification.

### 2. Database Schema (New `v2` Tables)

```sql
-- v2_companies (Shared logic with v1, but separate for clean break)
CREATE TABLE v2_companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    careers_url TEXT NOT NULL UNIQUE,
    strategy VARCHAR(50) DEFAULT 'bamboohr', -- 'bamboohr', 'greenhouse', 'custom_selenium'
    last_crawled_at TIMESTAMP
);

-- v2_jobs (Enhanced Data)
CREATE TABLE v2_jobs (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES v2_companies(id),
    external_id VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    url TEXT NOT NULL,
    
    -- Analysis Data
    is_analyzed BOOLEAN DEFAULT FALSE,
    ai_is_entry_level BOOLEAN,
    ai_confidence_score INTEGER, -- 0-100
    ai_reasoning TEXT,           -- "Rejected: Requires 5 years Java"
    years_experience_required INTEGER,
    
    -- Raw Data (for debugging/re-analysis)
    raw_description_text TEXT,
    
    first_seen_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(company_id, external_id)
);
```

---

## 🧠 AI Engine Specification

### Model
*   **Provider**: Google Gemini API
*   **Model**: `gemini-1.5-flash` (Free Tier eligible)
*   **Rate Limit**: 15 Requests Per Minute (RPM)

### The Prompt
> **Context**: You are a strict recruiter filtering jobs for a New Graduate (0-2 years experience).
> **Input**: Job Description Text
> **Task**: Extract requirements and determine eligibility.
> **Constraint**: 
> - "Preferred" skills are NOT requirements.
> - "3+ years" is REJECT. "0-3 years" is ACCEPT.
> - Masters/PhD requirements are REJECT (unless generic).
> 
> **Output JSON**:
> ```json
> {
>   "is_entry_level": boolean,
>   "confidence": int, // 0-100
>   "min_years_experience": int, // 0 if none stated
>   "reasoning": "string (max 100 chars)"
> }
> ```

---

## 🕷 Scraper Service Design

### Class Hierarchy
1.  **`BaseScraper`**: Abstract base class.
    *   `fetch_page(page_num)`
    *   `parse_jobs(html)` -> `List[JobStub]`
    *   `fetch_detail(url)` -> `full_text`
    *   `has_next_page()` -> `bool`

2.  **`PaginationStrategy`**:
    *   `OffsetStrategy` (API based: `?offset=20`)
    *   `TokenStrategy` (API based: `?next=token123`)
    *   `LinkStrategy` (HTML based: Find "Next >" <a> tag)

### Async Implementation
Use `asyncio` and `aiohttp`.
*   **Worker Queue**: 
    *   Queue 1: Page Fetching (Fast, high concurrency)
    *   Queue 2: Detail Fetching (Medium concurrency)
    *   Queue 3: AI Analysis (Strict rate limit: 1 worker, 4s delay)

---

## 🔌 API Contracts (Internal)

### `POST /api/v2/crawl`
Trigger a crawl.
*   **Body**: `{ "company_id": 1, "deep": true }`
*   **Response**: `{ "job_id": "uuid", "status": "queued" }`

### `GET /api/v2/jobs`
Get rich job data.
*   **Response**:
    ```json
    [
      {
        "title": "Software Engineer I",
        "ai_reasoning": "Matches 0-2 years requirement",
        "confidence": 95,
        "tags": ["Entry Level", "Python"]
      }
    ]
    ```
