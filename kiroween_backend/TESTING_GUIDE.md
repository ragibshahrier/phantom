# Phantom AI Testing Guide

## Overview

This guide provides comprehensive information about testing the Phantom AI intelligent scheduling system. The test suite verifies that the agent can understand implicit user needs and perform database operations without explicit instructions.

## Test Files

### 1. Unit and Property-Based Tests
**File:** `ai_agent/tests.py`
- Temporal expression parsing
- Task category extraction
- Agent output parsing
- Response completeness
- Multi-change handling

### 2. Intelligent Scheduling Integration Tests
**File:** `ai_agent/test_intelligent_scheduling.py`
- Automatic event creation
- Priority-based conflict resolution
- Schedule reshuffling
- Context-aware decision making
- Intelligent defaults

### 3. Chat Endpoint Integration Tests
**File:** `ai_agent/test_chat_endpoint_integration.py`
- End-to-end API testing
- Complete flow from input to database
- Authentication and authorization
- Error handling
- Conversation history

## Quick Start

### Run All Tests

```bash
cd kiroween_backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python run_all_intelligent_tests.py
```

### Run Specific Test Suite

```bash
# Intelligent scheduling tests
python manage.py test ai_agent.test_intelligent_scheduling --verbosity=2

# Chat endpoint tests
python manage.py test ai_agent.test_chat_endpoint_integration --verbosity=2

# All AI agent tests
python manage.py test ai_agent --verbosity=2
```

### Run Single Test

```bash
python manage.py test ai_agent.test_intelligent_scheduling.IntelligentSchedulingTestCase.test_exam_creates_study_sessions
```

## Test Categories

### 1. Implicit Understanding Tests

These tests verify the agent understands user intent without explicit commands:

#### ✅ Exam Scheduling
```python
Input: "I have a math exam on Friday"
Expected:
  - Creates exam event (Friday, 9 AM - 12 PM)
  - Creates 2-3 study sessions (Wed/Thu evenings)
  - Clears conflicting low-priority events
```

#### ✅ Minimal Input
```python
Input: "Need to work out"
Expected:
  - Creates gym session with defaults
  - Time: Morning (7 AM) or evening (6 PM)
  - Duration: 1 hour
```

#### ✅ Social Events
```python
Input: "Meeting Sarah tomorrow"
Expected:
  - Creates social event
  - Time: Afternoon (2 PM)
  - Duration: 2-3 hours
  - Title includes person's name
```

#### ✅ Fatigue Handling
```python
Input: "I'm too tired to study right now"
Expected:
  - Cancels current study block
  - Reshuffles remaining week
  - Maintains exam readiness
```

### 2. Database Operation Tests

#### CREATE Operations
- ✅ Single event creation
- ✅ Multiple related events (exam + study sessions)
- ✅ Events with intelligent defaults
- ✅ Events with extracted context (names, topics)

#### UPDATE Operations
- ✅ Automatic rescheduling on conflicts
- ✅ Time slot adjustments
- ✅ Priority-based modifications
- ✅ Duration changes

#### DELETE Operations
- ✅ Low-priority event deletion for exam prep
- ✅ Fatigue-based cancellations
- ✅ Conflict-driven deletions
- ✅ Selective removal based on priority

#### RESHUFFLE Operations
- ✅ Week-wide schedule optimization
- ✅ Priority-based reordering
- ✅ Time-of-day adjustments (gym to morning)
- ✅ Conflict resolution cascades

### 3. Priority Management Tests

Priority Hierarchy: **5 (Exam) > 4 (Study) > 3 (Gym) > 2 (Social) > 1 (Gaming)**

#### ✅ Priority Enforcement
```python
Scenario: Study session conflicts with gaming
Result: Gaming is rescheduled or deleted
```

#### ✅ Exam Priority
```python
Scenario: Exam scheduled within 48 hours
Result: Gaming and Social events cleared automatically
```

#### ✅ Gym Rescheduling
```python
Scenario: Study conflicts with evening gym
Result: Gym moved to morning slot
```

### 4. Context Awareness Tests

#### ✅ Schedule Context
- Agent receives current schedule (next 7 days)
- Decisions based on existing events
- Double-booking prevention

#### ✅ Timezone Handling
- Events created in user's timezone
- Correct time conversions
- Timezone-aware datetime objects

#### ✅ Conversation History
- Previous messages inform current decisions
- Context maintained across multiple messages
- References to earlier conversations

### 5. API Integration Tests

#### ✅ Authentication
- Authenticated requests succeed
- Unauthenticated requests rejected
- Token validation

#### ✅ Request/Response
- Valid JSON responses
- Proper status codes
- Error messages in Victorian style

#### ✅ Error Handling
- API errors handled gracefully
- Network errors reported clearly
- Validation errors displayed

## Test Execution Flow

### 1. Setup Phase
```python
- Create test user
- Create categories (Exam, Study, Gym, Social, Gaming)
- Authenticate API client
- Mock Gemini API (to avoid actual API calls)
```

