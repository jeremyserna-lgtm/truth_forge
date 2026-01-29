import React from 'react';

interface TokenMeterProps {
  current: number;
  max: number;
}

const TokenMeter: React.FC<TokenMeterProps> = ({ current, max }) => {
  const percentage = Math.min((current / max) * 100, 100);
  
  let colorClass = "bg-primary-500";
  if (percentage > 75) colorClass = "bg-yellow-500";
  if (percentage > 90) colorClass = "bg-red-500";

  return (
    <div className="w-full max-w-xs bg-slate-800 rounded-full h-4 border border-slate-700 overflow-hidden relative group">
      <div 
        className={`h-full ${colorClass} transition-all duration-500 ease-out`}
        style={{ width: `${percentage}%` }}
      />
      <div className="absolute inset-0 flex items-center justify-center text-[10px] font-mono font-bold text-white drop-shadow-md z-10">
        {current.toLocaleString()} / {max.toLocaleString()} TOKENS
      </div>
    </div>
  );
};

export default TokenMeter;