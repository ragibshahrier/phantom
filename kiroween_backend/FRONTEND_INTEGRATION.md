# Connecting React Frontend to Phantom Scheduler Backend

This guide will help you integrate your React frontend with the Phantom Scheduler Django backend.

## Table of Contents

- [Backend Setup](#backend-setup)
- [Frontend Configuration](#frontend-configuration)
- [API Integration](#api-integration)
- [Authentication Flow](#authentication-flow)
- [Example Components](#example-components)
- [Error Handling](#error-handling)
- [Testing the Integration](#testing-the-integration)

## Backend Setup

### 1. Configure CORS

The backend is already configured for CORS. Update your `.env` file to include your React frontend URL:

```env
# Add your React dev server URL
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# For production, add your production domain
# CORS_ALLOWED_ORIGINS=https://yourfrontend.com,https://www.yourfrontend.com
```

### 2. Start Backend Services

Open 3 terminals and run:

**Terminal 1 - Django Server:**
```bash
cd phantom-scheduler
source venv/bin/activate  # On Windows: venv\Scripts\activate
python manage.py runserver
```

**Terminal 2 - Redis:**
```bash
redis-server
```

**Terminal 3 - Celery Worker:**
```bash
cd phantom-scheduler
source venv/bin/activate
celery -A phantom worker -l info
```

### 3. Verify Backend is Running

Visit http://localhost:8000/api/docs/ to confirm the API is accessible.

## Frontend Configuration

### 1. Install Required Packages

In your React project directory:

```bash
# Using npm
npm install axios react-router-dom

# Using yarn
yarn add axios react-router-dom
```

### 2. Create API Configuration

Create `src/config/api.js`:

```javascript
// src/config/api.js
import axios from 'axios';

// Base API URL
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If error is 401 and we haven't tried to refresh yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken,
          });

          const { access } = response.data;
          localStorage.setItem('access_token', access);

          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, logout user
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
```

### 3. Create Environment File

Create `.env` in your React project root:

```env
REACT_APP_API_URL=http://localhost:8000/api
```

## API Integration

### 1. Create API Service

Create `src/services/phantomApi.js`:

```javascript
// src/services/phantomApi.js
import api from '../config/api';

// Authentication
export const authService = {
  register: (username, name, password) =>
    api.post('/auth/register/', { username, name, password }),

  login: (username, password) =>
    api.post('/auth/login/', { username, password }),

  logout: (refreshToken) =>
    api.post('/auth/logout/', { refresh: refreshToken }),

  refreshToken: (refreshToken) =>
    api.post('/auth/token/refresh/', { refresh: refreshToken }),

  verifyToken: (token) =>
    api.post('/auth/token/verify/', { token }),
};

// Events
export const eventService = {
  getEvents: (params) =>
    api.get('/events/', { params }),

  getEvent: (id) =>
    api.get(`/events/${id}/`),

  createEvent: (eventData) =>
    api.post('/events/', eventData),

  updateEvent: (id, eventData) =>
    api.put(`/events/${id}/`, eventData),

  deleteEvent: (id) =>
    api.delete(`/events/${id}/`),

  getEventsByDateRange: (startDate, endDate) =>
    api.get('/events/', {
      params: {
        start_date: startDate,
        end_date: endDate,
      },
    }),
};

// Natural Language Chat
export const chatService = {
  sendMessage: (message) =>
    api.post('/chat/', { message }),

  getConversationHistory: () =>
    api.get('/chat/history/'),
};

// Categories
export const categoryService = {
  getCategories: () =>
    api.get('/categories/'),

  getCategory: (id) =>
    api.get(`/categories/${id}/`),

  createCategory: (categoryData) =>
    api.post('/categories/', categoryData),
};

// User Preferences
export const preferenceService = {
  getPreferences: () =>
    api.get('/preferences/'),

  updatePreferences: (preferences) =>
    api.put('/preferences/', preferences),
};

// Google Calendar Integration
export const integrationService = {
  connectGoogleCalendar: () =>
    api.get('/integrations/google/connect/'),

  getGoogleCalendarStatus: () =>
    api.get('/integrations/google/status/'),

  disconnectGoogleCalendar: () =>
    api.post('/integrations/google/disconnect/'),
};

export default {
  auth: authService,
  events: eventService,
  chat: chatService,
  categories: categoryService,
  preferences: preferenceService,
  integrations: integrationService,
};
```

## Authentication Flow

### 1. Create Auth Context

Create `src/context/AuthContext.js`:

```javascript
// src/context/AuthContext.js
import React, { createContext, useState, useContext, useEffect } from 'react';
import { authService } from '../services/phantomApi';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in on mount
    const token = localStorage.getItem('access_token');
    if (token) {
      // Verify token is still valid
      authService
        .verifyToken(token)
        .then(() => {
          // Token is valid, user is logged in
          const username = localStorage.getItem('username');
          setUser({ username });
        })
        .catch(() => {
          // Token is invalid, clear storage
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('username');
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (username, password) => {
    try {
      const response = await authService.login(username, password);
      const { access, refresh } = response.data;

      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      localStorage.setItem('username', username);

      setUser({ username });
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed',
      };
    }
  };

  const register = async (username, name, password) => {
    try {
      await authService.register(username, name, password);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data || 'Registration failed',
      };
    }
  };

  const logout = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        await authService.logout(refreshToken);
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('username');
      setUser(null);
    }
  };

  const value = {
    user,
    login,
    register,
    logout,
    loading,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

### 2. Wrap App with Auth Provider

Update `src/App.js` or `src/main.jsx`:

```javascript
// src/App.js
import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import AppRoutes from './routes';

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </Router>
  );
}

export default App;
```

## Example Components

### 1. Login Component

Create `src/components/Login.jsx`:

```javascript
// src/components/Login.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = await login(username, password);

    if (result.success) {
      navigate('/dashboard');
    } else {
      setError(result.error);
    }

    setLoading(false);
  };

  return (
    <div className="login-container">
      <h2>Login to Phantom Scheduler</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Username:</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Password:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        {error && <div className="error">{error}</div>}
        <button type="submit" disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
    </div>
  );
};

export default Login;
```

### 2. Event List Component

Create `src/components/EventList.jsx`:

```javascript
// src/components/EventList.jsx
import React, { useState, useEffect } from 'react';
import { eventService } from '../services/phantomApi';

const EventList = () => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
    try {
      setLoading(true);
      const response = await eventService.getEvents();
      setEvents(response.data.results || response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch events');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (eventId) => {
    if (window.confirm('Are you sure you want to delete this event?')) {
      try {
        await eventService.deleteEvent(eventId);
        setEvents(events.filter((event) => event.id !== eventId));
      } catch (err) {
        alert('Failed to delete event');
        console.error(err);
      }
    }
  };

  if (loading) return <div>Loading events...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="event-list">
      <h2>Your Events</h2>
      {events.length === 0 ? (
        <p>No events scheduled yet.</p>
      ) : (
        <ul>
          {events.map((event) => (
            <li key={event.id} className="event-item">
              <h3>{event.title}</h3>
              <p>{event.description}</p>
              <p>
                <strong>Start:</strong> {new Date(event.start_time).toLocaleString()}
              </p>
              <p>
                <strong>End:</strong> {new Date(event.end_time).toLocaleString()}
              </p>
              <p>
                <strong>Category:</strong> {event.category_name}
              </p>
              <button onClick={() => handleDelete(event.id)}>Delete</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default EventList;
```

### 3. Chat Component (Natural Language)

Create `src/components/Chat.jsx`:

```javascript
// src/components/Chat.jsx
import React, { useState } from 'react';
import { chatService } from '../services/phantomApi';

const Chat = ({ onEventCreated }) => {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const result = await chatService.sendMessage(message);
      setResponse(result.data.response);
      
      // If events were created, notify parent component
      if (result.data.events_created && onEventCreated) {
        onEventCreated(result.data.events_created);
      }
      
      setMessage('');
    } catch (err) {
      setError('Failed to process message. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <h2>Chat with Phantom</h2>
      <p className="chat-intro">
        <em>"Good evening. How may I assist with your schedule today?"</em>
      </p>

      <form onSubmit={handleSubmit}>
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="e.g., Schedule a study session tomorrow at 2pm for 2 hours"
          rows="3"
          disabled={loading}
        />
        <button type="submit" disabled={loading || !message.trim()}>
          {loading ? 'Processing...' : 'Send'}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {response && (
        <div className="chat-response">
          <h3>Phantom's Response:</h3>
          <p>{response}</p>
        </div>
      )}
    </div>
  );
};

export default Chat;
```

### 4. Protected Route Component

Create `src/components/ProtectedRoute.jsx`:

```javascript
// src/components/ProtectedRoute.jsx
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;
```

## Error Handling

### Create Error Boundary

Create `src/components/ErrorBoundary.jsx`:

```javascript
// src/components/ErrorBoundary.jsx
import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => window.location.reload()}>
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
```

## Testing the Integration

### 1. Start Both Servers

**Backend (Terminal 1):**
```bash
cd phantom-scheduler
python manage.py runserver
```

**Frontend (Terminal 2):**
```bash
cd your-react-app
npm start
```

### 2. Test Authentication Flow

1. Navigate to `http://localhost:3000/register`
2. Register a new user
3. Login with credentials
4. Verify you're redirected to dashboard

### 3. Test Event Creation

**Via Chat:**
```
"Schedule a study session tomorrow at 2pm for 2 hours"
```

**Via Direct API:**
- Use the EventList component to view events
- Create events using a form component

### 4. Test Token Refresh

1. Login and wait 15 minutes (access token expires)
2. Make an API call
3. Verify token is automatically refreshed

## Common Issues and Solutions

### CORS Errors

**Problem:** `Access to XMLHttpRequest blocked by CORS policy`

**Solution:**
1. Verify backend `.env` has correct `CORS_ALLOWED_ORIGINS`
2. Restart Django server after changing `.env`
3. Check browser console for exact origin being blocked

### 401 Unauthorized

**Problem:** API returns 401 even with token

**Solution:**
1. Check token is being sent: Open DevTools → Network → Headers
2. Verify token format: `Bearer <token>`
3. Check token hasn't expired
4. Try logging out and back in

### Network Error

**Problem:** `Network Error` or `ERR_CONNECTION_REFUSED`

**Solution:**
1. Verify backend is running: `http://localhost:8000/api/docs/`
2. Check `REACT_APP_API_URL` in `.env`
3. Ensure no firewall blocking requests

## Next Steps

1. **Add More Components:**
   - Event creation form
   - Calendar view
   - User preferences page
   - Google Calendar integration UI

2. **Improve UX:**
   - Add loading states
   - Implement toast notifications
   - Add form validation
   - Improve error messages

3. **State Management:**
   - Consider Redux or Zustand for complex state
   - Implement React Query for data fetching

4. **Testing:**
   - Write unit tests for components
   - Add integration tests
   - Test error scenarios

## Additional Resources

- **Backend API Docs:** http://localhost:8000/api/docs/
- **Backend README:** [README.md](README.md)
- **React Documentation:** https://react.dev/
- **Axios Documentation:** https://axios-http.com/

---

**Need Help?**

If you encounter issues:
1. Check browser console for errors
2. Check Django server logs
3. Verify all environment variables are set
4. Review the API documentation at `/api/docs/`

*"Your frontend integration is proceeding splendidly. I shall ensure seamless communication between the realms."* - Phantom
