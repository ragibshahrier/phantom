#!/usr/bin/env python
"""
Test the parser fixes for "tonight 9pm" type expressions.
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phantom.settings')
django.setup()

from ai_agent.parsers import TemporalExpressionParser
from django.utils import timezone

def test_parser():
    """Test various time expressions."""
    parser = TemporalExpressionParser(
        user_timezone='UTC',
        reference_time=timezone.now()
    )
    
    test_cases = [
        "schedule an event tonight 9pm",
        "schedule a study session tomorrow at 2pm",
        "add gym workout next Monday morning",
        "create exam review on Friday at 3pm",
        "meet for coffee today at 4:30pm",
        "tonight at 8pm",
        "tomorrow 10am",
    ]
    
    print("\n" + "="*60)
    print("TESTING TEMPORAL PARSER")
    print("="*60)
    
    for test_input in test_cases:
        print(f"\nInput: {test_input}")
        results = parser.parse(test_input)
        
        if results:
            print(f"✓ Found {len(results)} time slot(s):")
            for start, end in results:
                print(f"  Start: {start}")
                print(f"  End:   {end}")
        else:
            print("✗ No temporal information found")
    
    print("\n" + "="*60)

if __name__ == '__main__':
    test_parser()
