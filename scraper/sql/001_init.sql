-- Job Crawler Database Schema
-- Version: 1.0.0
-- Description: Initial schema for storing companies and job postings

-- Enable UUID extension for future use
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- COMPANIES TABLE
-- ============================================
-- Stores the companies/career pages being tracked
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    careers_url TEXT NOT NULL UNIQUE,
    platform VARCHAR(50) NOT NULL DEFAULT 'unknown',  -- 'bamboohr', 'greenhouse', 'lever', 'custom'
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_crawled_at TIMESTAMP WITH TIME ZONE
);

-- Index for active companies lookup
CREATE INDEX idx_companies_active ON companies(is_active) WHERE is_active = TRUE;

-- ============================================
-- JOBS TABLE
-- ============================================
-- Stores individual job postings
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    external_id VARCHAR(255) NOT NULL,  -- ID from the career site
    title VARCHAR(500) NOT NULL,
    category VARCHAR(255),
    location VARCHAR(255),
    employment_type VARCHAR(100),
    url TEXT NOT NULL,
    is_entry_level BOOLEAN NOT NULL DEFAULT FALSE,
    posted_at TIMESTAMP WITH TIME ZONE,
    first_seen_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure no duplicate jobs per company
    CONSTRAINT unique_job_per_company UNIQUE (company_id, external_id)
);

-- Indexes for common queries
CREATE INDEX idx_jobs_company ON jobs(company_id);
CREATE INDEX idx_jobs_first_seen ON jobs(first_seen_at);
CREATE INDEX idx_jobs_entry_level ON jobs(is_entry_level) WHERE is_entry_level = TRUE;
CREATE INDEX idx_jobs_created ON jobs(created_at);

-- ============================================
-- FUNCTIONS
-- ============================================

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- ============================================
-- TRIGGERS
-- ============================================

-- Auto-update updated_at for companies
CREATE TRIGGER update_companies_updated_at
    BEFORE UPDATE ON companies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Auto-update updated_at for jobs
CREATE TRIGGER update_jobs_updated_at
    BEFORE UPDATE ON jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- SEED DATA
-- ============================================

-- Insert the initial test company (d1g1t)
INSERT INTO companies (name, careers_url, platform)
VALUES ('d1g1t', 'https://d1g1t.bamboohr.com/careers', 'bamboohr');

-- ============================================
-- COMMENTS
-- ============================================

COMMENT ON TABLE companies IS 'Companies/career pages being tracked by the job crawler';
COMMENT ON TABLE jobs IS 'Individual job postings scraped from company career pages';
COMMENT ON COLUMN jobs.external_id IS 'The job ID from the source career site (used for deduplication)';
COMMENT ON COLUMN jobs.first_seen_at IS 'When the job was first discovered (used for "new" job detection)';
COMMENT ON COLUMN jobs.is_entry_level IS 'Whether the job matches entry-level/new grad criteria';
