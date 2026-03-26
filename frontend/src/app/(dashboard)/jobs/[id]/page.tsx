"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { toast } from "sonner";
import { useJobs } from "@/hooks/useJobs";
import { useJobProgress } from "@/hooks/useJobProgress";
import { formatDate, formatFileSize, statusColor } from "@/lib/utils";
import type { Job } from "@/lib/types";
import api from "@/lib/api";
import { Download, Trash2, RotateCcw, Square } from "lucide-react";

const STEP_NAMES = [
  "",
  "Transcribing video",
  "Translating transcription",
  "Generating recap",
  "Generating narration",
  "Extracting clips",
  "Removing audio",
  "Merging final video",
];

export default function JobDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [job, setJob] = useState<Job | null>(null);
  const [resuming, setResuming] = useState(false);
  const [stopping, setStopping] = useState(false);
  const [activityLog, setActivityLog] = useState<{ time: string; message: string; step: number }[]>([]);
  const logEndRef = useRef<HTMLDivElement>(null);
  const { getJob, deleteJob, resumeJob, stopJob } = useJobs();
  const progress = useJobProgress(
    job?.status === "processing" || job?.status === "pending" ? id : null
  );
  const router = useRouter();

  const fetchJob = useCallback(async () => {
    const data = await getJob(id);
    setJob(data);
  }, [id, getJob]);

  useEffect(() => {
    fetchJob();
  }, [fetchJob]);

  useEffect(() => {
    if (progress?.type === "completed" || progress?.type === "failed" || progress?.type === "stopped") {
      fetchJob();
    }
    if (progress?.message) {
      const msg = progress.message;
      const step = progress.step ?? 0;
      setActivityLog((prev) => {
        if (prev.length > 0 && prev[prev.length - 1].message === msg) return prev;
        return [...prev, { time: new Date().toLocaleTimeString(), message: msg, step }];
      });
    }
  }, [progress, fetchJob]);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [activityLog]);

  const handleDownload = async () => {
    try {
      const response = await api.get(`/jobs/${id}/download`, { responseType: "blob" });
      const disposition = response.headers["content-disposition"] || "";
      const match = disposition.match(/filename="?(.+?)"?$/);
      const filename = match?.[1] || "recap_video.mp4";
      const url = URL.createObjectURL(response.data);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      toast.error("Download not available");
    }
  };

  const handleDelete = async () => {
    if (!confirm("Delete this job and all associated files?")) return;
    try {
      await deleteJob(id);
      toast.success("Job deleted");
      router.push("/jobs");
    } catch {
      toast.error("Failed to delete job");
    }
  };

  const handleResume = async () => {
    setResuming(true);
    try {
      const updated = await resumeJob(id);
      setJob(updated);
      toast.success(
        `Resuming from step ${updated.current_step}: ${STEP_NAMES[updated.current_step] || ""}`,
      );
    } catch {
      toast.error("Failed to resume job");
    } finally {
      setResuming(false);
    }
  };

  const handleStop = async () => {
    setStopping(true);
    try {
      const updated = await stopJob(id);
      setJob(updated);
      toast.success("Job stopped. You can resume it later.");
    } catch {
      toast.error("Failed to stop job");
    } finally {
      setStopping(false);
    }
  };

  if (!job) {
    return <div className="text-muted-foreground">Loading...</div>;
  }

  const activeStep = progress?.step ?? job.current_step;
  const activePct = progress?.progress_pct ?? job.progress_pct;
  const activeMessage = progress?.message ?? job.current_step_name;

  return (
    <div className="mx-auto max-w-3xl">
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-2xl font-bold">{job.original_filename}</h2>
        <div className="flex gap-2">
          {(job.status === "processing" || job.status === "pending") && (
            <button
              onClick={handleStop}
              disabled={stopping}
              className="flex items-center gap-1 rounded-md bg-orange-600 px-4 py-2 text-sm text-white hover:bg-orange-700 disabled:opacity-50"
            >
              <Square className="h-3.5 w-3.5 fill-current" />
              {stopping ? "Stopping..." : "Stop"}
            </button>
          )}
          {(job.status === "failed" || job.status === "stopped") && (
            <button
              onClick={handleResume}
              disabled={resuming}
              className="flex items-center gap-1 rounded-md bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
            >
              <RotateCcw className={`h-4 w-4 ${resuming ? "animate-spin" : ""}`} />
              {resuming ? "Resuming..." : `Resume from Step ${job.current_step}`}
            </button>
          )}
          {job.status === "completed" && (
            <button
              onClick={handleDownload}
              className="flex items-center gap-1 rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:opacity-90"
            >
              <Download className="h-4 w-4" />
              Download
            </button>
          )}
          <button
            onClick={handleDelete}
            className="flex items-center gap-1 rounded-md border px-4 py-2 text-sm text-destructive hover:bg-destructive/10"
          >
            <Trash2 className="h-4 w-4" />
            Delete
          </button>
        </div>
      </div>

      {/* Status */}
      <div className="mb-6 rounded-lg border p-6">
        <div className="mb-4 flex items-center justify-between">
          <span
            className={`rounded-full px-3 py-1 text-sm font-medium ${statusColor(
              job.status
            )}`}
          >
            {job.status}
          </span>
          <span className="text-sm text-muted-foreground">
            {formatFileSize(job.file_size_bytes)}
          </span>
        </div>

        {/* Progress bar */}
        {(job.status === "processing" || job.status === "pending") && (
          <div>
            <div className="mb-2 h-3 rounded-full bg-secondary">
              <div
                className="h-3 rounded-full bg-blue-600 transition-all duration-500"
                style={{ width: `${activePct}%` }}
              />
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">
                {activeMessage || "Waiting..."}
              </span>
              <span className="font-medium">{Math.round(activePct)}%</span>
            </div>

            {/* Step indicators */}
            <div className="mt-4 grid grid-cols-7 gap-1">
              {[1, 2, 3, 4, 5, 6, 7].map((step) => (
                <div key={step} className="text-center">
                  <div
                    className={`mx-auto mb-1 h-2 w-2 rounded-full ${
                      step < activeStep
                        ? "bg-green-500"
                        : step === activeStep
                        ? "bg-blue-500"
                        : "bg-gray-200"
                    }`}
                  />
                  <p className="text-[10px] text-muted-foreground">
                    {STEP_NAMES[step]?.split(" ")[0]}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {(job.status === "failed" || job.status === "stopped") && (
          <div>
            {job.status === "failed" && job.error_message && (
              <div className="rounded-md bg-red-50 p-4 text-sm text-red-800 dark:bg-red-950/30 dark:text-red-400">
                {job.error_message}
              </div>
            )}
            <div className={job.error_message && job.status === "failed" ? "mt-4" : ""}>
              <p className="mb-2 text-sm text-muted-foreground">
                {job.status === "stopped" ? "Stopped" : "Failed"} at step {job.current_step} of 7: {STEP_NAMES[job.current_step] || "Unknown"}
              </p>
              <div className="grid grid-cols-7 gap-1">
                {[1, 2, 3, 4, 5, 6, 7].map((step) => (
                  <div key={step} className="text-center">
                    <div
                      className={`mx-auto mb-1 h-2 w-2 rounded-full ${
                        step < job.current_step
                          ? "bg-green-500"
                          : step === job.current_step
                          ? job.status === "stopped" ? "bg-orange-500" : "bg-red-500"
                          : "bg-gray-200"
                      }`}
                    />
                    <p className="text-[10px] text-muted-foreground">
                      {STEP_NAMES[step]?.split(" ")[0]}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Activity Log */}
      {activityLog.length > 0 && (
        <div className="mb-6 rounded-lg border p-6">
          <h3 className="mb-3 text-sm font-semibold">Activity Log</h3>
          <div className="max-h-40 overflow-y-auto rounded-md bg-muted/30 p-3 font-mono text-xs leading-relaxed">
            {activityLog.map((entry, i) => (
              <div key={i} className="flex gap-3 py-0.5">
                <span className="shrink-0 text-muted-foreground">{entry.time}</span>
                <span className="shrink-0 text-blue-500">[Step {entry.step}]</span>
                <span>{entry.message}</span>
              </div>
            ))}
            <div ref={logEndRef} />
          </div>
        </div>
      )}

      {/* Details */}
      <div className="rounded-lg border p-6">
        <h3 className="mb-4 font-semibold">Details</h3>
        <dl className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <dt className="text-muted-foreground">Created</dt>
            <dd>{formatDate(job.created_at)}</dd>
          </div>
          {job.started_at && (
            <div>
              <dt className="text-muted-foreground">Started</dt>
              <dd>{formatDate(job.started_at)}</dd>
            </div>
          )}
          {job.completed_at && (
            <div>
              <dt className="text-muted-foreground">Completed</dt>
              <dd>{formatDate(job.completed_at)}</dd>
            </div>
          )}
          {job.expires_at && (
            <div>
              <dt className="text-muted-foreground">Expires</dt>
              <dd>{formatDate(job.expires_at)}</dd>
            </div>
          )}
          <div>
            <dt className="text-muted-foreground">Target Duration</dt>
            <dd>{job.config.target_duration}s</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Voice</dt>
            <dd>{job.config.tts_voice}</dd>
          </div>
        </dl>
      </div>
    </div>
  );
}
