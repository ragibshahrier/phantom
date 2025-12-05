# Design Document

## Overview

The Phantom Frontend Integration design provides a comprehensive architecture for connecting the existing React-based frontend with the Django REST API backend. The design maintains the unique Victorian Ghost Butler aesthetic while implementing robust API communication, state management, authentication flows, and error handling. The integration will transform the current mock implementation into a fully functional scheduling application with real-time data synchronization, natural language processing capabilities, and seamless user experience across devices.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (Vite)                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Presentation Layer                        │ │
│  │  - Pages (LoginPage, SeanceRoom)                      │ │
│  │  - Components (Monolith, Calendar, Chat, etc.)        │ │
│  │  - Styling (Tailwind CSS, Framer Motion)              │ │
│  └────────────────┬───────────────────────────────────────┘ │
│                   │                                          │
│  ┌────────────────▼───────────────────────────────────────┐ │
│  │              State Management Layer                    │ │
│  │  - Auth Context (user, tokens, login/logout)          │ │
│  │  - Event State (events, categories, preferences)      │ │
│  │  - Chat State (messages, history)                     │ │
│  └────────────────┬───────────────────────────────────────┘ │
│                   │                                          │
│  ┌────────────────▼───────────────────────────────────────┐ │
│  │              Service Layer                             │ │
│  │  - API Client (Axios with interceptors)               │ │
│  │  - Auth Service (register, login, logout, refresh)    │ │
│  │  - Event Service (CRUD operations)                    │ │
│  │  - Chat Service (natural language processing)         │ │
│  │  - Category Service (fetch categories)                │ │
│  │  - Preference Service (get/update preferences)        │ │
│  │  - Integration Service (Google Calendar)              │ │
│  └────────────────┬───────────────────────────────────────┘ │
└────────────────────┼───────────────────────────────────────┘
                     │ HTTP/REST (JSON)
                     │ Authorization: Bearer {token}
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Django REST Framework Backend                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  API Endpoints                                         │ │
│  │  - /api/auth/* (register, login, logout, refresh)     │ │
│  │  - /api/events/* (CRUD operations)                    │ │
│  │  - /api/chat/ (natural language processing)           │ │
│  │  - /api/categories/* (category management)            │ │
│  │  - /api/preferences/ (user preferences)               │ │
│  │  - /api/integrations/google/* (calendar sync)         │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Component Architecture

```
App.tsx
├── AuthProvider (Context)
│   ├── LoginPage
│   │   ├── CRTScanlines
│   │   └── Login Form
│   └── ProtectedRoute
│       └── SeanceRoom
│           ├── CRTScanlines
│           ├── GhostOverlay
│           ├── Chat Panel (Left)
│           │   ├── Chat History
│           │   └── TerminalInput
│           └── Timeline/Calendar Panel (Right)
│               ├── DoomsdayCalendar
│               └── Monolith (Event Cards)
```

## Components and Interfaces

### 1. API Client Configuration

**File:** `src/config/api.ts`

The API client is built on Axios with request/response interceptors for automatic token management.

**Configuration:**
```typescript
interface ApiConfig {
  baseURL: string;
  timeout: number;
  headers: {
    'Content-Type': string;
  };
}

const config: ApiConfig = {
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
};
```

**Request Interceptor:**
- Retrieves access token from localStorage
- Attaches token to Authorization header as "Bearer {token}"
- Allows requests to proceed

**Response Interceptor:**
- On 401 Unauthorized: Attempts token refresh
- On successful refresh: Retries original request with new token
- On refresh failure: Clears auth data and redirects to login
- On other errors: Passes error to caller

### 2. Authentication Service

**File:** `src/services/authService.ts`

**Interface:**
```typescript
interface RegisterData {
  username: string;
  name: string;
  password: string;
}

interface LoginData {
  username: string;
  password: string;
}

interface TokenResponse {
  access: string;
  refresh: string;
  user_id: number;
  username: string;
}

interface AuthService {
  register(data: RegisterData): Promise<void>;
  login(data: LoginData): Promise<TokenResponse>;
  logout(refreshToken: string): Promise<void>;
  refreshToken(refreshToken: string): Promise<{ access: string }>;
  verifyToken(token: string): Promise<boolean>;
}
```

**Methods:**
- `register()`: POST to `/api/auth/register/`
- `login()`: POST to `/api/auth/login/`, returns tokens
- `logout()`: POST to `/api/auth/logout/`, blacklists refresh token
- `refreshToken()`: POST to `/api/auth/token/refresh/`, returns new access token
- `verifyToken()`: Validates token is still valid

### 3. Event Service

**File:** `src/services/eventService.ts`

**Interface:**
```typescript
interface Event {
  id: number;
  title: string;
  description: string;
  category: number;
  category_name: string;
  category_color: string;
  start_time: string; // ISO 8601
  end_time: string; // ISO 8601
  is_flexible: boolean;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
}

interface EventCreateData {
  title: string;
  description?: string;
  category: number;
  start_time: string;
  end_time: string;
  is_flexible?: boolean;
}

interface EventQueryParams {
  start_date?: string;
  end_date?: string;
  category?: number;
  priority?: number;
}

interface EventService {
  getEvents(params?: EventQueryParams): Promise<Event[]>;
  getEvent(id: number): Promise<Event>;
  createEvent(data: EventCreateData): Promise<Event>;
  updateEvent(id: number, data: Partial<EventCreateData>): Promise<Event>;
  deleteEvent(id: number): Promise<void>;
}
```

### 4. Chat Service

**File:** `src/services/chatService.ts`

**Interface:**
```typescript
interface ChatMessage {
  message: string;
}

interface ChatResponse {
  response: string;
  events_created?: Event[];
  events_modified?: Event[];
  intent_detected?: string;
}

interface ConversationHistoryItem {
  id: number;
  message: string;
  response: string;
  intent_detected: string;
  timestamp: string;
}

interface ChatService {
  sendMessage(message: string): Promise<ChatResponse>;
  getConversationHistory(): Promise<ConversationHistoryItem[]>;
}
```

### 5. Category Service

**File:** `src/services/categoryService.ts`

**Interface:**
```typescript
interface Category {
  id: number;
  name: string;
  priority_level: number;
  color: string;
  description: string;
}

interface CategoryService {
  getCategories(): Promise<Category[]>;
  getCategory(id: number): Promise<Category>;
}
```

### 6. Preference Service

**File:** `src/services/preferenceService.ts`

**Interface:**
```typescript
interface UserPreferences {
  timezone: string;
  default_event_duration: number; // minutes
}

interface PreferenceService {
  getPreferences(): Promise<UserPreferences>;
  updatePreferences(data: Partial<UserPreferences>): Promise<UserPreferences>;
}
```

### 7. Integration Service

**File:** `src/services/integrationService.ts`

**Interface:**
```typescript
interface GoogleCalendarStatus {
  connected: boolean;
  email?: string;
}

interface IntegrationService {
  connectGoogleCalendar(): Promise<{ authorization_url: string }>;
  getGoogleCalendarStatus(): Promise<GoogleCalendarStatus>;
  disconnectGoogleCalendar(): Promise<void>;
}
```

### 8. Auth Context

**File:** `src/context/AuthContext.tsx`

**Interface:**
```typescript
interface AuthContextType {
  user: { username: string; userId: number } | null;
  isAuthenticated: boolean;
  loading: boolean;
  login(username: string, password: string): Promise<{ success: boolean; error?: string }>;
  register(username: string, name: string, password: string): Promise<{ success: boolean; error?: string }>;
  logout(): Promise<void>;
}
```

**State Management:**
- Stores current user information
- Manages authentication status
- Provides login/logout functions to components
- Handles token storage in localStorage
- Verifies token on app initialization

### 9. Event State Hook

**File:** `src/hooks/useEvents.ts`

**Interface:**
```typescript
interface UseEventsReturn {
  events: Event[];
  loading: boolean;
  error: string | null;
  fetchEvents(params?: EventQueryParams): Promise<void>;
  createEvent(data: EventCreateData): Promise<Event | null>;
  updateEvent(id: number, data: Partial<EventCreateData>): Promise<Event | null>;
  deleteEvent(id: number): Promise<boolean>;
  refreshEvents(): Promise<void>;
}
```

### 10. Chat State Hook

**File:** `src/hooks/useChat.ts`

**Interface:**
```typescript
interface ChatHistoryItem {
  id: string;
  sender: 'USER' | 'PHANTOM' | 'SYSTEM';
  text: string;
  timestamp: Date;
}

interface UseChatReturn {
  chatHistory: ChatHistoryItem[];
  isLoading: boolean;
  error: string | null;
  sendMessage(message: string): Promise<void>;
  clearHistory(): void;
}
```

## Data Models

### Frontend Data Models

**Event Model:**
```typescript
interface Event {
  id: number;
  title: string;
  description: string;
  category: number;
  category_name: string;
  category_color: string;
  priority_level: number;
  start_time: string; // ISO 8601 format
  end_time: string; // ISO 8601 format
  is_flexible: boolean;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
}
```

**Category Model:**
```typescript
interface Category {
  id: number;
  name: string;
  priority_level: number; // 1-5, higher is more important
  color: string; // Hex color code
  description: string;
}
```

**User Model:**
```typescript
interface User {
  id: number;
  username: string;
  name: string;
  timezone: string;
  default_event_duration: number;
}
```

**Chat Message Model:**
```typescript
interface ChatMessage {
  id: string; // UUID
  sender: 'USER' | 'PHANTOM' | 'SYSTEM';
  text: string;
  timestamp: Date;
  events_created?: Event[];
  events_modified?: Event[];
}
```

### Data Transformation

**Backend to Frontend:**
- Convert ISO 8601 date strings to Date objects for display
- Flatten nested category data into event objects
- Add computed properties (e.g., duration, isPast, isToday)

**Frontend to Backend:**
- Convert Date objects to ISO 8601 strings
- Extract only required fields for API requests
- Validate data before sending

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Authentication API calls are made correctly
*For any* valid registration or login credentials, the frontend should make the correct API call to the appropriate endpoint with the correct data format.
**Validates: Requirements 1.1, 1.3**

### Property 2: Successful authentication stores tokens
*For any* successful login response, the frontend should store the access token, refresh token, and username in localStorage.
**Validates: Requirements 1.4**

### Property 3: Token refresh is automatic
*For any* API request that returns 401 Unauthorized, the frontend should automatically attempt to refresh the access token using the refresh token before failing.
**Validates: Requirements 1.5, 2.3**

### Property 4: Logout clears authentication data
*For any* logout action, the frontend should send the refresh token to the backend for blacklisting and clear all authentication data from localStorage.
**Validates: Requirements 1.6**

### Property 5: Authorization header is attached to requests
*For any* authenticated API request, the frontend should automatically attach the access token in the Authorization header as "Bearer {token}".
**Validates: Requirements 2.2**

### Property 6: Failed token refresh triggers re-authentication
*For any* failed token refresh attempt, the frontend should clear all authentication data and redirect the user to the login page.
**Validates: Requirements 2.5, 2.6**

### Property 7: Events are fetched and ordered correctly
*For any* timeline view, the frontend should fetch events from the API and display them ordered by start time (earliest first).
**Validates: Requirements 3.1**

### Property 8: Event CRUD operations call correct endpoints
*For any* event create, update, or delete operation, the frontend should make the correct API call (POST, PUT, DELETE) to the appropriate endpoint with the correct data.
**Validates: Requirements 3.3, 3.4, 3.5**

### Property 9: Chat messages trigger API calls
*For any* user message in the chat interface, the frontend should send it to `/api/chat/` and display the response in the chat history.
**Validates: Requirements 4.1, 4.2**

### Property 10: Chat-created events update timeline
*For any* chat response that includes created events, the frontend should immediately update the timeline to display the new events without requiring a manual refresh.
**Validates: Requirements 4.3, 9.1**

### Property 11: Date filtering uses correct query parameters
*For any* selected date in the calendar, the frontend should fetch events using the `start_date` and `end_date` query parameters that encompass the selected date.
**Validates: Requirements 5.1**

### Property 12: Date filtering displays correct events
*For any* selected date, the frontend should display only events whose time range intersects with the selected date.
**Validates: Requirements 5.2**

### Property 13: Calendar navigation updates display
*For any* month navigation action, the frontend should update the calendar display to show the correct month with appropriate date cells.
**Validates: Requirements 5.4**

### Property 14: Categories are ordered by priority
*For any* fetched category list, the frontend should order categories by priority level with highest priority first (5 > 4 > 3 > 2 > 1).
**Validates: Requirements 6.4**

### Property 15: Critical events trigger warning banner
*For any* event with category priority level 5 (CRITICAL), the frontend should display an "IMPENDING DOOM" warning banner when that event is upcoming.
**Validates: Requirements 6.5**

### Property 16: Preference updates call API
*For any* preference modification, the frontend should send a PUT request to `/api/preferences/` with the updated settings.
**Validates: Requirements 7.2**

### Property 17: Preferences apply immediately
*For any* successful preference update, the frontend should apply the new settings immediately without requiring a page refresh.
**Validates: Requirements 7.3**

### Property 18: Timezone changes convert event times
*For any* timezone change, the frontend should display all event times converted to the new timezone.
**Validates: Requirements 7.4**

### Property 19: Loading indicators appear during requests
*For any* API request in progress, the frontend should display a loading indicator to inform the user.
**Validates: Requirements 8.1**

### Property 20: Validation errors are displayed
*For any* API request that fails with a 400 error, the frontend should extract and display the validation error messages from the backend response.
**Validates: Requirements 8.3**

### Property 21: Success operations show confirmation
*For any* successful operation (create, update, delete), the frontend should display a success message or visual confirmation to the user.
**Validates: Requirements 8.5**

### Property 22: Event deletion removes from all views
*For any* deleted event, the frontend should immediately remove it from all views (timeline, calendar) without requiring a manual refresh.
**Validates: Requirements 9.2**

### Property 23: Event updates reflect everywhere
*For any* updated event, the frontend should reflect the changes in all views where the event appears (timeline, calendar, chat).
**Validates: Requirements 9.3**

### Property 24: Tab navigation maintains state
*For any* tab switch, the frontend should maintain the current application state (selected date, filters, etc.) without making unnecessary API calls.
**Validates: Requirements 9.4**

### Property 25: Mobile tab switching shows correct view
*For any* tab selection on mobile, the frontend should display the appropriate view (Uplink, Timeline, or Prophecy) and hide others.
**Validates: Requirements 10.2**

### Property 26: Mobile calendar selection switches to timeline
*For any* date selection on mobile calendar, the frontend should automatically switch to the Timeline view to show events for that date.
**Validates: Requirements 10.3**

### Property 27: Touch gestures trigger actions
*For any* touch gesture (tap, swipe), the frontend should respond with the appropriate action (select, navigate, etc.).
**Validates: Requirements 10.5**

### Property 28: Invalid event times show validation errors
*For any* event creation or update where end time is before or equal to start time, the frontend should display a validation error and prevent submission.
**Validates: Requirements 11.2**

### Property 29: Invalid date formats show validation errors
*For any* date input with invalid format, the frontend should display a validation error and prevent submission.
**Validates: Requirements 11.3**

### Property 30: Empty required fields show validation errors
*For any* form submission with empty required fields, the frontend should highlight the fields and display error messages.
**Validates: Requirements 11.4**

### Property 31: Valid data is submitted to backend
*For any* form with valid data, the frontend should submit the data to the backend without client-side blocking.
**Validates: Requirements 11.5**

### Property 32: Valid tokens trigger auto-login
*For any* valid access token stored in localStorage, the frontend should verify it with the backend and automatically log the user in on application load.
**Validates: Requirements 12.2**

### Property 33: Expired tokens trigger refresh
*For any* expired access token stored in localStorage, the frontend should attempt to refresh it using the refresh token on application load.
**Validates: Requirements 12.3**

### Property 34: Invalid tokens trigger cleanup
*For any* invalid or expired tokens (both access and refresh), the frontend should clear localStorage and show the login page.
**Validates: Requirements 12.4**

### Property 35: Session restoration works after browser close
*For any* valid tokens stored in localStorage, the frontend should restore the authenticated session when the user returns after closing the browser.
**Validates: Requirements 12.5**

### Property 36: User messages appear with timestamps
*For any* user message sent in chat, the frontend should display it in the chat history with a timestamp.
**Validates: Requirements 13.1**

### Property 37: Phantom responses have distinct styling
*For any* Phantom response, the frontend should display it with distinct styling (color, formatting) different from user messages.
**Validates: Requirements 13.2**

### Property 38: Long chat history implements scrolling
*For any* chat history with many messages, the frontend should implement scrolling with the most recent messages visible.
**Validates: Requirements 13.4**

### Property 39: New messages trigger auto-scroll
*For any* new message added to chat history, the frontend should automatically scroll to show the new message.
**Validates: Requirements 13.5**

### Property 40: OAuth callback updates connection status
*For any* OAuth2 callback received, the frontend should handle it and display the updated Google Calendar connection status.
**Validates: Requirements 14.2**

### Property 41: Debouncing prevents rapid API calls
*For any* rapid sequence of search or filter operations, the frontend should debounce the requests to prevent excessive API calls.
**Validates: Requirements 15.2**

### Property 42: Caching reduces duplicate requests
*For any* repeated request for the same data within a short time period, the frontend should use cached data instead of making a new API call.
**Validates: Requirements 15.5**

### Property 43: Keyboard navigation shows focus indicators
*For any* keyboard navigation action, the frontend should display visible focus indicators on the currently focused interactive element.
**Validates: Requirements 16.1**

### Property 44: Tab order is logical
*For any* Tab key press, the frontend should move focus to the next interactive element in a logical order (top to bottom, left to right).
**Validates: Requirements 16.2**

### Property 45: Interactive elements have ARIA labels
*For any* interactive element (button, input, link), the frontend should provide appropriate ARIA labels for screen reader accessibility.
**Validates: Requirements 16.3**

### Property 46: Errors are announced to screen readers
*For any* error that occurs, the frontend should announce it to screen readers using appropriate ARIA live regions.
**Validates: Requirements 16.4**

### Property 47: Form feedback is accessible
*For any* form submission, the frontend should provide feedback (success or error) that is accessible to screen readers.
**Validates: Requirements 16.5**

## Error Handling

### Error Categories

**1. Network Errors**
- Connection timeout
- No internet connection
- DNS resolution failure

**Handling:**
- Display user-friendly message: "Connection failed. Please check your internet connection."
- Provide retry button
- Log error details for debugging

**2. Authentication Errors (401)**
- Invalid credentials
- Expired token
- Blacklisted token

**Handling:**
- Attempt automatic token refresh
- If refresh fails, redirect to login
- Clear stored authentication data
- Display appropriate error message

**3. Authorization Errors (403)**
- Insufficient permissions
- Account disabled

**Handling:**
- Display: "You don't have permission to perform this action."
- Log user out if account is disabled
- Provide contact support option

**4. Validation Errors (400)**
- Invalid input data
- Missing required fields
- Business rule violations

**Handling:**
- Extract error messages from backend response
- Display field-specific errors next to inputs
- Highlight invalid fields
- Prevent form submission until fixed

**5. Server Errors (500, 503)**
- Internal server error
- Service unavailable
- Database connection failure

**Handling:**
- Display: "Server error. Please try again later."
- Provide retry button
- Log error details
- Consider exponential backoff for retries

**6. Not Found Errors (404)**
- Resource doesn't exist
- Invalid URL

**Handling:**
- Display: "The requested resource was not found."
- Provide navigation back to main view
- Log error for debugging

### Error Recovery Strategies

**Automatic Retry:**
- Implement for transient network errors
- Use exponential backoff (1s, 2s, 4s, 8s)
- Maximum 3 retry attempts
- Show retry count to user

**Graceful Degradation:**
- Cache last successful data
- Display cached data with "offline" indicator
- Allow read-only operations when backend is unavailable
- Queue write operations for later sync

**User Feedback:**
- Always inform user of errors
- Provide actionable next steps
- Use consistent error message format
- Maintain Victorian Ghost Butler theme in error messages

### Error Logging

**Client-Side Logging:**
- Log all errors to console in development
- Send critical errors to monitoring service in production
- Include context: user ID, timestamp, action attempted
- Sanitize sensitive data before logging

## Testing Strategy

### Unit Testing

**Framework:** Vitest (Vite's native test runner)

**Coverage Areas:**
- Service functions (API calls, data transformation)
- Utility functions (date formatting, validation)
- Context providers (auth state management)
- Custom hooks (useEvents, useChat)

**Example Unit Tests:**
```typescript
describe('authService', () => {
  it('should format login request correctly', () => {
    // Test that login data is formatted properly
  });
  
  it('should store tokens in localStorage on successful login', () => {
    // Test token storage
  });
  
  it('should clear tokens on logout', () => {
    // Test token cleanup
  });
});

describe('eventService', () => {
  it('should transform backend event data to frontend format', () => {
    // Test data transformation
  });
  
  it('should include category information with events', () => {
    // Test data enrichment
  });
});
```

### Property-Based Testing

**Framework:** fast-check (JavaScript/TypeScript property-based testing library)

**Configuration:**
- Minimum 100 iterations per property test
- Use seed for reproducible failures
- Generate realistic test data

**Property Test Implementation:**
Each property-based test must:
1. Be tagged with a comment referencing the design document property
2. Generate random but valid test data
3. Execute the operation
4. Verify the property holds

**Example Property Tests:**
```typescript
import fc from 'fast-check';

describe('Property Tests', () => {
  it('Property 1: Authentication API calls are made correctly', () => {
    /**
     * Feature: phantom-frontend-integration, Property 1
     * For any valid registration or login credentials, the frontend should 
     * make the correct API call to the appropriate endpoint with the correct data format.
     */
    fc.assert(
      fc.property(
        fc.record({
          username: fc.string({ minLength: 3, maxLength: 20 }),
          password: fc.string({ minLength: 8, maxLength: 50 }),
        }),
        async (credentials) => {
          const mockApi = createMockApi();
          await authService.login(credentials.username, credentials.password);
          
          expect(mockApi.post).toHaveBeenCalledWith(
            '/auth/login/',
            credentials
          );
        }
      ),
      { numRuns: 100 }
    );
  });

  it('Property 8: Event CRUD operations call correct endpoints', () => {
    /**
     * Feature: phantom-frontend-integration, Property 8
     * For any event create, update, or delete operation, the frontend should 
     * make the correct API call to the appropriate endpoint with the correct data.
     */
    fc.assert(
      fc.property(
        fc.record({
          title: fc.string({ minLength: 1, maxLength: 200 }),
          description: fc.string({ maxLength: 1000 }),
          category: fc.integer({ min: 1, max: 5 }),
          start_time: fc.date(),
          end_time: fc.date(),
        }).filter(data => data.end_time > data.start_time),
        async (eventData) => {
          const mockApi = createMockApi();
          await eventService.createEvent(eventData);
          
          expect(mockApi.post).toHaveBeenCalledWith(
            '/events/',
            expect.objectContaining({
              title: eventData.title,
              category: eventData.category,
            })
          );
        }
      ),
      { numRuns: 100 }
    );
  });
});
```

### Integration Testing

**Framework:** Playwright or Cypress

**Coverage Areas:**
- Complete user flows (register → login → create event → logout)
- Authentication flow with token refresh
- Chat interface with event creation
- Calendar navigation and date filtering
- Mobile responsive behavior

**Example Integration Tests:**
```typescript
describe('Authentication Flow', () => {
  it('should complete full registration and login flow', async () => {
    // Navigate to registration
    // Fill form and submit
    // Verify redirect to login
    // Login with credentials
    // Verify redirect to dashboard
    // Verify tokens in localStorage
  });
  
  it('should automatically refresh expired token', async () => {
    // Login and store tokens
    // Manually expire access token
    // Make API request
    // Verify token refresh occurred
    // Verify request succeeded
  });
});

