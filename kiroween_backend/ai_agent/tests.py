"""
Tests for AI agent components including temporal parsing and task extraction.
"""
from django.test import TestCase
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings, assume
from hypothesis.extra.django import TestCase as HypothesisTestCase
from hypothesis.extra.pytz import timezones
import pytz

from .parsers import TemporalExpressionParser, TaskCategoryExtractor, AgentOutputParser
from .tools import CreateEventTool, UpdateEventTool, DeleteEventTool, QueryEventsTool, get_calendar_tools


class TestTemporalExpressionParser(HypothesisTestCase):
    """
    Property-based tests for temporal expression parsing.
    
    Tests Requirements: 9.1, 9.2, 9.5
    """
    
    @settings(max_examples=100)
    @given(
        timezone_str=timezones(),
        reference_time=st.datetimes(
            min_value=datetime(2020, 1, 1),
            max_value=datetime(2030, 12, 31)
        ),
        relative_expression=st.sampled_from([
            'tomorrow', 'today', 'next friday', 'next monday',
            'next tuesday', 'next wednesday', 'next thursday',
            'next saturday', 'next sunday', 'this friday',
            'this monday', 'in 3 days', 'in 7 days', 'next week'
        ])
    )
    def test_relative_date_parsing_correctness(self, timezone_str, reference_time, relative_expression):
        """
        Feature: phantom-scheduler, Property 18: Relative date parsing correctness
        
        For any relative time expression (tomorrow, next week, etc.), 
        the parsed absolute date should correctly correspond to the expression 
        relative to the current date.
        
        Validates: Requirements 9.1
        """
        # Make reference_time timezone-aware
        tz = pytz.timezone(str(timezone_str))
        if reference_time.tzinfo is None:
            reference_time = tz.localize(reference_time)
        else:
            reference_time = reference_time.astimezone(tz)
        
        # Create parser with the reference time
        parser = TemporalExpressionParser(
            user_timezone=str(timezone_str),
            reference_time=reference_time
        )
        
        # Parse the expression
        results = parser.parse(relative_expression)
        
        # Should return at least one result
        self.assertGreater(len(results), 0, f"Parser should return results for '{relative_expression}'")
        
        start_time, end_time = results[0]
        
        # Verify the parsed date is reasonable relative to reference time
        # For "today", it should be the same date (but may not be exactly >= due to time of day)
        # For future expressions, it should be >= reference time
        if 'today' not in relative_expression:
            self.assertGreaterEqual(
                start_time, reference_time,
                f"Parsed time {start_time} should be >= reference time {reference_time} for '{relative_expression}'"
            )
        
        # Verify end_time is after start_time
        self.assertGreater(
            end_time, start_time,
            f"End time should be after start time for '{relative_expression}'"
        )
        
        # Verify specific relative expressions
        if 'tomorrow' in relative_expression:
            # Tomorrow should be 1 day ahead (within reasonable bounds)
            days_diff = (start_time.date() - reference_time.date()).days
            self.assertEqual(
                days_diff, 1,
                f"'tomorrow' should be 1 day ahead, got {days_diff} days"
            )
        
        elif 'today' in relative_expression:
            # Today should be the same date
            self.assertEqual(
                start_time.date(), reference_time.date(),
                "'today' should be the same date as reference time"
            )
        
        elif 'next week' in relative_expression:
            # Next week should be 7 days ahead
            days_diff = (start_time.date() - reference_time.date()).days
            self.assertEqual(
                days_diff, 7,
                f"'next week' should be 7 days ahead, got {days_diff} days"
            )
        
        elif 'in 3 days' in relative_expression:
            days_diff = (start_time.date() - reference_time.date()).days
            self.assertEqual(
                days_diff, 3,
                f"'in 3 days' should be 3 days ahead, got {days_diff} days"
            )
        
        elif 'in 7 days' in relative_expression:
            days_diff = (start_time.date() - reference_time.date()).days
            self.assertEqual(
                days_diff, 7,
                f"'in 7 days' should be 7 days ahead, got {days_diff} days"
            )
        
        elif 'next' in relative_expression:
            # Next [weekday] should be within 1-7 days
            days_diff = (start_time.date() - reference_time.date()).days
            self.assertGreaterEqual(days_diff, 1, "Next weekday should be at least 1 day ahead")
            self.assertLessEqual(days_diff, 7, "Next weekday should be at most 7 days ahead")
        
        elif 'this' in relative_expression:
            # This [weekday] should be within 0-7 days
            days_diff = (start_time.date() - reference_time.date()).days
            self.assertGreaterEqual(days_diff, 0, "This weekday should be at least 0 days ahead")
            self.assertLessEqual(days_diff, 7, "This weekday should be at most 7 days ahead")
    
    @settings(max_examples=100)
    @given(
        timezone_str=timezones(),
        reference_time=st.datetimes(
            min_value=datetime(2020, 1, 1),
            max_value=datetime(2030, 12, 31)
        ),
        day1=st.sampled_from(['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']),
        day2=st.sampled_from(['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']),
        time_of_day=st.sampled_from(['morning', 'afternoon', 'evening', 'night', ''])
    )
    def test_multi_day_range_parsing(self, timezone_str, reference_time, day1, day2, time_of_day):
        """
        Feature: phantom-scheduler, Property 19: Multi-day range parsing
        
        For any time range expression covering multiple days, 
        the system should create events for all specified days in the range.
        
        Validates: Requirements 9.2
        """
        # Make reference_time timezone-aware
        tz = pytz.timezone(str(timezone_str))
        if reference_time.tzinfo is None:
            reference_time = tz.localize(reference_time)
        else:
            reference_time = reference_time.astimezone(tz)
        
        # Create parser
        parser = TemporalExpressionParser(
            user_timezone=str(timezone_str),
            reference_time=reference_time
        )
        
        # Create multi-day expression
        expression = f"{day1} and {day2} {time_of_day}".strip()
        
        # Parse the expression
        results = parser.parse(expression)
        
        # Should return at least one result
        self.assertGreater(len(results), 0, f"Parser should return results for '{expression}'")
        
        # If day1 and day2 are the same, we should get 1 result
        # If they're different, we should get multiple results
        if day1 == day2:
            self.assertEqual(len(results), 1, f"Same day range should return 1 result")
        else:
            # Should have at least 2 results (one for each day)
            self.assertGreaterEqual(len(results), 2, f"Multi-day range should return at least 2 results")
        
        # Verify all results are valid datetime tuples
        for start_time, end_time in results:
            self.assertIsInstance(start_time, datetime)
            self.assertIsInstance(end_time, datetime)
            self.assertGreater(end_time, start_time, "End time should be after start time")
            self.assertGreaterEqual(start_time, reference_time, "Parsed time should be >= reference time")
        
        # Verify results are in chronological order
        for i in range(len(results) - 1):
            self.assertLess(
                results[i][0], results[i + 1][0],
                "Results should be in chronological order"
            )
    
    @settings(max_examples=100)
    @given(
        timezone_str=timezones(),
        reference_time=st.datetimes(
            min_value=datetime(2020, 1, 1),
            max_value=datetime(2030, 12, 31)
        ),
        expression=st.sampled_from([
            'tomorrow morning', 'today afternoon', 'next friday evening',
            'in 3 days', 'next week'
        ])
    )
    def test_timezone_default_behavior(self, timezone_str, reference_time, expression):
        """
        Feature: phantom-scheduler, Property 20: Timezone default behavior
        
        For any time expression without explicit timezone information, 
        the parsed datetime should use the user's configured timezone.
        
        Validates: Requirements 9.5
        """
        # Make reference_time timezone-aware
        tz = pytz.timezone(str(timezone_str))
        if reference_time.tzinfo is None:
            reference_time = tz.localize(reference_time)
        else:
            reference_time = reference_time.astimezone(tz)
        
        # Create parser with user's timezone
        parser = TemporalExpressionParser(
            user_timezone=str(timezone_str),
            reference_time=reference_time
        )
        
        # Parse the expression (no explicit timezone in the text)
        results = parser.parse(expression)
        
        # Should return at least one result
        self.assertGreater(len(results), 0, f"Parser should return results for '{expression}'")
        
        start_time, end_time = results[0]
        
        # Verify the parsed datetime uses the user's timezone
        self.assertIsNotNone(start_time.tzinfo, "Parsed datetime should be timezone-aware")
        self.assertIsNotNone(end_time.tzinfo, "Parsed datetime should be timezone-aware")
        
        # The timezone should match the user's configured timezone
        # (comparing timezone names as strings)
        self.assertEqual(
            str(start_time.tzinfo), str(tz),
            f"Parsed datetime should use user's timezone {tz}, got {start_time.tzinfo}"
        )
        self.assertEqual(
            str(end_time.tzinfo), str(tz),
            f"Parsed datetime should use user's timezone {tz}, got {end_time.tzinfo}"
        )


