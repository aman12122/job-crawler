'use client';

import { useEffect, useState } from 'react';
import { JobV2 } from '@/lib/db';
import { JobCard } from '@/components/JobCard';
import { Bot, Sparkles } from 'lucide-react';

export default function Home() {
  const [jobs, setJobs] = useState<JobV2[]>([]);
  const [loading, setLoading] = useState(true);
  const [crawling, setCrawling] = useState(false);

  const fetchJobs = async () => {
    setLoading(true);
    try {
      const res = await fetch(`/api/jobs`);
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
  }, []);

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
      <header className="bg-white dark:bg-zinc-900 shadow-sm ring-1 ring-zinc-900/5 dark:ring-white/10 sticky top-0 z-50">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-xl font-bold tracking-tight text-zinc-900 dark:text-white flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-indigo-500" />
              Job Crawler <span className="text-xs font-normal text-zinc-500 border border-zinc-200 rounded px-1.5 py-0.5 ml-2">v2.0 AI</span>
            </h1>
            <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
              Powered by Gemini Flash • Smart Filtering • Full Transparency
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            <button
              onClick={handleCrawl}
              disabled={crawling}
              className="rounded-md bg-zinc-900 px-3.5 py-2 text-sm font-semibold text-white shadow-sm hover:bg-zinc-700 disabled:opacity-50 dark:bg-white dark:text-zinc-900 dark:hover:bg-zinc-200 transition-all flex items-center gap-2"
            >
              {crawling ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin dark:border-zinc-900/30 dark:border-t-zinc-900" />
                  Crawling...
                </>
              ) : (
                <>
                  <Bot className="w-4 h-4" />
                  Run AI Scraper
                </>
              )}
            </button>
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
            <Bot className="w-12 h-12 mx-auto text-zinc-300 mb-4" />
            <h3 className="text-lg font-medium text-zinc-900 dark:text-white">No jobs found yet</h3>
            <p className="text-zinc-500 dark:text-zinc-400 mt-2">
              Run the scraper to discover and analyze jobs.
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="flex items-center justify-between text-sm text-zinc-500">
              <p>Showing top 100 relevant jobs</p>
              <p>Sorted by AI Confidence</p>
            </div>
            <div className="grid gap-6 sm:grid-cols-1 lg:grid-cols-2">
              {jobs.map((job) => (
                <JobCard key={job.id} job={job} />
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
