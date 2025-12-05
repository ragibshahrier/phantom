#!/usr/bin/env python
"""
Comprehensive test runner for intelligent scheduling tests.

This script runs all tests related to intelligent scheduling and provides
a detailed report of the results.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phantom.settings')
django.setup()

from django.test.utils import get_runner
from django.conf import settings
from django.core.management import call_command


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def run_tests():
    """Run all intelligent scheduling tests."""
    print_header("PHANTOM AI INTELLIGENT SCHEDULING TEST SUITE")
    
    print("This test suite verifies that the Phantom AI agent can:")
    print("  ✓ Understand implicit user needs")
    print("  ✓ Create events automatically")
    print("  ✓ Update/reshuffle events based on priorities")
    print("  ✓ Delete low-priority events when necessary")
    print("  ✓ Maintain schedule integrity")
    print("  ✓ Use intelligent defaults")
    print("  ✓ Handle conflicts proactively")
    print()
    
    # Get the test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=False, keepdb=False)
    
    # Test modules to run
    test_modules = [
        'ai_agent.test_intelligent_scheduling',
        'ai_agent.test_chat_endpoint_integration',
    ]
    
    print_header("RUNNING TESTS")
    
    total_failures = 0
    
    for module in test_modules:
        print(f"\n{'─' * 80}")
        print(f"Running: {module}")
        print('─' * 80)
        
        failures = test_runner.run_tests([module])
        total_failures += failures
    
    # Print summary
    print_header("TEST SUMMARY")
    
    if total_failures == 0:
        print("✅ ALL TESTS PASSED!")
        print()
        print("The Phantom AI agent is working correctly:")
        print("  • Implicit understanding: ✓")
        print("  • Automatic event creation: ✓")
        print("  • Priority-based scheduling: ✓")
        print("  • Conflict resolution: ✓")
        print("  • Context awareness: ✓")
        print("  • Intelligent defaults: ✓")
        print()
        print("The agent is ready for production use! 🎉")
        return 0
    else:
        print(f"❌ {total_failures} TEST(S) FAILED")
        print()
        print("Please review the failures above and fix the issues.")
        print("Common issues:")
        print("  • Missing dependencies (check requirements.txt)")
        print("  • Database not migrated (run: python manage.py migrate)")
        print("  • Categories not populated (run: python manage.py populate_categories)")
        print("  • Gemini API key not configured (check .env file)")
        return 1


def main():
    """Main entry point."""
    try:
        # Check if database is ready
        print("Checking database...")
        call_command('check', '--database', 'default')
        print("✓ Database is ready\n")
        
        # Run migrations if needed
        print("Ensuring migrations are up to date...")
        call_command('migrate', '--no-input')
        print("✓ Migrations complete\n")
        
        # Run tests
        exit_code = run_tests()
        
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"\n❌ Error running tests: {str(e)}")
        print("\nPlease ensure:")
        print("  1. Virtual environment is activated")
        print("  2. All dependencies are installed (pip install -r requirements.txt)")
        print("  3. Database is configured correctly")
        print("  4. .env file contains required settings")
        sys.exit(1)


if __name__ == '__main__':
    main()
