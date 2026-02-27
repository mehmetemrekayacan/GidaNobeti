import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { AUTH_COOKIE_KEY } from './lib/utils/auth-constants';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get(AUTH_COOKIE_KEY)?.value;
  const isAuthenticated = !!token;

  const isDashboardRoute =
    pathname === '/dashboard' || pathname.startsWith('/dashboard/');
  const isLoginRoute = pathname === '/login';
  const isRootRoute = pathname === '/';

  if (!isAuthenticated && isDashboardRoute) {
    const loginUrl = request.nextUrl.clone();
    loginUrl.pathname = '/login';
    loginUrl.search = '';
    return NextResponse.redirect(loginUrl);
  }

  if (isAuthenticated && (isLoginRoute || isRootRoute)) {
    const dashboardUrl = request.nextUrl.clone();
    dashboardUrl.pathname = '/dashboard';
    dashboardUrl.search = '';
    return NextResponse.redirect(dashboardUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
