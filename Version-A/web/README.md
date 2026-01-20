# Job Crawler - Web UI

The frontend interface for the Job Crawler project. Built with Next.js 14, TypeScript, and Tailwind CSS.

## Features

- **Job Dashboard**: View all tracked jobs in a responsive grid layout
- **Filtering**: Filter by "Entry Level" only
- **Sorting**: Sort by date posted or company name
- **Dark Mode**: Automatic support based on system preference
- **Direct Apply**: Clickable links to original career pages

## Prerequisites

- Node.js 18+
- PostgreSQL database (running via Docker from the root directory)

## Setup

1. **Install dependencies**:

```bash
npm install
```

2. **Configure environment**:

```bash
cp .env.example .env.local
```

Adjust the database credentials in `.env.local` if you changed them in the Docker configuration. Default is port `5434`.

## Development

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser.

## Project Structure

```
src/
├── app/
│   ├── api/jobs/    # API endpoint for fetching jobs
│   ├── globals.css  # Global styles and Tailwind imports
│   ├── layout.tsx   # Root layout and metadata
│   └── page.tsx     # Main dashboard page
├── components/
│   └── JobCard.tsx  # Job listing component
└── lib/
    └── db.ts        # Database connection pool
```

## API Routes

### `GET /api/jobs`

Returns a list of jobs.

**Query Parameters:**
- `entryLevel` (boolean): Set to `true` to show only entry-level jobs
- `company` (string): Filter by company name (partial match)
- `sort` (string): `date` (default) or `company`
