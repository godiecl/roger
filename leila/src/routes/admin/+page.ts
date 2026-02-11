import { requireAuth, requireRole } from '$lib/utils/auth.guard';
import type { PageLoad } from './$types';

export const load: PageLoad = ({ url }) => {
  // First check if user is authenticated
  requireAuth(url.pathname);

  // Then check if user has required role
  requireRole(['administrador', 'curador']);

  return {};
};
