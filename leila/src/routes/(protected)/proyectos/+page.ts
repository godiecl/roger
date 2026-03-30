import type { PageLoad } from './$types';
import { requireAuth } from '$lib/utils/auth.guard';

export const load: PageLoad = ({ url }) => {
  requireAuth(url.pathname);
  return {};
};
