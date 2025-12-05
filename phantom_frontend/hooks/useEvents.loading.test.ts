import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useEvents } from './useEvents';
import eventService from '../services/eventService';
import type { Event, EventCreateData, EventUpdateData } from '../types';
import fc from 'fast-check';

// Mock the event service
vi.mock('../services/eventService');

describe('Property-Based Tests - Loading Indicators', () => {
  const createMockEvent = (overrides?: Partial<Event>): Event => ({
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
    ...overrides,
  });

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  /**
   * Feature: phantom-frontend-integration, Property 19: Loading indicators appear during requests
   * 
   * For any API request in progress, the frontend should display a loading indicator to inform the user.
   * 
   * This property tests that the loading state is set to true during async operations and false after completion.
   * 
   * Validates: Requirements 8.1
   */
  it('Property 19: Loading indicators appear during requests', async () => {
    await fc.assert(
      fc.asyncProperty(
        // Generate random event data for various operations
        fc.record({
          title: fc.string({ minLength: 1, maxLength: 200 }),
          description: fc.string({ maxLength: 1000 }),
          category: fc.integer({ min: 1, max: 5 }),
          start_time: fc.date({ min: new Date('2025-01-01'), max: new Date('2026-12-31') }),
          end_time: fc.date({ min: new Date('2025-01-01'), max: new Date('2026-12-31') }),
        }).filter(data => data.end_time > data.start_time),
        // Generate random event ID for update/delete operations
        fc.integer({ min: 1, max: 1000 }),
        async (eventData, eventId) => {
          // Convert dates to ISO strings for API
          const createData: EventCreateData = {
            title: eventData.title,
            description: eventData.description,
            category: eventData.category,
            start_time: eventData.start_time.toISOString(),
            end_time: eventData.end_time.toISOString(),
          };

          const mockEvent = createMockEvent({
            id: eventId,
            title: eventData.title,
            description: eventData.description,
            category: eventData.category,
            start_time: eventData.start_time.toISOString(),
            end_time: eventData.end_time.toISOString(),
          });

          // Test 1: fetchEvents shows loading indicator
          {
            vi.mocked(eventService.getEvents).mockImplementation(
              () => new Promise(resolve => setTimeout(() => resolve([mockEvent]), 10))
            );

            const { result } = renderHook(() => useEvents());

            // Initially not loading
            expect(result.current.loading).toBe(false);

            // Start fetch operation
            act(() => {
              result.current.fetchEvents();
            });

            // Should be loading immediately after starting the operation
            expect(result.current.loading).toBe(true);

            // Wait for operation to complete
            await waitFor(() => {
              expect(result.current.loading).toBe(false);
            }, { timeout: 100 });

            // Verify loading is false after completion
            expect(result.current.loading).toBe(false);
          }

          // Clear mocks between tests
          vi.clearAllMocks();

          // Test 2: createEvent shows loading indicator
          {
            vi.mocked(eventService.createEvent).mockImplementation(
              () => new Promise(resolve => setTimeout(() => resolve(mockEvent), 10))
            );

            const { result } = renderHook(() => useEvents());

            // Initially not loading
            expect(result.current.loading).toBe(false);

            // Start create operation
            let createPromise: Promise<Event | null>;
            act(() => {
              createPromise = result.current.createEvent(createData);
            });

            // Should be loading immediately after starting the operation
            expect(result.current.loading).toBe(true);

            // Wait for operation to complete
            await act(async () => {
              await createPromise;
            });

            // Verify loading is false after completion
            expect(result.current.loading).toBe(false);
          }

          // Clear mocks between tests
          vi.clearAllMocks();

          // Test 3: updateEvent shows loading indicator
          {
            const updateData: EventUpdateData = {
              title: eventData.title + ' Updated',
            };

            vi.mocked(eventService.updateEvent).mockImplementation(
              () => new Promise(resolve => setTimeout(() => resolve({ ...mockEvent, title: updateData.title! }), 10))
            );

            const { result } = renderHook(() => useEvents());

            // Initially not loading
            expect(result.current.loading).toBe(false);

            // Start update operation
            let updatePromise: Promise<Event | null>;
            act(() => {
              updatePromise = result.current.updateEvent(eventId, updateData);
            });

            // Should be loading immediately after starting the operation
            expect(result.current.loading).toBe(true);

            // Wait for operation to complete
            await act(async () => {
              await updatePromise;
            });

            // Verify loading is false after completion
            expect(result.current.loading).toBe(false);
          }

          // Clear mocks between tests
          vi.clearAllMocks();

          // Test 4: deleteEvent shows loading indicator
          {
            vi.mocked(eventService.deleteEvent).mockImplementation(
              () => new Promise(resolve => setTimeout(() => resolve(undefined), 10))
            );

            const { result } = renderHook(() => useEvents());

            // Initially not loading
            expect(result.current.loading).toBe(false);

            // Start delete operation
            let deletePromise: Promise<boolean>;
            act(() => {
              deletePromise = result.current.deleteEvent(eventId);
            });

            // Should be loading immediately after starting the operation
            expect(result.current.loading).toBe(true);

            // Wait for operation to complete
            await act(async () => {
              await deletePromise;
            });

            // Verify loading is false after completion
            expect(result.current.loading).toBe(false);
          }

          // Clear mocks between tests
          vi.clearAllMocks();

          // Test 5: refreshEvents shows loading indicator
          {
            vi.mocked(eventService.getEvents).mockImplementation(
              () => new Promise(resolve => setTimeout(() => resolve([mockEvent]), 10))
            );

            const { result } = renderHook(() => useEvents());

            // Initially not loading
            expect(result.current.loading).toBe(false);

            // Start refresh operation
            act(() => {
              result.current.refreshEvents();
            });

            // Should be loading immediately after starting the operation
            expect(result.current.loading).toBe(true);

            // Wait for operation to complete
            await waitFor(() => {
              expect(result.current.loading).toBe(false);
            }, { timeout: 100 });

            // Verify loading is false after completion
            expect(result.current.loading).toBe(false);
          }
        }
      ),
      { numRuns: 100 }
    );
  }, 30000); // 30 second timeout for property-based test with 100 runs

  /**
   * Additional test: Loading state is false even when operations fail
   * 
   * This ensures that loading indicators are properly cleared even when errors occur,
   * preventing the UI from being stuck in a loading state.
   */
  it('Property 19 (Error Case): Loading indicators are cleared on error', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.string({ minLength: 1, maxLength: 100 }),
        fc.integer({ min: 1, max: 1000 }),
        async (errorMessage, eventId) => {
          // Test fetchEvents error handling
          {
            vi.mocked(eventService.getEvents).mockImplementation(
              () => new Promise((_, reject) => setTimeout(() => reject(new Error(errorMessage)), 10))
            );

            const { result } = renderHook(() => useEvents());

            expect(result.current.loading).toBe(false);

            act(() => {
              result.current.fetchEvents();
            });

            expect(result.current.loading).toBe(true);

            await waitFor(() => {
              expect(result.current.loading).toBe(false);
            }, { timeout: 100 });

            // Verify error is set and loading is false
            expect(result.current.loading).toBe(false);
            expect(result.current.error).toBeTruthy();
          }

          vi.clearAllMocks();

          // Test createEvent error handling
          {
            vi.mocked(eventService.createEvent).mockImplementation(
              () => new Promise((_, reject) => setTimeout(() => reject(new Error(errorMessage)), 10))
            );

            const { result } = renderHook(() => useEvents());

            const createData: EventCreateData = {
              title: 'Test',
              category: 1,
              start_time: '2025-12-04T10:00:00Z',
              end_time: '2025-12-04T11:00:00Z',
            };

            expect(result.current.loading).toBe(false);

            let createPromise: Promise<Event | null>;
            act(() => {
              createPromise = result.current.createEvent(createData);
            });

            expect(result.current.loading).toBe(true);

            await act(async () => {
              await createPromise;
            });

            expect(result.current.loading).toBe(false);
            expect(result.current.error).toBeTruthy();
          }

          vi.clearAllMocks();

          // Test deleteEvent error handling
          {
            vi.mocked(eventService.deleteEvent).mockImplementation(
              () => new Promise((_, reject) => setTimeout(() => reject(new Error(errorMessage)), 10))
            );

            const { result } = renderHook(() => useEvents());

            expect(result.current.loading).toBe(false);

            let deletePromise: Promise<boolean>;
            act(() => {
              deletePromise = result.current.deleteEvent(eventId);
            });

            expect(result.current.loading).toBe(true);

            await act(async () => {
              await deletePromise;
            });

            expect(result.current.loading).toBe(false);
            expect(result.current.error).toBeTruthy();
          }
        }
      ),
      { numRuns: 100 }
    );
  }, 30000); // 30 second timeout for property-based test with 100 runs
});
