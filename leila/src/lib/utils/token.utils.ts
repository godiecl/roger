/**
 * Token utilities for validation and parsing
 */

/**
 * Decode JWT token (without verification - just parsing)
 */
export function parseJWT(token: string): any {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (e) {
    return null;
  }
}

/**
 * Check if token is expired
 */
export function isTokenExpired(token: string): boolean {
  const decoded = parseJWT(token);
  if (!decoded || !decoded.exp) {
    return true;
  }

  // Token expiration is in seconds, Date.now() is in milliseconds
  const expirationTime = decoded.exp * 1000;
  const currentTime = Date.now();

  // Consider expired if less than 5 minutes remaining
  const bufferTime = 5 * 60 * 1000; // 5 minutes
  return currentTime >= (expirationTime - bufferTime);
}

/**
 * Get token expiration time
 */
export function getTokenExpiration(token: string): Date | null {
  const decoded = parseJWT(token);
  if (!decoded || !decoded.exp) {
    return null;
  }
  return new Date(decoded.exp * 1000);
}

/**
 * Get time until token expires (in milliseconds)
 */
export function getTimeUntilExpiration(token: string): number {
  const expiration = getTokenExpiration(token);
  if (!expiration) {
    return 0;
  }
  return expiration.getTime() - Date.now();
}
