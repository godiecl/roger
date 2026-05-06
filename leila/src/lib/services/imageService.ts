/**
 * Image Service
 * Handles image-related operations
 */
import { apiClient } from './apiClient';
import type { Image } from '$lib/types';

export interface ListImagesParams {
  skip?: number;
  limit?: number;
  year?: number;
  location?: string;
  tags?: string[];
}

export interface ListImagesResponse {
  images: Image[];
  total: number;
  skip: number;
  limit: number;
}

export interface CreateImageRequest {
  title: string;
  file_path: string;
  description?: string;
  year?: number;
  location?: string;
  author?: string;
  tags?: string[];
  collection_id?: number;
  metadata?: Record<string, any>;
  is_public?: boolean;
}

export interface UpdateImageRequest {
  title?: string;
  description?: string;
  year?: number;
  location?: string;
  tags?: string[];
  is_public?: boolean;
}

class ImageService {
  /**
   * List images with pagination and filters
   */
  async listImages(params?: ListImagesParams): Promise<ListImagesResponse> {
    return apiClient.get<ListImagesResponse>('/images', params);
  }

  /**
   * Get single image by ID
   */
  async getImage(imageId: number): Promise<Image> {
    return apiClient.get<Image>(`/images/${imageId}`);
  }

  /**
   * Create new image
   */
  async createImage(data: CreateImageRequest): Promise<Image> {
    return apiClient.post<Image>('/images', data);
  }

  /**
   * Update existing image
   */
  async updateImage(imageId: number, data: UpdateImageRequest): Promise<Image> {
    return apiClient.put<Image>(`/images/${imageId}`, data);
  }

  /**
   * Delete image
   */
  async deleteImage(imageId: number): Promise<void> {
    return apiClient.delete(`/images/${imageId}`);
  }

  /**
   * Upload image file
   */
  async uploadImage(file: File, metadata: CreateImageRequest): Promise<Image> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('metadata', JSON.stringify(metadata));

    return apiClient.upload<Image>('/images/upload', formData);
  }

  /**
   * Get images by collection
   */
  async getImagesByCollection(collectionId: number): Promise<Image[]> {
    return apiClient.get<Image[]>(`/collections/${collectionId}/images`);
  }
}

export const imageService = new ImageService();
