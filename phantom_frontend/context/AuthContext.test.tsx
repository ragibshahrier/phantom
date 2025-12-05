import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from './AuthContext';
import authService from '../services/authService';
import React from 'react';

// Mock the authService
vi.mock('../services/authService', () => ({
  default: {
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(),
    verifyToken: vi.fn(),
    refreshToken: vi.fn(),
  },
}));

describe('AuthContext', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    vi.clearAllMocks();
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('should initialize with unauthenticated state when no tokens exist', async () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper: ({ children }) => <AuthProvider>{children}</AuthProvider>,
    });

    // Wait for initialization to complete
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // Should be unauthenticated
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBe(null);
  });

  it('should auto-login when valid tokens exist', async () => {
    // Setup localStorage with tokens
    localStorage.setItem('access_token', 'valid_access_token');
    localStorage.setItem('refresh_token', 'valid_refresh_token');
    localStorage.setItem('username', 'testuser');
    localStorage.setItem('user_id', '123');

    // Mock verifyToken to return true
    vi.mocked(authService.verifyToken).mockResolvedValue(true);

    const { result } = renderHook(() => useAuth(), {
      wrapper: ({ children }) => <AuthProvider>{children}</AuthProvider>,
    });

    // Wait for initialization to complete
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // Should be authenticated
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).toEqual({
      username: 'testuser',
      userId: 123,
    });
  });

  it('should attempt token refresh when access token is invalid', async () => {
    // Setup localStorage with tokens
    localStorage.setItem('access_token', 'invalid_access_token');
    localStorage.setItem('refresh_token', 'valid_refresh_token');
    localStorage.setItem('username', 'testuser');
    localStorage.setItem('user_id', '123');

    // Mock verifyToken to return false (invalid)
    vi.mocked(authService.verifyToken).mockResolvedValue(false);
    
    // Mock refreshToken to succeed
    vi.mocked(authService.refreshToken).mockResolvedValue({
      access: 'new_access_token',
    });

    const { result } = renderHook(() => useAuth(), {
      wrapper: ({ children }) => <AuthProvider>{children}</AuthProvider>,
    });

    // Wait for initialization to complete
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // Should be authenticated after refresh
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).toEqual({
      username: 'testuser',
      userId: 123,
    });
    
    // Should have stored new access token
    expect(localStorage.getItem('access_token')).toBe('new_access_token');
  });

  it('should clear storage when token refresh fails', async () => {
    // Setup localStorage with tokens
    localStorage.setItem('access_token', 'invalid_access_token');
    localStorage.setItem('refresh_token', 'invalid_refresh_token');
    localStorage.setItem('username', 'testuser');
    localStorage.setItem('user_id', '123');

    // Mock verifyToken to return false
    vi.mocked(authService.verifyToken).mockResolvedValue(false);
    
    // Mock refreshToken to fail
    vi.mocked(authService.refreshToken).mockRejectedValue(new Error('Refresh failed'));

    const { result } = renderHook(() => useAuth(), {
      wrapper: ({ children }) => <AuthProvider>{children}</AuthProvider>,
    });

    // Wait for initialization to complete
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // Should be unauthenticated
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBe(null);
    
    // Should have cleared localStorage
    expect(localStorage.getItem('access_token')).toBe(null);
    expect(localStorage.getItem('refresh_token')).toBe(null);
    expect(localStorage.getItem('username')).toBe(null);
    expect(localStorage.getItem('user_id')).toBe(null);
  });

  it('should login successfully and store tokens', async () => {
    // Mock login to succeed
    vi.mocked(authService.login).mockResolvedValue({
      access: 'new_access_token',
      refresh: 'new_refresh_token',
      user_id: 456,
      username: 'newuser',
    });

    const { result } = renderHook(() => useAuth(), {
      wrapper: ({ children }) => <AuthProvider>{children}</AuthProvider>,
    });

    // Wait for initialization
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // Call login
    const loginResult = await result.current.login('newuser', 'password123');

    // Should succeed
    expect(loginResult.success).toBe(true);
    expect(loginResult.error).toBeUndefined();

    // Wait for state to update
    await waitFor(() => {
      expect(result.current.isAuthenticated).toBe(true);
    });

    // Should be authenticated
    expect(result.current.user).toEqual({
      username: 'newuser',
      userId: 456,
    });

    // Should have stored tokens
    expect(localStorage.getItem('access_token')).toBe('new_access_token');
    expect(localStorage.getItem('refresh_token')).toBe('new_refresh_token');
    expect(localStorage.getItem('username')).toBe('newuser');
    expect(localStorage.getItem('user_id')).toBe('456');
  });

  it('should handle login failure', async () => {
    // Mock login to fail
    vi.mocked(authService.login).mockRejectedValue(new Error('Invalid credentials'));

    const { result } = renderHook(() => useAuth(), {
      wrapper: ({ children }) => <AuthProvider>{children}</AuthProvider>,
    });

    // Wait for initialization
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // Call login
    const loginResult = await result.current.login('baduser', 'badpass');

    // Should fail
    expect(loginResult.success).toBe(false);
    expect(loginResult.error).toBe('Invalid credentials');

    // Should remain unauthenticated
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBe(null);
  });

  it('should register successfully', async () => {
    // Mock register to succeed
    vi.mocked(authService.register).mockResolvedValue(undefined);

    const { result } = renderHook(() => useAuth(), {
      wrapper: ({ children }) => <AuthProvider>{children}</AuthProvider>,
    });

    // Wait for initialization
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // Call register
    const registerResult = await result.current.register('newuser', 'New User', 'password123');

    // Should succeed
    expect(registerResult.success).toBe(true);
    expect(registerResult.error).toBeUndefined();
  });

  it('should handle registration failure', async () => {
    // Mock register to fail
    vi.mocked(authService.register).mockRejectedValue(new Error('Username already exists'));

    const { result } = renderHook(() => useAuth(), {
      wrapper: ({ children }) => <AuthProvider>{children}</AuthProvider>,
    });

    // Wait for initialization
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // Call register
    const registerResult = await result.current.register('existinguser', 'Existing User', 'password123');

    // Should fail
    expect(registerResult.success).toBe(false);
    expect(registerResult.error).toBe('Username already exists');
  });

  it('should logout and clear authentication data', async () => {
    // Setup authenticated state
    localStorage.setItem('access_token', 'access_token');
    localStorage.setItem('refresh_token', 'refresh_token');
    localStorage.setItem('username', 'testuser');
    localStorage.setItem('user_id', '123');

    vi.mocked(authService.verifyToken).mockResolvedValue(true);
    vi.mocked(authService.logout).mockResolvedValue(undefined);

    const { result } = renderHook(() => useAuth(), {
      wrapper: ({ children }) => <AuthProvider>{children}</AuthProvider>,
    });

    // Wait for initialization (should auto-login)
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.isAuthenticated).toBe(true);

    // Call logout
    await result.current.logout();

    // Wait for state to update
    await waitFor(() => {
      expect(result.current.isAuthenticated).toBe(false);
    });

    // Should be unauthenticated
    expect(result.current.user).toBe(null);

    // Should have cleared localStorage
    expect(localStorage.getItem('access_token')).toBe(null);
    expect(localStorage.getItem('refresh_token')).toBe(null);
    expect(localStorage.getItem('username')).toBe(null);
    expect(localStorage.getItem('user_id')).toBe(null);

    // Should have called logout API
    expect(authService.logout).toHaveBeenCalledWith('refresh_token');
  });

  it('should throw error when useAuth is used outside AuthProvider', () => {
    expect(() => {
      renderHook(() => useAuth());
    }).toThrow('useAuth must be used within an AuthProvider');
  });
});
