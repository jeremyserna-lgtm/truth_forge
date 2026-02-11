import React, { useState, useEffect } from 'react';
import { GenesisView } from './types';
import { AtomizerView } from './views/atomizer/AtomizerView';
import { InterfaceView } from './views/interface/InterfaceView';
import { StudioView } from './views/studio/StudioView';
import {
  Boxes,
  Monitor,
  Rocket,
  Sun,
  Moon,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

const App: React.FC = () => {
  const [view, setView] = useState<GenesisView>('atomizer');
  const [isDark, setIsDark] = useState(true);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // Handle theme on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('sovereign-genesis-theme');
    if (savedTheme) {
      setIsDark(savedTheme === 'dark');
    }
  }, []);

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('sovereign-genesis-theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('sovereign-genesis-theme', 'light');
    }
  }, [isDark]);

  const toggleTheme = () => setIsDark(!isDark);
  const toggleSidebar = () => setSidebarCollapsed(!sidebarCollapsed);

  const navItems: { id: GenesisView; label: string; sublabel: string; icon: React.ReactNode; color: string }[] = [
    {
      id: 'atomizer',
      label: 'KNOWLEDGE ATOMIZER',
      sublabel: 'Ingest → Refine → Store → Use',
      icon: <Boxes className="w-5 h-5" />,
      color: 'text-indigo-400',
    },
    {
      id: 'interface',
      label: 'SOVEREIGN INTERFACE',
      sublabel: 'System Cognition Dashboard',
      icon: <Monitor className="w-5 h-5" />,
      color: 'text-emerald-400',
    },
    {
      id: 'studio',
      label: 'SOVEREIGN STUDIO',
      sublabel: 'Talk → Build → Done',
      icon: <Rocket className="w-5 h-5" />,
      color: 'text-rose-400',
    },
  ];

  return (
    <div className="flex h-screen w-screen bg-gray-50 dark:bg-black text-gray-900 dark:text-gray-200 font-sans selection:bg-emerald-500/30 transition-colors duration-300">

      {/* Main Navigation Sidebar */}
      <aside
        className={`${
          sidebarCollapsed ? 'w-16' : 'w-64'
        } bg-white dark:bg-zinc-950 border-r border-gray-200 dark:border-zinc-800 flex flex-col transition-all duration-300`}
      >
        {/* Header */}
        <div className="p-4 border-b border-gray-200 dark:border-zinc-800 flex items-center justify-between">
          {!sidebarCollapsed && (
            <div>
              <h1 className="text-lg font-bold tracking-tighter text-gray-900 dark:text-gray-100 flex items-center gap-2">
                <div className="w-3 h-3 bg-gradient-to-br from-indigo-500 via-emerald-500 to-rose-500 rounded-full animate-pulse"></div>
                SOVEREIGN GENESIS
              </h1>
              <p className="text-xs text-gray-500 dark:text-zinc-500 mt-1 font-mono uppercase tracking-widest">
                The Unified Platform
              </p>
            </div>
          )}
          {sidebarCollapsed && (
            <div className="w-8 h-8 mx-auto bg-gradient-to-br from-indigo-500 via-emerald-500 to-rose-500 rounded-lg flex items-center justify-center">
              <span className="font-bold text-white text-sm">SG</span>
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-2 space-y-1">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setView(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-3 text-xs font-bold tracking-wide rounded-lg transition-all duration-200 ${
                view === item.id
                  ? 'bg-gray-100 dark:bg-zinc-900 border-l-2 border-current ' + item.color
                  : 'text-gray-500 dark:text-zinc-500 hover:bg-gray-50 dark:hover:bg-zinc-900/50 hover:text-gray-900 dark:hover:text-zinc-300'
              }`}
              title={sidebarCollapsed ? item.label : undefined}
            >
              <span className={view === item.id ? item.color : ''}>{item.icon}</span>
              {!sidebarCollapsed && (
                <div className="text-left">
                  <div>{item.label}</div>
                  <div className="text-[10px] font-normal text-gray-400 dark:text-zinc-600 mt-0.5">
                    {item.sublabel}
                  </div>
                </div>
              )}
            </button>
          ))}
        </nav>

        {/* Footer Controls */}
        <div className="p-2 border-t border-gray-200 dark:border-zinc-800 flex items-center justify-between">
          <button
            onClick={toggleSidebar}
            className="text-gray-500 dark:text-zinc-500 hover:text-gray-700 dark:hover:text-zinc-300 transition-colors p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-zinc-900"
            title={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {sidebarCollapsed ? (
              <ChevronRight className="w-4 h-4" />
            ) : (
              <ChevronLeft className="w-4 h-4" />
            )}
          </button>
          {!sidebarCollapsed && (
            <button
              onClick={toggleTheme}
              className="text-gray-500 dark:text-zinc-500 hover:text-emerald-500 dark:hover:text-emerald-400 transition-colors p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-zinc-900"
              title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            >
              {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </button>
          )}
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-hidden relative">
        {view === 'atomizer' && <AtomizerView isDark={isDark} />}
        {view === 'interface' && <InterfaceView isDark={isDark} />}
        {view === 'studio' && <StudioView />}
      </main>
    </div>
  );
};

export default App;
