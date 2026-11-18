import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const PUBLIC_PATHS = ["/", "/login", "/signup", "/about", "/forgot-password", "/privacy", "/terms"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Public pages — always accessible
  if (PUBLIC_PATHS.includes(pathname) || pathname.startsWith("/book/")) {
    return NextResponse.next();
  }

  // Protected pages — check for auth token in cookie
  const token = request.cookies.get("pp_token")?.value;
  if (!token) {
    // Check if this is a client-side navigation right after login/signup
    // The cookie might not have been sent yet on the first redirect
    // Let the client-side auth context handle the redirect instead
    const referer = request.headers.get("referer") || "";
    const isPostAuth = referer.includes("/login") || referer.includes("/signup");
    if (isPostAuth) {
      // Allow the request — the client-side auth will handle redirection
      return NextResponse.next();
    }

    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/((?!api|_next/static|_next/image|favicon.ico|favicon.svg|sitemap.xml|robots.txt|google.*\\.html).*)",
  ],
};
