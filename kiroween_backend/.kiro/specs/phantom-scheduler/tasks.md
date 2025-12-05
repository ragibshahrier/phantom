# Implementation Plan

- [x] 1. Set up Django project structure and dependencies





  - Install Django, Django REST Framework, djangorestframework-simplejwt, LangChain, and other required packages
  - Configure Django settings for JWT authentication, database, and REST framework
  - Create necessary Django apps: scheduler, ai_agent, integrations
  - Set up environment variables for API keys and secrets
  - _Requirements: All_

- [x] 2. Implement authentication system with JWT





  - _Requirements: 13.1, 13.2, 13.5, 14.1, 14.2, 15.1, 15.2, 16.1, 16.5, 17.1, 17.3_



- [x] 2.1 Create User model and BlacklistedToken model





  - Extend Django's AbstractUser with name, timezone, default_event_duration fields
  - Create BlacklistedToken model for logout functionality
  - Run migrations to create database tables


  - _Requirements: 13.1, 13.5_

- [x] 2.2 Create registration API endpoint




  - Implement UserRegistrationSerializer with username, name, and password validation


  - Create registration view that checks username uniqueness and hashes passwords
  - Return appropriate error messages for duplicate usernames


  - _Requirements: 13.1, 13.2, 13.4, 13.5_


- [x] 2.3 Write property test for username uniqueness





  - **Property 29: Username uniqueness enforcement**
  - **Validates: Requirements 13.2**

- [x] 2.4 Write property test for password hashing





  - **Property 30: Password security**


  - **Validates: Requirements 13.5**



- [ ] 2.5 Create login API endpoint with JWT token generation





  - Implement login view that authenticates username and password

  - Generate and return both access token (15 min expiry) and refresh token (7 days expiry)
  - Include user ID and username in JWT payload
  - Return 401 for invalid credentials
  - _Requirements: 14.1, 14.2, 14.3, 14.4_



- [ ] 2.6 Write property test for JWT token generation
  - **Property 31: JWT token generation on login**


  - **Validates: Requirements 14.1**


- [ ] 2.7 Write property test for invalid credentials rejection
  - **Property 32: Invalid credentials rejection**
  - **Validates: Requirements 14.2**

- [x] 2.8 Implement JWT authentication for protected endpoints


  - Configure JWT authentication in Django REST Framework settings
  - Create custom permission classes for protected endpoints

  - Implement token validation and expiration checking
  - _Requirements: 15.1, 15.2, 15.3, 15.4_

- [ ] 2.9 Write property test for protected endpoint authentication
  - **Property 33: Protected endpoint authentication**


  - **Validates: Requirements 15.1**

- [ ] 2.10 Write property test for expired token rejection
  - **Property 34: Expired token rejection**
  - **Validates: Requirements 15.2**

- [ ] 2.11 Create token refresh endpoint
  - Implement refresh token validation and new access token generation
  - Maintain user identity from original token
  - Handle expired or invalid refresh tokens
  - _Requirements: 16.1, 16.2, 16.3_

- [ ] 2.12 Write property test for token refresh functionality
  - **Property 35: Token refresh functionality**
  - **Validates: Requirements 16.1**

- [x] 2.13 Create logout endpoint with token blacklisting





  - Implement logout view that adds refresh token to blacklist
  - Store blacklisted tokens with expiration times
  - Reject blacklisted tokens in refresh endpoint
  - _Requirements: 17.1, 17.2, 17.3, 17.4_

- [x] 2.14 Write property test for blacklisted token rejection





  - **Property 36: Blacklisted token rejection**
  - **Validates: Requirements 16.5, 17.3**

- [x] 3. Implement core database models for scheduling





  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [x] 3.1 Create Category model with priority levels


  - Define Category model with name, priority_level, color, description fields
  - Create database migration
  - Create management command to populate default categories (Exam=5, Study=4, Gym=3, Social=2, Gaming=1)
  - _Requirements: 11.4, 2.3_



