# Implementation Plan

## Phase 1: Project Setup and Infrastructure

- [x] 1. Set up project dependencies and configuration













  - Install axios for HTTP client
  - Install fast-check for property-based testing
  - Install vitest for unit testing
  - Create .env.example with required environment variables
  - Configure TypeScript for strict type checking
  - _Requirements: 17.1, 17.2_

- [x] 2. Create API client configuration




- [x] 2.1 Implement base Axios instance with configuration


  - Create src/config/api.ts
  - Configure base URL from environment variable (VITE_API_URL)
  - Set default headers (Content-Type: application/json)
  - Set timeout to 30 seconds
  - _Requirements: 2.1, 17.1, 17.2_

- [x] 2.2 Implement request interceptor for authentication


  - Retrieve access token from localStorage
  - Attach token to Authorization header as "Bearer {token}"
  - Allow requests without token for public endpoints
  - _Requirements: 2.2_

- [x] 2.3 Implement response interceptor for token refresh


  - Detect 401 Unauthorized responses
  - Attempt token refresh using refresh token
  - Retry original request with new access token on success
  - Redirect to login on refresh failure
  - Clear authentication data on refresh failure
  - _Requirements: 1.5, 2.3, 2.4, 2.5, 2.6_

- [ ]* 2.4 Write property test for request interceptor
  - **Property 5: Authorization header is attached to requests**
  - **Validates: Requirements 2.2**

- [x] 3. Create TypeScript interfaces and types









  - Create src/types/index.ts
  - Define Event, Category, User, ChatMessage interfaces
  - Define API request/response types
  - Define service method signatures
  - _Requirements: All_

## Phase 2: Authentication Implementation

- [x] 4. Implement authentication service




- [x] 4.1 Create authentication service module


  - Create src/services/authService.ts
  - Implement register() method - POST to /api/auth/register/
  - Implement login() method - POST to /api/auth/login/
  - Implement logout() method - POST to /api/auth/logout/
  - Implement refreshToken() method - POST to /api/auth/token/refresh/
  - Implement verifyToken() method for token validation
  - _Requirements: 1.1, 1.3, 1.6_


- [x] 4.2 Write property test for authentication API calls






  - **Property 1: Authentication API calls are made correctly**
  - **Validates: Requirements 1.1, 1.3**

- [ ]* 4.3 Write property test for token storage
  - **Property 2: Successful authentication stores tokens**
  - **Validates: Requirements 1.4**

- [ ]* 4.4 Write property test for logout cleanup
  - **Property 4: Logout clears authentication data**
  - **Validates: Requirements 1.6**

- [x] 5. Create authentication context





- [x] 5.1 Implement AuthContext provider


  - Create src/context/AuthContext.tsx
  - Manage user state (username, userId)
  - Manage authentication status (isAuthenticated, loading)
  - Implement login function with error handling
  - Implement register function with error handling
  - Implement logout function with token blacklisting
  - Store tokens in localStorage on successful login
  - Clear tokens from localStorage on logout
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.6, 1.7_

- [x] 5.2 Implement token verification on app initialization


  - Check for stored access token in localStorage on mount
  - Verify token with backend if present
  - Attempt token refresh if verification fails
  - Auto-login user if token is valid
  - Clear storage and show login if tokens are invalid
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ]* 5.3 Write property test for token refresh
  - **Property 3: Token refresh is automatic**
  - **Validates: Requirements 1.5, 2.3**

- [ ]* 5.4 Write property test for failed refresh
  - **Property 6: Failed token refresh triggers re-authentication**
  - **Validates: Requirements 2.5, 2.6**

- [ ]* 5.5 Write property test for auto-login
  - **Property 32: Valid tokens trigger auto-login**
  - **Validates: Requirements 12.2**

- [ ]* 5.6 Write property test for session restoration
  - **Property 35: Session restoration works after browser close**
  - **Validates: Requirements 12.5**

- [x] 6. Update LoginPage component





- [x] 6.1 Integrate real authentication with LoginPage


  - Import useAuth hook from AuthContext
  - Update handleSubmit to call real login/register functions
  - Handle loading states during authentication
  - Display backend error messages
  - Redirect to SeanceRoom on successful login
  - Add name field for registration mode
  - _Requirements: 1.1, 1.2, 1.3, 1.7_



- [x] 6.2 Add client-side validation to LoginPage






  - Validate username length (minimum 3 characters)
  - Validate password length (minimum 8 characters)
  - Display validation errors before submission
  - Prevent submission with invalid data
  - _Requirements: 11.1, 11.4_