class TestTaskCategoryExtractor(TestCase):
    """
    Unit tests for task category extraction.
    
    Tests Requirements: 1.1, 1.5
    """
    
    def test_extract_exam_category(self):
        """Test extraction of Exam category."""
        extractor = TaskCategoryExtractor()
        
        self.assertEqual(extractor.extract_category("I have an exam tomorrow"), "Exam")
        self.assertEqual(extractor.extract_category("midterm next week"), "Exam")
        self.assertEqual(extractor.extract_category("final test on Friday"), "Exam")
    
    def test_extract_study_category(self):
        """Test extraction of Study category."""
        extractor = TaskCategoryExtractor()
        
        self.assertEqual(extractor.extract_category("study session tonight"), "Study")
        self.assertEqual(extractor.extract_category("homework due tomorrow"), "Study")
        self.assertEqual(extractor.extract_category("review notes"), "Study")
    
    def test_extract_gym_category(self):
        """Test extraction of Gym category."""
        extractor = TaskCategoryExtractor()
        
        self.assertEqual(extractor.extract_category("gym workout tomorrow"), "Gym")
        self.assertEqual(extractor.extract_category("go for a run"), "Gym")
        self.assertEqual(extractor.extract_category("exercise in the morning"), "Gym")
    
    def test_extract_social_category(self):
        """Test extraction of Social category."""
        extractor = TaskCategoryExtractor()
        
        self.assertEqual(extractor.extract_category("meet friends for dinner"), "Social")
        self.assertEqual(extractor.extract_category("coffee with Sarah"), "Social")
        self.assertEqual(extractor.extract_category("party tonight"), "Social")
    
    def test_extract_gaming_category(self):
        """Test extraction of Gaming category."""
        extractor = TaskCategoryExtractor()
        
        self.assertEqual(extractor.extract_category("gaming session tonight"), "Gaming")
        self.assertEqual(extractor.extract_category("play valorant"), "Gaming")
        self.assertEqual(extractor.extract_category("stream on twitch"), "Gaming")
    
    def test_no_category_detected(self):
        """Test when no category can be detected."""
        extractor = TaskCategoryExtractor()
        
        self.assertIsNone(extractor.extract_category("something random"))
        self.assertIsNone(extractor.extract_category("meeting at 3pm"))
    
    def test_extract_task_title(self):
        """Test task title extraction."""
        extractor = TaskCategoryExtractor()
        
        # Should remove temporal expressions
        self.assertEqual(
            extractor.extract_task_title("schedule exam tomorrow"),
            "exam"
        )
        
        self.assertEqual(
            extractor.extract_task_title("study for math test next friday"),
            "study for math test"
        )
        
        # Should handle simple cases
        self.assertEqual(
            extractor.extract_task_title("gym workout"),
            "gym workout"
        )
    
    def test_is_ambiguous(self):
        """Test ambiguity detection."""
        extractor = TaskCategoryExtractor()
        
        # Too short
        self.assertTrue(extractor.is_ambiguous("hi"))
        self.assertTrue(extractor.is_ambiguous("a"))
        
        # Clear input
        self.assertFalse(extractor.is_ambiguous("exam tomorrow"))
        self.assertFalse(extractor.is_ambiguous("study session tonight"))



