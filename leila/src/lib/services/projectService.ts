/**
 * Project Service
 * Handles project and member management operations
 */
import { apiClient } from './apiClient';
import type {
  Project,
  ProjectMember,
  ProjectRole,
  ProjectListResponse,
  MemberListResponse,
  SentInvitationListResponse
} from '$lib/types';

export interface CreateProjectRequest {
  name: string;
  description?: string;
  start_date?: string;
  end_date?: string;
}

export interface UpdateProjectRequest {
  name?: string;
  description?: string;
  start_date?: string;
  end_date?: string;
  is_active?: boolean;
}

class ProjectService {
  async listProjects(skip = 0, limit = 100): Promise<ProjectListResponse> {
    return apiClient.get<ProjectListResponse>('/projects', { skip, limit });
  }

  async getProject(projectId: number): Promise<Project> {
    return apiClient.get<Project>(`/projects/${projectId}`);
  }

  async createProject(data: CreateProjectRequest): Promise<Project> {
    return apiClient.post<Project>('/projects', data);
  }

  async updateProject(projectId: number, data: UpdateProjectRequest): Promise<Project> {
    return apiClient.put<Project>(`/projects/${projectId}`, data);
  }

  async deleteProject(projectId: number): Promise<void> {
    return apiClient.delete(`/projects/${projectId}`);
  }

  async listMembers(projectId: number): Promise<MemberListResponse> {
    return apiClient.get<MemberListResponse>(`/projects/${projectId}/members`);
  }

  async addMember(projectId: number, email: string, role: ProjectRole = 'observador'): Promise<ProjectMember> {
    return apiClient.post<ProjectMember>(`/projects/${projectId}/members`, {
      email,
      role
    });
  }

  async removeMember(projectId: number, userId: number): Promise<void> {
    return apiClient.delete(`/projects/${projectId}/members/${userId}`);
  }

  async listProjectInvitations(projectId: number): Promise<SentInvitationListResponse> {
    return apiClient.get<SentInvitationListResponse>(`/projects/${projectId}/invitations`);
  }
}

export const projectService = new ProjectService();