- [ ]* 6.3 Write property test for validation errors
  - **Property 30: Empty required fields show validation errors**
  - **Validates: Requirements 11.4**

- [x] 7. Create ProtectedRoute component





  - Create src/components/ProtectedRoute.tsx
  - Check authentication status from AuthContext
  - Redirect to login if not authenticated
  - Show loading spinner while checking auth
  - Render children if authenticated
  - _Requirements: 1.1, 12.1_

- [x] 8. Update App.tsx with authentication flow





  - Wrap app with AuthProvider
  - Use ProtectedRoute for SeanceRoom
  - Remove mock authentication logic
  - Handle authentication state transitions
  - _Requirements: 1.1, 1.2, 1.6_

- [x] 9. Checkpoint - Ensure authentication tests pass





  - Ensure all tests pass, ask the user if questions arise.

## Phase 3: Event Management Implementation

- [x] 10. Implement event service




- [x] 10.1 Create event service module


  - Create src/services/eventService.ts
  - Implement getEvents() - GET /api/events/ with query params
  - Implement getEvent(id) - GET /api/events/{id}/
  - Implement createEvent(data) - POST /api/events/
  - Implement updateEvent(id, data) - PUT /api/events/{id}/
  - Implement deleteEvent(id) - DELETE /api/events/{id}/
  - Handle date serialization (Date to ISO 8601)
  - _Requirements: 3.1, 3.3, 3.4, 3.5_

- [ ]* 10.2 Write property test for event CRUD operations
  - **Property 8: Event CRUD operations call correct endpoints**
  - **Validates: Requirements 3.3, 3.4, 3.5**

- [x] 11. Create useEvents custom hook




- [x] 11.1 Implement useEvents hook


  - Create src/hooks/useEvents.ts
  - Manage events state array
  - Manage loading and error states
  - Implement fetchEvents function with query params
  - Implement createEvent function
  - Implement updateEvent function
  - Implement deleteEvent function
  - Implement refreshEvents function
  - Update local state after successful operations
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

- [ ]* 11.2 Write property test for event fetching and ordering
  - **Property 7: Events are fetched and ordered correctly**
  - **Validates: Requirements 3.1**

- [ ]* 11.3 Write property test for event deletion sync
  - **Property 22: Event deletion removes from all views**
  - **Validates: Requirements 9.2**

- [ ]* 11.4 Write property test for event update sync
  - **Property 23: Event updates reflect everywhere**
  - **Validates: Requirements 9.3**

- [x] 12. Implement category service




- [x] 12.1 Create category service module


  - Create src/services/categoryService.ts
  - Implement getCategories() - GET /api/categories/
  - Implement getCategory(id) - GET /api/categories/{id}/
  - Cache categories in memory (rarely change)
  - _Requirements: 6.1, 6.2_

- [ ]* 12.2 Write property test for category ordering
  - **Property 14: Categories are ordered by priority**
  - **Validates: Requirements 6.4**

- [x] 13. Update SeanceRoom to use real events




- [x] 13.1 Integrate useEvents hook in SeanceRoom


  - Import and use useEvents hook
  - Fetch events on component mount
  - Display loading state while fetching
  - Display error messages on fetch failure
  - Pass real events to Monolith components
  - Remove mock task data
  - _Requirements: 3.1, 3.6, 8.1_

- [x] 13.2 Implement event deletion in SeanceRoom


  - Call deleteEvent from useEvents hook
  - Update UI immediately after deletion
  - Show success confirmation
  - Handle deletion errors
  - _Requirements: 3.5, 3.7, 8.5, 9.2_

- [x] 13.3 Implement event editing in SeanceRoom


  - Call updateEvent from useEvents hook
  - Update UI immediately after edit
  - Show success confirmation
  - Handle update errors
  - _Requirements: 3.4, 3.7, 8.5, 9.3_

- [x] 13.4 Write property test for loading indicators






  - **Property 19: Loading indicators appear during requests**
  - **Validates: Requirements 8.1**

- [ ]* 13.5 Write property test for success confirmation
  - **Property 21: Success operations show confirmation**
  - **Validates: Requirements 8.5**

- [x] 14. Checkpoint - Ensure event management tests pass





  - Ensure all tests pass, ask the user if questions arise.

## Phase 4: Chat Integration

- [x] 15. Implement chat service




- [x] 15.1 Create chat service module


  - Create src/services/chatService.ts
  - Implement sendMessage(message) - POST /api/chat/
  - Implement getConversationHistory() - GET /api/chat/history/
  - Handle chat response with events_created field
  - _Requirements: 4.1, 4.2, 13.3_

