
import React, { useEffect, useRef, useState } from 'react';
import CRTScanlines from '../components/CRTScanlines';
import TerminalInput from '../components/TerminalInput';
import Monolith from '../components/Monolith';
import DoomsdayCalendar from '../components/DoomsdayCalendar';
import GhostOverlay from '../components/GhostOverlay';
import { useChat } from '../hooks/useChat';
import { useEvents } from '../hooks/useEvents';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, List, AlertCircle, CalendarClock, Skull, CalendarDays, Power, Loader2 } from 'lucide-react';
import { Event, Task } from '../types';

type Tab = 'UPLINK' | 'TIMELINE' | 'CALENDAR';

interface SeanceRoomProps {
    user: string;
    onLogout: () => void;
}

const SeanceRoom: React.FC<SeanceRoomProps> = ({ user, onLogout }) => {
  const { chatHistory, isLoading: isChatLoading, sendMessage } = useChat();
  const { 
    events, 
    loading: eventsLoading, 
    error: eventsError, 
    selectedDate, 
    setSelectedDate, 
    fetchEvents, 
    deleteEvent, 
    updateEvent, 
    refreshEvents 
  } = useEvents();
  const chatEndRef = useRef<HTMLDivElement>(null);
  
  const [activeTab, setActiveTab] = useState<Tab>('UPLINK');
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Fetch events on component mount
  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  // Wrapper function to handle chat messages and sync events
  const summonSpirit = async (message: string) => {
    // Send message to Phantom and get created/deleted events
    const {created, deleted} = await sendMessage(message);
    
    // If events were created or deleted, refresh the timeline
    if (created.length > 0 || deleted.length > 0) {
      await refreshEvents();
    }
  };

  // Auto-scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  // Auto-dismiss success messages
  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(null), 3000);
      return () => clearTimeout(timer);
    }
    return undefined;
  }, [successMessage]);

  // Transform Event to Task format for compatibility with existing components
  const transformEventToTask = (event: Event): Task => {
    // Parse the ISO datetime strings
    // The backend sends times in UTC (e.g., "2024-12-05T17:00:00Z")
    // JavaScript's Date constructor automatically converts to local timezone
    const startTime = new Date(event.start_time);
    const endTime = new Date(event.end_time);
    
    // Debug: Log the conversion
    console.log('Event:', event.title);
    console.log('Backend start_time:', event.start_time);
    console.log('Parsed startTime:', startTime.toString());
    console.log('Local hours:', startTime.getHours());
    
    // Format for timestamp (legacy format) - 24-hour format in LOCAL timezone
    const hours = startTime.getHours().toString().padStart(2, '0');
    const minutes = startTime.getMinutes().toString().padStart(2, '0');
    const timestamp = `${hours}${minutes} HRS`;
    
    // Format start and end times in 12-hour format with local timezone
    const formatTime12Hour = (date: Date): string => {
      // Use toLocaleTimeString to ensure proper timezone handling
      return date.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      });
    };
    
    // Calculate duration
    const durationMs = endTime.getTime() - startTime.getTime();
    const durationHours = Math.floor(durationMs / (1000 * 60 * 60));
    const durationMinutes = Math.floor((durationMs % (1000 * 60 * 60)) / (1000 * 60));
    const duration = durationHours > 0 
      ? `${durationHours}h ${durationMinutes}m`
      : `${durationMinutes}m`;
    
    // Extract date from start_time in LOCAL timezone
    // Don't use split on the ISO string as it gives UTC date
    const date = formatDateLocal(startTime);
    
    // Map priority_level to Priority type (5 = CRITICAL, others = NORMAL)
    const priority = event.priority_level === 5 ? 'CRITICAL' : 'NORMAL';
    
    return {
      id: event.id.toString(),
      title: event.title,
      priority,
      timestamp,
      date,
      description: event.description,
      startTime: formatTime12Hour(startTime),
      endTime: formatTime12Hour(endTime),
      duration,
    };
  };

  // Helper function to format date as YYYY-MM-DD in local timezone
  const formatDateLocal = (date: Date): string => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  // Transform all events to tasks
  const tasks: Task[] = events.map(transformEventToTask);

  // Convert selectedDate to string format for comparison
  const todayStr = formatDateLocal(new Date());
  const selectedDateStr: string = selectedDate ? formatDateLocal(selectedDate) : todayStr;
  
  // Filter Tasks by Selected Date
  const visibleTasks = tasks.filter(t => t.date === selectedDateStr);
  const isToday = selectedDateStr === todayStr;

  // Check for upcoming CRITICAL tasks (Impending Doom)
  const upcomingCriticalTask = tasks
    .filter(t => t.priority === 'CRITICAL' && t.date >= todayStr)
    .sort((a, b) => a.date.localeCompare(b.date))[0];

  // Handle event deletion
  const handleBanishTask = async (id: string) => {
    const success = await deleteEvent(Number(id));
    if (success) {
      setSuccessMessage('Event deleted successfully');
    }
  };

  // Handle event editing
  const handleEditTask = async (task: Task) => {
    // Find the original event to get full data
    const originalEvent = events.find(e => e.id.toString() === task.id);
    if (!originalEvent) return;

    // Transform task back to event update format
    const updatedEvent = await updateEvent(Number(task.id), {
      title: task.title,
      description: task.description,
      // Map priority back to priority_level
      // Note: We can't change category here as we don't have that info in Task
      // This is a limitation of the current Task interface
    });

    if (updatedEvent) {
      setSuccessMessage('Event updated successfully');
    }
  };

  return (
    <div className="relative min-h-[100dvh] w-full flex overflow-hidden font-mono text-sm selection:bg-[#00ff41] selection:text-black bg-[#020202]">
      {/* Background Visuals */}
      <CRTScanlines />
      <GhostOverlay isVisible={false} />

      {/* Success Message Banner */}
      <AnimatePresence>
        {successMessage && (
          <motion.div
            initial={{ y: -100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: -100, opacity: 0 }}
            className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 bg-[#00ff41]/10 border border-[#00ff41] px-6 py-3 rounded shadow-[0_0_15px_rgba(0,255,65,0.3)]"
          >
            <div className="text-[#00ff41] font-bold text-sm tracking-wide">
              {successMessage}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error Message Banner */}
      <AnimatePresence>
        {eventsError && (
          <motion.div
            initial={{ y: -100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: -100, opacity: 0 }}
            className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 bg-[#ff003c]/10 border border-[#ff003c] px-6 py-3 rounded shadow-[0_0_15px_rgba(255,0,60,0.3)]"
          >
            <div className="text-[#ff003c] font-bold text-sm tracking-wide">
              {eventsError}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Container */}
      <main className="relative z-10 flex flex-col md:flex-row w-full h-[100dvh] p-4 md:p-8 gap-8 pb-24 md:pb-8">
        
        {/* LEFT PANEL: THE UPLINK (Chat) */}
        <section className={`
          flex-1 flex-col h-full border border-[#00ff41]/20 bg-black/40 backdrop-blur-sm rounded-sm relative overflow-hidden
          transition-opacity duration-300
          ${activeTab === 'UPLINK' ? 'flex' : 'hidden md:flex'}
        `}>
          {/* Header */}
          <div className="p-4 border-b border-[#00ff41]/20 flex justify-between items-center bg-[#001100]/50 shrink-0">
            <div>
                <h2 className="text-[#00ff41] font-bold tracking-[0.2em] flex items-center gap-2">
                <div className="w-2 h-2 bg-[#00ff41] animate-pulse" />
                SYSTEM_UPLINK
                </h2>
                <div className="text-[10px] text-[#00ff41]/50">
                    OP:: {user}
                </div>
            </div>
            <button 
                onClick={onLogout}
                className="p-2 hover:bg-[#ff003c]/10 text-[#00ff41]/50 hover:text-[#ff003c] transition-colors rounded"
                title="TERMINATE_SESSION"
            >
                <Power className="w-4 h-4" />
            </button>
          </div>

          {/* Terminal Output */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3 scrollbar-hide">
            {chatHistory.map((msg) => (
              <motion.div 
                key={msg.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className={`font-mono text-sm leading-relaxed ${
                  msg.sender === 'PHANTOM' ? 'text-[#00ff41] drop-shadow-[0_0_5px_rgba(0,255,65,0.5)]' : 
                  msg.sender === 'SYSTEM' ? 'text-gray-500 italic' :
                  'text-white'
                }`}
              >
                <span className="opacity-50 text-[10px] mr-2 block sm:inline">
                  [{msg.timestamp.toLocaleTimeString([], {hour12: false})}]
                </span>
                <span className={`font-bold mr-2 ${msg.sender === 'PHANTOM' ? 'text-[#00ff41]' : 'text-blue-400'}`}>
                  {msg.sender === 'USER' ? '>>' : msg.sender === 'PHANTOM' ? 'PHANTOM:' : 'SYS::'}
                </span>
                <span className={msg.sender === 'PHANTOM' ? 'tracking-wide' : ''}>
                  {msg.text}
                </span>
              </motion.div>
            ))}
            <div ref={chatEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-4 md:p-6 bg-gradient-to-t from-black to-transparent shrink-0">
            <TerminalInput onSummon={summonSpirit} isLoading={isChatLoading} />
          </div>
        </section>


        {/* RIGHT PANEL: THE TIMELINE / CALENDAR */}
        <section className={`
          flex-1 flex-col h-full relative
          ${(activeTab === 'TIMELINE' || activeTab === 'CALENDAR') ? 'flex' : 'hidden md:flex'}
        `}>
          {/* IMPENDING DOOM BANNER (Sticky Top) */}
          <AnimatePresence>
            {upcomingCriticalTask && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="mb-4 shrink-0 overflow-hidden"
              >
                <div className="w-full bg-[#ff003c]/10 border border-[#ff003c] p-3 flex items-center justify-between shadow-[0_0_15px_rgba(255,0,60,0.2)]">
                  <div className="flex items-center gap-3">
                    <Skull className="w-5 h-5 text-[#ff003c] animate-pulse" />
                    <div>
                      <div className="text-[#ff003c] font-bold text-xs tracking-widest animate-pulse">
                        IMPENDING DOOM DETECTED
                      </div>
                      <div className="text-white/90 font-bold text-sm">
                        {upcomingCriticalTask.title}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-[#ff003c] text-xs">DUE DATE</div>
                    <div className="text-white font-mono">{upcomingCriticalTask.date}</div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Right Panel Header (Desktop Navigation) */}
          <div className="flex justify-between items-end mb-4 px-2 shrink-0">
             <div className="flex items-center space-x-4">
               {/* Desktop Toggle */}
               <h2 
                 className={`hidden md:block text-4xl font-black transition-opacity duration-300 cursor-pointer hover:opacity-80 select-none ${activeTab === 'TIMELINE' ? 'text-transparent bg-clip-text bg-gradient-to-b from-[#00ff41] to-transparent opacity-80' : 'text-[#00ff41]/20'}`}
                 onClick={() => setActiveTab('TIMELINE')}
               >
                  TIMELINE
               </h2>
               <span className="hidden md:block text-[#00ff41]/20 text-4xl">/</span>
               <h2 
                 className={`hidden md:block text-4xl font-black transition-opacity duration-300 cursor-pointer hover:opacity-80 select-none ${activeTab === 'CALENDAR' ? 'text-transparent bg-clip-text bg-gradient-to-b from-[#00ff41] to-transparent opacity-80' : 'text-[#00ff41]/20'}`}
                 onClick={() => setActiveTab('CALENDAR')}
               >
                  PROPHECY
               </h2>
               
               {/* Mobile Header (Shows current active) */}
               <h2 className="md:hidden text-4xl font-black text-transparent bg-clip-text bg-gradient-to-b from-[#00ff41] to-transparent opacity-80">
                 {activeTab === 'CALENDAR' ? 'PROPHECY' : 'TIMELINE'}
               </h2>
             </div>

             <div className="text-right">
               <div className="text-[#00ff41] text-xs font-bold tracking-widest mb-1 flex items-center justify-end gap-2">
                 {isToday ? 'TODAY' : selectedDateStr} <CalendarClock className="w-3 h-3" />
               </div>
               {activeTab !== 'CALENDAR' && (
                  <div className="text-[#00ff41]/60 text-xs">{visibleTasks.length} ENTITIES</div>
               )}
            </div>
          </div>

          {/* Content Area */}
          <div className="flex-1 overflow-hidden relative">
            <AnimatePresence mode="wait">
              {activeTab === 'CALENDAR' ? (
                <motion.div
                  key="calendar"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.2 }}
                  className="h-full"
                >
                  <DoomsdayCalendar 
                      events={events} 
                      selectedDate={selectedDateStr} 
                      onSelectDate={(dateStr) => {
                        // Convert string date to Date object
                        // Parse the date components to avoid timezone issues
                        const parts = dateStr.split('-');
                        const year = parseInt(parts[0] || '0', 10);
                        const month = parseInt(parts[1] || '1', 10);
                        const day = parseInt(parts[2] || '1', 10);
                        const newDate = new Date(year, month - 1, day, 0, 0, 0, 0);
                        setSelectedDate(newDate);
                        // On mobile, switch back to timeline to see tasks
                        if (window.innerWidth < 768) {
                          setActiveTab('TIMELINE');
                        } else {
                           setActiveTab('TIMELINE'); // Auto switch on desktop too for flow
                        }
                      }} 
                  />
                </motion.div>
              ) : (
                <motion.div
                  key="timeline"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ duration: 0.2 }}
                  className="h-full overflow-y-auto pr-2 pb-20 mask-image-gradient"
                >
                  {eventsLoading ? (
                    <div className="h-40 flex flex-col items-center justify-center text-[#00ff41]/50">
                      <Loader2 className="w-8 h-8 animate-spin mb-2" />
                      <span className="text-sm tracking-wide">LOADING EVENTS...</span>
                    </div>
                  ) : visibleTasks.length === 0 ? (
                    <div className="h-40 flex flex-col items-center justify-center text-[#00ff41]/30 border border-[#00ff41]/10 border-dashed rounded-sm mt-4">
                      <span className="mb-2">NO ACTIVE HAUNTINGS FOR THIS DATE</span>
                      {!isToday && (
                        <button onClick={() => setSelectedDate(new Date())} className="text-xs hover:text-[#00ff41] underline">
                          Return to Present
                        </button>
                      )}
                    </div>
                  ) : (
                    visibleTasks.map((task) => (
                      <Monolith key={task.id} task={task} onBanish={handleBanishTask} onEdit={handleEditTask} />
                    ))
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </section>

      </main>

      {/* MOBILE NAVIGATION DOCK */}
      <nav className="fixed bottom-0 left-0 right-0 z-50 md:hidden flex bg-[#020202] border-t border-[#00ff41] pb-safe shadow-[0_-5px_20px_rgba(0,255,65,0.1)]">
        <button
          onClick={() => setActiveTab('UPLINK')}
          className={`
            flex-1 p-4 flex flex-col items-center justify-center gap-1 uppercase tracking-widest text-[10px] transition-all duration-200
            ${activeTab === 'UPLINK' 
              ? 'bg-[#00ff41]/10 text-[#00ff41] shadow-[inset_0_3px_0_#00ff41]' 
              : 'text-gray-600 hover:text-[#00ff41]/50'}
          `}
        >
          <MessageSquare className="w-5 h-5" />
          <span>Uplink</span>
        </button>
        <button
          onClick={() => setActiveTab('TIMELINE')}
          className={`
            flex-1 p-4 flex flex-col items-center justify-center gap-1 uppercase tracking-widest text-[10px] transition-all duration-200 relative
            ${activeTab === 'TIMELINE' 
              ? 'bg-[#00ff41]/10 text-[#00ff41] shadow-[inset_0_3px_0_#00ff41]' 
              : 'text-gray-600 hover:text-[#00ff41]/50'}
          `}
        >
          {upcomingCriticalTask && (
            <AlertCircle className="w-3 h-3 text-[#ff003c] absolute top-3 right-[35%] animate-pulse" />
          )}
          <List className="w-5 h-5" />
          <span>Timeline</span>
        </button>
        <button
          onClick={() => setActiveTab('CALENDAR')}
          className={`
            flex-1 p-4 flex flex-col items-center justify-center gap-1 uppercase tracking-widest text-[10px] transition-all duration-200 relative
            ${activeTab === 'CALENDAR' 
              ? 'bg-[#00ff41]/10 text-[#00ff41] shadow-[inset_0_3px_0_#00ff41]' 
              : 'text-gray-600 hover:text-[#00ff41]/50'}
          `}
        >
          <CalendarDays className="w-5 h-5" />
          <span>Prophecy</span>
        </button>
      </nav>
    </div>
  );
};

export default SeanceRoom;