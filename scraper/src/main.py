"""
Job Crawler - Main Entry Point

This is the main script that runs the job crawler.
For Phase 1 MVP, it fetches jobs and prints them to the console.
"""

import argparse
import sys
from datetime import datetime

from .scrapers import create_scraper, BambooHRScraper
from .models import Job


# Default companies to track (can be extended via config file later)
DEFAULT_COMPANIES = [
    {
        "name": "d1g1t",
        "careers_url": "https://d1g1t.bamboohr.com/careers",
        "platform": "bamboohr",
    },
]


def print_job_summary(jobs: list[Job], company_name: str) -> None:
    """Print a formatted summary of jobs found."""
    print(f"\n{'='*60}")
    print(f"  {company_name.upper()} - {len(jobs)} job(s) found")
    print(f"{'='*60}\n")
    
    if not jobs:
        print("  No jobs found.\n")
        return
    
    entry_level_jobs = [j for j in jobs if j.is_entry_level]
    other_jobs = [j for j in jobs if not j.is_entry_level]
    
    if entry_level_jobs:
        print(f"  ENTRY-LEVEL / NEW GRAD ROLES ({len(entry_level_jobs)}):")
        print(f"  {'-'*40}")
        for job in entry_level_jobs:
            location = f" | {job.location}" if job.location else ""
            category = f" | {job.category}" if job.category else ""
            print(f"  * {job.title}{category}{location}")
            print(f"    {job.url}")
            print()
    
    if other_jobs:
        print(f"  OTHER ROLES ({len(other_jobs)}):")
        print(f"  {'-'*40}")
        for job in other_jobs:
            location = f" | {job.location}" if job.location else ""
            category = f" | {job.category}" if job.category else ""
            print(f"  - {job.title}{category}{location}")
            print(f"    {job.url}")
            print()


def run_crawler(
    companies: list[dict] | None = None,
    entry_level_only: bool = False,
    verbose: bool = True,
) -> list[Job]:
    """
    Run the job crawler for all configured companies.
    
    Args:
        companies: List of company configs. Uses DEFAULT_COMPANIES if None.
        entry_level_only: If True, only return entry-level jobs
        verbose: If True, print progress to console
        
    Returns:
        List of all jobs found
    """
    if companies is None:
        companies = DEFAULT_COMPANIES
    
    all_jobs: list[Job] = []
    
    for company in companies:
        name = company["name"]
        url = company["careers_url"]
        
        if verbose:
            print(f"\nFetching jobs from {name}...")
        
        try:
            scraper = create_scraper(url)
            
            if entry_level_only:
                jobs = scraper.fetch_entry_level_jobs()
            else:
                jobs = scraper.fetch_jobs()
            
            all_jobs.extend(jobs)
            
            if verbose:
                print_job_summary(jobs, name)
                
        except Exception as e:
            print(f"ERROR: Failed to fetch jobs from {name}: {e}", file=sys.stderr)
    
    return all_jobs


def main() -> int:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Job Crawler - Track new grad/associate job postings"
    )
    parser.add_argument(
        "--entry-level-only",
        action="store_true",
        help="Only show entry-level / new grad positions",
    )
    parser.add_argument(
        "--url",
        type=str,
        help="Crawl a specific careers page URL instead of defaults",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress verbose output",
    )
    
    args = parser.parse_args()
    
    print(f"\n{'#'*60}")
    print(f"  JOB CRAWLER - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*60}")
    
    if args.url:
        # Single URL mode
        companies = [{"name": "custom", "careers_url": args.url, "platform": "unknown"}]
    else:
        companies = None  # Use defaults
    
    jobs = run_crawler(
        companies=companies,
        entry_level_only=args.entry_level_only,
        verbose=not args.quiet,
    )
    
    # Summary
    entry_level_count = sum(1 for j in jobs if j.is_entry_level)
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    print(f"  Total jobs found: {len(jobs)}")
    print(f"  Entry-level jobs: {entry_level_count}")
    print(f"{'='*60}\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
