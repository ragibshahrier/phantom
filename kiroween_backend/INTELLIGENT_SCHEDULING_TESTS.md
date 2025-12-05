# Intelligent Scheduling Tests Documentation

## Overview

This document describes the comprehensive test suite for verifying that the Phantom AI agent can properly understand implicit user needs and perform database operations (create, update, reshuffle, delete) without explicit instructions.

## Test File

**Location:** `kiroween_backend/ai_agent/test_intelligent_scheduling.py`

## Test Classes

### 1. IntelligentSchedulingTestCase

Integration tests for intelligent scheduling behavior that verify the agent can:
- Understand implicit scheduling needs
- Create events automatically
- Create related events (e.g., study sessions for exams)
- Reshuffle/reschedule conflicting events
- Delete low-priority events when needed

#### Test Methods

##### test_exam_creates_study_sessions
**User Input:** "I have a math exam on Friday"

**Expected Behavior:**
- Creates the exam event on Friday (9 AM - 12 PM)
- Automatically creates 2-3 study sessions on Wed/Thu evenings (6 PM - 8 PM)
- Study sessions are properly linked to the exam topic

**Verifies:**
- Automatic creation of related events
- Intelligent time slot selection
- Proper event categorization

##### test_conflict_resolution_reschedules_lower_priority
**Scenario:** High-priority event scheduled when low-priority event exists at same time

**Expected Behavior:**
- Low-priority event (Gaming) is automatically rescheduled
- High-priority event (Study) takes the original time slot
- Both events exist without overlap

**Verifies:**
- Priority-based conflict resolution
- Automatic rescheduling
- No data loss

##### test_fatigue_cancels_and_reshuffles
**User Input:** "I'm too tired to study right now"

**Expected Behavior:**
- Current study block is cancelled/deleted
- Remaining week is reshuffled to compensate
- Exam preparation remains adequate
- Replacement session is created at alternative time

**Verifies:**
- Dynamic schedule adjustment
- Context-aware cancellation
- Intelligent rescheduling

##### test_minimal_input_creates_event
**User Input:** "Need to work out"

**Expected Behavior:**
- Creates gym session with intelligent defaults:
  - Time: Morning (7 AM) or evening (6 PM)
  - Duration: 1 hour
  - Category: Gym
  - Flexibility: True

**Verifies:**
- Minimal input interpretation
- Intelligent default values
- Optimal time slot selection

##### test_social_event_with_minimal_details
**User Input:** "Meeting Sarah tomorrow"

**Expected Behavior:**
- Creates social event with defaults:
  - Time: Afternoon (2 PM)
  - Duration: 2-3 hours
  - Category: Social
  - Title includes person's name

