import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import authService from './authService';
import apiClient from '../config/api';
import { RegisterData, LoginData, TokenResponse } from '../types';
import fc from 'fast-check';

// Mock the API client
vi.mock('../config/api');

describe('authService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('register', () => {
    it('should call POST /auth/register/ with correct data', async () => {
      const registerData: RegisterData = {
        username: 'testuser',
        name: 'Test User',
        password: 'password123',
      };

      vi.mocked(apiClient.post).mockResolvedValueOnce({ data: {} });

      await authService.register(registerData);

      expect(apiClient.post).toHaveBeenCalledWith('/auth/register/', registerData);
      expect(apiClient.post).toHaveBeenCalledTimes(1);
    });

    it('should throw error when registration fails', async () => {
      const registerData: RegisterData = {
        username: 'testuser',
        name: 'Test User',
        password: 'password123',
      };

      const errorResponse = {
        response: {
          data: {
            message: 'Username already exists',
          },
        },
      };

      vi.mocked(apiClient.post).mockRejectedValueOnce(errorResponse);

      await expect(authService.register(registerData)).rejects.toThrow('Username already exists');
    });
  });

  describe('login', () => {
    it('should call POST /auth/login/ and return token response', async () => {
      const loginData: LoginData = {
        username: 'testuser',
        password: 'password123',
      };

      const tokenResponse: TokenResponse = {
        access: 'access-token-123',
        refresh: 'refresh-token-456',
        user_id: 1,
        username: 'testuser',
      };

      vi.mocked(apiClient.post).mockResolvedValueOnce({ data: tokenResponse });

      const result = await authService.login(loginData);

      expect(apiClient.post).toHaveBeenCalledWith('/auth/login/', loginData);
      expect(result).toEqual(tokenResponse);
    });

    it('should throw error when login fails', async () => {
      const loginData: LoginData = {
        username: 'testuser',
        password: 'wrongpassword',
      };

      const errorResponse = {
        response: {
          data: {
            detail: 'Invalid credentials',
          },
        },
      };

      vi.mocked(apiClient.post).mockRejectedValueOnce(errorResponse);

      await expect(authService.login(loginData)).rejects.toThrow('Invalid credentials');
    });
  });

  describe('logout', () => {
    it('should call POST /auth/logout/ with refresh token', async () => {
      const refreshToken = 'refresh-token-456';

      vi.mocked(apiClient.post).mockResolvedValueOnce({ data: {} });

      await authService.logout(refreshToken);

      expect(apiClient.post).toHaveBeenCalledWith('/auth/logout/', { refresh: refreshToken });
    });

    it('should not throw error when logout API call fails', async () => {
      const refreshToken = 'refresh-token-456';
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      vi.mocked(apiClient.post).mockRejectedValueOnce(new Error('Network error'));

      // Should not throw
      await expect(authService.logout(refreshToken)).resolves.toBeUndefined();

      expect(consoleErrorSpy).toHaveBeenCalled();
      consoleErrorSpy.mockRestore();
    });
  });

  describe('refreshToken', () => {
    it('should call POST /auth/token/refresh/ and return new access token', async () => {
      const refreshToken = 'refresh-token-456';
      const refreshResponse = {
        access: 'new-access-token-789',
      };

      vi.mocked(apiClient.post).mockResolvedValueOnce({ data: refreshResponse });

      const result = await authService.refreshToken(refreshToken);

      expect(apiClient.post).toHaveBeenCalledWith('/auth/token/refresh/', { refresh: refreshToken });
      expect(result).toEqual(refreshResponse);
    });

    it('should throw error when token refresh fails', async () => {
      const refreshToken = 'invalid-refresh-token';

      const errorResponse = {
        response: {
          data: {
            detail: 'Token is invalid or expired',
          },
        },
      };

      vi.mocked(apiClient.post).mockRejectedValueOnce(errorResponse);

      await expect(authService.refreshToken(refreshToken)).rejects.toThrow('Token is invalid or expired');
    });
  });

  describe('verifyToken', () => {
    it('should return true when token is valid', async () => {
      const token = 'valid-access-token';

      vi.mocked(apiClient.post).mockResolvedValueOnce({ data: {} });

      const result = await authService.verifyToken(token);

      expect(apiClient.post).toHaveBeenCalledWith('/auth/token/verify/', { token });
      expect(result).toBe(true);
    });

    it('should return false when token is invalid', async () => {
      const token = 'invalid-access-token';

      vi.mocked(apiClient.post).mockRejectedValueOnce(new Error('Invalid token'));

      const result = await authService.verifyToken(token);

      expect(result).toBe(false);
    });
  });
});

// ============================================================================
// Property-Based Tests
// ============================================================================

describe('Property-Based Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  /**
   * Feature: phantom-frontend-integration, Property 1: Authentication API calls are made correctly
   * 
   * For any valid registration or login credentials, the frontend should make the correct 
   * API call to the appropriate endpoint with the correct data format.
   * 
   * Validates: Requirements 1.1, 1.3
   */
  it('Property 1: Authentication API calls are made correctly', async () => {
    await fc.assert(
      fc.asyncProperty(
        // Generate valid registration data
        fc.record({
          username: fc.string({ minLength: 3, maxLength: 20 }).filter(s => s.trim().length >= 3),
          name: fc.string({ minLength: 1, maxLength: 100 }).filter(s => s.trim().length >= 1),
          password: fc.string({ minLength: 8, maxLength: 50 }),
        }),
        // Generate valid login data
        fc.record({
          username: fc.string({ minLength: 3, maxLength: 20 }).filter(s => s.trim().length >= 3),
          password: fc.string({ minLength: 8, maxLength: 50 }),
        }),
        async (registerData, loginData) => {
          // Test registration API call
          vi.mocked(apiClient.post).mockResolvedValueOnce({ data: {} });
          
          await authService.register(registerData);
          
          // Verify registration endpoint and data format
          expect(apiClient.post).toHaveBeenCalledWith('/auth/register/', registerData);
          expect(apiClient.post).toHaveBeenCalledWith(
            '/auth/register/',
            expect.objectContaining({
              username: expect.any(String),
              name: expect.any(String),
              password: expect.any(String),
            })
          );

          // Clear mocks for login test
          vi.clearAllMocks();

          // Test login API call
          const mockTokenResponse: TokenResponse = {
            access: 'mock-access-token',
            refresh: 'mock-refresh-token',
            user_id: 1,
            username: loginData.username,
          };
          
          vi.mocked(apiClient.post).mockResolvedValueOnce({ data: mockTokenResponse });
          
          const result = await authService.login(loginData);
          
          // Verify login endpoint and data format
          expect(apiClient.post).toHaveBeenCalledWith('/auth/login/', loginData);
          expect(apiClient.post).toHaveBeenCalledWith(
            '/auth/login/',
            expect.objectContaining({
              username: expect.any(String),
              password: expect.any(String),
            })
          );
          
          // Verify response structure
          expect(result).toHaveProperty('access');
          expect(result).toHaveProperty('refresh');
          expect(result).toHaveProperty('user_id');
          expect(result).toHaveProperty('username');
        }
      ),
      { numRuns: 100 }
    );
  });
});
