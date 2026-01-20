import { JobV2 } from '@/lib/db';
import { formatDistanceToNow } from 'date-fns';
import { Bot, CheckCircle, AlertCircle, XCircle, Clock } from 'lucide-react';
import clsx from 'clsx';

export function JobCard({ job }: { job: JobV2 }) {
  const isAnalyzed = job.analysis_status === 'analyzed';
  const isFailed = job.analysis_status === 'failed';
  const isPending = job.analysis_status === 'pending';
  
  // Confidence Color Logic
  const confidence = job.ai_confidence_score || 0;
  const confidenceColor = 
    confidence >= 80 ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' :
    confidence >= 50 ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400' :
    'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400';

  return (
    <div className="group relative bg-white dark:bg-zinc-900 p-6 shadow-sm ring-1 ring-zinc-900/5 dark:ring-white/10 transition-all hover:shadow-md hover:ring-zinc-900/10 dark:hover:ring-white/20 sm:rounded-lg">
      <div className="flex items-start justify-between gap-x-4">
        <div className="min-w-0 flex-1">
          <h3 className="text-lg font-semibold leading-6 text-zinc-900 dark:text-white">
            <a href={job.url} target="_blank" rel="noopener noreferrer">
              <span className="absolute inset-0" />
              {job.title}
            </a>
          </h3>
          <div className="mt-1 flex items-center gap-x-2 text-sm leading-5 text-zinc-500 dark:text-zinc-400">
            <p className="font-medium text-zinc-900 dark:text-zinc-200">{job.company_name}</p>
            {job.location && (
              <>
                <svg viewBox="0 0 2 2" className="h-0.5 w-0.5 fill-current"><circle cx={1} cy={1} r={1} /></svg>
                <p>{job.location}</p>
              </>
            )}
            {job.department && (
              <>
                <svg viewBox="0 0 2 2" className="h-0.5 w-0.5 fill-current"><circle cx={1} cy={1} r={1} /></svg>
                <p>{job.department}</p>
              </>
            )}
          </div>
        </div>
        
        {/* Badges */}
        <div className="flex flex-col gap-2 items-end">
          {isAnalyzed && job.ai_is_entry_level && (
            <span className={clsx(
              "inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ring-black/10",
              confidenceColor
            )}>
              <Bot className="w-3 h-3" />
              {confidence}% Confidence
            </span>
          )}
          {isPending && (
            <span className="inline-flex items-center gap-1 rounded-md bg-gray-100 px-2 py-1 text-xs font-medium text-gray-600 ring-1 ring-inset ring-gray-500/10 dark:bg-gray-400/10 dark:text-gray-400">
              <Clock className="w-3 h-3" />
              Analyzing...
            </span>
          )}
           {isFailed && (
            <span className="inline-flex items-center gap-1 rounded-md bg-red-50 px-2 py-1 text-xs font-medium text-red-700 ring-1 ring-inset ring-red-600/10 dark:bg-red-400/10 dark:text-red-400">
              <AlertCircle className="w-3 h-3" />
              Analysis Failed
            </span>
          )}
        </div>
      </div>

      {/* AI Reasoning Box */}
      {isAnalyzed && job.ai_reasoning && (
        <div className="mt-4 rounded-md bg-zinc-50 dark:bg-zinc-800/50 p-3 text-sm text-zinc-600 dark:text-zinc-300 ring-1 ring-inset ring-zinc-900/5 dark:ring-white/5">
          <p className="flex items-start gap-2">
            <Bot className="w-4 h-4 mt-0.5 flex-shrink-0 text-indigo-500" />
            <span>{job.ai_reasoning}</span>
          </p>
          {job.ai_years_required !== null && (
             <p className="ml-6 mt-1 text-xs text-zinc-500">
               Experience detected: {job.ai_years_required} years
             </p>
          )}
        </div>
      )}

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
