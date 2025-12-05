# Phantom Scheduler - Design Document

## Overview

The Phantom scheduler is a Django REST Framework application that provides an AI-powered scheduling backend. The system uses LangChain with Google's Gemini API to process natural language inputs and automatically manage calendar events. The architecture follows a layered approach with clear separation between the API layer, business logic, AI agent, and data persistence.

The system consists of:
- **Django REST Framework API**: RESTful endpoints for event management
- **LangChain AI Agent**: Natural language processing using Gemini API
- **Scheduling Engine**: Priority-based conflict resolution and auto-optimization
- **Database Layer**: PostgreSQL/SQLite for persistent storage
- **External Integration**: Google Calendar API synchronization

## Architecture

### High-Level Architecture

```
┌─────────────────┐
│  Client/Frontend│
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────────────────────────┐
│     Django REST Framework API       │
│  ┌──────────────────────────────┐  │
│  │   ViewSets & Serializers     │  │
│  └──────────────┬───────────────┘  │
└─────────────────┼───────────────────┘
                  │
         ┌────────┴────────┐
         │                 │
         ▼                 ▼
┌─────────────────┐  ┌──────────────────┐
│  LangChain      │  │   Scheduling     │
│  AI Agent       │◄─┤   Engine         │
│  (Gemini API)   │  │                  │
└────────┬────────┘  └────────┬─────────┘
         │                    │
         │                    │
         ▼                    ▼
┌──────────────────────────────────────┐
│         Django ORM / Models          │
│  ┌────────────────────────────────┐ │
│  │  User │ Event │ Category │ etc │ │
│  └────────────────────────────────┘ │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│         Database (PostgreSQL)        │
└──────────────────────────────────────┘
```

### Component Interaction Flow

1. **User Input Flow**:
   - Client sends natural language text to `/api/chat/` endpoint
   - Django view passes input to LangChain Agent
   - Agent processes with Gemini API and extracts scheduling intent
   - Scheduling Engine creates/modifies events based on intent
   - Response returned to client with confirmation

2. **Event Management Flow**:
   - Client makes CRUD requests to `/api/events/` endpoints
   - Django serializers validate input data
   - Business logic in services layer handles scheduling rules
   - ORM persists changes to database
   - Response returned with updated event data

3. **Auto-Optimization Flow**:
   - Event change triggers optimization check
   - Scheduling Engine loads all relevant events
   - Conflict detection algorithm identifies overlaps
   - Priority-based resolution rearranges events
   - Batch update persists all changes atomically

## Components and Interfaces

### 1. Django Apps Structure

```
phantom/
├── manage.py
├── phantom/              # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── scheduler/            # Main scheduling app
│   ├── models.py         # Database models
│   ├── serializers.py    # DRF serializers
│   ├── views.py          # API viewsets
│   ├── services.py       # Business logic
│   ├── urls.py           # App URLs
│   └── tests.py          # Tests
├── ai_agent/             # LangChain integration
│   ├── agent.py          # LangChain agent setup
│   ├── prompts.py        # Prompt templates
│   ├── tools.py          # LangChain tools
│   └── parsers.py        # Output parsers
└── integrations/         # External services
    ├── google_calendar.py
    └── notifications.py
```

### 2. API Endpoints

#### Authentication (Public)
- `POST /api/auth/register/` - Register new user account
- `POST /api/auth/login/` - Login and receive JWT tokens
- `POST /api/auth/logout/` - Logout and blacklist refresh token
- `POST /api/auth/token/refresh/` - Refresh access token using refresh token
- `POST /api/auth/token/verify/` - Verify token validity

#### Event Management (Protected)
- `POST /api/events/` - Create new event
- `GET /api/events/` - List events (with filters)
- `GET /api/events/{id}/` - Retrieve specific event
- `PUT /api/events/{id}/` - Update event
- `DELETE /api/events/{id}/` - Delete event
- `GET /api/events/range/` - Get events in date range

#### Natural Language Interface (Protected)
- `POST /api/chat/` - Process natural language input
- `POST /api/chat/optimize/` - Trigger manual optimization

