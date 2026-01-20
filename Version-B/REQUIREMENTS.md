# Requirements (Version B)

## 🎯 Functional Requirements

### FR-01: Pagination Handling
*   The system MUST follow pagination links (e.g., "Page 2", "Next", or offset params) to retrieve **100% of open jobs**.
*   The system MUST support at least 2 pagination methods:
    1.  **Offset-based** (e.g., `?start=20`)
    2.  **Token-based** (e.g., `?token=NEXT_PAGE_TOKEN`)

### FR-02: Detail Scraping
*   The system MUST fetch the full HTML description of a job if the list view provides a link.
*   The system MUST strip HTML tags to produce clean text for the AI.

### FR-03: AI Analysis
*   The system MUST use **Google Gemini 1.5 Flash** (via API) to analyze job text.
*   The system MUST output:
    *   `Is Entry Level?` (Yes/No)
    *   `Years Required` (Integer)
    *   `Confidence` (Score)
    *   `Reasoning` (Short text)

### FR-04: Rate Limiting
*   The system MUST NOT exceed **15 requests per minute** to the Gemini API.
*   The system MUST implement a queue to handle bursts of jobs (e.g., finding 100 jobs at once but processing them over 7 minutes).

---

## 🛑 Non-Functional Requirements

### NFR-01: Cost Zero
*   The system MUST run on the existing `e2-micro` VM (1GB RAM).
*   The system MUST NOT use paid cloud services (no Cloud Tasks, no paid DBs). **In-memory queues** are preferred over Redis to save RAM.

### NFR-02: Resilience
*   The system MUST handle network failures during a 50-page crawl (e.g., retry logic).
*   If the AI API fails (quota exceeded), the system MUST mark the job as "Pending Analysis" and retry later, OR fallback to keyword matching.

### NFR-03: Performance
*   Broad crawling (finding links) should be fast (async).
*   AI analysis can be slow (background).
