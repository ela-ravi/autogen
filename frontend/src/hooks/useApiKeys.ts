"use client";

import { useCallback, useState } from "react";
import api from "@/lib/api";
import type { ApiKey, ApiKeyCreated } from "@/lib/types";

export function useApiKeys() {
  const [keys, setKeys] = useState<ApiKey[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchKeys = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await api.get<ApiKey[]>("/api-keys");
      setKeys(data);
    } finally {
      setLoading(false);
    }
  }, []);

  const createKey = useCallback(async (name: string): Promise<ApiKeyCreated> => {
    const { data } = await api.post<ApiKeyCreated>("/api-keys", { name });
    await fetchKeys();
    return data;
  }, [fetchKeys]);

  const revokeKey = useCallback(async (id: string) => {
    await api.delete(`/api-keys/${id}`);
    await fetchKeys();
  }, [fetchKeys]);

  return { keys, loading, fetchKeys, createKey, revokeKey };
}
