/**
 * Chat store for project messages.
 */
import { writable, derived } from 'svelte/store';
import type { ProjectMessage } from '$lib/types';

interface ChatState {
  messages: ProjectMessage[];
  loading: boolean;
  sending: boolean;
  error: string | null;
}

function createChatStore() {
  const { subscribe, update, set } = writable<ChatState>({
    messages: [],
    loading: false,
    sending: false,
    error: null
  });

  return {
    subscribe,

    setMessages(messages: ProjectMessage[]) {
      update(s => ({ ...s, messages, error: null }));
    },

    /** Append only messages with id greater than the last stored id */
    mergeNew(incoming: ProjectMessage[]) {
      update(s => {
        const maxId = s.messages.length > 0
          ? Math.max(...s.messages.map(m => m.id))
          : 0;
        const newOnes = incoming.filter(m => m.id > maxId);
        if (newOnes.length === 0) return s;
        return { ...s, messages: [...s.messages, ...newOnes] };
      });
    },

    addMessage(message: ProjectMessage) {
      update(s => ({ ...s, messages: [...s.messages, message] }));
    },

    setLoading(loading: boolean) {
      update(s => ({ ...s, loading }));
    },

    setSending(sending: boolean) {
      update(s => ({ ...s, sending }));
    },

    setError(error: string | null) {
      update(s => ({ ...s, error }));
    },

    reset() {
      set({ messages: [], loading: false, sending: false, error: null });
    }
  };
}

export const chatStore = createChatStore();

export const hasMessages = derived(
  chatStore,
  $chat => $chat.messages.length > 0
);
