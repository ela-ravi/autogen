"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import api from "@/lib/api";
import type { UsageSummary } from "@/lib/types";

const tiers = [
  {
    name: "Free",
    price: "$0/mo",
    limit: 3,
    features: ["Basic voices", "30s max", "7-day retention"],
  },
  {
    name: "Pro",
    price: "$19/mo",
    limit: 50,
    features: ["All voices", "HD TTS", "120s max", "30-day retention", "Translation"],
  },
  {
    name: "Enterprise",
    price: "$99/mo",
    limit: -1,
    features: ["Unlimited recaps", "Priority queue", "90-day retention", "Dedicated support"],
  },
];

export default function BillingPage() {
  const { user } = useAuth();
  const [usage, setUsage] = useState<UsageSummary | null>(null);

  useEffect(() => {
    api.get<UsageSummary>("/billing/usage").then(({ data }) => setUsage(data)).catch(() => {});
  }, []);

  const handleUpgrade = async (tierName: string) => {
    try {
      const { data } = await api.post<{ checkout_url: string }>("/billing/checkout", {
        tier: tierName.toLowerCase(),
      });
      window.location.href = data.checkout_url;
    } catch {
      // Billing not set up yet
    }
  };

  return (
    <div className="mx-auto max-w-4xl">
      <h2 className="mb-6 text-2xl font-bold">Billing</h2>

      {/* Current usage */}
      {usage && (
        <div className="mb-8 rounded-lg border p-6">
          <h3 className="mb-4 font-semibold">Current Usage</h3>
          <div className="mb-2 flex justify-between text-sm">
            <span>
              {usage.used} / {usage.limit === -1 ? "Unlimited" : usage.limit} recaps
              this month
            </span>
            <span className="font-medium capitalize">{usage.tier} plan</span>
          </div>
          {usage.limit !== -1 && (
            <div className="h-2 rounded-full bg-secondary">
              <div
                className="h-2 rounded-full bg-blue-600"
                style={{
                  width: `${Math.min(100, (usage.used / usage.limit) * 100)}%`,
                }}
              />
            </div>
          )}
        </div>
      )}

      {/* Plans */}
      <div className="grid gap-6 md:grid-cols-3">
        {tiers.map((tier) => {
          const isCurrent = user?.tier === tier.name.toLowerCase();
          return (
            <div
              key={tier.name}
              className={`rounded-lg border p-6 ${
                isCurrent ? "border-blue-600 ring-2 ring-blue-600" : ""
              }`}
            >
              <h4 className="text-xl font-bold">{tier.name}</h4>
              <p className="text-2xl font-bold">{tier.price}</p>
              <p className="mb-4 text-sm text-muted-foreground">
                {tier.limit === -1 ? "Unlimited" : tier.limit} recaps/month
              </p>
              <ul className="mb-6 space-y-2">
                {tier.features.map((f) => (
                  <li key={f} className="flex items-center text-sm">
                    <span className="mr-2 text-green-600">✓</span>
                    {f}
                  </li>
                ))}
              </ul>
              {isCurrent ? (
                <button
                  disabled
                  className="w-full rounded-md border py-2 text-sm opacity-50"
                >
                  Current Plan
                </button>
              ) : (
                <button
                  onClick={() => handleUpgrade(tier.name)}
                  className="w-full rounded-md bg-primary py-2 text-sm text-primary-foreground hover:opacity-90"
                >
                  {tier.name === "Free" ? "Downgrade" : "Upgrade"}
                </button>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
