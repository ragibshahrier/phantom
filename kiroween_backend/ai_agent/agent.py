"""
LangChain agent setup for Phantom scheduler.

This module configures the LangChain agent with Google's Gemini API
for natural language processing of scheduling requests.

Requirements: 12.1, 12.5
"""
from typing import Dict, Any, Optional
import os
from decouple import config
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage
import logging

logger = logging.getLogger(__name__)


class PhantomAgentError(Exception):
    """Base exception for Phantom agent errors."""
    pass


class GeminiAPIError(PhantomAgentError):
    """Exception for Gemini API failures."""
    pass


class PhantomAgent:
    """
    LangChain agent for processing natural language scheduling requests.
    
    Uses Google's Gemini API to understand user intent and extract
    scheduling information from conversational input.
    
    Requirements: 12.1, 12.5
    """
    
    def __init__(self, user_id: int, user_timezone: str = 'UTC'):
        """
        Initialize the Phantom agent.
        
        Args:
            user_id: ID of the user for context
            user_timezone: User's timezone for temporal parsing
            
        Raises:
            GeminiAPIError: If API credentials are missing or invalid
        """
        self.user_id = user_id
        self.user_timezone = user_timezone
        
        # Get Gemini API key from environment
        self.api_key = config('GEMINI_API_KEY', default=None)
        if not self.api_key:
            raise GeminiAPIError("GEMINI_API_KEY not found in environment variables")
        
        # Initialize the Gemini model
        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=self.api_key,
                temperature=0.7,
                max_output_tokens=1024,
                convert_system_message_to_human=True  # Gemini requires this
            )
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API: {str(e)}")
            raise GeminiAPIError(f"Failed to initialize Gemini API: {str(e)}")
        
        # Initialize conversation memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        logger.info(f"PhantomAgent initialized for user {user_id}")
    
    def process_input(self, user_input: str, context: Optional[Dict[str, Any]] = None, conversation_history: Optional[list] = None) -> Dict[str, Any]:
        """
        Process natural language input and return structured response.
        
        Args:
            user_input: Raw text from user
            context: Optional context dictionary with additional information
            conversation_history: Optional list of previous conversation messages
            
        Returns:
            Dictionary with:
                - 'response': Text response for the user
                - 'actions': List of scheduling actions to perform
                - 'intent': Detected intent type
                - 'entities': Extracted entities (events, times, etc.)
                
        Raises:
            GeminiAPIError: If API call fails
            
        Requirements: 12.1, 12.5
        """
        if not user_input or not user_input.strip():
            return {
                'response': "I beg your pardon, but I did not quite catch that. Might you rephrase your request?",
                'actions': [],
                'intent': 'unclear',
                'entities': {}
            }
        
        try:
            logger.info(f"Processing input for user {self.user_id}: {user_input[:50]}...")
            
            # Import the enhanced system prompt
            from .prompts import get_system_prompt
            system_prompt = get_system_prompt()

            # Build conversation context from history
            conversation_context = ""
            if conversation_history:
                conversation_context = "\n\nPrevious conversation:\n"
                for conv in conversation_history[-5:]:  # Last 5 messages for context
                    conversation_context += f"User: {conv['message']}\n"
                    conversation_context += f"Phantom: {conv['response']}\n"
                conversation_context += "\n"
            
            # Add current schedule context if provided
            schedule_context = ""
            if context and 'current_events' in context:
                schedule_context = "\n\nCurrent schedule overview:\n"
                events = context['current_events']
                if events:
                    for event in events[:10]:  # Show next 10 events
                        schedule_context += f"- {event.get('title', 'Untitled')} on {event.get('start_time', 'TBD')} ({event.get('category_name', 'Unknown')})\n"
                else:
                    schedule_context += "- No events currently scheduled\n"
                schedule_context += "\n"
            
            # Add timezone context
            timezone_context = f"\n\nUser timezone: {self.user_timezone}\n"
            
            # Combine system prompt, schedule context, conversation history, and user input
            full_prompt = f"{system_prompt}{timezone_context}{schedule_context}{conversation_context}\nUser request: {user_input}\n\nYour response (be proactive and intelligent - infer what they need, don't just repeat what they said):"
            
            # Call the Gemini API
            response = self.llm.invoke(full_prompt)
            
            # Extract the response text
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Return structured response
            return {
                'response': response_text,
                'actions': [],
                'intent': 'general_query',
                'entities': {}
            }
            
        except Exception as e:
            logger.error(f"Error processing input: {str(e)}")
            
            # Check if it's a rate limit or API error
            if "rate limit" in str(e).lower() or "quota" in str(e).lower():
                raise GeminiAPIError(f"API rate limit exceeded: {str(e)}")
            elif "api" in str(e).lower() or "authentication" in str(e).lower():
                raise GeminiAPIError(f"API error: {str(e)}")
            else:
                raise PhantomAgentError(f"Failed to process input: {str(e)}")
    
    def reset_conversation(self):
        """
        Reset the conversation memory.
        
        Useful for starting a new conversation context.
        """
        self.memory.clear()
        logger.info(f"Conversation memory reset for user {self.user_id}")
    
    def get_conversation_history(self) -> list:
        """
        Get the current conversation history.
        
        Returns:
            List of conversation messages
        """
        return self.memory.chat_memory.messages
