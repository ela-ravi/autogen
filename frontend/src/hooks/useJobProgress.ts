"use client";

import { useEffect, useRef, useState } from "react";
import { JobWebSocket } from "@/lib/websocket";
import type { ProgressEvent } from "@/lib/types";

export function useJobProgress(jobId: string | null) {
  const [progress, setProgress] = useState<ProgressEvent | null>(null);
  const wsRef = useRef<JobWebSocket | null>(null);

  useEffect(() => {
    if (!jobId) return;

    const ws = new JobWebSocket(
      jobId,
      (data) => setProgress(data),
      () => setProgress(null)
    );
    ws.connect();
    wsRef.current = ws;

    return () => {
      ws.disconnect();
      wsRef.current = null;
    };
  }, [jobId]);

  return progress;
}
