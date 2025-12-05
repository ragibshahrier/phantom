#!/usr/bin/env python
"""
Quick test script to verify the Phantom agent works with the Gemini API.
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phantom.settings')
django.setup()

from ai_agent.agent import PhantomAgent, GeminiAPIError

def test_agent():
    """Test the Phantom agent with a simple query."""
    try:
        print("Initializing Phantom agent...")
        agent = PhantomAgent(user_id=1, user_timezone='UTC')
        print("✓ Agent initialized successfully!")
        
        print("\nTesting agent with a simple query...")
        test_message = "Hello Phantom, how are you today?"
        result = agent.process_input(test_message)
        
        print(f"\n{'='*60}")
        print(f"User: {test_message}")
        print(f"{'='*60}")
        print(f"Phantom: {result['response']}")
        print(f"{'='*60}")
        print(f"\nIntent: {result['intent']}")
        print(f"Actions: {result['actions']}")
        print("\n✓ Agent test completed successfully!")
        
    except GeminiAPIError as e:
        print(f"\n✗ Gemini API Error: {e}")
        print("\nPlease check:")
        print("1. Your GEMINI_API_KEY is set correctly in .env")
        print("2. The API key is valid and not expired")
        print("3. You have internet connectivity")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    test_agent()
