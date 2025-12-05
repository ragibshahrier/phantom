"""
Natural language parsing utilities for temporal expressions and task extraction.

This module provides functionality to parse natural language date/time expressions
and extract scheduling information from user input. It also includes structured
output parsing for LangChain agent responses.

Requirements: 9.1, 9.2, 9.4, 9.5, 1.1, 1.5, 12.3
"""
from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Dict
import re
import pytz
from django.utils import timezone


class TemporalExpressionParser:
    """
    Parser for natural language temporal expressions.
    
    Handles:
    - Relative dates (tomorrow, next Friday, etc.)
    - Multi-day ranges (Wednesday and Thursday evening)
    - Various date formats and colloquial expressions
    - User timezone as default
    
    Requirements: 9.1, 9.2, 9.4, 9.5
    """
    
    # Day name mappings
    WEEKDAYS = {
        'monday': 0, 'mon': 0,
        'tuesday': 1, 'tue': 1, 'tues': 1,
        'wednesday': 2, 'wed': 2,
        'thursday': 3, 'thu': 3, 'thur': 3, 'thurs': 3,
        'friday': 4, 'fri': 4,
        'saturday': 5, 'sat': 5,
        'sunday': 6, 'sun': 6,
    }
    
    # Time of day mappings (hour in 24-hour format)
    TIME_OF_DAY = {
        'morning': 9,
        'afternoon': 14,
        'evening': 18,
        'night': 20,
    }
    
    def __init__(self, user_timezone: str = 'UTC', reference_time: Optional[datetime] = None):
        """
        Initialize the temporal expression parser.
        
        Args:
            user_timezone: User's timezone string (e.g., 'America/New_York')
            reference_time: Reference time for relative expressions (defaults to now)
        """
        self.user_timezone = pytz.timezone(user_timezone)
        self.reference_time = reference_time or timezone.now()
        
        # Convert reference_time to user's timezone
        if timezone.is_naive(self.reference_time):
            # If naive, localize to user's timezone
            self.reference_time = self.user_timezone.localize(self.reference_time)
        else:
            # If already timezone-aware (e.g., from timezone.now() which returns UTC),
            # convert to user's timezone
            self.reference_time = self.reference_time.astimezone(self.user_timezone)
    
    def _extract_duration(self, text: str) -> timedelta:
        """
        Extract duration from text like "for 2 hours", "for 30 minutes", "2 hour session".
        
        Args:
            text: Text to search for duration
            
        Returns:
            timedelta object representing the duration (defaults to 1 hour if not found)
        """
        text_lower = text.lower()
        
        # Pattern: "for X hours/minutes" or "X hour/minute"
        # Examples: "for 2 hours", "for 30 minutes", "2 hour session", "90 minute meeting"
        
        # Try hours first
        hours_match = re.search(r'(?:for\s+)?(\d+(?:\.\d+)?)\s*(?:hour|hr|hours|hrs)', text_lower)
        if hours_match:
            hours = float(hours_match.group(1))
            return timedelta(hours=hours)
        
        # Try minutes
        minutes_match = re.search(r'(?:for\s+)?(\d+)\s*(?:minute|min|minutes|mins)', text_lower)
        if minutes_match:
            minutes = int(minutes_match.group(1))
            return timedelta(minutes=minutes)
        
        # Default to 1 hour if no duration specified
        return timedelta(hours=1)
    
    def parse(self, text: str) -> List[Tuple[datetime, datetime]]:
        """
        Parse temporal expressions from text and return datetime ranges.
        
        Args:
            text: Natural language text containing temporal expressions
            
        Returns:
            List of tuples (start_datetime, end_datetime) for each parsed time range
            
        Requirements: 9.1, 9.2, 9.4, 9.5
        """
        text_lower = text.lower()
        results = []
        
        # Extract duration once for all patterns
        duration = self._extract_duration(text_lower)
        
        # Try to parse various temporal patterns
        # Priority order: specific patterns first, then general patterns
        
        # Pattern: "right now" or "currently"
        if re.search(r'\b(right now|currently|now)\b', text_lower):
            start = self.reference_time
            end = start + duration
            results.append((start, end))
            return results
        
        # Pattern: "today"
        if re.search(r'\btoday\b', text_lower):
            start = self._get_today_at_time(text_lower)
            end = start + duration
            results.append((start, end))
            return results
        
        # Pattern: "tonight"
        if re.search(r'\btonight\b', text_lower):
            start = self._get_today_at_time(text_lower)
            # If no specific time mentioned, default to 8pm
            if start.hour < 18:  # If it parsed to before 6pm, set to evening
                start = start.replace(hour=20, minute=0, second=0, microsecond=0)
            end = start + duration
            results.append((start, end))
            return results
        
        # Pattern: "tomorrow"
        if re.search(r'\btomorrow\b', text_lower):
            start = self._get_tomorrow_at_time(text_lower)
            end = start + duration
            results.append((start, end))
            return results
        
        # Pattern: "next [weekday]"
        next_weekday_match = re.search(r'\bnext\s+(' + '|'.join(self.WEEKDAYS.keys()) + r')\b', text_lower)
        if next_weekday_match:
            weekday_name = next_weekday_match.group(1)
            start = self._get_next_weekday(weekday_name, text_lower)
            end = start + duration
            results.append((start, end))
            return results
        
        # Pattern: "this [weekday]"
        this_weekday_match = re.search(r'\bthis\s+(' + '|'.join(self.WEEKDAYS.keys()) + r')\b', text_lower)
        if this_weekday_match:
            weekday_name = this_weekday_match.group(1)
            start = self._get_this_weekday(weekday_name, text_lower)
            end = start + duration
            results.append((start, end))
            return results
        
        # Pattern: multi-day range like "Wednesday and Thursday evening"
        multi_day_match = re.search(
            r'\b(' + '|'.join(self.WEEKDAYS.keys()) + r')\s+and\s+(' + '|'.join(self.WEEKDAYS.keys()) + r')\b',
            text_lower
        )
        if multi_day_match:
            day1_name = multi_day_match.group(1)
            day2_name = multi_day_match.group(2)
            results = self._parse_multi_day_range(day1_name, day2_name, text_lower)
            return results
        
        # Pattern: single weekday without "next" or "this"
        single_weekday_match = re.search(r'\b(' + '|'.join(self.WEEKDAYS.keys()) + r')\b', text_lower)
        if single_weekday_match:
            weekday_name = single_weekday_match.group(0)
            start = self._get_next_weekday(weekday_name, text_lower)
            end = start + duration
            results.append((start, end))
            return results
        
        # Pattern: "in X days/weeks"
        in_days_match = re.search(r'\bin\s+(\d+)\s+(day|days)\b', text_lower)
        if in_days_match:
            num_days = int(in_days_match.group(1))
            start = self._get_future_date(num_days, text_lower)
            end = start + duration
            results.append((start, end))
            return results
        
        in_weeks_match = re.search(r'\bin\s+(\d+)\s+(week|weeks)\b', text_lower)
        if in_weeks_match:
            num_weeks = int(in_weeks_match.group(1))
            start = self._get_future_date(num_weeks * 7, text_lower)
            end = start + duration
            results.append((start, end))
            return results
        
        # Pattern: "next week"
        if re.search(r'\bnext\s+week\b', text_lower):
            start = self._get_future_date(7, text_lower)
            end = start + duration
            results.append((start, end))
            return results
        
        # Pattern: Standalone time like "at 10pm", "at 5:30pm" (fallback - assumes today)
        # This catches cases where user specifies only a time without a day
        time_only_match = re.search(r'\bat\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)', text_lower)
        if time_only_match:
            # Assume today if only time is specified
            start = self._get_today_at_time(text_lower)
            # If the time has already passed today, schedule for tomorrow
            if start < self.reference_time:
                start = self._get_tomorrow_at_time(text_lower)
            end = start + duration
            results.append((start, end))
            return results
        
        # If no pattern matched, return empty list
        return results
    
    def _get_time_of_day(self, text: str) -> Tuple[int, int]:
        """
        Extract time of day from text (morning, afternoon, evening, night, or specific times like 2pm, 9am).
        
        Args:
            text: Text to search for time of day
            
        Returns:
            Tuple of (hour, minute) in 24-hour format (defaults to (14, 0) if not found)
        """
        # First, try to extract specific time like "2pm", "9am", "14:00", "11pm"
        # Pattern: "at 9pm", "2:30pm", "14:00", "11 pm" - must have am/pm or be after "at"
        # This prevents matching duration numbers like "30 minute"
        time_match = re.search(r'(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm|AM|PM)', text)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            meridiem = time_match.group(3).lower() if time_match.group(3) else None
            
            # Convert to 24-hour format
            if meridiem == 'pm' and hour != 12:
                hour += 12
            elif meridiem == 'am' and hour == 12:
                hour = 0
            
            return (hour, minute)
        
        # Fall back to time of day words
        for time_word, hour in self.TIME_OF_DAY.items():
            if time_word in text:
                return (hour, 0)
        return (14, 0)  # Default to 2 PM
    
    def _get_today_at_time(self, text: str) -> datetime:
        """Get today's date at the specified time of day."""
        hour, minute = self._get_time_of_day(text)
        # Create a naive datetime first, then localize it to user's timezone
        today_naive = self.reference_time.replace(hour=hour, minute=minute, second=0, microsecond=0, tzinfo=None)
        today = self.user_timezone.localize(today_naive)
        return today
    
    def _get_tomorrow_at_time(self, text: str) -> datetime:
        """Get tomorrow's date at the specified time of day."""
        hour, minute = self._get_time_of_day(text)
        # Create a naive datetime first, then localize it to user's timezone
        tomorrow_naive = (self.reference_time + timedelta(days=1)).replace(hour=hour, minute=minute, second=0, microsecond=0, tzinfo=None)
        tomorrow = self.user_timezone.localize(tomorrow_naive)
        return tomorrow
    
    def _get_next_weekday(self, weekday_name: str, text: str) -> datetime:
        """
        Get the next occurrence of a specific weekday.
        
        Args:
            weekday_name: Name of the weekday (e.g., 'monday', 'friday')
            text: Full text to extract time of day
            
        Returns:
            Datetime of the next occurrence of that weekday
        """
        target_weekday = self.WEEKDAYS[weekday_name]
        current_weekday = self.reference_time.weekday()
        
        # Calculate days until target weekday
        days_ahead = target_weekday - current_weekday
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        
        hour, minute = self._get_time_of_day(text)
        # Create a naive datetime first, then localize it to user's timezone
        next_date_naive = (self.reference_time + timedelta(days=days_ahead)).replace(hour=hour, minute=minute, second=0, microsecond=0, tzinfo=None)
        next_date = self.user_timezone.localize(next_date_naive)
        
        return next_date
    
    def _get_this_weekday(self, weekday_name: str, text: str) -> datetime:
        """
        Get this week's occurrence of a specific weekday.
        
        If the day has already passed this week, returns next week's occurrence.
        
        Args:
            weekday_name: Name of the weekday
            text: Full text to extract time of day
            
        Returns:
            Datetime of this week's occurrence of that weekday
        """
        target_weekday = self.WEEKDAYS[weekday_name]
        current_weekday = self.reference_time.weekday()
        
        # Calculate days until target weekday
        days_ahead = target_weekday - current_weekday
        if days_ahead < 0:  # Target day already happened this week
            days_ahead += 7
        
        hour, minute = self._get_time_of_day(text)
        # Create a naive datetime first, then localize it to user's timezone
        target_date_naive = (self.reference_time + timedelta(days=days_ahead)).replace(hour=hour, minute=minute, second=0, microsecond=0, tzinfo=None)
        target_date = self.user_timezone.localize(target_date_naive)
        
        return target_date
    
    def _get_future_date(self, days_ahead: int, text: str) -> datetime:
        """
        Get a date in the future by number of days.
        
        Args:
            days_ahead: Number of days in the future
            text: Full text to extract time of day
            
        Returns:
            Datetime for the future date
        """
        hour, minute = self._get_time_of_day(text)
        # Create a naive datetime first, then localize it to user's timezone
        future_date_naive = (self.reference_time + timedelta(days=days_ahead)).replace(hour=hour, minute=minute, second=0, microsecond=0, tzinfo=None)
        future_date = self.user_timezone.localize(future_date_naive)
        return future_date
    
    def _parse_multi_day_range(self, day1_name: str, day2_name: str, text: str) -> List[Tuple[datetime, datetime]]:
        """
        Parse multi-day ranges like "Wednesday and Thursday evening".
        
        Args:
            day1_name: First day name
            day2_name: Second day name
            text: Full text to extract time of day
            
        Returns:
            List of datetime tuples for each day in the range
            
        Requirements: 9.2
        """
        results = []
        duration = self._extract_duration(text)
        
        # If both days are the same, just return one event
        if day1_name == day2_name:
            day_date = self._get_next_weekday(day1_name, text)
            end_date = day_date + duration
            results.append((day_date, end_date))
            return results
        
        # Get the next occurrence of the first day
        day1_date = self._get_next_weekday(day1_name, text)
        day2_date = self._get_next_weekday(day2_name, text)
        
        # Ensure day2 is after day1
        if day2_date <= day1_date:
            day2_date += timedelta(days=7)
        
        # Create events for each day in the range
        current_date = day1_date
        while current_date <= day2_date:
            end_date = current_date + duration
            results.append((current_date, end_date))
            # Move to next day, keeping the same time
            current_date_naive = (current_date + timedelta(days=1)).replace(tzinfo=None)
            current_date = self.user_timezone.localize(current_date_naive)
        
        return results


