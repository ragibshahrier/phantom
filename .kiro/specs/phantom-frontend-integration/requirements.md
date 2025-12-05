# Requirements Document

## Introduction

The Phantom Scheduler frontend is a React-based application with a unique Victorian Ghost Butler theme featuring terminal-style UI, CRT effects, and a dark aesthetic. The backend is a fully functional Django REST API with comprehensive features including authentication, event management, natural language chat, categories, user preferences, and Google Calendar integration. This specification defines the requirements for integrating the existing frontend with the backend APIs to create a fully functional, bug-free scheduling application.

## Glossary

- **Frontend**: The React-based user interface application built with TypeScript, Vite, and Framer Motion
- **Backend**: The Django REST Framework API providing scheduling, authentication, and AI chat services
- **Phantom**: The AI-powered Victorian Ghost Butler assistant that processes natural language scheduling requests
- **Event**: A calendar entry with title, description, start time, end time, and category
- **Category**: A classification for events with associated priority levels (Exam=5, Study=4, Gym=3, Social=2, Gaming=1)
- **JWT Token**: JSON Web Token used for authentication (access token expires in 15 minutes, refresh token in 7 days)
- **API Client**: Axios-based HTTP client configured for backend communication
- **Protected Route**: A route that requires user authentication to access
- **Natural Language Processing**: AI-powered interpretation of user messages to create/modify events

## Requirements

### Requirement 1: Authentication System

**User Story:** As a user, I want to register, login, and logout securely, so that my calendar data is protected and accessible only to me.

#### Acceptance Criteria

1. WHEN a user submits the registration form with username, name, and password THEN the Frontend SHALL send a POST request to `/api/auth/register/` with the credentials
2. WHEN registration is successful THEN the Frontend SHALL display a success message and redirect the user to the login form
3. WHEN a user submits the login form with username and password THEN the Frontend SHALL send a POST request to `/api/auth/login/` and receive JWT access and refresh tokens
4. WHEN login is successful THEN the Frontend SHALL store the access token, refresh token, and username in localStorage
5. WHEN an access token expires (after 15 minutes) THEN the Frontend SHALL automatically use the refresh token to obtain a new access token without user intervention
6. WHEN a user clicks logout THEN the Frontend SHALL send the refresh token to `/api/auth/logout/` to blacklist it and clear all stored authentication data
7. WHEN authentication fails THEN the Frontend SHALL display appropriate error messages to the user

### Requirement 2: API Client Configuration

**User Story:** As a developer, I want a centralized API client with automatic token management, so that all API requests are authenticated and token refresh is handled seamlessly.

#### Acceptance Criteria

1. WHEN the API client is initialized THEN the Frontend SHALL configure the base URL to point to the backend API endpoint
2. WHEN an API request is made THEN the Frontend SHALL automatically attach the access token in the Authorization header as "Bearer {token}"
3. WHEN an API response returns 401 Unauthorized THEN the Frontend SHALL attempt to refresh the access token using the refresh token
4. WHEN token refresh succeeds THEN the Frontend SHALL retry the original failed request with the new access token
5. WHEN token refresh fails THEN the Frontend SHALL clear authentication data and redirect the user to the login page
6. WHEN the refresh token is blacklisted THEN the Frontend SHALL treat it as an invalid token and require re-authentication

### Requirement 3: Event Management

**User Story:** As a user, I want to create, view, update, and delete calendar events, so that I can manage my schedule effectively.

#### Acceptance Criteria

1. WHEN a user views the timeline THEN the Frontend SHALL fetch events from `/api/events/` and display them ordered by start time
2. WHEN a user creates an event via the chat interface THEN the Frontend SHALL send the message to `/api/chat/` and display the created events
3. WHEN a user creates an event directly THEN the Frontend SHALL send a POST request to `/api/events/` with title, description, category, start_time, and end_time
4. WHEN a user updates an event THEN the Frontend SHALL send a PUT request to `/api/events/{id}/` with the modified data
5. WHEN a user deletes an event THEN the Frontend SHALL send a DELETE request to `/api/events/{id}/` and remove it from the display
6. WHEN events are fetched THEN the Frontend SHALL include category information with each event for display purposes
7. WHEN an event operation fails THEN the Frontend SHALL display an error message to the user

### Requirement 4: Natural Language Chat Interface

**User Story:** As a user, I want to interact with Phantom using natural language, so that I can create and manage events conversationally without filling forms.

#### Acceptance Criteria