class TestAgentOutputParser(HypothesisTestCase):
    """
    Property-based tests for agent output parsing.
    
    Tests Requirements: 12.3
    """
    
    @settings(max_examples=100)
    @given(
        action_type=st.sampled_from(['create', 'update', 'delete', 'reschedule', 'query', 'optimize']),
        event_title=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=['Cs', 'Cc'])),
        category=st.sampled_from(['Exam', 'Study', 'Gym', 'Social', 'Gaming']),
        event_id=st.integers(min_value=1, max_value=10000),
        duration=st.integers(min_value=15, max_value=480),
        response_text=st.text(min_size=10, max_size=200, alphabet=st.characters(blacklist_categories=['Cs', 'Cc']))
    )
    def test_agent_output_parsing_correctness(self, action_type, event_title, category, event_id, duration, response_text):
        """
        Feature: phantom-scheduler, Property 27: Agent output parsing correctness
        
        For any valid Gemini API response, the LangChain agent should successfully 
        extract scheduling actions and response text without errors.
        
        Validates: Requirements 12.3
        """
        # Create a structured agent output
        agent_output = f"""
{action_type.upper()}: {event_title}
CATEGORY: {category}
EVENT_ID: {event_id}
DURATION: {duration} minutes
RESPONSE: {response_text}
"""
        
        # Parse the output
        parser = AgentOutputParser()
        result = parser.parse(agent_output)
        
        # Verify parsing was successful
        self.assertTrue(result['success'], "Parser should successfully parse valid output")
        
        # Verify actions were extracted
        self.assertIsInstance(result['actions'], list, "Actions should be a list")
        self.assertGreater(len(result['actions']), 0, "Should extract at least one action")
        
        # Verify the action type was correctly identified
        action_types = [action['type'] for action in result['actions']]
        self.assertIn(action_type, action_types, f"Should extract action type '{action_type}'")
        
        # Verify entities were extracted
        self.assertIsInstance(result['entities'], dict, "Entities should be a dictionary")
        
        # Verify response text was extracted
        self.assertIsInstance(result['response_text'], str, "Response text should be a string")
        self.assertGreater(len(result['response_text']), 0, "Response text should not be empty")
        
        # Verify that the response text contains the original response
        # (it might be cleaned up, but should contain key parts)
        self.assertIn(
            response_text.strip()[:20] if len(response_text) >= 20 else response_text.strip(),
            result['response_text'],
            "Response text should contain the original response"
        )
    
    @settings(max_examples=100)
    @given(
        action_type=st.sampled_from(['create', 'update', 'delete', 'reschedule']),
        event_title=st.text(min_size=5, max_size=50, alphabet=st.characters(blacklist_categories=['Cs', 'Cc'])),
        category=st.sampled_from(['Exam', 'Study', 'Gym', 'Social', 'Gaming'])
    )
    def test_parser_extracts_all_action_types(self, action_type, event_title, category):
        """
        Test that parser correctly identifies all valid action types.
        
        Validates: Requirements 12.3
        """
        # Create output with explicit action marker
        agent_output = f"{action_type.upper()}: {event_title} ({category})"
        
        parser = AgentOutputParser()
        result = parser.parse(agent_output)
        
        # Should successfully parse
        self.assertTrue(result['success'])
        
        # Should extract the action
        self.assertGreater(len(result['actions']), 0)
        
        # Should identify the correct action type
        extracted_types = [action['type'] for action in result['actions']]
        self.assertIn(action_type, extracted_types)
    
    @settings(max_examples=100)
    @given(
        event_title=st.text(min_size=5, max_size=50, alphabet=st.characters(blacklist_categories=['Cs', 'Cc'])),
        category=st.sampled_from(['Exam', 'Study', 'Gym', 'Social', 'Gaming']),
        event_id=st.integers(min_value=1, max_value=10000)
    )
    def test_parser_extracts_entities(self, event_title, category, event_id):
        """
        Test that parser correctly extracts event entities.
        
        Validates: Requirements 12.3
        """
        # Create output with entity information
        agent_output = f"""
CREATE: New event
TITLE: {event_title}
CATEGORY: {category}
EVENT_ID: {event_id}
"""
        
        parser = AgentOutputParser()
        result = parser.parse(agent_output)
        
        # Should successfully parse
        self.assertTrue(result['success'])
        
        # Should extract entities
        entities = result['entities']
        self.assertIsInstance(entities, dict)
        
        # Should extract category if present
        if 'category' in entities:
            self.assertEqual(entities['category'], category)
        
        # Should extract event_id if present
        if 'event_id' in entities:
            self.assertEqual(entities['event_id'], event_id)
    
    def test_parser_handles_empty_input(self):
        """
        Test that parser gracefully handles empty input.
        
        Validates: Requirements 12.3
        """
        parser = AgentOutputParser()
        
        # Test empty string
        result = parser.parse("")
        self.assertFalse(result['success'])
        self.assertIsInstance(result['response_text'], str)
        
        # Test None
        result = parser.parse(None)
        self.assertFalse(result['success'])
        self.assertIsInstance(result['response_text'], str)
    
    def test_parser_handles_malformed_input(self):
        """
        Test that parser handles malformed input without crashing.
        
        Validates: Requirements 12.3
        """
        parser = AgentOutputParser()
        
        malformed_inputs = [
            "random text with no structure",
            "::::::::",
            "123456789",
            "\n\n\n",
            "ACTION: but no details",
        ]
        
        for malformed_input in malformed_inputs:
            result = parser.parse(malformed_input)
            # Should not crash and should return a result
            self.assertIsInstance(result, dict)
            self.assertIn('success', result)
            self.assertIn('actions', result)
            self.assertIn('entities', result)
            self.assertIn('response_text', result)
    
    @settings(max_examples=100)
    @given(
        action1=st.sampled_from(['create', 'update', 'delete']),
        action2=st.sampled_from(['create', 'update', 'delete']),
        event1=st.text(min_size=5, max_size=30, alphabet=st.characters(blacklist_categories=['Cs', 'Cc'])),
        event2=st.text(min_size=5, max_size=30, alphabet=st.characters(blacklist_categories=['Cs', 'Cc']))
    )
    def test_parser_handles_multiple_actions(self, action1, action2, event1, event2):
        """
        Test that parser can extract multiple actions from a single output.
        
        Validates: Requirements 12.3
        """
        # Assume actions are different to ensure we get multiple
        assume(action1 != action2 or event1 != event2)
        
        # Create output with multiple actions
        agent_output = f"""
{action1.upper()}: {event1}
{action2.upper()}: {event2}
"""
        
        parser = AgentOutputParser()
        result = parser.parse(agent_output)
        
        # Should successfully parse
        self.assertTrue(result['success'])
        
        # Should extract multiple actions
        self.assertGreaterEqual(len(result['actions']), 2, "Should extract at least 2 actions")
        
        # Should identify both action types
        extracted_types = [action['type'] for action in result['actions']]
        self.assertIn(action1, extracted_types)
        self.assertIn(action2, extracted_types)



