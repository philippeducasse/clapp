import { NextResponse, NextRequest } from "next/server";

export const middleware = (request: NextRequest) => {
  const sessionid = request.cookies.get("sessionid");
  const { pathname } = request.nextUrl;
  if (sessionid && (pathname === "/" || pathname.startsWith("/login") || pathname.startsWith("/register"))) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }
  if (!sessionid && pathname !== "/" && !pathname.startsWith("/login") && !pathname.startsWith("/register")) {
    return NextResponse.redirect(new URL("/", request.url));
  }
  return NextResponse.next();
};

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico|logo.png).*)"],
};
