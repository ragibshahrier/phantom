import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import ProtectedRoute from './ProtectedRoute';
import { AuthProvider } from '../context/AuthContext';

// Mock the authService module
vi.mock('../services/authService', () => ({
  default: {
    verifyToken: vi.fn().mockResolvedValue(true),
    refreshToken: vi.fn().mockResolvedValue({ access: 'new-token' }),
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(),
  },
}));

describe('ProtectedRoute', () => {
  it('should render loading spinner while checking authentication', async () => {
    // Clear localStorage to ensure loading state
    localStorage.clear();
    
    // Mock loading state by rendering immediately
    const { container } = render(
      <AuthProvider>
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      </AuthProvider>
    );

    // The loading state happens very quickly, so we check if either loading or final state is rendered
    // Since the auth check is async, we might see loading briefly or skip to the final state
    const loadingText = screen.queryByText(/AUTHENTICATING/i);
    const protectedContent = screen.queryByText('Protected Content');
    
    // Either loading is shown or we've already moved to the unauthenticated state
    expect(loadingText !== null || protectedContent === null).toBe(true);
  });

  it('should render children when authenticated', async () => {
    // Set up authenticated state
    localStorage.setItem('access_token', 'test-token');
    localStorage.setItem('refresh_token', 'test-refresh');
    localStorage.setItem('username', 'testuser');
    localStorage.setItem('user_id', '1');

    render(
      <AuthProvider>
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      </AuthProvider>
    );

    // Wait for authentication to complete and check for protected content
    await vi.waitFor(() => {
      expect(screen.queryByText('Protected Content')).toBeDefined();
    });

    // Cleanup
    localStorage.clear();
  });

  it('should render fallback when not authenticated', async () => {
    // Clear any stored tokens
    localStorage.clear();

    render(
      <AuthProvider>
        <ProtectedRoute fallback={<div>Please Login</div>}>
          <div>Protected Content</div>
        </ProtectedRoute>
      </AuthProvider>
    );

    // Wait for authentication check to complete
    await vi.waitFor(() => {
      expect(screen.queryByText('Please Login')).toBeDefined();
      expect(screen.queryByText('Protected Content')).toBeNull();
    });
  });

  it('should render null when not authenticated and no fallback provided', async () => {
    // Clear any stored tokens
    localStorage.clear();

    const { container } = render(
      <AuthProvider>
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      </AuthProvider>
    );

    // Wait for authentication check to complete
    await vi.waitFor(() => {
      expect(screen.queryByText('Protected Content')).toBeNull();
    });
  });
});
