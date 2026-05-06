/**
 * Search store
 * Manages search filters and results
 */
import { writable, derived } from 'svelte/store';
import type { SearchFilters, SearchFacets } from '$lib/types';

interface SearchState {
  filters: SearchFilters;
  facets: SearchFacets | null;
  loading: boolean;
  error: string | null;
  searchType: 'keyword' | 'semantic';
}

const initialState: SearchState = {
  filters: {
    query: '',
    only_public: true,
    semantic: false
  },
  facets: null,
  loading: false,
  error: null,
  searchType: 'keyword'
};

function createSearchStore() {
  const { subscribe, set, update } = writable<SearchState>(initialState);

  return {
    subscribe,

    setFilter(key: keyof SearchFilters, value: any) {
      update(state => ({
        ...state,
        filters: {
          ...state.filters,
          [key]: value
        }
      }));
    },

    setFilters(filters: Partial<SearchFilters>) {
      update(state => ({
        ...state,
        filters: {
          ...state.filters,
          ...filters
        }
      }));
    },

    setQuery(query: string) {
      update(state => ({
        ...state,
        filters: {
          ...state.filters,
          query
        }
      }));
    },

    setYearRange(year_from?: number, year_to?: number) {
      update(state => ({
        ...state,
        filters: {
          ...state.filters,
          year_from,
          year_to
        }
      }));
    },

    setLocations(locations: string[]) {
      update(state => ({
        ...state,
        filters: {
          ...state.filters,
          locations
        }
      }));
    },

    addLocation(location: string) {
      update(state => ({
        ...state,
        filters: {
          ...state.filters,
          locations: [...(state.filters.locations || []), location]
        }
      }));
    },

    removeLocation(location: string) {
      update(state => ({
        ...state,
        filters: {
          ...state.filters,
          locations: (state.filters.locations || []).filter(l => l !== location)
        }
      }));
    },

    setTags(tags: string[]) {
      update(state => ({
        ...state,
        filters: {
          ...state.filters,
          tags
        }
      }));
    },

    addTag(tag: string) {
      update(state => ({
        ...state,
        filters: {
          ...state.filters,
          tags: [...(state.filters.tags || []), tag]
        }
      }));
    },

    removeTag(tag: string) {
      update(state => ({
        ...state,
        filters: {
          ...state.filters,
          tags: (state.filters.tags || []).filter(t => t !== tag)
        }
      }));
    },

    toggleSemantic() {
      update(state => ({
        ...state,
        filters: {
          ...state.filters,
          semantic: !state.filters.semantic
        }
      }));
    },

    setFacets(facets: SearchFacets) {
      update(state => ({ ...state, facets }));
    },

    setSearchType(searchType: 'keyword' | 'semantic') {
      update(state => ({ ...state, searchType }));
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

    clearFilters() {
      update(state => ({
        ...state,
        filters: initialState.filters
      }));
    },

    reset() {
      set(initialState);
    }
  };
}

export const searchStore = createSearchStore();

// Derived stores
export const hasActiveFilters = derived(
  searchStore,
  $search => {
    const { query, year_from, year_to, locations, tags, author } = $search.filters;
    return !!(
      query ||
      year_from ||
      year_to ||
      (locations && locations.length > 0) ||
      (tags && tags.length > 0) ||
      author
    );
  }
);

export const activeFilterCount = derived(
  searchStore,
  $search => {
    let count = 0;
    const { query, year_from, year_to, locations, tags, author } = $search.filters;

    if (query) count++;
    if (year_from || year_to) count++;
    if (locations && locations.length > 0) count += locations.length;
    if (tags && tags.length > 0) count += tags.length;
    if (author) count++;

    return count;
  }
);

export const isSemanticSearch = derived(
  searchStore,
  $search => $search.filters.semantic === true
);
