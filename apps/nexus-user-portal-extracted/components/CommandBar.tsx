import React, { useState } from 'react';
import { Mic, Send, Sparkles } from 'lucide-react';
import { SubscriptionTier } from '../types';

interface CommandBarProps {
  tier: SubscriptionTier;
}

export const CommandBar: React.FC<CommandBarProps> = ({ tier }) => {
  const [input, setInput] = useState('');

  const getPlaceholder = () => {
    switch (tier) {
      case SubscriptionTier.STAGE_3_FROZEN: return "Awaiting external command. System locked.";
      case SubscriptionTier.STAGE_4_FLUID: return "I wish to...";
      case SubscriptionTier.STAGE_5_STRUCTURAL: return "Manifest...";
      default: return "";
    }
  };

  return (
    <div className="h-16 bg-[#0D0D0D] border-t border-[#2D2D2D] flex items-center justify-center px-4 relative z-50">
      <div className={`max-w-3xl w-full relative ${tier === SubscriptionTier.STAGE_3_FROZEN ? 'opacity-50' : ''}`}>
        <div className="absolute inset-y-0 left-3 flex items-center pointer-events-none">
          {tier === SubscriptionTier.STAGE_5_STRUCTURAL ? (
            <Sparkles size={18} className="text-[#F59E0B] animate-pulse" />
          ) : (
            <Mic size={18} className="text-[#4A4A4A]" />
          )}
        </div>
        <input 
          type="text" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={tier === SubscriptionTier.STAGE_3_FROZEN}
          className={`w-full bg-[#1A1A1A] border rounded-full py-3 pl-10 pr-12 text-sm font-mono text-[#F5F0E6] focus:outline-none focus:ring-1 transition-all placeholder-[#4A4A4A] ${tier === SubscriptionTier.STAGE_5_STRUCTURAL ? 'border-[#F59E0B]/50 focus:border-[#F59E0B] focus:ring-[#F59E0B]' : 'border-[#2D2D2D] focus:border-[#F5F0E6] focus:ring-[#F5F0E6]'}`}
          placeholder={getPlaceholder()}
        />
        <button 
          className="absolute inset-y-0 right-2 flex items-center justify-center w-8 h-8 my-auto rounded-full bg-[#2D2D2D] text-[#F5F0E6] hover:bg-[#F5F0E6] hover:text-[#0D0D0D] transition-colors"
          disabled={tier === SubscriptionTier.STAGE_3_FROZEN}
        >
          <Send size={14} />
        </button>
      </div>
    </div>
  );
};