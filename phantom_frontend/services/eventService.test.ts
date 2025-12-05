import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import eventService from './eventService';
import apiClient from '../config/api';
import { Event, EventCreateData, EventUpdateData, EventQueryParams } from '../types';

// Mock the API client
vi.mock('../config/api');

describe('eventService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('getEvents', () => {
    it('should call GET /events/ without params', async () => {
      const mockEvents: Event[] = [
        {
          id: 1,
          title: 'Test Event',
          description: 'Test Description',
          category: 1,
          category_name: 'Study',
          category_color: '#FF0000',
          priority_level: 4,
          start_time: '2024-01-01T10:00:00Z',
          end_time: '2024-01-01T11:00:00Z',
          is_flexible: false,
          is_completed: false,
          created_at: '2024-01-01T09:00:00Z',
          updated_at: '2024-01-01T09:00:00Z',
        },
      ];

      vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockEvents });

      const result = await eventService.getEvents();

      expect(apiClient.get).toHaveBeenCalledWith('/events/', { params: undefined });
      expect(result).toEqual(mockEvents);
    });

    it('should call GET /events/ with query params', async () => {
      const params: EventQueryParams = {
        start_date: '2024-01-01',
        end_date: '2024-01-31',
        category: 1,
      };

      const mockEvents: Event[] = [];

      vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockEvents });

      const result = await eventService.getEvents(params);

      expect(apiClient.get).toHaveBeenCalledWith('/events/', { params });
      expect(result).toEqual(mockEvents);
    });

    it('should throw error when fetching events fails', async () => {
      const errorResponse = {
        response: {
          data: {
            message: 'Failed to fetch events',
          },
        },
      };

      vi.mocked(apiClient.get).mockRejectedValueOnce(errorResponse);

      await expect(eventService.getEvents()).rejects.toThrow('Failed to fetch events');
    });
  });

  describe('getEvent', () => {
    it('should call GET /events/{id}/', async () => {
      const mockEvent: Event = {
        id: 1,
        title: 'Test Event',
        description: 'Test Description',
        category: 1,
        category_name: 'Study',
        category_color: '#FF0000',
        priority_level: 4,
        start_time: '2024-01-01T10:00:00Z',
        end_time: '2024-01-01T11:00:00Z',
        is_flexible: false,
        is_completed: false,
        created_at: '2024-01-01T09:00:00Z',
        updated_at: '2024-01-01T09:00:00Z',
      };

      vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockEvent });

      const result = await eventService.getEvent(1);

      expect(apiClient.get).toHaveBeenCalledWith('/events/1/');
      expect(result).toEqual(mockEvent);
    });

    it('should throw error when event not found', async () => {
      const errorResponse = {
        response: {
          data: {
            detail: 'Event not found',
          },
        },
      };

      vi.mocked(apiClient.get).mockRejectedValueOnce(errorResponse);

      await expect(eventService.getEvent(999)).rejects.toThrow('Event not found');
    });
  });

  describe('createEvent', () => {
    it('should call POST /events/ with event data', async () => {
      const eventData: EventCreateData = {
        title: 'New Event',
        description: 'New Description',
        category: 1,
        start_time: '2024-01-01T10:00:00Z',
        end_time: '2024-01-01T11:00:00Z',
        is_flexible: false,
      };

      const mockCreatedEvent: Event = {
        id: 1,
        ...eventData,
        category_name: 'Study',
        category_color: '#FF0000',
        priority_level: 4,
        is_completed: false,
        created_at: '2024-01-01T09:00:00Z',
        updated_at: '2024-01-01T09:00:00Z',
      };

      vi.mocked(apiClient.post).mockResolvedValueOnce({ data: mockCreatedEvent });

      const result = await eventService.createEvent(eventData);

      // The service ensures ISO format, which may add milliseconds
      expect(apiClient.post).toHaveBeenCalledWith('/events/', expect.objectContaining({
        title: eventData.title,
        description: eventData.description,
        category: eventData.category,
        is_flexible: eventData.is_flexible,
      }));
      expect(result).toEqual(mockCreatedEvent);
    });

    it('should handle Date objects and convert to ISO format', async () => {
      const startDate = new Date('2024-01-01T10:00:00Z');
      const endDate = new Date('2024-01-01T11:00:00Z');

      const eventData: EventCreateData = {
        title: 'New Event',
        category: 1,
        start_time: startDate as any, // Type assertion for test
        end_time: endDate as any,
      };

      const mockCreatedEvent: Event = {
        id: 1,
        title: 'New Event',
        description: '',
        category: 1,
        category_name: 'Study',
        category_color: '#FF0000',
        priority_level: 4,
        start_time: startDate.toISOString(),
        end_time: endDate.toISOString(),
        is_flexible: false,
        is_completed: false,
        created_at: '2024-01-01T09:00:00Z',
        updated_at: '2024-01-01T09:00:00Z',
      };

      vi.mocked(apiClient.post).mockResolvedValueOnce({ data: mockCreatedEvent });

      await eventService.createEvent(eventData);

      expect(apiClient.post).toHaveBeenCalledWith('/events/', {
        ...eventData,
        start_time: startDate.toISOString(),
        end_time: endDate.toISOString(),
      });
    });

    it('should throw error when event creation fails', async () => {
      const eventData: EventCreateData = {
        title: 'New Event',
        category: 1,
        start_time: '2024-01-01T10:00:00Z',
        end_time: '2024-01-01T11:00:00Z',
      };

      const errorResponse = {
        response: {
          data: {
            message: 'Invalid event data',
          },
        },
      };

      vi.mocked(apiClient.post).mockRejectedValueOnce(errorResponse);

      await expect(eventService.createEvent(eventData)).rejects.toThrow('Invalid event data');
    });
  });

  describe('updateEvent', () => {
    it('should call PUT /events/{id}/ with updated data', async () => {
      const updateData: EventUpdateData = {
        title: 'Updated Event',
        description: 'Updated Description',
      };

      const mockUpdatedEvent: Event = {
        id: 1,
        title: 'Updated Event',
        description: 'Updated Description',
        category: 1,
        category_name: 'Study',
        category_color: '#FF0000',
        priority_level: 4,
        start_time: '2024-01-01T10:00:00Z',
        end_time: '2024-01-01T11:00:00Z',
        is_flexible: false,
        is_completed: false,
        created_at: '2024-01-01T09:00:00Z',
        updated_at: '2024-01-01T09:30:00Z',
      };

      vi.mocked(apiClient.put).mockResolvedValueOnce({ data: mockUpdatedEvent });

      const result = await eventService.updateEvent(1, updateData);

      expect(apiClient.put).toHaveBeenCalledWith('/events/1/', updateData);
      expect(result).toEqual(mockUpdatedEvent);
    });

    it('should handle Date objects in update data', async () => {
      const newStartDate = new Date('2024-01-02T10:00:00Z');

      const updateData: EventUpdateData = {
        start_time: newStartDate as any,
      };

      const mockUpdatedEvent: Event = {
        id: 1,
        title: 'Event',
        description: '',
        category: 1,
        category_name: 'Study',
        category_color: '#FF0000',
        priority_level: 4,
        start_time: newStartDate.toISOString(),
        end_time: '2024-01-01T11:00:00Z',
        is_flexible: false,
        is_completed: false,
        created_at: '2024-01-01T09:00:00Z',
        updated_at: '2024-01-01T09:30:00Z',
      };

      vi.mocked(apiClient.put).mockResolvedValueOnce({ data: mockUpdatedEvent });

      await eventService.updateEvent(1, updateData);

      expect(apiClient.put).toHaveBeenCalledWith('/events/1/', {
        start_time: newStartDate.toISOString(),
      });
    });

    it('should throw error when event update fails', async () => {
      const updateData: EventUpdateData = {
        title: 'Updated Event',
      };

      const errorResponse = {
        response: {
          data: {
            detail: 'Event not found',
          },
        },
      };

      vi.mocked(apiClient.put).mockRejectedValueOnce(errorResponse);

      await expect(eventService.updateEvent(999, updateData)).rejects.toThrow('Event not found');
    });
  });

  describe('deleteEvent', () => {
    it('should call DELETE /events/{id}/', async () => {
      vi.mocked(apiClient.delete).mockResolvedValueOnce({ data: {} });

      await eventService.deleteEvent(1);

      expect(apiClient.delete).toHaveBeenCalledWith('/events/1/');
    });

    it('should throw error when event deletion fails', async () => {
      const errorResponse = {
        response: {
          data: {
            detail: 'Event not found',
          },
        },
      };

      vi.mocked(apiClient.delete).mockRejectedValueOnce(errorResponse);

      await expect(eventService.deleteEvent(999)).rejects.toThrow('Event not found');
    });
  });
});
