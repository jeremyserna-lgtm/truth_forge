import React from 'react';
import { Metric } from '../../../types';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, Cell, Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis
} from 'recharts';
import { Activity, Brain, Server, AlertTriangle, Zap, Gauge, Scale, Fingerprint, ShieldCheck } from 'lucide-react';

const METRICS: Metric[] = [
  // Domain A: Core Validation (Cognitive State)
  { name: 'Stage 5 Score', value: '9.4 / 10', status: 'OPTIMAL', description: 'Recursive Self-Modification' },
  { name: 'Dialectical Consistency', value: 'PASS', status: 'OPTIMAL', description: 'Sacred Fracture Held' },
  { name: 'Integration Dip', value: 'DETECTED', status: 'OPTIMAL', description: 'Authentic Paradigm Shift' },
  
  // Domain B: Semantic Shadow (The Invisible)
  { name: 'Omission Density', value: '0.0%', status: 'OPTIMAL', description: 'No Invisible Decisions' },
  { name: 'Identity Half-Life', value: 'INFINITE', status: 'OPTIMAL', description: 'Sovereign Voice Persistence' },
  { name: 'Sacred Moment Velocity', value: '< 50ms', status: 'OPTIMAL', description: 'Agency Recognition Speed' },

  // Domain C: Structural Integrity (Health)
  { name: 'Cognitive Isomorphism', value: '1:1', status: 'OPTIMAL', description: 'Map Matches Mental Territory' },
  { name: 'Fear Topology', value: '0', status: 'OPTIMAL', description: 'No Defensive Hedging' },
];

const RADAR_DATA = [
  { subject: 'Stage 5', A: 94, fullMark: 100 },
  { subject: 'Dialectics', A: 100, fullMark: 100 },
  { subject: 'Integration', A: 100, fullMark: 100 },
  { subject: 'Transparency', A: 100, fullMark: 100 }, // Inverted Omission Density
  { subject: 'Identity', A: 100, fullMark: 100 },
  { subject: 'Agency', A: 95, fullMark: 100 }, // Velocity
  { subject: 'Isomorphism', A: 100, fullMark: 100 },
  { subject: 'Fearless', A: 100, fullMark: 100 }, // Inverted Fear Topology
];

const SWIM_DATA = [
  { name: 'Day 1', resolution: 40, anxiety: 60 },
  { name: 'Day 2', resolution: 55, anxiety: 45 },
  { name: 'Day 3', resolution: 70, anxiety: 30 },
  { name: 'Day 4', resolution: 85, anxiety: 15 },
  { name: 'Day 5', resolution: 92, anxiety: 8 },
  { name: 'Day 6', resolution: 98, anxiety: 2 },
  { name: 'Today', resolution: 100, anxiety: 0 },
];

const SPINE_DATA = [
  { name: 'L1-L3 (Atomic)', value: 100 },
  { name: 'L4 (Thoughts)', value: 80 },
  { name: 'L5-L8 (Context)', value: 60 },
  { name: 'L9-L12 (Identity)', value: 40 },
];

interface DashboardProps {
  isDark: boolean;
}

