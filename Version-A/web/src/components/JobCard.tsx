import { Job } from '@/lib/db';
import { formatDistanceToNow } from 'date-fns';

export function JobCard({ job }: { job: Job }) {
  return (
    <div className="group relative bg-white dark:bg-zinc-900 p-6 shadow-sm ring-1 ring-zinc-900/5 dark:ring-white/10 transition-all hover:shadow-md hover:ring-zinc-900/10 dark:hover:ring-white/20 sm:rounded-lg">
      <div className="flex items-center justify-between gap-x-4">
        <h3 className="text-lg font-semibold leading-6 text-zinc-900 dark:text-white">
          <a href={job.url} target="_blank" rel="noopener noreferrer">
            <span className="absolute inset-0" />
            {job.title}
          </a>
        </h3>
        {job.is_entry_level && (
          <span className="inline-flex items-center rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20 dark:bg-green-500/10 dark:text-green-400 dark:ring-green-500/20">
            Entry Level
          </span>
        )}
      </div>
      <div className="mt-1 flex items-center gap-x-2 text-sm leading-5 text-zinc-500 dark:text-zinc-400">
        <p className="font-medium text-zinc-900 dark:text-zinc-200">{job.company_name}</p>
        <svg viewBox="0 0 2 2" className="h-0.5 w-0.5 fill-current">
          <circle cx={1} cy={1} r={1} />
        </svg>
        <p>{job.category || 'General'}</p>
        {job.location && (
          <>
            <svg viewBox="0 0 2 2" className="h-0.5 w-0.5 fill-current">
              <circle cx={1} cy={1} r={1} />
            </svg>
            <p>{job.location}</p>
          </>
        )}
      </div>
      <div className="mt-4 flex items-center gap-x-4 text-xs leading-5 text-zinc-500 dark:text-zinc-400">
        <p>Found {formatDistanceToNow(new Date(job.first_seen_at), { addSuffix: true })}</p>
        <a 
          href={job.url}
          target="_blank" 
          rel="noopener noreferrer"
          className="relative z-10 rounded-full bg-zinc-50 px-3 py-1.5 font-medium text-zinc-600 hover:bg-zinc-100 dark:bg-zinc-800 dark:text-zinc-300 dark:hover:bg-zinc-700 transition-colors"
        >
          Apply &rarr;
        </a>
      </div>
    </div>
  );
}
