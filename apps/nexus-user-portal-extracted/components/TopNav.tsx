import React from 'react';
import { AppContext, User, SubscriptionTier } from '../types';
import { Hexagon, Database, Activity, Lock, Unlock, Cpu, Hammer, Eye, User as UserIcon, Zap } from 'lucide-react';

interface TopNavProps {
  currentContext: AppContext;
  onContextChange: (context: AppContext) => void;
  user: User | null;
  onTierChange: (tier: SubscriptionTier) => void;
}

export const TopNav: React.FC<TopNavProps> = ({ currentContext, onContextChange, user, onTierChange }) => {
  
  const getStageLabel = (tier: SubscriptionTier) => {
    switch(tier) {
      case SubscriptionTier.STAGE_3_FROZEN: return "Stage 3: Frozen";
      case SubscriptionTier.STAGE_4_FLUID: return "Stage 4: Fluid";
      case SubscriptionTier.STAGE_5_STRUCTURAL: return "Stage 5: Structural";
    }
  };

  const getStageColor = (tier: SubscriptionTier) => {
    switch(tier) {
      case SubscriptionTier.STAGE_3_FROZEN: return "text-[#888888] border-[#4A4A4A] hover:bg-[#232323]";
      case SubscriptionTier.STAGE_4_FLUID: return "text-[#F5F0E6] border-[#F5F0E6] hover:bg-[#2D2D2D]";
      case SubscriptionTier.STAGE_5_STRUCTURAL: return "text-[#F59E0B] border-[#F59E0B] hover:bg-[#F59E0B]/10";
    }
  };

  const getNavLabel = (context: AppContext, tier: SubscriptionTier) => {
    const map: Record<AppContext, Record<SubscriptionTier, string>> = {
      [AppContext.PORTAL]: {
        [SubscriptionTier.STAGE_3_FROZEN]: "User Profile",
        [SubscriptionTier.STAGE_4_FLUID]: "My Identity",
        [SubscriptionTier.STAGE_5_STRUCTURAL]: "The Subject"
      },
      [AppContext.DATA_SYNTHESIS]: {
        [SubscriptionTier.STAGE_3_FROZEN]: "Data Sources",
        [SubscriptionTier.STAGE_4_FLUID]: "My Knowledge",
        [SubscriptionTier.STAGE_5_STRUCTURAL]: "Perception"
      },
      [AppContext.FOUNDRY]: {
        [SubscriptionTier.STAGE_3_FROZEN]: "Workstation",
        [SubscriptionTier.STAGE_4_FLUID]: "Creation",
        [SubscriptionTier.STAGE_5_STRUCTURAL]: "Willpower"
      },
      [AppContext.OBSERVABILITY]: {
        [SubscriptionTier.STAGE_3_FROZEN]: "System Monitor",
        [SubscriptionTier.STAGE_4_FLUID]: "Self Reflection",
        [SubscriptionTier.STAGE_5_STRUCTURAL]: "Awareness"
      }
    };
    return map[context][tier];
  };

  const tier = user?.tier || SubscriptionTier.STAGE_3_FROZEN;

  return (
    <div className="h-14 bg-[#0D0D0D] border-b border-[#2D2D2D] flex items-center justify-between px-4 select-none z-50 relative">
      <div className="flex items-center space-x-4">
        {/* Logo Area */}
        <div className="flex items-center mr-4">
            <img src="./truth_forge_logo.png" alt="Logo" className="h-8 w-8 mr-3 object-contain" />
            <span className="font-serif text-[#F5F0E6] uppercase tracking-wider text-lg hidden md:block">Truth Forge</span>
        </div>

        {/* Context Tabs */}
        <div className="flex items-center bg-[#1A1A1A] rounded-sm p-1 border border-[#2D2D2D]">
            <button 
                onClick={() => onContextChange(AppContext.PORTAL)}
                className={`
                    flex items-center px-3 py-1.5 rounded-sm text-xs font-mono uppercase tracking-wide transition-all
                    ${currentContext === AppContext.PORTAL 
                        ? 'bg-[#2D2D2D] text-[#F5F0E6] shadow-sm' 
                        : 'text-[#888888] hover:text-[#B5B5B5]'}
                `}
            >
                <UserIcon size={14} className="mr-2" />
                <span className="hidden sm:inline">{getNavLabel(AppContext.PORTAL, tier)}</span>
            </button>
            <button 
                onClick={() => onContextChange(AppContext.DATA_SYNTHESIS)}
                className={`
                    flex items-center px-3 py-1.5 rounded-sm text-xs font-mono uppercase tracking-wide transition-all
                    ${currentContext === AppContext.DATA_SYNTHESIS 
                        ? 'bg-[#2D2D2D] text-[#F5F0E6] shadow-sm' 
                        : 'text-[#888888] hover:text-[#B5B5B5]'}
                `}
            >
                <Database size={14} className="mr-2" />
                <span className="hidden sm:inline">{getNavLabel(AppContext.DATA_SYNTHESIS, tier)}</span>
            </button>
            <button 
                onClick={() => onContextChange(AppContext.FOUNDRY)}
                className={`
                    flex items-center px-3 py-1.5 rounded-sm text-xs font-mono uppercase tracking-wide transition-all
                    ${currentContext === AppContext.FOUNDRY 
                        ? 'bg-[#2D2D2D] text-[#F5F0E6] shadow-sm' 
                        : 'text-[#888888] hover:text-[#B5B5B5]'}
                `}
            >
                {tier === SubscriptionTier.STAGE_5_STRUCTURAL ? <Zap size={14} className="mr-2" /> : <Hammer size={14} className="mr-2" />}
                <span className="hidden sm:inline">{getNavLabel(AppContext.FOUNDRY, tier)}</span>
            </button>
            <button 
                onClick={() => onContextChange(AppContext.OBSERVABILITY)}
                className={`
                    flex items-center px-3 py-1.5 rounded-sm text-xs font-mono uppercase tracking-wide transition-all
                    ${currentContext === AppContext.OBSERVABILITY 
                        ? 'bg-[#2D2D2D] text-[#F5F0E6] shadow-sm' 
                        : 'text-[#888888] hover:text-[#B5B5B5]'}
                `}
            >
                {tier === SubscriptionTier.STAGE_5_STRUCTURAL ? <Eye size={14} className="mr-2" /> : <Activity size={14} className="mr-2" />}
                <span className="hidden sm:inline">{getNavLabel(AppContext.OBSERVABILITY, tier)}</span>
            </button>
        </div>
      </div>

      {/* User Status & Tier Switcher (For Demo) */}
      {user && (
          <div className="flex items-center space-x-4">
              {/* Stage Indicator / Switcher */}
              <button 
                onClick={() => {
                   const next = user.tier === SubscriptionTier.STAGE_3_FROZEN 
                    ? SubscriptionTier.STAGE_4_FLUID 
                    : user.tier === SubscriptionTier.STAGE_4_FLUID 
                        ? SubscriptionTier.STAGE_5_STRUCTURAL 
                        : SubscriptionTier.STAGE_3_FROZEN;
                   onTierChange(next);
                }}
                className={`flex items-center space-x-2 px-3 py-1 rounded-sm border bg-[#1A1A1A] transition-colors ${getStageColor(user.tier)}`}
                title="Click to Simulate Upgrade"
              >
                  {user.tier === SubscriptionTier.STAGE_5_STRUCTURAL ? <Cpu size={12} /> : user.tier === SubscriptionTier.STAGE_4_FLUID ? <Unlock size={12} /> : <Lock size={12} />}
                  <span className="text-[10px] font-mono uppercase tracking-widest">{getStageLabel(user.tier)}</span>
              </button>

              <div className="flex items-center space-x-2 border-l border-[#2D2D2D] pl-4">
                  <img 
                    src={user.avatar} 
                    className="h-8 w-8 rounded-sm border border-[#4A4A4A]"
                    alt="User"
                  />
              </div>
          </div>
      )}
    </div>
  );
};