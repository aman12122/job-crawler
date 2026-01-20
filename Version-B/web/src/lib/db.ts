import { Pool } from 'pg';

const pool = new Pool({
  user: process.env.DATABASE_USER,
  password: process.env.DATABASE_PASSWORD,
  host: process.env.DATABASE_HOST,
  port: parseInt(process.env.DATABASE_PORT || '5432'),
  database: process.env.DATABASE_NAME,
});

export default pool;

export type JobV2 = {
  id: number;
  company_name: string;
  title: string;
  url: string;
  
  // Metadata
  location: string | null;
  department: string | null;
  employment_type: string | null;
  
  // AI Analysis
  analysis_status: 'pending' | 'analyzed' | 'failed' | 'skipped';
  ai_is_entry_level: boolean | null;
  ai_confidence_score: number | null;
  ai_years_required: number | null;
  ai_reasoning: string | null;
  
  first_seen_at: Date;
  updated_at: Date;
};