class TestActionToEndpointMapping(HypothesisTestCase):
    """
    Property-based tests for action-to-endpoint mapping.
    
    Tests Requirements: 12.4
    """
    
    @settings(max_examples=100)
    @given(
        user_id=st.integers(min_value=1, max_value=10000),
        event_title=st.text(min_size=5, max_size=100, alphabet=st.characters(blacklist_categories=['Cs', 'Cc'])),
        category=st.sampled_from(['Exam', 'Study', 'Gym', 'Social', 'Gaming']),
        start_time=st.datetimes(
            min_value=datetime(2024, 1, 1),
            max_value=datetime(2025, 12, 31)
        ),
        duration_minutes=st.integers(min_value=15, max_value=480)
    )
    def test_action_to_endpoint_mapping(self, user_id, event_title, category, start_time, duration_minutes):
        """
        Feature: phantom-scheduler, Property 28: Action-to-endpoint mapping
        
        For any scheduling action determined by the agent (create, update, delete, reschedule), 
        the agent should invoke the correct Django REST Framework endpoint.
        
        Validates: Requirements 12.4
        """
        # Get the calendar tools
        tools = get_calendar_tools(user_id=user_id)
        
        # Verify we have all expected tools
        self.assertEqual(len(tools), 4, "Should have 4 calendar tools")
        
        # Verify tool names match expected actions
        tool_names = [tool.name for tool in tools]
        expected_tools = ['create_event', 'update_event', 'delete_event', 'query_events']
        
        for expected_tool in expected_tools:
            self.assertIn(expected_tool, tool_names, f"Should have {expected_tool} tool")
        
        # Test create action mapping
        create_tool = next(tool for tool in tools if tool.name == 'create_event')
        self.assertIsInstance(create_tool, CreateEventTool)
        self.assertEqual(create_tool.user_id, user_id, "Tool should have correct user_id")
        
        # Format times for the tool
        end_time = start_time + timedelta(minutes=duration_minutes)
        start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%S')
        end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%S')
        
        # Execute the create action
        result = create_tool._run(
            title=event_title,
            category=category,
            start_time=start_time_str,
            end_time=end_time_str,
            description=""
        )
        
        # Verify the result indicates success
        self.assertIsInstance(result, str, "Tool should return a string result")
        self.assertIn(event_title, result, "Result should mention the event title")
        self.assertIn(category, result, "Result should mention the category")
    
    @settings(max_examples=100)
    @given(
        user_id=st.integers(min_value=1, max_value=10000),
        event_id=st.integers(min_value=1, max_value=10000),
        new_title=st.text(min_size=5, max_size=100, alphabet=st.characters(blacklist_categories=['Cs', 'Cc']))
    )
    def test_update_action_mapping(self, user_id, event_id, new_title):
        """
        Test that update actions map to the correct endpoint.
        
        Validates: Requirements 12.4
        """
        tools = get_calendar_tools(user_id=user_id)
        
        # Get update tool
        update_tool = next(tool for tool in tools if tool.name == 'update_event')
        self.assertIsInstance(update_tool, UpdateEventTool)
        self.assertEqual(update_tool.user_id, user_id)
        
        # Execute update action
        result = update_tool._run(event_id=event_id, title=new_title)
        
        # Verify result
        self.assertIsInstance(result, str)
        self.assertIn(str(event_id), result, "Result should mention the event ID")
    
    @settings(max_examples=100)
    @given(
        user_id=st.integers(min_value=1, max_value=10000),
        event_id=st.integers(min_value=1, max_value=10000)
    )
    def test_delete_action_mapping(self, user_id, event_id):
        """
        Test that delete actions map to the correct endpoint.
        
        Validates: Requirements 12.4
        """
        tools = get_calendar_tools(user_id=user_id)
        
        # Get delete tool
        delete_tool = next(tool for tool in tools if tool.name == 'delete_event')
        self.assertIsInstance(delete_tool, DeleteEventTool)
        self.assertEqual(delete_tool.user_id, user_id)
        
        # Execute delete action
        result = delete_tool._run(event_id=event_id)
        
        # Verify result
        self.assertIsInstance(result, str)
        self.assertIn(str(event_id), result, "Result should mention the event ID")
    
    @settings(max_examples=100)
    @given(
        user_id=st.integers(min_value=1, max_value=10000),
        category=st.sampled_from(['Exam', 'Study', 'Gym', 'Social', 'Gaming', None]),
        start_date=st.dates(min_value=datetime(2024, 1, 1).date(), max_value=datetime(2025, 12, 31).date()),
        end_date=st.dates(min_value=datetime(2024, 1, 1).date(), max_value=datetime(2025, 12, 31).date())
    )
    def test_query_action_mapping(self, user_id, category, start_date, end_date):
        """
        Test that query actions map to the correct endpoint.
        
        Validates: Requirements 12.4
        """
        # Ensure start_date is before end_date
        if start_date > end_date:
            start_date, end_date = end_date, start_date
        
        tools = get_calendar_tools(user_id=user_id)
        
        # Get query tool
        query_tool = next(tool for tool in tools if tool.name == 'query_events')
        self.assertIsInstance(query_tool, QueryEventsTool)
        self.assertEqual(query_tool.user_id, user_id)
        
        # Execute query action
        result = query_tool._run(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            category=category
        )
        
        # Verify result
        self.assertIsInstance(result, str)
    
    @settings(max_examples=100)
    @given(
        user_id=st.integers(min_value=1, max_value=10000)
    )
    def test_all_tools_have_user_context(self, user_id):
        """
        Test that all tools receive and maintain user context.
        
        Validates: Requirements 12.4
        """
        tools = get_calendar_tools(user_id=user_id)
        
        # Verify all tools have the correct user_id
        for tool in tools:
            self.assertEqual(
                tool.user_id, user_id,
                f"Tool {tool.name} should have user_id {user_id}"
            )
    
    def test_tool_descriptions_are_clear(self):
        """
        Test that all tools have clear descriptions for the agent.
        
        Validates: Requirements 12.4
        """
        tools = get_calendar_tools(user_id=1)
        
        for tool in tools:
            # Each tool should have a non-empty description
            self.assertIsInstance(tool.description, str)
            self.assertGreater(len(tool.description), 10, f"Tool {tool.name} should have a meaningful description")
            
            # Description should mention what the tool does
            self.assertTrue(
                any(word in tool.description.lower() for word in ['create', 'update', 'delete', 'query', 'event']),
                f"Tool {tool.name} description should mention its purpose"
            )