#### Categories & Priorities (Protected)
- `GET /api/categories/` - List all categories with priorities
- `POST /api/categories/` - Create custom category

#### User Preferences (Protected)
- `GET /api/preferences/` - Get user preferences
- `PUT /api/preferences/` - Update preferences

### 3. LangChain Agent Interface

```python
class PhantomAgent:
    """
    LangChain agent for processing natural language scheduling requests.
    """
    
    def process_input(self, user_input: str, user_id: int) -> AgentResponse:
        """
        Process natural language input and return structured response.
        
        Args:
            user_input: Raw text from user
            user_id: ID of the user making request
            
        Returns:
            AgentResponse with actions and response text
        """
        pass
    
    def extract_scheduling_intent(self, input: str) -> SchedulingIntent:
        """
        Extract scheduling actions from natural language.
        
        Returns:
            SchedulingIntent with action type, entities, and temporal info
        """
        pass
```

### 4. Scheduling Engine Interface

```python
class SchedulingEngine:
    """
    Core scheduling logic for conflict resolution and optimization.
    """
    
    def create_event(self, event_data: dict, user_id: int) -> Event:
        """Create event and resolve conflicts."""
        pass
    
    def optimize_schedule(self, user_id: int, date_range: tuple) -> List[Event]:
        """Optimize all events in date range."""
        pass
    
    def resolve_conflicts(self, events: List[Event]) -> List[Event]:
        """Resolve scheduling conflicts based on priority."""
        pass
    
    def find_free_slots(self, user_id: int, duration: int, date_range: tuple) -> List[datetime]:
        """Find available time slots."""
        pass
```

## Data Models

### User Model
```python
class User(AbstractUser):
    """Extended user model with scheduling preferences."""
    # username, password, email inherited from AbstractUser
    name = models.CharField(max_length=150)  # User's display name
    timezone = models.CharField(max_length=50, default='UTC')
    default_event_duration = models.IntegerField(default=60)  # minutes
    google_calendar_token = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Username is unique and required (from AbstractUser)
    # Password is hashed automatically by Django
```

### BlacklistedToken Model
```python
class BlacklistedToken(models.Model):
    """Store blacklisted refresh tokens for logout functionality."""
    token = models.TextField(unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blacklisted_tokens')
    blacklisted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()  # Token's original expiration
    
    class Meta:
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['expires_at']),
        ]
```

### Category Model
```python
class Category(models.Model):
    """Event categories with priority levels."""
    name = models.CharField(max_length=50, unique=True)
    priority_level = models.IntegerField()  # Higher = more important
    color = models.CharField(max_length=7)  # Hex color
    description = models.TextField(blank=True)
    
    # Default categories: Exam(5), Study(4), Gym(3), Social(2), Gaming(1)
```

### Event Model
```python
class Event(models.Model):
    """Calendar event with scheduling metadata."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    is_flexible = models.BooleanField(default=True)  # Can be rescheduled
    is_completed = models.BooleanField(default=False)
    
    google_calendar_id = models.CharField(max_length=255, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['user', 'start_time']),
            models.Index(fields=['user', 'category']),
        ]
```

### ConversationHistory Model
```python
class ConversationHistory(models.Model):
    """Store conversation context for better AI responses."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    intent_detected = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
```

