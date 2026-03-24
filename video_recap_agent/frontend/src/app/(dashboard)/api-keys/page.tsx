"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { useApiKeys } from "@/hooks/useApiKeys";
import { formatDate } from "@/lib/utils";
import { Copy, Key, Trash2 } from "lucide-react";

export default function ApiKeysPage() {
  const { keys, loading, fetchKeys, createKey, revokeKey } = useApiKeys();
  const [name, setName] = useState("");
  const [newKey, setNewKey] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    fetchKeys();
  }, [fetchKeys]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setCreating(true);
    try {
      const result = await createKey(name.trim());
      setNewKey(result.key);
      setName("");
      toast.success("API key created");
    } catch {
      toast.error("Failed to create API key");
    } finally {
      setCreating(false);
    }
  };

  const handleRevoke = async (id: string) => {
    if (!confirm("Revoke this API key? This action cannot be undone.")) return;
    try {
      await revokeKey(id);
      toast.success("API key revoked");
    } catch {
      toast.error("Failed to revoke key");
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard");
  };

  return (
    <div className="mx-auto max-w-3xl">
      <h2 className="mb-6 text-2xl font-bold">API Keys</h2>
      <p className="mb-6 text-sm text-muted-foreground">
        Use API keys to authenticate requests to the Video Recap API. Include the
        key in the <code className="rounded bg-secondary px-1">X-API-Key</code>{" "}
        header.
      </p>

      {/* New key display */}
      {newKey && (
        <div className="mb-6 rounded-lg border border-green-200 bg-green-50 p-4">
          <p className="mb-2 text-sm font-medium text-green-800">
            Your new API key (copy it now - it won't be shown again):
          </p>
          <div className="flex items-center gap-2">
            <code className="flex-1 rounded bg-white px-3 py-2 text-sm">
              {newKey}
            </code>
            <button
              onClick={() => copyToClipboard(newKey)}
              className="rounded-md border p-2 hover:bg-white"
            >
              <Copy className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      {/* Create form */}
      <form onSubmit={handleCreate} className="mb-8 flex gap-2">
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Key name (e.g. CLI, Production)"
          className="flex-1 rounded-md border px-3 py-2 text-sm"
        />
        <button
          type="submit"
          disabled={creating || !name.trim()}
          className="flex items-center gap-1 rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:opacity-90 disabled:opacity-50"
        >
          <Key className="h-4 w-4" />
          Create Key
        </button>
      </form>

      {/* Keys list */}
      <div className="rounded-lg border">
        {loading ? (
          <div className="p-8 text-center text-muted-foreground">Loading...</div>
        ) : keys.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            No API keys yet.
          </div>
        ) : (
          <div className="divide-y">
            {keys.map((key) => (
              <div key={key.id} className="flex items-center justify-between p-4">
                <div>
                  <p className="font-medium">{key.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {key.key_prefix}... &middot;{" "}
                    {key.last_used_at
                      ? `Last used ${formatDate(key.last_used_at)}`
                      : "Never used"}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs ${
                      key.is_active
                        ? "bg-green-100 text-green-800"
                        : "bg-gray-100 text-gray-500"
                    }`}
                  >
                    {key.is_active ? "Active" : "Revoked"}
                  </span>
                  {key.is_active && (
                    <button
                      onClick={() => handleRevoke(key.id)}
                      className="rounded-md border p-1.5 text-destructive hover:bg-destructive/10"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
