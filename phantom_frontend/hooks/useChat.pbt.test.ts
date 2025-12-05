import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import fc from 'fast-check';
import { useChat } from './useChat';
import { useEvents } from './useEvents';
import chatService from '../services/chatService';
import eventService from '../services/eventService';
import type { ChatResponse, Event } from '../types';

// Mock the services
vi.mock('../services/chatService');
vi.mock('../services/eventService');

describe('useChat Property-Based Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  /**
   * Feature: phantom-frontend-integration, Property 10: Chat-created events update timeline
   * For any chat response that includes created events, the frontend should immediately 
   * update the timeline to display the new events without requiring a manual refresh.
   * Validates: Requirements 4.3, 9.1
   */
  it('Property 10: Chat-created events update timeline', async () => {
    await fc.assert(
      fc.asyncProperty(
        // Generate random chat messages
        fc.string({ minLength: 1, maxLength: 200 }),
        // Generate random event data with unique IDs
        fc.array(
          fc.record({
            title: fc.string({ minLength: 1, maxLength: 100 }),
            description: fc.string({ maxLength: 500 }),
            category: fc.integer({ min: 1, max: 5 }),
            category_name: fc.constantFrom('Exam', 'Study', 'Gym', 'Social', 'Gaming'),
            category_color: fc.constantFrom('#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF'),
            priority_level: fc.integer({ min: 1, max: 5 }),
            start_time: fc.date({ min: new Date('2025-01-01'), max: new Date('2026-12-31') }).map(d => d.toISOString()),
            end_time: fc.date({ min: new Date('2025-01-01'), max: new Date('2026-12-31') }).map(d => d.toISOString()),
            is_flexible: fc.boolean(),
            is_completed: fc.boolean(),
            created_at: fc.date().map(d => d.toISOString()),
            updated_at: fc.date().map(d => d.toISOString()),
          }),
          { minLength: 0, maxLength: 5 }
        ),
        async (message, generatedEventsWithoutIds) => {
          // Clear mocks for each iteration
          vi.clearAllMocks();

          // Assign unique IDs and ensure end_time is after start_time for each event
          const validEvents: Event[] = generatedEventsWithoutIds.map((event, index) => ({
            ...event,
            id: 1000 + index, // Unique IDs starting from 1000
            end_time: new Date(new Date(event.start_time).getTime() + 3600000).toISOString(), // Add 1 hour
          }));

          // Mock chat service to return events
          const mockChatResponse: ChatResponse = {
            response: 'I have created your events.',
            events_created: validEvents,
            intent_detected: 'create_event',
          };
          vi.mocked(chatService.sendMessage).mockResolvedValue(mockChatResponse);

          // Mock event service to return all events (including newly created ones)
          const existingEvents: Event[] = [
            {
              id: 99999,
              title: 'Existing Event',
              description: 'Already exists',
              category: 1,
              category_name: 'Study',
              category_color: '#FF0000',
              priority_level: 3,
              start_time: '2025-12-01T10:00:00Z',
              end_time: '2025-12-01T11:00:00Z',
              is_flexible: false,
              is_completed: false,
              created_at: '2025-12-01T00:00:00Z',
              updated_at: '2025-12-01T00:00:00Z',
            },
          ];
          
          // First call returns existing events, second call returns existing + new events
          vi.mocked(eventService.getEvents)
            .mockResolvedValueOnce(existingEvents)
            .mockResolvedValueOnce([...existingEvents, ...validEvents]);

          // Render both hooks
          const { result: chatResult } = renderHook(() => useChat());
          const { result: eventsResult } = renderHook(() => useEvents());

          // Fetch initial events
          await act(async () => {
            await eventsResult.current.fetchEvents();
          });

          const initialEventCount = eventsResult.current.events.length;
          expect(initialEventCount).toBe(existingEvents.length);

          // Send chat message and get created events
          let createdEvents: Event[] = [];
          await act(async () => {
            createdEvents = await chatResult.current.sendMessage(message);
          });

          // Verify chat service was called
          expect(chatService.sendMessage).toHaveBeenCalledWith(message);
          expect(chatService.sendMessage).toHaveBeenCalledTimes(1);

          // Verify sendMessage returns the created events
          expect(createdEvents).toEqual(validEvents);

          // Simulate the SeanceRoom pattern: refresh events after chat creates them
          await act(async () => {
            await eventsResult.current.refreshEvents();
          });

          // Verify event service was called to refresh
          expect(eventService.getEvents).toHaveBeenCalledTimes(2); // Initial fetch + refresh

          // Verify timeline is updated with new events
          const finalEventCount = eventsResult.current.events.length;
          expect(finalEventCount).toBe(initialEventCount + validEvents.length);

          // Verify all created events are now in the timeline
          validEvents.forEach(createdEvent => {
            const foundEvent = eventsResult.current.events.find(e => e.id === createdEvent.id);
            expect(foundEvent).toBeDefined();
            expect(foundEvent?.title).toBe(createdEvent.title);
          });

          // Verify chat history contains the user message and phantom response
          expect(chatResult.current.chatHistory.length).toBeGreaterThanOrEqual(2);
          expect(chatResult.current.chatHistory[0].sender).toBe('USER');
          expect(chatResult.current.chatHistory[0].text).toBe(message);
          expect(chatResult.current.chatHistory[1].sender).toBe('PHANTOM');
          expect(chatResult.current.chatHistory[1].text).toBe(mockChatResponse.response);
        }
      ),
      { numRuns: 100 }
    );
  });
});
