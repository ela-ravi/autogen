"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useJobs } from "@/hooks/useJobs";
import { formatDate, formatFileSize, statusColor } from "@/lib/utils";

export default function JobsPage() {
  const { jobs, total, loading, fetchJobs } = useJobs();
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string>("");

  useEffect(() => {
    fetchJobs(page, statusFilter || undefined);
  }, [fetchJobs, page, statusFilter]);

  const totalPages = Math.ceil(total / 20);

  return (
    <div>
      <h2 className="mb-6 text-2xl font-bold">Jobs</h2>

      {/* Filters */}
      <div className="mb-4 flex gap-2">
        {["", "pending", "processing", "completed", "failed"].map((s) => (
          <button
            key={s}
            onClick={() => {
              setStatusFilter(s);
              setPage(1);
            }}
            className={`rounded-md px-3 py-1.5 text-xs font-medium ${
              statusFilter === s
                ? "bg-primary text-primary-foreground"
                : "bg-secondary text-muted-foreground hover:text-foreground"
            }`}
          >
            {s || "All"}
          </button>
        ))}
      </div>

      {/* Jobs Table */}
      <div className="rounded-lg border">
        {loading ? (
          <div className="p-8 text-center text-muted-foreground">Loading...</div>
        ) : jobs.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            No jobs found.
          </div>
        ) : (
          <div className="divide-y">
            {jobs.map((job) => (
              <Link
                key={job.id}
                href={`/jobs/${job.id}`}
                className="flex items-center justify-between p-4 hover:bg-secondary/50"
              >
                <div className="min-w-0 flex-1">
                  <p className="truncate font-medium">{job.original_filename}</p>
                  <p className="text-xs text-muted-foreground">
                    {formatFileSize(job.file_size_bytes)} &middot;{" "}
                    {formatDate(job.created_at)}
                  </p>
                </div>
                <div className="ml-4 flex items-center gap-3">
                  {job.status === "processing" && (
                    <span className="text-xs text-muted-foreground">
                      {Math.round(job.progress_pct)}%
                    </span>
                  )}
                  <span
                    className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${statusColor(
                      job.status
                    )}`}
                  >
                    {job.status}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-4 flex justify-center gap-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="rounded-md border px-3 py-1 text-sm disabled:opacity-50"
          >
            Previous
          </button>
          <span className="px-3 py-1 text-sm text-muted-foreground">
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="rounded-md border px-3 py-1 text-sm disabled:opacity-50"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
