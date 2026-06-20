"use client";

import { useState } from "react";
import { Download, ChevronDown, Lock, Info } from "lucide-react";
import { toast } from "sonner";
import type { Job, IntermediateFile } from "@/lib/types";
import api from "@/lib/api";

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

const STEP_DESCRIPTIONS = [
  "",
  "Extract speech and convert to text",
  "Translate transcription if needed",
  "Generate AI-powered video recap",
  "Generate voice narration audio",
  "Extract key clips from original video",
  "Remove original audio from video",
  "Merge video and narration audio",
];

const INTERMEDIATE_STEPS = [1, 2, 3, 4, 5];

interface IntermediateDownloadsProps {
  job: Job;
  activeStep: number;
  onDownload: (endpoint: string, filename: string) => Promise<void>;
}

export function IntermediateDownloads({
  job,
  activeStep,
  onDownload,
}: IntermediateDownloadsProps) {
  const [expandedDetails, setExpandedDetails] = useState<string | null>(null);

  if (!job.intermediate_keys_detailed) {
    return null;
  }

  const hasTranslation = job.config.translate_to !== null && job.config.translate_to !== undefined;

  const handleStepDownload = async (stepNum: number, intermediateKey: string) => {
    const intermediate = job.intermediate_keys_detailed?.[intermediateKey];
    if (!intermediate || !intermediate.download_url) {
      toast.error("Download link not available");
      return;
    }

    try {
      await onDownload(intermediate.download_url, `${job.id}_${intermediateKey}`);
    } catch {
      toast.error(`Failed to download ${intermediateKey}`);
    }
  };

  const getStepStatus = (stepNum: number): "completed" | "active" | "pending" => {
    if (stepNum < activeStep) return "completed";
    if (stepNum === activeStep) return "active";
    return "pending";
  };

  const getStatusColor = (status: "completed" | "active" | "pending") => {
    switch (status) {
      case "completed":
        return "bg-green-100 text-green-800 border-green-300";
      case "active":
        return "bg-blue-100 text-blue-800 border-blue-300";
      case "pending":
        return "bg-gray-100 text-gray-600 border-gray-300";
    }
  };

  const getStatusIcon = (status: "completed" | "active" | "pending") => {
    if (status === "completed") return "✓";
    if (status === "active") return "•";
    return "○";
  };

  const intermediateMap: Record<number, string> = {
    1: "transcription",
    2: "translation",
    3: "recap_data",
    4: "tts_audio",
    5: "recap_video",
  };

  return (
    <div className="rounded-lg border border-gray-200 p-4 sm:p-6">
      <h3 className="mb-1 text-lg font-semibold">Step-by-Step Outputs</h3>
      <p className="mb-4 text-sm text-gray-600">
        Download intermediate files from each processing step for debugging and inspection.
      </p>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3, 4, 5, 6, 7].map((step) => {
          const status = getStepStatus(step);
          const intermediateKey = intermediateMap[step as keyof typeof intermediateMap];
          const intermediate = intermediateKey ? job.intermediate_keys_detailed?.[intermediateKey] : null;
          const isTranslationDisabled = step === 2 && !hasTranslation;
          const canDownload = intermediate && INTERMEDIATE_STEPS.includes(step) && !isTranslationDisabled;

          return (
            <div
              key={step}
              className={`rounded-lg border-2 p-4 transition-all ${
                status === "completed"
                  ? "border-green-300 bg-green-50"
                  : status === "active"
                    ? "border-blue-300 bg-blue-50"
                    : "border-gray-300 bg-gray-50"
              }`}
            >
              <div className="mb-3 flex items-center gap-2">
                <div
                  className={`flex h-8 w-8 items-center justify-center rounded-full font-bold text-white ${
                    status === "completed"
                      ? "bg-green-500"
                      : status === "active"
                        ? "bg-blue-500"
                        : "bg-gray-400"
                  }`}
                >
                  {getStatusIcon(status)}
                </div>
                <h4 className="font-semibold text-gray-900">
                  Step {step}: {STEP_NAMES[step]}
                </h4>
              </div>

              <p className="mb-3 text-xs text-gray-600">{STEP_DESCRIPTIONS[step]}</p>

              {canDownload && intermediate && (
                <>
                  <div className="mb-3 space-y-1 text-xs text-gray-600">
                    <p>
                      <strong>File:</strong>{" "}
                      {intermediateKey === "transcription"
                        ? "transcription.json"
                        : intermediateKey === "translation"
                          ? "translation.json"
                          : intermediateKey === "recap_data"
                            ? "recap_data.json"
                            : intermediateKey === "tts_audio"
                              ? "narration.mp3"
                              : "recap_video.mp4"}
                    </p>
                    {intermediate.size_mb && (
                      <p>
                        <strong>Size:</strong> {intermediate.size_mb} MB
                      </p>
                    )}
                  </div>

                  {expandedDetails === intermediateKey && (
                    <div className="mb-3 rounded-md bg-gray-100 p-2 text-xs text-gray-700">
                      <p className="mb-1 break-all">
                        <strong>S3 Key:</strong> {intermediate.key}
                      </p>
                      <p>
                        <strong>Type:</strong> {intermediateKey}
                      </p>
                    </div>
                  )}

                  <div className="flex flex-col gap-2">
                    <button
                      onClick={() => handleStepDownload(step, intermediateKey)}
                      className="flex items-center justify-center gap-2 rounded-md bg-green-100 px-3 py-2 text-sm font-medium text-green-700 hover:bg-green-200"
                    >
                      <Download className="h-4 w-4" />
                      Download
                    </button>
                    <button
                      onClick={() =>
                        setExpandedDetails(expandedDetails === intermediateKey ? null : intermediateKey)
                      }
                      className="flex items-center justify-center gap-1 rounded-md border border-gray-300 px-3 py-1 text-xs text-gray-600 hover:bg-gray-100"
                    >
                      <Info className="h-3 w-3" />
                      {expandedDetails === intermediateKey ? "Hide" : "Details"}
                      <ChevronDown
                        className={`h-3 w-3 transition-transform ${
                          expandedDetails === intermediateKey ? "rotate-180" : ""
                        }`}
                      />
                    </button>
                  </div>
                </>
              )}

              {isTranslationDisabled && (
                <div className="flex flex-col gap-2">
                  <button disabled className="flex items-center justify-center gap-2 rounded-md bg-gray-100 px-3 py-2 text-sm font-medium text-gray-500">
                    <Lock className="h-4 w-4" />
                    Not Applicable
                  </button>
                  <p className="text-xs text-gray-600">Translation not enabled for this job</p>
                </div>
              )}

              {(step === 6 || step === 7) && (
                <div className="text-xs text-gray-600">
                  <p className="text-gray-500">No intermediate file (final processing step)</p>
                </div>
              )}

              {!canDownload && !isTranslationDisabled && step !== 6 && step !== 7 && (
                <button disabled className="w-full rounded-md bg-gray-100 px-3 py-2 text-sm font-medium text-gray-500">
                  <Lock className="mr-1 inline h-4 w-4" />
                  Not Available Yet
                </button>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
