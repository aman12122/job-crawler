# Job Crawler

A tool to track new grad and associate-level job postings from specific company career pages.

## Overview

Job Crawler automatically monitors career pages from your target companies, identifies new grad/associate roles (0-3 years experience), and sends you daily email digests with new postings.

## Project Structure

```
job-crawler/
├── scraper/          # Python web scraper
│   ├── src/          # Source code
│   ├── tests/        # Test files
│   └── pyproject.toml
├── web/              # Next.js frontend
│   ├── src/          # Source code
│   └── package.json
├── ROADMAP.md        # Project roadmap and documentation
└── README.md         # This file
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- GCP account (for deployment)

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/aman12122/job-crawler.git
cd job-crawler
```

### 2. Set up the scraper

```bash
cd scraper
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 3. Set up the web app

```bash
cd web
npm install
npm run dev
```

The web app will be available at http://localhost:3000

## Development

### Scraper

```bash
cd scraper
source .venv/bin/activate

# Run tests
pytest

# Lint code
ruff check src/

# Type check
mypy src/
```

### Web App

```bash
cd web

# Run development server
npm run dev

# Build for production
npm run build

# Run linting
npm run lint
```

## Documentation

See [ROADMAP.md](./ROADMAP.md) for the full project roadmap, technical architecture, and development log.

## License

MIT
