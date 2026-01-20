import { NextResponse } from 'next/server';
import pool from '@/lib/db';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const entryLevelOnly = searchParams.get('entryLevel') === 'true';
  const company = searchParams.get('company');
  const sort = searchParams.get('sort') || 'date'; // date, company

  let query = `
    SELECT 
      j.id, j.title, j.category, j.location, j.employment_type,
      j.url, j.is_entry_level, j.first_seen_at, j.created_at,
      c.name as company_name
    FROM jobs j
    JOIN companies c ON j.company_id = c.id
    WHERE 1=1
  `;

  const params: any[] = [];
  let paramIndex = 1;

  if (entryLevelOnly) {
    query += ` AND j.is_entry_level = true`;
  }

  if (company) {
    query += ` AND c.name ILIKE $${paramIndex}`;
    params.push(`%${company}%`);
    paramIndex++;
  }

  if (sort === 'company') {
    query += ` ORDER BY c.name ASC, j.first_seen_at DESC`;
  } else {
    // Default to date sort
    query += ` ORDER BY j.first_seen_at DESC`;
  }

  query += ` LIMIT 100`;

  try {
    const result = await pool.query(query, params);
    return NextResponse.json(result.rows);
  } catch (error) {
    console.error('Database error:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
