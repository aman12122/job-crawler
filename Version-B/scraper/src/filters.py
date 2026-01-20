import logging
from .models import Job

logger = logging.getLogger(__name__)

class PreFilter:
    """
    Heuristic-based filter to discard jobs before expensive AI analysis.
    """
    
    # Titles that are definitely NOT entry level
    REJECT_KEYWORDS = [
        "senior", "principal", "staff", "lead", "manager", "director", "vp", 
        "head of", "architect", "sr.", "mgr", "ii", "iii", "iv"
    ]
    
    # Titles that ARE definitely entry level (to bypass strict filtering if needed)
    ACCEPT_KEYWORDS = [
        "junior", "associate", "analyst", "intern", "trainee", "entry level", 
        "graduate", "grad", "apprentice"
    ]

    @classmethod
    def filter(cls, job: Job) -> Job:
        """
        Applies filtering logic to a job.
        Updates job.prefilter_rejected and job.prefilter_reason.
        """
        title_lower = job.title.lower()
        
        # Check for rejection keywords
        for keyword in cls.REJECT_KEYWORDS:
            # Word boundary check is better, but simple substring is faster and usually sufficient for these specific words
            # E.g., "Senior" in "Senior Engineer"
            if f" {keyword} " in f" {title_lower} " or title_lower.startswith(f"{keyword} ") or title_lower.endswith(f" {keyword}"):
                job.prefilter_rejected = True
                job.prefilter_reason = f"Title contains rejection keyword: '{keyword}'"
                job.analysis_status = 'skipped'
                return job
                
        return job
