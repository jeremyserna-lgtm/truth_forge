import React, { useState, useRef } from 'react';
import { User } from '../../types';
import { Button } from '../Button';
import { Input } from '../Input';
import { User as UserIcon, Mail, MapPin, AtSign, Save, Camera, Lock, AlertCircle } from 'lucide-react';

interface AccountSettingsProps {
  user: User;
  onUpdateUser: (updatedUser: User) => void;
}

export const AccountSettings: React.FC<AccountSettingsProps> = ({ user, onUpdateUser }) => {
  const [formData, setFormData] = useState<User>(user);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Change Password State
  const [passwordForm, setPasswordForm] = useState({
      current: '',
      new: '',
      confirm: ''
  });
  const [passwordMessage, setPasswordMessage] = useState<{type: 'success' | 'error', text: string} | null>(null);
  const [passwordLoading, setPasswordLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const { name, value } = e.target;
      setPasswordForm(prev => ({ ...prev, [name]: value }));
  };

  const handleSaveProfile = () => {
    setIsSaving(true);
    // Simulate API save
    setTimeout(() => {
      onUpdateUser(formData);
      setIsEditing(false);
      setIsSaving(false);
    }, 800);
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
          const reader = new FileReader();
          reader.onloadend = () => {
              const base64String = reader.result as string;
              setFormData(prev => ({ ...prev, avatar: base64String }));
              // Auto save avatar update for better UX or wait for main save
              // Choosing to auto-update local state immediately, user must click save to persist
              setIsEditing(true); 
          };
          reader.readAsDataURL(file);
      }
  };

  const handleSubmitPasswordChange = (e: React.FormEvent) => {
      e.preventDefault();
      setPasswordMessage(null);
      if (passwordForm.new !== passwordForm.confirm) {
          setPasswordMessage({ type: 'error', text: 'New passwords do not match.' });
          return;
      }
      if (passwordForm.new.length < 6) {
        setPasswordMessage({ type: 'error', text: 'Password must be at least 6 characters.' });
        return;
      }

      setPasswordLoading(true);
      setTimeout(() => {
          setPasswordLoading(false);
          setPasswordMessage({ type: 'success', text: 'Credentials updated successfully.' });
          setPasswordForm({ current: '', new: '', confirm: '' });
      }, 1000);
  };

  const handleCancel = () => {
    setFormData(user);
    setIsEditing(false);
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      
      {/* SECTION: IDENTITY */}
      <div className="bg-[#1A1A1A] border border-[#2D2D2D] rounded-sm overflow-hidden">
        <div className="px-6 py-5 border-b border-[#2D2D2D] flex items-center justify-between">
            <div>
                <h3 className="text-xl font-serif text-[#F5F0E6] uppercase tracking-wide">Identity Matrix</h3>
                <p className="text-xs font-mono text-[#888888] mt-1">Manage public facing persona details</p>
            </div>
            <div className="flex space-x-3">
                {isEditing ? (
                    <>
                    <Button variant="secondary" size="sm" onClick={handleCancel} disabled={isSaving}>
                        Revert
                    </Button>
                    <Button size="sm" onClick={handleSaveProfile} isLoading={isSaving} icon={<Save size={14} />}>
                        Commit
                    </Button>
                    </>
                ) : (
                    <Button variant="secondary" size="sm" onClick={() => setIsEditing(true)}>
                    Edit Identity
                    </Button>
                )}
            </div>
        </div>

        <div className="p-8">
            <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
                {/* Avatar Column */}
                <div className="md:col-span-4 flex flex-col items-center space-y-6">
                    <div className="relative group">
                        <div className="w-40 h-40 rounded-sm overflow-hidden border-2 border-[#2D2D2D] group-hover:border-[#F5F0E6] transition-colors relative">
                            <img 
                                src={formData.avatar || `https://ui-avatars.com/api/?name=${formData.firstName}+${formData.lastName}&background=2D2D2D&color=F5F0E6`} 
                                alt="Profile" 
                                className="w-full h-full object-cover"
                            />
                            {/* Overlay for upload */}
                            {isEditing && (
                                <div 
                                    className="absolute inset-0 bg-black/60 flex flex-col items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer"
                                    onClick={() => fileInputRef.current?.click()}
                                >
                                    <Camera className="text-[#F5F0E6] mb-1" size={24} />
                                    <span className="text-[#F5F0E6] text-xs font-mono uppercase">Update</span>
                                </div>
                            )}
                            <input 
                                type="file" 
                                ref={fileInputRef} 
                                className="hidden" 
                                accept="image/*"
                                onChange={handleImageUpload}
                            />
                        </div>
                    </div>
                    <div className="text-center">
                        <div className="font-mono text-xs text-[#888888] uppercase tracking-wider mb-1">Subject ID</div>
                        <div className="font-mono text-sm text-[#F5F0E6] bg-[#0D0D0D] px-3 py-1 rounded-sm border border-[#2D2D2D] inline-block">
                            {user.id}
                        </div>
                    </div>
                </div>

                {/* Fields Column */}
                <div className="md:col-span-8 space-y-5">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                        <Input
                            label="First Name"
                            name="firstName"
                            value={formData.firstName}
                            onChange={handleChange}
                            disabled={!isEditing}
                        />
                        <Input
                            label="Last Name"
                            name="lastName"
                            value={formData.lastName}
                            onChange={handleChange}
                            disabled={!isEditing}
                        />
                    </div>

                    <Input
                        label="Primary Email"
                        name="email"
                        type="email"
                        value={formData.email}
                        onChange={handleChange}
                        disabled={!isEditing}
                        icon={<Mail size={16} />}
                        helperText="Used for system notifications and recovery."
                    />

                    <Input
                        label="Username"
                        name="username"
                        value={formData.username}
                        onChange={handleChange}
                        disabled={!isEditing}
                        icon={<AtSign size={16} />}
                    />

                    <Input
                        label="Physical Address"
                        name="address"
                        value={formData.address}
                        onChange={handleChange}
                        disabled={!isEditing}
                        icon={<MapPin size={16} />}
                    />
                </div>
            </div>
        </div>
      </div>

      {/* SECTION: CREDENTIALS */}
      <div className="bg-[#1A1A1A] border border-[#2D2D2D] rounded-sm overflow-hidden">
          <div className="px-6 py-5 border-b border-[#2D2D2D]">
            <h3 className="text-xl font-serif text-[#F5F0E6] uppercase tracking-wide">Security Protocols</h3>
            <p className="text-xs font-mono text-[#888888] mt-1">Update access credentials</p>
          </div>
          
          <div className="p-8">
              <form onSubmit={handleSubmitPasswordChange} className="max-w-2xl">
                {passwordMessage && (
                    <div className={`mb-6 p-3 flex items-center space-x-3 text-xs font-mono uppercase tracking-wide border ${passwordMessage.type === 'success' ? 'bg-green-900/10 border-green-900/30 text-green-400' : 'bg-red-900/10 border-red-900/30 text-red-400'}`}>
                        <AlertCircle size={16} />
                        <span>{passwordMessage.text}</span>
                    </div>
                )}
                
                <div className="space-y-5">
                    <Input 
                        label="Current Password"
                        type="password"
                        name="current"
                        value={passwordForm.current}
                        onChange={handlePasswordChange}
                        icon={<Lock size={16} />}
                    />
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                        <Input 
                            label="New Password"
                            type="password"
                            name="new"
                            value={passwordForm.new}
                            onChange={handlePasswordChange}
                        />
                         <Input 
                            label="Confirm New Password"
                            type="password"
                            name="confirm"
                            value={passwordForm.confirm}
                            onChange={handlePasswordChange}
                        />
                    </div>

                    <div className="pt-2">
                        <Button type="submit" isLoading={passwordLoading}>
                            Update Password
                        </Button>
                    </div>
                </div>
              </form>
          </div>
      </div>
    </div>
  );
};