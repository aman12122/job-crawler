# Job Crawler

A tool to track new grad and associate-level job postings from specific company career pages.

## Overview

Job Crawler automatically monitors career pages from your target companies, identifies new grad/associate roles (0-3 years experience), and sends you daily email digests with new postings.

## Project Structure

```
job-crawler/
├── scraper/          # Python web scraper & digest sender
├── web/              # Next.js frontend dashboard
├── docker-compose.yml # Full stack local deployment
└── ROADMAP.md        # Project roadmap
```

## Quick Start (MVP)

The easiest way to run the entire system is via Docker Compose.

### 1. Start the System

```bash
docker compose up --build -d
```

This starts:
- **Database** (PostgreSQL) on port `5434` (external) / `5432` (internal)
- **Web Dashboard** on [http://localhost:3000](http://localhost:3000)
- **Scraper** (runs once to fetch initial jobs)

### 2. View the Dashboard

Open **[http://localhost:3000](http://localhost:3000)** in your browser.
You should see the jobs fetched from the test company (d1g1t).

### 3. Run Scraper Manually

To trigger a new crawl:

```bash
docker compose run scraper
```

To send the email digest (requires `credentials.json` for real email, defaults to console output):

```bash
docker compose run scraper python -m src.digest your.email@example.com
```

## Configuration

- **Database**: `scraper/sql/001_init.sql` defines the schema.
- **Companies**: Add more companies to the `companies` table using SQL or by extending the seed data.
- **Email**: To enable real emails, place your `credentials.json` (Gmail API) in `scraper/`.

## Development

See individual READMEs for detailed development instructions:
- [Scraper Documentation](./scraper/README.md)
- [Web UI Documentation](./web/README.md)
- [Full Roadmap](./ROADMAP.md)

## License

MIT
