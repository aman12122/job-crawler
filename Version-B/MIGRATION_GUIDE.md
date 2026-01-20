# Migration Guide (Version A -> Version B)

## 🔄 Transition Philosophy
We are **replacing** the engine but **keeping** the chassis. The VM, Docker, and PostgreSQL instance remain. The code inside the containers changes completely.

## 📦 Data Migration
*   **Strategy**: "Fresh Start".
*   **Reason**: Version A data is "dumb" (keyword based). Version B data is "smart" (AI based). Mixing them would confuse the user ("Why does this job have reasoning but that one doesn't?").
*   **Action**: Create `v2_` tables. Keep `v1` tables for archival/reference until V-B is stable.

## 🛠 Infrastructure Updates

### Docker Compose
*   **Version A**: `job-crawler-scraper` container ran `src/server.py` (simple loop).
*   **Version B**: `job-crawler-scraper-v2` will run a complex `asyncio` loop with a Redis queue (optional) or internal queue.
*   **Action**: Update `docker-compose.prod.yml` to point to the new Version B Dockerfile.

### Deployment Process
1.  **Stop V1**: `docker compose stop scraper web`
2.  **Migrate DB**: Run V2 SQL init scripts manually or via entrypoint.
3.  **Deploy V2**: `docker compose up -d` (pulling V2 images).

## ⚠️ Breaking Changes
*   **Scraper Config**: The configuration format for companies might change to support pagination strategies.
    *   *V1*: `{"url": "..."}`
    *   *V2*: `{"url": "...", "strategy": "greenhouse", "pagination": "offset"}`
*   **API Response**: The frontend API response format will change to include `ai_reasoning`. The Frontend MUST be updated simultaneously.
