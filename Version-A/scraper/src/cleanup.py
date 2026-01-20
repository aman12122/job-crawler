"""
Job Crawler - Cleanup Job

Removes jobs older than the configured retention period (default: 7 days).
This script can be run as a cron job or scheduled task.
"""

import argparse
import sys
from datetime import datetime

from .config import get_config
from .database import Database, JobRepository


def cleanup_old_jobs(days: int | None = None, dry_run: bool = False) -> int:
    """
    Remove jobs older than the specified number of days.
    
    Args:
        days: Number of days to retain. Uses config default if None.
        dry_run: If True, only report what would be deleted without actually deleting.
        
    Returns:
        Number of jobs deleted (or would be deleted in dry-run mode)
    """
    config = get_config()
    retention_days = days if days is not None else config.job_retention_days
    
    with Database() as db:
        job_repo = JobRepository(db)
        
        if dry_run:
            # Count jobs that would be deleted
            with db.cursor(commit=False) as cur:
                cur.execute("""
                    SELECT COUNT(*) as count FROM jobs
                    WHERE first_seen_at < NOW() - INTERVAL '%s days'
                """, (retention_days,))
                row = cur.fetchone()
                return row["count"] if row else 0
        else:
            return job_repo.delete_old_jobs(retention_days)


def main() -> int:
    """Main entry point for cleanup CLI."""
    parser = argparse.ArgumentParser(
        description="Clean up old job postings from the database"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=None,
        help="Number of days to retain (default: from config, typically 7)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting",
    )
    
    args = parser.parse_args()
    
    config = get_config()
    retention_days = args.days if args.days is not None else config.job_retention_days
    
    print(f"\n{'='*50}")
    print(f"  JOB CLEANUP - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")
    print(f"  Retention period: {retention_days} days")
    print(f"  Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"{'='*50}\n")
    
    try:
        count = cleanup_old_jobs(days=args.days, dry_run=args.dry_run)
        
        if args.dry_run:
            print(f"  Would delete {count} job(s) older than {retention_days} days.")
        else:
            print(f"  Deleted {count} job(s) older than {retention_days} days.")
        
        print(f"\n{'='*50}\n")
        return 0
        
    except Exception as e:
        print(f"ERROR: Cleanup failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
