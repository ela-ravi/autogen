"use client";

import { useState } from "react";
import { Download, FileJson, FileAudio, FileVideo, Sparkles } from "lucide-react";
import { toast } from "sonner";
import type { Job, IntermediateFile } from "@/lib/types";

type IntermediateKey =
  | "transcription"
  | "translation"
  | "recap_data"
  | "tts_audio"
  | "recap_video"
  | "emotions";

interface StepOutput {
  key: IntermediateKey;
  step: number | null; // null for emotions (sub-output of step 1)
  label: string;
  description: string;
  defaultFilename: string;
  icon: typeof FileJson;
  iconWrapClass: string;
}

const STEP_OUTPUTS: StepOutput[] = [
  {
    key: "transcription",
    step: 1,
    label: "Transcription",
    description: "Raw transcript with timing (JSON)",
    defaultFilename: "transcription.json",
    icon: FileJson,
    iconWrapClass: "bg-sky-100 text-sky-700 dark:bg-sky-950/60 dark:text-sky-300",
  },
  {
    key: "emotions",
    step: null,
    label: "Audio emotions",
    description: "Per-segment emotion analysis (JSON, PREMIUM)",
    defaultFilename: "emotions.json",
    icon: Sparkles,
    iconWrapClass:
      "bg-purple-100 text-purple-700 dark:bg-purple-950/60 dark:text-purple-300",
  },
  {
    key: "translation",
    step: 2,
    label: "Translation",
    description: "Translated transcript (JSON)",
    defaultFilename: "translated.json",
    icon: FileJson,
    iconWrapClass:
      "bg-indigo-100 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300",
  },
  {
    key: "recap_data",
    step: 3,
    label: "Recap plan",
    description: "Selected clips + narration text (JSON)",
    defaultFilename: "recap_data.json",
    icon: FileJson,
    iconWrapClass:
      "bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300",
  },
  {
    key: "tts_audio",
    step: 4,
    label: "Narration audio",
    description: "TTS-generated voiceover (MP3)",
    defaultFilename: "recap_narration.mp3",
    icon: FileAudio,
    iconWrapClass:
      "bg-rose-100 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300",
  },
  {
    key: "recap_video",
    step: 5,
    label: "Clipped video",
    description: "Concatenated clips, no narration (MP4)",
    defaultFilename: "recap_video.mp4",
    icon: FileVideo,
    iconWrapClass:
      "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300",
  },
];

interface StepOutputsPanelProps {
  job: Job;
  /** Async download triggered by the panel. Receives the API path and a default filename. */
  onDownload: (endpoint: string, filename: string) => Promise<void>;
}

export function StepOutputsPanel({ job, onDownload }: StepOutputsPanelProps) {
  const intermediates = job.intermediate_keys_detailed || {};
  const baseName = job.original_filename.replace(/\.[^.]+$/, "") || "recap";
  const [busyKey, setBusyKey] = useState<IntermediateKey | null>(null);

  const handleDownload = async (output: StepOutput, file: IntermediateFile) => {
    if (!file.download_url) {
      toast.error("Download URL is not available for this step");
      return;
    }
    setBusyKey(output.key);
    try {
      await onDownload(file.download_url, `${baseName}_${output.defaultFilename}`);
    } finally {
      setBusyKey(null);
    }
  };

  return (
    <div className="rounded-lg border p-4 sm:p-6">
      <div className="mb-3 flex items-center justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold">Step outputs</h3>
          <p className="mt-0.5 text-xs text-muted-foreground">
            Download each intermediate file produced during processing.
          </p>
        </div>
        <span className="rounded-full border border-amber-300 bg-amber-50 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide text-amber-800 dark:border-amber-900 dark:bg-amber-950/40 dark:text-amber-300">
          Debug
        </span>
      </div>

      <ul className="divide-y rounded-md border">
        {STEP_OUTPUTS.map((output) => {
          const file = intermediates[output.key] as IntermediateFile | undefined;
          const Icon = output.icon;
          const available = !!file && !!file.download_url;
          const busy = busyKey === output.key;

          return (
            <li
              key={output.key}
              className="flex items-center gap-3 px-3 py-2.5 sm:px-4"
            >
              <div
                className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-md ${output.iconWrapClass}`}
              >
                <Icon className="h-4 w-4" />
              </div>

              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-baseline gap-x-2">
                  <span className="text-sm font-medium">
                    {output.step !== null && (
                      <span className="text-muted-foreground">
                        Step {output.step}:{" "}
                      </span>
                    )}
                    {output.label}
                  </span>
                  {available && file?.size_mb != null && (
                    <span className="text-xs text-muted-foreground">
                      {file.size_mb} MB
                    </span>
                  )}
                </div>
                <p className="truncate text-xs text-muted-foreground">
                  {output.description}
                </p>
              </div>

              <button
                type="button"
                disabled={!available || busy}
                onClick={() => file && handleDownload(output, file)}
                className="flex shrink-0 items-center gap-1.5 rounded-md border border-primary/30 px-2.5 py-1.5 text-xs font-medium text-primary transition-colors hover:bg-primary/10 disabled:cursor-not-allowed disabled:border-muted disabled:text-muted-foreground disabled:hover:bg-transparent"
                title={
                  available
                    ? `Download ${output.label}`
                    : "Not generated for this job"
                }
              >
                <Download className={`h-3.5 w-3.5 ${busy ? "animate-pulse" : ""}`} />
                {busy ? "..." : available ? "Download" : "N/A"}
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
