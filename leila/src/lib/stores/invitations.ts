/**
 * Invitations store — tracks pending project invitations for the current user.
 */
import { writable, derived } from 'svelte/store';
import type { ProjectInvitation } from '$lib/types';

interface InvitationState {
  pending: ProjectInvitation[];
  loading: boolean;
}

function createInvitationsStore() {
  const { subscribe, update, set } = writable<InvitationState>({
    pending: [],
    loading: false
  });

  return {
    subscribe,

    setPending(invitations: ProjectInvitation[]) {
      update(s => ({ ...s, pending: invitations }));
    },

    remove(invitationId: number) {
      update(s => ({ ...s, pending: s.pending.filter(i => i.id !== invitationId) }));
    },

    setLoading(loading: boolean) {
      update(s => ({ ...s, loading }));
    },

    reset() {
      set({ pending: [], loading: false });
    }
  };
}

export const invitationsStore = createInvitationsStore();

export const pendingCount = derived(
  invitationsStore,
  $s => $s.pending.length
);
