import React, { useState, useEffect } from 'react';
import { ViewState } from './types';
import { Dashboard } from './components/Dashboard';
import { Terminal } from './components/Terminal';
import { FidelityInspector } from './components/FidelityInspector';
import { SeeingSession } from './components/SeeingSession';
import { BootstrapProtocol } from './components/BootstrapProtocol';
import { LayoutDashboard, Terminal as TermIcon, Eye, Workflow, Zap, Sun, Moon } from 'lucide-react';

const App: React.FC = () => {
  const [view, setView] = useState<ViewState>(ViewState.DASHBOARD);
  const [isDark, setIsDark] = useState(true);

  // Handle theme on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      setIsDark(savedTheme === 'dark');
    }
  }, []);

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [isDark]);

  const toggleTheme = () => setIsDark(!isDark);

  return (
    <div className="flex h-screen w-screen bg-gray-50 dark:bg-black text-gray-900 dark:text-gray-200 font-sans selection:bg-emerald-500/30 transition-colors duration-300">
      
      {/* Sidebar Navigation */}
      <aside className="w-64 bg-white dark:bg-zinc-950 border-r border-gray-200 dark:border-zinc-800 flex flex-col transition-colors duration-300">
        <div className="p-6 border-b border-gray-200 dark:border-zinc-800">
          <h1 className="text-xl font-bold tracking-tighter text-gray-900 dark:text-gray-100 flex items-center gap-2">
            <div className="w-3 h-3 bg-emerald-500 rounded-full animate-pulse"></div>
            TRUTH ENGINE
          </h1>
          <p className="text-xs text-gray-500 dark:text-zinc-500 mt-1 font-mono uppercase tracking-widest">Sovereign Architecture</p>
        </div>

        <nav className="flex-1 p-4 space-y-2">
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
          <div className="my-4 border-t border-gray-200 dark:border-zinc-800/50"></div>
          <NavButton 
            active={view === ViewState.BOOTSTRAP} 
            onClick={() => setView(ViewState.BOOTSTRAP)} 
            icon={<Zap className="w-4 h-4 text-emerald-500" />}
            label="BOOTSTRAP PROTOCOL"
          />
        </nav>

        <div className="p-4 border-t border-gray-200 dark:border-zinc-800 flex items-center justify-end">
          <button
            onClick={toggleTheme}
            className="text-gray-500 dark:text-zinc-500 hover:text-emerald-500 dark:hover:text-emerald-400 transition-colors p-1"
            title={isDark ? "Switch to Light Mode" : "Switch to Dark Mode"}
          >
            {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-hidden relative">
        {view === ViewState.DASHBOARD && <Dashboard isDark={isDark} />}
        {view === ViewState.TERMINAL && <Terminal />}
        {view === ViewState.SEEING_SESSION && <SeeingSession />}
        {view === ViewState.FIDELITY && <div className="p-6 h-full"><FidelityInspector isDark={isDark} /></div>}
        {view === ViewState.BOOTSTRAP && <BootstrapProtocol />}
      </main>
    </div>
  );
};

const NavButton: React.FC<{ active: boolean; onClick: () => void; icon: React.ReactNode; label: string }> = ({ active, onClick, icon, label }) => (
  <button
    onClick={onClick}
    className={`w-full flex items-center gap-3 px-4 py-3 text-xs font-bold tracking-wide rounded-sm transition-all duration-200 ${
      active 
        ? 'bg-gray-100 dark:bg-zinc-900 text-emerald-600 dark:text-emerald-400 border-l-2 border-emerald-500' 
        : 'text-gray-500 dark:text-zinc-500 hover:bg-gray-50 dark:hover:bg-zinc-900/50 hover:text-gray-900 dark:hover:text-zinc-300 border-l-2 border-transparent'
    }`}
  >
    {icon}
    {label}
  </button>
);

export default App;