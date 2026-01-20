#!/bin/bash
set -e

# Configuration
VERSION_A_DIR="../Version-A"
VERSION_B_DIR="."
ENV_FILE="scraper/.env"

echo "🚀 Starting Deployment of Job Crawler V2..."

# 1. Check Prerequisites
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Error: $ENV_FILE not found. Please create it from .env.example"
    exit 1
fi

echo "📋 Checking environment variables..."
if ! grep -q "GEMINI_API_KEY" "$ENV_FILE"; then
    echo "❌ Error: GEMINI_API_KEY missing in $ENV_FILE"
    exit 1
fi

# 2. Stop Version A (if running)
if [ -d "$VERSION_A_DIR" ]; then
    echo "🛑 Stopping Version A containers..."
    cd "$VERSION_A_DIR"
    # Try to stop both possible compose filenames
    docker compose -f docker-compose.prod.yml down || docker compose down || true
    cd - > /dev/null
else
    echo "ℹ️ Version A directory not found, skipping stop."
fi

# 3. Build & Start Version B
echo "🏗️ Building Version B containers..."
docker compose -f docker-compose.prod.yml build

echo "🚀 Starting Version B..."
docker compose -f docker-compose.prod.yml up -d

# 4. Initialize Database Schema
echo "💾 Initializing Database Schema..."
# Wait for DB to be ready
sleep 10
docker compose -f docker-compose.prod.yml exec -T db psql -U jobcrawler -d job_crawler -f /docker-entrypoint-initdb.d/001_v2_init.sql || echo "⚠️ Schema might already exist (ignoring error)"

echo "✅ Deployment Complete!"
echo "   Web: http://localhost:80"
echo "   Scraper logs: docker logs -f job-crawler-scraper-v2"
