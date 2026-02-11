import React, { useState } from 'react';
import { SubscriptionTier } from '../types';
import { Sparkles, Brain, Boxes, ChevronUp, ChevronDown, Info } from 'lucide-react';

interface SystemGuideProps {
  tier: SubscriptionTier;
}

export const SystemGuide: React.FC<SystemGuideProps> = ({ tier }) => {
  const [isExpanded, setIsExpanded] = useState(true);

  const getContent = () => {
    switch (tier) {
      case SubscriptionTier.STAGE_3_FROZEN:
        return {
          title: "Status: FROZEN",
          icon: <Boxes size={12} className="text-blue-400" />,
          intro: "Why is the system prescribing meaning?",
          body: "You are currently in the 'Socialized Mind' state. The interface labels (e.g., 'User Profile', 'Workstation') are external, formal definitions provided by the system. This structure is rigid because it is given to you, not created by you. To reshape these definitions into your own language, you must unlock Fluidity.",
          instruction: "Mission: Upgrade to Stage 4 to authorize your own interface."
        };
      case SubscriptionTier.STAGE_4_FLUID:
        return {
          title: "Status: FLUID",
          icon: <Brain size={12} className="text-green-400" />,
          intro: "Why does the system speak as me?",
          body: "You have entered the 'Self-Authoring Mind'. The labels now reflect your ownership (e.g., 'My Identity', 'My Knowledge'). The AI is simulating your internal voice, predicting what you would call these tools if you were naming them yourself. You are no longer using a tool; you are extending your will.",
          instruction: "Mission: Use your voice to shape the semantics."
        };
      case SubscriptionTier.STAGE_5_STRUCTURAL:
        return {
          title: "Status: ARCHITECT",
          icon: <Sparkles size={12} className="text-amber-400" />,
          intro: "Why are the labels existential?",
          body: "You have achieved the 'Self-Transforming Mind'. The interface now reveals the meta-structure of reality (e.g., 'The Subject', 'Perception', 'Willpower'). The system is showing you what you *would* see if you could look at the construct from the outside. You are not just the user; you are the context.",
          instruction: "Mission: Speak to restructure reality."
        };
      default: return null;
    }
  };

  const content = getContent();
  if (!content) return null;

  return (
    <div className="mx-3 mt-auto mb-4 border border-[#2D2D2D] bg-[#151515] rounded-sm overflow-hidden transition-all duration-300 shadow-lg">
      <button 
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-3 py-2 flex items-center justify-between bg-[#1A1A1A] hover:bg-[#232323] transition-colors border-b border-[#2D2D2D]"
      >
        <div className="flex items-center space-x-2">
           {content.icon}
           <span className="text-[10px] font-mono text-[#F5F0E6] uppercase tracking-wider">{content.title}</span>
        </div>
        {isExpanded ? <ChevronDown size={12} className="text-[#888888]" /> : <ChevronUp size={12} className="text-[#888888]" />}
      </button>
      
      {isExpanded && (
        <div className="p-3 animate-in slide-in-from-top-2 duration-200 bg-[#0D0D0D]">
          <div className="flex items-start space-x-2 mb-2">
            <Info size={12} className="text-[#888888] flex-shrink-0 mt-0.5" />
            <p className="text-[10px] font-mono text-[#F5F0E6] uppercase">{content.intro}</p>
          </div>
          <p className="text-xs text-[#888888] leading-relaxed font-sans mb-3 pl-5 border-l border-[#2D2D2D] ml-1">
            {content.body}
          </p>
          <div className="text-[10px] font-mono text-[#F5F0E6] bg-[#1A1A1A] p-2 rounded-sm border border-[#2D2D2D]">
            {content.instruction}
          </div>
        </div>
      )}
    </div>
  );
};