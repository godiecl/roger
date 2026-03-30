import { requireAuth } from '$lib/utils/auth.guard';
import type { PageLoad } from './$types';

export const load: PageLoad = ({ url }) => {
  // Protect this route - only authenticated users can access
  requireAuth(url.pathname);

  return {};
};
