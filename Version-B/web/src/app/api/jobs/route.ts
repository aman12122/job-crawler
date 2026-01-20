import { NextResponse } from 'next/server';
import pool from '@/lib/db';

export const dynamic = 'force-dynamic';

export async function GET() {
  try {
    const client = await pool.connect();
    
    // Query v2 tables
    // Prioritize jobs that AI thinks are entry level
    const result = await client.query(`
      SELECT 
        j.id,
        j.title,
        j.url,
        j.location,
        j.department,
        j.employment_type,
        j.analysis_status,
        j.ai_is_entry_level,
        j.ai_confidence_score,
        j.ai_years_required,
        j.ai_reasoning,
        j.first_seen_at,
        j.updated_at,
        c.name as company_name
      FROM v2_jobs j
      JOIN v2_companies c ON j.company_id = c.id
      ORDER BY 
        -- 1. Analyzed & Entry Level jobs first
        (j.analysis_status = 'analyzed' AND j.ai_is_entry_level = TRUE) DESC,
        -- 2. Then by confidence
        j.ai_confidence_score DESC NULLS LAST,
        -- 3. Then by newest
        j.updated_at DESC
      LIMIT 100
    `);
    
    client.release();
    
    return NextResponse.json(result.rows);
  } catch (error) {
    console.error('Error fetching jobs:', error);
    return NextResponse.json(
      { error: 'Failed to fetch jobs' },
      { status: 500 }
    );
  }
}
