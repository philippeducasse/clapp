import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export const middleware = (request: NextRequest) => {
  const sessionid = request.cookies.get("sessionid");
  const { pathname } = request.nextUrl;
  console.log("sessionId", sessionid);
  if (sessionid && (pathname.startsWith("/login") || pathname.startsWith("/register"))) {
    console.log("redirecting to root");
    return NextResponse.redirect(new URL("/", request.url));
  }
  if (!sessionid && !pathname.startsWith("/login") && !pathname.startsWith("/register")) {
    console.log("redirecting to login");
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
};

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
