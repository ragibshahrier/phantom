import { useState, useCallback } from 'react';
import eventService from '../services/eventService';
import {
  Event,
  EventCreateData,
  EventUpdateData,
  EventQueryParams,
  UseEventsReturn,
} from '../types';

/**
 * useEvents Hook
 * 
 * Custom hook for managing event state and operations.
 * Provides functions for fetching, creating, updating, and deleting events
 * with automatic state management and error handling.
 * 
 * @returns UseEventsReturn object with events, loading state, error state, and CRUD functions
 */
export const useEvents = (): UseEventsReturn => {
  // State management
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedDate, setSelectedDate] = useState<Date | null>(() => new Date());

  /**
   * Fetch events from the backend with optional query parameters
   * Updates local state with fetched events
   * 
   * @param params - Optional query parameters for filtering events
   */
  const fetchEvents = useCallback(async (params?: EventQueryParams): Promise<void> => {
    setLoading(true);
    setError(null);
    
    try {
      const fetchedEvents = await eventService.getEvents(params);
      setEvents(fetchedEvents);
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to fetch events. Please try again.';
      setError(errorMessage);
      console.error('Error fetching events:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Create a new event
   * Updates local state with the newly created event on success
   * 
   * @param data - Event creation data
   * @returns Created event object or null if creation fails
   */
  const createEvent = useCallback(async (data: EventCreateData): Promise<Event | null> => {
    setLoading(true);
    setError(null);
    
    try {
      const newEvent = await eventService.createEvent(data);
      // Add new event to local state
      setEvents(prev => [...prev, newEvent]);
      return newEvent;
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to create event. Please try again.';
      setError(errorMessage);
      console.error('Error creating event:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Update an existing event
   * Updates local state with the modified event on success
   * 
   * @param id - The event ID to update
   * @param data - Partial event data to update
   * @returns Updated event object or null if update fails
   */
  const updateEvent = useCallback(async (
    id: number,
    data: EventUpdateData
  ): Promise<Event | null> => {
    setLoading(true);
    setError(null);
    
    try {
      const updatedEvent = await eventService.updateEvent(id, data);
      // Update event in local state
      setEvents(prev =>
        prev.map(event => (event.id === id ? updatedEvent : event))
      );
      return updatedEvent;
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to update event. Please try again.';
      setError(errorMessage);
      console.error('Error updating event:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Delete an event
   * Removes the event from local state on success
   * 
   * @param id - The event ID to delete
   * @returns true if deletion succeeds, false otherwise
   */
  const deleteEvent = useCallback(async (id: number): Promise<boolean> => {
    setLoading(true);
    setError(null);
    
    try {
      await eventService.deleteEvent(id);
      // Remove event from local state
      setEvents(prev => prev.filter(event => event.id !== id));
      return true;
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to delete event. Please try again.';
      setError(errorMessage);
      console.error('Error deleting event:', err);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Refresh events by re-fetching from the backend
   * Respects the current selectedDate filter if set
   * This is useful for syncing state after external changes (e.g., chat-created events)
   */
  const refreshEvents = useCallback(async (): Promise<void> => {
    // Refresh with current date filter (if any)
    await fetchEvents();
  }, [fetchEvents]);

  /**
   * Custom setSelectedDate that also triggers a refetch
   * This ensures events are filtered by the new date
   */
  const handleSetSelectedDate = useCallback((date: Date | null) => {
    setSelectedDate(date);
  }, []);

  return {
    events,
    loading,
    error,
    selectedDate,
    setSelectedDate: handleSetSelectedDate,
    fetchEvents,
    createEvent,
    updateEvent,
    deleteEvent,
    refreshEvents,
  };
};

export default useEvents;