class TestResponseCompleteness(HypothesisTestCase):
    """
    Property-based tests for response completeness.
    
    Tests Requirements: 7.2
    """
    
    @settings(max_examples=100)
    @given(
        event_title=st.text(min_size=5, max_size=100, alphabet=st.characters(blacklist_categories=['Cs', 'Cc'])),
        start_time=st.datetimes(
            min_value=datetime(2024, 1, 1),
            max_value=datetime(2025, 12, 31)
        ),
        duration_minutes=st.integers(min_value=15, max_value=480)
    )
    def test_response_completeness_for_confirmations(self, event_title, start_time, duration_minutes):
        """
        Feature: phantom-scheduler, Property 12: Response completeness for confirmations
        
        For any successful scheduling operation, the response message should 
        contain the event title and scheduled time.
        
        Validates: Requirements 7.2
        """
        from .prompts import format_confirmation
        
        # Calculate end time
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Format times for display
        start_str = start_time.strftime('%Y-%m-%d at %H:%M')
        end_str = end_time.strftime('%H:%M')
        
        # Create action summary that includes event details
        action_summary = f"I have scheduled '{event_title}' from {start_str} to {end_str}."
        
        # Format the confirmation
        response = format_confirmation(action_summary)
        
        # Verify response is a string
        self.assertIsInstance(response, str, "Response should be a string")
        
        # Verify response is not empty
        self.assertGreater(len(response), 0, "Response should not be empty")
        
        # Verify response contains the event title
        self.assertIn(
            event_title, response,
            f"Response should contain event title '{event_title}'"
        )
        
        # Verify response contains time information
        # The time should be mentioned in some form
        time_mentioned = (
            start_str in response or
            str(start_time.year) in response or
            str(start_time.hour) in response or
            'scheduled' in response.lower()
        )
        self.assertTrue(
            time_mentioned,
            "Response should contain time information"
        )
    
    @settings(max_examples=100)
    @given(
        event_title=st.text(min_size=5, max_size=50, alphabet=st.characters(blacklist_categories=['Cs', 'Cc'])),
        category=st.sampled_from(['Exam', 'Study', 'Gym', 'Social', 'Gaming']),
        date_str=st.dates(
            min_value=datetime(2024, 1, 1).date(),
            max_value=datetime(2025, 12, 31).date()
        )
    )
    def test_confirmation_includes_category(self, event_title, category, date_str):
        """
        Test that confirmations include category information.
        
        Validates: Requirements 7.2
        """
        from .prompts import format_confirmation
        
        # Create action summary with category
        action_summary = f"I have scheduled '{event_title}' ({category}) on {date_str.strftime('%Y-%m-%d')}."
        
        # Format the confirmation
        response = format_confirmation(action_summary)
        
        # Verify response contains the category
        self.assertIn(
            category, response,
            f"Response should contain category '{category}'"
        )
    
    @settings(max_examples=100)
    @given(
        event_title=st.text(min_size=5, max_size=50, alphabet=st.characters(blacklist_categories=['Cs', 'Cc'])),
        start_time=st.datetimes(
            min_value=datetime(2024, 1, 1),
            max_value=datetime(2025, 12, 31)
        )
    )
    def test_confirmation_maintains_victorian_style(self, event_title, start_time):
        """
        Test that confirmations maintain Victorian Ghost Butler style.
        
        Validates: Requirements 7.1, 7.2
        """
        from .prompts import format_confirmation
        
        # Create action summary
        action_summary = f"Scheduled '{event_title}' at {start_time.strftime('%Y-%m-%d %H:%M')}."
        
        # Format the confirmation
        response = format_confirmation(action_summary)
        
        # Verify response maintains Victorian style
        # Should contain formal language markers
        victorian_markers = [
            'excellent', 'attended', 'request', 'care',
            'schedule', 'updated', 'accordingly', 'assist'
        ]
        
        has_victorian_style = any(marker in response.lower() for marker in victorian_markers)
        self.assertTrue(
            has_victorian_style,
            "Response should maintain Victorian Ghost Butler style"
        )
    
    def test_empty_action_summary_handled(self):
        """
        Test that empty action summaries are handled gracefully.
        
        Validates: Requirements 7.2
        """
        from .prompts import format_confirmation
        
        # Test with empty string
        response = format_confirmation("")
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0, "Should return a non-empty response even with empty input")
    
    @settings(max_examples=100)
    @given(
        event_title=st.text(min_size=5, max_size=50, alphabet=st.characters(blacklist_categories=['Cs', 'Cc'])),
        time_str=st.text(min_size=5, max_size=30, alphabet=st.characters(blacklist_categories=['Cs', 'Cc']))
    )
    def test_response_contains_both_title_and_time(self, event_title, time_str):
        """
        Test that responses contain both event title and time information.
        
        Validates: Requirements 7.2
        """
        from .prompts import format_confirmation
        
        # Create action summary with both title and time
        action_summary = f"Scheduled '{event_title}' at {time_str}."
        
        # Format the confirmation
        response = format_confirmation(action_summary)
        
        # Both should be present in the response
        self.assertIn(event_title, response, "Response should contain event title")
        self.assertIn(time_str, response, "Response should contain time information")