- [x] 15.2 Write property test for chat message sending






  - **Property 9: Chat messages trigger API calls**
  - **Validates: Requirements 4.1, 4.2**

- [-] 16. Create useChat custom hook





- [x] 16.1 Implement useChat hook



  - Create src/hooks/useChat.ts
  - Manage chat history state
  - Manage loading and error states
  - Implement sendMessage function
  - Add user message to history immediately
  - Add Phantom response to history after API call
  - Add system messages for errors
  - Implement clearHistory function
  - _Requirements: 4.1, 4.2, 4.5, 13.1, 13.2_

- [ ]* 16.2 Write property test for chat response styling
  - **Property 37: Phantom responses have distinct styling**
  - **Validates: Requirements 13.2**

- [ ]* 16.3 Write property test for message timestamps
  - **Property 36: User messages appear with timestamps**
  - **Validates: Requirements 13.1**

- [x] 17. Integrate chat with event creation




- [x] 17.1 Update useChat to handle event creation


  - Extract events_created from chat response
  - Return created events from sendMessage
  - _Requirements: 4.3_

- [x] 17.2 Update SeanceRoom to sync chat-created events


  - Import and use useChat hook
  - Call useEvents.refreshEvents when chat creates events
  - Update timeline immediately after chat response
  - Display created events in timeline
  - _Requirements: 4.3, 9.1_

- [x] 17.3 Write property test for chat-event synchronization






  - **Property 10: Chat-created events update timeline**
  - **Validates: Requirements 4.3, 9.1**

- [x] 18. Update TerminalInput component




- [x] 18.1 Integrate real chat with TerminalInput

  - Accept onSummon prop that calls useChat.sendMessage
  - Display loading state during chat request
  - Disable input while loading
  - Clear input after successful send
  - Handle chat errors
  - _Requirements: 4.1, 4.4, 4.5_

- [ ]* 18.2 Write property test for chat loading state
  - **Property 4: Chat loading shows indicator and disables input**
  - **Validates: Requirements 4.4**

- [x] 19. Implement chat auto-scroll





  - Add ref to chat history container
  - Scroll to bottom when new messages are added
  - Use smooth scrolling behavior
  - _Requirements: 4.6, 13.5_

- [ ]* 19.1 Write property test for auto-scroll
  - **Property 39: New messages trigger auto-scroll**
  - **Validates: Requirements 13.5**

- [x] 20. Checkpoint - Ensure chat integration tests pass





  - Ensure all tests pass, ask the user if questions arise.

## Phase 5: Calendar and Date Filtering

- [x] 21. Implement date filtering in useEvents




- [x] 21.1 Add date filtering to useEvents hook


  - Add selectedDate state
  - Add setSelectedDate function
  - Filter events by selected date in getEvents query params
  - Use start_date and end_date query parameters
  - Calculate date range for selected date (start of day to end of day)
  - _Requirements: 5.1, 5.2_

- [ ]* 21.2 Write property test for date filtering API calls
  - **Property 11: Date filtering uses correct query parameters**
  - **Validates: Requirements 5.1**

- [ ]* 21.3 Write property test for date filtering display
  - **Property 12: Date filtering displays correct events**
  - **Validates: Requirements 5.2**

- [x] 22. Update DoomsdayCalendar component





- [x] 22.1 Integrate real events with calendar


  - Accept events prop from useEvents
  - Display event indicators on dates with events
  - Highlight current date
  - Handle date selection
  - Call onSelectDate callback with selected date
  - _Requirements: 5.1, 5.2, 5.3_

- [x] 22.2 Implement month navigation


  - Add previous/next month buttons
  - Update calendar display when month changes
  - Maintain selected date across month changes
  - _Requirements: 5.4_

- [ ]* 22.3 Write property test for calendar navigation
  - **Property 13: Calendar navigation updates display**
  - **Validates: Requirements 5.4**

- [x] 23. Update SeanceRoom date filtering




  - Connect selectedDate from useEvents to DoomsdayCalendar
  - Filter displayed events by selectedDate
  - Show "no events" message when date has no events
  - Add "Return to Present" button for non-today dates
  - _Requirements: 5.2, 5.5_

- [ ] 24. Implement mobile calendar behavior
  - Auto-switch to Timeline view after date selection on mobile
  - Maintain calendar state during tab switches
  - _Requirements: 10.3_

- [ ]* 24.1 Write property test for mobile date selection
  - **Property 26: Mobile calendar selection switches to timeline**
  - **Validates: Requirements 10.3**

## Phase 6: Additional Features

