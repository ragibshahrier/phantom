import { useState, useCallback } from 'react';
import chatService from '../services/chatService';
import { ChatHistoryItem, UseChatReturn, Event } from '../types';

/**
 * Default welcome message from Phantom
 * Displayed when the chat is first initialized
 */
const PHANTOM_WELCOME_MESSAGE: ChatHistoryItem = {
  id: 'phantom-welcome',
  sender: 'PHANTOM',
  text: `Good evening. I am PHANTOM, your Victorian Ghost Butler, at your eternal service.

I have been summoned to assist you in managing the temporal affairs of your mortal existence. You may speak to me in plain language, and I shall endeavor to interpret your scheduling needs with the utmost precision.

For instance, you might say:
• "Schedule a study session tomorrow at 2pm for 2 hours"
• "Add an exam on Friday at 10am"
• "Create a gym appointment next Monday at 6pm"

I shall dutifully record your engagements and ensure your calendar remains... impeccably organized.

How may I be of assistance this evening?`,
  timestamp: new Date(),
};

/**
 * useChat Hook
 * 
 * Custom hook for managing chat state and operations with Phantom.
 * Provides functions for sending messages, managing chat history,
 * and handling loading/error states.
 * 
 * @returns UseChatReturn object with chat history, loading state, error state, and chat functions
 */
export const useChat = (): UseChatReturn => {
  // State management - Initialize with welcome message
  const [chatHistory, setChatHistory] = useState<ChatHistoryItem[]>([PHANTOM_WELCOME_MESSAGE]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Generate a unique ID for chat messages
   * Uses timestamp and random number to ensure uniqueness
   * 
   * @returns Unique string ID
   */
  const generateMessageId = (): string => {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  };

  /**
   * Send a message to Phantom and handle the response
   * Adds user message to history immediately, then adds Phantom's response after API call
   * Adds system error messages if the API call fails
   * 
   * @param message - The user's message text
   * @returns Object with arrays of created and deleted events
   */
  const sendMessage = useCallback(async (message: string): Promise<{created: Event[], deleted: number[]}> => {
    // Clear any previous errors
    setError(null);

    // Add user message to history immediately
    const userMessage: ChatHistoryItem = {
      id: generateMessageId(),
      sender: 'USER',
      text: message,
      timestamp: new Date(),
    };
    setChatHistory(prev => [...prev, userMessage]);

    // Set loading state
    setIsLoading(true);

    try {
      // Send message to backend
      const response = await chatService.sendMessage(message);

      // Add Phantom's response to history
      const phantomMessage: ChatHistoryItem = {
        id: generateMessageId(),
        sender: 'PHANTOM',
        text: response.response,
        timestamp: new Date(),
      };
      setChatHistory(prev => [...prev, phantomMessage]);

      // Return created and deleted events
      return {
        created: response.events_created || [],
        deleted: (response.events_deleted || []).map(e => e.id)
      };
    } catch (err: any) {
      // Extract error message
      const errorMessage = err.message || 'Failed to send message. Please try again.';
      setError(errorMessage);

      // Add system error message to chat history
      const systemMessage: ChatHistoryItem = {
        id: generateMessageId(),
        sender: 'SYSTEM',
        text: `Error: ${errorMessage}`,
        timestamp: new Date(),
      };
      setChatHistory(prev => [...prev, systemMessage]);

      console.error('Error sending message:', err);
      
      // Return empty arrays on error
      return {created: [], deleted: []};
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Clear all chat history
   * Resets the chat history to an empty array
   */
  const clearHistory = useCallback((): void => {
    setChatHistory([]);
    setError(null);
  }, []);

  return {
    chatHistory,
    isLoading,
    error,
    sendMessage,
    clearHistory,
  };
};

export default useChat;
