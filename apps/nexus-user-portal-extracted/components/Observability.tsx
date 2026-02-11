import React from 'react';
import { User, SubscriptionTier } from '../types';
import { Lock, Settings2, BarChart3, Network, Zap } from 'lucide-react';
import { Button } from './Button';

interface ObservabilityProps {
  user: User;
}

export const Observability: React.FC<ObservabilityProps> = ({ user }) => {
  const isStage3 = user.tier === SubscriptionTier.STAGE_3_FROZEN;
  const isStage4 = user.tier === SubscriptionTier.STAGE_4_FLUID;
  const isStage5 = user.tier === SubscriptionTier.STAGE_5_STRUCTURAL;

  return (
    <div className="flex h-full bg-[#0D0D0D] overflow-hidden">
        {/* Sidebar */}
        <div className="w-64 bg-[#151515] border-r border-[#2D2D2D] p-4">
            <h3 className="text-xs font-mono text-[#888888] uppercase tracking-widest mb-6">Metrics</h3>
            <div className="space-y-2">
                <div className="px-3 py-2 bg-[#2D2D2D] rounded-sm text-xs font-mono text-[#F5F0E6] flex items-center justify-between">
                    <span>{isStage3 ? "System Load" : "Cognitive Resonance"}</span>
                    <div className="w-2 h-2 rounded-full bg-green-500"></div>
                </div>
                <div className={`px-3 py-2 rounded-sm text-xs font-mono flex items-center justify-between ${isStage3 ? 'opacity-50 text-[#4A4A4A]' : 'text-[#888888] hover:bg-[#1A1A1A]'}`}>
                    <span>{isStage3 ? "Latency" : "Thought Velocity"}</span>
                    {isStage3 && <Lock size={12} />}
                </div>
                 <div className={`px-3 py-2 rounded-sm text-xs font-mono flex items-center justify-between ${!isStage5 ? 'opacity-50 text-[#4A4A4A]' : 'text-[#888888] hover:bg-[#1A1A1A]'}`}>
                    <span>Structural Integrity</span>
                    {!isStage5 && <Lock size={12} />}
                </div>
            </div>

            {isStage5 && (
                <div className="mt-8 pt-6 border-t border-[#2D2D2D]">
                    <Button fullWidth size="sm" variant="secondary" icon={<Settings2 size={14}/>}>
                        Edit Dash
                    </Button>
                </div>
            )}
        </div>

        {/* Main Dashboard */}
        <div className="flex-1 p-8 overflow-y-auto custom-scrollbar">
            <header className="mb-8 flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-serif text-[#F5F0E6] uppercase tracking-wide">
                        {isStage3 ? "System Observability" : "Essence Visualization"}
                    </h1>
                    <p className="text-xs font-mono text-[#888888] mt-2">
                        {isStage3 ? "Basic usage metrics." : "Real-time semantic analysis and pattern detection."}
                    </p>
                </div>
                {isStage5 && (
                     <span className="px-2 py-1 rounded text-[10px] font-mono bg-[#F59E0B]/20 text-[#F59E0B] border border-[#F59E0B]/50">ARCHITECT MODE</span>
                )}
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                
                {/* Graph 1: Always Visible */}
                <div className="bg-[#1A1A1A] border border-[#2D2D2D] rounded-sm p-6 relative overflow-hidden group">
                    <div className="flex justify-between items-center mb-6">
                        <div className="flex items-center space-x-2">
                            <BarChart3 size={16} className="text-[#F5F0E6]" />
                            <span className="text-xs font-mono text-[#F5F0E6] uppercase tracking-wider">
                                {isStage3 ? "Request Volume" : "Idea Flow"}
                            </span>
                        </div>
                        <span className="text-xs font-mono text-[#888888]">Live</span>
                    </div>
                    {/* Fake Bar Chart */}
                    <div className="h-40 flex items-end justify-between space-x-2">
                        {[40, 65, 30, 80, 55, 90, 45, 70, 60, 50, 85, 40].map((h, i) => (
                            <div key={i} className="w-full bg-[#2D2D2D] group-hover:bg-[#4A4A4A] transition-colors relative">
                                <div style={{height: `${h}%`}} className={`absolute bottom-0 w-full ${isStage5 ? 'bg-[#F59E0B]' : 'bg-[#F5F0E6]'} opacity-80`}></div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Graph 2: Locked in Stage 3 */}
                <div className={`bg-[#1A1A1A] border border-[#2D2D2D] rounded-sm p-6 relative ${isStage3 ? 'opacity-50' : ''}`}>
                    {isStage3 && (
                        <div className="absolute inset-0 bg-black/50 z-10 flex flex-col items-center justify-center backdrop-blur-sm">
                            <Lock size={24} className="text-[#888888] mb-2" />
                            <span className="text-xs font-mono text-[#F5F0E6] uppercase">Tier 4 Required</span>
                        </div>
                    )}
                     <div className="flex justify-between items-center mb-6">
                        <div className="flex items-center space-x-2">
                            <Network size={16} className="text-[#F5F0E6]" />
                            <span className="text-xs font-mono text-[#F5F0E6] uppercase tracking-wider">
                                {isStage3 ? "Network Topology" : "Semantic Connections"}
                            </span>
                        </div>
                    </div>
                    {/* Fake Network Graph */}
                    <div className="h-40 flex items-center justify-center border border-dashed border-[#2D2D2D] rounded-sm">
                        <div className="w-4 h-4 rounded-full bg-[#F5F0E6] relative">
                            <div className="absolute top-0 left-0 w-20 h-[1px] bg-[#4A4A4A] -rotate-45 origin-left"></div>
                            <div className="absolute top-0 left-0 w-20 h-[1px] bg-[#4A4A4A] rotate-12 origin-left"></div>
                            <div className="absolute top-0 left-0 w-20 h-[1px] bg-[#4A4A4A] rotate-90 origin-left"></div>
                        </div>
                    </div>
                </div>

                {/* Graph 3: Locked until Stage 5 */}
                <div className={`md:col-span-2 bg-[#1A1A1A] border border-[#2D2D2D] rounded-sm p-6 relative ${!isStage5 ? 'opacity-50' : ''}`}>
                     {!isStage5 && (
                        <div className="absolute inset-0 bg-black/50 z-10 flex flex-col items-center justify-center backdrop-blur-sm">
                            <Lock size={24} className="text-[#888888] mb-2" />
                            <span className="text-xs font-mono text-[#F5F0E6] uppercase">Tier 5 Required (Structural)</span>
                        </div>
                    )}
                    <div className="flex justify-between items-center mb-6">
                        <div className="flex items-center space-x-2">
                            <Zap size={16} className={isStage5 ? "text-[#F59E0B]" : "text-[#F5F0E6]"} />
                            <span className="text-xs font-mono text-[#F5F0E6] uppercase tracking-wider">
                                System Evolution Velocity
                            </span>
                        </div>
                        {isStage5 && <Button size="sm" variant="secondary">Configure Source</Button>}
                    </div>
                    {/* Fake Waveform */}
                    <div className="h-40 flex items-center overflow-hidden">
                        <svg className="w-full h-full" preserveAspectRatio="none">
                            <path d="M0,50 Q20,20 40,50 T80,50 T120,50 T160,50 T200,80 T240,20 T280,50 T320,50 T360,50 T400,50" 
                                fill="none" 
                                stroke={isStage5 ? "#F59E0B" : "#4A4A4A"} 
                                strokeWidth="2" 
                            />
                        </svg>
                    </div>
                </div>

            </div>
        </div>
    </div>
  );
};