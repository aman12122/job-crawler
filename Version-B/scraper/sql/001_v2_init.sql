-- Job Crawler Version B - Database Schema
-- =========================================
-- This schema supports AI-powered job analysis with full transparency.
-- 
-- Key Differences from V1:
--   1. Stores full job descriptions for AI analysis
--   2. Tracks AI reasoning and confidence scores
--   3. Supports multiple pagination strategies per company
--   4. Separates "analysis pending" from "analyzed" states
--
-- Migration Note: V1 tables are preserved. V2 uses v2_ prefix.

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- V2 COMPANIES TABLE
-- ============================================
-- Enhanced company tracking with scraping strategy metadata
CREATE TABLE IF NOT EXISTS v2_companies (
    id SERIAL PRIMARY KEY,
    
    -- Basic Info
    name VARCHAR(255) NOT NULL,
    careers_url TEXT NOT NULL UNIQUE,
    
    -- Scraping Configuration
    -- strategy: 'bamboohr', 'greenhouse', 'lever', 'workday', 'custom'
    strategy VARCHAR(50) NOT NULL DEFAULT 'auto',
    
    -- pagination_type: 'offset', 'token', 'link', 'none'
    pagination_type VARCHAR(20) DEFAULT 'auto',
    
    -- Optional: Custom selectors for 'custom' strategy
    custom_config JSONB,
    
    -- Operational State
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_crawled_at TIMESTAMP WITH TIME ZONE,
    last_error TEXT,  -- Store last crawl error for debugging
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for active companies
CREATE INDEX IF NOT EXISTS idx_v2_companies_active 
    ON v2_companies(is_active) WHERE is_active = TRUE;

-- ============================================
-- V2 JOBS TABLE
-- ============================================
-- Enhanced job storage with AI analysis fields
CREATE TABLE IF NOT EXISTS v2_jobs (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES v2_companies(id) ON DELETE CASCADE,
    
    -- Job Identity
    external_id VARCHAR(255) NOT NULL,  -- ID from source site
    title VARCHAR(500) NOT NULL,
    url TEXT NOT NULL,
    
    -- Job Metadata (from list view)
    location VARCHAR(255),
    department VARCHAR(255),
    employment_type VARCHAR(100),  -- Full-time, Part-time, Contract, etc.
    
    -- Raw Content (for AI analysis and re-processing)
    raw_description_text TEXT,  -- Cleaned text from HTML
    raw_description_html TEXT,  -- Original HTML (optional, for debugging)
    
    -- =========================================
    -- AI ANALYSIS FIELDS (populated by Gemini)
    -- =========================================
    
    -- Analysis State
    -- 'pending': Not yet analyzed
    -- 'analyzed': Successfully analyzed by AI
    -- 'failed': AI analysis failed (quota, error, etc.)
    -- 'skipped': Pre-filtered out (e.g., "Senior" in title)
    analysis_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    
    -- AI Results
    ai_is_entry_level BOOLEAN,           -- True = suitable for new grads
    ai_confidence_score INTEGER,          -- 0-100, how confident the AI is
    ai_years_required INTEGER,            -- Extracted years of experience
    ai_reasoning TEXT,                    -- "Requires 5+ years Java experience"
    
    -- Analysis Metadata
    analyzed_at TIMESTAMP WITH TIME ZONE,
    analysis_model VARCHAR(50),           -- e.g., 'gemini-1.5-flash'
    analysis_prompt_version INTEGER,      -- Track prompt iterations
    
    -- Pre-filter Info
    prefilter_rejected BOOLEAN DEFAULT FALSE,
    prefilter_reason VARCHAR(255),        -- "Title contains 'Senior'"
    
    -- =========================================
    -- TIMESTAMPS & TRACKING
    -- =========================================
    first_seen_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure no duplicate jobs per company
    CONSTRAINT unique_v2_job_per_company UNIQUE (company_id, external_id)
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_v2_jobs_company ON v2_jobs(company_id);
CREATE INDEX IF NOT EXISTS idx_v2_jobs_analysis_status ON v2_jobs(analysis_status);
CREATE INDEX IF NOT EXISTS idx_v2_jobs_entry_level ON v2_jobs(ai_is_entry_level) 
    WHERE ai_is_entry_level = TRUE;
CREATE INDEX IF NOT EXISTS idx_v2_jobs_first_seen ON v2_jobs(first_seen_at);
CREATE INDEX IF NOT EXISTS idx_v2_jobs_pending ON v2_jobs(analysis_status) 
    WHERE analysis_status = 'pending';

-- ============================================
-- V2 CRAWL HISTORY TABLE
-- ============================================
-- Track crawl runs for debugging and monitoring
CREATE TABLE IF NOT EXISTS v2_crawl_history (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES v2_companies(id) ON DELETE CASCADE,
    
    -- Crawl Metrics
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Results
    jobs_discovered INTEGER DEFAULT 0,      -- Total jobs found on pages
    jobs_new INTEGER DEFAULT 0,             -- New jobs added to DB
    jobs_prefiltered INTEGER DEFAULT 0,     -- Rejected by pre-filter
    jobs_analyzed INTEGER DEFAULT 0,        -- Sent to AI
    jobs_entry_level INTEGER DEFAULT 0,     -- Marked as entry level
    
    -- Pagination Stats
    pages_crawled INTEGER DEFAULT 0,
    
    -- Status
    status VARCHAR(20) DEFAULT 'running',   -- running, completed, failed
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_v2_crawl_history_company ON v2_crawl_history(company_id);

-- ============================================
-- FUNCTIONS
-- ============================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_v2_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- ============================================
-- TRIGGERS
-- ============================================

-- Apply to v2_companies
DROP TRIGGER IF EXISTS update_v2_companies_updated_at ON v2_companies;
CREATE TRIGGER update_v2_companies_updated_at
    BEFORE UPDATE ON v2_companies
    FOR EACH ROW
    EXECUTE FUNCTION update_v2_updated_at_column();

-- Apply to v2_jobs
DROP TRIGGER IF EXISTS update_v2_jobs_updated_at ON v2_jobs;
CREATE TRIGGER update_v2_jobs_updated_at
    BEFORE UPDATE ON v2_jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_v2_updated_at_column();

-- ============================================
-- COMMENTS (Documentation)
-- ============================================

COMMENT ON TABLE v2_companies IS 'Version B: Companies with enhanced scraping metadata';
COMMENT ON TABLE v2_jobs IS 'Version B: Jobs with AI analysis results and full descriptions';
COMMENT ON TABLE v2_crawl_history IS 'Version B: Crawl run history for monitoring';

COMMENT ON COLUMN v2_jobs.analysis_status IS 'pending=not analyzed, analyzed=AI complete, failed=AI error, skipped=pre-filtered';
COMMENT ON COLUMN v2_jobs.ai_reasoning IS 'Human-readable explanation from AI (shown in UI)';
COMMENT ON COLUMN v2_jobs.raw_description_text IS 'Full job description text for AI re-analysis';
COMMENT ON COLUMN v2_companies.strategy IS 'Scraping strategy: bamboohr, greenhouse, lever, workday, custom, auto';
