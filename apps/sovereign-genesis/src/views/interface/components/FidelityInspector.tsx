import React, { useState, useEffect, useMemo } from 'react';
import { LogEntry } from '../../../types';
import { ShieldAlert, ShieldCheck, Eye, Database, Activity, Scale } from 'lucide-react';
import { AreaChart, Area, ResponsiveContainer, YAxis, Tooltip } from 'recharts';

const MOCK_LOGS: LogEntry[] = [
  {
    id: 'log-001',
    timestamp: new Date().toISOString(),
    type: 'MANIFESTATION',
    message: 'EXIST-NOW: System state declared.',
    metadata: { decision_source: 'HUMAN_DECISION', layer: 'L12_Identity' }
  },
  {
    id: 'log-002',
    timestamp: new Date(Date.now() - 5000).toISOString(),
    type: 'DECISION',
    message: 'Context window optimization applied.',
    metadata: { 
      decision_source: 'AI_DEFAULT', 
      data_kept: '128kb', 
      data_lost: '0kb (Lossless)',
      magic_numbers_detected: 0
    }
  },
  {
    id: 'log-003',
    timestamp: new Date(Date.now() - 15000).toISOString(),
    type: 'VALIDATION_PENALTY',
    message: 'Hedging pattern detected in candidate response. Applying -1.0 reward.',
    metadata: { 
      decision_source: 'EMPIRE_PROTOCOL',
      validation_penalty_applied: true 
    }
  },
  {
    id: 'log-004',
    timestamp: new Date(Date.now() - 45000).toISOString(),
    type: 'TRUNCATION',
    message: 'Struggle Filter applied to input stream.',
    metadata: { 
      data_kept: 'High-Agency Resolution', 
      data_lost: 'Looping/Anxiety Logs',
      decision_source: 'EMPIRE_PROTOCOL'
    }
  }
];

interface FidelityInspectorProps {
  isDark: boolean;
}

