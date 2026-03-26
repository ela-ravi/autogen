"use client";

import { useEffect } from "react";
import "./globals.css";
import { AuthContext, useAuthProvider } from "@/lib/auth";
import api from "@/lib/api";
import { Toaster } from "sonner";

declare global {
  interface Window {
    __meta__?: {
      version: string;
      enable_user_api_keys: boolean;
      api_key_restricted_to_emails: boolean;
      enable_api_keys_menu: boolean;
      enable_billing: boolean;
      billing_disabled_message: string | null;
    };
  }
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const auth = useAuthProvider();

  useEffect(() => {
    api
      .get("/meta")
      .then((res) => {
        window.__meta__ = res.data;
      })
      .catch(() => {});
  }, []);

  return (
    <html lang="en">
      <body className="min-h-screen antialiased">
        <AuthContext.Provider value={auth}>
          {children}
          <Toaster position="top-right" />
        </AuthContext.Provider>
      </body>
    </html>
  );
}
