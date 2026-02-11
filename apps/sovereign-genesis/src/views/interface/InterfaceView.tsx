/**
 * InterfaceView - Sovereign Interface Unified View
 *
 * System Cognition Dashboard for the Sovereign Architecture.
 * Provides monitoring, terminal, seeing sessions, and bootstrap protocols.
 */

import React, { useState } from 'react';
import { InterfaceView as ViewState } from '../../types';
import { Dashboard } from './components/Dashboard';
import { Terminal } from './components/Terminal';
import { FidelityInspector } from './components/FidelityInspector';
import { SeeingSession } from './components/SeeingSession';
import { BootstrapProtocol } from './components/BootstrapProtocol';
import {
  LayoutDashboard,
  Terminal as TermIcon,
  Eye,
  Workflow,
  Zap
} from 'lucide-react';

interface InterfaceViewProps {
  isDark: boolean;
}

export const InterfaceView: React.FC<InterfaceViewProps> = ({ isDark }) => {
  const [view, setView] = useState<ViewState>(ViewState.DASHBOARD);

  const NavButton: React.FC<{
    active: boolean;
    onClick: () => void;
    icon: React.ReactNode;
    label: string;
    highlight?: boolean;
  }> = ({ active, onClick, icon, label, highlight }) => (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-4 py-3 text-xs font-bold tracking-wide rounded-sm transition-all duration-200 ${
        active
          ? 'bg-zinc-900 text-emerald-400 border-l-2 border-emerald-500'
          : `text-zinc-500 hover:bg-zinc-900/50 hover:text-zinc-300 border-l-2 border-transparent ${
              highlight ? 'text-emerald-500' : ''
            }`
      }`}
    >
      {icon}
      {label}
    </button>
  );

  return (
    <div className="flex h-full w-full bg-black text-gray-200 font-sans transition-colors duration-300">

      {/* Local Navigation Sidebar */}
      <aside className="w-56 bg-zinc-950 border-r border-zinc-800 flex flex-col transition-colors duration-300">
        <div className="p-4 border-b border-zinc-800">
          <h1 className="text-lg font-bold tracking-tighter text-gray-100 flex items-center gap-2">
            <div className="w-3 h-3 bg-emerald-500 rounded-full animate-pulse"></div>
            TRUTH ENGINE
          </h1>
          <p className="text-xs text-zinc-500 mt-1 font-mono uppercase tracking-widest">
            Sovereign Architecture
          </p>
        </div>

        <nav className="flex-1 p-3 space-y-1">
          <NavButton
            active={view === ViewState.DASHBOARD}
            onClick={() => setView(ViewState.DASHBOARD)}
            icon={<LayoutDashboard className="w-4 h-4" />}
            label="THE SEER (DASHBOARD)"
          />
          <NavButton
            active={view === ViewState.TERMINAL}
            onClick={() => setView(ViewState.TERMINAL)}
            icon={<TermIcon className="w-4 h-4" />}
            label="NOT-ME (TERMINAL)"
          />
          <NavButton
            active={view === ViewState.SEEING_SESSION}
            onClick={() => setView(ViewState.SEEING_SESSION)}
            icon={<Workflow className="w-4 h-4" />}
            label="SEEING SESSION"
          />
          <NavButton
            active={view === ViewState.FIDELITY}
            onClick={() => setView(ViewState.FIDELITY)}
            icon={<Eye className="w-4 h-4" />}
            label="FIDELITY INSPECTOR"
          />
          <div className="my-3 border-t border-zinc-800/50"></div>
          <NavButton
            active={view === ViewState.BOOTSTRAP}
            onClick={() => setView(ViewState.BOOTSTRAP)}
            icon={<Zap className="w-4 h-4 text-emerald-500" />}
            label="BOOTSTRAP PROTOCOL"
            highlight
          />
        </nav>

        <div className="p-3 border-t border-zinc-800">
          <div className="text-xs text-zinc-600 font-mono">
            <div className="flex justify-between">
              <span>Empire Cluster</span>
              <span className="text-emerald-500">●</span>
            </div>
            <div className="text-zinc-700 mt-1">1.28TB Unified Memory</div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-hidden relative bg-black">
        {view === ViewState.DASHBOARD && <Dashboard isDark={isDark} />}
        {view === ViewState.TERMINAL && <Terminal />}
        {view === ViewState.SEEING_SESSION && <SeeingSession />}
        {view === ViewState.FIDELITY && (
          <div className="p-6 h-full">
            <FidelityInspector isDark={isDark} />
          </div>
        )}
        {view === ViewState.BOOTSTRAP && <BootstrapProtocol />}
      </main>
    </div>
  );
};

export default InterfaceView;
