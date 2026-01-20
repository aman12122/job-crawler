# 🔐 Handover Protocol & Access Instructions

**Target Audience**: AI Agents & Developers maintaining the Job Crawler.
**Purpose**: Centralized reference for access, secrets, and operations.

---

## 1. Infrastructure Access (Google Cloud)

The system runs on a single **e2-micro VM** in Google Cloud Platform (GCP).

### Prerequisites
*   GCP Project ID: `job-crawler-8d8065` (Check `.gcp_project_id` file if unsure)
*   Zone: `us-east1-b`
*   VM Name: `job-crawler-vm`

### 🔑 SSH Access
To access the server shell:
```bash
PROJECT_ID=$(cat .gcp_project_id)
gcloud compute ssh job-crawler-vm --project=$PROJECT_ID --zone=us-east1-b
```

### 📦 Docker Registry Access
Images are stored in Google Container Registry (GCR) / Artifact Registry.
*   **Pushing Images**:
    ```bash
    gcloud auth configure-docker
    docker push gcr.io/$PROJECT_ID/job-crawler-web:latest
    ```
*   **VM Pull Access**: The VM's service account already has `Artifact Registry Reader` permissions.

---

## 2. Secrets & Configuration

### Local Environment
*   **Version A**: `Version-A/web/.env.local` and `Version-A/scraper/.env` (Created from `.env.example`).

### Production Environment (On VM)
The secrets are stored in the `~/job-crawler/.env` file on the VM.

**To View/Edit Production Secrets:**
```bash
gcloud compute ssh job-crawler-vm --zone=us-east1-b --command="cat ~/job-crawler/.env"
```

**Required Variables:**
```env
DATABASE_PASSWORD=...  # The postgres password
```

**API Keys (Version B Preparation):**
*   **Gemini API Key**: Will need to be added to `~/job-crawler/.env` as `GEMINI_API_KEY=...` once obtained.

---

## 3. Database Maintenance

The database runs in a Docker container named `job-crawler-db`.

**Connect via CLI (on VM):**
```bash
# SSH into VM first
sudo docker compose -f docker-compose.prod.yml exec db psql -U jobcrawler -d job_crawler
```

**Useful Queries:**
*   `\dt` - List tables
*   `SELECT count(*) FROM jobs;` - Check job count

---

## 4. Disaster Recovery / Recreation

If the VM is deleted or corrupted, follow these exact steps to restore:

1.  **Create VM**: Follow `docs/deployment.md` "Step 1: Create the Free VM".
2.  **Bootstrap**:
    ```bash
    # Run the setup script to install Docker/Git
    curl -fsSL https://raw.githubusercontent.com/aman12122/job-crawler/main/docs/vm-setup.sh | bash
    ```
3.  **Restore Secrets**:
    *   Manually create `.env` file on the VM.
    *   Upload `credentials.json` (Gmail) if you have one.
4.  **Deploy**:
    ```bash
    git clone https://github.com/aman12122/job-crawler.git
    cd job-crawler
    # For Version A (current):
    sudo docker compose -f docker-compose.gcr.yml up -d
    ```

---

## 5. Version B Development Handoff

The codebase has been restructured.
*   **Legacy Code**: `Version-A/`
*   **New Code**: `Version-B/`

**Agent Instructions for Version B:**
1.  Read `Version-B/ROADMAP.md` first.
2.  Do NOT modify `Version-A` unless fixing a critical bug in production.
3.  Build new features in `Version-B`.
4.  When ready to deploy V-B:
    *   Update `docker-compose.prod.yml` to point to V-B Dockerfiles.
    *   Run migration scripts to create `v2_` tables.
