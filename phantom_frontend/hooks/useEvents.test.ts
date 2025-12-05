import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useEvents } from './useEvents';
import eventService from '../services/eventService';
import type { Event, EventCreateData, EventUpdateData } from '../types';

// Mock the event service
vi.mock('../services/eventService');

describe('useEvents Hook', () => {
  const mockEvent: Event = {
    id: 1,
    title: 'Test Event',
    description: 'Test Description',
    category: 1,
    category_name: 'Study',
    category_color: '#FF0000',
    priority_level: 4,
    start_time: '2025-12-04T10:00:00Z',
    end_time: '2025-12-04T11:00:00Z',
    is_flexible: false,
    is_completed: false,
    created_at: '2025-12-03T00:00:00Z',
    updated_at: '2025-12-03T00:00:00Z',
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should initialize with empty events array', () => {
    const { result } = renderHook(() => useEvents());
    
    expect(result.current.events).toEqual([]);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('should fetch events successfully', async () => {
    const mockEvents = [mockEvent];
    vi.mocked(eventService.getEvents).mockResolvedValue(mockEvents);

    const { result } = renderHook(() => useEvents());

    await act(async () => {
      await result.current.fetchEvents();
    });

    expect(eventService.getEvents).toHaveBeenCalledWith(undefined);
    expect(result.current.events).toEqual(mockEvents);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('should fetch events with query parameters', async () => {
    const mockEvents = [mockEvent];
    const queryParams = { start_date: '2025-12-04', end_date: '2025-12-05' };
    vi.mocked(eventService.getEvents).mockResolvedValue(mockEvents);

    const { result } = renderHook(() => useEvents());

    await act(async () => {
      await result.current.fetchEvents(queryParams);
    });

    expect(eventService.getEvents).toHaveBeenCalledWith(queryParams);
    expect(result.current.events).toEqual(mockEvents);
  });

  it('should handle fetch errors', async () => {
    const errorMessage = 'Failed to fetch events';
    vi.mocked(eventService.getEvents).mockRejectedValue(new Error(errorMessage));

    const { result } = renderHook(() => useEvents());

    await act(async () => {
      await result.current.fetchEvents();
    });

    expect(result.current.events).toEqual([]);
    expect(result.current.error).toBe(errorMessage);
    expect(result.current.loading).toBe(false);
  });

  it('should create event successfully', async () => {
    const createData: EventCreateData = {
      title: 'New Event',
      description: 'New Description',
      category: 1,
      start_time: '2025-12-04T10:00:00Z',
      end_time: '2025-12-04T11:00:00Z',
    };
    vi.mocked(eventService.createEvent).mockResolvedValue(mockEvent);

    const { result } = renderHook(() => useEvents());

    let createdEvent: Event | null = null;
    await act(async () => {
      createdEvent = await result.current.createEvent(createData);
    });

    expect(eventService.createEvent).toHaveBeenCalledWith(createData);
    expect(createdEvent).toEqual(mockEvent);
    expect(result.current.events).toContain(mockEvent);
    expect(result.current.error).toBeNull();
  });

  it('should handle create errors', async () => {
    const createData: EventCreateData = {
      title: 'New Event',
      category: 1,
      start_time: '2025-12-04T10:00:00Z',
      end_time: '2025-12-04T11:00:00Z',
    };
    const errorMessage = 'Failed to create event';
    vi.mocked(eventService.createEvent).mockRejectedValue(new Error(errorMessage));

    const { result } = renderHook(() => useEvents());

    let createdEvent: Event | null = null;
    await act(async () => {
      createdEvent = await result.current.createEvent(createData);
    });

    expect(createdEvent).toBeNull();
    expect(result.current.error).toBe(errorMessage);
  });

  it('should update event successfully', async () => {
    const updatedEvent = { ...mockEvent, title: 'Updated Event' };
    vi.mocked(eventService.getEvents).mockResolvedValue([mockEvent]);
    vi.mocked(eventService.updateEvent).mockResolvedValue(updatedEvent);

    const { result } = renderHook(() => useEvents());

    // First fetch events
    await act(async () => {
      await result.current.fetchEvents();
    });

    // Then update
    const updateData: EventUpdateData = { title: 'Updated Event' };
    let updated: Event | null = null;
    await act(async () => {
      updated = await result.current.updateEvent(1, updateData);
    });

    expect(eventService.updateEvent).toHaveBeenCalledWith(1, updateData);
    expect(updated).toEqual(updatedEvent);
    expect(result.current.events[0].title).toBe('Updated Event');
  });

  it('should handle update errors', async () => {
    const updateData: EventUpdateData = { title: 'Updated Event' };
    const errorMessage = 'Failed to update event';
    vi.mocked(eventService.updateEvent).mockRejectedValue(new Error(errorMessage));

    const { result } = renderHook(() => useEvents());

    let updated: Event | null = null;
    await act(async () => {
      updated = await result.current.updateEvent(1, updateData);
    });

    expect(updated).toBeNull();
    expect(result.current.error).toBe(errorMessage);
  });

  it('should delete event successfully', async () => {
    vi.mocked(eventService.getEvents).mockResolvedValue([mockEvent]);
    vi.mocked(eventService.deleteEvent).mockResolvedValue(undefined);

    const { result } = renderHook(() => useEvents());

    // First fetch events
    await act(async () => {
      await result.current.fetchEvents();
    });

    expect(result.current.events).toHaveLength(1);

    // Then delete
    let success = false;
    await act(async () => {
      success = await result.current.deleteEvent(1);
    });

    expect(eventService.deleteEvent).toHaveBeenCalledWith(1);
    expect(success).toBe(true);
    expect(result.current.events).toHaveLength(0);
  });

  it('should handle delete errors', async () => {
    const errorMessage = 'Failed to delete event';
    vi.mocked(eventService.deleteEvent).mockRejectedValue(new Error(errorMessage));

    const { result } = renderHook(() => useEvents());

    let success = false;
    await act(async () => {
      success = await result.current.deleteEvent(1);
    });

    expect(success).toBe(false);
    expect(result.current.error).toBe(errorMessage);
  });

  it('should refresh events', async () => {
    const mockEvents = [mockEvent];
    vi.mocked(eventService.getEvents).mockResolvedValue(mockEvents);

    const { result } = renderHook(() => useEvents());

    await act(async () => {
      await result.current.refreshEvents();
    });

    expect(eventService.getEvents).toHaveBeenCalled();
    expect(result.current.events).toEqual(mockEvents);
  });

  it('should set loading state during operations', async () => {
    vi.mocked(eventService.getEvents).mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve([mockEvent]), 100))
    );

    const { result } = renderHook(() => useEvents());

    act(() => {
      result.current.fetchEvents();
    });

    // Should be loading immediately
    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
  });

  it('should initialize with null selectedDate', () => {
    const { result } = renderHook(() => useEvents());
    
    expect(result.current.selectedDate).toBeNull();
  });

  it('should update selectedDate when setSelectedDate is called', () => {
    const { result } = renderHook(() => useEvents());
    const testDate = new Date('2025-12-04');

    act(() => {
      result.current.setSelectedDate(testDate);
    });

    expect(result.current.selectedDate).toEqual(testDate);
  });

  it('should filter events by selectedDate when fetching', async () => {
    const mockEvents = [mockEvent];
    const testDate = new Date('2025-12-04');
    vi.mocked(eventService.getEvents).mockResolvedValue(mockEvents);

    const { result } = renderHook(() => useEvents());

    // Set selected date
    act(() => {
      result.current.setSelectedDate(testDate);
    });

    // Fetch events
    await act(async () => {
      await result.current.fetchEvents();
    });

    // Verify that getEvents was called with date range parameters
    const callArgs = vi.mocked(eventService.getEvents).mock.calls[0][0];
    expect(callArgs).toBeDefined();
    expect(callArgs?.start_date).toBeDefined();
    expect(callArgs?.end_date).toBeDefined();
    
    // Verify the dates are for the correct day (accounting for timezone)
    const startDate = new Date(callArgs!.start_date);
    const endDate = new Date(callArgs!.end_date);
    expect(startDate.getHours()).toBe(0);
    expect(startDate.getMinutes()).toBe(0);
    expect(endDate.getHours()).toBe(23);
    expect(endDate.getMinutes()).toBe(59);
    
    expect(result.current.events).toEqual(mockEvents);
  });

  it('should merge selectedDate with other query params', async () => {
    const mockEvents = [mockEvent];
    const testDate = new Date('2025-12-04');
    const additionalParams = { category: 1 };
    vi.mocked(eventService.getEvents).mockResolvedValue(mockEvents);

    const { result } = renderHook(() => useEvents());

    // Set selected date
    act(() => {
      result.current.setSelectedDate(testDate);
    });

    // Fetch events with additional params
    await act(async () => {
      await result.current.fetchEvents(additionalParams);
    });

    // Verify that getEvents was called with both date range and additional params
    const callArgs = vi.mocked(eventService.getEvents).mock.calls[0][0];
    expect(callArgs).toBeDefined();
    expect(callArgs?.category).toBe(1);
    expect(callArgs?.start_date).toBeDefined();
    expect(callArgs?.end_date).toBeDefined();
  });

  it('should not filter by date when selectedDate is null', async () => {
    const mockEvents = [mockEvent];
    vi.mocked(eventService.getEvents).mockResolvedValue(mockEvents);

    const { result } = renderHook(() => useEvents());

    // Fetch events without setting selectedDate
    await act(async () => {
      await result.current.fetchEvents();
    });

    // Verify that getEvents was called without date parameters
    expect(eventService.getEvents).toHaveBeenCalledWith(undefined);
  });

  it('should respect selectedDate when refreshing events', async () => {
    const mockEvents = [mockEvent];
    const testDate = new Date('2025-12-04');
    vi.mocked(eventService.getEvents).mockResolvedValue(mockEvents);

    const { result } = renderHook(() => useEvents());

    // Set selected date
    act(() => {
      result.current.setSelectedDate(testDate);
    });

    // Refresh events
    await act(async () => {
      await result.current.refreshEvents();
    });

    // Verify that getEvents was called with date range parameters
    const callArgs = vi.mocked(eventService.getEvents).mock.calls[0][0];
    expect(callArgs).toBeDefined();
    expect(callArgs?.start_date).toBeDefined();
    expect(callArgs?.end_date).toBeDefined();
  });

  it('should clear date filter when selectedDate is set to null', async () => {
    const mockEvents = [mockEvent];
    const testDate = new Date('2025-12-04');
    vi.mocked(eventService.getEvents).mockResolvedValue(mockEvents);

    const { result } = renderHook(() => useEvents());

    // Set selected date
    act(() => {
      result.current.setSelectedDate(testDate);
    });

    // Clear selected date
    act(() => {
      result.current.setSelectedDate(null);
    });

    // Fetch events
    await act(async () => {
      await result.current.fetchEvents();
    });

    // Verify that getEvents was called without date parameters
    expect(eventService.getEvents).toHaveBeenCalledWith(undefined);
  });
});