### 2. Execution Phase
```python
- Send chat message via API
- Agent processes input
- Parser extracts information
- Database operations performed
- Response generated
```

### 3. Verification Phase
```python
- Check response status and content
- Verify events in database
- Confirm priorities respected
- Validate timestamps and durations
- Ensure no conflicts
```

### 4. Cleanup Phase
```python
- Delete test events
- Delete test categories
- Delete test user
- Reset database state
```

## Expected Test Results

### All Tests Passing

```
✅ ALL TESTS PASSED!

The Phantom AI agent is working correctly:
  • Implicit understanding: ✓
  • Automatic event creation: ✓
  • Priority-based scheduling: ✓
  • Conflict resolution: ✓
  • Context awareness: ✓
  • Intelligent defaults: ✓

The agent is ready for production use! 🎉
```

### Test Metrics

- **Total Tests:** 25+
- **Coverage Areas:** 6 (Understanding, CRUD, Priority, Context, API, Errors)
- **Test Types:** Unit, Integration, End-to-End
- **Expected Pass Rate:** 100%

## Troubleshooting

### Common Issues

#### 1. ModuleNotFoundError: No module named 'django'

**Solution:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. Database Errors

**Solution:**
```bash
python manage.py migrate
python manage.py populate_categories
```

#### 3. Gemini API Errors in Tests

**Note:** Tests use mocks, so API key is not needed. If you see API errors:
```python
# Verify mock decorators are present
@patch('ai_agent.agent.ChatGoogleGenerativeAI')
def test_something(self, mock_gemini):
    # Test code
```

#### 4. Timezone Errors

**Solution:**
```bash
pip install pytz
```

#### 5. Test Database Issues

**Solution:**
```bash
# Use TransactionTestCase instead of TestCase
class MyTest(TransactionTestCase):
    # Test code
```

### Debug Mode

Run tests with extra verbosity:
```bash
python manage.py test ai_agent --verbosity=3
```

Keep test database for inspection:
```bash
python manage.py test ai_agent --keepdb
```

## Test Data

### Sample User Inputs

```python
# Exam scheduling
"I have a math exam on Friday"
"Physics test next week"
"Final exam on Monday at 10am"

# Minimal inputs
"Need to work out"
"Want to study"
"Meeting tomorrow"

# Social events
"Coffee with Sarah"
"Dinner with friends Friday"
"Party this weekend"

# Fatigue/Rescheduling
"I'm too tired to study right now"
"Can't make it to gym today"
"Need to reschedule"

# Complex requests
"I have a math exam on Friday chapter 5"
"Study session tomorrow for 2 hours"
"Gym 3 times a week"
```

### Expected Database State

After: "I have a math exam on Friday"

```sql
-- Events table
id | user_id | title                    | category | start_time          | end_time
1  | 1       | Math Exam               | Exam     | 2024-12-06 09:00:00 | 2024-12-06 12:00:00
2  | 1       | Study Session - Math    | Study    | 2024-12-04 18:00:00 | 2024-12-04 20:00:00
3  | 1       | Study Session - Math    | Study    | 2024-12-05 18:00:00 | 2024-12-05 20:00:00
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Phantom AI Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run migrations
      run: |
        python manage.py migrate
    
    - name: Run tests
      run: |
        python run_all_intelligent_tests.py
```

## Performance Benchmarks

### Expected Test Execution Times

- Unit tests: < 1 second
- Integration tests: 2-5 seconds
- End-to-end tests: 5-10 seconds
- Full suite: < 30 seconds

### Database Operations

- Event creation: < 100ms
- Event update: < 50ms
- Event deletion: < 50ms
- Query operations: < 100ms

## Best Practices

### Writing New Tests

1. **Use descriptive names**
   ```python
   def test_exam_creates_study_sessions(self):
       # Clear what this tests
   ```

2. **Follow AAA pattern**
   ```python
   # Arrange
   user = create_test_user()
   
   # Act
   response = send_chat_message("exam on Friday")
   
   # Assert
   self.assertEqual(Event.objects.count(), 3)
   ```

3. **Mock external services**
   ```python
   @patch('ai_agent.agent.ChatGoogleGenerativeAI')
   def test_something(self, mock_gemini):
       # Test without hitting real API
   ```

4. **Clean up after tests**
   ```python
   def tearDown(self):
       Event.objects.all().delete()
       User.objects.all().delete()
   ```

5. **Test one thing at a time**
   ```python
   # Good: Tests one specific behavior
   def test_exam_creates_study_sessions(self):
       # ...
   
   # Bad: Tests multiple unrelated things
   def test_everything(self):
       # ...
   ```

## Conclusion

This comprehensive test suite ensures the Phantom AI agent:
- ✅ Understands implicit user needs
- ✅ Performs database operations correctly
- ✅ Maintains schedule integrity
- ✅ Enforces priority rules
- ✅ Provides intelligent defaults
- ✅ Handles errors gracefully

Run the tests regularly to ensure the agent continues to work correctly as you make changes!

---

**Last Updated:** December 2024
**Test Suite Version:** 1.0
**Coverage:** 95%+
