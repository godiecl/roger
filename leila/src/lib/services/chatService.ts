/**
 * Chat Service
 * Handles project chat messages and AI assistant queries.
 */
import { apiClient } from './apiClient';
import type { ProjectMessage, MessageListResponse, AiMessageResponse } from '$lib/types';

class ChatService {
  async listMessages(
    projectId: number,
    skip = 0,
    limit = 100
  ): Promise<MessageListResponse> {
    return apiClient.get<MessageListResponse>(
      `/projects/${projectId}/messages`,
      { skip, limit }
    );
  }

  async sendMessage(projectId: number, content: string): Promise<ProjectMessage> {
    return apiClient.post<ProjectMessage>(
      `/projects/${projectId}/messages`,
      { content }
    );
  }

  async askAI(projectId: number, question: string): Promise<AiMessageResponse> {
    return apiClient.post<AiMessageResponse>(
      `/projects/${projectId}/messages/ai`,
      { question }
    );
  }
}

export const chatService = new ChatService();
