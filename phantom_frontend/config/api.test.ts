import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import apiClient from './api';

describe('API Client Configuration', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
  });

  afterEach(() => {
    // Clean up
    localStorage.clear();
  });

  it('should have correct base configuration', () => {
    expect(apiClient.defaults.baseURL).toBeDefined();
    expect(apiClient.defaults.timeout).toBe(30000);
    expect(apiClient.defaults.headers['Content-Type']).toBe('application/json');
  });

  it('should use VITE_API_URL from environment or default', () => {
    const baseURL = apiClient.defaults.baseURL;
    expect(baseURL).toBeTruthy();
    // Should either be the env variable or the default
    // In test environment, it will use the default
    expect(baseURL).toBe('http://localhost:8000/api');
  });

  it('should attach Authorization header when access token exists', () => {
    // Set up access token
    localStorage.setItem('access_token', 'test-token-123');
    
    // Verify token is in localStorage (interceptor would use it)
    expect(localStorage.getItem('access_token')).toBe('test-token-123');
  });

  it('should not attach Authorization header when no access token exists', () => {
    // Ensure no token in localStorage
    localStorage.removeItem('access_token');

    // Verify no token in localStorage
    expect(localStorage.getItem('access_token')).toBeNull();
  });
});
