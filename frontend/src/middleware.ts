import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { getToken } from 'next-auth/jwt';

export async function middleware(request: NextRequest) {
  const path = request.nextUrl.pathname;
  const token = await getToken({ req: request, secret: process.env.NEXTAUTH_SECRET });

  // Public paths that don't require authentication
  const publicPaths = ['/', '/auth', '/features', '/guide', '/pricing'];
  const isPublicPath = publicPaths.includes(path);

  // Check if the path starts with /dashboard
  const isDashboardPath = path.startsWith('/dashboard');

  // If user is not authenticated and trying to access dashboard
  if (!token && isDashboardPath) {
    return NextResponse.redirect(new URL('/auth', request.url));
  }

  // If user is authenticated and trying to access auth page
  if (token && path === '/auth') {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  // If user is authenticated and on home page, redirect to dashboard
  if (token && path === '/') {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  // Continue with the request
  return NextResponse.next();
}

// Configure which paths the middleware should run on
export const config = {
  matcher: ['/', '/auth', '/dashboard/:path*']
}; 