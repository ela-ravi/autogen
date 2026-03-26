"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { useAuth } from "@/hooks/useAuth";
import api from "@/lib/api";
import type { FeatureFlags } from "@/lib/types";
import { formatDate } from "@/lib/utils";

function OpenAIKeySection({ hasKey }: { hasKey: boolean }) {
  const [key, setKey] = useState("");
  const [saving, setSaving] = useState(false);
  const [removing, setRemoving] = useState(false);
  const [saved, setSaved] = useState(hasKey);

  const handleSave = async () => {
    if (!key.trim()) {
      toast.error("API key cannot be empty");
      return;
    }
    setSaving(true);
    try {
      await api.put("/auth/me/openai-key", { openai_api_key: key.trim() });
      toast.success("OpenAI API key saved");
      setSaved(true);
      setKey("");
    } catch {
      toast.error("Failed to save API key");
    } finally {
      setSaving(false);
    }
  };

  const handleRemove = async () => {
    setRemoving(true);
    try {
      await api.delete("/auth/me/openai-key");
      toast.success("OpenAI API key removed");
      setSaved(false);
    } catch {
      toast.error("Failed to remove API key");
    } finally {
      setRemoving(false);
    }
  };

  return (
    <div className="rounded-lg border p-6">
      <h3 className="mb-1 font-semibold">OpenAI API Key</h3>
      <p className="mb-4 text-sm text-muted-foreground">
        Your key is encrypted at rest and used for transcription, recap
        generation, and narration.
      </p>

      <div className="mb-3 flex items-center gap-2 text-sm">
        <span
          className={`inline-block h-2 w-2 rounded-full ${saved ? "bg-green-500" : "bg-red-500"}`}
        />
        <span className={saved ? "text-green-700" : "text-red-700"}>
          {saved ? "Key saved" : "Key required"}
        </span>
      </div>

      <div className="flex gap-2">
        <input
          type="password"
          value={key}
          onChange={(e) => setKey(e.target.value)}
          placeholder={saved ? "Enter new key to replace" : "sk-..."}
          className="flex-1 rounded-md border px-3 py-2 text-sm"
        />
        <button
          onClick={handleSave}
          disabled={saving || !key.trim()}
          className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:opacity-90 disabled:opacity-50"
        >
          {saving ? "Saving..." : saved ? "Update" : "Save"}
        </button>
      </div>

      {saved && (
        <button
          onClick={handleRemove}
          disabled={removing}
          className="mt-3 text-sm text-red-600 hover:underline disabled:opacity-50"
        >
          {removing ? "Removing..." : "Remove saved key"}
        </button>
      )}
    </div>
  );
}

export default function SettingsPage() {
  const { user } = useAuth();
  const [flags, setFlags] = useState<FeatureFlags | null>(null);

  useEffect(() => {
    api
      .get<FeatureFlags>("/auth/feature-flags")
      .then((res) => setFlags(res.data))
      .catch(() => setFlags({ requires_api_key: false }));
  }, []);

  if (!user) return null;

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h2 className="text-2xl font-bold">Settings</h2>

      <div className="rounded-lg border p-6">
        <h3 className="mb-4 font-semibold">Profile</h3>
        <dl className="space-y-4 text-sm">
          <div>
            <dt className="text-muted-foreground">Name</dt>
            <dd className="font-medium">{user.full_name}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Email</dt>
            <dd className="font-medium">{user.email}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Auth Provider</dt>
            <dd className="font-medium capitalize">{user.auth_provider}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Plan</dt>
            <dd className="font-medium capitalize">{user.tier}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Member Since</dt>
            <dd className="font-medium">{formatDate(user.created_at)}</dd>
          </div>
        </dl>
      </div>

      {flags?.requires_api_key && (
        <OpenAIKeySection hasKey={user.has_openai_key} />
      )}
    </div>
  );
}
