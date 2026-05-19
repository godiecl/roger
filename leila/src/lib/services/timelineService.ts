import { apiClient } from './apiClient';

export interface TimelineEvent {
  id: number | null;
  date_label: string;
  year: number | null;
  title: string;
  description: string;
  axis: string;
  event_type: string;
  source_type: string;
}

export interface Timeline {
  id: number | null;
  photograph_id: number;
  context_summary: string;
  provider: string;
  generation_time_ms: number;
  is_approved: boolean;
  approved_by: number | null;
  approved_at: string | null;
  event_count: number;
  events: TimelineEvent[];
  created_at: string | null;
  updated_at: string | null;
}

export interface GenerateTimelineRequest {
  photograph_id: number;
  photograph_date?: string;
  photograph_location?: string;
  photograph_description?: string;
  detected_objects?: string[];
  force_regeneration?: boolean;
}

class TimelineService {
  async generate(request: GenerateTimelineRequest): Promise<Timeline> {
    return apiClient.post('/timelines', request);
  }

  async getByPhotograph(photographId: number): Promise<Timeline> {
    return apiClient.get(`/timelines/photograph/${photographId}`);
  }

  async get(timelineId: number): Promise<Timeline> {
    return apiClient.get(`/timelines/${timelineId}`);
  }

  async generateMany(photographIds: number[]): Promise<PromiseSettledResult<Timeline>[]> {
    return Promise.allSettled(
      photographIds.map((id) => this.generate({ photograph_id: id })),
    );
  }

  async getWikipediaEvents(year: number): Promise<TimelineEvent[]> {
    return apiClient.get(`/timelines/wikipedia/${year}`);
  }
}

export const timelineService = new TimelineService();
