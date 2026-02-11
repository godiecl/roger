/**
 * Search Service
 * Handles search and filtering operations
 */
import { apiClient } from './apiClient';
import type { SearchFilters, SearchResponse, SearchFacets } from '$lib/types';

class SearchService {
  /**
   * Search images using GET method
   */
  async searchImages(
    filters: SearchFilters,
    skip: number = 0,
    limit: number = 100
  ): Promise<SearchResponse> {
    const params: Record<string, any> = {
      skip,
      limit,
      ...filters
    };

    return apiClient.get<SearchResponse>('/search', params);
  }

  /**
   * Search images using POST method (for complex queries)
   */
  async searchImagesPost(
    filters: SearchFilters,
    skip: number = 0,
    limit: number = 100
  ): Promise<SearchResponse> {
    return apiClient.post<SearchResponse>(`/search?skip=${skip}&limit=${limit}`, filters);
  }

  /**
   * Get search facets (aggregations)
   */
  async getFacets(onlyPublic: boolean = true): Promise<SearchFacets> {
    return apiClient.get<SearchFacets>('/search/facets', {
      only_public: onlyPublic
    });
  }

  /**
   * Semantic search using AI embeddings
   */
  async semanticSearch(
    query: string,
    limit: number = 10,
    onlyPublic: boolean = true
  ): Promise<SearchResponse> {
    return apiClient.get<SearchResponse>('/search', {
      query,
      semantic: true,
      only_public: onlyPublic,
      limit
    });
  }
}

export const searchService = new SearchService();