### SchedulingLog Model
```python
class SchedulingLog(models.Model):
    """Audit log for scheduling operations."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)  # CREATE, UPDATE, DELETE, OPTIMIZE
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True)
    details = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Event creation persistence
*For any* successfully parsed scheduling request, creating an event should result in a database record containing all required fields (title, start_time, end_time, category, user).
**Validates: Requirements 1.2, 11.2**

### Property 2: Exam triggers study sessions
*For any* exam event with a future date, the system should automatically create study session events in the 2-3 days preceding the exam date.
**Validates: Requirements 1.3**

### Property 3: Multi-event atomicity
*For any* set of related events created together, either all events should be persisted to the database or none should be (no partial saves).
**Validates: Requirements 1.4**

### Property 4: Priority-based conflict resolution
*For any* pair of overlapping events with different priority levels, the conflict resolution should preserve the higher priority event and reschedule or remove the lower priority event.
**Validates: Requirements 2.1**

### Property 5: Event preservation during rescheduling
*For any* scheduling optimization operation, the total number of events should remain constant unless events are explicitly deleted by the user.
**Validates: Requirements 2.5**

### Property 6: Duration and category invariance
*For any* event that is rescheduled, the event's duration and category should remain unchanged after rescheduling.
**Validates: Requirements 3.4**

### Property 7: Conflict detection completeness
*For any* schedule containing overlapping events, the optimization algorithm should identify all conflicts (no overlapping events should remain undetected).
**Validates: Requirements 4.2**

### Property 8: Atomic schedule updates
*For any* optimization operation that modifies multiple events, either all changes should be persisted to the database or none should be (transaction atomicity).
**Validates: Requirements 4.5, 5.3**

### Property 9: Query range correctness
*For any* time range query, the returned events should include all and only those events whose time intervals intersect with the requested range.
**Validates: Requirements 5.2, 8.2**

### Property 10: Data persistence across restarts
*For any* set of events saved before system shutdown, all events should be retrievable after system restart with identical data.
**Validates: Requirements 5.5**

### Property 11: Google Calendar sync consistency
*For any* event created or modified in Phantom, the corresponding event in Google Calendar should reflect the same data (title, time, description).
**Validates: Requirements 6.2, 6.3**

### Property 12: Response completeness for confirmations
*For any* successful scheduling operation, the response message should contain the event title and scheduled time.
**Validates: Requirements 7.2**

### Property 13: Multi-change response completeness
*For any* operation that modifies multiple events, the response should mention all modified events.
**Validates: Requirements 7.4**

### Property 14: API response correctness for valid requests
*For any* valid POST request to create an event, the API should return a 201 status code and the response body should contain the created event with all fields.
**Validates: Requirements 8.1**

### Property 15: API update response consistency
*For any* valid PUT request to update an event, the returned event data should match the updated state in the database.
**Validates: Requirements 8.3**

### Property 16: API deletion behavior
*For any* valid DELETE request for an existing event, the event should be removed from the database and a 204 status should be returned.
**Validates: Requirements 8.4**

### Property 17: API error handling
*For any* invalid request (malformed data, missing fields, invalid IDs), the API should return an appropriate error status code (400, 404, 422) and a descriptive error message.
**Validates: Requirements 8.5**

### Property 18: Relative date parsing correctness
*For any* relative time expression (tomorrow, next week, etc.), the parsed absolute date should correctly correspond to the expression relative to the current date.
**Validates: Requirements 9.1**

### Property 19: Multi-day range parsing
*For any* time range expression covering multiple days, the system should create events for all specified days in the range.
**Validates: Requirements 9.2**

### Property 20: Timezone default behavior
*For any* time expression without explicit timezone information, the parsed datetime should use the user's configured timezone.
**Validates: Requirements 9.5**

### Property 21: Operation logging completeness
*For any* scheduling operation (create, update, delete, optimize), a log entry should be created containing timestamp, user ID, and action type.
**Validates: Requirements 10.1**

### Property 22: Error logging completeness
*For any* error that occurs during processing, a log entry should be created containing the error message, stack trace, and input data.
**Validates: Requirements 10.2**

### Property 23: Retry with exponential backoff
*For any* failed external API call, the system should retry the operation with increasing delays between attempts (exponential backoff pattern).
**Validates: Requirements 10.3**

### Property 24: Query filtering correctness
*For any* combination of filters (user, date range, category, priority), the query results should include all and only those events matching all specified filters.
**Validates: Requirements 11.3**

### Property 25: Category relationship integrity
*For any* event with a category, retrieving the event should also provide access to the category name and priority level.
**Validates: Requirements 11.4**

### Property 26: User preference persistence
*For any* user preference update (timezone, default duration, notifications), the new values should be retrievable in subsequent queries.
**Validates: Requirements 11.5**

### Property 27: Agent output parsing correctness
*For any* valid Gemini API response, the LangChain agent should successfully extract scheduling actions and response text without errors.
**Validates: Requirements 12.3**

### Property 28: Action-to-endpoint mapping
*For any* scheduling action determined by the agent (create, update, delete, reschedule), the agent should invoke the correct Django REST Framework endpoint.
**Validates: Requirements 12.4**

### Property 29: Username uniqueness enforcement
*For any* registration attempt with a username that already exists in the database, the system should reject the registration and return an error.
**Validates: Requirements 13.2**

### Property 30: Password security
*For any* user registration or password change, the stored password in the database should be hashed (not plain text).
**Validates: Requirements 13.5**

### Property 31: JWT token generation on login
*For any* successful login with valid credentials, the system should return both an access token and a refresh token.
**Validates: Requirements 14.1**

### Property 32: Invalid credentials rejection
*For any* login attempt with incorrect username or password, the system should return a 401 Unauthorized status.
**Validates: Requirements 14.2**

### Property 33: Protected endpoint authentication
*For any* request to a protected endpoint with a valid access token, the system should authenticate the request and process it normally.
**Validates: Requirements 15.1**

### Property 34: Expired token rejection
*For any* request with an expired access token, the system should return a 401 Unauthorized status.
**Validates: Requirements 15.2**

### Property 35: Token refresh functionality
*For any* valid refresh token submitted to the refresh endpoint, the system should generate and return a new access token.
**Validates: Requirements 16.1**

### Property 36: Blacklisted token rejection
*For any* refresh token that has been blacklisted (after logout), the system should reject refresh attempts and return a 401 Unauthorized status.
**Validates: Requirements 16.5, 17.3**

## Error Handling

### Error Categories

1. **Validation Errors**
   - Invalid date/time formats
   - Missing required fields
   - Invalid category references
   - Constraint violations (end_time before start_time)
   - Response: 400 Bad Request with field-specific error messages

2. **Not Found Errors**
   - Event ID doesn't exist
   - User not found
   - Category not found
   - Response: 404 Not Found with descriptive message

3. **Conflict Errors**
   - Impossible scheduling scenarios (no valid arrangement)
   - Concurrent modification conflicts
   - Response: 409 Conflict with explanation

4. **External Service Errors**
   - Google Calendar API failures
   - Gemini API rate limits or errors
   - Network timeouts
   - Response: 503 Service Unavailable with retry-after header

5. **Authentication Errors**
   - Invalid or expired tokens
   - Insufficient permissions
   - Response: 401 Unauthorized or 403 Forbidden

### Error Handling Strategies

1. **Graceful Degradation**
   - If Google Calendar sync fails, continue with local operations
   - If AI agent fails, fall back to rule-based parsing
   - Log all degradation events for monitoring

2. **Retry Logic**
   - External API calls: 3 retries with exponential backoff (1s, 2s, 4s)
   - Database deadlocks: Automatic retry with Django transaction handling
   - Rate limits: Respect retry-after headers

3. **Transaction Management**
   - Use Django's atomic transactions for multi-event operations
   - Rollback on any failure during optimization
   - Ensure database consistency at all times

4. **User Feedback**
   - Clear error messages in Victorian Ghost Butler persona
   - Actionable suggestions for resolution
   - Never expose internal error details to users

### Logging Strategy

- **INFO**: Successful operations, event creations, optimizations
- **WARNING**: Degraded functionality, retry attempts, near-limit conditions
- **ERROR**: Failed operations, validation errors, external service failures
- **CRITICAL**: Data corruption risks, system-wide failures, security issues

## Testing Strategy

### Unit Testing

The system will use Django's built-in testing framework with pytest for enhanced functionality. Unit tests will cover:

1. **Model Tests**
   - Model validation logic
   - Custom model methods
   - Database constraints
   - Example: Test that Event.clean() raises ValidationError when end_time < start_time

2. **Serializer Tests**
   - Data validation
   - Serialization/deserialization
   - Custom field handling
   - Example: Test that EventSerializer rejects events with invalid category IDs

3. **API Endpoint Tests**
   - Request/response formats
   - Status codes
   - Authentication and permissions
   - Example: Test that unauthenticated requests to /api/events/ return 401

4. **Service Layer Tests**
   - Business logic correctness
   - Edge cases (empty schedules, single events, etc.)
   - Example: Test that SchedulingEngine.find_free_slots() returns empty list when no slots available

5. **Integration Tests**
   - End-to-end API workflows
   - Database transaction behavior
   - Example: Test complete flow from natural language input to event creation

### Property-Based Testing

The system will use **Hypothesis** (Python property-based testing library) to verify universal properties. Each property-based test will:

- Run a minimum of 100 iterations with randomly generated inputs
- Be tagged with a comment referencing the specific correctness property from this design document
- Use the format: `# Feature: phantom-scheduler, Property X: <property text>`

