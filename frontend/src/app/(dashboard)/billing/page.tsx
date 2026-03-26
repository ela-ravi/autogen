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
  const [billingEnabled, setBillingEnabled] = useState(true);
  const [disabledMessage, setDisabledMessage] = useState("");

  useEffect(() => {
    const meta = window.__meta__;
    if (meta) {
      setBillingEnabled(meta.enable_billing);
      setDisabledMessage(meta.billing_disabled_message || "");
    } else {
      const t = setTimeout(() => {
        const m = window.__meta__;
        if (m) {
          setBillingEnabled(m.enable_billing);
          setDisabledMessage(m.billing_disabled_message || "");
        }
      }, 2000);
      return () => clearTimeout(t);
    }
  }, []);

  useEffect(() => {
    if (billingEnabled) {
      api.get<UsageSummary>("/billing/usage").then(({ data }) => setUsage(data)).catch(() => {});
    }
  }, [billingEnabled]);

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

      <div className="relative">
        {/* Overlay with message when billing is disabled */}
        {!billingEnabled && (
          <div className="absolute inset-0 z-10 flex items-center justify-center rounded-lg bg-background/70 backdrop-blur-[2px]">
            <div className="rounded-lg border bg-background p-8 text-center shadow-lg">
              <p className="text-lg font-medium text-muted-foreground">
                {disabledMessage}
              </p>
            </div>
          </div>
        )}

        {/* Content — always rendered, grayed out when disabled */}
        <div className={!billingEnabled ? "pointer-events-none select-none opacity-40" : ""}>
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
      </div>
    </div>
  );
}
