/**
 * Authentication Service
 * Handles user authentication operations
 */
import { apiClient } from './apiClient';
import type { LoginRequest, LoginResponse, User } from '$lib/types';

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  full_name?: string;
  verification_token: string;
  verification_code: string;
}

export interface SendVerificationCodeResponse {
  token: string;
  message: string;
}

export interface RegisterResponse {
  user: User;
  message: string;
}

class AuthService {
  /**
   * Login user
   */
  async login(email: string, password: string): Promise<LoginResponse> {
    const data: LoginRequest = { email, password };
    return apiClient.post<LoginResponse>('/auth/login', data);
  }

  /**
   * Register new user
   */
  async register(data: RegisterRequest): Promise<RegisterResponse> {
    return apiClient.post<RegisterResponse>('/auth/register', data);
  }

  /**
   * Refresh access token
   */
  async refreshToken(refreshToken: string): Promise<{ access_token: string; token_type: string }> {
    return apiClient.post('/auth/refresh', { refresh_token: refreshToken });
  }

  /**
   * Get current user profile
   */
  async getCurrentUser(): Promise<User> {
    return apiClient.get<User>('/auth/me');
  }

  /**
   * Update user profile
   */
  async updateProfile(userId: number, data: Partial<User>): Promise<User> {
    return apiClient.put<User>(`/auth/users/${userId}`, data);
  }

  /**
   * Change password
   */
  async changePassword(
    userId: number,
    currentPassword: string,
    newPassword: string
  ): Promise<{ message: string }> {
    return apiClient.post(`/auth/users/${userId}/change-password`, {
      current_password: currentPassword,
      new_password: newPassword
    });
  }

  /**
   * Send email verification code for registration
   */
  async sendVerificationCode(email: string): Promise<SendVerificationCodeResponse> {
    return apiClient.post('/auth/send-verification-code', { email });
  }

  /**
   * Request password reset email
   */
  async forgotPassword(email: string): Promise<{ message: string }> {
    return apiClient.post('/auth/forgot-password', { email });
  }

  /**
   * Reset password using token from email
   */
  async resetPassword(token: string, newPassword: string): Promise<{ message: string }> {
    return apiClient.post('/auth/reset-password', { token, new_password: newPassword });
  }
}

export const authService = new AuthService();
