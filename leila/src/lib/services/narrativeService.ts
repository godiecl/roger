/**
 * Narrative Service
 * Handles AI-generated narratives operations
 */
import { apiClient } from './apiClient';
import type { Narrative } from '$lib/types';

export interface GenerateNarrativeRequest {
  image_id: number;
  prompt?: string;
  language?: 'es' | 'en' | 'de';
}

export interface RegenerateNarrativeRequest {
  prompt?: string;
}

export interface ApproveNarrativeRequest {
  approved_by: number;
}

export interface ListNarrativesResponse {
  total: number;
  skip: number;
  limit: number;
  narratives: Narrative[];
}

class NarrativeService {
  /**
   * Generate a new narrative for an image
   */
  async generateNarrative(data: GenerateNarrativeRequest): Promise<Narrative> {
    return apiClient.post<Narrative>('/narratives', data);
  }

  /**
   * Get single narrative by ID
   */
  async getNarrative(narrativeId: number): Promise<Narrative> {
    return apiClient.get<Narrative>(`/narratives/${narrativeId}`);
  }

  /**
   * Get all narratives for an image
   */
  async getNarrativesForImage(
    imageId: number,
    onlyApproved: boolean = false
  ): Promise<ListNarrativesResponse> {
    return apiClient.get<ListNarrativesResponse>(`/narratives/image/${imageId}`, {
      only_approved: onlyApproved
    });
  }

  /**
   * List all narratives with pagination
   */
  async listNarratives(
    skip: number = 0,
    limit: number = 100,
    onlyApproved: boolean = false
  ): Promise<ListNarrativesResponse> {
    return apiClient.get<ListNarrativesResponse>('/narratives', {
      skip,
      limit,
      only_approved: onlyApproved
    });
  }

  /**
   * Regenerate an existing narrative
   */
  async regenerateNarrative(
    narrativeId: number,
    data: RegenerateNarrativeRequest
  ): Promise<Narrative> {
    return apiClient.post<Narrative>(`/narratives/${narrativeId}/regenerate`, data);
  }

  /**
   * Approve a narrative (curator/admin only)
   */
  async approveNarrative(
    narrativeId: number,
    approvedBy: number
  ): Promise<Narrative> {
    return apiClient.post<Narrative>(`/narratives/${narrativeId}/approve`, {
      approved_by: approvedBy
    });
  }

  /**
   * Unapprove a narrative (curator/admin only)
   */
  async unapproveNarrative(narrativeId: number): Promise<Narrative> {
    return apiClient.post<Narrative>(`/narratives/${narrativeId}/unapprove`);
  }

  /**
   * Delete a narrative (admin only)
   */
  async deleteNarrative(narrativeId: number): Promise<void> {
    return apiClient.delete(`/narratives/${narrativeId}`);
  }
}

export const narrativeService = new NarrativeService();