1. WHEN a user types a message in the chat input THEN the Frontend SHALL send it to `/api/chat/` with the message text
2. WHEN Phantom responds THEN the Frontend SHALL display the response in the chat history with appropriate styling
3. WHEN Phantom creates events from a message THEN the Frontend SHALL update the timeline to show the newly created events
4. WHEN the chat is loading THEN the Frontend SHALL display a loading indicator and disable the input field
5. WHEN a chat request fails THEN the Frontend SHALL display an error message and allow the user to retry
6. WHEN the chat history grows THEN the Frontend SHALL automatically scroll to show the latest messages

### Requirement 5: Calendar and Date Filtering

**User Story:** As a user, I want to view events by date and navigate through my calendar, so that I can see my schedule for specific days.

#### Acceptance Criteria

1. WHEN a user selects a date in the calendar THEN the Frontend SHALL fetch events for that date using the `start_date` and `end_date` query parameters
2. WHEN events are filtered by date THEN the Frontend SHALL display only events that intersect with the selected date
3. WHEN a user views today's events THEN the Frontend SHALL highlight the current date in the calendar
4. WHEN a user navigates to a different month THEN the Frontend SHALL update the calendar display to show that month
5. WHEN no events exist for a selected date THEN the Frontend SHALL display a message indicating no events are scheduled

### Requirement 6: Category Management

**User Story:** As a user, I want to view and use event categories with their priority levels, so that I can organize my events by importance.

#### Acceptance Criteria

1. WHEN the application loads THEN the Frontend SHALL fetch categories from `/api/categories/` and cache them for event creation
2. WHEN a user creates an event THEN the Frontend SHALL allow selection from available categories
3. WHEN events are displayed THEN the Frontend SHALL show the category name and color for each event
4. WHEN categories are fetched THEN the Frontend SHALL order them by priority level (highest first)
5. WHEN a critical priority event exists THEN the Frontend SHALL display an "IMPENDING DOOM" warning banner

### Requirement 7: User Preferences

**User Story:** As a user, I want to configure my preferences like timezone and default event duration, so that the application works according to my needs.

#### Acceptance Criteria

1. WHEN a user accesses preferences THEN the Frontend SHALL fetch current preferences from `/api/preferences/`
2. WHEN a user updates preferences THEN the Frontend SHALL send a PUT request to `/api/preferences/` with the modified settings
3. WHEN preferences are updated THEN the Frontend SHALL apply the new settings immediately without requiring a page refresh
4. WHEN timezone is changed THEN the Frontend SHALL display all event times in the new timezone

### Requirement 8: Error Handling and User Feedback

**User Story:** As a user, I want clear error messages and loading states, so that I understand what's happening and can recover from errors.

#### Acceptance Criteria

1. WHEN any API request is in progress THEN the Frontend SHALL display a loading indicator
2. WHEN an API request fails with a network error THEN the Frontend SHALL display "Connection failed. Please check your internet connection."
3. WHEN an API request fails with a 400 error THEN the Frontend SHALL display the validation errors from the backend
4. WHEN an API request fails with a 500 error THEN the Frontend SHALL display "Server error. Please try again later."
5. WHEN an operation succeeds THEN the Frontend SHALL display a success message or visual confirmation
6. WHEN the backend is unavailable THEN the Frontend SHALL display a message indicating the service is temporarily unavailable

### Requirement 9: State Management and Data Synchronization

**User Story:** As a user, I want the interface to stay synchronized with the backend, so that I always see the most current data.

#### Acceptance Criteria

1. WHEN an event is created via chat THEN the Frontend SHALL immediately update the timeline without requiring a manual refresh
2. WHEN an event is deleted THEN the Frontend SHALL remove it from all views immediately
3. WHEN an event is updated THEN the Frontend SHALL reflect the changes in all views where the event appears
4. WHEN the user navigates between tabs THEN the Frontend SHALL maintain the current state without unnecessary API calls
5. WHEN the application regains focus after being in the background THEN the Frontend SHALL refresh event data to ensure synchronization

### Requirement 10: Responsive Design and Mobile Support

**User Story:** As a user, I want the application to work seamlessly on mobile devices, so that I can manage my schedule on any device.

#### Acceptance Criteria

1. WHEN the application is viewed on mobile THEN the Frontend SHALL display the mobile navigation dock at the bottom
2. WHEN a user switches tabs on mobile THEN the Frontend SHALL show the appropriate view (Uplink, Timeline, or Prophecy)
3. WHEN a user selects a date on mobile calendar THEN the Frontend SHALL automatically switch to the Timeline view to show events
4. WHEN the keyboard is open on mobile THEN the Frontend SHALL adjust the layout to keep input fields visible
5. WHEN touch gestures are used THEN the Frontend SHALL respond appropriately to swipes and taps

### Requirement 11: Data Validation and Input Sanitization

**User Story:** As a user, I want the application to validate my input before sending it to the server, so that I receive immediate feedback on invalid data.

