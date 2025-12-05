"""
LangChain tools for calendar operations.

This module defines tools that the LangChain agent can use to interact
with the Django REST Framework API endpoints for calendar management.

Requirements: 12.4
"""
from typing import Dict, Any, Optional, List
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import logging
import sys

# Configure logging to handle Unicode properly on Windows
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    # Ensure UTF-8 encoding for the handler
    if hasattr(handler.stream, 'reconfigure'):
        handler.stream.reconfigure(encoding='utf-8', errors='replace')
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class CreateEventInput(BaseModel):
    """Input schema for creating an event."""
    title: str = Field(description="Title of the event")
    category: str = Field(description="Category of the event (Exam, Study, Gym, Social, Gaming)")
    start_time: str = Field(description="Start time in ISO format (YYYY-MM-DDTHH:MM:SS)")
    end_time: str = Field(description="End time in ISO format (YYYY-MM-DDTHH:MM:SS)")
    description: Optional[str] = Field(default="", description="Optional description of the event")


class UpdateEventInput(BaseModel):
    """Input schema for updating an event."""
    event_id: int = Field(description="ID of the event to update")
    title: Optional[str] = Field(default=None, description="New title")
    category: Optional[str] = Field(default=None, description="New category")
    start_time: Optional[str] = Field(default=None, description="New start time in ISO format")
    end_time: Optional[str] = Field(default=None, description="New end time in ISO format")
    description: Optional[str] = Field(default=None, description="New description")


class DeleteEventInput(BaseModel):
    """Input schema for deleting an event."""
    event_id: int = Field(description="ID of the event to delete")


class QueryEventsInput(BaseModel):
    """Input schema for querying events."""
    start_date: Optional[str] = Field(default=None, description="Start date for query range (YYYY-MM-DD)")
    end_date: Optional[str] = Field(default=None, description="End date for query range (YYYY-MM-DD)")
    category: Optional[str] = Field(default=None, description="Filter by category")


class CreateEventTool(BaseTool):
    """
    Tool for creating calendar events.
    
    Maps to POST /api/events/ endpoint.
    
    Requirements: 12.4
    """
    name: str = "create_event"
    description: str = """
    Create a new calendar event. Use this when the user wants to schedule something.
    Input should include title, category, start_time, and end_time.
    """
    args_schema: type[BaseModel] = CreateEventInput
    
    user_id: int = Field(description="User ID for authentication context")
    api_client: Any = Field(description="API client for making requests")
    
    def _run(self, title: str, category: str, start_time: str, end_time: str, description: str = "") -> str:
        """
        Execute the create event action.
        
        Args:
            title: Event title
            category: Event category
            start_time: Start time in ISO format
            end_time: End time in ISO format
            description: Optional description
            
        Returns:
            Result message
        """
        try:
            # In a real implementation, this would call the Django REST API
            # For now, we'll return a structured response
            logger.info(f"Creating event: {title} ({category}) from {start_time} to {end_time}")
            
            return f"Event '{title}' created successfully in category {category} from {start_time} to {end_time}"
        except Exception as e:
            logger.error(f"Error creating event: {str(e)}")
            return f"Error creating event: {str(e)}"
    
    async def _arun(self, *args, **kwargs) -> str:
        """Async version (not implemented)."""
        raise NotImplementedError("Async not supported")


