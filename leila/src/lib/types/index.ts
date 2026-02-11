/**
 * Type definitions for ROGER - Leila
 */

export interface Image {
  id: number;
  title: string;
  file_path: string;
  description?: string;
  year?: number;
  location?: string;
  author: string;
  tags: string[];
  collection_id?: number;
  metadata: Record<string, any>;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  last_login?: string;
}

export type UserRole =
  | 'usuario_estandar'
  | 'curador'
  | 'administrador'
  | 'sistema_ia'
  | 'investigador'
  | 'digitalizador'
  | 'colaborador';

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface Source {
  text: string;
  source_type: 'veraz' | 'verosímil';
  reference?: string;
  relevance_score?: number;
}

export interface Trazabilidad {
  sources: Source[];
  primary_source_type: 'veraz' | 'verosímil';
  confidence_score: number;
  verified_sources_count: number;
  plausible_sources_count: number;
}

export interface Narrative {
  id: number;
  image_id: number;
  text: string;
  trazabilidad: Trazabilidad;
  user_id?: number;
  prompt?: string;
  language: string;
  model_used?: string;
  generation_time_ms?: number;
  is_approved: boolean;
  approved_by?: number;
  approved_at?: string;
  is_verified: boolean;
  confidence_level: 'high' | 'medium' | 'low';
  created_at: string;
  updated_at: string;
}

export interface SearchFilters {
  query?: string;
  year_from?: number;
  year_to?: number;
  locations?: string[];
  tags?: string[];
  author?: string;
  only_public?: boolean;
  semantic?: boolean;
}

export interface SearchResponse {
  images: Image[];
  total_count: number;
  query: string;
  relevance_scores?: number[];
  search_type: 'keyword' | 'semantic';
  skip: number;
  limit: number;
}

export interface FacetItem {
  value: string;
  count: number;
}

export interface SearchFacets {
  years: { year: number; count: number }[];
  locations: { location: string; count: number }[];
  authors: { author: string; count: number }[];
  total: number;
}

export interface ApiError {
  detail: string;
  status?: number;
}
