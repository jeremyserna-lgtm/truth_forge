import React, { useState } from 'react';
import { User, DashboardTab, SubscriptionTier } from '../types';
import { AccountSettings } from './views/AccountSettings';
import { SystemGuide } from './SystemGuide';
import { User as UserIcon, CreditCard, LogOut, ChevronRight, Anchor, Square, Boxes, Brain, Sparkles } from 'lucide-react';

interface UserPortalProps {
  user: User;
  onLogout: () => void;
  onUpdateUser: (user: User) => void;
}

export const UserPortal: React.FC<UserPortalProps> = ({ user, onLogout, onUpdateUser }) => {
  const [activeTab, setActiveTab] = useState<DashboardTab>(DashboardTab.ACCOUNT);

  const isStage3 = user.tier === SubscriptionTier.STAGE_3_FROZEN;
  const isStage5 = user.tier === SubscriptionTier.STAGE_5_STRUCTURAL;

  const getTabLabel = (tabId: DashboardTab, tier: SubscriptionTier) => {
      if (tabId === DashboardTab.ACCOUNT) {
          switch(tier) {
              case SubscriptionTier.STAGE_3_FROZEN: return "Identity Matrix"; // External/Formal
              case SubscriptionTier.STAGE_4_FLUID: return "My Self"; // Internal/Possessive
              case SubscriptionTier.STAGE_5_STRUCTURAL: return "Entity Definition"; // Meta/Structural
          }
      }
      if (tabId === DashboardTab.BILLING) {
          switch(tier) {
              case SubscriptionTier.STAGE_3_FROZEN: return "Resource Allocation";
              case SubscriptionTier.STAGE_4_FLUID: return "My Capacity";
              case SubscriptionTier.STAGE_5_STRUCTURAL: return "Energy Dynamics";
          }
      }
      return "";
  };

  const getTabDesc = (tabId: DashboardTab, tier: SubscriptionTier) => {
      if (tabId === DashboardTab.ACCOUNT) {
          switch(tier) {
              case SubscriptionTier.STAGE_3_FROZEN: return "Core Identity Framework";
              case SubscriptionTier.STAGE_4_FLUID: return "Who I am in this space";
              case SubscriptionTier.STAGE_5_STRUCTURAL: return "The parameters of being";
          }
      }
      if (tabId === DashboardTab.BILLING) {
          switch(tier) {
              case SubscriptionTier.STAGE_3_FROZEN: return "System Fuel & Tiering";
              case SubscriptionTier.STAGE_4_FLUID: return "What I can do";
              case SubscriptionTier.STAGE_5_STRUCTURAL: return "Entropy Management";
          }
      }
      return "";
  };

  // Dynamic Tabs based on Tier
  const tabs = [
    { 
        id: DashboardTab.ACCOUNT, 
        label: getTabLabel(DashboardTab.ACCOUNT, user.tier), 
        icon: <UserIcon size={16} />, 
        status: isStage5 ? 'FLUID' : 'IMMUTABLE',
        desc: getTabDesc(DashboardTab.ACCOUNT, user.tier)
    },
    { 
        id: DashboardTab.BILLING, 
        label: getTabLabel(DashboardTab.BILLING, user.tier), 
        icon: <CreditCard size={16} />, 
        status: 'IMMUTABLE',
        desc: getTabDesc(DashboardTab.BILLING, user.tier)
    },
  ];

  const renderContent = () => {
    switch (activeTab) {
      case DashboardTab.ACCOUNT:
        return <AccountSettings user={user} onUpdateUser={onUpdateUser} />;
      
      case DashboardTab.BILLING:
          return (
            <div className="flex flex-col items-center justify-center h-full text-center p-12">
                <CreditCard size={48} className="text-[#F5F0E6] mb-4" />
                <h3 className="text-xl font-serif text-[#F5F0E6] mb-2">{getTabLabel(DashboardTab.BILLING, user.tier)}</h3>
                <p className="text-[#888888] font-mono text-sm mb-6">Current Status: <span className="text-[#F5F0E6]">{user.tier}</span></p>
                
                <div className="grid gap-4 max-w-md w-full">
                    {/* Stage 3 Card */}
                    <div className={`p-4 border rounded-sm flex justify-between items-center transition-all ${isStage3 ? 'border-[#F5F0E6] bg-[#1A1A1A] shadow-[0_0_15px_rgba(245,240,230,0.1)]' : 'border-[#2D2D2D] opacity-50'}`}>
                        <div className="text-left">
                            <div className="text-sm font-mono text-[#F5F0E6]">Stage 3 (Socialized)</div>
                            <div className="text-xs text-[#888888]">Frozen State</div>
                        </div>
                        {isStage3 && <div className="text-xs font-mono text-[#F5F0E6] px-2 py-1 bg-[#2D2D2D] rounded">ACTIVE</div>}
                    </div>
                    
                    {/* Stage 4 Card */}
                    <div className={`p-4 border rounded-sm flex justify-between items-center transition-all ${!isStage3 && !isStage5 ? 'border-[#F5F0E6] bg-[#1A1A1A] shadow-[0_0_15px_rgba(245,240,230,0.1)]' : 'border-[#2D2D2D] opacity-70 hover:border-[#4A4A4A]'}`}>
                        <div className="text-left">
                            <div className="text-sm font-mono text-[#F5F0E6]">Stage 4 (Self-Authoring)</div>
                            <div className="text-xs text-[#888888]">Fluid State</div>
                        </div>
                        {(!isStage3 && !isStage5) ? <div className="text-xs font-mono text-[#F5F0E6] px-2 py-1 bg-[#2D2D2D] rounded">ACTIVE</div> : <button className="text-xs font-mono underline decoration-[#888888] hover:text-[#F5F0E6]">Upgrade</button>}
                    </div>

                     {/* Stage 5 Card */}
                     <div className={`p-4 border rounded-sm flex justify-between items-center transition-all ${isStage5 ? 'border-[#F59E0B] bg-[#F59E0B]/10 shadow-[0_0_15px_rgba(245,158,11,0.1)]' : 'border-[#2D2D2D] opacity-70 hover:border-[#4A4A4A]'}`}>
                        <div className="text-left">
                            <div className="text-sm font-mono text-[#F59E0B]">Stage 5 (Self-Transforming)</div>
                            <div className="text-xs text-[#888888]">Structural State</div>
                        </div>
                        {isStage5 ? <div className="text-xs font-mono text-[#F59E0B] px-2 py-1 bg-[#F59E0B]/20 rounded">ACTIVE</div> : <button className="text-xs font-mono underline decoration-[#888888] hover:text-[#F59E0B]">Upgrade</button>}
                    </div>
                </div>
            </div>
          );
      default:
        return null;
    }
  };

  return (
    <div className="flex h-full bg-[#0D0D0D] overflow-hidden">
      {/* Vertical Sidebar */}
      <div className="w-64 bg-[#1A1A1A] border-r border-[#2D2D2D] flex flex-col flex-shrink-0 transition-all duration-500">
        
        {/* Portal Header */}
        <div className="h-16 flex items-center px-6 border-b border-[#2D2D2D] bg-[#151515]">
           <span className="font-mono text-xs text-[#888888] uppercase tracking-widest">
               Administrative
           </span>
        </div>

        {/* Navigation & Guide */}
        <div className="flex-1 flex flex-col overflow-hidden">
            <div className="flex-1 overflow-y-auto py-6 px-3 custom-scrollbar">
                <nav className="space-y-1 mb-6">
                    {tabs.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`
                        w-full flex items-center px-3 py-3 text-xs font-mono uppercase tracking-wider transition-all duration-200 group rounded-sm border-l-2 relative overflow-hidden
                        ${activeTab === tab.id 
                            ? 'bg-[#2D2D2D] text-[#F5F0E6] border-[#F5F0E6]' 
                            : 'text-[#888888] border-transparent hover:bg-[#232323] hover:text-[#B5B5B5]'}
                        `}
                    >
                        <span className={`mr-3 ${activeTab === tab.id ? 'text-[#F5F0E6]' : 'text-[#4A4A4A] group-hover:text-[#888888]'}`}>
                        {tab.icon}
                        </span>
                        <div className="flex flex-col items-start">
                            <span>{tab.label}</span>
                        </div>
                        
                        {/* Status Indicator */}
                        {tab.status === 'IMMUTABLE' && (
                            <div className="ml-auto group/icon relative">
                                <Square size={10} className="text-[#4A4A4A] fill-[#4A4A4A]" />
                                <div className="absolute right-0 top-full mt-1 hidden group-hover/icon:block z-50 bg-black border border-[#2D2D2D] p-1 text-[10px] whitespace-nowrap text-[#888888]">
                                    Fixed Structure
                                </div>
                            </div>
                        )}
                        
                        {activeTab === tab.id && <ChevronRight size={14} className="ml-auto opacity-50" />}
                    </button>
                    ))}
                </nav>

                {/* Embedded System Guide */}
                <SystemGuide tier={user.tier} />
            </div>
        </div>

        {/* Footer Actions */}
        <div className="border-t border-[#2D2D2D] p-4 bg-[#151515]">
            <button 
                onClick={onLogout}
                className="w-full flex items-center justify-center space-x-2 p-2 rounded-sm text-[#888888] hover:text-[#F5F0E6] hover:bg-[#2D2D2D] transition-colors font-mono text-xs uppercase"
            >
                <LogOut size={14} />
                <span>Disconnect</span>
            </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden relative bg-[#0D0D0D]">
        <header className="h-16 bg-[#0D0D0D] border-b border-[#2D2D2D] flex items-center justify-between px-8">
            <div className="flex items-center space-x-3">
                <Anchor size={16} className="text-[#4A4A4A]" />
                <h1 className="text-2xl font-serif text-[#F5F0E6] uppercase tracking-wide">
                    {tabs.find(t => t.id === activeTab)?.label}
                </h1>
                <span className="text-[10px] font-mono text-[#4A4A4A] border border-[#2D2D2D] px-1 rounded">
                   {isStage5 ? "STRUCTURAL" : isStage3 ? "FIXED" : "FLUID"}
                </span>
            </div>
            <div className="flex items-center space-x-4">
                <div className={`flex items-center space-x-2 px-3 py-1 bg-[#1A1A1A] rounded-full border ${isStage5 ? 'border-[#F59E0B]/50' : 'border-[#2D2D2D]'}`}>
                    <div className={`w-2 h-2 rounded-full ${isStage3 ? 'bg-blue-500' : isStage5 ? 'bg-[#F59E0B]' : 'bg-green-500'}`}></div>
                    <span className={`text-[10px] font-mono uppercase ${isStage5 ? 'text-[#F59E0B]' : 'text-[#888888]'}`}>
                        {isStage3 ? "Frozen" : isStage5 ? "Structural" : "Fluid"}
                    </span>
                </div>
            </div>
        </header>

        <main className="flex-1 overflow-y-auto bg-[#0D0D0D] p-8 custom-scrollbar">
          <div className="max-w-4xl mx-auto">
            {renderContent()}
          </div>
        </main>
      </div>
    </div>
  );
};