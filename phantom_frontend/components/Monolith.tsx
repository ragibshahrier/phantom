import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Task } from '../types';
import { AlertTriangle, Database, Edit2, Check, X, Skull, Trash2, ChevronDown } from 'lucide-react';

interface MonolithProps {
  task: Task;
  onBanish: (id: string) => void;
  onEdit: (task: Task) => void;
}

const Monolith: React.FC<MonolithProps> = ({ task, onBanish, onEdit }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [editForm, setEditForm] = useState({ 
    title: task.title, 
    description: task.description || '', 
    priority: task.priority 
  });
  
  // Use current form state for priority visual if editing, otherwise use props
  const currentPriority = isEditing ? editForm.priority : task.priority;
  const isCurrentlyCritical = currentPriority === 'CRITICAL';

  useEffect(() => {
    setEditForm({ 
      title: task.title, 
      description: task.description || '', 
      priority: task.priority 
    });
  }, [task]);

  const handleEditClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsEditing(true);
    setIsExpanded(true); // Force expand when editing
  };

  const handleSave = (e: React.MouseEvent) => {
    e.stopPropagation();
    onEdit({ 
      ...task, 
      title: editForm.title, 
      description: editForm.description, 
      priority: editForm.priority 
    });
    setIsEditing(false);
  };

  const handleCancel = (e: React.MouseEvent) => {
    e.stopPropagation();
    setEditForm({ 
      title: task.title, 
      description: task.description || '', 
      priority: task.priority 
    });
    setIsEditing(false);
  };

  const togglePriority = (e: React.MouseEvent) => {
    e.stopPropagation();
    setEditForm(prev => ({
      ...prev,
      priority: prev.priority === 'NORMAL' ? 'CRITICAL' : 'NORMAL'
    }));
  };

  const handleMainClick = () => {
    if (!isEditing) {
      setIsExpanded(!isExpanded);
    }
  };

  const handleBanish = (e: React.MouseEvent) => {
      e.stopPropagation();
      onBanish(task.id);
  }

  return (
    // LAYER 1: Layout & Entrance (Position in List)
    <motion.div
      layout
      initial={{ opacity: 0, y: 50, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9, transition: { duration: 0.2 } }}
      className="w-full mb-8 relative z-0"
    >
      {/* LAYER 2: Interaction (Hover Scale) */}
      <motion.div
        whileHover={!isEditing && !isExpanded ? { scale: 1.02, zIndex: 10 } : {}}
        className="relative w-full group"
      >
        {/* Horrific Banish Button (Desktop Hover) */}
        {!isEditing && (
             <button
                onClick={handleBanish}
                className="hidden md:flex absolute -top-3 -right-3 z-30 bg-black border border-[#ff003c] text-[#ff003c] p-2 rounded-full opacity-0 group-hover:opacity-100 transition-all duration-300 hover:scale-125 hover:shadow-[0_0_15px_#ff003c] items-center justify-center"
                title="BANISH_ENTITY"
             >
                 <Skull className="w-5 h-5 animate-pulse" />
             </button>
        )}

        {/* LAYER 3: Visuals & Continuous Animation */}
        <motion.div
            animate={
                isCurrentlyCritical && !isEditing
                ? { x: [-1, 1, -1, 1, 0] } 
                : { y: [0, -2, 0] }       
            }
            transition={{
                x: { duration: 0.4, repeat: Infinity, repeatDelay: 3 },
                y: { duration: 4, repeat: Infinity, ease: "easeInOut" }
            }}
            className={`
                relative w-full p-6
                border-l-4 backdrop-blur-md
                flex flex-col justify-between
                overflow-hidden transition-all duration-300
                ${isCurrentlyCritical 
                ? 'bg-red-900/10 border-[#ff003c] shadow-[0_0_15px_rgba(255,0,60,0.3)]' 
                : 'bg-green-900/10 border-[#00ff41] shadow-[0_0_10px_rgba(0,255,65,0.1)]'
                }
                ${isExpanded ? 'bg-opacity-20' : ''}
            `}
            onClick={handleMainClick}
            style={{ cursor: isEditing ? 'default' : 'pointer' }}
        >
            {/* Glass Reflection Highlight */}
            <div className="absolute top-0 right-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white/20 to-transparent" />
            
            {/* Subtle Inner Glow on Hover */}
            <div className={`absolute inset-0 opacity-0 group-hover:opacity-10 transition-opacity duration-300 pointer-events-none ${isCurrentlyCritical ? 'bg-red-500' : 'bg-green-500'}`} />

            {/* Header Section */}
            <div className="flex items-start justify-between mb-2 z-10 relative">
                <div className="flex items-center space-x-2">
                {isCurrentlyCritical ? (
                    <AlertTriangle className="w-4 h-4 text-[#ff003c] animate-pulse" />
                ) : (
                    <Database className="w-4 h-4 text-[#00ff41]" />
                )}
                <span className={`text-xs tracking-widest ${isCurrentlyCritical ? 'text-[#ff003c]' : 'text-[#00ff41]/70'}`}>
                    ID::{task.id}
                </span>
                </div>
                
                <div className="flex items-center space-x-3">
                {/* Action Buttons (Edit Mode) */}
                {isEditing ? (
                    <div className="flex space-x-2">
                    <button 
                        onClick={handleSave}
                        className="p-1 hover:bg-[#00ff41]/20 rounded text-[#00ff41] transition-colors"
                        title="Save Changes"
                    >
                        <Check className="w-4 h-4" />
                    </button>
                    <button 
                        onClick={handleCancel}
                        className="p-1 hover:bg-red-500/20 rounded text-red-500 transition-colors"
                        title="Cancel"
                    >
                        <X className="w-4 h-4" />
                    </button>
                    </div>
                ) : (
                    <motion.div 
                        animate={{ rotate: isExpanded ? 180 : 0 }}
                        className="text-[#00ff41]/50"
                    >
                        <ChevronDown className="w-4 h-4" />
                    </motion.div>
                )}
                </div>
            </div>

            {/* Time Display Section */}
            {!isEditing && (task.startTime || task.endTime) && (
                <div className={`flex items-center gap-3 mb-3 text-xs font-mono border-l-2 pl-3 ${isCurrentlyCritical ? 'border-[#ff003c]/50' : 'border-[#00ff41]/30'}`}>
                    {task.startTime && (
                        <div className="flex items-center gap-1">
                            <span className="text-gray-500">START:</span>
                            <span className={`font-bold ${isCurrentlyCritical ? 'text-[#ff003c]' : 'text-[#00ff41]'}`}>
                                {task.startTime}
                            </span>
                        </div>
                    )}
                    {task.endTime && (
                        <>
                            <span className="text-gray-600">→</span>
                            <div className="flex items-center gap-1">
                                <span className="text-gray-500">END:</span>
                                <span className={`font-bold ${isCurrentlyCritical ? 'text-[#ff003c]' : 'text-[#00ff41]'}`}>
                                    {task.endTime}
                                </span>
                            </div>
                        </>
                    )}
                    {task.duration && (
                        <>
                            <span className="text-gray-600">|</span>
                            <div className="flex items-center gap-1">
                                <span className="text-gray-500">DURATION:</span>
                                <span className="text-gray-300 font-bold">
                                    {task.duration}
                                </span>
                            </div>
                        </>
                    )}
                </div>
            )}

            {/* Content Section */}
            <div className="relative z-10 w-full">
                {isEditing ? (
                <div className="space-y-4">
                    {/* Edit Priority */}
                    <button
                    onClick={togglePriority}
                    className={`
                        text-[10px] font-bold border px-2 py-1 rounded transition-colors w-full md:w-auto
                        ${isCurrentlyCritical 
                        ? 'border-[#ff003c] text-[#ff003c] hover:bg-[#ff003c]/20' 
                        : 'border-[#00ff41] text-[#00ff41] hover:bg-[#00ff41]/20'}
                    `}
                    >
                    PRIORITY: {editForm.priority} [CLICK TO TOGGLE]
                    </button>

                    {/* Edit Title */}
                    <input 
                    type="text"
                    value={editForm.title}
                    onChange={(e) => setEditForm(prev => ({...prev, title: e.target.value}))}
                    onClick={(e) => e.stopPropagation()}
                    className={`
                        w-full bg-transparent border-b text-xl font-bold font-mono uppercase tracking-tighter focus:outline-none py-1
                        ${isCurrentlyCritical 
                        ? 'border-[#ff003c] text-[#ff003c] placeholder-[#ff003c]/50' 
                        : 'border-[#00ff41] text-[#00ff41] placeholder-[#00ff41]/50'}
                    `}
                    placeholder="TASK_TITLE"
                    autoFocus
                    />
                    
                    {/* Edit Description */}
                    <textarea
                    value={editForm.description}
                    onChange={(e) => setEditForm(prev => ({...prev, description: e.target.value}))}
                    onClick={(e) => e.stopPropagation()}
                    className="w-full bg-black/30 text-gray-300 text-sm font-mono border border-gray-700 p-2 focus:border-[#00ff41] outline-none min-h-[80px]"
                    placeholder="Task details..."
                    />
                </div>
                ) : (
                <>
                    <h3 
                    className={`
                        relative inline-block text-lg md:text-2xl font-bold font-mono uppercase tracking-tighter mb-2 z-20
                        ${isCurrentlyCritical ? 'text-[#ff003c] glitch-effect' : 'text-[#ccffda]'}
                    `}
                    data-text={task.title}
                    >
                    {task.title}
                    </h3>
                    
                    {/* Expandable Details */}
                    <AnimatePresence>
                        {isExpanded && (
                            <motion.div
                                initial={{ height: 0, opacity: 0 }}
                                animate={{ height: 'auto', opacity: 1 }}
                                exit={{ height: 0, opacity: 0 }}
                                className="overflow-hidden"
                            >
                                {task.description && (
                                    <p className="text-sm text-gray-400 font-mono leading-relaxed border-l border-gray-700 pl-3 mb-4">
                                        {task.description}
                                    </p>
                                )}
                                
                                {/* Action Bar for Mobile / Expanded View */}
                                <div className="flex items-center justify-between border-t border-gray-800 pt-3 mt-2">
                                    <button 
                                        onClick={handleEditClick}
                                        className="flex items-center gap-2 text-xs text-[#00ff41]/70 hover:text-[#00ff41] hover:underline"
                                    >
                                        <Edit2 className="w-3 h-3" /> REWRITE_CODE
                                    </button>
                                    
                                    <button
                                        onClick={handleBanish}
                                        className="flex items-center gap-2 text-xs text-[#ff003c]/70 hover:text-[#ff003c] hover:bg-[#ff003c]/10 px-2 py-1 rounded transition-colors"
                                    >
                                        <Trash2 className="w-3 h-3" /> PURGE
                                    </button>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </>
                )}
            </div>

            {/* Critical Glitch Overlay */}
            {isCurrentlyCritical && !isEditing && (
                <div className="absolute inset-0 pointer-events-none opacity-20 bg-[url('https://media.giphy.com/media/oEI9uBYSzLpBK/giphy.gif')] bg-cover mix-blend-overlay z-0" />
            )}
        </motion.div>
      </motion.div>
    </motion.div>
  );
};

export default Monolith;