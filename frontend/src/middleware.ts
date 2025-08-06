import { NextRequest, NextResponse } from 'next/server';

export async function middleware(request: NextRequest) {
  const { pathname, hostname } = request.nextUrl;
  
  // Skip middleware for static files and API routes
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api') ||
    pathname.includes('.') // Static files
  ) {
    return NextResponse.next();
  }

  // Extract tenant info from hostname
  const tenantInfo = extractTenantFromHostname(hostname);
  
  // Public routes that don't require tenant
  const publicRoutes = ['/tenant-select', '/health', '/'];
  if (publicRoutes.includes(pathname)) {
    return NextResponse.next();
  }

  // If tenant is detected from subdomain, store it in headers
  if (tenantInfo.subdomain || tenantInfo.domain) {
    const response = NextResponse.next();
    
    if (tenantInfo.subdomain) {
      response.headers.set('X-Tenant-Subdomain', tenantInfo.subdomain);
    }
    
    if (tenantInfo.domain) {
      response.headers.set('X-Tenant-Domain', tenantInfo.domain);
    }
    
    return response;
  }

  // If no tenant detected and not on tenant selection page, redirect
  if (!pathname.startsWith('/tenant-select')) {
    const url = request.nextUrl.clone();
    url.pathname = '/tenant-select';
    return NextResponse.redirect(url);
  }

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