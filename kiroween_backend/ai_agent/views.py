"""
Views for the AI agent chat interface.

This module provides the chat API endpoint that receives natural language input,
processes it through the LangChain agent, and returns formatted responses.

Requirements: 1.1, 7.2, 7.4, 7.5, 12.1, 12.2, 12.3, 12.4
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db import transaction
import logging
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from scheduler.models import ConversationHistory
from .agent import PhantomAgent, GeminiAPIError, PhantomAgentError
from .parsers import TemporalExpressionParser, TaskCategoryExtractor, AgentOutputParser
from .prompts import format_confirmation, format_error, format_clarification

logger = logging.getLogger(__name__)


def _detect_intent(user_input: str) -> str:
    """
    Detect the user's intent from their input.
    
    Args:
        user_input: The user's natural language input
        
    Returns:
        Intent string: 'create', 'delete', 'update', 'query', or 'general'
    """
    user_input_lower = user_input.lower()
    
    # Delete intent keywords
    delete_keywords = [
        'delete', 'remove', 'cancel', 'banish', 'get rid of', 'erase',
        'clear', 'eliminate', 'drop'
    ]
    if any(keyword in user_input_lower for keyword in delete_keywords):
        return 'delete'
    
    # Update/modify intent keywords
    update_keywords = [
        'update', 'change', 'modify', 'edit', 'reschedule', 'move',
        'shift', 'adjust', 'alter', 'revise'
    ]
    if any(keyword in user_input_lower for keyword in update_keywords):
        return 'update'
    
    # Query intent keywords (asking questions)
    query_keywords = [
        'what', 'when', 'where', 'who', 'which', 'how many', 'show me',
        'list', 'tell me', 'do i have', 'am i', 'is there', 'are there',
        'can you show', 'display', 'view', 'see', 'check', 'find'
    ]
    if any(keyword in user_input_lower for keyword in query_keywords):
        return 'query'
    
    # Create intent keywords
    create_keywords = [
        'schedule', 'add', 'create', 'make', 'set up', 'book', 'plan',
        'arrange', 'organize', 'put', 'insert', 'new'
    ]
    if any(keyword in user_input_lower for keyword in create_keywords):
        return 'create'
    
    # If no specific intent detected, treat as general query
    return 'general'


@extend_schema(
    tags=['Chat'],
    summary='Process natural language scheduling request',
    description='Send a natural language message to the Victorian Ghost Butler AI agent. '
                'The agent will parse your request, create/modify calendar events, and respond '
                'in character with confirmation of actions taken.',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'message': {
                    'type': 'string',
                    'description': 'Natural language scheduling request',
                    'example': 'Schedule a study session tomorrow at 2pm for 2 hours'
                }
            },
            'required': ['message']
        }
    },
    responses={
        200: {'description': 'Request processed successfully'},
        400: {'description': 'Empty message or invalid input'},
        503: {'description': 'AI service temporarily unavailable'},
        500: {'description': 'Internal server error'}
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat(request):
    """
    Process natural language input and return agent response.
    
    Receives user input, passes it to the LangChain agent for processing,
    and returns a response with Victorian Ghost Butler formatting.
    
    Request body:
        {
            "message": "Natural language scheduling request"
        }
    
    Response:
        {
            "response": "Victorian Ghost Butler formatted response",
            "actions": [list of actions taken],
            "intent": "detected intent type",
            "success": true/false
        }
    
    Requirements: 1.1, 7.2, 7.4, 7.5, 12.1, 12.2, 12.3, 12.4
    """
    user = request.user
    user_input = request.data.get('message', '').strip()
    
    if not user_input:
        return Response(
            {
                'response': "I beg your pardon, but I did not receive any message to process.",
                'actions': [],
                'intent': 'empty',
                'success': False
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Initialize the agent with user context
        agent = PhantomAgent(
            user_id=user.id,
            user_timezone=user.timezone
        )
        
        # Fetch recent conversation history for context (last 10 messages)
        recent_conversations = ConversationHistory.objects.filter(
            user=user
        ).order_by('-timestamp')[:10]
        
        # Convert to list and reverse to get chronological order
        conversation_history = [
            {
                'message': conv.message,
                'response': conv.response,
                'intent': conv.intent_detected,
                'timestamp': conv.timestamp.isoformat()
            }
            for conv in reversed(recent_conversations)
        ]
        
        # Check if input is ambiguous and needs clarification
        category_extractor = TaskCategoryExtractor()
        if category_extractor.is_ambiguous(user_input):
            clarification_msg = format_clarification(
                "I require more details about what you wish to schedule. "
                "Please provide the task description and when you would like it scheduled."
            )
            
            # Store conversation with transaction support
            try:
                with transaction.atomic():
                    ConversationHistory.objects.create(
                        user=user,
                        message=user_input,
                        response=clarification_msg,
                        intent_detected='ambiguous'
                    )
            except Exception as e:
                logger.error(
                    f"Failed to store conversation history for user {user.id}: {str(e)}",
                    exc_info=True,
                    extra={'user_id': user.id, 'operation': 'store_conversation'}
                )
                # Continue even if logging fails - don't block user interaction
            
            return Response(
                {
                    'response': clarification_msg,
                    'actions': [],
                    'intent': 'ambiguous',
                    'success': False
                },
                status=status.HTTP_200_OK
            )
        
        # Fetch current events for context (next 7 days)
        from scheduler.models import Event
        from datetime import timedelta
        
        current_time = timezone.now()
        week_from_now = current_time + timedelta(days=7)
        
        current_events = Event.objects.filter(
            user=user,
            start_time__gte=current_time,
            start_time__lte=week_from_now
        ).order_by('start_time').values(
            'id', 'title', 'start_time', 'end_time', 'category__name'
        )
        
        # Prepare context with current schedule
        context = {
            'current_events': [
                {
                    'id': event['id'],
                    'title': event['title'],
                    'start_time': event['start_time'].isoformat(),
                    'end_time': event['end_time'].isoformat(),
                    'category_name': event['category__name']
                }
                for event in current_events
            ]
        }
        
        # Process the input through the agent with conversation history and schedule context
        result = agent.process_input(user_input, context=context, conversation_history=conversation_history)
        
        # Detect user intent from the input
        user_intent = _detect_intent(user_input)
        logger.info(f"Detected intent: {user_intent}")
        
        # Parse temporal expressions
        temporal_parser = TemporalExpressionParser(
            user_timezone=user.timezone,
            reference_time=timezone.now()
        )
        temporal_results = temporal_parser.parse(user_input)
        
        # Extract category
        category = category_extractor.extract_category(user_input)
        task_title = category_extractor.extract_task_title(user_input)
        
        # Log extracted information for debugging
        logger.info(f"Extracted - Temporal: {len(temporal_results) if temporal_results else 0}, Category: {category}, Title: {task_title}")
        
        # Initialize created_events and deleted_events lists
        created_events = []
        deleted_events = []
        
        # Handle DELETE intent
        if user_intent == 'delete':
            from scheduler.models import Event
            
            # Extract what to delete from the input
            events_to_delete = []
            
            # Get user's events (recent ones first) - convert to list to avoid queryset slicing issues
            user_events = list(Event.objects.filter(user=user).order_by('-start_time')[:20])
            
            # Try to match by title keywords
            input_lower = user_input.lower()
            
            # Remove common words that shouldn't be used for matching
            stop_words = {'delete', 'remove', 'cancel', 'my', 'the', 'a', 'an', 'test', 'please', 'can', 'you'}
            
            # Extract meaningful keywords from user input
            input_words = [word for word in input_lower.split() if len(word) > 2 and word not in stop_words]
            
            # Score each event based on keyword matches
            event_scores = []
            for event in user_events:
                event_title_lower = event.title.lower()
                score = 0
                
                # Check for exact phrase match (highest priority)
                if any(word in event_title_lower for word in input_words if len(word) > 4):
                    # Count how many significant words match
                    for word in input_words:
                        if word in event_title_lower:
                            score += 2 if len(word) > 4 else 1
                
                if score > 0:
                    event_scores.append((event, score))
            
            # Sort by score and take the best match(es)
            if event_scores:
                event_scores.sort(key=lambda x: x[1], reverse=True)
                # Only take events with the highest score
                max_score = event_scores[0][1]
                events_to_delete = [event for event, score in event_scores if score == max_score]
                # Limit to 3 events max to avoid accidental mass deletion
                events_to_delete = events_to_delete[:3]
            
            # If no matches by title, try to match by category
            if not events_to_delete and category:
                # Filter by category from the list of events
                events_to_delete = [e for e in user_events if e.category.name == category][:3]
            
            # Delete the matched events
            if events_to_delete:
                try:
                    with transaction.atomic():
                        for event in events_to_delete:
                            deleted_events.append({
                                'id': event.id,
                                'title': event.title,
                                'start_time': event.start_time.isoformat()
                            })
                            event.delete()
                            logger.info(f"Deleted event '{event.title}' (ID: {event.id}) for user {user.id}")
                        
                        # Update the agent response
                        event_count = len(deleted_events)
                        event_word = "event" if event_count == 1 else "events"
                        result['response'] = f"{result.get('response', '')} I have successfully deleted {event_count} {event_word} for you."
                except Exception as e:
                    logger.error(f"Failed to delete events for user {user.id}: {str(e)}", exc_info=True)
                    result['response'] = "I encountered an error while attempting to delete the events. Please try again."
            else:
                result['response'] = f"{result.get('response', '')} I could not find any matching events to delete. Please be more specific about which event you'd like to remove."
        
        # Only create events if the user intent is to CREATE and we have all required information
        elif user_intent == 'create' and temporal_results and task_title and category:
            from scheduler.models import Event, Category
            from scheduler.serializers import EventSerializer
            
            try:
                # Get the category object
                category_obj = Category.objects.get(name=category)
                
                # Create events for each parsed time slot
                for start_time, end_time in temporal_results:
                    event = Event.objects.create(
                        user=user,
                        title=task_title,
                        description=f"Created via chat: {user_input}",
                        category=category_obj,
                        start_time=start_time,
                        end_time=end_time,
                        is_flexible=True
                    )
                    
                    # Serialize the event for response
                    serializer = EventSerializer(event)
                    created_events.append(serializer.data)
                    
                    logger.info(f"Created event '{task_title}' for user {user.id}")
                
                # Update the agent response to confirm event creation
                if created_events:
                    event_count = len(created_events)
                    event_word = "event" if event_count == 1 else "events"
                    result['response'] = f"{result.get('response', '')} I have successfully scheduled {event_count} {event_word} for you."
                    
            except Category.DoesNotExist:
                logger.warning(f"Category '{category}' not found for user {user.id}")
            except Exception as e:
                logger.error(f"Failed to create event for user {user.id}: {str(e)}", exc_info=True)
        
        # Enhance result with parsed information
        if temporal_results:
            result['temporal_info'] = {
                'parsed_times': [
                    {
                        'start': start.isoformat(),
                        'end': end.isoformat()
                    }
                    for start, end in temporal_results
                ]
            }
        
        if category:
            result['category'] = category
        
        if task_title:
            result['task_title'] = task_title
        
        # Format response based on intent
        response_text = result.get('response', '')
        intent = user_intent  # Use the detected intent instead of agent's intent
        actions = result.get('actions', [])
        
        # Add helpful message for non-create intents
        if user_intent == 'delete':
            response_text += "\n\nTo delete an event, please use the delete button on the event card in your timeline."
        elif user_intent == 'update':
            response_text += "\n\nTo update an event, please click the edit button on the event card in your timeline."
        elif user_intent == 'query':
            response_text += "\n\nYou can view your events in the Timeline or Calendar view."
        
        # Store conversation in history with transaction support
        try:
            with transaction.atomic():
                ConversationHistory.objects.create(
                    user=user,
                    message=user_input,
                    response=response_text,
                    intent_detected=intent
                )
        except Exception as e:
            logger.error(
                f"Failed to store conversation history for user {user.id}: {str(e)}",
                exc_info=True,
                extra={'user_id': user.id, 'operation': 'store_conversation'}
            )
            # Continue even if logging fails - don't block user interaction
        
        logger.info(f"Chat processed for user {user.id}: intent={intent}, actions={len(actions)}, events_created={len(created_events)}, events_deleted={len(deleted_events)}")
        
        return Response(
            {
                'response': response_text,
                'actions': actions,
                'intent': intent,
                'category': category,
                'task_title': task_title,
                'temporal_info': result.get('temporal_info'),
                'events_created': created_events,
                'events_deleted': deleted_events,
                'success': True
            },
            status=status.HTTP_200_OK
        )
        
    except GeminiAPIError as e:
        logger.error(f"Gemini API error for user {user.id}: {str(e)}")
        
        error_msg = format_error(
            "I regret to inform you that I am experiencing difficulties "
            "communicating with my ethereal faculties at the moment. "
            "Might you try again in a brief moment?"
        )
        
        return Response(
            {
                'response': error_msg,
                'actions': [],
                'intent': 'error',
                'success': False,
                'error': 'API rate limit or connection issue'
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
        
    except PhantomAgentError as e:
        logger.error(f"Agent error for user {user.id}: {str(e)}")
        
        error_msg = format_error(
            "I encountered an unexpected difficulty while processing your request. "
            "Please accept my apologies."
        )
        
        return Response(
            {
                'response': error_msg,
                'actions': [],
                'intent': 'error',
                'success': False,
                'error': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
    except Exception as e:
        logger.error(f"Unexpected error for user {user.id}: {str(e)}", exc_info=True)
        
        error_msg = format_error(
            "A most peculiar error has occurred. I shall need to investigate this matter further."
        )
        
        return Response(
            {
                'response': error_msg,
                'actions': [],
                'intent': 'error',
                'success': False,
                'error': 'Internal server error'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    tags=['Chat'],
    summary='Get conversation history',
    description='Retrieve recent conversation history with the AI agent.',
    parameters=[
        OpenApiParameter(
            name='limit',
            type=OpenApiTypes.INT,
            description='Number of recent conversations to return',
            required=False,
            default=10
        )
    ],
    responses={
        200: {'description': 'Conversation history retrieved'}
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversation_history(request):
    """
    Retrieve conversation history for the authenticated user.
    
    Query parameters:
        - limit: Number of recent conversations to return (default: 10)
    
    Response:
        {
            "conversations": [
                {
                    "message": "user message",
                    "response": "agent response",
                    "intent": "detected intent",
                    "timestamp": "ISO timestamp"
                },
                ...
            ]
        }
    
    Requirements: 10.1
    """
    user = request.user
    limit = int(request.query_params.get('limit', 10))
    
    conversations = ConversationHistory.objects.filter(user=user)[:limit]
    
    conversation_data = [
        {
            'message': conv.message,
            'response': conv.response,
            'intent': conv.intent_detected,
            'timestamp': conv.timestamp.isoformat()
        }
        for conv in conversations
    ]
    
    return Response(
        {
            'conversations': conversation_data,
            'count': len(conversation_data)
        },
        status=status.HTTP_200_OK
    )
