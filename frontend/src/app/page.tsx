"use client";

import Link from "next/link";
import { Play, Zap, Shield, Globe } from "lucide-react";

const features = [
  {
    icon: Play,
    title: "AI Video Recaps",
    description: "Transform long videos into concise, narrated recaps using AI.",
  },
  {
    icon: Zap,
    title: "Fast Processing",
    description: "Powered by Whisper, GPT-4, and OpenAI TTS for rapid results.",
  },
  {
    icon: Shield,
    title: "Developer API",
    description: "Integrate video recaps into your own apps with our REST API.",
  },
  {
    icon: Globe,
    title: "Multi-Language",
    description: "Transcribe and translate videos across multiple languages.",
  },
];

const tiers = [
  {
    name: "Free",
    price: "$0",
    limit: "3 recaps/month",
    features: ["Basic voices", "30s max duration", "7-day file retention"],
  },
  {
    name: "Pro",
    price: "$19",
    limit: "50 recaps/month",
    features: ["All voices", "HD TTS", "120s max", "30-day retention", "Translation"],
    popular: true,
  },
  {
    name: "Enterprise",
    price: "$99",
    limit: "Unlimited recaps",
    features: ["Priority queue", "Custom branding", "90-day retention", "Dedicated support"],
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto flex items-center justify-between px-6 py-4">
          <h1 className="text-xl font-bold">Video Recap Agent</h1>
          <div className="flex gap-4">
            <Link href="/login" className="px-4 py-2 text-sm hover:underline">
              Log in
            </Link>
            <Link
              href="/signup"
              className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:opacity-90"
            >
              Sign up free
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="py-24 text-center">
        <div className="container mx-auto px-6">
          <h2 className="text-5xl font-bold tracking-tight">
            Turn Long Videos into
            <br />
            <span className="text-blue-600">AI-Narrated Recaps</span>
          </h2>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground">
            Upload any video and get a short, professional recap with AI-generated
            narration. Perfect for meetings, lectures, and content creation.
          </p>
          <div className="mt-10 flex justify-center gap-4">
            <Link
              href="/signup"
              className="rounded-md bg-primary px-8 py-3 text-primary-foreground hover:opacity-90"
            >
              Get Started Free
            </Link>
            <Link
              href="#pricing"
              className="rounded-md border px-8 py-3 hover:bg-secondary"
            >
              View Pricing
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="border-t py-20">
        <div className="container mx-auto px-6">
          <h3 className="mb-12 text-center text-3xl font-bold">How It Works</h3>
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
            {features.map((f) => (
              <div key={f.title} className="rounded-lg border p-6">
                <f.icon className="mb-4 h-8 w-8 text-blue-600" />
                <h4 className="mb-2 text-lg font-semibold">{f.title}</h4>
                <p className="text-sm text-muted-foreground">{f.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="border-t py-20">
        <div className="container mx-auto px-6">
          <h3 className="mb-12 text-center text-3xl font-bold">Pricing</h3>
          <div className="grid gap-8 md:grid-cols-3">
            {tiers.map((tier) => (
              <div
                key={tier.name}
                className={`rounded-lg border p-8 ${
                  tier.popular ? "border-blue-600 ring-2 ring-blue-600" : ""
                }`}
              >
                {tier.popular && (
                  <span className="mb-4 inline-block rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-800">
                    Most Popular
                  </span>
                )}
                <h4 className="text-2xl font-bold">{tier.name}</h4>
                <p className="mt-2 text-3xl font-bold">
                  {tier.price}
                  <span className="text-sm font-normal text-muted-foreground">
                    /month
                  </span>
                </p>
                <p className="mt-1 text-sm text-muted-foreground">{tier.limit}</p>
                <ul className="mt-6 space-y-3">
                  {tier.features.map((f) => (
                    <li key={f} className="flex items-center text-sm">
                      <span className="mr-2 text-green-600">✓</span>
                      {f}
                    </li>
                  ))}
                </ul>
                <Link
                  href="/signup"
                  className="mt-8 block w-full rounded-md border py-2 text-center text-sm hover:bg-secondary"
                >
                  Get Started
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-8 text-center text-sm text-muted-foreground">
        <p>Video Recap Agent — AI-powered video summarization</p>
      </footer>
    </div>
  );
}