- [x] 3.2 Create Event model with scheduling metadata




  - Define Event model with user, title, description, category, start_time, end_time, is_flexible, is_completed fields
  - Add database indexes for user+start_time and user+category


  - Implement model validation (end_time must be after start_time)
  - _Requirements: 11.2, 5.1_



- [x] 3.3 Write property test for event creation persistence





  - **Property 1: Event creation persistence**
  - **Validates: Requirements 1.2, 11.2**



- [x] 3.4 Create ConversationHistory and SchedulingLog models




  - Implement ConversationHistory model for AI context
  - Implement SchedulingLog model for audit trail
  - Run migrations
  - _Requirements: 10.1, 10.2_

- [x] 3.5 Write property test for operation logging completeness





  - **Property 21: Operation logging completeness**
  - **Validates: Requirements 10.1**

- [x] 4. Create Django REST Framework serializers and API endpoints





  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 4.1 Implement Event serializers


  - Create EventSerializer with all fields and validation
  - Create EventListSerializer for optimized list views
  - Add custom validation for date/time constraints
  - _Requirements: 8.1, 8.5_

- [x] 4.2 Create Event CRUD API endpoints


  - Implement EventViewSet with create, list, retrieve, update, destroy actions
  - Add JWT authentication requirement
  - Filter events by authenticated user
  - Implement query parameter filtering (date range, category, priority)
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 11.3_

- [x] 4.3 Write property test for API response correctness


  - **Property 14: API response correctness for valid requests**
  - **Validates: Requirements 8.1**

- [x] 4.4 Write property test for API update response consistency


  - **Property 15: API update response consistency**
  - **Validates: Requirements 8.3**

- [x] 4.5 Write property test for API deletion behavior


  - **Property 16: API deletion behavior**
  - **Validates: Requirements 8.4**

- [x] 4.6 Write property test for API error handling


  - **Property 17: API error handling**
  - **Validates: Requirements 8.5**

- [x] 4.7 Write property test for query filtering correctness


  - **Property 24: Query filtering correctness**
  - **Validates: Requirements 11.3**

- [x] 4.8 Create Category API endpoints

  - Implement CategoryViewSet for listing and creating categories
  - Add JWT authentication
  - _Requirements: 2.3, 11.4_

- [x] 4.9 Write property test for category relationship integrity


  - **Property 25: Category relationship integrity**
  - **Validates: Requirements 11.4**

- [x] 4.10 Create UserPreferences API endpoints

  - Implement user preferences retrieval and update endpoints
  - Store timezone, default_event_duration, notification preferences
  - _Requirements: 11.5_

- [x] 4.11 Write property test for user preference persistence


  - **Property 26: User preference persistence**
  - **Validates: Requirements 11.5**
-

- [x] 5. Checkpoint - Ensure all tests pass




  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement scheduling engine with conflict resolution





  - _Requirements: 2.1, 2.2, 2.4, 2.5, 4.2, 4.3, 4.5_

- [x] 6.1 Create SchedulingEngine service class


  - Implement conflict detection algorithm to find overlapping events
  - Create method to find free time slots in a date range
  - Add helper methods for time range calculations
  - _Requirements: 4.2_

- [x] 6.2 Write property test for conflict detection completeness


  - **Property 7: Conflict detection completeness**
  - **Validates: Requirements 4.2**



- [x] 6.3 Implement priority-based conflict resolution
  - Create resolve_conflicts method that uses category priority levels
  - Ensure higher priority events are preserved
  - Move lower priority events to next available free slots
  - _Requirements: 2.1, 2.4_

- [x] 6.4 Write property test for priority-based conflict resolution
  - **Property 4: Priority-based conflict resolution**
  - **Validates: Requirements 2.1**



- [x] 6.5 Implement event preservation during rescheduling


  - Ensure rescheduled events maintain original duration and category
  - Verify total event count remains constant unless explicitly deleted


  - _Requirements: 2.5, 3.4_

