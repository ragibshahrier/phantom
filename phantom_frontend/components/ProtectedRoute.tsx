import React, { ReactNode } from 'react';
import { useAuth } from '../context/AuthContext';

/**
 * ProtectedRoute Props
 */
interface ProtectedRouteProps {
  children: ReactNode;
  fallback?: ReactNode;
}

/**
 * ProtectedRoute Component
 * 
 * Protects routes by checking authentication status from AuthContext.
 * - Shows loading spinner while checking authentication
 * - Renders children if user is authenticated
 * - Renders fallback (or null) if user is not authenticated
 * 
 * Requirements: 1.1, 12.1
 * 
 * @param children - The protected content to render when authenticated
 * @param fallback - Optional component to render when not authenticated (defaults to null)
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, fallback = null }) => {
  const { isAuthenticated, loading } = useAuth();

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-black">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-green-500 mb-4"></div>
          <p className="text-green-500 font-mono text-sm">
            AUTHENTICATING...
          </p>
        </div>
      </div>
    );
  }

  // Render children if authenticated, otherwise render fallback
  if (isAuthenticated) {
    return <>{children}</>;
  }

  return <>{fallback}</>;
};

export default ProtectedRoute;