export const FidelityInspector: React.FC<FidelityInspectorProps> = ({ isDark }) => {
  const [logs, setLogs] = useState<LogEntry[]>(MOCK_LOGS);

  // Simulate live logs
  useEffect(() => {
    const interval = setInterval(() => {
      const type = Math.random() > 0.8 ? 'VALIDATION_PENALTY' : (Math.random() > 0.5 ? 'SYSTEM' : 'DECISION');
      const newLog: LogEntry = {
        id: `log-${Date.now()}`,
        timestamp: new Date().toISOString(),
        type: type as any,
        message: type === 'VALIDATION_PENALTY' 
          ? 'Fear Topology detected. Correcting trajectory.' 
          : 'Heartbeat: Validating zero-trust boundaries.',
        metadata: { 
          decision_source: 'EMPIRE_PROTOCOL', 
          magic_numbers_detected: 0,
          validation_penalty_applied: type === 'VALIDATION_PENALTY'
        }
      };
      setLogs(prev => [newLog, ...prev].slice(0, 50));
    }, 8000);
    return () => clearInterval(interval);
  }, []);

  // Calculate Fidelity Score History
  const scoreHistory = useMemo(() => {
    // Clone and reverse to process chronologically (oldest first)
    const chronologicalLogs = [...logs].reverse();
    let currentScore = 100;
    
    const history = chronologicalLogs.map(log => {
      // Determine delta based on log type
      let delta = 0;
      switch (log.type) {
        case 'VALIDATION_PENALTY': delta = -5; break;
        case 'TRUNCATION': delta = -2; break;
        case 'MANIFESTATION': delta = 1; break;
        case 'DECISION': delta = 0.5; break;
        case 'SYSTEM': delta = 0.1; break;
        default: delta = 0;
      }
      
      currentScore = Math.max(0, Math.min(100, currentScore + delta));
      
      return {
        id: log.id,
        time: new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        score: Number(currentScore.toFixed(1)),
        type: log.type
      };
    });
    
    if (history.length === 0) return [{ time: 'Start', score: 100 }];
    return history;
  }, [logs]);

  const currentFidelity = scoreHistory[scoreHistory.length - 1]?.score ?? 100;
  const getScoreColor = (score: number) => score > 90 ? '#10b981' : score > 70 ? '#f59e0b' : '#ef4444';

  const tooltipBg = isDark ? "#18181b" : "#ffffff";
  const tooltipBorder = isDark ? "#27272a" : "#e5e7eb";

  return (
    <div className="flex flex-col h-full bg-white dark:bg-zinc-950 border border-gray-200 dark:border-zinc-800 rounded-lg overflow-hidden transition-colors duration-300">
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-zinc-800 bg-gray-50 dark:bg-zinc-900/50">
        <div className="flex items-center gap-2">
          <Eye className="w-5 h-5 text-emerald-500" />
          <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100 tracking-wider">FIDELITY INSPECTOR</h2>
        </div>
        <div className="flex items-center gap-4 text-xs font-mono">
          <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400">
            <ShieldCheck className="w-4 h-4" /> MAGIC NUMBERS: 0
          </span>
          <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400">
            <Activity className="w-4 h-4" /> OMISSION DENSITY: 0.0
          </span>
           <span className="flex items-center gap-1 text-gray-500 dark:text-zinc-500">
            <Scale className="w-4 h-4" /> EXPOSURES STACK: ACTIVE
          </span>
        </div>
      </div>

      {/* Fidelity Visualization */}
      <div className="h-32 bg-gray-50 dark:bg-zinc-900/30 border-b border-gray-200 dark:border-zinc-800 p-4 flex items-center gap-6">
        {/* Score Card */}
        <div className="flex flex-col min-w-[140px] px-4 py-2 bg-white dark:bg-black/40 rounded border border-gray-200 dark:border-zinc-800">
          <span className="text-[10px] text-gray-500 dark:text-zinc-500 font-mono uppercase tracking-widest mb-1">Fidelity Score</span>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold font-mono tracking-tighter" style={{ color: getScoreColor(currentFidelity) }}>
              {currentFidelity.toFixed(1)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-zinc-800 h-1 mt-2 rounded-full overflow-hidden">
            <div 
              className="h-full transition-all duration-500" 
              style={{ width: `${currentFidelity}%`, backgroundColor: getScoreColor(currentFidelity) }}
            />
          </div>
        </div>

        {/* Trend Chart */}
        <div className="flex-1 h-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={scoreHistory}>
              <defs>
                <linearGradient id="colorFidelity" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={getScoreColor(currentFidelity)} stopOpacity={0.2}/>
                  <stop offset="95%" stopColor={getScoreColor(currentFidelity)} stopOpacity={0}/>
                </linearGradient>
              </defs>
              <YAxis domain={[60, 100]} hide />
              <Tooltip 
                contentStyle={{ backgroundColor: tooltipBg, borderColor: tooltipBorder, fontSize: '11px', color: isDark ? '#d4d4d8' : '#1f2937' }}
                itemStyle={{ color: getScoreColor(currentFidelity) }}
                labelStyle={{ display: 'none' }}
                formatter={(value: number) => [`${value}%`, 'Score']}
              />
              <Area 
                type="monotone" 
                dataKey="score" 
                stroke={getScoreColor(currentFidelity)} 
                fill="url(#colorFidelity)" 
                strokeWidth={2}
                isAnimationActive={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="flex-1 overflow-auto p-0">
        <table className="w-full text-left text-xs font-mono border-collapse">
          <thead className="bg-gray-100 dark:bg-zinc-900 sticky top-0 z-10 text-gray-500 dark:text-zinc-400">
            <tr>
              <th className="p-3 border-b border-gray-200 dark:border-zinc-800">TIMESTAMP</th>
              <th className="p-3 border-b border-gray-200 dark:border-zinc-800">TYPE</th>
              <th className="p-3 border-b border-gray-200 dark:border-zinc-800">MESSAGE</th>
              <th className="p-3 border-b border-gray-200 dark:border-zinc-800">METADATA (ZERO TRUST)</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-zinc-800/50">
            {logs.map((log) => (
              <tr key={log.id} className="hover:bg-gray-50 dark:hover:bg-zinc-900/30 transition-colors">
                <td className="p-3 text-gray-500 dark:text-zinc-500 whitespace-nowrap">{log.timestamp.split('T')[1].replace('Z','')}</td>
                <td className="p-3">
                  <span className={`px-2 py-1 rounded-sm text-[10px] font-bold ${
                    log.type === 'MANIFESTATION' ? 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800' :
                    log.type === 'TRUNCATION' ? 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 border border-amber-200 dark:border-amber-800' :
                    log.type === 'VALIDATION_PENALTY' ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 border border-red-200 dark:border-red-800' :
                    'bg-gray-200 dark:bg-zinc-800 text-gray-700 dark:text-zinc-300'
                  }`}>
                    {log.type}
                  </span>
                </td>
                <td className="p-3 text-gray-700 dark:text-zinc-300">{log.message}</td>
                <td className="p-3 text-gray-500 dark:text-zinc-400">
                  <div className="flex flex-col gap-1">
                    {Object.entries(log.metadata).map(([key, value]) => (
                      <div key={key} className="flex gap-2">
                        <span className="text-gray-500 dark:text-zinc-600 uppercase">{key.replace('_', ' ')}:</span>
                        <span className={key === 'data_lost' ? 'text-red-500 dark:text-red-400' : key === 'validation_penalty_applied' ? 'text-red-500 dark:text-red-400' : 'text-gray-700 dark:text-zinc-300'}>
                          {value.toString()}
                        </span>
                      </div>
                    ))}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};