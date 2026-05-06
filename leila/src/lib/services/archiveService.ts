import { apiClient } from './apiClient';
import type {
  Collection, CollectionListResponse,
  Box, BoxListResponse,
  Roll, RollListResponse,
  Photograph, PhotographListResponse,
} from '$lib/types';

class ArchiveService {
  // ── Collections ────────────────────────────────────────────────────────────

  async listCollections(params?: { skip?: number; limit?: number; public_only?: boolean }): Promise<CollectionListResponse> {
    return apiClient.get('/archive/collections', params);
  }

  async getCollection(id: number): Promise<Collection> {
    return apiClient.get(`/archive/collections/${id}`);
  }

  // ── Boxes ──────────────────────────────────────────────────────────────────

  async listBoxes(collection_id: number, params?: { skip?: number; limit?: number }): Promise<BoxListResponse> {
    return apiClient.get('/archive/boxes', { collection_id, ...params });
  }

  async getBox(id: number): Promise<Box> {
    return apiClient.get(`/archive/boxes/${id}`);
  }

  // ── Rolls ──────────────────────────────────────────────────────────────────

  async listRolls(box_id: number, params?: { skip?: number; limit?: number }): Promise<RollListResponse> {
    return apiClient.get(`/archive/boxes/${box_id}/rolls`, params);
  }

  async getRoll(id: number): Promise<Roll> {
    return apiClient.get(`/archive/rolls/${id}`);
  }

  // ── Photographs ────────────────────────────────────────────────────────────

  async listPhotographs(roll_id: number, params?: { skip?: number; limit?: number }): Promise<PhotographListResponse> {
    return apiClient.get(`/archive/rolls/${roll_id}/photographs`, params);
  }

  async getPhotograph(id: number): Promise<Photograph> {
    return apiClient.get(`/archive/photographs/${id}`);
  }
}

export const archiveService = new ArchiveService();
