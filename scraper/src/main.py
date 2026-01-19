"""
Job Crawler - Main Entry Point

This is the main script that runs the job crawler.
Phase 2: Now integrates with PostgreSQL database for persistence.
"""

import argparse
import sys
from datetime import datetime

from .scrapers import create_scraper
from .models import Job
from .database import Database, CompanyRepository, JobRepository


def print_job_summary(jobs: list[Job], company_name: str, new_count: int = 0) -> None:
    """Print a formatted summary of jobs found."""
    print(f"\n{'='*60}")
    print(f"  {company_name.upper()} - {len(jobs)} job(s) found")
    if new_count > 0:
        print(f"  NEW: {new_count} job(s) added to database")
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
    entry_level_only: bool = False,
    save_to_db: bool = True,
    verbose: bool = True,
) -> tuple[list[Job], int]:
    """
    Run the job crawler for all active companies in the database.
    
    Args:
        entry_level_only: If True, only return entry-level jobs
        save_to_db: If True, save jobs to database (default True)
        verbose: If True, print progress to console
        
    Returns:
        Tuple of (all_jobs, new_job_count)
    """
    all_jobs: list[Job] = []
    total_new = 0
    
    with Database() as db:
        company_repo = CompanyRepository(db)
        job_repo = JobRepository(db)
        
        companies = company_repo.get_all_active()
        
        if not companies:
            if verbose:
                print("  No active companies to crawl. Add companies to the database first.")
            return [], 0
        
        for company in companies:
            if verbose:
                print(f"\nFetching jobs from {company.name}...")
            
            try:
                scraper = create_scraper(company.careers_url)
                
                if entry_level_only:
                    jobs = scraper.fetch_entry_level_jobs()
                else:
                    jobs = scraper.fetch_jobs()
                
                new_count = 0
                if save_to_db and company.id is not None:
                    for job in jobs:
                        _, is_new = job_repo.upsert(job, company.id)
                        if is_new:
                            new_count += 1
                    
                    # Update last_crawled_at
                    company_repo.update_last_crawled(company.id)
                
                all_jobs.extend(jobs)
                total_new += new_count
                
                if verbose:
                    print_job_summary(jobs, company.name, new_count)
                    
            except Exception as e:
                print(f"ERROR: Failed to fetch jobs from {company.name}: {e}", file=sys.stderr)
    
    return all_jobs, total_new


def run_crawler_for_url(
    url: str,
    entry_level_only: bool = False,
    verbose: bool = True,
) -> list[Job]:
    """
    Run the job crawler for a single URL (without database).
    
    Args:
        url: The careers page URL to crawl
        entry_level_only: If True, only return entry-level jobs
        verbose: If True, print progress to console
        
    Returns:
        List of jobs found
    """
    if verbose:
        print(f"\nFetching jobs from {url}...")
    
    try:
        scraper = create_scraper(url)
        
        if entry_level_only:
            jobs = scraper.fetch_entry_level_jobs()
        else:
            jobs = scraper.fetch_jobs()
        
        if verbose:
            print_job_summary(jobs, "custom")
        
        return jobs
        
    except Exception as e:
        print(f"ERROR: Failed to fetch jobs: {e}", file=sys.stderr)
        return []


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
        help="Crawl a specific careers page URL (bypasses database)",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save jobs to database (dry run)",
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
        # Single URL mode (no database)
        jobs = run_crawler_for_url(
            url=args.url,
            entry_level_only=args.entry_level_only,
            verbose=not args.quiet,
        )
        new_count = 0
    else:
        # Database mode
        jobs, new_count = run_crawler(
            entry_level_only=args.entry_level_only,
            save_to_db=not args.no_save,
            verbose=not args.quiet,
        )
    
    # Summary
    entry_level_count = sum(1 for j in jobs if j.is_entry_level)
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    print(f"  Total jobs found: {len(jobs)}")
    print(f"  Entry-level jobs: {entry_level_count}")
    if not args.url:
        print(f"  New jobs added:   {new_count}")
    print(f"{'='*60}\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
