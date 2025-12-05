import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface GhostOverlayProps {
  isVisible: boolean;
}

const GhostOverlay: React.FC<GhostOverlayProps> = ({ isVisible }) => {
  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.1 }}
          className="fixed inset-0 z-[100] pointer-events-none flex items-center justify-center overflow-hidden"
        >
          {/* Red Flash Overlay */}
          <div className="absolute inset-0 bg-[#ff003c] mix-blend-multiply opacity-40 animate-pulse" />
          
          {/* Vignette Intensity */}
          <div className="absolute inset-0 bg-[radial-gradient(circle,transparent_0%,black_90%)]" />

          {/* Glitch Noise Texture */}
          <div className="absolute inset-0 opacity-20 bg-[url('https://media.giphy.com/media/oEI9uBYSzLpBK/giphy.gif')] bg-cover mix-blend-overlay" />

          {/* Horror Text */}
          <div className="relative z-10 text-center transform scale-150 md:scale-100">
             <motion.h1 
                initial={{ scale: 0.8, opacity: 0, y: 20 }}
                animate={{ scale: [1, 1.2, 1], opacity: 1, y: 0, x: [-5, 5, -5, 5, 0] }}
                exit={{ scale: 2, opacity: 0 }}
                className="text-6xl md:text-9xl font-black text-[#ff003c] tracking-tighter uppercase glitch-effect"
                data-text="FATE SEALED"
                style={{
                  textShadow: '4px 4px 0px #000, -2px -2px 0px #00ff41'
                }}
             >
               FATE SEALED
             </motion.h1>
             <motion.p 
               initial={{ opacity: 0 }}
               animate={{ opacity: 1 }}
               transition={{ delay: 0.2 }}
               className="text-white font-mono tracking-[0.5em] mt-4 bg-black inline-block px-2"
             >
               DO NOT RESIST
             </motion.p>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default GhostOverlay;