class TestMultiChangeResponseCompleteness(HypothesisTestCase):
    """
    Property-based tests for multi-change response completeness.
    
    Tests Requirements: 7.4
    """
    
    @settings(max_examples=100)
    @given(
        num_changes=st.integers(min_value=2, max_value=10),
        event_titles=st.lists(
            st.text(min_size=5, max_size=50, alphabet=st.characters(blacklist_categories=['Cs', 'Cc'])),
            min_size=2,
            max_size=10
        )
    )
    def test_multi_change_response_completeness(self, num_changes, event_titles):
        """
        Feature: phantom-scheduler, Property 13: Multi-change response completeness
        
        For any operation that modifies multiple events, the response should 
        mention all modified events.
        
        Validates: Requirements 7.4
        """
        from .prompts import format_multi_change
        
        # Ensure we have enough event titles
        if len(event_titles) < num_changes:
            event_titles = event_titles * ((num_changes // len(event_titles)) + 1)
        
        # Take only the number of changes we need
        event_titles = event_titles[:num_changes]
        
        # Create change descriptions
        changes = [
            f"Rescheduled '{title}' to a new time slot"
            for title in event_titles
        ]
        
        # Format the multi-change response
        response = format_multi_change(changes)
        
        # Verify response is a string
        self.assertIsInstance(response, str, "Response should be a string")
        
        # Verify response is not empty
        self.assertGreater(len(response), 0, "Response should not be empty")
        
        # Verify all event titles are mentioned in the response
        for title in event_titles:
            self.assertIn(
                title, response,
                f"Response should mention event '{title}'"
            )
        
        # Verify the response indicates multiple changes
        # Should contain list markers or multiple mentions
        bullet_count = response.count('•')
        self.assertGreaterEqual(
            bullet_count, num_changes,
            f"Response should have at least {num_changes} bullet points for {num_changes} changes"
        )
    
    @settings(max_examples=100)
    @given(
        changes=st.lists(
            st.text(min_size=10, max_size=100, alphabet=st.characters(blacklist_categories=['Cs', 'Cc'])),
            min_size=2,
            max_size=10
        )
    )
    def test_all_changes_listed(self, changes):
        """
        Test that all changes are listed in the response.
        
        Validates: Requirements 7.4
        """
        from .prompts import format_multi_change
        
        # Format the multi-change response
        response = format_multi_change(changes)
        
        # Verify each change is mentioned
        for change in changes:
            # The change text should appear in the response
            # (might be slightly modified with formatting)
            self.assertIn(
                change, response,
                f"Response should contain change: {change}"
            )
    
    @settings(max_examples=100)
    @given(
        num_events=st.integers(min_value=2, max_value=8),
        action_type=st.sampled_from(['created', 'updated', 'deleted', 'rescheduled'])
    )
    def test_multi_change_with_action_types(self, num_events, action_type):
        """
        Test multi-change responses with different action types.
        
        Validates: Requirements 7.4
        """
        from .prompts import format_multi_change
        
        # Create changes with action types
        changes = [
            f"Event {i+1} was {action_type}"
            for i in range(num_events)
        ]
        
        # Format the response
        response = format_multi_change(changes)
        
        # Verify all events are mentioned
        for i in range(num_events):
            event_ref = f"Event {i+1}"
            self.assertIn(
                event_ref, response,
                f"Response should mention {event_ref}"
            )
        
        # Verify action type is mentioned
        action_mentions = response.lower().count(action_type.lower())
        self.assertGreaterEqual(
            action_mentions, num_events,
            f"Response should mention action '{action_type}' at least {num_events} times"
        )
    
    def test_single_change_handled(self):
        """
        Test that single change is handled (edge case).
        
        Validates: Requirements 7.4
        """
        from .prompts import format_multi_change
        
        # Test with single change
        changes = ["Scheduled 'Meeting' for tomorrow"]
        response = format_multi_change(changes)
        
        # Should still work
        self.assertIsInstance(response, str)
        self.assertIn("Meeting", response)
    
    def test_empty_changes_list_handled(self):
        """
        Test that empty changes list is handled gracefully.
        
        Validates: Requirements 7.4
        """
        from .prompts import format_multi_change
        
        # Test with empty list
        response = format_multi_change([])
        
        # Should return a valid response
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
    
    @settings(max_examples=100)
    @given(
        event_titles=st.lists(
            st.text(min_size=5, max_size=50, alphabet=st.characters(blacklist_categories=['Cs', 'Cc'])),
            min_size=2,
            max_size=5
        ),
        categories=st.lists(
            st.sampled_from(['Exam', 'Study', 'Gym', 'Social', 'Gaming']),
            min_size=2,
            max_size=5
        )
    )
    def test_multi_change_with_categories(self, event_titles, categories):
        """
        Test multi-change responses include category information.
        
        Validates: Requirements 7.4
        """
        from .prompts import format_multi_change
        
        # Ensure lists are same length
        min_len = min(len(event_titles), len(categories))
        event_titles = event_titles[:min_len]
        categories = categories[:min_len]
        
        # Create changes with categories
        changes = [
            f"Scheduled '{title}' ({category})"
            for title, category in zip(event_titles, categories)
        ]
        
        # Format the response
        response = format_multi_change(changes)
        
        # Verify all titles and categories are mentioned
        for title, category in zip(event_titles, categories):
            self.assertIn(title, response, f"Response should mention event '{title}'")
            self.assertIn(category, response, f"Response should mention category '{category}'")
    
    @settings(max_examples=100)
    @given(
        num_changes=st.integers(min_value=2, max_value=10)
    )
    def test_multi_change_maintains_victorian_style(self, num_changes):
        """
        Test that multi-change responses maintain Victorian Ghost Butler style.
        
        Validates: Requirements 7.1, 7.4
        """
        from .prompts import format_multi_change
        
        # Create generic changes
        changes = [f"Change {i+1} completed" for i in range(num_changes)]
        
        # Format the response
        response = format_multi_change(changes)
        
        # Verify Victorian style is maintained
        victorian_markers = [
            'made', 'adjustments', 'schedule', 'follows',
            'modifications', 'completed', 'satisfaction', 'trust'
        ]
        
        has_victorian_style = any(marker in response.lower() for marker in victorian_markers)
        self.assertTrue(
            has_victorian_style,
            "Multi-change response should maintain Victorian Ghost Butler style"
        )
