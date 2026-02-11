/**
 * Images store
 * Manages images collection and state
 */
import { writable, derived } from 'svelte/store';
import type { Image } from '$lib/types';

interface ImagesState {
  images: Image[];
  currentImage: Image | null;
  loading: boolean;
  error: string | null;
  total: number;
  page: number;
  limit: number;
}

const initialState: ImagesState = {
  images: [],
  currentImage: null,
  loading: false,
  error: null,
  total: 0,
  page: 0,
  limit: 20
};

function createImagesStore() {
  const { subscribe, set, update } = writable<ImagesState>(initialState);

  return {
    subscribe,

    setImages(images: Image[], total: number = images.length) {
      update(state => ({
        ...state,
        images,
        total,
        loading: false,
        error: null
      }));
    },

    addImages(images: Image[]) {
      update(state => ({
        ...state,
        images: [...state.images, ...images],
        loading: false,
        error: null
      }));
    },

    setCurrentImage(image: Image | null) {
      update(state => ({
        ...state,
        currentImage: image
      }));
    },

    updateImage(imageId: number, updates: Partial<Image>) {
      update(state => ({
        ...state,
        images: state.images.map(img =>
          img.id === imageId ? { ...img, ...updates } : img
        ),
        currentImage:
          state.currentImage?.id === imageId
            ? { ...state.currentImage, ...updates }
            : state.currentImage
      }));
    },

    removeImage(imageId: number) {
      update(state => ({
        ...state,
        images: state.images.filter(img => img.id !== imageId),
        currentImage:
          state.currentImage?.id === imageId ? null : state.currentImage
      }));
    },

    setLoading(loading: boolean) {
      update(state => ({ ...state, loading }));
    },

    setError(error: string | null) {
      update(state => ({ ...state, error, loading: false }));
    },

    clearError() {
      update(state => ({ ...state, error: null }));
    },

    setPage(page: number) {
      update(state => ({ ...state, page }));
    },

    setLimit(limit: number) {
      update(state => ({ ...state, limit }));
    },

    reset() {
      set(initialState);
    }
  };
}

export const imagesStore = createImagesStore();

// Derived stores
export const totalPages = derived(
  imagesStore,
  $images => Math.ceil($images.total / $images.limit)
);

export const hasImages = derived(
  imagesStore,
  $images => $images.images.length > 0
);

export const hasNextPage = derived(
  imagesStore,
  $images => ($images.page + 1) * $images.limit < $images.total
);

export const hasPreviousPage = derived(
  imagesStore,
  $images => $images.page > 0
);
