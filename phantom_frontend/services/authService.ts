import apiClient from '../config/api';
import {
  RegisterData,
  LoginData,
  TokenResponse,
  RefreshTokenResponse,
  AuthService,
} from '../types';

/**
 * Authentication Service
 * Handles all authentication-related API calls including registration,
 * login, logout, token refresh, and token verification.
 */

/**
 * Register a new user
 * POST /api/auth/register/
 * 
 * @param data - Registration data containing username, name, and password
 * @throws Error if registration fails
 */
const register = async (data: RegisterData): Promise<void> => {
  try {
    await apiClient.post('/auth/register/', data);
  } catch (error: any) {
    // Extract error message from response
    const errorMessage = error.response?.data?.message || 
                        error.response?.data?.error ||
                        'Registration failed. Please try again.';
    throw new Error(errorMessage);
  }
};

/**
 * Login user and retrieve JWT tokens
 * POST /api/auth/login/
 * 
 * @param data - Login credentials containing username and password
 * @returns TokenResponse with access token, refresh token, user_id, and username
 * @throws Error if login fails
 */
const login = async (data: LoginData): Promise<TokenResponse> => {
  try {
    const response = await apiClient.post<TokenResponse>('/auth/login/', data);
    return response.data;
  } catch (error: any) {
    // Extract error message from response
    const errorMessage = error.response?.data?.message || 
                        error.response?.data?.error ||
                        error.response?.data?.detail ||
                        'Login failed. Please check your credentials.';
    throw new Error(errorMessage);
  }
};

/**
 * Logout user and blacklist refresh token
 * POST /api/auth/logout/
 * 
 * @param refreshToken - The refresh token to blacklist
 * @throws Error if logout fails (non-critical, can be ignored)
 */
const logout = async (refreshToken: string): Promise<void> => {
  try {
    await apiClient.post('/auth/logout/', { refresh: refreshToken });
  } catch (error: any) {
    // Logout errors are non-critical - we still clear local storage
    console.error('Logout API call failed:', error);
    // Don't throw - allow logout to proceed even if API call fails
  }
};

/**
 * Refresh access token using refresh token
 * POST /api/auth/token/refresh/
 * 
 * @param refreshToken - The refresh token to use for obtaining a new access token
 * @returns RefreshTokenResponse with new access token
 * @throws Error if token refresh fails
 */
const refreshToken = async (refreshToken: string): Promise<RefreshTokenResponse> => {
  try {
    const response = await apiClient.post<RefreshTokenResponse>(
      '/auth/token/refresh/',
      { refresh: refreshToken }
    );
    return response.data;
  } catch (error: any) {
    // Extract error message from response
    const errorMessage = error.response?.data?.message || 
                        error.response?.data?.error ||
                        error.response?.data?.detail ||
                        'Token refresh failed. Please login again.';
    throw new Error(errorMessage);
  }
};

/**
 * Verify if an access token is still valid
 * POST /api/auth/token/verify/
 * 
 * @param token - The access token to verify
 * @returns true if token is valid, false otherwise
 */
const verifyToken = async (token: string): Promise<boolean> => {
  try {
    await apiClient.post('/auth/token/verify/', { token });
    return true;
  } catch (error: any) {
    // Token is invalid or expired
    return false;
  }
};

/**
 * Export authentication service object implementing AuthService interface
 */
const authService: AuthService = {
  register,
  login,
  logout,
  refreshToken,
  verifyToken,
};

export default authService;
