import { NextRequest, NextResponse } from 'next/server';

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Skip middleware for static files and API routes
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api') ||
    pathname.includes('.') // Static files
  ) {
    return NextResponse.next();
  }

  // Public routes that don't require authentication
  const publicRoutes = ['/', '/tenant-select', '/test-api'];
  
  // Allow all routes for now (development mode)
  // In production, add authentication checks here
  return NextResponse.next();
}

function extractTenantFromHostname(hostname: string): { subdomain?: string; domain?: string } {
  // Skip localhost and IP addresses
  if (hostname === 'localhost' || /^\d+\.\d+\.\d+\.\d+$/.test(hostname)) {
    return {};
  }

  const parts = hostname.split('.');
  
  // If it's a subdomain (e.g., demo.hse-system.com)
  if (parts.length >= 3) {
    return {
      subdomain: parts[0],
      domain: hostname
    };
  }

  // If it's a direct domain
  return { domain: hostname };
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};