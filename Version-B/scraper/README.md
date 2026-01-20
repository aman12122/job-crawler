# Job Crawler Scraper (Version B)

The intelligence engine of the Job Crawler. This service is responsible for discovering jobs, fetching details, and using Google Gemini AI to filter them based on experience requirements.

## 🚀 Setup Guide

### 1. Prerequisites
- Python 3.11+
- PostgreSQL 15+ (or use Docker)
- Google Gemini API Key

### 2. Getting a Gemini API Key (Free)
Version B relies on Google Gemini Flash for AI analysis. The free tier provides 15 requests per minute, which is sufficient for our rate-limited pipeline.

1.  Go to **[Google AI Studio](https://aistudio.google.com/app/apikey)**.
2.  Click **"Create API key"**.
3.  Select a project (or create a new one).
4.  Copy the generated API key.
5.  Paste it into your `.env` file (see below).

### 3. Configuration
Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and fill in your details:
```ini
DATABASE_PASSWORD=your_db_password
GEMINI_API_KEY=your_api_key_starts_with_AIza...
```

### 4. Installation
This project uses `pip` and `venv`:

```bash
# Create virtual environment
python -m venv .venv

# Activate it
source .venv/bin/activate  # Mac/Linux
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -e .
```

### 5. Running Locally
To run the scraper manually (after setting up the database):

```bash
job-crawler
# OR
python -m src.main
```

## 🏗 Architecture

- **`src/config.py`**: Pydantic-based configuration.
- **`src/database.py`**: Async PostgreSQL connection pooling.
- **`sql/`**: Database initialization scripts.
