import { describe, it, expect } from 'vitest';
import type {
  Event,
  Category,
  User,
  ChatMessage,
  RegisterData,
  LoginData,
  TokenResponse,
  EventCreateData,
  EventQueryParams,
  ChatResponse,
  UserPreferences,
  GoogleCalendarStatus,
  ApiError,
  ApiConfig,
} from './index';

describe('TypeScript Interfaces', () => {
  it('should have valid Event interface', () => {
    const event: Event = {
      id: 1,
      title: 'Test Event',
      description: 'Test Description',
      category: 1,
      category_name: 'Study',
      category_color: '#FF0000',
      priority_level: 4,
      start_time: '2025-12-03T10:00:00Z',
      end_time: '2025-12-03T11:00:00Z',
      is_flexible: false,
      is_completed: false,
      created_at: '2025-12-03T09:00:00Z',
      updated_at: '2025-12-03T09:00:00Z',
    };
    
    expect(event.id).toBe(1);
    expect(event.title).toBe('Test Event');
  });

  it('should have valid Category interface', () => {
    const category: Category = {
      id: 1,
      name: 'Study',
      priority_level: 4,
      color: '#FF0000',
      description: 'Study sessions',
    };
    
    expect(category.id).toBe(1);
    expect(category.name).toBe('Study');
  });

  it('should have valid User interface', () => {
    const user: User = {
      id: 1,
      username: 'testuser',
      name: 'Test User',
      timezone: 'America/New_York',
      default_event_duration: 60,
    };
    
    expect(user.id).toBe(1);
    expect(user.username).toBe('testuser');
  });

  it('should have valid ChatMessage interface', () => {
    const message: ChatMessage = {
      id: '123',
      sender: 'USER',
      text: 'Hello Phantom',
      timestamp: new Date(),
    };
    
    expect(message.id).toBe('123');
    expect(message.sender).toBe('USER');
  });

  it('should have valid RegisterData interface', () => {
    const registerData: RegisterData = {
      username: 'newuser',
      name: 'New User',
      password: 'password123',
      password_confirm: 'password123',
    };
    
    expect(registerData.username).toBe('newuser');
  });

  it('should have valid LoginData interface', () => {
    const loginData: LoginData = {
      username: 'testuser',
      password: 'password123',
    };
    
    expect(loginData.username).toBe('testuser');
  });

  it('should have valid TokenResponse interface', () => {
    const tokenResponse: TokenResponse = {
      access: 'access_token',
      refresh: 'refresh_token',
      user_id: 1,
      username: 'testuser',
    };
    
    expect(tokenResponse.access).toBe('access_token');
  });

  it('should have valid EventCreateData interface', () => {
    const eventData: EventCreateData = {
      title: 'New Event',
      description: 'Event description',
      category: 1,
      start_time: '2025-12-03T10:00:00Z',
      end_time: '2025-12-03T11:00:00Z',
      is_flexible: false,
    };
    
    expect(eventData.title).toBe('New Event');
  });

  it('should have valid EventQueryParams interface', () => {
    const params: EventQueryParams = {
      start_date: '2025-12-01',
      end_date: '2025-12-31',
      category: 1,
      priority: 4,
    };
    
    expect(params.start_date).toBe('2025-12-01');
  });

  it('should have valid ChatResponse interface', () => {
    const response: ChatResponse = {
      response: 'I have created your event',
      events_created: [],
      intent_detected: 'create_event',
    };
    
    expect(response.response).toBe('I have created your event');
  });

  it('should have valid UserPreferences interface', () => {
    const prefs: UserPreferences = {
      timezone: 'America/New_York',
      default_event_duration: 60,
    };
    
    expect(prefs.timezone).toBe('America/New_York');
  });

  it('should have valid GoogleCalendarStatus interface', () => {
    const status: GoogleCalendarStatus = {
      connected: true,
      email: 'user@example.com',
    };
    
    expect(status.connected).toBe(true);
  });

  it('should have valid ApiError interface', () => {
    const error: ApiError = {
      message: 'An error occurred',
      errors: { field: ['Error message'] },
      status: 400,
    };
    
    expect(error.message).toBe('An error occurred');
  });

  it('should have valid ApiConfig interface', () => {
    const config: ApiConfig = {
      baseURL: 'http://localhost:8000/api',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    };
    
    expect(config.baseURL).toBe('http://localhost:8000/api');
  });
});
