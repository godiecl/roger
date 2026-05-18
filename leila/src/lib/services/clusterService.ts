import { apiClient } from './apiClient';

export type ClusterAlgorithm = 'dbscan' | 'kmeans';

export interface ClusterRequest {
  photograph_ids: number[];
  algorithm?: ClusterAlgorithm;
  n_clusters?: number;
  texts?: string[];
}

export interface Cluster {
  id: number | null;
  label: string;
  algorithm: string;
  member_count: number;
  centroid_photograph_id: number | null;
  photograph_ids: number[];
  status: string;
  justification?: string | null;
}

export interface ClusteringJob {
  id: number | null;
  algorithm: string;
  embedding_model: string;
  n_clusters: number;
  noise_count: number;
  processing_time_ms: number;
  status: string;
  photograph_ids: number[];
  clusters: Cluster[];
  created_at: string | null;
  updated_at: string | null;
}

export interface ClusteringJobListResponse {
  total: number;
  skip: number;
  limit: number;
  jobs: ClusteringJob[];
}

class ClusterService {
  async create(payload: ClusterRequest): Promise<ClusteringJob> {
    return apiClient.post('/clusters', { algorithm: 'dbscan', ...payload });
  }

  async get(jobId: number): Promise<ClusteringJob> {
    return apiClient.get(`/clusters/${jobId}`);
  }

  async list(params?: { skip?: number; limit?: number }): Promise<ClusteringJobListResponse> {
    return apiClient.get('/clusters', params);
  }

  async justify(jobId: number): Promise<ClusteringJob> {
    return apiClient.post(`/clusters/${jobId}/justify`);
  }

  async delete(jobId: number): Promise<void> {
    return apiClient.delete(`/clusters/${jobId}`);
  }
}

export const clusterService = new ClusterService();
