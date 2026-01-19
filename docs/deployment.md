# Deployment Guide: Google Cloud Platform (GCP)

This guide outlines how to move the Job Crawler from local Docker Compose to a production Google Cloud environment.

## Architecture

- **Web App**: Cloud Run Service (always available, scales to zero)
- **Scraper**: Cloud Run Job (triggered on schedule)
- **Database**: Cloud SQL for PostgreSQL
- **Scheduler**: Cloud Scheduler (cron trigger)

## Prerequisites

1.  Google Cloud Project created
2.  `gcloud` CLI installed and authenticated
3.  Billing enabled (required for Cloud Build/Run, though free tier covers most usage)

## Step 1: Set up Cloud SQL (Database)

1.  **Create Instance**:
    ```bash
    gcloud sql instances create job-crawler-db \
        --database-version=POSTGRES_15 \
        --tier=db-f1-micro \
        --region=us-east1
    ```

2.  **Create Database & User**:
    ```bash
    gcloud sql databases create job_crawler --instance=job-crawler-db
    gcloud sql users create jobcrawler --instance=job-crawler-db --password=YOUR_SECURE_PASSWORD
    ```

3.  **Get Connection Name**:
    ```bash
    gcloud sql instances describe job-crawler-db --format='value(connectionName)'
    # Output example: project-id:us-east1:job-crawler-db
    ```

## Step 2: Deploy Web App

1.  **Build & Push Image**:
    ```bash
    gcloud builds submit ./web --tag gcr.io/YOUR_PROJECT_ID/job-crawler-web
    ```

2.  **Deploy to Cloud Run**:
    ```bash
    gcloud run deploy job-crawler-web \
        --image gcr.io/YOUR_PROJECT_ID/job-crawler-web \
        --region us-east1 \
        --allow-unauthenticated \
        --set-env-vars="DATABASE_USER=jobcrawler,DATABASE_PASSWORD=YOUR_SECURE_PASSWORD,DATABASE_NAME=job_crawler" \
        --add-cloudsql-instances=YOUR_CONNECTION_NAME
    ```

    *Note: Cloud Run automatically handles the Unix socket connection to Cloud SQL.*

## Step 3: Deploy Scraper Job

1.  **Build & Push Image**:
    ```bash
    gcloud builds submit ./scraper --tag gcr.io/YOUR_PROJECT_ID/job-crawler-scraper
    ```

2.  **Create Cloud Run Job**:
    ```bash
    gcloud run jobs create job-crawler-scraper \
        --image gcr.io/YOUR_PROJECT_ID/job-crawler-scraper \
        --region us-east1 \
        --set-env-vars="DATABASE_USER=jobcrawler,DATABASE_PASSWORD=YOUR_SECURE_PASSWORD,DATABASE_NAME=job_crawler,DATABASE_HOST=/cloudsql/YOUR_CONNECTION_NAME" \
        --add-cloudsql-instances=YOUR_CONNECTION_NAME \
        --command="python,-m,src.main"
    ```

## Step 4: Schedule the Scraper

1.  **Create Scheduler Job**:
    ```bash
    gcloud scheduler jobs create http daily-crawl \
        --location=us-east1 \
        --schedule="0 12 * * *" \
        --uri="https://us-east1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/YOUR_PROJECT_ID/jobs/job-crawler-scraper:run" \
        --http-method=POST \
        --oauth-service-account-email=YOUR_SA_EMAIL
    ```

## Step 5: Email Setup

1.  Upload your `credentials.json` (Gmail API) to Secret Manager.
2.  Mount the secret in the Scraper Cloud Run Job so it can send emails securely.

## Cost Estimation (Free Tier candidates)

- **Cloud Run**: First 180,000 vCPU-seconds free per month.
- **Cloud SQL**: `db-f1-micro` is NOT free (approx $7-10/mo). 
  - *Alternative*: Run Postgres in a VM (Compute Engine e2-micro) which IS free tier eligible, but requires more manual setup.
