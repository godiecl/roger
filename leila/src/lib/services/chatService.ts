/**
 * Chat Service
 * Handles project chat messages and AI assistant queries.
 */
import { apiClient } from './apiClient';
import type { ProjectMessage, MessageListResponse, AiMessageResponse, PdfContextResponse } from '$lib/types';

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

  async askAI(projectId: number, question: string, context?: string): Promise<AiMessageResponse> {
    return apiClient.post<AiMessageResponse>(
      `/projects/${projectId}/messages/ai`,
      { question, context }
    );
  }

  async uploadPdfContext(projectId: number, file: File): Promise<PdfContextResponse> {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.upload<PdfContextResponse>(
      `/projects/${projectId}/context/pdf`,
      formData
    );
  }
}

export const chatService = new ChatService();
