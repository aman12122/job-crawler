import { Pool } from 'pg';

const pool = new Pool({
  user: process.env.DATABASE_USER,
  password: process.env.DATABASE_PASSWORD,
  host: process.env.DATABASE_HOST,
  port: parseInt(process.env.DATABASE_PORT || '5434'),
  database: process.env.DATABASE_NAME,
});

export default pool;

export type Job = {
  id: number;
  title: string;
  company_name: string;
  category: string | null;
  location: string | null;
  url: string;
  is_entry_level: boolean;
  first_seen_at: Date;
  created_at: Date;
  employment_type: string | null;
};
