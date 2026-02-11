/**
 * Client-side Rate Limiter
 * Tracks and limits request frequency to prevent abuse
 */
import { browser } from '$app/environment';

interface RateLimitConfig {
  maxAttempts: number;
  windowMs: number;
  blockDurationMs?: number;
}

interface AttemptRecord {
  attempts: number;
  firstAttempt: number;
  blockedUntil?: number;
}

class RateLimiter {
  private records: Map<string, AttemptRecord> = new Map();

  /**
   * Check if an action is allowed
   */
  isAllowed(key: string, config: RateLimitConfig): boolean {
    if (!browser) return true;

    const now = Date.now();
    const record = this.records.get(key);

    // Check if blocked
    if (record?.blockedUntil && now < record.blockedUntil) {
      return false;
    }

    // Check if window has expired
    if (record && (now - record.firstAttempt) > config.windowMs) {
      // Reset the record
      this.records.delete(key);
      return true;
    }

    // Check attempts
    if (record && record.attempts >= config.maxAttempts) {
      // Block the key
      const blockUntil = now + (config.blockDurationMs || config.windowMs);
      this.records.set(key, {
        ...record,
        blockedUntil: blockUntil
      });
      return false;
    }

    return true;
  }

  /**
   * Record an attempt
   */
  recordAttempt(key: string): void {
    if (!browser) return;

    const now = Date.now();
    const record = this.records.get(key);

    if (record) {
      this.records.set(key, {
        ...record,
        attempts: record.attempts + 1
      });
    } else {
      this.records.set(key, {
        attempts: 1,
        firstAttempt: now
      });
    }
  }

  /**
   * Get remaining time until unblocked (in ms)
   */
  getBlockTimeRemaining(key: string): number {
    if (!browser) return 0;

    const record = this.records.get(key);
    if (!record?.blockedUntil) return 0;

    const remaining = record.blockedUntil - Date.now();
    return Math.max(0, remaining);
  }

  /**
   * Get number of attempts
   */
  getAttempts(key: string): number {
    return this.records.get(key)?.attempts || 0;
  }

  /**
   * Reset attempts for a key
   */
  reset(key: string): void {
    this.records.delete(key);
  }

  /**
   * Clear all records
   */
  clearAll(): void {
    this.records.clear();
  }
}

export const rateLimiter = new RateLimiter();

// Pre-configured limiters
export const loginRateLimiter = {
  check: () => rateLimiter.isAllowed('login', {
    maxAttempts: 5,
    windowMs: 15 * 60 * 1000, // 15 minutes
    blockDurationMs: 30 * 60 * 1000 // 30 minutes block
  }),
  record: () => rateLimiter.recordAttempt('login'),
  getBlockTime: () => rateLimiter.getBlockTimeRemaining('login'),
  getAttempts: () => rateLimiter.getAttempts('login'),
  reset: () => rateLimiter.reset('login')
};

export const registerRateLimiter = {
  check: () => rateLimiter.isAllowed('register', {
    maxAttempts: 3,
    windowMs: 60 * 60 * 1000, // 1 hour
    blockDurationMs: 2 * 60 * 60 * 1000 // 2 hours block
  }),
  record: () => rateLimiter.recordAttempt('register'),
  getBlockTime: () => rateLimiter.getBlockTimeRemaining('register'),
  getAttempts: () => rateLimiter.getAttempts('register'),
  reset: () => rateLimiter.reset('register')
};