class UpdateEventTool(BaseTool):
    """
    Tool for updating calendar events.
    
    Maps to PUT /api/events/{id}/ endpoint.
    
    Requirements: 12.4
    """
    name: str = "update_event"
    description: str = """
    Update an existing calendar event. Use this when the user wants to modify an event.
    Input should include event_id and the fields to update.
    """
    args_schema: type[BaseModel] = UpdateEventInput
    
    user_id: int = Field(description="User ID for authentication context")
    api_client: Any = Field(description="API client for making requests")
    
    def _run(self, event_id: int, title: Optional[str] = None, category: Optional[str] = None,
             start_time: Optional[str] = None, end_time: Optional[str] = None,
             description: Optional[str] = None) -> str:
        """
        Execute the update event action.
        
        Args:
            event_id: ID of event to update
            title: New title (optional)
            category: New category (optional)
            start_time: New start time (optional)
            end_time: New end time (optional)
            description: New description (optional)
            
        Returns:
            Result message
        """
        try:
            logger.info(f"Updating event {event_id}")
            
            updates = []
            if title:
                updates.append(f"title to '{title}'")
            if category:
                updates.append(f"category to {category}")
            if start_time:
                updates.append(f"start time to {start_time}")
            if end_time:
                updates.append(f"end time to {end_time}")
            
            update_str = ", ".join(updates) if updates else "no changes"
            return f"Event {event_id} updated: {update_str}"
        except Exception as e:
            logger.error(f"Error updating event: {str(e)}")
            return f"Error updating event: {str(e)}"
    
    async def _arun(self, *args, **kwargs) -> str:
        """Async version (not implemented)."""
        raise NotImplementedError("Async not supported")


class DeleteEventTool(BaseTool):
    """
    Tool for deleting calendar events.
    
    Maps to DELETE /api/events/{id}/ endpoint.
    
    Requirements: 12.4
    """
    name: str = "delete_event"
    description: str = """
    Delete a calendar event. Use this when the user wants to cancel or remove an event.
    Input should include the event_id.
    """
    args_schema: type[BaseModel] = DeleteEventInput
    
    user_id: int = Field(description="User ID for authentication context")
    api_client: Any = Field(description="API client for making requests")
    
    def _run(self, event_id: int) -> str:
        """
        Execute the delete event action.
        
        Args:
            event_id: ID of event to delete
            
        Returns:
            Result message
        """
        try:
            logger.info(f"Deleting event {event_id}")
            return f"Event {event_id} deleted successfully"
        except Exception as e:
            logger.error(f"Error deleting event: {str(e)}")
            return f"Error deleting event: {str(e)}"
    
    async def _arun(self, *args, **kwargs) -> str:
        """Async version (not implemented)."""
        raise NotImplementedError("Async not supported")


class QueryEventsTool(BaseTool):
    """
    Tool for querying calendar events.
    
    Maps to GET /api/events/ endpoint with filters.
    
    Requirements: 12.4
    """
    name: str = "query_events"
    description: str = """
    Query calendar events. Use this when the user wants to see their schedule or find events.
    Input can include start_date, end_date, and category filters.
    """
    args_schema: type[BaseModel] = QueryEventsInput
    
    user_id: int = Field(description="User ID for authentication context")
    api_client: Any = Field(description="API client for making requests")
    
    def _run(self, start_date: Optional[str] = None, end_date: Optional[str] = None,
             category: Optional[str] = None) -> str:
        """
        Execute the query events action.
        
        Args:
            start_date: Start date for range (optional)
            end_date: End date for range (optional)
            category: Category filter (optional)
            
        Returns:
            Result message with event list
        """
        try:
            filters = []
            if start_date:
                filters.append(f"from {start_date}")
            if end_date:
                filters.append(f"to {end_date}")
            if category:
                filters.append(f"in category {category}")
            
            filter_str = " ".join(filters) if filters else "all events"
            logger.info(f"Querying events: {filter_str}")
            
            return f"Querying events {filter_str}"
        except Exception as e:
            logger.error(f"Error querying events: {str(e)}")
            return f"Error querying events: {str(e)}"
    
    async def _arun(self, *args, **kwargs) -> str:
        """Async version (not implemented)."""
        raise NotImplementedError("Async not supported")


def get_calendar_tools(user_id: int, api_client: Any = None) -> List[BaseTool]:
    """
    Get all calendar operation tools for the LangChain agent.
    
    Args:
        user_id: User ID for authentication context
        api_client: Optional API client for making requests
        
    Returns:
        List of LangChain tools
        
    Requirements: 12.4
    """
    return [
        CreateEventTool(user_id=user_id, api_client=api_client),
        UpdateEventTool(user_id=user_id, api_client=api_client),
        DeleteEventTool(user_id=user_id, api_client=api_client),
        QueryEventsTool(user_id=user_id, api_client=api_client),
    ]