- [x] 6.6 Write property test for event preservation
  - **Property 5: Event preservation during rescheduling**
  - **Validates: Requirements 2.5**

- [x] 6.7 Write property test for duration and category invariance
  - **Property 6: Duration and category invariance**
  - **Validates: Requirements 3.4**

- [x] 6.8 Implement auto-optimization with transaction support
  - Create optimize_schedule method that processes all events in a date range
  - Use Django atomic transactions for all-or-nothing updates
  - Log all optimization operations
  - _Requirements: 4.3, 4.5_

- [x] 6.9 Write property test for atomic schedule updates
  - **Property 8: Atomic schedule updates**
  - **Validates: Requirements 4.5, 5.3**

- [x] 6.10 Implement exam-triggered study session creation
  - Detect when an exam event is created
  - Automatically generate 2-3 study sessions in preceding days
  - Apply priority rules to clear conflicts
  - _Requirements: 1.3, 2.2_

- [x] 6.11 Write property test for exam triggers study sessions
  - **Property 2: Exam triggers study sessions**
  - **Validates: Requirements 1.3**

- [x] 7. Implement natural language parsing with date/time extraction





  - _Requirements: 9.1, 9.2, 9.4, 9.5_


- [x] 7.1 Create temporal expression parser

  - Implement parser for relative dates (tomorrow, next Friday, etc.)
  - Handle multi-day ranges (Wednesday and Thursday evening)
  - Parse various date formats and colloquial expressions
  - Apply user's timezone as default
  - _Requirements: 9.1, 9.2, 9.4, 9.5_



- [x] 7.2 Write property test for relative date parsing correctness





  - **Property 18: Relative date parsing correctness**


  - **Validates: Requirements 9.1**



- [x] 7.3 Write property test for multi-day range parsing





  - **Property 19: Multi-day range parsing**


  - **Validates: Requirements 9.2**

- [x] 7.4 Write property test for timezone default behavior





  - **Property 20: Timezone default behavior**
  - **Validates: Requirements 9.5**

- [x] 7.5 Create task and category extraction logic





  - Implement keyword-based category detection (exam, study, gym, social, gaming)
  - Extract task titles from natural language
  - Handle ambiguous inputs by requesting clarification
  - _Requirements: 1.1, 1.5_

- [x] 8. Integrate LangChain with Gemini API




  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [x] 8.1 Set up LangChain agent with Gemini API


  - Configure Gemini API credentials from environment variables
  - Initialize LangChain agent with appropriate model settings
  - Implement error handling for API failures and rate limits
  - _Requirements: 12.1, 12.5_

- [x] 8.2 Create Victorian Ghost Butler prompt templates


  - Write system prompt defining the Victorian Ghost Butler persona
  - Include scheduling rules and priority hierarchy in prompt
  - Create templates for different interaction types (confirmation, error, clarification)
  - _Requirements: 12.2, 7.1, 7.3_

- [x] 8.3 Implement structured output parsing


  - Create output parser to extract scheduling actions from Gemini responses
  - Parse action type (create, update, delete, reschedule), entities, and temporal info
  - Extract response text for user feedback
  - _Requirements: 12.3_

- [x] 8.4 Write property test for agent output parsing correctness


  - **Property 27: Agent output parsing correctness**
  - **Validates: Requirements 12.3**

- [x] 8.4 Create LangChain tools for calendar operations


  - Implement tools that call Django REST Framework endpoints
  - Map scheduling actions to appropriate API calls (create event, update event, etc.)
  - Pass authenticated user context to API calls
  - _Requirements: 12.4_

- [x] 8.5 Write property test for action-to-endpoint mapping


  - **Property 28: Action-to-endpoint mapping**
  - **Validates: Requirements 12.4**



- [x] 8.6 Implement chat API endpoint





  - Create /api/chat/ endpoint that receives natural language input
  - Pass input to LangChain agent for processing
  - Return agent response with Victorian Ghost Butler formatting
  - Store conversation in ConversationHistory for context


  - _Requirements: 1.1, 7.2, 7.4, 7.5_