describe('Event Management', () => {
  it('should create event via chat and display in timeline', async () => {
    // Login
    // Send chat message: "Schedule study session tomorrow at 2pm"
    // Verify Phantom response
    // Verify event appears in timeline
    // Verify event appears in calendar
  });
});
```

### End-to-End Testing

**Coverage Areas:**
- Critical user journeys
- Cross-browser compatibility
- Mobile device testing
- Performance benchmarks

### Test Data Generators

**For Property-Based Tests:**
```typescript
// Generate valid event data
const eventGenerator = fc.record({
  title: fc.string({ minLength: 1, maxLength: 200 }),
  description: fc.option(fc.string({ maxLength: 1000 })),
  category: fc.integer({ min: 1, max: 5 }),
  start_time: fc.date({ min: new Date() }),
  end_time: fc.date({ min: new Date() }),
}).filter(data => data.end_time > data.start_time);

// Generate valid user credentials
const credentialsGenerator = fc.record({
  username: fc.string({ minLength: 3, maxLength: 20 })
    .filter(s => /^[a-zA-Z0-9_]+$/.test(s)),
  password: fc.string({ minLength: 8, maxLength: 50 }),
  name: fc.string({ minLength: 1, maxLength: 150 }),
});

// Generate date ranges
const dateRangeGenerator = fc.tuple(fc.date(), fc.date())
  .filter(([start, end]) => end > start)
  .map(([start, end]) => ({
    start_date: start.toISOString(),
    end_date: end.toISOString(),
  }));