#### Acceptance Criteria

1. WHEN a user enters a username shorter than 3 characters THEN the Frontend SHALL display a validation error before submitting
2. WHEN a user creates an event with end time before start time THEN the Frontend SHALL display a validation error
3. WHEN a user enters invalid date formats THEN the Frontend SHALL display a validation error
4. WHEN a user submits empty required fields THEN the Frontend SHALL highlight the fields and display error messages
5. WHEN validation passes THEN the Frontend SHALL submit the data to the backend

### Requirement 12: Session Persistence and Auto-Login

**User Story:** As a user, I want to remain logged in when I close and reopen the application, so that I don't have to login every time.

#### Acceptance Criteria

1. WHEN the application loads THEN the Frontend SHALL check for stored access tokens in localStorage
2. WHEN a valid access token exists THEN the Frontend SHALL verify it with the backend and automatically log the user in
3. WHEN the stored token is invalid or expired THEN the Frontend SHALL attempt to refresh it using the refresh token
4. WHEN both tokens are invalid THEN the Frontend SHALL clear storage and show the login page
5. WHEN a user closes the browser and returns THEN the Frontend SHALL restore the authenticated session if tokens are still valid

### Requirement 13: Conversation History

**User Story:** As a user, I want to see my previous conversations with Phantom, so that I can review what I've asked and the responses I received.

#### Acceptance Criteria

1. WHEN a user sends a message THEN the Frontend SHALL display it in the chat history with a timestamp
2. WHEN Phantom responds THEN the Frontend SHALL display the response with distinct styling from user messages
3. WHEN the application loads THEN the Frontend SHALL optionally fetch conversation history from `/api/chat/history/`
4. WHEN the chat history is long THEN the Frontend SHALL implement scrolling with the most recent messages visible
5. WHEN a new message is added THEN the Frontend SHALL automatically scroll to show it

### Requirement 14: Google Calendar Integration UI

**User Story:** As a user, I want to connect my Google Calendar, so that my Phantom events sync with my existing calendar.

#### Acceptance Criteria

1. WHEN a user clicks "Connect Google Calendar" THEN the Frontend SHALL redirect to the OAuth2 authorization URL from `/api/integrations/google/connect/`
2. WHEN OAuth2 callback is received THEN the Frontend SHALL handle the callback and display connection status
3. WHEN Google Calendar is connected THEN the Frontend SHALL display a connected status indicator
4. WHEN a user clicks "Disconnect Google Calendar" THEN the Frontend SHALL send a POST request to `/api/integrations/google/disconnect/`
5. WHEN checking connection status THEN the Frontend SHALL fetch status from `/api/integrations/google/status/`

### Requirement 15: Performance Optimization

**User Story:** As a user, I want the application to load quickly and respond smoothly, so that I have a pleasant user experience.

#### Acceptance Criteria

1. WHEN the application loads THEN the Frontend SHALL display the initial UI within 2 seconds
2. WHEN API requests are made THEN the Frontend SHALL implement request debouncing for search and filter operations
3. WHEN large lists of events are displayed THEN the Frontend SHALL implement virtual scrolling or pagination
4. WHEN images or assets are loaded THEN the Frontend SHALL use lazy loading to improve initial load time
5. WHEN the same data is requested multiple times THEN the Frontend SHALL implement caching to reduce unnecessary API calls

### Requirement 16: Accessibility

**User Story:** As a user with accessibility needs, I want the application to be usable with keyboard navigation and screen readers, so that I can access all features.

#### Acceptance Criteria

1. WHEN a user navigates with keyboard THEN the Frontend SHALL provide visible focus indicators on all interactive elements
2. WHEN a user uses Tab key THEN the Frontend SHALL follow a logical tab order through the interface
3. WHEN a screen reader is used THEN the Frontend SHALL provide appropriate ARIA labels for all interactive elements
4. WHEN errors occur THEN the Frontend SHALL announce them to screen readers
5. WHEN forms are submitted THEN the Frontend SHALL provide clear feedback that is accessible to screen readers

### Requirement 17: Environment Configuration

**User Story:** As a developer, I want to configure the API endpoint and other settings via environment variables, so that the application works in different environments (development, staging, production).

#### Acceptance Criteria

1. WHEN the application is built THEN the Frontend SHALL read the API base URL from the `VITE_API_URL` environment variable
2. WHEN no environment variable is set THEN the Frontend SHALL default to `http://localhost:8000/api`
3. WHEN deployed to production THEN the Frontend SHALL use the production API URL from environment configuration
4. WHEN CORS is configured THEN the Frontend SHALL successfully make requests to the backend from the configured origin
5. WHEN environment changes THEN the Frontend SHALL not require code changes, only environment variable updates
