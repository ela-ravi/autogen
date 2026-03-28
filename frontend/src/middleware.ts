import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const protectedRoutes = ["/dashboard", "/upload", "/jobs", "/api-keys", "/billing", "/settings"];

function getBackendProxyBase(): string {
  if (process.env.BACKEND_INTERNAL_URL?.trim()) {
    return process.env.BACKEND_INTERNAL_URL.trim().replace(/\/$/, "");
  }
  if (process.env.NODE_ENV === "development") {
    return "http://127.0.0.1:8000";
  }
  return "";
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  /** Same-origin /api/v1 when NEXT_PUBLIC_API_URL is empty (e.g. Docker frontend) */
  if (pathname.startsWith("/api/v1")) {
    const backend = getBackendProxyBase();
    if (backend) {
      const target = new URL(pathname + request.nextUrl.search, backend);
      return NextResponse.rewrite(target);
    }
  }

  const token = request.cookies.get("access_token");

  const isProtected = protectedRoutes.some((route) => pathname.startsWith(route));

  if (isProtected && !token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // Redirect logged-in users away from auth pages
  if (token && (pathname === "/login" || pathname === "/signup")) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/api/v1/:path*",
    "/((?!api|_next/static|_next/image|favicon.ico).*)",
  ],
};
