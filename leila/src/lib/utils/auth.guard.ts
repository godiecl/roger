/**
 * Route guard utility for protecting authenticated routes
 */
import { redirect } from '@sveltejs/kit';
import { browser } from '$app/environment';

/**
 * Check if user is authenticated
 * Should be used in +page.ts or +layout.ts load functions
 */
export function requireAuth(returnUrl?: string) {
  if (!browser) return;

  const authTokens = localStorage.getItem('auth_tokens');
  const authUser = localStorage.getItem('auth_user');

  if (!authTokens || !authUser) {
    // Not authenticated, redirect to login
    const loginUrl = returnUrl ? `/login?redirect=${encodeURIComponent(returnUrl)}` : '/login';
    throw redirect(307, loginUrl);
  }

  // Validate token expiration (basic check)
  try {
    const tokens = JSON.parse(authTokens);
    if (!tokens.access_token) {
      localStorage.removeItem('auth_tokens');
      localStorage.removeItem('auth_user');
      throw redirect(307, '/login');
    }
  } catch {
    localStorage.removeItem('auth_tokens');
    localStorage.removeItem('auth_user');
    throw redirect(307, '/login');
  }
}

/**
 * Check if user has required role
 */
export function requireRole(allowedRoles: string[]) {
  if (!browser) return;

  const authUser = localStorage.getItem('auth_user');

  if (!authUser) {
    throw redirect(307, '/login');
  }

  try {
    const user = JSON.parse(authUser);
    const userRole = user.role?.toLowerCase();

    if (!allowedRoles.map(r => r.toLowerCase()).includes(userRole)) {
      // User doesn't have required role, redirect to home
      throw redirect(307, '/');
    }
  } catch {
    throw redirect(307, '/login');
  }
}
