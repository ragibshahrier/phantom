import apiClient from '../config/api';
import {
  Event,
  EventCreateData,
  EventUpdateData,
  EventQueryParams,
  EventService,
} from '../types';

/**
 * Event Service
 * Handles all event-related API calls including fetching, creating,
 * updating, and deleting calendar events.
 */

/**
 * Get all events with optional query parameters
 * GET /api/events/
 * 
 * @param params - Optional query parameters for filtering events
 * @returns Array of events ordered by start time
 * @throws Error if fetching events fails
 */
const getEvents = async (params?: EventQueryParams): Promise<Event[]> => {
  try {
    const response = await apiClient.get<Event[]>('/events/', { params });
    return response.data;
  } catch (error: any) {
    // Extract error message from response
    const errorMessage = error.response?.data?.message || 
                        error.response?.data?.error ||
                        error.response?.data?.detail ||
                        'Failed to fetch events. Please try again.';
    throw new Error(errorMessage);
  }
};

/**
 * Get a single event by ID
 * GET /api/events/{id}/
 * 
 * @param id - The event ID
 * @returns Event object
 * @throws Error if fetching event fails
 */
const getEvent = async (id: number): Promise<Event> => {
  try {
    const response = await apiClient.get<Event>(`/events/${id}/`);
    return response.data;
  } catch (error: any) {
    // Extract error message from response
    const errorMessage = error.response?.data?.message || 
                        error.response?.data?.error ||
                        error.response?.data?.detail ||
                        'Failed to fetch event. Please try again.';
    throw new Error(errorMessage);
  }
};

/**
 * Create a new event
 * POST /api/events/
 * 
 * @param data - Event creation data
 * @returns Created event object
 * @throws Error if event creation fails
 */
const createEvent = async (data: EventCreateData): Promise<Event> => {
  try {
    // Ensure dates are in ISO 8601 format
    const eventData = {
      ...data,
      start_time: ensureISOFormat(data.start_time),
      end_time: ensureISOFormat(data.end_time),
    };
    
    const response = await apiClient.post<Event>('/events/', eventData);
    return response.data;
  } catch (error: any) {
    // Extract error message from response
    const errorMessage = error.response?.data?.message || 
                        error.response?.data?.error ||
                        error.response?.data?.detail ||
                        'Failed to create event. Please try again.';
    throw new Error(errorMessage);
  }
};

/**
 * Update an existing event
 * PUT /api/events/{id}/
 * 
 * @param id - The event ID to update
 * @param data - Partial event data to update
 * @returns Updated event object
 * @throws Error if event update fails
 */
const updateEvent = async (id: number, data: EventUpdateData): Promise<Event> => {
  try {
    // Ensure dates are in ISO 8601 format if provided
    const eventData = {
      ...data,
      ...(data.start_time && { start_time: ensureISOFormat(data.start_time) }),
      ...(data.end_time && { end_time: ensureISOFormat(data.end_time) }),
    };
    
    const response = await apiClient.put<Event>(`/events/${id}/`, eventData);
    return response.data;
  } catch (error: any) {
    // Extract error message from response
    const errorMessage = error.response?.data?.message || 
                        error.response?.data?.error ||
                        error.response?.data?.detail ||
                        'Failed to update event. Please try again.';
    throw new Error(errorMessage);
  }
};

/**
 * Delete an event
 * DELETE /api/events/{id}/
 * 
 * @param id - The event ID to delete
 * @throws Error if event deletion fails
 */
const deleteEvent = async (id: number): Promise<void> => {
  try {
    await apiClient.delete(`/events/${id}/`);
  } catch (error: any) {
    // Extract error message from response
    const errorMessage = error.response?.data?.message || 
                        error.response?.data?.error ||
                        error.response?.data?.detail ||
                        'Failed to delete event. Please try again.';
    throw new Error(errorMessage);
  }
};

/**
 * Helper function to ensure date is in ISO 8601 format
 * Handles both Date objects and ISO string inputs
 * 
 * @param date - Date as string or Date object
 * @returns ISO 8601 formatted string
 */
const ensureISOFormat = (date: string | Date): string => {
  if (date instanceof Date) {
    return date.toISOString();
  }
  
  // If it's already a string, check if it's a valid ISO format
  // If not, try to parse and convert
  try {
    const parsedDate = new Date(date);
    if (isNaN(parsedDate.getTime())) {
      throw new Error('Invalid date');
    }
    return parsedDate.toISOString();
  } catch {
    // If parsing fails, return as-is and let backend handle validation
    return date;
  }
};

/**
 * Export event service object implementing EventService interface
 */
const eventService: EventService = {
  getEvents,
  getEvent,
  createEvent,
  updateEvent,
  deleteEvent,
};

export default eventService;
