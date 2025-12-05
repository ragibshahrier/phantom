import { describe, it, expect } from 'vitest';
import type { Task, ChatMessage } from '../types';

describe('usePhantom Hook Types', () => {
  it('should have valid Task type structure', () => {
    const task: Task = {
      id: '0x1A4',
      title: 'Test Task',
      priority: 'NORMAL',
      timestamp: '0800 HRS',
      date: '2025-12-03',
      description: 'Test description'
    };
    
    expect(task.id).toBe('0x1A4');
    expect(task.title).toBe('Test Task');
    expect(task.priority).toBe('NORMAL');
    expect(task.timestamp).toBe('0800 HRS');
    expect(task.date).toBe('2025-12-03');
    expect(task.description).toBe('Test description');
  });

  it('should have valid ChatMessage type structure', () => {
    const message: ChatMessage = {
      id: 'test-1',
      sender: 'USER',
      text: 'Hello',
      timestamp: new Date()
    };
    
    expect(message.id).toBe('test-1');
    expect(message.sender).toBe('USER');
    expect(message.text).toBe('Hello');
    expect(message.timestamp).toBeInstanceOf(Date);
  });

  it('should support CRITICAL priority', () => {
    const criticalTask: Task = {
      id: '0x9F2',
      title: 'URGENT',
      priority: 'CRITICAL',
      timestamp: 'NOW',
      date: '2025-12-03'
    };
    
    expect(criticalTask.priority).toBe('CRITICAL');
  });

  it('should support all sender types', () => {
    const userMsg: ChatMessage = {
      id: '1',
      sender: 'USER',
      text: 'test',
      timestamp: new Date()
    };
    
    const phantomMsg: ChatMessage = {
      id: '2',
      sender: 'PHANTOM',
      text: 'test',
      timestamp: new Date()
    };
    
    const systemMsg: ChatMessage = {
      id: '3',
      sender: 'SYSTEM',
      text: 'test',
      timestamp: new Date()
    };
    
    expect(userMsg.sender).toBe('USER');
    expect(phantomMsg.sender).toBe('PHANTOM');
    expect(systemMsg.sender).toBe('SYSTEM');
  });

  it('should allow optional description in Task', () => {
    const taskWithoutDesc: Task = {
      id: '0x1',
      title: 'Test',
      priority: 'NORMAL',
      timestamp: '1000 HRS',
      date: '2025-12-03'
    };
    
    expect(taskWithoutDesc.description).toBeUndefined();
  });
});
