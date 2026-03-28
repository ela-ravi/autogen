"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useJobs } from "@/hooks/useJobs";
import { formatDate, formatFileSize, statusColor } from "@/lib/utils";
import { JobDetailContent } from "@/components/jobs/JobDetailContent";

function JobsPageContent() {
  const { jobs, total, loading, fetchJobs } = useJobs();
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [modalJobId, setModalJobId] = useState<string | null>(null);
  const searchParams = useSearchParams();
  const router = useRouter();

  useEffect(() => {
    fetchJobs(page, statusFilter || undefined);
  }, [fetchJobs, page, statusFilter]);

  useEffect(() => {
    const j = searchParams.get("job");
    if (!j) return;
    setModalJobId(j);
    router.replace("/jobs", { scroll: false });
  }, [searchParams, router]);

  useEffect(() => {
    if (!modalJobId) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setModalJobId(null);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [modalJobId]);

  const totalPages = Math.ceil(total / 20);

  return (
    <div>
      <h2 className="mb-6 text-2xl font-bold">Jobs</h2>

      <div className="mb-4 flex flex-wrap gap-2">
        {["", "pending", "processing", "completed", "failed"].map((s) => (
          <button
            key={s || "all"}
            type="button"
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

      <div className="rounded-lg border">
        {loading ? (
          <div className="p-8 text-center text-muted-foreground">Loading...</div>
        ) : jobs.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">No jobs found.</div>
        ) : (
          <div className="divide-y">
            {jobs.map((job) => (
              <button
                key={job.id}
                type="button"
                onClick={() => setModalJobId(job.id)}
                className="flex w-full items-center justify-between p-4 text-left hover:bg-secondary/50"
              >
                <div className="min-w-0 flex-1">
                  <p className="truncate font-medium">{job.original_filename}</p>
                  <p className="text-xs text-muted-foreground">
                    {formatFileSize(job.file_size_bytes)} &middot; {formatDate(job.created_at)}
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
                      job.status,
                    )}`}
                  >
                    {job.status}
                  </span>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {totalPages > 1 && (
        <div className="mt-4 flex justify-center gap-2">
          <button
            type="button"
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
            type="button"
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="rounded-md border px-3 py-1 text-sm disabled:opacity-50"
          >
            Next
          </button>
        </div>
      )}

      {modalJobId && (
        <div
          className="fixed inset-0 z-50 flex justify-center overflow-y-auto bg-black/50 px-3 pb-10 pt-12 sm:px-4 sm:pt-16"
          role="dialog"
          aria-modal="true"
          aria-label="Job details"
        >
          <button
            type="button"
            className="fixed inset-0 z-0 cursor-default border-0 bg-transparent p-0"
            aria-label="Close job details"
            onClick={() => setModalJobId(null)}
          />
          <div
            className="relative z-10 mt-0 w-[min(75vw,calc(100vw-2rem))] rounded-lg border bg-background shadow-lg"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="max-h-[85vh] overflow-y-auto p-4 sm:p-6">
              <JobDetailContent
                key={modalJobId}
                jobId={modalJobId}
                onClose={() => setModalJobId(null)}
                onAfterDelete={() => {
                  setModalJobId(null);
                  fetchJobs(page, statusFilter || undefined);
                }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function JobsPage() {
  return (
    <Suspense
      fallback={<div className="p-8 text-center text-muted-foreground">Loading jobs…</div>}
    >
      <JobsPageContent />
    </Suspense>
  );
}
