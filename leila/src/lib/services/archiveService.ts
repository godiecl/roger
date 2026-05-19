import { apiClient } from './apiClient';
import type {
  Collection, CollectionListResponse,
  Box, BoxListResponse,
  Roll, RollListResponse,
  Photograph, PhotographListResponse,
} from '$lib/types';

export interface UploadedImage {
  id: number;
  title: string;
  file_path: string;
  year: number | null;
  location: string | null;
  collection_id: number | null;
  is_public: boolean;
  created_at: string;
}

export interface BulkUploadResult {
  filename: string;
  ok: boolean;
  image_id: number | null;
  error: string | null;
}

export interface BulkUploadResponse {
  total: number;
  succeeded: number;
  failed: number;
  results: BulkUploadResult[];
}

export interface CreateCollectionPayload {
  name: string;
  slug?: string;
  description?: string;
  photographer_name?: string;
  origin_country?: string;
  date_range_from?: number;
  date_range_to?: number;
  is_public?: boolean;
  license?: string;
  copyright_notes?: string;
}

class ArchiveService {
  // ── Collections ────────────────────────────────────────────────────────────

  async listCollections(params?: { skip?: number; limit?: number; public_only?: boolean }): Promise<CollectionListResponse> {
    return apiClient.get('/archive/collections', params);
  }

  async listAllCollections(params?: { skip?: number; limit?: number }): Promise<CollectionListResponse> {
    return apiClient.get('/archive/collections/all', params);
  }

  async getCollection(id: number): Promise<Collection> {
    return apiClient.get(`/archive/collections/${id}`);
  }

  async createCollection(data: CreateCollectionPayload): Promise<Collection> {
    return apiClient.post('/archive/collections', data);
  }

  async updateCollection(id: number, data: Partial<CreateCollectionPayload>): Promise<Collection> {
    return apiClient.put(`/archive/collections/${id}`, data);
  }

  async deleteCollection(id: number): Promise<void> {
    return apiClient.delete(`/archive/collections/${id}`);
  }

  async deleteImagesByCollection(collectionId: number): Promise<void> {
    return apiClient.delete(`/images/by-collection/${collectionId}`);
  }

  // ── Upload ─────────────────────────────────────────────────────────────────

  async uploadSingle(
    file: File,
    meta: {
      collection_id: number;
      title?: string;
      year?: number;
      location?: string;
      description?: string;
      is_public?: boolean;
      box?: string;
      subdivision?: string;
    }
  ): Promise<UploadedImage> {
    const fd = new FormData();
    fd.append('file', file);
    fd.append('collection_id', String(meta.collection_id));
    if (meta.title)       fd.append('title', meta.title);
    if (meta.year)        fd.append('year', String(meta.year));
    if (meta.location)    fd.append('location', meta.location);
    if (meta.description) fd.append('description', meta.description);
    fd.append('is_public', String(meta.is_public ?? true));
    if (meta.box)         fd.append('box', meta.box);
    if (meta.subdivision) fd.append('subdivision', meta.subdivision);
    return apiClient.upload('/archive/upload/single', fd);
  }

  async uploadBulk(
    files: File[],
    meta: {
      collection_id: number;
      year?: number;
      location?: string;
      is_public?: boolean;
      box?: string;
      subdivision?: string;
    },
    onProgress?: (done: number, total: number) => void
  ): Promise<BulkUploadResponse> {
    const fd = new FormData();
    for (const f of files) fd.append('files', f);
    fd.append('collection_id', String(meta.collection_id));
    if (meta.year)        fd.append('year', String(meta.year));
    if (meta.location)    fd.append('location', meta.location);
    fd.append('is_public', String(meta.is_public ?? true));
    if (meta.box)         fd.append('box', meta.box);
    if (meta.subdivision) fd.append('subdivision', meta.subdivision);
    return apiClient.upload('/archive/upload/bulk', fd);
  }

  async setCollectionCover(collectionId: number, fileOrPath: File | string): Promise<Collection> {
    const fd = new FormData();
    if (typeof fileOrPath === 'string') {
      fd.append('image_path', fileOrPath);
    } else {
      fd.append('file', fileOrPath);
    }
    return apiClient.upload(`/archive/collections/${collectionId}/cover`, fd);
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
