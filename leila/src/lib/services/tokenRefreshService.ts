/**
 * Token Refresh Service
 * Automatically refreshes access tokens before they expire
 */
import { browser } from '$app/environment';
import { authStore } from '$lib/stores/auth';
import { activityTracker } from './activityTracker';
import { getTimeUntilExpiration, isTokenExpired } from '$lib/utils/token.utils';
import { apiClient } from './apiClient';
import type { AuthTokens } from '$lib/types';

class TokenRefreshService {
  private refreshTimer: number | null = null;
  private isRefreshing = false;

  /**
   * Start automatic token refresh
   */
  start() {
    if (!browser) return;

    this.scheduleRefresh();
  }

  /**
   * Stop automatic token refresh
   */
  stop() {
    if (this.refreshTimer) {
      clearTimeout(this.refreshTimer);
      this.refreshTimer = null;
    }
    this.isRefreshing = false;
  }

  /**
   * Schedule the next token refresh
   */
  private scheduleRefresh() {
    if (this.refreshTimer) {
      clearTimeout(this.refreshTimer);
    }

    authStore.subscribe(auth => {
      if (!auth.tokens?.access_token) {
        return;
      }

      const timeUntilExpiration = getTimeUntilExpiration(auth.tokens.access_token);

      // Refresh 5 minutes before expiration
      const refreshTime = Math.max(timeUntilExpiration - (5 * 60 * 1000), 60000); // At least 1 minute

      this.refreshTimer = setTimeout(() => {
        this.checkAndRefresh();
      }, refreshTime) as unknown as number;
    })();
  }

  /**
   * Check if should refresh and refresh token if needed
   */
  private async checkAndRefresh() {
    if (this.isRefreshing) return;

    let currentAuth: any;
    authStore.subscribe(auth => {
      currentAuth = auth;
    })();

    if (!currentAuth?.tokens?.refresh_token) {
      return;
    }

    // Check if user is active
    const timeSinceActivity = activityTracker.getTimeSinceLastActivity();
    const THIRTY_MINUTES = 30 * 60 * 1000;

    if (timeSinceActivity > THIRTY_MINUTES) {
      authStore.logout();
      return;
    }

    // Check if token is expired or about to expire
    if (isTokenExpired(currentAuth.tokens.access_token)) {
      await this.refreshToken(currentAuth.tokens.refresh_token);
    } else {
      // Schedule next refresh
      this.scheduleRefresh();
    }
  }

  /**
   * Refresh the access token using the refresh token
   */
  async refreshToken(refreshToken: string, logoutOnFailure = true): Promise<boolean> {
    if (this.isRefreshing) {
      return false;
    }

    this.isRefreshing = true;

    try {
      const response = await apiClient.post<{
        access_token: string;
        refresh_token: string;
        token_type: string;
      }>('/auth/refresh', {
        refresh_token: refreshToken
      });

      // Update tokens in store
      authStore.updateTokens({
        access_token: response.access_token,
        refresh_token: response.refresh_token,
        token_type: response.token_type
      });

      // Schedule next refresh
      this.scheduleRefresh();

      return true;
    } catch (error) {
      console.error('Failed to refresh token:', error);
      if (logoutOnFailure) {
        authStore.logout();
      }
      return false;
    } finally {
      this.isRefreshing = false;
    }
  }
}

export const tokenRefreshService = new TokenRefreshService();
