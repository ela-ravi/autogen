"use client";

import "./globals.css";
import { AuthContext, useAuthProvider } from "@/lib/auth";
import { Toaster } from "sonner";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const auth = useAuthProvider();

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
