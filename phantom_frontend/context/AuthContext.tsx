import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import authService from '../services/authService';
import { AuthContextType } from '../types';

/**
 * Authentication Context
 * Provides authentication state and methods throughout the application
 */
const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * AuthProvider Props
 */
interface AuthProviderProps {
  children: ReactNode;
}

/**
 * AuthProvider Component
 * Manages authentication state and provides login/logout functionality
 * 
 * Features:
 * - User state management (username, userId)
 * - Authentication status tracking
 * - Token storage in localStorage
 * - Automatic token verification on mount
 * - Login/register/logout functions with error handling
 */
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<{ username: string; userId: number } | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  /**
   * Initialize authentication state on mount
   * Checks for stored tokens and verifies them with the backend
   */
  useEffect(() => {
    const initializeAuth = async () => {
      console.log('AuthContext: Initializing auth...');
      setLoading(true);
      
      try {
        // Check for stored access token
        const accessToken = localStorage.getItem('access_token');
        const refreshToken = localStorage.getItem('refresh_token');
        const storedUsername = localStorage.getItem('username');
        const storedUserId = localStorage.getItem('user_id');

        console.log('AuthContext: Stored tokens:', { 
          hasAccessToken: !!accessToken, 
          hasRefreshToken: !!refreshToken,
          username: storedUsername 
        });

        if (!accessToken || !refreshToken || !storedUsername || !storedUserId) {
          // No stored credentials, user is not authenticated
          console.log('AuthContext: No stored credentials, showing login');
          setLoading(false);
          return;
        }

        // Try to verify the access token with the backend
        try {
          console.log('AuthContext: Verifying token...');
          const isValid = await authService.verifyToken(accessToken);
          console.log('AuthContext: Token valid:', isValid);

          if (isValid) {
            // Token is valid, auto-login the user
            setUser({
              username: storedUsername,
              userId: parseInt(storedUserId, 10),
            });
            setIsAuthenticated(true);
            console.log('AuthContext: Auto-login successful');
          } else {
            // Access token is invalid, attempt to refresh
            console.log('AuthContext: Token invalid, attempting refresh...');
            try {
              const refreshResponse = await authService.refreshToken(refreshToken);
              
              // Store new access token
              localStorage.setItem('access_token', refreshResponse.access);
              
              // Auto-login with existing user data
              setUser({
                username: storedUsername,
                userId: parseInt(storedUserId, 10),
              });
              setIsAuthenticated(true);
              console.log('AuthContext: Token refresh successful');
            } catch (refreshError) {
              // Refresh failed, clear storage and require re-authentication
              console.log('AuthContext: Token refresh failed, clearing storage');
              localStorage.removeItem('access_token');
              localStorage.removeItem('refresh_token');
              localStorage.removeItem('username');
              localStorage.removeItem('user_id');
              setUser(null);
              setIsAuthenticated(false);
            }
          }
        } catch (verifyError) {
          // If verification fails (e.g., network error), just clear and show login
          console.error('AuthContext: Token verification error:', verifyError);
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('username');
          localStorage.removeItem('user_id');
          setUser(null);
          setIsAuthenticated(false);
        }
      } catch (error) {
        // Error during initialization, clear auth state
        console.error('Auth initialization error:', error);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('username');
        localStorage.removeItem('user_id');
        setUser(null);
        setIsAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, []);

  /**
   * Login function
   * Authenticates user with username and password
   * 
   * @param username - User's username
   * @param password - User's password
   * @returns Object with success status and optional error message
   */
  const login = async (
    username: string,
    password: string
  ): Promise<{ success: boolean; error?: string }> => {
    try {
      // Call login API
      const response = await authService.login({ username, password });

      // Store tokens in localStorage
      localStorage.setItem('access_token', response.access);
      localStorage.setItem('refresh_token', response.refresh);
      localStorage.setItem('username', response.username);
      localStorage.setItem('user_id', response.user_id.toString());

      // Update state
      setUser({
        username: response.username,
        userId: response.user_id,
      });
      setIsAuthenticated(true);

      return { success: true };
    } catch (error: any) {
      // Return error message
      return {
        success: false,
        error: error.message || 'Login failed. Please try again.',
      };
    }
  };

  /**
   * Register function
   * Creates a new user account
   * 
   * @param username - Desired username
   * @param name - User's full name
   * @param password - Desired password
   * @param passwordConfirm - Password confirmation
   * @returns Object with success status and optional error message
   */
  const register = async (
    username: string,
    name: string,
    password: string,
    passwordConfirm: string
  ): Promise<{ success: boolean; error?: string }> => {
    try {
      // Call register API
      await authService.register({ username, name, password, password_confirm: passwordConfirm });

      return { success: true };
    } catch (error: any) {
      // Return error message
      return {
        success: false,
        error: error.message || 'Registration failed. Please try again.',
      };
    }
  };

  /**
   * Logout function
   * Logs out the user and clears authentication data
   * Blacklists the refresh token on the backend
   */
  const logout = async (): Promise<void> => {
    try {
      // Get refresh token for blacklisting
      const refreshToken = localStorage.getItem('refresh_token');

      if (refreshToken) {
        // Call logout API to blacklist the refresh token
        await authService.logout(refreshToken);
      }
    } catch (error) {
      // Logout API call failed, but we still proceed with local cleanup
      console.error('Logout API error:', error);
    } finally {
      // Clear tokens from localStorage
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('username');
      localStorage.removeItem('user_id');

      // Clear state
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated,
    loading,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

/**
 * useAuth Hook
 * Custom hook to access authentication context
 * 
 * @throws Error if used outside of AuthProvider
 * @returns AuthContextType with user state and auth methods
 */
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
};

export default AuthContext;
