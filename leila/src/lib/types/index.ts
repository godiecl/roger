/**
 * Type definitions for ROGER - Leila
 */

export interface PhotoPin {
  id: number;
  title: string;
  year: number | null;
  location: string;
  region?: string;
  lat: number;
  lng: number;
  tags: string[];
  source?: 'ai' | 'curator' | 'metadata';
  validated?: boolean;
  confidence?: number | null;
  attribute_id?: number;
}

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
  company?: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  last_login?: string;
}

export type UserRole =
  | 'usuario_estandar'
  | 'colaborador'
  | 'investigador'
  | 'digitalizador'
  | 'mesa_evaluadora'
  | 'curador'
  | 'administrador'
  | 'sistema_ia';

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
  like_count: number;
  report_count: number;
  is_manual: boolean;
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

// --- Projects ---

export type ProjectRole = 'lider' | 'investigador' | 'colaborador' | 'observador';

export interface Project {
  id: number;
  name: string;
  description?: string;
  start_date?: string;
  end_date?: string;
  owner_id: number;
  is_active: boolean;
  ai_instructions?: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectMember {
  id: number;
  project_id: number;
  user_id: number;
  role: ProjectRole;
  user_email?: string;
  user_full_name?: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectListResponse {
  total: number;
  skip: number;
  limit: number;
  projects: Project[];
}

export interface MemberListResponse {
  total: number;
  members: ProjectMember[];
}

export interface ProjectMessage {
  id: number;
  project_id: number;
  user_id: number;
  content: string;
  message_type: 'user' | 'ai';
  sender_name?: string;
  created_at: string;
  updated_at: string;
}

export interface MessageListResponse {
  total: number;
  messages: ProjectMessage[];
}

export interface AiMessageResponse {
  user_message: ProjectMessage;
  ai_message: ProjectMessage;
}

export interface ProjectInvitation {
  id: number;
  project_id: number;
  project_name: string;
  invited_by_email: string;
  status: 'pending' | 'accepted' | 'declined';
  created_at: string;
}

export interface InvitationListResponse {
  total: number;
  invitations: ProjectInvitation[];
}

export interface SentInvitation {
  id: number;
  project_id: number;
  invited_email: string;
  invited_by_email: string;
  status: 'pending' | 'accepted' | 'declined';
  created_at: string;
}

export interface SentInvitationListResponse {
  total: number;
  invitations: SentInvitation[];
}

export interface PdfContextResponse {
  filename: string;
  pages: number;
  text: string;
  char_count: number;
}

// ── Archive ───────────────────────────────────────────────────────────────────

export interface Collection {
  id: number;
  name: string;
  slug: string;
  description?: string;
  photographer_name?: string;
  origin_country?: string;
  date_range_from?: string;
  date_range_to?: string;
  is_public: boolean;
  cover_image_path?: string;
  license?: string;
  copyright_notes?: string;
  created_by: number;
  created_at: string;
}

export interface CollectionListResponse {
  total: number;
  skip: number;
  limit: number;
  collections: Collection[];
}

export interface Box {
  id: number;
  collection_id: number;
  box_number: number;
  name?: string;
  location_in_archive?: string;
  created_at: string;
}

export interface BoxListResponse {
  total: number;
  skip: number;
  limit: number;
  boxes: Box[];
}

export interface Roll {
  id: number;
  box_id: number;
  general_number: number;
  internal_number?: number;
  og_number?: string;
  strip_letter?: string;
  name?: string;
  image_type?: string;
  support?: string;
  physical_status?: string;
  color_mode?: string;
  frame_count?: number;
  created_at: string;
}

export interface RollListResponse {
  total: number;
  skip: number;
  limit: number;
  rolls: Roll[];
}

export interface Photograph {
  id: number;
  roll_id: number;
  frame_number?: number;
  identifier?: string;
  physical_location_ref?: string;
  digitalization_date?: string;
  width_px?: number;
  height_px?: number;
  color_depth?: number;
  resolution_dpi?: number;
  internal_cronology?: string;
  license?: string;
  is_public: boolean;
  created_at: string;
}

export interface PhotographListResponse {
  total: number;
  skip: number;
  limit: number;
  photographs: Photograph[];
}

// ── Contributions ─────────────────────────────────────────────────────────────

export type AttributeType = 'CHRONOLOGY' | 'GEOGRAPHIC' | 'ENVIRONMENTAL' | 'TAG';
export type ContributionStatus = 'PENDING' | 'APPROVED' | 'REJECTED';

export interface Contribution {
  id: number;
  photograph_id: number;
  contributor_id: number;
  attribute_type: AttributeType;
  field_name: string;
  proposed_value: string;
  evidence_notes?: string;
  status: ContributionStatus;
  reviewed_by?: number;
  reviewed_at?: string;
  rejection_reason?: string;
  created_at: string;
}

export interface ContributionListResponse {
  total: number;
  skip: number;
  limit: number;
  contributions: Contribution[];
}
