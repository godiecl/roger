import { apiClient } from './apiClient';
import type { Contribution, ContributionListResponse, AttributeType } from '$lib/types';

export interface SubmitContributionRequest {
  photograph_id: number;
  attribute_type: AttributeType;
  field_name: string;
  proposed_value: string;
  evidence_notes?: string;
}

class ContributionService {
  async submit(data: SubmitContributionRequest): Promise<Contribution> {
    return apiClient.post('/contributions/', data);
  }

  async listMine(params?: { skip?: number; limit?: number }): Promise<ContributionListResponse> {
    return apiClient.get('/contributions/mine', params);
  }

  async listPending(params?: { skip?: number; limit?: number }): Promise<ContributionListResponse> {
    return apiClient.get('/contributions/pending', params);
  }

  async listForPhotograph(photograph_id: number): Promise<ContributionListResponse> {
    return apiClient.get(`/contributions/photograph/${photograph_id}`);
  }

  async approve(id: number): Promise<Contribution> {
    return apiClient.post(`/contributions/${id}/approve`);
  }

  async reject(id: number, reason: string): Promise<Contribution> {
    return apiClient.post(`/contributions/${id}/reject`, { rejection_reason: reason });
  }
}

export const contributionService = new ContributionService();
