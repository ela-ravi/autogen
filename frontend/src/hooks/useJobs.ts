"use client";

import { useCallback, useState } from "react";
import api from "@/lib/api";
import type { Job, JobListResponse } from "@/lib/types";

export function useJobs() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);

  const fetchJobs = useCallback(
    async (page = 1, status?: string) => {
      setLoading(true);
      try {
        const params: Record<string, string | number> = { page };
        if (status) params.status = status;
        const { data } = await api.get<JobListResponse>("/jobs", { params });
        setJobs(data.items);
        setTotal(data.total);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const getJob = useCallback(async (id: string): Promise<Job> => {
    const { data } = await api.get<Job>(`/jobs/${id}`);
    return data;
  }, []);

  const deleteJob = useCallback(async (id: string) => {
    await api.delete(`/jobs/${id}`);
  }, []);

  const getDownloadUrl = useCallback(
    async (id: string): Promise<string> => {
      const { data } = await api.get<{ download_url: string }>(
        `/jobs/${id}/download`
      );
      return data.download_url;
    },
    []
  );

  const resumeJob = useCallback(async (id: string): Promise<Job> => {
    const { data } = await api.post<Job>(`/jobs/${id}/resume`);
    return data;
  }, []);

  return { jobs, total, loading, fetchJobs, getJob, deleteJob, getDownloadUrl, resumeJob };
}
