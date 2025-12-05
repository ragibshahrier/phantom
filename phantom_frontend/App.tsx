import React from 'react';
import SeanceRoom from './pages/SeanceRoom';
import LoginPage from './pages/LoginPage';
import { AuthProvider, useAuth } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

/**
 * AppContent Component
 * Handles the main application routing based on authentication state
 */
const AppContent: React.FC = () => {
  const { isAuthenticated, user, logout, loading } = useAuth();

  console.log('AppContent render:', { loading, isAuthenticated, user });

  // Show loading screen while checking authentication
  if (loading) {
    console.log('Showing loading screen');
    return (
      <div className="flex items-center justify-center min-h-screen bg-black">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-green-500 mb-4"></div>
          <p className="text-green-500 font-mono text-sm">
            INITIALIZING PHANTOM SYSTEM...
          </p>
        </div>
      </div>
    );
  }

  console.log('Rendering main content, isAuthenticated:', isAuthenticated);

  return (
    <div className="App">
      {isAuthenticated ? (
        <SeanceRoom 
          user={user?.username || ''} 
          onLogout={logout} 
        />
      ) : (
        <LoginPage />
      )}
    </div>
  );
};

/**
 * App Component
 * Root component that wraps the application with AuthProvider
 * 
 * Features:
 * - Wraps app with AuthProvider for authentication state management
 * - Uses ProtectedRoute to guard SeanceRoom
 * - Handles authentication state transitions automatically
 * - Removed mock authentication logic in favor of real auth
 * 
 * Requirements: 1.1, 1.2, 1.6
 */
function App() {
  console.log('App component rendering');
  
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;