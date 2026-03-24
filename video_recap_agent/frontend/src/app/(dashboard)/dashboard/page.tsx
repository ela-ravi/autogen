"use client";

import { useEffect } from "react";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { useJobs } from "@/hooks/useJobs";
import { formatDate, statusColor } from "@/lib/utils";
import { Upload, ListVideo, Zap } from "lucide-react";

export default function DashboardPage() {
  const { user } = useAuth();
  const { jobs, total, fetchJobs } = useJobs();

  useEffect(() => {
    fetchJobs(1);
  }, [fetchJobs]);

  const completedCount = jobs.filter((j) => j.status === "completed").length;
  const processingCount = jobs.filter((j) => j.status === "processing").length;

  return (
    <div>
      <h2 className="mb-6 text-2xl font-bold">
        Welcome back, {user?.full_name}
      </h2>

      {/* Stats */}
      <div className="mb-8 grid gap-4 md:grid-cols-3">
        <div className="rounded-lg border p-6">
          <div className="flex items-center gap-3">
            <ListVideo className="h-5 w-5 text-blue-600" />
            <div>
              <p className="text-2xl font-bold">{total}</p>
              <p className="text-sm text-muted-foreground">Total Jobs</p>
            </div>
          </div>
        </div>
        <div className="rounded-lg border p-6">
          <div className="flex items-center gap-3">
            <Zap className="h-5 w-5 text-green-600" />
            <div>
              <p className="text-2xl font-bold">{completedCount}</p>
              <p className="text-sm text-muted-foreground">Completed</p>
            </div>
          </div>
        </div>
        <div className="rounded-lg border p-6">
          <div className="flex items-center gap-3">
            <Upload className="h-5 w-5 text-orange-600" />
            <div>
              <p className="text-2xl font-bold">{processingCount}</p>
              <p className="text-sm text-muted-foreground">Processing</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Jobs */}
      <div className="rounded-lg border">
        <div className="flex items-center justify-between border-b p-4">
          <h3 className="font-semibold">Recent Jobs</h3>
          <Link
            href="/jobs"
            className="text-sm text-blue-600 hover:underline"
          >
            View all
          </Link>
        </div>
        {jobs.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            <p>No jobs yet.</p>
            <Link
              href="/upload"
              className="mt-2 inline-block text-blue-600 hover:underline"
            >
              Upload your first video
            </Link>
          </div>
        ) : (
          <div className="divide-y">
            {jobs.slice(0, 5).map((job) => (
              <Link
                key={job.id}
                href={`/jobs/${job.id}`}
                className="flex items-center justify-between p-4 hover:bg-secondary/50"
              >
                <div>
                  <p className="font-medium">{job.original_filename}</p>
                  <p className="text-xs text-muted-foreground">
                    {formatDate(job.created_at)}
                  </p>
                </div>
                <span
                  className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${statusColor(
                    job.status
                  )}`}
                >
                  {job.status}
                </span>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
