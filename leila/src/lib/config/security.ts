/**
 * Security Configuration
 * Environment-specific security settings
 */
import { browser } from '$app/environment';
import { dev } from '$app/environment';

export const securityConfig = {
  // Force HTTPS in production
  forceHttps: !dev,

  // Session timeout (30 minutes)
  sessionTimeout: 30 * 60 * 1000,

  // Token refresh buffer (refresh 5 minutes before expiration)
  tokenRefreshBuffer: 5 * 60 * 1000,

  // Rate limiting
  rateLimit: {
    login: {
      maxAttempts: 5,
      windowMs: 15 * 60 * 1000, // 15 minutes
      blockDurationMs: 30 * 60 * 1000 // 30 minutes
    },
    register: {
      maxAttempts: 3,
      windowMs: 60 * 60 * 1000, // 1 hour
      blockDurationMs: 2 * 60 * 60 * 1000 // 2 hours
    }
  },

  // Password requirements
  password: {
    minLength: 8,
    requireUppercase: false,
    requireLowercase: true,
    requireNumbers: true,
    requireSpecialChars: false
  },

  // Content Security Policy headers (for production)
  csp: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'", "'unsafe-inline'"], // Remove unsafe-inline in production
    styleSrc: ["'self'", "'unsafe-inline'"], // Remove unsafe-inline in production
    imgSrc: ["'self'", 'data:', 'https:'],
    fontSrc: ["'self'", 'data:'],
    connectSrc: ["'self'", process.env.VITE_API_URL || 'http://localhost:8000']
  }
};

/**
 * Enforce HTTPS in production
 */
export function enforceHttps() {
  if (!browser || dev) return;

  if (window.location.protocol !== 'https:') {
    console.warn('Redirecting to HTTPS...');
    window.location.href = window.location.href.replace('http://', 'https://');
  }
}

/**
 * Set secure cookie (helper for future implementation)
 */
export function setSecureCookie(name: string, value: string, days: number = 7) {
  if (!browser) return;

  const expires = new Date();
  expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);

  const secure = !dev ? '; Secure' : '';
  const sameSite = '; SameSite=Strict';
  const httpOnly = ''; // Can't set HttpOnly from JavaScript

  document.cookie = `${name}=${value}; expires=${expires.toUTCString()}; path=/${secure}${sameSite}`;
}

/**
 * Validate password strength
 */
export function validatePasswordStrength(password: string): {
  valid: boolean;
  errors: string[];
  strength: 'weak' | 'medium' | 'strong';
} {
  const errors: string[] = [];
  const config = securityConfig.password;

  if (password.length < config.minLength) {
    errors.push(`La contraseña debe tener al menos ${config.minLength} caracteres`);
  }

  if (config.requireUppercase && !/[A-Z]/.test(password)) {
    errors.push('La contraseña debe contener al menos una letra mayúscula');
  }

  if (config.requireLowercase && !/[a-z]/.test(password)) {
    errors.push('La contraseña debe contener al menos una letra minúscula');
  }

  if (config.requireNumbers && !/\d/.test(password)) {
    errors.push('La contraseña debe contener al menos un número');
  }

  if (config.requireSpecialChars && !/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
    errors.push('La contraseña debe contener al menos un carácter especial');
  }

  // Calculate strength
  let strength: 'weak' | 'medium' | 'strong' = 'weak';
  let score = 0;

  if (password.length >= 8) score++;
  if (password.length >= 12) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/[a-z]/.test(password)) score++;
  if (/\d/.test(password)) score++;
  if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) score++;

  if (score <= 2) strength = 'weak';
  else if (score <= 4) strength = 'medium';
  else strength = 'strong';

  return {
    valid: errors.length === 0,
    errors,
    strength
  };
}
