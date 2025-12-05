import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';

interface TerminalInputProps {
  onSummon: (message: string) => void;
  isLoading: boolean;
}

const TerminalInput: React.FC<TerminalInputProps> = ({ onSummon, isLoading }) => {
  const [input, setInput] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSummon(input);
      setInput('');
    }
  };

  // Keep focus logic: Only aggressive on desktop to avoid mobile keyboard fighting
  useEffect(() => {
    const isMobile = window.innerWidth <= 768;
    if (isMobile) return;

    const keepFocus = () => inputRef.current?.focus();
    window.addEventListener('click', keepFocus);
    return () => window.removeEventListener('click', keepFocus);
  }, []);

  const placeholderText = isLoading ? "Establishing link..." : "Enter command...";

  return (
    <div className="w-full relative group">
      <form onSubmit={handleSubmit} className="relative">
        {/* Glowing Line Container */}
        <div className="relative flex items-center w-full">
          <span className="mr-2 md:mr-4 text-[#00ff41] animate-pulse whitespace-nowrap text-xs md:text-base">
            {isLoading ? 'COMMUNING...' : 'root@phantom:~$'}
          </span>
          
          <div className="relative flex-1">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isLoading}
              className="w-full bg-transparent border-b border-[#00ff41]/30 
                         text-[#00ff41] font-mono text-sm md:text-lg py-2 focus:outline-none 
                         focus:border-[#00ff41] focus:shadow-[0_4px_20px_rgba(0,255,65,0.2)]
                         transition-all duration-300 relative z-10
                         disabled:opacity-50 disabled:cursor-wait placeholder-transparent"
            />
            
            {/* Custom Animated Placeholder */}
            {input.length === 0 && (
              <motion.div
                initial={{ opacity: 0.5 }}
                animate={{ opacity: [0.4, 0.2, 0.6, 0.3, 0.5, 0.35] }}
                transition={{ 
                  duration: 3, 
                  repeat: Infinity, 
                  ease: "easeInOut",
                  times: [0, 0.2, 0.4, 0.6, 0.8, 1]
                }}
                className="absolute left-0 top-0 h-full flex items-center text-gray-600 font-mono text-sm md:text-lg pointer-events-none z-0 select-none"
              >
                {placeholderText} <span className="animate-pulse ml-1 text-[#00ff41]/50">_</span>
              </motion.div>
            )}
          </div>
        </div>

        {/* Typing Glow Effect */}
        {input.length > 0 && (
          <motion.div 
            layoutId="glow-line"
            className="absolute bottom-0 left-0 h-[1px] bg-[#00ff41] shadow-[0_0_10px_#00ff41]"
            style={{ width: '100%' }}
          />
        )}
      </form>
    </div>
  );
};

export default TerminalInput;