- [x] 8.7 Write property test for response completeness





  - **Property 12: Response completeness for confirmations**
  - **Validates: Requirements 7.2**

- [x] 8.8 Write property test for multi-change response completeness





  - **Property 13: Multi-change response completeness**
  - **Validates: Requirements 7.4**

- [x] 9. Checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Implement Google Calendar integration





  - _Requirements: 6.1, 6.2, 6.3, 6.5_



- [x] 10.1 Set up Google Calendar API authentication





  - Implement OAuth2 flow for Google Calendar
  - Store access and refresh tokens in User model
  - Handle token refresh automatically


  - _Requirements: 6.1_

- [x] 10.2 Implement event synchronization to Google Calendar





  - Create sync service that pushes events to Google Calendar on create/update/delete


  - Store Google Calendar event IDs in Event model
  - Implement retry logic with exponential backoff for API failures


  - _Requirements: 6.2, 6.3, 6.5, 10.3_

- [x] 10.3 Write property test for Google Calendar sync consistency





  - **Property 11: Google Calendar sync consistency**
  - **Validates: Requirements 6.2, 6.3**
-

- [x] 10.4 Write property test for retry with exponential backoff




  - **Property 23: Retry with exponential backoff**
  - **Validates: Requirements 10.3**

- [x] 11. Implement comprehensive error handling and logging
  - _Requirements: 10.1, 10.2, 10.3, 10.4_

- [x] 11.1 Set up Django logging configuration


  - Configure logging levels (INFO, WARNING, ERROR, CRITICAL)
  - Set up log file rotation
  - Add structured logging for better parsing
  - _Requirements: 10.1, 10.2_

- [x] 11.2 Implement error handling middleware


  - Create custom exception handler for DRF
  - Return appropriate status codes and error messages
  - Log all errors with context
  - Never expose internal details to users
  - _Requirements: 8.5, 10.2_



- [x] 11.3 Write property test for error logging completeness
  - **Property 22: Error logging completeness**
  - **Validates: Requirements 10.2**
  - **PBT Status**: ✅ PASSED

- [x] 11.4 Add transaction rollback for database failures










  - Ensure all multi-step operations use atomic transactions
  - Implement rollback on any failure
  - Log transaction failures
  - _Requirements: 10.4_
-

-

- [x] 12. Implement data persistence and query operations












  - _Requirements: 5.1, 5.2, 5.3, 5.5_


- [x] 12.1 Implement event persistence with validation

  - Ensure all event fields are saved immediately on creation
  - Validate data before saving
  - Handle database constraints properly
  - _Requirements: 5.1_

- [x] 12.2 Write property test for multi-event atomicity




  - **Property 3: Multi-event atomicity**
  - **Validates: Requirements 1.4**

- [x] 12.3 Implement date range query functionality




  - Create efficient queries for events in time ranges
  - Use database indexes for performance
  - Return only events that intersect with requested range
  - _Requirements: 5.2_

- [x] 12.4 Write property test for query range correctness




  - **Property 9: Query range correctness**
  - **Validates: Requirements 5.2, 8.2**

- [x] 12.5 Verify data persistence across restarts




  - Ensure database connections are properly managed
  - Test that saved events survive application restart
  - _Requirements: 5.5_

- [x] 12.6 Write property test for data persistence across restarts




  - **Property 10: Data persistence across restarts**
  - **Validates: Requirements 5.5**

- [x] 13. Final checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.

- [x] 14. Set up API documentation and testing tools





  - Configure drf-spectacular for OpenAPI/Swagger documentation
  - Generate API schema
  - Set up interactive API documentation at /api/docs/
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 15. Create README and deployment documentation





  - Write README with project overview, setup instructions, and API usage examples
  - Document environment variables required
  - Provide example .env file
  - Include instructions for running tests
  - _Requirements: All_
