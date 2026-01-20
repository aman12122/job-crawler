import json
import logging
import google.generativeai as genai
from typing import Optional, Dict, Any
from ..config import get_settings
from ..models import Job
from .limiter import RateLimiter

logger = logging.getLogger(__name__)

class AIService:
    """
    Service for analyzing job descriptions using Google Gemini.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.limiter = RateLimiter.get_instance()
        
        # Configure Gemini
        genai.configure(api_key=self.settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    async def analyze_job(self, job: Job) -> Job:
        """
        Analyzes a job description and updates the Job object with AI insights.
        """
        if not job.raw_description_text:
            logger.warning(f"Job {job.external_id} has no description text. Skipping AI analysis.")
            job.analysis_status = 'failed'
            job.ai_reasoning = "Missing description text"
            return job

        # Construct the prompt
        prompt = self._build_prompt(job)
        
        # Wait for rate limiter
        await self.limiter.acquire()
        
        try:
            # Call Gemini (async)
            response = await self.model.generate_content_async(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            
            # Parse response
            result = json.loads(response.text)
            
            # Update job object
            job.ai_is_entry_level = result.get('is_entry_level')
            job.ai_confidence_score = result.get('confidence')
            job.ai_years_required = result.get('min_years_experience')
            job.ai_reasoning = result.get('reasoning')
            job.analysis_status = 'analyzed'
            
            logger.info(f"AI Analysis for {job.title}: Entry Level? {job.ai_is_entry_level} ({job.ai_confidence_score}%)")
            
        except Exception as e:
            logger.error(f"AI Analysis failed for {job.title}: {e}")
            job.analysis_status = 'failed'
            job.ai_reasoning = f"AI Error: {str(e)}"
            
        return job

    def _build_prompt(self, job: Job) -> str:
        """
        Constructs the analysis prompt.
        """
        return f"""
        You are a strict recruiter filtering jobs for a New Graduate (0-2 years experience).
        
        Analyze this job description:
        Title: {job.title}
        Company: {self.settings.USER_AGENT} (Placeholder)
        
        --- DESCRIPTION START ---
        {job.raw_description_text[:10000]} 
        --- DESCRIPTION END ---
        
        Task: Determine if this job is suitable for an entry-level candidate (0-2 years).
        
        Rules:
        1. "Preferred" skills are NOT requirements. Ignore "3+ years preferred" if "0 years required".
        2. "3+ years required" -> REJECT (is_entry_level: false).
        3. "0-3 years" or "1-3 years" -> ACCEPT (is_entry_level: true).
        4. Masters/PhD requirements -> REJECT (unless generic "or equivalent experience").
        5. Internship -> ACCEPT.
        
        Output JSON format:
        {{
          "is_entry_level": boolean,
          "confidence": int, // 0-100
          "min_years_experience": int, // 0 if none stated
          "reasoning": "string (max 100 chars)"
        }}
        """
