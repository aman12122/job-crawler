'use client';

import { useEffect, useState } from 'react';
import { Job } from '@/lib/db';
import { JobCard } from '@/components/JobCard';

export default function Home() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [crawling, setCrawling] = useState(false);
  const [filters, setFilters] = useState({
    entryLevel: false,
    sort: 'date', // 'date' | 'company'
  });

  const fetchJobs = async () => {
    setLoading(true);
    const params = new URLSearchParams();
    if (filters.entryLevel) params.append('entryLevel', 'true');
    params.append('sort', filters.sort);

    try {
      const res = await fetch(`/api/jobs?${params.toString()}`);
      const data = await res.json();
      setJobs(data);
    } catch (error) {
      console.error('Failed to fetch jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, [filters]);

  const handleCrawl = async () => {
    setCrawling(true);
    try {
      const res = await fetch('/api/crawl', { method: 'POST' });
      if (res.status === 202) {
        alert('Crawl started! It may take a few minutes. Refresh later to see new jobs.');
      } else if (res.status === 409) {
        alert('Crawl already in progress.');
      } else {
        alert('Failed to start crawl.');
      }
    } catch (error) {
      console.error('Crawl trigger error:', error);
      alert('Error triggering crawl.');
    } finally {
      setCrawling(false);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black">
      <header className="bg-white dark:bg-zinc-900 shadow-sm ring-1 ring-zinc-900/5 dark:ring-white/10">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-zinc-900 dark:text-white">
              Job Crawler
            </h1>
            <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
              Tracking new grad & associate roles daily
            </p>
          </div>
          
          <div className="flex flex-wrap items-center gap-4">
            <button
              onClick={handleCrawl}
              disabled={crawling}
              className="rounded-md bg-zinc-900 px-3.5 py-2 text-sm font-semibold text-white shadow-sm hover:bg-zinc-700 disabled:opacity-50 dark:bg-white dark:text-zinc-900 dark:hover:bg-zinc-200"
            >
              {crawling ? 'Starting...' : 'Crawl Now'}
            </button>

            <div className="h-6 w-px bg-zinc-200 dark:bg-zinc-700 hidden sm:block"></div>

            <label className="flex items-center gap-2 text-sm font-medium text-zinc-700 dark:text-zinc-300">
              <input
                type="checkbox"
                checked={filters.entryLevel}
                onChange={(e) => setFilters(prev => ({ ...prev, entryLevel: e.target.checked }))}
                className="h-4 w-4 rounded border-zinc-300 text-black focus:ring-black dark:border-zinc-700 dark:bg-zinc-800"
              />
              Entry Level Only
            </label>
            
            <select
              value={filters.sort}
              onChange={(e) => setFilters(prev => ({ ...prev, sort: e.target.value }))}
              className="rounded-md border-0 py-1.5 pl-3 pr-8 text-sm text-zinc-900 ring-1 ring-inset ring-zinc-300 focus:ring-2 focus:ring-black dark:bg-zinc-800 dark:text-white dark:ring-zinc-700 sm:leading-6"
            >
              <option value="date">Newest First</option>
              <option value="company">Company Name</option>
            </select>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {loading ? (
          <div className="flex justify-center py-12">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-zinc-900 border-t-transparent dark:border-white"></div>
          </div>
        ) : jobs.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-zinc-500 dark:text-zinc-400">No jobs found matching your criteria.</p>
          </div>
        ) : (
          <div className="grid gap-6 sm:grid-cols-1 lg:grid-cols-2">
            {jobs.map((job) => (
              <JobCard key={job.id} job={job} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