Property-based tests will cover:

1. **Scheduling Properties**
   - Property 4: Priority-based conflict resolution
   - Property 5: Event preservation during rescheduling
   - Property 6: Duration and category invariance
   - Property 7: Conflict detection completeness

2. **Data Persistence Properties**
   - Property 1: Event creation persistence
   - Property 8: Atomic schedule updates
   - Property 10: Data persistence across restarts

3. **Query Properties**
   - Property 9: Query range correctness
   - Property 24: Query filtering correctness

4. **API Properties**
   - Property 14: API response correctness for valid requests
   - Property 15: API update response consistency
   - Property 17: API error handling

5. **Parsing Properties**
   - Property 18: Relative date parsing correctness
   - Property 20: Timezone default behavior

### Test Data Generation

Hypothesis strategies will be defined for:

- **Random events**: Generate events with random titles, times, categories, and users
- **Random schedules**: Generate collections of events with controlled overlap
- **Random time expressions**: Generate various natural language time references
- **Random API payloads**: Generate valid and invalid request bodies

### Testing Configuration

```python
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = phantom.settings
python_files = tests.py test_*.py *_tests.py
addopts = --hypothesis-show-statistics --hypothesis-seed=random

# Hypothesis settings
hypothesis_profile = dev
hypothesis_max_examples = 100
```

