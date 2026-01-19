# Zero Cost Deployment Guide: Google Cloud Platform

This guide details how to deploy the Job Crawler on Google Cloud Platform's **Always Free Tier**.

We will use a single **Compute Engine e2-micro instance** to host the Database, Web App, and Scraper. This architecture incurs **$0 cost** if you stay within the free tier limits.

## Architecture

- **Infrastructure**: 1x `e2-micro` VM (2 vCPUs, 1GB RAM)
- **Region**: `us-east1`, `us-west1`, or `us-central1` (Required for free tier)
- **Storage**: 30GB Standard Persistent Disk
- **Orchestration**: Docker Compose

## Prerequisites

1.  Google Cloud Account
2.  `gcloud` CLI installed locally
3.  Project Billing Account linked (no charges will occur, but required for activation)

## Step 1: Create the Free VM

Run this command to create the instance eligible for the free tier:

```bash
gcloud compute instances create job-crawler-vm \
    --project=YOUR_PROJECT_ID \
    --zone=us-east1-b \
    --machine-type=e2-micro \
    --network-tier=STANDARD \
    --image-family=debian-12 \
    --image-project=debian-cloud \
    --boot-disk-size=30GB \
    --boot-disk-type=pd-standard \
    --tags=http-server
```

*Note: `network-tier=STANDARD` and `pd-standard` are important for cost optimization.*

## Step 2: Configure Firewall

Allow HTTP traffic to access the web dashboard:

```bash
gcloud compute firewall-rules create allow-http-job-crawler \
    --allow tcp:80 \
    --target-tags http-server
```

## Step 3: Setup the Server

1.  **SSH into the VM**:
    ```bash
    gcloud compute ssh job-crawler-vm
    ```

2.  **Install Docker & Git** (using our helper script):
    ```bash
    # Copy script content or curl it if you hosted it
    curl -fsSL https://raw.githubusercontent.com/aman12122/job-crawler/main/docs/vm-setup.sh | bash
    ```

3.  **Clone the Repository**:
    ```bash
    git clone https://github.com/aman12122/job-crawler.git
    cd job-crawler
    ```

4.  **Configure Environment**:
    Create a `.env` file for production secrets:
    ```bash
    nano .env
    ```
    Add:
    ```
    DATABASE_PASSWORD=super_secure_password_123
    ```

5.  **Setup Email Credentials**:
    Upload your `credentials.json` (Gmail API) to the server:
    ```bash
    # From your local machine
    gcloud compute scp ./scraper/credentials.json job-crawler-vm:~/job-crawler/scraper/
    ```

## Step 4: Start the Application

Run the production Docker Compose configuration:

```bash
sudo docker compose -f docker-compose.prod.yml up -d --build
```

The web dashboard should now be accessible at `http://YOUR_VM_EXTERNAL_IP`.

## Step 5: Schedule the Scraper

To run the scraper daily at 12 PM, we'll use the VM's system cron.

1.  Open crontab:
    ```bash
    crontab -e
    ```

2.  Add the following line (adjust path as needed):
    ```cron
    0 12 * * * cd /home/YOUR_USER/job-crawler && sudo docker compose -f docker-compose.prod.yml run --rm scraper
    ```

## Maintenance

- **View Logs**:
    ```bash
    sudo docker compose -f docker-compose.prod.yml logs -f
    ```
- **Update Application**:
    ```bash
    git pull
    sudo docker compose -f docker-compose.prod.yml up -d --build
    ```
