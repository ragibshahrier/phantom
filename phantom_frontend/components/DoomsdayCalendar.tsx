
import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon } from 'lucide-react';
import { motion } from 'framer-motion';
import { Event } from '../types';

interface DoomsdayCalendarProps {
  events: Event[];
  selectedDate: string;
  onSelectDate: (date: string) => void;
}

const DoomsdayCalendar: React.FC<DoomsdayCalendarProps> = ({ events, selectedDate, onSelectDate }) => {
  // Helper function to format date as YYYY-MM-DD in local timezone
  const formatDateLocal = (date: Date): string => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  const [currentDate, setCurrentDate] = useState(() => {
    const d = new Date(selectedDate);
    return isNaN(d.getTime()) ? new Date() : d;
  });

  const getDaysInMonth = (year: number, month: number) => {
    return new Date(year, month + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (year: number, month: number) => {
    return new Date(year, month, 1).getDay();
  };

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();
  const daysInMonth = getDaysInMonth(year, month);
  const firstDay = getFirstDayOfMonth(year, month);

  const prevMonth = () => {
    const newDate = new Date(year, month - 1, 1);
    setCurrentDate(newDate);
    // Maintain selected date if it exists in the new month, otherwise select the 1st
    const selectedDay = parseInt(selectedDate.split('-')[2] || '1');
    const daysInNewMonth = getDaysInMonth(newDate.getFullYear(), newDate.getMonth());
    const dayToSelect = Math.min(selectedDay, daysInNewMonth);
    const newSelectedDate = `${newDate.getFullYear()}-${String(newDate.getMonth() + 1).padStart(2, '0')}-${String(dayToSelect).padStart(2, '0')}`;
    onSelectDate(newSelectedDate);
  };

  const nextMonth = () => {
    const newDate = new Date(year, month + 1, 1);
    setCurrentDate(newDate);
    // Maintain selected date if it exists in the new month, otherwise select the 1st
    const selectedDay = parseInt(selectedDate.split('-')[2] || '1');
    const daysInNewMonth = getDaysInMonth(newDate.getFullYear(), newDate.getMonth());
    const dayToSelect = Math.min(selectedDay, daysInNewMonth);
    const newSelectedDate = `${newDate.getFullYear()}-${String(newDate.getMonth() + 1).padStart(2, '0')}-${String(dayToSelect).padStart(2, '0')}`;
    onSelectDate(newSelectedDate);
  };

  const monthNames = [
    "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE",
    "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"
  ];

  const days = [];
  for (let i = 0; i < firstDay; i++) {
    days.push(<div key={`empty-${i}`} className="p-2" />);
  }
  
  for (let i = 1; i <= daysInMonth; i++) {
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`;
    
    // Filter events that occur on this date
    // An event occurs on a date if its start_time or any part of its duration falls on that date
    const dayEvents = events.filter(event => {
      const eventStartDate = event.start_time.split('T')[0] || '';
      const eventEndDate = event.end_time.split('T')[0] || '';
      // Event is on this date if it starts on this date or spans across this date
      return eventStartDate === dateStr || 
             (eventStartDate <= dateStr && eventEndDate >= dateStr);
    });
    
    const hasCritical = dayEvents.some(e => e.priority_level === 5);
    const hasNormal = dayEvents.some(e => e.priority_level < 5);
    const isSelected = selectedDate === dateStr;
    const isToday = dateStr === formatDateLocal(new Date());

    days.push(
      <motion.button
        key={dateStr}
        whileHover={{ scale: 1.05, backgroundColor: 'rgba(0, 255, 65, 0.1)' }}
        whileTap={{ scale: 0.95 }}
        onClick={() => onSelectDate(dateStr)}
        className={`
            relative p-2 h-16 md:h-24 w-full flex flex-col items-start justify-start rounded-sm transition-all border
            ${isSelected ? 'bg-[#00ff41]/20 border-[#00ff41] shadow-[0_0_10px_rgba(0,255,65,0.3)]' : 'border-white/5 hover:border-[#00ff41]/30 bg-black/40'}
            ${isToday ? 'text-white font-bold bg-[#00ff41]/5' : 'text-gray-400'}
        `}
      >
        <span className={`text-sm md:text-lg mb-1 ${isToday && !isSelected ? 'text-[#00ff41]' : ''}`}>{i}</span>
        
        {/* Event Indicators */}
        <div className="flex flex-wrap gap-1 mt-auto w-full">
            {hasCritical && (
                <div className="w-full h-1.5 bg-[#ff003c] animate-pulse shadow-[0_0_5px_#ff003c]" title="Critical Event" />
            )}
            {hasNormal && (
                 <div className="w-full h-1.5 bg-[#00ff41]/50" title="Event" />
            )}
            {dayEvents.length > 2 && (
              <div className="w-full h-1.5 bg-gray-600" title="More..." />
            )}
        </div>

        {/* Today Corner Marker */}
        {isToday && (
            <div className="absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 border-[#00ff41]" />
        )}
      </motion.button>
    );
  }

  return (
    <div className="w-full h-full flex flex-col">
      {/* Calendar Header */}
      <div className="flex justify-between items-center mb-6 p-4 bg-[#001100]/50 border border-[#00ff41]/20">
        <button onClick={prevMonth} className="p-2 hover:text-[#00ff41] hover:bg-white/5 rounded transition-colors">
            <ChevronLeft className="w-6 h-6" />
        </button>
        <div className="text-[#00ff41] font-bold tracking-[0.2em] text-xl flex items-center gap-2">
            <CalendarIcon className="w-5 h-5" />
            {monthNames[month]} {year}
        </div>
        <button onClick={nextMonth} className="p-2 hover:text-[#00ff41] hover:bg-white/5 rounded transition-colors">
            <ChevronRight className="w-6 h-6" />
        </button>
      </div>

      {/* Days Header */}
      <div className="grid grid-cols-7 gap-1 mb-2 text-center border-b border-[#00ff41]/20 pb-2">
        {['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'].map((d, i) => (
            <div key={i} className="text-xs md:text-sm text-[#00ff41]/60 tracking-wider font-bold">{d}</div>
        ))}
      </div>

      {/* Calendar Grid */}
      <div className="grid grid-cols-7 gap-1 md:gap-2 flex-1 overflow-y-auto">
        {days}
      </div>
    </div>
  );
};

export default DoomsdayCalendar;