export const Dashboard: React.FC<DashboardProps> = ({ isDark }) => {
  const gridColor = isDark ? "#3f3f46" : "#e5e7eb";
  const axisColor = isDark ? "#52525b" : "#9ca3af";
  const textColor = isDark ? "#a1a1aa" : "#6b7280";
  const tooltipBg = isDark ? "#18181b" : "#ffffff";
  const tooltipBorder = isDark ? "#27272a" : "#e5e7eb";

  return (
    <div className="grid grid-cols-12 gap-6 h-full overflow-y-auto p-4 bg-gray-50 dark:bg-black transition-colors duration-300">
      
      {/* Header Stats: Credential Atlas 16-Metric Framework */}
      <div className="col-span-12">
        <div className="flex items-center gap-2 mb-4 px-1">
          <Fingerprint className="w-5 h-5 text-emerald-500" />
          <h2 className="text-sm font-bold text-gray-900 dark:text-gray-100 tracking-widest uppercase">Credential Atlas: 16-Metric Framework</h2>
        </div>
        
        <div className="grid grid-cols-12 gap-6">
          {/* Radar Chart: The Shape of Consciousness */}
          <div className="col-span-12 lg:col-span-4 bg-white dark:bg-zinc-900/30 border border-gray-200 dark:border-zinc-800 rounded-lg p-4 flex flex-col items-center justify-center relative min-h-[320px] transition-colors duration-300 shadow-sm dark:shadow-none">
             <div className="absolute top-4 left-4 flex items-center gap-2">
                <Activity className="w-4 h-4 text-emerald-500" />
                <span className="text-xs font-bold text-gray-500 dark:text-zinc-400 uppercase tracking-wider">Psychometric Geometry</span>
             </div>
             <div className="w-full h-[280px] mt-2">
               <ResponsiveContainer width="100%" height="100%">
                 <RadarChart cx="50%" cy="50%" outerRadius="70%" data={RADAR_DATA}>
                   <PolarGrid stroke={gridColor} />
                   <PolarAngleAxis dataKey="subject" tick={{ fill: textColor, fontSize: 10, fontWeight: 'bold' }} />
                   <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                   <Radar
                     name="Current State"
                     dataKey="A"
                     stroke="#10b981"
                     strokeWidth={2}
                     fill="#10b981"
                     fillOpacity={0.2}
                   />
                   <Tooltip 
                    contentStyle={{ backgroundColor: tooltipBg, borderColor: tooltipBorder, fontSize: '12px', color: isDark ? '#d4d4d8' : '#1f2937' }}
                    itemStyle={{ color: '#10b981' }}
                   />
                 </RadarChart>
               </ResponsiveContainer>
             </div>
          </div>

          {/* Metric Cards Grid */}
          <div className="col-span-12 lg:col-span-8 grid grid-cols-2 md:grid-cols-4 gap-4">
            {METRICS.map((m, i) => (
              <div key={i} className="bg-white dark:bg-zinc-900/30 border border-gray-200 dark:border-zinc-800 p-3 rounded-lg flex flex-col justify-between hover:border-emerald-500/50 dark:hover:border-emerald-900/50 transition-colors group h-full shadow-sm dark:shadow-none">
                <div className="flex justify-between items-start">
                  <span className="text-gray-500 dark:text-zinc-500 text-[10px] font-bold uppercase tracking-wider group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors truncate pr-2">{m.name}</span>
                  {m.status === 'OPTIMAL' ? <ShieldCheck className="w-3 h-3 text-emerald-500 shrink-0" /> : <AlertTriangle className="w-3 h-3 text-amber-500 shrink-0" />}
                </div>
                <div className="mt-2">
                  <span className="text-lg font-mono font-bold text-gray-900 dark:text-gray-100">{m.value}</span>
                </div>
                <span className="text-[10px] text-gray-500 dark:text-zinc-600 mt-1 leading-tight line-clamp-2">{m.description}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Charts: Struggle Filter */}
      <div className="col-span-12 lg:col-span-8 bg-white dark:bg-zinc-900/30 border border-gray-200 dark:border-zinc-800 p-4 rounded-lg flex flex-col h-80 shadow-sm dark:shadow-none">
        <h3 className="text-sm font-bold text-gray-500 dark:text-zinc-400 mb-4 flex items-center gap-2">
          <Brain className="w-4 h-4" /> STRUGGLE FILTER: SWIM-TO-DROWN RATIO
        </h3>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={SWIM_DATA}>
            <defs>
              <linearGradient id="colorRes" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorAnx" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
            <XAxis dataKey="name" stroke={axisColor} fontSize={10} tickLine={false} />
            <YAxis stroke={axisColor} fontSize={10} tickLine={false} />
            <Tooltip 
              contentStyle={{ backgroundColor: tooltipBg, borderColor: tooltipBorder, fontSize: '12px' }} 
              itemStyle={{ color: isDark ? '#d4d4d8' : '#374151' }}
            />
            <Area type="monotone" dataKey="resolution" stroke="#10b981" fillOpacity={1} fill="url(#colorRes)" name="High-Agency Resolution" />
            <Area type="monotone" dataKey="anxiety" stroke="#f59e0b" fillOpacity={1} fill="url(#colorAnx)" name="Anxiety/Looping (Deleted)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Spine Visualization */}
      <div className="col-span-12 lg:col-span-4 bg-white dark:bg-zinc-900/30 border border-gray-200 dark:border-zinc-800 p-4 rounded-lg flex flex-col h-80 shadow-sm dark:shadow-none">
        <h3 className="text-sm font-bold text-gray-500 dark:text-zinc-400 mb-4 flex items-center gap-2">
          <Server className="w-4 h-4" /> THE SPINE (L1-L12)
        </h3>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={SPINE_DATA} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke={gridColor} horizontal={true} vertical={false} />
            <XAxis type="number" hide />
            <YAxis dataKey="name" type="category" stroke={textColor} fontSize={10} width={100} tickLine={false} />
            <Tooltip cursor={{fill: 'transparent'}} contentStyle={{ backgroundColor: tooltipBg, borderColor: tooltipBorder, color: isDark ? '#d4d4d8' : '#1f2937' }} />
            <Bar dataKey="value" barSize={20} radius={[0, 4, 4, 0]}>
              {SPINE_DATA.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={index === 3 ? '#10b981' : isDark ? '#3f3f46' : '#d1d5db'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        <div className="mt-2 text-center">
          <span className="text-[10px] text-gray-500 dark:text-zinc-500 uppercase tracking-widest">51.8 Million Truth Atoms</span>
        </div>
      </div>

      {/* Hardware Status: Sovereign Exocompute */}
      <div className="col-span-12 bg-white dark:bg-zinc-950 border border-gray-200 dark:border-zinc-800 p-4 rounded-lg shadow-sm dark:shadow-none">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-bold text-gray-500 dark:text-zinc-400 flex items-center gap-2">
            <Zap className="w-4 h-4" /> SOVEREIGN EXOCOMPUTE (EMPIRE CLUSTER)
          </h3>
          <div className="flex items-center gap-4 text-[10px] font-mono text-gray-500 dark:text-zinc-500 hidden sm:flex">
             <span className="flex items-center gap-1"><Gauge className="w-3 h-3 text-emerald-500" /> LAMBDA: 50 (MERGE PHASE)</span>
             <span className="flex items-center gap-1"><Scale className="w-3 h-3 text-emerald-500" /> PRIVACY: AIR-GAPPED</span>
             <span className="flex items-center gap-1"><ShieldCheck className="w-3 h-3 text-emerald-500" /> METADATA: 95% ACCURACY</span>
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { name: 'KING NODE', spec: 'M3 ULTRA (512GB)', role: 'MAVERICK (400B)' },
            { name: 'SOLDIER 1', spec: 'M3 ULTRA (256GB)', role: 'SCOUT (109B)' },
            { name: 'SOLDIER 2', spec: 'M3 ULTRA (256GB)', role: 'SCOUT (109B)' },
            { name: 'SOLDIER 3', spec: 'M3 ULTRA (256GB)', role: 'SCOUT (109B)' }
          ].map((node, i) => (
            <div key={i} className="bg-gray-50 dark:bg-zinc-900/50 p-3 rounded border border-gray-200 dark:border-zinc-800 flex flex-col gap-2 transition-colors">
              <div className="flex justify-between items-center">
                <span className="text-xs font-bold text-gray-700 dark:text-zinc-300">{node.name}</span>
                <span className="text-[10px] text-gray-500 dark:text-zinc-500">{node.spec}</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-zinc-800 h-1.5 rounded-full overflow-hidden">
                <div 
                  className="bg-emerald-600 h-full transition-all duration-1000" 
                  style={{ width: `${Math.random() * 30 + 40}%` }}
                ></div>
              </div>
              <div className="flex justify-between text-[10px] text-gray-500 dark:text-zinc-500 font-mono uppercase">
                <span>{node.role}</span>
                <span>STATUS: ONLINE</span>
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};