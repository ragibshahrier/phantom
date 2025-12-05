
import { useState, useCallback } from 'react';
import { Task, ChatMessage } from '../types';

export const usePhantom = () => {
  // Helper to format dates as YYYY-MM-DD
  const formatDate = (d: Date): string => {
    const isoString = d.toISOString();
    const datePart = isoString.split('T')[0];
    return datePart || '';
  };
  
  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);
  const nextWeek = new Date(today);
  nextWeek.setDate(nextWeek.getDate() + 3);

  // Format dates as strings
  const todayStr: string = formatDate(today);
  const nextWeekStr: string = formatDate(nextWeek);

  const [selectedDate, setSelectedDate] = useState<string>(todayStr);
  const [isHaunting, setIsHaunting] = useState(false); // State for spooky animation

  const [tasks, setTasks] = useState<Task[]>([
    {
      id: '0x1A4',
      title: 'Routine Maintenance: Gym',
      priority: 'NORMAL',
      timestamp: '0800 HRS',
      date: todayStr,
      description: 'Physical vessel upkeep required.'
    },
    {
      id: '0x1B5',
      title: 'Dark Ritual: Coffee',
      priority: 'NORMAL',
      timestamp: '0930 HRS',
      date: todayStr,
      description: 'Caffeine intake required for neural connectivity.'
    },
    {
      id: '0x9F2',
      title: 'FINAL JUDGMENT: EXAM',
      priority: 'CRITICAL',
      timestamp: '1400 HRS',
      date: nextWeekStr,
      description: 'Academic termination imminent. Failure is not an option.'
    }
  ]);

  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([
    {
      id: 'init-1',
      sender: 'PHANTOM',
      text: 'SYSTEM ONLINE. The calendar of fate awaits.',
      timestamp: new Date()
    }
  ]);

  const [isLoading, setIsLoading] = useState(false);

  const triggerHaunting = () => {
    setIsHaunting(true);
    // Play sound here if audio was enabled
    setTimeout(() => setIsHaunting(false), 2500); // Ghost disappears after 2.5s
  };

  const summonSpirit = useCallback(async (message: string) => {
    setIsLoading(true);
    
    // Add user message immediately
    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: 'USER',
      text: message,
      timestamp: new Date()
    };
    setChatHistory(prev => [...prev, userMsg]);

    // Simulate Network/Spirit Delay
    await new Promise(resolve => setTimeout(resolve, 1500));

    // Determine response based on keywords (Mock Logic)
    let ghostText = "The void stares back.";
    let newTask: Task | null = null;
    let isCritical = false;
    
    // Date Logic for new task
    const msgLower = message.toLowerCase();
    let targetDate = new Date();
    
    if (msgLower.includes('tomorrow')) {
      targetDate.setDate(targetDate.getDate() + 1);
    } else if (msgLower.includes('next week')) {
      targetDate.setDate(targetDate.getDate() + 7);
    }

    const targetDateStr: string = formatDate(targetDate);

    if (msgLower.includes('urgent') || msgLower.includes('deadline') || msgLower.includes('exam') || msgLower.includes('die') || msgLower.includes('doom')) {
      ghostText = "YOUR ANXIETY FEEDS THE MACHINE. FATE SEALED.";
      isCritical = true;
      newTask = {
        id: `0x${Math.floor(Math.random() * 1000).toString(16).toUpperCase()}`,
        title: 'UNFORESEEN CONSEQUENCE',
        priority: 'CRITICAL',
        timestamp: 'NOW',
        date: targetDateStr,
        description: message
      };
    } else if (msgLower.includes('buy') || msgLower.includes('get') || msgLower.includes('call')) {
      ghostText = "Material acquisition logged.";
      newTask = {
        id: `0x${Math.floor(Math.random() * 1000).toString(16).toUpperCase()}`,
        title: 'ACQUISITION',
        priority: 'NORMAL',
        timestamp: 'SOON',
        date: targetDateStr,
        description: message
      };
    }

    if (newTask) {
      setTasks(prev => [...prev, newTask!]);
      // If task was added for a different day, switch view context conceptually
      if (newTask.date !== selectedDate) {
        ghostText += ` (Recorded for ${newTask.date})`;
      }
    }

    const phantomMsg: ChatMessage = {
      id: (Date.now() + 1).toString(),
      sender: 'PHANTOM',
      text: ghostText,
      timestamp: new Date()
    };

    setChatHistory(prev => [...prev, phantomMsg]);
    setIsLoading(false);

    if (isCritical) {
      triggerHaunting();
    }

  }, [selectedDate]);

  const banishTask = useCallback((id: string) => {
    setTasks(prev => prev.filter(t => t.id !== id));
    setChatHistory(prev => [...prev, {
      id: Date.now().toString(),
      sender: 'SYSTEM',
      text: `TASK 0x${id} PURGED FROM MEMORY.`,
      timestamp: new Date()
    }]);
  }, []);

  const editTask = useCallback((updatedTask: Task) => {
    setTasks(prev => prev.map(t => t.id === updatedTask.id ? updatedTask : t));
  }, []);

  return {
    tasks,
    chatHistory,
    isLoading,
    isHaunting,
    selectedDate,
    setSelectedDate,
    summonSpirit,
    banishTask,
    editTask
  };
};
