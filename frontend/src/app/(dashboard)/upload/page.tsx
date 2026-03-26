"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { FileVideo, CheckCircle2 } from "lucide-react";
import { DropZone } from "@/components/upload/DropZone";
import { UploadForm } from "@/components/upload/UploadForm";
import { useUpload } from "@/hooks/useUpload";
import { formatFileSize } from "@/lib/utils";
import api from "@/lib/api";
import type { Job, JobConfig, UploadResponse } from "@/lib/types";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null);
  const { uploading, uploadProgress, uploadVideo } = useUpload();
  const router = useRouter();

  const handleFileSelect = async (f: File) => {
    setFile(f);
    try {
      const result = await uploadVideo(f);
      setUploadResult(result);
      toast.success("Video uploaded successfully");
    } catch {
      toast.error("Upload failed");
      setFile(null);
    }
  };

  const handleSubmit = async (config: JobConfig) => {
    if (!uploadResult || !file) return;
    try {
      const { data } = await api.post<Job>("/jobs", {
        upload_id: uploadResult.upload_id,
        s3_key: uploadResult.s3_key,
        original_filename: uploadResult.filename,
        file_size_bytes: uploadResult.size,
        config,
      });
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

  return (
    <div>
      <h2 className="mb-6 text-2xl font-bold">Upload Video</h2>
      <div className="grid gap-6 lg:grid-cols-2">
        <div>
          <DropZone onFileSelect={handleFileSelect} disabled={uploading} />
          {file && (
            <div
              className={`mt-4 rounded-lg border p-4 transition-colors ${
                uploadResult && !uploading
                  ? "border-green-300 bg-green-50"
                  : uploading
                    ? "border-blue-300 bg-blue-50"
                    : "border-border"
              }`}
            >
              <div className="flex items-center gap-3">
                <FileVideo className="h-6 w-6 shrink-0 text-muted-foreground" />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-base font-semibold">{file.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {formatFileSize(file.size)}
                  </p>
                </div>
                {uploadResult && !uploading && (
                  <span className="flex shrink-0 items-center gap-1 text-sm font-medium text-green-600">
                    <CheckCircle2 className="h-5 w-5" />
                    Uploaded
                  </span>
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
