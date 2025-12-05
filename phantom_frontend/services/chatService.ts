import apiClient from '../config/api';
import {
  ChatResponse,
  ConversationHistoryItem,
  ChatService,
} from '../types';

/**
 * Chat Service
 * Handles all chat-related API calls including sending messages to Phantom
 * and retrieving conversation history.
 */

/**
 * Send a message to Phantom and receive a response
 * POST /api/chat/
 * 
 * @param message - The user's message text
 * @returns ChatResponse with Phantom's response and any created/modified events
 * @throws Error if sending message fails
 */
const sendMessage = async (message: string): Promise<ChatResponse> => {
  try {
    const response = await apiClient.post<ChatResponse>('/chat/', { message });
    return response.data;
  } catch (error: any) {
    // Extract error message from response
    const errorMessage = error.response?.data?.message || 
                        error.response?.data?.error ||
                        error.response?.data?.detail ||
                        'Failed to send message. Please try again.';
    throw new Error(errorMessage);
  }
};

/**
 * Get conversation history with Phantom
 * GET /api/chat/history/
 * 
 * @returns Array of conversation history items
 * @throws Error if fetching history fails
 */
const getConversationHistory = async (): Promise<ConversationHistoryItem[]> => {
  try {
    const response = await apiClient.get<ConversationHistoryItem[]>('/chat/history/');
    return response.data;
  } catch (error: any) {
    // Extract error message from response
    const errorMessage = error.response?.data?.message || 
                        error.response?.data?.error ||
                        error.response?.data?.detail ||
                        'Failed to fetch conversation history. Please try again.';
    throw new Error(errorMessage);
  }
};

/**
 * Export chat service object implementing ChatService interface
 */
const chatService: ChatService = {
  sendMessage,
  getConversationHistory,
};

export default chatService;
