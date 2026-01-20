# Job Crawler - Version B Master Plan

> **Objective**: Upgrade the Job Crawler from a simple keyword-based scraper to an intelligent, AI-powered system capable of handling complex career sites with hundreds of listings.

## 1. Transition Strategy (Version A -> Version B)

To preserve the working state of Version A while building Version B:

1.  **Restructure Repository**:
    *   Create a root directory `Version-A/`.
    *   Move `scraper/`, `web/`, `docs/`, `docker-compose*`, and `README.md` (Version A specific) into `Version-A/`.
    *   Create `Version-B/` for the new development.
    *   Create a root `README.md` that links to both versions.

2.  **Infrastructure Transition**:
    *   **Goal**: Replace Version A on the *existing* VM without incurring extra costs.
    *   **Method**: We will stop the Version A Docker containers, update the `docker-compose.prod.yml` to point to Version B images, and restart.
    *   **Database**: We will create a *new* database schema (`job_crawler_b`) within the *same* PostgreSQL container to keep data separate but share resources.

---

## 2. Technical Architecture (Version B)

### Core Improvements

| Feature | Version A (Current) | Version B (New) |
| :--- | :--- | :--- |
| **Filtering** | Keyword Matching (`if "Senior" in title`) | **AI Analysis** (LLM reads description) |
| **Scale** | Single page, simple list | **Pagination** & Detail Page Scraping |
| **Accuracy** | Low (Misses context) | **High** (Understands "3+ years preferred") |
| **Scraping** | Simple JSON/HTML | **Async Pipeline** (Scrape -> Filter -> AI) |

### System Components

1.  **Smart Scraper Service** (`/services/scraper`):
    *   **Pagination Engine**: Automatically follows "Next" buttons or API offsets.
    *   **Pipeline**:
        1.  **Discovery**: Fetch all job titles/links (fast).
        2.  **Pre-Filter**: Discard obvious mismatches (e.g., "Senior", "Principal") using keywords to save AI quota.
        3.  **Detail Fetch**: Download full HTML description for candidates.
        4.  **AI Analysis**: Send text to Google Gemini Flash.
    *   **Rate Limiter**: Strict 15 RPM limit for AI calls (Free Tier constraint).

2.  **Database** (Shared PostgreSQL):
    *   New Schema `v2_jobs`: Stores full job descriptions and AI reasoning ("Why is this entry level?").

3.  **Web Dashboard** (Updated Next.js):
    *   Displays "AI Confidence" score.
    *   Shows the "Reasoning" provided by the AI.

---

## 3. The AI Integration (Google Gemini Flash)

**Why Gemini Flash?**
*   **Cost**: Free tier available (15 requests/minute, 1,500/day).
*   **Performance**: Fast, sufficient for text classification.

**Pipeline Logic:**
```python
async def analyze_job(description: str) -> dict:
    prompt = f"""
    Analyze this job description. 
    Is it suitable for a New Grad or someone with 0-3 years experience?
    Return JSON: {{ "is_entry_level": bool, "reasoning": str, "years_required": int }}
    
    Job: {description[:5000]}
    """
    # Call Gemini API with rate limiting
    return await gemini.generate_content(prompt)
```

---

## 4. Implementation Steps

### Phase 1: Setup & Restructure
- [x] Move Version A files to `Version-A/`.
- [ ] Initialize `Version-B/` structure.
- [ ] Set up `Version-B/docker-compose.yml`.

### Phase 2: Enhanced Scraper Foundation
- [ ] Implement `AsyncScraper` base class (using `aiohttp` for speed).
- [ ] Add **Pagination** support (recursive fetching).
- [ ] Create `DetailFetcher` to get full job descriptions.

### Phase 3: AI Filter Implementation
- [ ] Get Google Gemini API Key.
- [ ] Create `AIFilter` service with rate limiting (Token Bucket algorithm).
- [ ] Integrate AI check into the scraping pipeline.

### Phase 4: Database & UI Updates
- [ ] Update DB schema to store `ai_reasoning` and `full_description`.
- [ ] Update UI to show AI insights.

### Phase 5: Deployment (Replace Ver A)
- [ ] Build Version B Docker images.
- [ ] Stop Version A containers on VM.
- [ ] Deploy Version B to the same VM.

---

## 5. Cost Management Strategy (Crucial)

To maintain **$0 Cost** with AI:
1.  **Aggressive Pre-filtering**: Don't send "Senior Architect" jobs to the AI. Filter them out by title first.
2.  **Rate Limiting**: Hard limit of 1 request per 4 seconds (15/min) to stay in free tier.
3.  **Concurrency**: Use Python `asyncio` to fetch pages fast, but process AI queues slowly.

## 6. Required User Actions
*   [ ] Generate a **Google Gemini API Key** (AI Studio).
*   [ ] Provide the **URL of the complex career site** for testing pagination.
