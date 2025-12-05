#!/usr/bin/env python
"""
Test script to verify conversation history is being maintained.
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phantom.settings')
django.setup()

from ai_agent.agent import PhantomAgent

def test_conversation_history():
    """Test that the agent maintains conversation context."""
    try:
        print("Testing conversation history...")
        agent = PhantomAgent(user_id=1, user_timezone='UTC')
        
        # Simulate a conversation history
        conversation_history = [
            {
                'message': 'My name is John',
                'response': 'A pleasure to make your acquaintance, John.',
                'intent': 'greeting',
                'timestamp': '2024-01-01T10:00:00Z'
            },
            {
                'message': 'I like pizza',
                'response': 'I shall make note of your culinary preferences, John.',
                'intent': 'general',
                'timestamp': '2024-01-01T10:01:00Z'
            }
        ]
        
        # Test 1: Ask about name (should remember from history)
        print("\n" + "="*60)
        print("Test 1: Asking about name (should remember 'John')")
        print("="*60)
        result = agent.process_input(
            "What is my name?",
            conversation_history=conversation_history
        )
        print(f"User: What is my name?")
        print(f"Phantom: {result['response']}")
        
        # Test 2: Ask about preference (should remember pizza)
        print("\n" + "="*60)
        print("Test 2: Asking about food preference (should remember 'pizza')")
        print("="*60)
        result = agent.process_input(
            "What food do I like?",
            conversation_history=conversation_history
        )
        print(f"User: What food do I like?")
        print(f"Phantom: {result['response']}")
        
        # Test 3: Without history (should not remember)
        print("\n" + "="*60)
        print("Test 3: Same question without history (should not remember)")
        print("="*60)
        result = agent.process_input("What is my name?")
        print(f"User: What is my name?")
        print(f"Phantom: {result['response']}")
        
        print("\n✓ Conversation history test completed!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    test_conversation_history()