### Continuous Testing

- All tests must pass before merging to main branch
- Property-based tests run on every commit
- Integration tests run on pull requests
- Performance tests run nightly

## Implementation Notes

### Technology Stack

- **Framework**: Django 4.2+ with Django REST Framework 3.14+
- **Authentication**: djangorestframework-simplejwt for JWT token management
- **Database**: PostgreSQL 14+ (production), SQLite (development)
- **AI**: LangChain 0.1+ with Google Gemini API
- **Testing**: pytest-django, Hypothesis
- **Task Queue**: Celery with Redis (for async operations)
- **API Documentation**: drf-spectacular (OpenAPI/Swagger)

### Development Phases

1. **Phase 1: Core Models and API**
   - Set up Django project structure
   - Implement database models
   - Create basic CRUD API endpoints
   - Write model and serializer tests

2. **Phase 2: Scheduling Engine**
   - Implement conflict detection algorithm
   - Build priority-based resolution logic
   - Create optimization engine
   - Write property-based tests for scheduling

3. **Phase 3: LangChain Integration**
   - Set up LangChain with Gemini API
   - Create prompt templates for Victorian Ghost Butler persona
   - Implement natural language parsing
   - Build agent tools for calendar operations

4. **Phase 4: External Integrations**
   - Implement Google Calendar sync
   - Add webhook handlers for external changes
   - Create retry and error handling logic

5. **Phase 5: Optimization and Polish**
   - Performance tuning
   - Comprehensive error handling
   - Logging and monitoring
   - API documentation

### Security Considerations

- Use Django's built-in authentication and authorization
- Store API keys in environment variables (never in code)
- Implement rate limiting on API endpoints
- Validate and sanitize all user inputs
- Use HTTPS for all external API calls
- Implement CORS properly for frontend access

### Performance Considerations

- Index database fields used in queries (user_id, start_time, category_id)
- Use select_related() and prefetch_related() to minimize database queries
- Cache category priority mappings
- Implement pagination for event lists
- Use Celery for long-running optimization tasks
- Consider read replicas for high-traffic scenarios
