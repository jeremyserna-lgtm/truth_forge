import React, { useState } from 'react';
import { User, SubscriptionTier } from '../types';
import { Button } from './Button';
import { Input } from './Input';
import { User as UserIcon, Lock, Mail, MapPin, ArrowLeft, ArrowRight } from 'lucide-react';

interface AuthProps {
  onLogin: (user: User) => void;
}

type AuthView = 'LOGIN' | 'SIGNUP' | 'FORGOT_PASSWORD' | 'RESET_PASSWORD';

export const Auth: React.FC<AuthProps> = ({ onLogin }) => {
  const [view, setView] = useState<AuthView>('LOGIN');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  // Form State
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [username, setUsername] = useState('');
  const [address, setAddress] = useState('');
  
  // Reset Password State
  const [resetCode, setResetCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmNewPassword, setConfirmNewPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    // Simulate API call
    setTimeout(() => {
      const mockUser: User = {
        id: '12345',
        firstName: firstName || 'Jeremy',
        lastName: lastName || 'Doe',
        email: email || 'jeremy@truthforge.ai',
        username: username || 'architect',
        address: address || '123 Forge Way',
        avatar: `https://ui-avatars.com/api/?name=${(firstName || 'J')}+${(lastName || 'D')}&background=F5F0E6&color=0D0D0D`,
        tier: SubscriptionTier.STAGE_3_FROZEN
      };
      
      onLogin(mockUser);
      setLoading(false);
    }, 1000);
  };

  const handleForgotPassword = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    // Simulate sending email
    setTimeout(() => {
        setLoading(false);
        setMessage({ type: 'success', text: `Recovery code sent to ${email}` });
        setView('RESET_PASSWORD');
    }, 1000);
  };

  const handleResetPassword = (e: React.FormEvent) => {
      e.preventDefault();
      if (newPassword !== confirmNewPassword) {
          setMessage({ type: 'error', text: 'Passwords do not match.' });
          return;
      }
      setLoading(true);
      // Simulate password reset
      setTimeout(() => {
          setLoading(false);
          setMessage({ type: 'success', text: 'Password reset successfully. Please login.' });
          setView('LOGIN');
          setNewPassword('');
          setConfirmNewPassword('');
          setResetCode('');
      }, 1000);
  };

  const renderHeader = () => {
      switch(view) {
          case 'LOGIN': return { title: 'Authentic Identity', subtitle: 'Enter the forge.' };
          case 'SIGNUP': return { title: 'Join the Source', subtitle: 'Create your permanent record.' };
          case 'FORGOT_PASSWORD': return { title: 'Recover Access', subtitle: 'We will send a verification code.' };
          case 'RESET_PASSWORD': return { title: 'New Credentials', subtitle: 'Secure your account.' };
      }
  };

  const headerContent = renderHeader();

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-[#0D0D0D] relative overflow-hidden">
      {/* Texture Background */}
      <div className="absolute inset-0 opacity-20 pointer-events-none" style={{ backgroundImage: 'url("https://www.transparenttextures.com/patterns/stardust.png")' }}></div>
      
      <div className="max-w-md w-full bg-[#1A1A1A] border border-[#2D2D2D] shadow-2xl relative z-10">
        {/* Header */}
        <div className="px-8 pt-10 pb-6 text-center border-b border-[#2D2D2D]">
          <div className="inline-block mb-4">
             {/* Logo Image */}
             <img src="./truth_forge_logo.png" alt="Truth Forge" className="h-16 w-16 mx-auto object-contain" />
          </div>
          <h2 className="text-4xl font-serif text-[#F5F0E6] tracking-wide uppercase">
            {headerContent.title}
          </h2>
          <p className="mt-3 text-sm font-mono text-[#888888] uppercase tracking-wider">
            {headerContent.subtitle}
          </p>
        </div>

        {/* Message Banner */}
        {message && (
            <div className={`px-8 py-3 text-xs font-mono uppercase tracking-wide text-center ${message.type === 'success' ? 'bg-green-900/20 text-green-400' : 'bg-red-900/20 text-red-400'}`}>
                {message.text}
            </div>
        )}

        {/* Form Container */}
        <div className="px-8 py-8">
            
          {/* LOGIN & SIGNUP VIEWS */}
          {(view === 'LOGIN' || view === 'SIGNUP') && (
            <form onSubmit={handleSubmit} className="space-y-5">
                {view === 'SIGNUP' && (
                <div className="grid grid-cols-2 gap-4">
                    <Input
                    label="First Name"
                    placeholder="JEREMY"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    required
                    />
                    <Input
                    label="Last Name"
                    placeholder="DOE"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    required
                    />
                </div>
                )}

                {view === 'SIGNUP' && (
                <Input
                label="Username"
                icon={<UserIcon size={16} />}
                placeholder="ARCHITECT"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                />
                )}

                <Input
                label="Email Address"
                type="email"
                icon={<Mail size={16} />}
                placeholder="YOU@TRUTHFORGE.AI"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                />
                
                {view === 'SIGNUP' && (
                <Input
                label="Address"
                icon={<MapPin size={16} />}
                placeholder="123 MAIN ST"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                />
                )}

                <div className="space-y-1">
                    <Input
                    label="Password"
                    type="password"
                    icon={<Lock size={16} />}
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    />
                    {view === 'LOGIN' && (
                        <div className="flex justify-end">
                            <button 
                                type="button" 
                                onClick={() => { setView('FORGOT_PASSWORD'); setMessage(null); }}
                                className="text-xs font-mono text-[#888888] hover:text-[#F5F0E6] uppercase tracking-wider mt-2 transition-colors"
                            >
                                Forgot Password?
                            </button>
                        </div>
                    )}
                </div>

                <div className="pt-4">
                <Button type="submit" fullWidth isLoading={loading} size="md">
                    {view === 'LOGIN' ? 'Enter Portal' : 'Initialize Account'}
                </Button>
                </div>
            </form>
          )}

          {/* FORGOT PASSWORD VIEW */}
          {view === 'FORGOT_PASSWORD' && (
              <form onSubmit={handleForgotPassword} className="space-y-6">
                  <Input
                    label="Email Address"
                    type="email"
                    icon={<Mail size={16} />}
                    placeholder="YOU@EXAMPLE.COM"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    helperText="Enter your verified email address to receive a reset code."
                  />
                  <div className="pt-2 space-y-3">
                    <Button type="submit" fullWidth isLoading={loading}>
                        Send Verification
                    </Button>
                    <Button type="button" variant="secondary" fullWidth onClick={() => { setView('LOGIN'); setMessage(null); }} icon={<ArrowLeft size={16}/>}>
                        Back to Login
                    </Button>
                  </div>
              </form>
          )}

          {/* RESET PASSWORD VIEW */}
          {view === 'RESET_PASSWORD' && (
              <form onSubmit={handleResetPassword} className="space-y-5">
                   <Input
                    label="Verification Code"
                    placeholder="123456"
                    value={resetCode}
                    onChange={(e) => setResetCode(e.target.value)}
                    required
                    icon={<Lock size={16} />}
                  />
                  <Input
                    label="New Password"
                    type="password"
                    placeholder="••••••••"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    required
                  />
                  <Input
                    label="Confirm Password"
                    type="password"
                    placeholder="••••••••"
                    value={confirmNewPassword}
                    onChange={(e) => setConfirmNewPassword(e.target.value)}
                    required
                  />
                  <div className="pt-2">
                    <Button type="submit" fullWidth isLoading={loading}>
                        Update Credentials
                    </Button>
                  </div>
              </form>
          )}

          {/* Footer Links */}
          {(view === 'LOGIN' || view === 'SIGNUP') && (
            <div className="mt-8 pt-6 border-t border-[#2D2D2D] text-center">
                <p className="text-xs font-mono text-[#888888] uppercase tracking-wider">
                {view === 'LOGIN' ? "No credentials? " : "Existing entity? "}
                <button
                    type="button"
                    onClick={() => { setView(view === 'LOGIN' ? 'SIGNUP' : 'LOGIN'); setMessage(null); }}
                    className="text-[#F5F0E6] hover:text-white underline decoration-[#4A4A4A] underline-offset-4 hover:decoration-[#F5F0E6] transition-all ml-1"
                >
                    {view === 'LOGIN' ? 'Initialize' : 'Authenticate'}
                </button>
                </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};