import { redirect } from '@sveltejs/kit';
import { browser } from '$app/environment';
import type { PageLoad } from './$types';

export const load: PageLoad = () => {
  // Check if user is already authenticated
  if (browser) {
    const authTokens = localStorage.getItem('auth_tokens');
    const authUser = localStorage.getItem('auth_user');

    if (authTokens && authUser) {
      // User is already logged in, redirect to home
      throw redirect(307, '/');
    }
  }

  return {};
};
