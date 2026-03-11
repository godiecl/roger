/**
 * Services barrel export
 */
export { apiClient, ApiClient } from './apiClient';
export { authService } from './authService';
export { imageService } from './imageService';
export { narrativeService } from './narrativeService';
export { searchService } from './searchService';
export { projectService } from './projectService';
export { chatService } from './chatService';
export { invitationService } from './invitationService';

// Re-export types
export type { RegisterRequest, RegisterResponse } from './authService';
export type {
  ListImagesParams,
  ListImagesResponse,
  CreateImageRequest,
  UpdateImageRequest
} from './imageService';
export type {
  GenerateNarrativeRequest,
  RegenerateNarrativeRequest,
  ApproveNarrativeRequest,
  ListNarrativesResponse
} from './narrativeService';
