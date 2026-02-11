import React, { useState } from 'react';
import { ContextWindowState } from '../../../types';

interface TokenMeterProps {
  current: number;
  max: number;
  contextState?: ContextWindowState | null;
  modelLabel?: string;
  provider?: 'gemini' | 'ollama';
}

const TokenMeter: React.FC<TokenMeterProps> = ({
  current,
  max,
  contextState,
  modelLabel,
  provider
}) => {
  const [showDetails, setShowDetails] = useState(false);
  const percentage = Math.min((current / max) * 100, 100);

  // Color based on usage
  let colorClass = "bg-primary-500";
  let healthLabel = "Healthy";
  if (percentage > 70) {
    colorClass = "bg-yellow-500";
    healthLabel = "Warning";
  }
  if (percentage > 90) {
    colorClass = "bg-red-500";
    healthLabel = "Critical";
  }

  // Format large numbers
  const formatTokens = (n: number): string => {
    if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
    if (n >= 1_000) return `${(n / 1_000).toFixed(0)}K`;
    return n.toString();
  };

  // Provider-specific styling
  const providerColor = provider === 'ollama' ? 'emerald' : 'indigo';

  return (
    <div className="relative w-full max-w-xs">
      {/* Main meter */}
      <div
        className="bg-slate-800 rounded-full h-4 border border-slate-700 overflow-hidden relative cursor-pointer"
        onMouseEnter={() => setShowDetails(true)}
        onMouseLeave={() => setShowDetails(false)}
      >
        <div
          className={`h-full ${colorClass} transition-all duration-500 ease-out`}
          style={{ width: `${percentage}%` }}
        />
        <div className="absolute inset-0 flex items-center justify-center text-[10px] font-mono font-bold text-white drop-shadow-md z-10">
          {formatTokens(current)} / {formatTokens(max)}
        </div>
      </div>

      {/* Details popup on hover */}
      {showDetails && contextState && (
        <div className="absolute top-6 right-0 w-64 bg-slate-900 border border-slate-700 rounded-lg shadow-xl p-3 z-50 text-xs">
          {/* Header */}
          <div className="flex items-center justify-between mb-2 pb-2 border-b border-slate-700">
            <span className="font-bold text-slate-200">Context Window</span>
            <span className={`px-2 py-0.5 rounded text-${providerColor}-400 bg-${providerColor}-900/30 text-[10px] font-medium`}>
              {provider === 'ollama' ? '🦙 Local' : '☁️ Cloud'}
            </span>
          </div>

          {/* Model info */}
          {modelLabel && (
            <div className="text-slate-400 mb-2">
              Model: <span className="text-slate-200">{modelLabel}</span>
            </div>
          )}

          {/* Usage breakdown */}
          <div className="space-y-1.5">
            <div className="flex justify-between">
              <span className="text-slate-400">Documents</span>
              <span className="text-slate-200 font-mono">{formatTokens(contextState.breakdown.documents)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Atoms</span>
              <span className="text-slate-200 font-mono">{formatTokens(contextState.breakdown.atoms)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Chat History</span>
              <span className="text-slate-200 font-mono">{formatTokens(contextState.breakdown.chatHistory)}</span>
            </div>
            {contextState.breakdown.systemPrompt > 0 && (
              <div className="flex justify-between">
                <span className="text-slate-400">System</span>
                <span className="text-slate-200 font-mono">{formatTokens(contextState.breakdown.systemPrompt)}</span>
              </div>
            )}
          </div>

          {/* Total */}
          <div className="mt-2 pt-2 border-t border-slate-700 flex justify-between font-bold">
            <span className="text-slate-200">Total</span>
            <span className={`font-mono ${percentage > 90 ? 'text-red-400' : percentage > 70 ? 'text-yellow-400' : 'text-emerald-400'}`}>
              {percentage.toFixed(1)}% used
            </span>
          </div>

          {/* Remaining */}
          <div className="mt-1 text-slate-500 text-center">
            {formatTokens(max - current)} tokens remaining
          </div>

          {/* Health indicator */}
          <div className={`mt-2 text-center text-[10px] font-medium ${
            percentage > 90 ? 'text-red-400' : percentage > 70 ? 'text-yellow-400' : 'text-emerald-400'
          }`}>
            Status: {healthLabel}
          </div>
        </div>
      )}
    </div>
  );
};

export default TokenMeter;
