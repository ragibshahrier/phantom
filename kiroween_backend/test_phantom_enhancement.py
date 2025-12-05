"""
Test script to verify Phantom AI enhancements.

This script tests the enhanced prompts and intelligent scheduling capabilities.
Run with: python manage.py shell < test_phantom_enhancement.py
"""

from ai_agent.prompts import get_system_prompt

# Test 1: Verify enhanced system prompt is loaded
print("=" * 80)
print("TEST 1: Enhanced System Prompt")
print("=" * 80)

system_prompt = get_system_prompt()

# Check for key enhancements
enhancements_to_check = [
    "supernatural intuition",
    "INTELLIGENT SCHEDULING",
    "AUTOMATIC INTERPRETATION",
    "PROACTIVE BEHAVIOR",
    "Default times",
    "Default durations",
    "I'm too tired to study",
    "math exam on Friday"
]

print("\nChecking for key enhancements in system prompt:")
for enhancement in enhancements_to_check:
    if enhancement in system_prompt:
        print(f"✓ Found: {enhancement}")
    else:
        print(f"✗ Missing: {enhancement}")

# Test 2: Verify prompt structure
print("\n" + "=" * 80)
print("TEST 2: Prompt Structure")
print("=" * 80)

sections = [
    "CHARACTER TRAITS",
    "SCHEDULING RULES AND PRIORITY HIERARCHY",
    "INTELLIGENT SCHEDULING - AUTOMATIC INTERPRETATION",
    "CONFLICT RESOLUTION RULES",
    "PROACTIVE BEHAVIOR",
    "YOUR RESPONSIBILITIES",
    "RESPONSE STYLE",
    "EXAMPLES OF INTELLIGENT INTERPRETATION"
]

print("\nChecking for required sections:")
for section in sections:
    if section in system_prompt:
        print(f"✓ Found section: {section}")
    else:
        print(f"✗ Missing section: {section}")

# Test 3: Verify priority hierarchy
print("\n" + "=" * 80)
print("TEST 3: Priority Hierarchy")
print("=" * 80)

priorities = [
    "Exam (Priority 5)",
    "Study (Priority 4)",
    "Gym (Priority 3)",
    "Social (Priority 2)",
    "Gaming (Priority 1)"
]

print("\nChecking priority hierarchy:")
for priority in priorities:
    if priority in system_prompt:
        print(f"✓ Found: {priority}")
    else:
        print(f"✗ Missing: {priority}")

# Test 4: Verify example scenarios
print("\n" + "=" * 80)
print("TEST 4: Example Scenarios")
print("=" * 80)

scenarios = [
    "I have a math exam on Friday chapter 5",
    "I'm too tired to study right now",
    "Need to work out",
    "Meeting Sarah tomorrow"
]

print("\nChecking for example scenarios:")
for scenario in scenarios:
    if scenario in system_prompt:
        print(f"✓ Found scenario: {scenario}")
    else:
        print(f"✗ Missing scenario: {scenario}")

# Test 5: Verify default values
print("\n" + "=" * 80)
print("TEST 5: Default Values")
print("=" * 80)

defaults = [
    "Morning (9 AM)",
    "Afternoon (2 PM)",
    "Evening (6 PM)",
    "Exam (2-3h)",
    "Study (2h)",
    "Gym (1h)"
]

print("\nChecking for default values:")
for default in defaults:
    if default in system_prompt:
        print(f"✓ Found default: {default}")
    else:
        print(f"✗ Missing default: {default}")

print("\n" + "=" * 80)
print("TESTS COMPLETE")
print("=" * 80)
print("\nIf all checks passed, the Phantom AI enhancement is properly configured!")
print("You can now test with actual user inputs through the chat API.")