```

### Testing Requirements

**All tests must:**
- Run in CI/CD pipeline
- Pass before merging to main branch
- Maintain minimum 80% code coverage
- Execute in under 5 minutes (unit + property tests)
- Be deterministic and reproducible

**Property-based tests must:**
- Run minimum 100 iterations
- Be tagged with property number from design doc
- Use smart generators that produce realistic data
- Test core logic without mocking when possible

## Implementation Notes

### Technology Stack

**Frontend:**
- React 19.2.0
- TypeScript 5.8.2
- Vite 6.2.0 (build tool)
- Framer Motion 12.23.24 (animations)
- Lucide React 0.555.0 (icons)
- Axios (HTTP client)
- fast-check (property-based testing)
- Vitest (unit testing)

**Styling:**
- Tailwind CSS (utility-first CSS)
- Custom CRT effects and Victorian theme

### File Structure

```
phantom_frontend/
├── src/
│   ├── config/
│   │   └── api.ts                 # Axios configuration
│   ├── services/
│   │   ├── authService.ts         # Authentication API calls
│   │   ├── eventService.ts        # Event CRUD operations
│   │   ├── chatService.ts         # Chat/NLP API calls
│   │   ├── categoryService.ts     # Category operations
│   │   ├── preferenceService.ts   # User preferences
│   │   └── integrationService.ts  # Google Calendar integration
│   ├── context/
│   │   └── AuthContext.tsx        # Authentication state management
│   ├── hooks/
│   │   ├── usePhantom.ts          # Main app state hook (refactor)
│   │   ├── useEvents.ts           # Event management hook
│   │   ├── useChat.ts             # Chat state hook
│   │   └── useAuth.ts             # Auth hook (from context)
│   ├── components/
│   │   ├── CRTScanlines.tsx       # Visual effect
│   │   ├── GhostOverlay.tsx       # Visual effect
│   │   ├── Monolith.tsx           # Event card
│   │   ├── DoomsdayCalendar.tsx   # Calendar component
│   │   ├── TerminalInput.tsx      # Chat input
│   │   └── ProtectedRoute.tsx     # Route guard
│   ├── pages/
│   │   ├── LoginPage.tsx          # Login/Register page
│   │   └── SeanceRoom.tsx         # Main app page
│   ├── types/
│   │   └── index.ts               # TypeScript interfaces
│   ├── utils/
│   │   ├── dateUtils.ts           # Date formatting/parsing
│   │   ├── validation.ts          # Input validation
│   │   └── storage.ts             # localStorage helpers
│   ├── App.tsx                    # Root component
│   └── main.tsx                   # Entry point
├── tests/
│   ├── unit/
│   │   ├── services/              # Service unit tests
│   │   ├── hooks/                 # Hook unit tests
│   │   └── utils/                 # Utility unit tests
│   ├── property/
│   │   ├── auth.property.test.ts  # Auth property tests
│   │   ├── events.property.test.ts # Event property tests
│   │   └── chat.property.test.ts  # Chat property tests
│   └── integration/
│       └── flows.test.ts          # E2E integration tests
├── .env.example                   # Environment variables template
├── .env.development               # Development environment
├── .env.production                # Production environment
├── vite.config.ts                 # Vite configuration
├── tsconfig.json                  # TypeScript configuration
└── package.json                   # Dependencies
```

### Environment Variables

```env
# API Configuration
VITE_API_URL=http://localhost:8000/api

