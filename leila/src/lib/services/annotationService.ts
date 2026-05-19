import { apiClient } from './apiClient';

export interface MetricResult {
  value: number | null;
  target: number;
  passes: boolean | null;
  label: string;
  description: string;
  detail: Record<string, unknown>;
}

export interface AnnotationCoverage {
  detections_total: number;
  detections_annotated: number;
  detection_coverage_pct: number;
  descriptions_total: number;
  descriptions_annotated: number;
  description_coverage_pct: number;
  total_detection_annotations: number;
  total_description_annotations: number;
}

export interface EvaluationMetrics {
  ica1: MetricResult;
  ica2: MetricResult;
  ica3: MetricResult;
  ica4: MetricResult;
  coverage: AnnotationCoverage;
  sufficient_data: boolean;
  computed_at: string;
}

export type AnnotationVerdict = 'correct' | 'incorrect' | 'uncertain';

export interface ExpertDetectionAnnotationCreate {
  detected_object_id?: number | null;
  verdict: AnnotationVerdict;
  corrected_label?: string | null;
  corrected_category?: string | null;
  notes?: string | null;
}

export interface ExpertDetectionAnnotation {
  id: number;
  detection_id: number;
  detected_object_id: number | null;
  annotator_id: number;
  verdict: string;
  corrected_label: string | null;
  corrected_category: string | null;
  notes: string | null;
  created_at: string;
}

export interface ExpertDetectionAnnotationListResponse {
  total: number;
  annotations: ExpertDetectionAnnotation[];
}

export interface ExpertDescriptionAnnotationCreate {
  ai_rating?: number | null;  // 1-5
  reference_description: string;
  notes?: string | null;
}

export interface ExpertDescriptionAnnotation {
  id: number;
  photograph_id: number;
  annotator_id: number;
  ai_rating: number | null;
  reference_description: string;
  notes: string | null;
  created_at: string;
}

class AnnotationService {
  async annotateDetection(
    detectionId: number,
    payload: ExpertDetectionAnnotationCreate,
  ): Promise<ExpertDetectionAnnotation> {
    return apiClient.post(`/detections/${detectionId}/annotations`, payload);
  }

  async getDetectionAnnotations(
    detectionId: number,
  ): Promise<ExpertDetectionAnnotationListResponse> {
    return apiClient.get(`/detections/${detectionId}/annotations`);
  }

  async annotateDescription(
    photographId: number,
    payload: ExpertDescriptionAnnotationCreate,
  ): Promise<ExpertDescriptionAnnotation> {
    return apiClient.post(`/detections/photograph/${photographId}/description-annotation`, payload);
  }

  async getDescriptionAnnotations(
    photographId: number,
  ): Promise<ExpertDescriptionAnnotation[]> {
    return apiClient.get(`/detections/photograph/${photographId}/description-annotation`);
  }

  async getMetrics(): Promise<EvaluationMetrics> {
    return apiClient.get('/detections/metrics');
  }
}

export const annotationService = new AnnotationService();
