/**
 * Invitation Service
 * Handles project invitations.
 */
import { apiClient } from './apiClient';
import type { ProjectInvitation, InvitationListResponse, ProjectMember } from '$lib/types';

class InvitationService {
  async listPending(): Promise<InvitationListResponse> {
    return apiClient.get<InvitationListResponse>('/invitations');
  }

  async accept(invitationId: number): Promise<ProjectMember> {
    return apiClient.patch<ProjectMember>(`/invitations/${invitationId}/accept`);
  }

  async decline(invitationId: number): Promise<void> {
    return apiClient.patch<void>(`/invitations/${invitationId}/decline`);
  }
}

export const invitationService = new InvitationService();
