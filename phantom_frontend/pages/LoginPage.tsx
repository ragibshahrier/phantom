import React, { useState } from 'react';
import { motion } from 'framer-motion';
import CRTScanlines from '../components/CRTScanlines';
import { Skull, Lock, ChevronRight, Fingerprint, User } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');
  const [name, setName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [validationErrors, setValidationErrors] = useState<{ username?: string; password?: string; passwordConfirm?: string; name?: string }>({});
  const [mode, setMode] = useState<'LOGIN' | 'REGISTER'>('LOGIN');
  const [successMessage, setSuccessMessage] = useState('');

  const { login, register } = useAuth();

  // Client-side validation
  const validateForm = (): boolean => {
    const errors: { username?: string; password?: string; passwordConfirm?: string; name?: string } = {};

    // Validate username length (minimum 3 characters)
    if (username.trim().length < 3) {
      errors.username = 'USERNAME_TOO_SHORT: MIN_3_CHARS';
    }

    // Validate password length (minimum 8 characters)
    if (password.length < 8) {
      errors.password = 'PASSWORD_TOO_SHORT: MIN_8_CHARS';
    }

    // Validate name for registration mode
    if (mode === 'REGISTER' && name.trim().length === 0) {
      errors.name = 'NAME_REQUIRED';
    }

    // Validate password confirmation for registration mode
    if (mode === 'REGISTER' && password !== passwordConfirm) {
      errors.passwordConfirm = 'PASSWORDS_DO_NOT_MATCH';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccessMessage('');
    setValidationErrors({});
    
    // Validate empty required fields
    if (!username.trim() || !password.trim() || (mode === 'REGISTER' && (!name.trim() || !passwordConfirm.trim()))) {
      setError('ALL_FIELDS_REQUIRED');
      return;
    }

    // Run client-side validation
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      if (mode === 'LOGIN') {
        // Call real login function
        const result = await login(username, password);
        
        if (result.success) {
          // Successful login - AuthContext will handle state update
          // The App component will detect isAuthenticated and show SeanceRoom
        } else {
          // Display backend error message
          setError(result.error || 'LOGIN_FAILED');
        }
      } else {
        // Call real register function
        const result = await register(username, name, password, passwordConfirm);
        
        if (result.success) {
          // Display success message and redirect to login form
          setSuccessMessage('REGISTRATION_SUCCESSFUL: PROCEED_TO_LOGIN');
          setMode('LOGIN');
          setPassword('');
          setPasswordConfirm('');
          setName('');
        } else {
          // Display backend error message
          setError(result.error || 'REGISTRATION_FAILED');
        }
      }
    } catch (err: any) {
      // Handle unexpected errors
      setError(err.message || 'SYSTEM_ERROR: TRY_AGAIN');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative w-full h-screen bg-[#020202] text-[#00ff41] font-mono flex items-center justify-center overflow-hidden">
      <CRTScanlines />
      
      {/* Background Glitch Text */}
      <div className="absolute inset-0 pointer-events-none z-0 flex items-center justify-center opacity-5">
        <h1 className="text-9xl font-black rotate-90 md:rotate-0 tracking-tighter">PHANTOM</h1>
      </div>

      <motion.div 
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="relative z-10 w-full max-w-md p-8 bg-black/80 border border-[#00ff41]/30 backdrop-blur-md shadow-[0_0_50px_rgba(0,255,65,0.1)]"
      >
        {/* Header */}
        <div className="text-center mb-10 relative">
          <motion.div
            animate={{ rotate: [0, 5, -5, 0] }}
            transition={{ duration: 0.5, repeat: Infinity, repeatDelay: 5 }}
            className="inline-block mb-4"
          >
            <Skull className="w-12 h-12 text-[#00ff41] mx-auto" />
          </motion.div>
          <h2 className="text-3xl font-bold tracking-[0.2em] glitch-effect" data-text="PHANTOM_OS">
            PHANTOM_OS
          </h2>
          <p className="text-xs text-[#00ff41]/50 mt-2 tracking-widest">
            {mode === 'LOGIN' ? 'AUTHENTICATION_REQUIRED' : 'NEW_SOUL_REGISTRATION'}
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label className="text-xs font-bold flex items-center gap-2">
              <Fingerprint className="w-3 h-3" /> USERNAME
            </label>
            <div className="relative">
                <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    disabled={isLoading}
                    className={`w-full bg-black/50 border-b p-2 text-lg focus:outline-none focus:bg-[#00ff41]/10 transition-all placeholder-[#00ff41]/20 ${
                      validationErrors.username ? 'border-[#ff003c]' : 'border-[#00ff41]/50 focus:border-[#00ff41]'
                    }`}
                    placeholder="ENTER_ID"
                    autoFocus
                />
            </div>
            {validationErrors.username && (
              <motion.div 
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="text-[#ff003c] text-xs font-bold"
              >
                  {validationErrors.username}
              </motion.div>
            )}
          </div>

          {mode === 'REGISTER' && (
            <div className="space-y-2">
              <label className="text-xs font-bold flex items-center gap-2">
                <User className="w-3 h-3" /> FULL NAME
              </label>
              <div className="relative">
                  <input
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      disabled={isLoading}
                      className={`w-full bg-black/50 border-b p-2 text-lg focus:outline-none focus:bg-[#00ff41]/10 transition-all placeholder-[#00ff41]/20 ${
                        validationErrors.name ? 'border-[#ff003c]' : 'border-[#00ff41]/50 focus:border-[#00ff41]'
                      }`}
                      placeholder="ENTER_NAME"
                  />
              </div>
              {validationErrors.name && (
                <motion.div 
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="text-[#ff003c] text-xs font-bold"
                >
                    {validationErrors.name}
                </motion.div>
              )}
            </div>
          )}

          <div className="space-y-2">
            <label className="text-xs font-bold flex items-center gap-2">
              <Lock className="w-3 h-3" /> PASSWORD
            </label>
            <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading}
                className={`w-full bg-black/50 border-b p-2 text-lg focus:outline-none focus:bg-[#00ff41]/10 transition-all placeholder-[#00ff41]/20 ${
                  validationErrors.password ? 'border-[#ff003c]' : 'border-[#00ff41]/50 focus:border-[#00ff41]'
                }`}
                placeholder="••••••"
            />
            {validationErrors.password && (
              <motion.div 
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="text-[#ff003c] text-xs font-bold"
              >
                  {validationErrors.password}
              </motion.div>
            )}
          </div>

          {mode === 'REGISTER' && (
            <div className="space-y-2">
              <label className="text-xs font-bold flex items-center gap-2">
                <Lock className="w-3 h-3" /> CONFIRM PASSWORD
              </label>
              <input
                  type="password"
                  value={passwordConfirm}
                  onChange={(e) => setPasswordConfirm(e.target.value)}
                  disabled={isLoading}
                  className={`w-full bg-black/50 border-b p-2 text-lg focus:outline-none focus:bg-[#00ff41]/10 transition-all placeholder-[#00ff41]/20 ${
                    validationErrors.passwordConfirm ? 'border-[#ff003c]' : 'border-[#00ff41]/50 focus:border-[#00ff41]'
                  }`}
                  placeholder="••••••"
              />
              {validationErrors.passwordConfirm && (
                <motion.div 
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="text-[#ff003c] text-xs font-bold"
                >
                    {validationErrors.passwordConfirm}
                </motion.div>
              )}
            </div>
          )}

          {successMessage && (
            <motion.div 
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="text-[#00ff41] text-xs font-bold border-l-2 border-[#00ff41] pl-2"
            >
                SUCCESS:: {successMessage}
            </motion.div>
          )}

          {error && (
            <motion.div 
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="text-[#ff003c] text-xs font-bold border-l-2 border-[#ff003c] pl-2"
            >
                ERROR:: {error}
            </motion.div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className={`
                w-full py-4 bg-[#00ff41]/10 border border-[#00ff41] text-[#00ff41] font-bold tracking-widest hover:bg-[#00ff41] hover:text-black transition-all flex items-center justify-center gap-2 group
                ${isLoading ? 'opacity-50 cursor-wait' : ''}
            `}
          >
            {isLoading ? (
                <span className="animate-pulse">DECRYPTING...</span>
            ) : (
                <>
                    {mode === 'LOGIN' ? 'ACCESS_SYSTEM' : 'INITIATE_BOND'} 
                    <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </>
            )}
          </button>
        </form>

        {/* Footer Toggle */}
        <div className="mt-8 text-center border-t border-[#00ff41]/20 pt-4">
            <button 
                onClick={() => {
                    setMode(mode === 'LOGIN' ? 'REGISTER' : 'LOGIN');
                    setError('');
                    setSuccessMessage('');
                    setValidationErrors({});
                    setPasswordConfirm('');
                }}
                className="text-xs text-[#00ff41]/60 hover:text-[#00ff41] underline decoration-dashed underline-offset-4"
                disabled={isLoading}
            >
                {mode === 'LOGIN' ? 'NO_ID? REGISTER_SOUL' : 'HAS_ID? ACCESS_LOG'}
            </button>
        </div>

        {/* Decorative Corner Borders */}
        <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-[#00ff41]" />
        <div className="absolute top-0 right-0 w-4 h-4 border-t border-r border-[#00ff41]" />
        <div className="absolute bottom-0 left-0 w-4 h-4 border-b border-l border-[#00ff41]" />
        <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-[#00ff41]" />
      </motion.div>
    </div>
  );
};

export default LoginPage;