"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { useApiKeys } from "@/hooks/useApiKeys";
import { formatDate } from "@/lib/utils";
import { Copy, Key, Trash2 } from "lucide-react";

export default function ApiKeysPage() {
  const { keys, loading, fetchKeys, createKey, revokeKey, deleteKey } =
    useApiKeys();
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
    if (!confirm("Revoke this API key? It will immediately stop working."))
      return;
    try {
      await revokeKey(id);
      setNewKey(null);
      toast.success("API key revoked");
    } catch {
      toast.error("Failed to revoke key");
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Permanently delete this API key? This cannot be undone."))
      return;
    try {
      await deleteKey(id);
      toast.success("API key deleted");
    } catch {
      toast.error("Failed to delete key");
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard");
  };

  return (
    <div className="mx-auto max-w-3xl">
      <h2 className="mb-2 text-2xl font-bold">API Keys</h2>
      <p className="mb-6 text-sm text-muted-foreground">
        API keys let you access the Video Recap service programmatically
        (scripts, CLI, integrations) without logging in through the browser.
      </p>

      <div className="mb-6 rounded-lg border bg-secondary/30 p-4">
        <h4 className="mb-2 text-sm font-semibold">How to use</h4>
        <p className="mb-2 text-sm text-muted-foreground">
          Include your key in the{" "}
          <code className="rounded bg-secondary px-1.5 py-0.5 text-xs">
            X-API-Key
          </code>{" "}
          request header:
        </p>
        <code className="block rounded bg-secondary px-3 py-2 text-xs">
          curl -H &quot;X-API-Key: vra_your_key_here&quot;
          https://your-server/api/v1/jobs
        </code>
        <p className="mt-2 text-xs text-muted-foreground">
          This is not your OpenAI key. API keys authenticate you with the Video
          Recap service itself.
        </p>
      </div>

      {newKey && (
        <div className="mb-6 rounded-lg border border-green-200 bg-green-50 p-4">
          <p className="mb-2 text-sm font-medium text-green-800">
            Your new API key (copy it now — it won&apos;t be shown again):
          </p>
          <div className="flex items-center gap-2">
            <code className="flex-1 overflow-x-auto rounded bg-white px-3 py-2 text-sm">
              {newKey}
            </code>
            <button
              onClick={() => copyToClipboard(newKey)}
              className="shrink-0 rounded-md border p-2 hover:bg-white"
              title="Copy to clipboard"
            >
              <Copy className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

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
          {creating ? "Creating..." : "Create Key"}
        </button>
      </form>

      <h3 className="mb-3 text-sm font-semibold">Your Keys</h3>
      <div className="rounded-lg border">
        {loading ? (
          <div className="p-8 text-center text-muted-foreground">
            Loading...
          </div>
        ) : keys.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            No API keys yet. Create one above to get started.
          </div>
        ) : (
          <div className="divide-y">
            {keys.map((key) => (
              <div
                key={key.id}
                className="flex items-center justify-between p-4"
              >
                <div className="min-w-0">
                  <p className="font-medium">{key.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {key.key_prefix}... &middot; Created{" "}
                    {formatDate(key.created_at)}
                    {key.last_used_at &&
                      ` · Last used ${formatDate(key.last_used_at)}`}
                  </p>
                </div>
                <div className="flex shrink-0 items-center gap-2">
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs ${
                      key.is_active
                        ? "bg-green-100 text-green-800"
                        : "bg-red-100 text-red-700"
                    }`}
                  >
                    {key.is_active ? "Active" : "Revoked"}
                  </span>
                  {key.is_active ? (
                    <button
                      onClick={() => handleRevoke(key.id)}
                      className="rounded-md border p-1.5 text-destructive hover:bg-destructive/10"
                      title="Revoke key"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  ) : (
                    <button
                      onClick={() => handleDelete(key.id)}
                      className="rounded-md border p-1.5 text-muted-foreground hover:bg-secondary"
                      title="Delete key"
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
