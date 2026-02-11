/**
 * Authentication store
 * Manages user authentication state and tokens
 */
import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import type { User, AuthTokens } from '$lib/types';
import { isTokenExpired } from '$lib/utils/token.utils';

interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  loading: boolean;
  error: string | null;
}

const initialState: AuthState = {
  user: null,
  tokens: null,
  loading: false,
  error: null
};

function createAuthStore() {
  const { subscribe, set, update } = writable<AuthState>(initialState);

  // Load from localStorage on init
  if (browser) {
    const storedTokens = localStorage.getItem('auth_tokens');
    const storedUser = localStorage.getItem('auth_user');

    if (storedTokens && storedUser) {
      try {
        const tokens = JSON.parse(storedTokens);
        const user = JSON.parse(storedUser);

        // Check if token is expired
        if (tokens.access_token && isTokenExpired(tokens.access_token)) {
          console.warn('Token expired, clearing auth data');
          localStorage.removeItem('auth_tokens');
          localStorage.removeItem('auth_user');
        } else {
          set({ user, tokens, loading: false, error: null });
        }
      } catch (e) {
        console.error('Failed to parse stored auth data', e);
        localStorage.removeItem('auth_tokens');
        localStorage.removeItem('auth_user');
      }
    }
  }

  return {
    subscribe,

    login(user: User, tokens: AuthTokens) {
      if (browser) {
        localStorage.setItem('auth_tokens', JSON.stringify(tokens));
        localStorage.setItem('auth_user', JSON.stringify(user));
      }
      set({ user, tokens, loading: false, error: null });
    },

    logout() {
      if (browser) {
        localStorage.removeItem('auth_tokens');
        localStorage.removeItem('auth_user');
        // Clear all auth-related data
        localStorage.removeItem('auth_refresh_token');
        sessionStorage.clear();
      }
      set(initialState);

      // Redirect to home and reload to ensure clean state
      if (browser) {
        window.location.href = '/';
      }
    },

    updateUser(user: User) {
      if (browser) {
        localStorage.setItem('auth_user', JSON.stringify(user));
      }
      update(state => ({ ...state, user }));
    },

    updateTokens(tokens: AuthTokens) {
      if (browser) {
        localStorage.setItem('auth_tokens', JSON.stringify(tokens));
      }
      update(state => ({ ...state, tokens }));
    },

    setLoading(loading: boolean) {
      update(state => ({ ...state, loading }));
    },

    setError(error: string | null) {
      update(state => ({ ...state, error }));
    },

    clearError() {
      update(state => ({ ...state, error: null }));
    }
  };
}

export const authStore = createAuthStore();

// Derived stores for convenience
export const isAuthenticated = derived(
  authStore,
  $auth => $auth.user !== null && $auth.tokens !== null
);

export const currentUser = derived(
  authStore,
  $auth => $auth.user
);

export const accessToken = derived(
  authStore,
  $auth => $auth.tokens?.access_token
);

export const isCurador = derived(
  authStore,
  $auth => $auth.user?.role === 'curador' || $auth.user?.role === 'administrador'
);

export const isAdmin = derived(
  authStore,
  $auth => $auth.user?.role === 'administrador'
);
