import { apiClient } from './apiClient';

export interface GeoPin {
  photograph_id: number;
  attribute_id: number;
  title: string;
  year: number | null;
  location: string;
  lat: number;
  lng: number;
  source: 'ai' | 'curator' | 'metadata';
  validated: boolean;
  confidence: number | null;
}

export interface PinsResponse {
  total: number;
  pins: GeoPin[];
}

class GeoReferenceService {
  async listPins(): Promise<PinsResponse> {
    return apiClient.get('/georeference/pins');
  }

  async validateGeoreference(photographId: number): Promise<void> {
    return apiClient.post(`/georeference/validate/${photographId}`, {});
  }

  async deleteGeoreference(attributeId: number): Promise<void> {
    return apiClient.delete(`/georeference/${attributeId}`);
  }

  async batchInfer(): Promise<{ processed: number; inferred: number; errors: number }> {
    return apiClient.post('/georeference/batch-infer', {});
  }

  async inferCoordinates(
    photographId: number,
    data: { geographic_location: string; title?: string; year?: number }
  ): Promise<{ lat: number; lng: number; attribute_id: number }> {
    return apiClient.post(`/georeference/infer/${photographId}`, data);
  }
}

export const georeferenceService = new GeoReferenceService();