- [ ] 25. Implement user preferences
- [ ] 25.1 Create preference service module
  - Create src/services/preferenceService.ts
  - Implement getPreferences() - GET /api/preferences/
  - Implement updatePreferences(data) - PUT /api/preferences/
  - _Requirements: 7.1, 7.2_

- [ ] 25.2 Create preferences page/modal
  - Create preferences UI component
  - Fetch preferences on mount
  - Display timezone and default_event_duration settings
  - Implement preference update form
  - Apply preferences immediately after update
  - _Requirements: 7.1, 7.2, 7.3_

- [ ]* 25.3 Write property test for preference updates
  - **Property 16: Preference updates call API**
  - **Validates: Requirements 7.2**

- [ ]* 25.4 Write property test for immediate application
  - **Property 17: Preferences apply immediately**
  - **Validates: Requirements 7.3**

- [ ] 26. Implement Google Calendar integration UI
- [ ] 26.1 Create integration service module
  - Create src/services/integrationService.ts
  - Implement connectGoogleCalendar() - GET /api/integrations/google/connect/
  - Implement getGoogleCalendarStatus() - GET /api/integrations/google/status/
  - Implement disconnectGoogleCalendar() - POST /api/integrations/google/disconnect/
  - _Requirements: 14.1, 14.4, 14.5_

- [ ] 26.2 Create Google Calendar integration UI
  - Add "Connect Google Calendar" button
  - Display connection status indicator
  - Handle OAuth2 redirect flow
  - Add "Disconnect" button when connected
  - Show connected email address
  - _Requirements: 14.1, 14.2, 14.3, 14.4_

- [ ]* 26.3 Write property test for OAuth callback handling
  - **Property 40: OAuth callback updates connection status**
  - **Validates: Requirements 14.2**

- [ ] 27. Implement critical event warning banner
  - Check for events with priority level 5 (CRITICAL)
  - Display "IMPENDING DOOM" banner when critical events exist
  - Show event title and due date in banner
  - Make banner dismissible
  - _Requirements: 6.5_

- [ ]* 27.1 Write property test for critical event banner
  - **Property 15: Critical events trigger warning banner**
  - **Validates: Requirements 6.5**

## Phase 7: Error Handling and User Feedback

- [ ] 28. Implement comprehensive error handling
- [ ] 28.1 Create error handling utilities
  - Create src/utils/errorHandling.ts
  - Implement error message extraction from API responses
  - Implement error categorization (network, auth, validation, server)
  - Create user-friendly error messages
  - _Requirements: 8.2, 8.3, 8.4, 8.6_

- [ ] 28.2 Add error display components
  - Create error toast/notification component
  - Display errors with appropriate styling
  - Add retry buttons for recoverable errors
  - Auto-dismiss success messages after 3 seconds
  - _Requirements: 8.2, 8.3, 8.4, 8.5, 8.6_

- [ ]* 28.3 Write property test for validation error display
  - **Property 20: Validation errors are displayed**
  - **Validates: Requirements 8.3**

- [ ] 29. Implement loading states
  - Add loading spinners to all async operations
  - Disable buttons during loading
  - Show skeleton screens for data loading
  - Maintain Victorian Ghost Butler theme in loading states
  - _Requirements: 8.1_

- [ ] 30. Add input validation
- [ ] 30.1 Create validation utilities
  - Create src/utils/validation.ts
  - Implement username validation (min 3 chars)
  - Implement password validation (min 8 chars)
  - Implement date validation (end > start)
  - Implement required field validation
  - _Requirements: 11.1, 11.2, 11.3, 11.4_

- [ ] 30.2 Apply validation to forms
  - Add validation to LoginPage
  - Add validation to event creation/edit forms
  - Display validation errors inline
  - Prevent submission with invalid data
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [ ]* 30.3 Write property test for date validation
  - **Property 28: Invalid event times show validation errors**
  - **Validates: Requirements 11.2**

- [ ]* 30.4 Write property test for date format validation
  - **Property 29: Invalid date formats show validation errors**
  - **Validates: Requirements 11.3**

- [ ]* 30.5 Write property test for valid data submission
  - **Property 31: Valid data is submitted to backend**
  - **Validates: Requirements 11.5**

## Phase 8: State Management and Synchronization

- [ ] 31. Implement state persistence
  - Maintain state during tab navigation
  - Avoid unnecessary API calls on tab switches
  - Cache category data
  - Implement stale-while-revalidate for events
  - _Requirements: 9.4_

- [ ]* 31.1 Write property test for tab navigation state
  - **Property 24: Tab navigation maintains state**
  - **Validates: Requirements 9.4**

- [ ] 32. Implement background sync
  - Detect when app regains focus
  - Refresh event data when app becomes active
  - Show sync indicator during refresh
  - _Requirements: 9.5_

