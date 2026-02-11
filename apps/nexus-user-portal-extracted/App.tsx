import React, { useState } from 'react';
import { User, AppContext, SubscriptionTier } from './types';
import { Auth } from './components/Auth';
import { UserPortal } from './components/UserPortal';
import { DataSynthesis } from './components/DataSynthesis';
import { Observability } from './components/Observability';
import { Foundry } from './components/Foundry';
import { TopNav } from './components/TopNav';
import { CommandBar } from './components/CommandBar';

const App: React.FC = () => {
  // Hardwired default user for immediate access
  const [currentUser, setCurrentUser] = useState<User | null>({
    id: 'hardwired-1',
    firstName: 'Jeremy',
    lastName: 'Doe',
    email: 'jeremy@truthforge.ai',
    username: 'architect',
    address: '123 Forge Way',
    avatar: 'https://ui-avatars.com/api/?name=Jeremy+Doe&background=2D2D2D&color=F5F0E6',
    tier: SubscriptionTier.STAGE_3_FROZEN // Default to Stage 3
  });

  const [currentContext, setCurrentContext] = useState<AppContext>(AppContext.PORTAL);

  const handleLogin = (user: User) => {
    setCurrentUser(user);
    localStorage.setItem('nexus_user', JSON.stringify(user));
  };

  const handleLogout = () => {
    setCurrentUser(null);
    localStorage.removeItem('nexus_user');
  };

  const handleUpdateUser = (updatedUser: User) => {
    setCurrentUser(updatedUser);
    localStorage.setItem('nexus_user', JSON.stringify(updatedUser));
  };
  
  // Debug function to manually switch tiers
  const handleTierChange = (tier: SubscriptionTier) => {
      if (currentUser) {
          setCurrentUser({ ...currentUser, tier });
      }
  };

  if (!currentUser) {
      return (
        <div className="min-h-screen bg-[#0D0D0D] text-[#F5F0E6]">
            <Auth onLogin={handleLogin} />
        </div>
      );
  }

  return (
    <div className="h-screen bg-[#0D0D0D] text-[#F5F0E6] flex flex-col overflow-hidden">
      {/* Top Global Navigation */}
      <TopNav 
        currentContext={currentContext} 
        onContextChange={setCurrentContext} 
        user={currentUser} 
        onTierChange={handleTierChange}
      />

      {/* Main Application Area - Dynamic Switching */}
      <div className="flex-1 overflow-hidden relative">
          {currentContext === AppContext.PORTAL && (
              <UserPortal 
                  user={currentUser} 
                  onLogout={handleLogout} 
                  onUpdateUser={handleUpdateUser} 
              />
          )}
          {currentContext === AppContext.DATA_SYNTHESIS && (
              <DataSynthesis user={currentUser} />
          )}
          {currentContext === AppContext.FOUNDRY && (
              <Foundry user={currentUser} />
          )}
          {currentContext === AppContext.OBSERVABILITY && (
              <Observability user={currentUser} />
          )}
      </div>

      {/* Persistent Command Bar */}
      <CommandBar tier={currentUser.tier} />
    </div>
  );
};

export default App;