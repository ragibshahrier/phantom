import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useChat } from './useChat';
import chatService from '../services/chatService';
import type { ChatResponse } from '../types';

// Mock the chat service
vi.mock('../services/chatService');

describe('useChat Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should initialize with welcome message from Phantom', () => {
    const { result } = renderHook(() => useChat());
    
    // Should have one welcome message
    expect(result.current.chatHistory).toHaveLength(1);
    expect(result.current.chatHistory[0].sender).toBe('PHANTOM');
    expect(result.current.chatHistory[0].id).toBe('phantom-welcome');
    expect(result.current.chatHistory[0].text).toContain('Good evening');
    expect(result.current.chatHistory[0].text).toContain('Victorian Ghost Butler');
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('should add user message immediately when sending', async () => {
    const mockResponse: ChatResponse = {
      response: 'Hello! How can I help you?',
    };
    vi.mocked(chatService.sendMessage).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useChat());

    await act(async () => {
      await result.current.sendMessage('Hello Phantom');
    });

    // Should have welcome message + user message + phantom response
    expect(result.current.chatHistory).toHaveLength(3);
    
    // Second message should be from user
    expect(result.current.chatHistory[1].sender).toBe('USER');
    expect(result.current.chatHistory[1].text).toBe('Hello Phantom');
    expect(result.current.chatHistory[1].timestamp).toBeInstanceOf(Date);
    
    // Third message should be from Phantom
    expect(result.current.chatHistory[2].sender).toBe('PHANTOM');
    expect(result.current.chatHistory[2].text).toBe('Hello! How can I help you?');
  });

  it('should add Phantom response after API call', async () => {
    const mockResponse: ChatResponse = {
      response: 'I have scheduled your meeting.',
      intent_detected: 'create_event',
    };
    vi.mocked(chatService.sendMessage).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useChat());

    await act(async () => {
      await result.current.sendMessage('Schedule a meeting tomorrow');
    });

    expect(chatService.sendMessage).toHaveBeenCalledWith('Schedule a meeting tomorrow');
    expect(result.current.chatHistory).toHaveLength(3);
    expect(result.current.chatHistory[2].text).toBe('I have scheduled your meeting.');
  });

  it('should add system error message when API call fails', async () => {
    const errorMessage = 'Network error';
    vi.mocked(chatService.sendMessage).mockRejectedValue(new Error(errorMessage));

    const { result } = renderHook(() => useChat());

    await act(async () => {
      await result.current.sendMessage('Hello');
    });

    // Should have welcome message + user message + system error message
    expect(result.current.chatHistory).toHaveLength(3);
    
    // Second message is user message
    expect(result.current.chatHistory[1].sender).toBe('USER');
    expect(result.current.chatHistory[1].text).toBe('Hello');
    
    // Third message is system error
    expect(result.current.chatHistory[2].sender).toBe('SYSTEM');
    expect(result.current.chatHistory[2].text).toContain('Error:');
    expect(result.current.chatHistory[2].text).toContain(errorMessage);
    
    // Error state should be set
    expect(result.current.error).toBe(errorMessage);
  });

  it('should handle multiple messages in sequence', async () => {
    const mockResponse1: ChatResponse = {
      response: 'First response',
    };
    const mockResponse2: ChatResponse = {
      response: 'Second response',
    };
    
    vi.mocked(chatService.sendMessage)
      .mockResolvedValueOnce(mockResponse1)
      .mockResolvedValueOnce(mockResponse2);

    const { result } = renderHook(() => useChat());

    await act(async () => {
      await result.current.sendMessage('First message');
    });

    await act(async () => {
      await result.current.sendMessage('Second message');
    });

    // Should have 5 messages total (welcome + 2 user + 2 phantom)
    expect(result.current.chatHistory).toHaveLength(5);
    expect(result.current.chatHistory[1].text).toBe('First message');
    expect(result.current.chatHistory[2].text).toBe('First response');
    expect(result.current.chatHistory[3].text).toBe('Second message');
    expect(result.current.chatHistory[4].text).toBe('Second response');
  });

  it('should clear chat history', async () => {
    const mockResponse: ChatResponse = {
      response: 'Test response',
    };
    vi.mocked(chatService.sendMessage).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useChat());

    // Add some messages
    await act(async () => {
      await result.current.sendMessage('Test message');
    });

    expect(result.current.chatHistory).toHaveLength(3);

    // Clear history
    act(() => {
      result.current.clearHistory();
    });

    expect(result.current.chatHistory).toEqual([]);
    expect(result.current.error).toBeNull();
  });

  it('should set loading state during message send', async () => {
    vi.mocked(chatService.sendMessage).mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve({ response: 'Test' }), 100))
    );

    const { result } = renderHook(() => useChat());

    act(() => {
      result.current.sendMessage('Test');
    });

    // Should be loading immediately
    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });
  });

  it('should clear previous errors when sending new message', async () => {
    // First call fails
    vi.mocked(chatService.sendMessage).mockRejectedValueOnce(new Error('First error'));

    const { result } = renderHook(() => useChat());

    await act(async () => {
      await result.current.sendMessage('First message');
    });

    expect(result.current.error).toBe('First error');

    // Second call succeeds
    vi.mocked(chatService.sendMessage).mockResolvedValueOnce({ response: 'Success' });

    await act(async () => {
      await result.current.sendMessage('Second message');
    });

    // Error should be cleared
    expect(result.current.error).toBeNull();
  });

  it('should generate unique IDs for each message', async () => {
    const mockResponse: ChatResponse = {
      response: 'Test response',
    };
    vi.mocked(chatService.sendMessage).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useChat());

    await act(async () => {
      await result.current.sendMessage('Test message');
    });

    const ids = result.current.chatHistory.map(msg => msg.id);
    const uniqueIds = new Set(ids);
    
    // All IDs should be unique
    expect(uniqueIds.size).toBe(ids.length);
    
    // IDs should be strings
    ids.forEach(id => {
      expect(typeof id).toBe('string');
      expect(id.length).toBeGreaterThan(0);
    });
  });

  it('should preserve message order', async () => {
    const mockResponse: ChatResponse = {
      response: 'Response',
    };
    vi.mocked(chatService.sendMessage).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useChat());

    await act(async () => {
      await result.current.sendMessage('Message 1');
    });

    await act(async () => {
      await result.current.sendMessage('Message 2');
    });

    // Messages should be in chronological order (after welcome message)
    expect(result.current.chatHistory[1].text).toBe('Message 1');
    expect(result.current.chatHistory[2].text).toBe('Response');
    expect(result.current.chatHistory[3].text).toBe('Message 2');
    expect(result.current.chatHistory[4].text).toBe('Response');
    
    // Timestamps should be in order
    for (let i = 1; i < result.current.chatHistory.length; i++) {
      expect(result.current.chatHistory[i].timestamp.getTime())
        .toBeGreaterThanOrEqual(result.current.chatHistory[i - 1].timestamp.getTime());
    }
  });
});
