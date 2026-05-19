import { apiClient } from './apiClient';

export interface AttributeRecord {
  id: number;
  status: string;
  source_type: string | null;
  analyzed_at: string | null;
  confidence_level: number | null;
  analysis_provider: string | null;
  data: Record<string, unknown>;
}

export interface ContributionSummary {
  id: number;
  attribute_type: string;
  field_name: string;
  proposed_value: string;
  evidence_notes: string | null;
  contributor_id: number;
  created_at: string;
}

export interface PhotographMetadata {
  photograph_id: number;
  technical: AttributeRecord[];
  chronology: AttributeRecord[];
  geographic: AttributeRecord[];
  environmental: AttributeRecord[];
  pending_contributions: ContributionSummary[];
  pending_count: number;
}

class MetadataService {
  async getPhotographMetadata(photographId: number, includeSuperseded = false): Promise<PhotographMetadata> {
    return apiClient.get(
      `/metadata/${photographId}?include_superseded=${includeSuperseded}`,
    );
  }

  async listWithPending(skip = 0, limit = 50): Promise<Array<{ photograph_id: number; pending_contributions: number }>> {
    return apiClient.get(`/metadata?skip=${skip}&limit=${limit}`);
  }
}

export const metadataService = new MetadataService();