# Feature Flags
VITE_ENABLE_GOOGLE_CALENDAR=true
VITE_ENABLE_CONVERSATION_HISTORY=true

# Development
VITE_ENABLE_DEBUG_LOGGING=true
```

### Migration Strategy

**Phase 1: Setup Infrastructure**
1. Install dependencies (axios, fast-check, vitest)
2. Create API client configuration
3. Set up environment variables
4. Create service layer structure

**Phase 2: Authentication**
1. Implement auth service
2. Create auth context
3. Update LoginPage to use real API
4. Implement token refresh logic
5. Add protected routes

**Phase 3: Event Management**
1. Implement event service
2. Create useEvents hook
3. Update SeanceRoom to fetch real events
4. Implement event CRUD operations
5. Add error handling

**Phase 4: Chat Integration**
1. Implement chat service
2. Create useChat hook
3. Update TerminalInput to send real messages
4. Handle Phantom responses
5. Sync chat-created events with timeline

**Phase 5: Additional Features**
1. Implement category service
2. Implement preference service
3. Add Google Calendar integration UI
4. Implement date filtering
5. Add conversation history

**Phase 6: Polish & Testing**
1. Add loading states
2. Implement error handling
3. Add success feedback
4. Write property-based tests
5. Write integration tests
6. Performance optimization

### Security Considerations

**Token Storage:**
- Store tokens in localStorage (acceptable for this use case)
- Consider httpOnly cookies for enhanced security in production
- Implement token rotation

**XSS Prevention:**
- React's built-in XSS protection via JSX
- Sanitize any HTML rendered from backend
- Use Content Security Policy headers

**CSRF Protection:**
- Not required for JWT-based auth
- Backend handles CSRF for session-based endpoints

**Input Validation:**
- Validate all user input client-side
- Never trust client-side validation alone
- Backend performs authoritative validation

### Performance Optimization

**Code Splitting:**
- Lazy load pages and heavy components
- Use React.lazy() and Suspense
- Split vendor bundles

**Caching:**
- Cache category data (rarely changes)
- Implement stale-while-revalidate for events
- Use React Query or SWR for data fetching

**Rendering:**
- Memoize expensive computations
- Use React.memo for pure components
- Implement virtual scrolling for long lists

**Network:**
- Debounce search and filter inputs
- Batch multiple API calls when possible
- Compress API responses (gzip)

### Accessibility Checklist

- [ ] All interactive elements are keyboard accessible
- [ ] Focus indicators are visible
- [ ] ARIA labels on all buttons and inputs
- [ ] Form errors are announced to screen readers
- [ ] Color contrast meets WCAG AA standards
- [ ] Text is resizable up to 200%
- [ ] No content flashes more than 3 times per second
- [ ] Skip navigation links provided
- [ ] Semantic HTML elements used
- [ ] Alt text for all images

## Deployment Considerations

### Build Configuration

**Development:**
```bash
npm run dev
# Runs on http://localhost:5173
# Hot module replacement enabled
# Source maps enabled
```

**Production:**
```bash
npm run build
# Outputs to dist/
# Minified and optimized
# Source maps disabled
```

### Environment-Specific Settings

**Development:**
- API URL: http://localhost:8000/api
- Debug logging enabled
- Detailed error messages

**Production:**
- API URL: https://api.phantom.example.com/api
- Debug logging disabled
- Generic error messages
- Performance monitoring enabled

### CORS Configuration

Backend must allow frontend origin:
```python
# Django settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Development
    "https://phantom.example.com",  # Production
]
```

### Deployment Checklist

- [ ] Environment variables configured
- [ ] API URL points to production backend
- [ ] CORS configured on backend
- [ ] HTTPS enabled
- [ ] Error monitoring configured (Sentry, etc.)
- [ ] Analytics configured (optional)
- [ ] Performance monitoring enabled
- [ ] Build optimizations verified
- [ ] Browser compatibility tested
- [ ] Mobile responsiveness verified
- [ ] Accessibility audit passed
- [ ] Security headers configured
- [ ] CDN configured for static assets
- [ ] Backup and rollback plan in place
