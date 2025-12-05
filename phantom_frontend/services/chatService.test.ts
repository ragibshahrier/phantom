import { describe, it, expect, vi, beforeEach } from 'vitest';
import fc from 'fast-check';
import chatService from './chatService';
import apiClient from '../config/api';

// Mock the API client
vi.mock('../config/api');

describe('chatService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('sendMessage', () => {
    it('should send message to /chat/ endpoint', async () => {
      const mockResponse = {
        response: 'I have scheduled your study session.',
        events_created: [],
        intent_detected: 'create_event',
      };

      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse });

      const result = await chatService.sendMessage('Schedule study session tomorrow at 2pm');

      expect(apiClient.post).toHaveBeenCalledWith('/chat/', {
        message: 'Schedule study session tomorrow at 2pm',
      });
      expect(result).toEqual(mockResponse);
    });

    it('should handle chat response with events_created', async () => {
      const mockResponse = {
        response: 'I have created your event.',
        events_created: [
          {
            id: 1,
            title: 'Study Session',
            description: '',
            category: 2,
            category_name: 'Study',
            category_color: '#4A90E2',
            priority_level: 4,
            start_time: '2024-12-05T14:00:00Z',
            end_time: '2024-12-05T16:00:00Z',
            is_flexible: false,
            is_completed: false,
            created_at: '2024-12-04T10:00:00Z',
            updated_at: '2024-12-04T10:00:00Z',
          },
        ],
        intent_detected: 'create_event',
      };

      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse });

      const result = await chatService.sendMessage('Schedule study session tomorrow at 2pm');

      expect(result.events_created).toBeDefined();
      expect(result.events_created).toHaveLength(1);
      expect(result.events_created![0].title).toBe('Study Session');
    });

    it('should throw error when API call fails', async () => {
      const mockError = {
        response: {
          data: {
            detail: 'Chat service unavailable',
          },
        },
      };

      vi.mocked(apiClient.post).mockRejectedValue(mockError);

      await expect(chatService.sendMessage('Hello')).rejects.toThrow(
        'Chat service unavailable'
      );
    });

    it('should throw generic error when no error details provided', async () => {
      vi.mocked(apiClient.post).mockRejectedValue(new Error('Network error'));

      await expect(chatService.sendMessage('Hello')).rejects.toThrow(
        'Failed to send message. Please try again.'
      );
    });
  });

  describe('getConversationHistory', () => {
    it('should fetch conversation history from /chat/history/ endpoint', async () => {
      const mockHistory = [
        {
          id: 1,
          message: 'Schedule study session tomorrow',
          response: 'I have scheduled your study session.',
          intent_detected: 'create_event',
          timestamp: '2024-12-04T10:00:00Z',
        },
        {
          id: 2,
          message: 'What events do I have today?',
          response: 'You have 3 events scheduled for today.',
          intent_detected: 'query_events',
          timestamp: '2024-12-04T11:00:00Z',
        },
      ];

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockHistory });

      const result = await chatService.getConversationHistory();

      expect(apiClient.get).toHaveBeenCalledWith('/chat/history/');
      expect(result).toEqual(mockHistory);
      expect(result).toHaveLength(2);
    });

    it('should return empty array when no history exists', async () => {
      vi.mocked(apiClient.get).mockResolvedValue({ data: [] });

      const result = await chatService.getConversationHistory();

      expect(result).toEqual([]);
    });

    it('should throw error when fetching history fails', async () => {
      const mockError = {
        response: {
          data: {
            detail: 'Failed to fetch history',
          },
        },
      };

      vi.mocked(apiClient.get).mockRejectedValue(mockError);

      await expect(chatService.getConversationHistory()).rejects.toThrow(
        'Failed to fetch history'
      );
    });

    it('should throw generic error when no error details provided', async () => {
      vi.mocked(apiClient.get).mockRejectedValue(new Error('Network error'));

      await expect(chatService.getConversationHistory()).rejects.toThrow(
        'Failed to fetch conversation history. Please try again.'
      );
    });
  });

  describe('Property-Based Tests', () => {
    /**
     * Feature: phantom-frontend-integration, Property 9: Chat messages trigger API calls
     * For any user message in the chat interface, the frontend should send it to 
     * `/api/chat/` and display the response in the chat history.
     * Validates: Requirements 4.1, 4.2
     */
    it('Property 9: Chat messages trigger API calls', async () => {
      await fc.assert(
        fc.asyncProperty(
          // Generate random non-empty strings as chat messages
          fc.string({ minLength: 1, maxLength: 500 }),
          async (message) => {
            // Clear mocks for each iteration
            vi.clearAllMocks();

            // Mock a successful response
            const mockResponse = {
              response: 'Mock response from Phantom',
              events_created: [],
              intent_detected: 'general_query',
            };

            vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse });

            // Send the message
            const result = await chatService.sendMessage(message);

            // Verify the API was called with correct endpoint and data
            expect(apiClient.post).toHaveBeenCalledTimes(1);
            expect(apiClient.post).toHaveBeenCalledWith('/chat/', {
              message: message,
            });

            // Verify the response is returned correctly
            expect(result).toEqual(mockResponse);
            expect(result.response).toBeDefined();
          }
        ),
        { numRuns: 100 }
      );
    });
  });
});