class TaskCategoryExtractor:
    """
    Extract task titles and categories from natural language input.
    
    Implements keyword-based category detection and task title extraction.
    
    Requirements: 1.1, 1.5
    """
    
    # Category keywords mapping
    CATEGORY_KEYWORDS = {
        'Exam': ['exam', 'test', 'quiz', 'midterm', 'final'],
        'Study': ['study', 'review', 'homework', 'assignment', 'reading'],
        'Gym': ['gym', 'workout', 'exercise', 'fitness', 'training', 'run', 'jog'],
        'Social': ['meet', 'meeting', 'hangout', 'party', 'dinner', 'lunch', 'coffee', 'friend', 'sleep', 'rest', 'nap', 'bedtime', 'wake', 'call'],
        'Gaming': ['game', 'gaming', 'play', 'stream', 'esports'],
    }
    
    def __init__(self):
        """Initialize the task category extractor."""
        pass
    
    def extract_category(self, text: str) -> Optional[str]:
        """
        Detect category from text using keyword matching.
        
        Args:
            text: Natural language text
            
        Returns:
            Category name if detected, None otherwise
            
        Requirements: 1.1
        """
        text_lower = text.lower()
        
        # Check each category's keywords
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                    return category
        
        return None
    
    def extract_task_title(self, text: str) -> str:
        """
        Extract task title from natural language input.
        
        Attempts to identify the main task description by removing
        temporal expressions and common filler words.
        
        Args:
            text: Natural language text
            
        Returns:
            Extracted task title
            
        Requirements: 1.1
        """
        # Remove common temporal expressions
        cleaned = text
        
        temporal_patterns = [
            r'\b(tomorrow|today|tonight|now|currently|right now)\b',
            r'\b(next|this|last)\s+(week|month|year|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            r'\b(in|at|on)\s+\d+\s*(am|pm|hour|hours|minute|minutes|day|days|week|weeks)?\b',
            r'\b(morning|afternoon|evening|night)\b',
            r'\b\d{1,2}:\d{2}\s*(am|pm)?\b',
        ]
        
        for pattern in temporal_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Remove common action verbs at the start
        cleaned = re.sub(r'^\s*(schedule|add|create|make|set up|book)\s+', '', cleaned, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # If nothing left, return original text
        if not cleaned:
            return text.strip()
        
        return cleaned
    
    def is_ambiguous(self, text: str) -> bool:
        """
        Check if the input is ambiguous and requires clarification.
        
        Args:
            text: Natural language text
            
        Returns:
            True if input is ambiguous, False otherwise
            
        Requirements: 1.5
        """
        # Check if text is too short
        if len(text.strip()) < 3:
            return True
        
        # Check if no category can be detected and no clear task description
        category = self.extract_category(text)
        task_title = self.extract_task_title(text)
        
        # If we have neither category nor meaningful task title, it's ambiguous
        if category is None and len(task_title.strip()) < 3:
            return True
        
        return False



class AgentOutputParser:
    """
    Parser for extracting structured scheduling actions from Gemini API responses.
    
    Extracts:
    - Action type (create, update, delete, reschedule)
    - Event entities (title, category, time, duration)
    - Temporal information
    - Response text for user feedback
    
    Requirements: 12.3
    """
    
    # Valid action types
    VALID_ACTIONS = ['create', 'update', 'delete', 'reschedule', 'query', 'optimize']
    
    def __init__(self):
        """Initialize the agent output parser."""
        pass
    
    def parse(self, agent_output: str) -> Dict[str, any]:
        """
        Parse agent output and extract structured scheduling information.
        
        Args:
            agent_output: Raw output from the LangChain agent
            
        Returns:
            Dictionary containing:
                - 'actions': List of action dictionaries
                - 'response_text': Text response for the user
                - 'entities': Extracted entities
                - 'success': Whether parsing was successful
                
        Requirements: 12.3
        """
        result = {
            'actions': [],
            'response_text': '',
            'entities': {},
            'success': False
        }
        
        if not agent_output or not isinstance(agent_output, str):
            result['response_text'] = "I beg your pardon, but I received no response to parse."
            return result
        
        try:
            # Extract action type from the output
            actions = self._extract_actions(agent_output)
            result['actions'] = actions
            
            # Extract entities (events, times, categories)
            entities = self._extract_entities(agent_output)
            result['entities'] = entities
            
            # Extract response text (the part meant for the user)
            response_text = self._extract_response_text(agent_output)
            result['response_text'] = response_text
            
            result['success'] = True
            
        except Exception as e:
            result['response_text'] = f"I encountered a difficulty parsing the response: {str(e)}"
            result['success'] = False
        
        return result
    
    def _extract_actions(self, text: str) -> List[Dict[str, any]]:
        """
        Extract scheduling actions from text.
        
        Args:
            text: Text to parse
            
        Returns:
            List of action dictionaries with 'type' and 'params'
        """
        actions = []
        text_lower = text.lower()
        
        # Look for action keywords
        for action_type in self.VALID_ACTIONS:
            # Pattern: ACTION: <details>
            pattern = rf'{action_type}:\s*(.+?)(?:\n|$)'
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            
            for match in matches:
                action_details = match.group(1).strip()
                actions.append({
                    'type': action_type,
                    'params': {'details': action_details}
                })
        
        # If no explicit actions found, try to infer from keywords
        if not actions:
            if any(word in text_lower for word in ['schedule', 'add', 'create', 'book']):
                actions.append({'type': 'create', 'params': {}})
            elif any(word in text_lower for word in ['update', 'change', 'modify', 'edit']):
                actions.append({'type': 'update', 'params': {}})
            elif any(word in text_lower for word in ['delete', 'remove', 'cancel']):
                actions.append({'type': 'delete', 'params': {}})
            elif any(word in text_lower for word in ['reschedule', 'move', 'shift']):
                actions.append({'type': 'reschedule', 'params': {}})
            elif any(word in text_lower for word in ['show', 'list', 'query', 'what', 'when']):
                actions.append({'type': 'query', 'params': {}})
            elif any(word in text_lower for word in ['optimize', 'reorganize', 'rearrange']):
                actions.append({'type': 'optimize', 'params': {}})
        
        return actions
    
    def _extract_entities(self, text: str) -> Dict[str, any]:
        """
        Extract event entities from text.
        
        Args:
            text: Text to parse
            
        Returns:
            Dictionary of extracted entities
        """
        entities = {}
        
        # Extract event title (look for quoted text or after "event:" or "title:")
        title_match = re.search(r'(?:event|title):\s*["\']?([^"\'\n]+)["\']?', text, re.IGNORECASE)
        if title_match:
            entities['title'] = title_match.group(1).strip()
        
        # Extract category
        category_match = re.search(r'category:\s*(\w+)', text, re.IGNORECASE)
        if category_match:
            entities['category'] = category_match.group(1).strip()
        
        # Extract event ID (for updates/deletes)
        id_match = re.search(r'(?:event_)?id:\s*(\d+)', text, re.IGNORECASE)
        if id_match:
            entities['event_id'] = int(id_match.group(1))
        
        # Extract duration
        duration_match = re.search(r'duration:\s*(\d+)\s*(hour|hours|minute|minutes|min)', text, re.IGNORECASE)
        if duration_match:
            value = int(duration_match.group(1))
            unit = duration_match.group(2).lower()
            if 'hour' in unit:
                entities['duration_minutes'] = value * 60
            else:
                entities['duration_minutes'] = value
        
        # Extract date/time information (basic patterns)
        # This will be enhanced by TemporalExpressionParser
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'tomorrow|today|tonight',
            r'next \w+',
            r'this \w+',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                entities['temporal_expression'] = match.group(0)
                break
        
        return entities
    
    def _extract_response_text(self, text: str) -> str:
        """
        Extract the response text meant for the user.
        
        This attempts to separate the structured data from the natural language response.
        
        Args:
            text: Full agent output
            
        Returns:
            Response text for the user
        """
        # If the text contains structured markers, extract only the response part
        # Otherwise, return the full text
        
        # Look for a "RESPONSE:" marker
        response_match = re.search(r'RESPONSE:\s*(.+)', text, re.IGNORECASE | re.DOTALL)
        if response_match:
            return response_match.group(1).strip()
        
        # Look for text after action markers
        # Remove lines that look like structured data
        lines = text.split('\n')
        response_lines = []
        
        for line in lines:
            # Skip lines that look like structured data
            if re.match(r'^\w+:\s*.+$', line) and ':' in line:
                # This looks like "key: value" format
                continue
            response_lines.append(line)
        
        response = '\n'.join(response_lines).strip()
        
        # If we filtered everything out, return the original text
        if not response:
            return text
        
        return response
    
    def validate_action(self, action: Dict[str, any]) -> bool:
        """
        Validate that an action dictionary is well-formed.
        
        Args:
            action: Action dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(action, dict):
            return False
        
        if 'type' not in action:
            return False
        
        if action['type'] not in self.VALID_ACTIONS:
            return False
        
        if 'params' not in action:
            return False
        
        return True
