# User Stories & Pain Points (Version B)

## 🛑 Pain Points (The "Why")

### 1. The "Experience Trap"
**Problem**: Version A uses keyword matching (`"Senior" in title`).
**Reality**: Job titles are misleading.
- *"Junior Developer"* might require "3+ years experience" in the description.
- *"Software Engineer"* (generic) might be an Entry Level role, but Version A might miss it if it lacks specific keywords, or include it when it requires 5 years.
**Impact**: The user wastes time clicking links only to find they are underqualified.

### 2. The "Hidden Jobs" Issue
**Problem**: Version A only scrapes the first page of results (often the first 25-50 jobs).
**Reality**: Large companies (e.g., Google, Microsoft) have hundreds of open roles.
**Impact**: The user misses 80% of available opportunities because they are buried on Page 2+.

### 3. "Black Box" Filtering
**Problem**: When a job is hidden/filtered, the user doesn't know *why*.
**Impact**: Lack of trust in the automation. "Did it miss a job? Or did it filter it?"

---

## 👤 User Stories

### Core Analysis Stories
| ID | Story | Acceptance Criteria |
| :--- | :--- | :--- |
| **US-B1** | As a user, I want the system to read the *full* job description, not just the title, so that filtering is accurate. | System fetches detailed HTML for candidate jobs. |
| **US-B2** | As a user, I want the system to understand "Years of Experience" contextually (e.g., distinguishing "Preferred" vs "Required"). | AI Analysis returns a structured `years_required` integer and `is_strict` boolean. |
| **US-B3** | As a user, I want to see *why* a job was marked as "Entry Level" or "Senior". | UI displays a short "AI Reasoning" snippet (e.g., "Requires 5 years Python"). |

### Scale & Coverage Stories
| ID | Story | Acceptance Criteria |
| :--- | :--- | :--- |
| **US-B4** | As a user, I want the system to find *all* jobs, even if there are 500 listings across 10 pages. | Scraper handles pagination (Next tokens/offsets) automatically. |
| **US-B5** | As a user, I want to track large tech companies (FAANG) which often have complex, non-standard career sites. | Scraper architecture supports "Complex" site profiles with custom pagination logic. |

### Operational Stories
| ID | Story | Acceptance Criteria |
| :--- | :--- | :--- |
| **US-B6** | As a user on a budget, I want the AI to only analyze "promising" leads to save API quota. | System implements a "Pre-Filter" step to discard obvious mismatches before calling AI. |
| **US-B7** | As a user, I want to manually trigger a deep crawl for a specific company when I know they just did a drop. | "Crawl Now" button supports "Full Deep Crawl" mode vs "Quick Update". |
