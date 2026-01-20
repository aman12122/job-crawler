"""
Job Crawler Version B

An AI-powered job crawler that uses Google Gemini to intelligently
filter job postings based on experience requirements.

Key Features:
- Pagination handling for large career sites (100s of listings)
- AI-powered analysis using Google Gemini Flash
- Pre-filtering to save API quota
- Async architecture for fast scraping

Architecture:
    Discovery Queue → Pre-Filter → Detail Fetch → AI Analysis → Database
    (Fast)           (Keywords)    (HTML)         (Rate Limited)  (Store)
"""

__version__ = "2.0.0"
__author__ = "Job Crawler Team"
