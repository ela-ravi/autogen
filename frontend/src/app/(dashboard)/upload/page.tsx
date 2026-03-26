"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { FileVideo, CheckCircle2, X } from "lucide-react";
import { DropZone } from "@/components/upload/DropZone";
import { UploadForm } from "@/components/upload/UploadForm";
import { useUpload } from "@/hooks/useUpload";
import { formatFileSize } from "@/lib/utils";
import api from "@/lib/api";
import type { Job, JobConfig, UploadResponse } from "@/lib/types";

const STORAGE_KEY = "videorecap_pending_upload";

interface PersistedUpload {
  fileName: string;
  fileSize: number;
  result: UploadResponse;
}

export default function UploadPage() {
  const [fileName, setFileName] = useState<string | null>(null);
  const [fileSize, setFileSize] = useState<number>(0);
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null);
  const { uploading, uploadProgress, uploadVideo } = useUpload();
  const router = useRouter();

  useEffect(() => {
    try {
      const saved = sessionStorage.getItem(STORAGE_KEY);
      if (saved) {
        const data: PersistedUpload = JSON.parse(saved);
        setFileName(data.fileName);
        setFileSize(data.fileSize);
        setUploadResult(data.result);
      }
    } catch { /* ignore */ }
  }, []);

  const handleFileSelect = async (f: File) => {
    setFileName(f.name);
    setFileSize(f.size);
    setUploadResult(null);
    try {
      const result = await uploadVideo(f);
      setUploadResult(result);
      sessionStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({ fileName: f.name, fileSize: f.size, result } satisfies PersistedUpload)
      );
      toast.success("Video uploaded successfully");
    } catch {
      toast.error("Upload failed");
      setFileName(null);
      setUploadResult(null);
      sessionStorage.removeItem(STORAGE_KEY);
    }
  };

  const handleRemoveFile = async () => {
    if (uploadResult?.s3_key) {
      try {
        await api.delete(`/uploads/${uploadResult.s3_key}`);
      } catch {
        /* best-effort cleanup */
      }
    }
    setFileName(null);
    setFileSize(0);
    setUploadResult(null);
    sessionStorage.removeItem(STORAGE_KEY);
  };

  const handleSubmit = async (config: JobConfig) => {
    if (!uploadResult || !fileName) return;
    try {
      const { data } = await api.post<Job>("/jobs", {
        upload_id: uploadResult.upload_id,
        s3_key: uploadResult.s3_key,
        original_filename: uploadResult.filename,
        file_size_bytes: uploadResult.size,
        config,
      });
      sessionStorage.removeItem(STORAGE_KEY);
      toast.success("Job created! Processing started.");
      router.push(`/jobs/${data.id}`);
    } catch (err: unknown) {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail || "Failed to create job";
      if (detail.toLowerCase().includes("api key")) {
        toast.error(detail, {
          action: {
            label: "Go to Settings",
            onClick: () => router.push("/settings"),
          },
          duration: 8000,
        });
      } else {
        toast.error(detail);
      }
    }
  };

  const hasUpload = !!fileName;

  return (
    <div>
      <h2 className="mb-6 text-2xl font-bold">Upload Video</h2>
      <div className="grid gap-6 lg:grid-cols-2">
        <div>
          {!hasUpload && (
            <DropZone onFileSelect={handleFileSelect} disabled={uploading} />
          )}
          {hasUpload && (
            <div
              className={`rounded-lg border p-4 transition-colors ${
                uploadResult && !uploading
                  ? "border-green-300 bg-green-50 dark:border-green-700 dark:bg-green-950/30"
                  : uploading
                    ? "border-blue-300 bg-blue-50 dark:border-blue-700 dark:bg-blue-950/30"
                    : "border-border"
              }`}
            >
              <div className="flex items-center gap-3">
                <FileVideo className="h-6 w-6 shrink-0 text-muted-foreground" />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-base font-semibold">{fileName}</p>
                  <p className="text-sm text-muted-foreground">
                    {formatFileSize(fileSize)}
                  </p>
                </div>
                {uploadResult && !uploading && (
                  <span className="flex shrink-0 items-center gap-1 text-sm font-medium text-green-600">
                    <CheckCircle2 className="h-5 w-5" />
                    Uploaded
                  </span>
                )}
                {!uploading && (
                  <button
                    type="button"
                    onClick={handleRemoveFile}
                    title="Remove file"
                    className="shrink-0 rounded-md p-1 text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive"
                  >
                    <X className="h-5 w-5" />
                  </button>
                )}
              </div>
              {uploading && (
                <div className="mt-3">
                  <div className="h-2 rounded-full bg-blue-100">
                    <div
                      className="h-2 rounded-full bg-blue-600 transition-all"
                      style={{ width: `${uploadProgress}%` }}
                    />
                  </div>
                  <p className="mt-1 text-xs text-muted-foreground">
                    Uploading... {uploadProgress}%
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
        <UploadForm
          onSubmit={handleSubmit}
          disabled={!uploadResult || uploading}
        />
      </div>
    </div>
  );
}
