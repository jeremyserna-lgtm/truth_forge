import React, { useState } from 'react';
import { User, DashboardTab } from '../types';
import { AccountSettings } from './views/AccountSettings';
import { User as UserIcon, Shield, Bell, CreditCard, LogOut, LayoutDashboard, ChevronRight } from 'lucide-react';

interface DashboardProps {
  user: User;
  onLogout: () => void;
  onUpdateUser: (user: User) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ user, onLogout, onUpdateUser }) => {
  const [activeTab, setActiveTab] = useState<DashboardTab>(DashboardTab.ACCOUNT);

  // Tab configuration
  const tabs = [
    { id: DashboardTab.ACCOUNT, label: 'Account Info', icon: <UserIcon size={16} /> },
    { id: DashboardTab.SECURITY, label: 'Security', icon: <Shield size={16} /> },
    { id: DashboardTab.NOTIFICATIONS, label: 'Notifications', icon: <Bell size={16} /> },
    { id: DashboardTab.BILLING, label: 'Billing & Plans', icon: <CreditCard size={16} /> },
  ];

  const renderContent = () => {
    switch (activeTab) {
      case DashboardTab.ACCOUNT:
        return <AccountSettings user={user} onUpdateUser={onUpdateUser} />;
      case DashboardTab.SECURITY:
      case DashboardTab.NOTIFICATIONS:
      case DashboardTab.BILLING:
        return (
          <div className="flex flex-col items-center justify-center h-full text-center p-12">
            <div className="w-16 h-16 bg-[#1A1A1A] rounded-full flex items-center justify-center mb-6 border border-[#2D2D2D]">
                <LayoutDashboard size={32} className="text-[#4A4A4A]" />
            </div>
            <h3 className="text-2xl font-serif text-[#F5F0E6] mb-2">Module Offline</h3>
            <p className="max-w-md text-[#888888] font-mono text-sm">
              This system component is currently under development. Access restricted.
            </p>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="flex h-screen bg-[#0D0D0D] overflow-hidden">
      {/* Vertical Sidebar */}
      <div className="w-72 bg-[#1A1A1A] border-r border-[#2D2D2D] flex flex-col flex-shrink-0 z-20">
        <div className="h-20 flex items-center px-6 border-b border-[#2D2D2D]">
           {/* Logo Image */}
           <img src="./truth_forge_logo.png" alt="Truth Forge" className="h-10 w-10 mr-4 object-contain" />
           <div>
               <span className="block font-serif text-xl text-[#F5F0E6] tracking-wide uppercase leading-none">Truth Forge</span>
               <span className="block font-mono text-[10px] text-[#888888] uppercase tracking-[0.2em] mt-1">User Portal</span>
           </div>
        </div>

        {/* Navigation */}
        <div className="flex-1 overflow-y-auto py-8 px-4 custom-scrollbar">
          <nav className="space-y-1">
            <p className="px-4 text-[10px] font-mono font-bold text-[#4A4A4A] uppercase tracking-widest mb-4">
              Core Systems
            </p>
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  w-full flex items-center px-4 py-3 text-xs font-mono uppercase tracking-wider transition-all duration-200 group rounded-sm border-l-2
                  ${activeTab === tab.id 
                    ? 'bg-[#2D2D2D] text-[#F5F0E6] border-[#F5F0E6]' 
                    : 'text-[#888888] border-transparent hover:bg-[#232323] hover:text-[#B5B5B5]'}
                `}
              >
                <span className={`mr-3 ${activeTab === tab.id ? 'text-[#F5F0E6]' : 'text-[#4A4A4A] group-hover:text-[#888888]'}`}>
                  {tab.icon}
                </span>
                {tab.label}
                {activeTab === tab.id && <ChevronRight size={14} className="ml-auto opacity-50" />}
              </button>
            ))}
          </nav>

          <div className="mt-12">
             <p className="px-4 text-[10px] font-mono font-bold text-[#4A4A4A] uppercase tracking-widest mb-4">
              Resources
            </p>
            <button className="w-full flex items-center px-4 py-3 text-xs font-mono uppercase tracking-wider text-[#888888] hover:bg-[#232323] hover:text-[#B5B5B5] transition-colors rounded-sm border-l-2 border-transparent">
                <span className="mr-3 text-[#4A4A4A]">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                </span>
                Knowledge Base
            </button>
          </div>
        </div>

        {/* User Footer in Sidebar */}
        <div className="border-t border-[#2D2D2D] p-4 bg-[#151515]">
          <div className="flex items-center w-full justify-between">
            <div className="flex items-center min-w-0 mr-2">
                <div className="flex-shrink-0">
                    <img className="h-9 w-9 rounded-sm object-cover border border-[#4A4A4A]" src={user.avatar || `https://ui-avatars.com/api/?name=${user.firstName}+${user.lastName}&background=2D2D2D&color=F5F0E6`} alt="" />
                </div>
                <div className="ml-3 min-w-0">
                    <p className="text-xs font-mono text-[#F5F0E6] truncate uppercase tracking-wide">
                        {user.firstName} {user.lastName}
                    </p>
                    <p className="text-[10px] text-[#888888] truncate font-mono">
                        Online
                    </p>
                </div>
            </div>
            <button 
                onClick={onLogout}
                className="p-2 rounded-sm text-[#4A4A4A] hover:text-[#F5F0E6] hover:bg-[#2D2D2D] transition-colors"
                title="Log out"
            >
                <LogOut size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden relative bg-[#0D0D0D]">
        <header className="h-20 bg-[#0D0D0D] border-b border-[#2D2D2D] flex items-center justify-between px-10">
            <div>
                <h1 className="text-3xl font-serif text-[#F5F0E6] uppercase tracking-wide">
                    {tabs.find(t => t.id === activeTab)?.label}
                </h1>
                <div className="h-1 w-12 bg-[#F5F0E6] mt-2"></div>
            </div>
            <div className="flex items-center space-x-4">
                <button className="p-2 text-[#888888] hover:text-[#F5F0E6] transition-colors">
                    <Bell size={20} />
                </button>
            </div>
        </header>

        <main className="flex-1 overflow-y-auto bg-[#0D0D0D] p-10 custom-scrollbar">
          <div className="max-w-5xl mx-auto">
            {renderContent()}
          </div>
        </main>
      </div>
    </div>
  );
};