**Verifies:**
- Natural language understanding
- Context extraction (person's name)
- Appropriate default values

##### test_exam_clears_low_priority_conflicts
**Scenario:** Exam scheduled within 48 hours with conflicting low-priority events

**Expected Behavior:**
- Gaming and Social events are automatically deleted
- Exam and study sessions take priority
- Schedule is optimized for exam preparation

**Verifies:**
- Proactive conflict resolution
- Priority-based deletion
- Exam preparation optimization

##### test_gym_moves_to_morning_on_evening_conflict
**Scenario:** Study session conflicts with evening gym session

**Expected Behavior:**
- Gym session is automatically moved to morning (7 AM)
- Study session remains in evening slot
- No overlap between events

**Verifies:**
- Intelligent rescheduling logic
- Time-of-day preferences
- Conflict avoidance

##### test_multiple_events_from_single_message
**User Input:** "I have a math exam on Friday chapter 5"

**Expected Behavior:**
- Creates 3 events from single message:
  - 1 exam event
  - 2 study sessions
- All events are related to the same topic
- Events are properly sequenced

**Verifies:**
- Multi-event creation
- Topic coherence
- Temporal sequencing

##### test_priority_hierarchy_maintained
**Scenario:** Multiple events at same time with different priorities

**Expected Behavior:**
- Highest priority event (Study - Priority 4) remains
- Lower priority events are rescheduled or deleted:
  - Gaming (Priority 1) - deleted
  - Social (Priority 2) - deleted
  - Gym (Priority 3) - rescheduled to morning

**Verifies:**
- Strict priority hierarchy enforcement
- Appropriate conflict resolution strategies
- No compromise of high-priority events

### 2. AgentContextAwarenessTestCase

Tests for agent context awareness and intelligent decision-making.

#### Test Methods

##### test_agent_receives_current_schedule_context
**Scenario:** Agent makes decisions with existing events

**Expected Behavior:**
- Agent receives current schedule (next 7 days)
- Agent can see existing events
- Decisions are made with full context

**Verifies:**
- Context passing to agent
- Schedule awareness
- Informed decision-making

##### test_agent_avoids_double_booking
**Scenario:** Creating new event when existing event occupies time slot

**Expected Behavior:**
- New event is scheduled around existing event
- No overlap occurs
- Both events coexist

**Verifies:**
- Conflict detection
- Automatic time slot adjustment
- Double-booking prevention

##### test_agent_uses_timezone_context
**Scenario:** User in specific timezone creates events

**Expected Behavior:**
- Events are created in user's timezone
- Times are correctly converted
- Timezone information is preserved

**Verifies:**
- Timezone awareness
- Correct time handling
- Timezone-aware datetime objects

## Running the Tests

### Method 1: Using Django Test Runner

```bash
cd kiroween_backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python manage.py test ai_agent.test_intelligent_scheduling --verbosity=2
```

### Method 2: Using Test Script

```bash
cd kiroween_backend
chmod +x run_intelligent_tests.sh
./run_intelligent_tests.sh
```

### Method 3: Run Specific Test

```bash
python manage.py test ai_agent.test_intelligent_scheduling.IntelligentSchedulingTestCase.test_exam_creates_study_sessions
```

## Test Coverage

The test suite covers:

### 1. Implicit Understanding
- ✅ Exam scheduling with automatic study sessions
- ✅ Minimal input interpretation ("Need to work out")
- ✅ Natural language parsing ("Meeting Sarah tomorrow")
- ✅ Fatigue-based rescheduling ("I'm too tired")

### 2. Database Operations

#### Create
- ✅ Single event creation
- ✅ Multiple related events creation
- ✅ Events with intelligent defaults

#### Update
- ✅ Automatic rescheduling on conflicts
- ✅ Time slot adjustments
- ✅ Priority-based modifications

#### Delete
- ✅ Low-priority event deletion for exam prep
- ✅ Fatigue-based cancellation
- ✅ Conflict-driven deletion

#### Reshuffle
- ✅ Week-wide schedule optimization
- ✅ Priority-based reordering
- ✅ Time-of-day adjustments (gym to morning)

### 3. Priority Management
- ✅ Priority hierarchy enforcement (5 > 4 > 3 > 2 > 1)
- ✅ Higher priority events never compromised
- ✅ Lower priority events rescheduled/deleted appropriately

### 4. Context Awareness
- ✅ Current schedule visibility
- ✅ Timezone handling
- ✅ Double-booking prevention
- ✅ Informed decision-making

### 5. Intelligent Defaults
- ✅ Time defaults (Morning: 9 AM, Afternoon: 2 PM, Evening: 6 PM)
- ✅ Duration defaults (Exam: 2-3h, Study: 2h, Gym: 1h, Social: 2-3h, Gaming: 1-2h)
- ✅ Category inference from context
- ✅ Flexibility settings

## Expected Test Results

All tests should pass, demonstrating:

1. **Automatic Event Creation**: Agent creates events without explicit "create" commands
2. **Intelligent Scheduling**: Agent uses smart defaults and optimal time slots
3. **Conflict Resolution**: Agent automatically resolves scheduling conflicts
4. **Priority Enforcement**: Higher priority events are never compromised
5. **Context Awareness**: Agent makes decisions based on existing schedule
6. **Natural Language Understanding**: Agent interprets minimal, natural input

## Integration with Enhanced Prompts

These tests verify the behavior defined in the enhanced system prompts:

- **INTELLIGENT SCHEDULING - AUTOMATIC INTERPRETATION** section
- **CONFLICT RESOLUTION RULES** section
- **PROACTIVE BEHAVIOR** section
- **Default times and durations** specifications

## Troubleshooting

### Tests Fail Due to Missing Dependencies

```bash
pip install -r requirements.txt
```

### Tests Fail Due to Database Issues

```bash
python manage.py migrate
python manage.py populate_categories
```

### Tests Fail Due to Timezone Issues

Ensure `pytz` is installed:
```bash
pip install pytz
```

### Mock Issues

The tests use `unittest.mock.patch` to mock the Gemini API. If tests fail due to API calls, verify:
- Mock decorators are properly applied
- Mock return values are correctly configured
- API key is not being used in tests

## Future Enhancements

Potential additions to the test suite:

1. **Learning Tests**: Verify agent learns user preferences over time
2. **Pattern Recognition Tests**: Test recurring event detection
3. **Optimization Tests**: Verify schedule optimization algorithms
4. **Multi-User Tests**: Test concurrent scheduling for multiple users
5. **Performance Tests**: Measure response time for complex schedules
6. **Edge Case Tests**: Test boundary conditions and unusual inputs

## Conclusion

This comprehensive test suite ensures that the Phantom AI agent can:
- Understand implicit user needs
- Perform database operations intelligently
- Maintain schedule integrity
- Enforce priority rules
- Provide a seamless, natural scheduling experience

All tests should pass before deploying the enhanced agent to production.
