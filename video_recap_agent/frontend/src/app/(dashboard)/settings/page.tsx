"use client";

import { useAuth } from "@/hooks/useAuth";
import { formatDate } from "@/lib/utils";

export default function SettingsPage() {
  const { user } = useAuth();

  if (!user) return null;

  return (
    <div className="mx-auto max-w-2xl">
      <h2 className="mb-6 text-2xl font-bold">Settings</h2>

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
    </div>
  );
}
