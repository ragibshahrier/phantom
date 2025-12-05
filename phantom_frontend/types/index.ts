// ============================================================================
// Core Data Models
// ============================================================================

/**
 * Event represents a calendar entry with title, description, time range, and category
 */
export interface Event {
  id: number;
  title: string;
  description: string;
  category: number;
  category_name: string;
  category_color: string;
  priority_level: number;
  start_time: string; // ISO 8601 format
  end_time: string; // ISO 8601 format
  is_flexible: boolean;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * Category represents an event classification with priority level
 */
export interface Category {
  id: number;
  name: string;
  priority_level: number; // 1-5, higher is more important
  color: string; // Hex color code
  description: string;
}

/**
 * User represents the authenticated user
 */
export interface User {
  id: number;
  username: string;
  name: string;
  timezone: string;
  default_event_duration: number;
}

/**
 * ChatMessage represents a message in the chat interface
 */
export interface ChatMessage {
  id: string;
  sender: 'USER' | 'PHANTOM' | 'SYSTEM';
  text: string;
  timestamp: Date;
  events_created?: Event[];
  events_modified?: Event[];
}

// ============================================================================
// API Request/Response Types
// ============================================================================

/**
 * Authentication API types
 */
export interface RegisterData {
  username: string;
  name: string;
  password: string;
  password_confirm: string;
}

export interface LoginData {
  username: string;
  password: string;
}

export interface TokenResponse {
  access: string;
  refresh: string;
  user_id: number;
  username: string;
}

export interface RefreshTokenRequest {
  refresh: string;
}

export interface RefreshTokenResponse {
  access: string;
}

/**
 * Event API types
 */
export interface EventCreateData {
  title: string;
  description?: string;
  category: number;
  start_time: string;
  end_time: string;
  is_flexible?: boolean;
}

export interface EventUpdateData {
  title?: string;
  description?: string;
  category?: number;
  start_time?: string;
  end_time?: string;
  is_flexible?: boolean;
  is_completed?: boolean;
}

export interface EventQueryParams {
  start_date?: string;
  end_date?: string;
  category?: number;
  priority?: number;
}

/**
 * Chat API types
 */
export interface ChatMessageRequest {
  message: string;
}

export interface ChatResponse {
  response: string;
  events_created?: Event[];
  events_modified?: Event[];
  events_deleted?: Array<{id: number; title: string; start_time: string}>;
  intent_detected?: string;
}

export interface ConversationHistoryItem {
  id: number;
  message: string;
  response: string;
  intent_detected: string;
  timestamp: string;
}

/**
 * User Preferences API types
 */
export interface UserPreferences {
  timezone: string;
  default_event_duration: number; // minutes
}

export interface UpdatePreferencesData {
  timezone?: string;
  default_event_duration?: number;
}

/**
 * Google Calendar Integration API types
 */
export interface GoogleCalendarStatus {
  connected: boolean;
  email?: string;
}

export interface GoogleCalendarConnectResponse {
  authorization_url: string;
}

// ============================================================================
// Service Method Signatures
// ============================================================================

/**
 * Authentication Service interface
 */
export interface AuthService {
  register(data: RegisterData): Promise<void>;
  login(data: LoginData): Promise<TokenResponse>;
  logout(refreshToken: string): Promise<void>;
  refreshToken(refreshToken: string): Promise<RefreshTokenResponse>;
  verifyToken(token: string): Promise<boolean>;
}

/**
 * Event Service interface
 */
export interface EventService {
  getEvents(params?: EventQueryParams): Promise<Event[]>;
  getEvent(id: number): Promise<Event>;
  createEvent(data: EventCreateData): Promise<Event>;
  updateEvent(id: number, data: EventUpdateData): Promise<Event>;
  deleteEvent(id: number): Promise<void>;
}

/**
 * Chat Service interface
 */
export interface ChatService {
  sendMessage(message: string): Promise<ChatResponse>;
  getConversationHistory(): Promise<ConversationHistoryItem[]>;
}

/**
 * Category Service interface
 */
export interface CategoryService {
  getCategories(): Promise<Category[]>;
  getCategory(id: number): Promise<Category>;
}

/**
 * Preference Service interface
 */
export interface PreferenceService {
  getPreferences(): Promise<UserPreferences>;
  updatePreferences(data: UpdatePreferencesData): Promise<UserPreferences>;
}

/**
 * Integration Service interface
 */
export interface IntegrationService {
  connectGoogleCalendar(): Promise<GoogleCalendarConnectResponse>;
  getGoogleCalendarStatus(): Promise<GoogleCalendarStatus>;
  disconnectGoogleCalendar(): Promise<void>;
}

// ============================================================================
// Context and Hook Types
// ============================================================================

/**
 * Auth Context type
 */
export interface AuthContextType {
  user: { username: string; userId: number } | null;
  isAuthenticated: boolean;
  loading: boolean;
  login(username: string, password: string): Promise<{ success: boolean; error?: string }>;
  register(username: string, name: string, password: string, passwordConfirm: string): Promise<{ success: boolean; error?: string }>;
  logout(): Promise<void>;
}

/**
 * useEvents hook return type
 */
export interface UseEventsReturn {
  events: Event[];
  loading: boolean;
  error: string | null;
  selectedDate: Date | null;
  setSelectedDate: (date: Date | null) => void;
  fetchEvents(params?: EventQueryParams): Promise<void>;
  createEvent(data: EventCreateData): Promise<Event | null>;
  updateEvent(id: number, data: EventUpdateData): Promise<Event | null>;
  deleteEvent(id: number): Promise<boolean>;
  refreshEvents(): Promise<void>;
}

/**
 * Chat history item for useChat hook
 */
export interface ChatHistoryItem {
  id: string;
  sender: 'USER' | 'PHANTOM' | 'SYSTEM';
  text: string;
  timestamp: Date;
}

/**
 * useChat hook return type
 */
export interface UseChatReturn {
  chatHistory: ChatHistoryItem[];
  isLoading: boolean;
  error: string | null;
  sendMessage(message: string): Promise<{created: Event[], deleted: number[]}>;
  clearHistory(): void;
}

// ============================================================================
// Utility Types
// ============================================================================

/**
 * API Error response structure
 */
export interface ApiError {
  message: string;
  errors?: Record<string, string[]>;
  status?: number;
}

/**
 * API Configuration
 */
export interface ApiConfig {
  baseURL: string;
  timeout: number;
  headers: {
    'Content-Type': string;
  };
}

// ============================================================================
// Legacy Types (for backward compatibility during migration)
// ============================================================================

export type Priority = 'NORMAL' | 'CRITICAL';

export interface Task {
  id: string;
  title: string;
  priority: Priority;
  timestamp: string; // Display time (e.g. "0800 HRS")
  date: string;      // ISO Date string (YYYY-MM-DD) for calendar mapping
  description?: string;
  startTime?: string; // Start time in readable format (e.g. "08:00 AM")
  endTime?: string;   // End time in readable format (e.g. "10:00 AM")
  duration?: string;  // Duration in readable format (e.g. "2h 30m")
}

export interface GhostResponse {
  message: string;
  action?: 'SPAWN_TASK' | 'BANISH_TASK';
  payload?: any;
}