- [ ] 33. Implement request debouncing
  - Add debouncing to search inputs
  - Add debouncing to filter operations
  - Prevent rapid API calls
  - _Requirements: 15.2_

- [ ]* 33.1 Write property test for debouncing
  - **Property 41: Debouncing prevents rapid API calls**
  - **Validates: Requirements 15.2**

- [ ] 34. Implement caching
  - Cache category data (rarely changes)
  - Implement cache invalidation strategy
  - Cache recent event queries
  - _Requirements: 15.5_

- [ ]* 34.1 Write property test for caching
  - **Property 42: Caching reduces duplicate requests**
  - **Validates: Requirements 15.5**

## Phase 9: Mobile Responsiveness

- [ ] 35. Verify mobile navigation
  - Test mobile navigation dock on small screens
  - Verify tab switching works correctly
  - Test touch interactions
  - _Requirements: 10.1, 10.2, 10.5_

- [ ]* 35.1 Write property test for mobile tab switching
  - **Property 25: Mobile tab switching shows correct view**
  - **Validates: Requirements 10.2**

- [ ]* 35.2 Write property test for touch gestures
  - **Property 27: Touch gestures trigger actions**
  - **Validates: Requirements 10.5**

- [ ] 36. Test mobile layouts
  - Test on various screen sizes
  - Verify responsive breakpoints
  - Test landscape and portrait orientations
  - Verify keyboard behavior on mobile
  - _Requirements: 10.1, 10.2, 10.3, 10.4_

## Phase 10: Accessibility

- [ ] 37. Implement keyboard navigation
  - Ensure all interactive elements are keyboard accessible
  - Add visible focus indicators
  - Implement logical tab order
  - Add skip navigation links
  - _Requirements: 16.1, 16.2_

- [ ]* 37.1 Write property test for focus indicators
  - **Property 43: Keyboard navigation shows focus indicators**
  - **Validates: Requirements 16.1**

- [ ]* 37.2 Write property test for tab order
  - **Property 44: Tab order is logical**
  - **Validates: Requirements 16.2**

- [ ] 38. Add ARIA labels and semantic HTML
  - Add ARIA labels to all interactive elements
  - Use semantic HTML elements
  - Add ARIA live regions for dynamic content
  - Add alt text for images
  - _Requirements: 16.3, 16.4, 16.5_

- [ ]* 38.1 Write property test for ARIA labels
  - **Property 45: Interactive elements have ARIA labels**
  - **Validates: Requirements 16.3**

- [ ]* 38.2 Write property test for error announcements
  - **Property 46: Errors are announced to screen readers**
  - **Validates: Requirements 16.4**

- [ ]* 38.3 Write property test for form feedback accessibility
  - **Property 47: Form feedback is accessible**
  - **Validates: Requirements 16.5**

- [ ] 39. Run accessibility audit
  - Use axe DevTools or Lighthouse
  - Fix any accessibility violations
  - Verify WCAG AA compliance
  - Test with screen reader
  - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5_

## Phase 11: Testing and Quality Assurance

- [ ] 40. Write remaining property-based tests
  - Ensure all 47 properties have corresponding tests
  - Run tests with 100+ iterations
  - Fix any failing tests
  - Achieve 80%+ code coverage

- [ ] 41. Write integration tests
  - Test complete authentication flow
  - Test event creation via chat
  - Test event CRUD operations
  - Test calendar navigation and filtering
  - Test mobile responsive behavior

- [ ] 42. Perform manual testing
  - Test all user flows manually
  - Test on different browsers (Chrome, Firefox, Safari, Edge)
  - Test on mobile devices (iOS, Android)
  - Test error scenarios
  - Test edge cases

- [ ] 43. Performance testing
  - Measure initial load time
  - Test with large numbers of events
  - Verify debouncing and caching work
  - Optimize bundle size
  - _Requirements: 15.1, 15.2, 15.5_

- [ ] 44. Final checkpoint - All tests passing
  - Ensure all tests pass, ask the user if questions arise.

## Phase 12: Documentation and Deployment

- [ ] 45. Update documentation
  - Update README with setup instructions
  - Document environment variables
  - Add API integration examples
  - Document component usage
  - Add troubleshooting guide

- [ ] 46. Prepare for deployment
  - Create production build
  - Test production build locally
  - Configure environment variables for production
  - Verify CORS configuration with backend
  - Set up error monitoring (optional)

- [ ] 47. Final review and polish
  - Review all code for consistency
  - Remove console.logs and debug code
  - Verify all features work end-to-end
  - Get user acceptance
