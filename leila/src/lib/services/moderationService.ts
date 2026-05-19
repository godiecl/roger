import { apiClient } from './apiClient';

export interface ModerationStats {
  pending: number;
  approved: number;
  rejected: number;
  total: number;
}

export interface ContributionQueueItem {
  id: number;
  photograph_id: number;
  contributor_id: number;
  attribute_type: string;
  field_name: string;
  proposed_value: string;
  evidence_notes: string | null;
  created_at: string;
}

export interface ContributionQueueResponse {
  total: number;
  skip: number;
  limit: number;
  items: ContributionQueueItem[];
}

export interface BatchActionResponse {
  processed: number;
  failed: number;
  errors: string[];
}

export interface PendingTag {
  photograph_tag_id: number;
  photograph_id: number;
  tag_id: number;
  tag_name: string;
  tag_category: string;
  confidence: number | null;
  created_at: string;
}

export interface PendingTagsResponse {
  total: number;
  skip: number;
  limit: number;
  items: PendingTag[];
}

class ModerationService {
  async getStats(): Promise<ModerationStats> {
    return apiClient.get('/moderation/stats');
  }

  async getQueue(params: {
    skip?: number;
    limit?: number;
    attribute_type?: string;
  } = {}): Promise<ContributionQueueResponse> {
    const qs = new URLSearchParams();
    if (params.skip != null) qs.set('skip', String(params.skip));
    if (params.limit != null) qs.set('limit', String(params.limit));
    if (params.attribute_type) qs.set('attribute_type', params.attribute_type);
    return apiClient.get(`/moderation/queue?${qs}`);
  }

  async approve(contributionId: number): Promise<void> {
    return apiClient.post(`/moderation/contributions/${contributionId}/approve`, {});
  }

  async reject(contributionId: number, rejectionReason?: string): Promise<void> {
    return apiClient.post(`/moderation/contributions/${contributionId}/reject`, {
      rejection_reason: rejectionReason,
    });
  }

  async batchApprove(ids: number[]): Promise<BatchActionResponse> {
    return apiClient.post('/moderation/contributions/batch-approve', { contribution_ids: ids });
  }

  async batchReject(ids: number[], rejectionReason?: string): Promise<BatchActionResponse> {
    return apiClient.post('/moderation/contributions/batch-reject', {
      contribution_ids: ids,
      rejection_reason: rejectionReason,
    });
  }

  async getPendingTags(params: { skip?: number; limit?: number; photograph_id?: number } = {}): Promise<PendingTagsResponse> {
    const qs = new URLSearchParams();
    if (params.skip != null) qs.set('skip', String(params.skip));
    if (params.limit != null) qs.set('limit', String(params.limit));
    if (params.photograph_id != null) qs.set('photograph_id', String(params.photograph_id));
    return apiClient.get(`/tag-images/pending?${qs}`);
  }

  async approveTag(photographTagId: number): Promise<void> {
    return apiClient.post(`/tag-images/${photographTagId}/approve`, {});
  }

  async rejectTag(photographTagId: number): Promise<void> {
    return apiClient.delete(`/tag-images/${photographTagId}`);
  }
}

export const moderationService = new ModerationService();
