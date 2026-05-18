/**
 * Selection store — carrito de fotografías para clustering / timeline / asociación a proyecto.
 * Persiste entre navegaciones (sessionStorage), no entre sesiones del navegador.
 * Agnóstico a la jerarquía: una foto seleccionada en /archivo/[box_id] sigue ahí al cambiar de cajón.
 */
import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import type { Photograph } from '$lib/types';

const STORAGE_KEY = 'roger_selection';
const MIN_FOR_CLUSTERING = 5;

interface SelectionState {
  items: Map<number, Photograph>;
}

const initialState: SelectionState = { items: new Map() };

function loadFromSession(): SelectionState {
  if (!browser) return initialState;
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return initialState;
    const entries: [number, Photograph][] = JSON.parse(raw);
    return { items: new Map(entries) };
  } catch {
    return initialState;
  }
}

function persist(state: SelectionState) {
  if (!browser) return;
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(Array.from(state.items.entries())));
}

function createSelectionStore() {
  const { subscribe, set, update } = writable<SelectionState>(loadFromSession());

  return {
    subscribe,

    toggle(photo: Photograph) {
      update((state) => {
        const next = new Map(state.items);
        if (next.has(photo.id)) {
          next.delete(photo.id);
        } else {
          next.set(photo.id, photo);
        }
        const newState = { items: next };
        persist(newState);
        return newState;
      });
    },

    add(photo: Photograph) {
      update((state) => {
        if (state.items.has(photo.id)) return state;
        const next = new Map(state.items);
        next.set(photo.id, photo);
        const newState = { items: next };
        persist(newState);
        return newState;
      });
    },

    addMany(photos: Photograph[]) {
      update((state) => {
        const next = new Map(state.items);
        for (const p of photos) next.set(p.id, p);
        const newState = { items: next };
        persist(newState);
        return newState;
      });
    },

    remove(photoId: number) {
      update((state) => {
        if (!state.items.has(photoId)) return state;
        const next = new Map(state.items);
        next.delete(photoId);
        const newState = { items: next };
        persist(newState);
        return newState;
      });
    },

    clear() {
      const newState = { items: new Map<number, Photograph>() };
      persist(newState);
      set(newState);
    },
  };
}

export const selection = createSelectionStore();

export const selectedPhotographs = derived(selection, ($s) => Array.from($s.items.values()));
export const selectedIds = derived(selection, ($s) => Array.from($s.items.keys()));
export const selectedCount = derived(selection, ($s) => $s.items.size);
export const canCluster = derived(selection, ($s) => $s.items.size >= MIN_FOR_CLUSTERING);
export const isSelected = derived(selection, ($s) => (id: number) => $s.items.has(id));

export { MIN_FOR_CLUSTERING };
