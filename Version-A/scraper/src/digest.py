"""
Job Crawler - Daily Digest Script

Fetches new jobs found in the last 24 hours and sends an email digest.
"""

import argparse
import sys
from datetime import datetime

from .config import get_config
from .database import Database, JobRepository
from .models import Job
from .notifications import get_notification_service


def send_daily_digest(email: str, hours: int = 24) -> int:
    """
    Find new jobs and send digest.
    
    Args:
        email: Recipient email address
        hours: Lookback window in hours
        
    Returns:
        Number of jobs included in digest
    """
    with Database() as db:
        repo = JobRepository(db)
        new_jobs_data = repo.get_new_jobs(hours=hours)
        
        # Convert dicts back to Job objects for the template
        jobs = []
        for d in new_jobs_data:
            job = Job(
                title=d['title'],
                url=d['url'],
                external_id='', # Not needed for display
                company_name=d['company_name'],
                category=d['category'],
                location=d['location'],
                employment_type=d['employment_type'],
                is_entry_level=d['is_entry_level'],
                first_seen_at=d['first_seen_at']
            )
            jobs.append(job)
            
        if not jobs:
            print(f"No new jobs found in the last {hours} hours.")
            return 0
            
        print(f"Found {len(jobs)} new jobs. Sending email to {email}...")
        
        service = get_notification_service()
        service.send_digest(email, jobs)
        
        return len(jobs)


def main() -> int:
    parser = argparse.ArgumentParser(description="Send daily job digest email")
    parser.add_argument("email", help="Recipient email address")
    parser.add_argument("--hours", type=int, default=24, help="Lookback hours (default: 24)")
    
    args = parser.parse_args()
    
    try:
        count = send_daily_digest(args.email, args.hours)
        print(f"Digest complete. Sent {count} jobs.")
        return 0
    except Exception as e:
        print(f"ERROR: Failed to send digest: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
