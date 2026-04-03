"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { Suspense, useCallback, useEffect, useRef, useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { toast } from "sonner";

function VerifyOTPContent() {
  const searchParams = useSearchParams();
  const email = searchParams.get("email") || "";
  const router = useRouter();
  const { verifyOtp, resendOtp } = useAuth();

  const [digits, setDigits] = useState<string[]>(Array(6).fill(""));
  const [loading, setLoading] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  useEffect(() => {
    if (!email) router.replace("/signup");
  }, [email, router]);

  useEffect(() => {
    if (resendCooldown <= 0) return;
    const t = setTimeout(() => setResendCooldown((c) => c - 1), 1000);
    return () => clearTimeout(t);
  }, [resendCooldown]);

  const submitCode = useCallback(
    async (code: string) => {
      setLoading(true);
      try {
        await verifyOtp(email, code);
        toast.success("Email verified!");
        router.push("/dashboard");
      } catch {
        toast.error("Invalid or expired code");
        setDigits(Array(6).fill(""));
        inputRefs.current[0]?.focus();
      } finally {
        setLoading(false);
      }
    },
    [email, verifyOtp, router]
  );

  const handleChange = (idx: number, value: string) => {
    if (!/^\d*$/.test(value)) return;
    const next = [...digits];
    next[idx] = value.slice(-1);
    setDigits(next);

    if (value && idx < 5) {
      inputRefs.current[idx + 1]?.focus();
    }

    const code = next.join("");
    if (code.length === 6 && next.every(Boolean)) {
      submitCode(code);
    }
  };

  const handleKeyDown = (idx: number, e: React.KeyboardEvent) => {
    if (e.key === "Backspace" && !digits[idx] && idx > 0) {
      inputRefs.current[idx - 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    e.preventDefault();
    const pasted = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, 6);
    if (!pasted) return;
    const next = Array(6).fill("");
    for (let i = 0; i < pasted.length; i++) next[i] = pasted[i];
    setDigits(next);
    if (pasted.length === 6) submitCode(pasted);
    else inputRefs.current[pasted.length]?.focus();
  };

  const handleResend = async () => {
    try {
      await resendOtp(email);
      toast.success("New code sent");
      setResendCooldown(60);
    } catch {
      toast.error("Failed to resend code");
    }
  };

  if (!email) return null;

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="w-full max-w-md rounded-lg border p-8 text-center">
        <h2 className="mb-2 text-2xl font-bold">Verify your email</h2>
        <p className="mb-6 text-sm text-muted-foreground">
          We sent a 6-digit code to{" "}
          <span className="font-medium text-foreground">{email}</span>
        </p>

        <div className="mb-6 flex justify-center gap-2" onPaste={handlePaste}>
          {digits.map((d, i) => (
            <input
              key={i}
              ref={(el) => { inputRefs.current[i] = el; }}
              type="text"
              inputMode="numeric"
              maxLength={1}
              value={d}
              onChange={(e) => handleChange(i, e.target.value)}
              onKeyDown={(e) => handleKeyDown(i, e)}
              disabled={loading}
              className="h-12 w-12 rounded-md border text-center text-xl font-semibold focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20 disabled:opacity-50"
              autoFocus={i === 0}
            />
          ))}
        </div>

        {loading && (
          <p className="mb-4 text-sm text-muted-foreground">Verifying...</p>
        )}

        <button
          onClick={handleResend}
          disabled={resendCooldown > 0}
          className="text-sm text-primary hover:underline disabled:text-muted-foreground disabled:no-underline"
        >
          {resendCooldown > 0
            ? `Resend code in ${resendCooldown}s`
            : "Resend code"}
        </button>
      </div>
    </div>
  );
}

export default function VerifyPage() {
  return (
    <Suspense>
      <VerifyOTPContent />
    </Suspense>
  );
}
