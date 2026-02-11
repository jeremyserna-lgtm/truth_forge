// Genesis Console — Main Application Shell
import { useEffect, useRef } from 'react';
import {
  Routes, Route, NavLink, Navigate, useLocation, useNavigate,
} from 'react-router-dom';
import {
  LayoutDashboard, Workflow, Brain, Cpu, Heart, Settings,
  Activity, Zap, Shield, MessageSquare, Bot, Eye,
} from 'lucide-react';
import { useOllamaStatus, useSystemLog, usePipeline, useAnimaMemory, useUptime } from './hooks';
import { Heartbeat } from './components';

// Pages
import DashboardPage from './pages/Dashboard';
import PipelinePage from './pages/Pipeline';
import KnowledgePage from './pages/Knowledge';
import ModelsPage from './pages/Models';
import AnimaPage from './pages/Anima';
import SettingsPage from './pages/Settings';
import ActionsPage from './pages/Actions';
import MissionPage from './pages/Mission';
import AssistantPage from './pages/Assistant';
import WatcherPage from './pages/Watcher';
import AnnotationLayer from './components/AnnotationLayer';

const PAGE_GUIDES = {
  '/': {
    title: 'Mission',
    summary: 'Type your intent and run the governed stack. This is the primary operator command surface.',
    primaryAction: { label: 'Open Actions', to: '/actions' },
  },
  '/chat': {
    title: 'Chat',
    summary: 'Speak directly with the Genesis monitor and route to Scout, Maverick, or R1 from one window.',
    primaryAction: { label: 'Open Mission', to: '/' },
  },
  '/dashboard': {
    title: 'Dashboard',
    summary: 'Live overview of system health, model status, atoms, and recent runtime events.',
    primaryAction: { label: 'Run Pipeline', to: '/pipeline' },
  },
  '/pipeline': {
    title: 'Pipeline',
    summary: 'Drop files, run atomization, and watch stage-by-stage processing into knowledge atoms.',
    primaryAction: { label: 'View Knowledge', to: '/knowledge' },
  },
  '/knowledge': {
    title: 'Knowledge',
    summary: 'Search, filter, and inspect persistent atoms with confidence and provenance details.',
    primaryAction: { label: 'Open Chat', to: '/chat' },
  },
  '/models': {
    title: 'Models',
    summary: 'Inspect cognitive routing, fleet roles, and loaded local model availability.',
    primaryAction: { label: 'Open Settings', to: '/settings' },
  },
  '/anima': {
    title: 'ANIMA',
    summary: 'Track memory engine fill and what each engine consumes and emits.',
    primaryAction: { label: 'Open Mission', to: '/' },
  },
  '/actions': {
    title: 'Actions',
    summary: 'Run handover, sentinel, and recursive synthesis operations from one control surface.',
    primaryAction: { label: 'Open Mission', to: '/' },
  },
  '/settings': {
    title: 'Settings',
    summary: 'Configure infrastructure endpoints and governance posture.',
    primaryAction: { label: 'Open Models', to: '/models' },
  },
  '/watcher': {
    title: 'Passive Atomization',
    summary: 'Autonomous file watcher that extracts knowledge atoms from every file in truth_forge/ without direction.',
    primaryAction: { label: 'View Knowledge', to: '/knowledge' },
  },
  '/assistant': {
    title: 'Chat',
    summary: 'Legacy assistant route. Use Chat for direct model conversation.',
    primaryAction: { label: 'Open Mission', to: '/' },
  },
};

function App() {
  const location = useLocation();
  const navigate = useNavigate();
  const ollamaStatus = useOllamaStatus(15000);
  const { log, addLog } = useSystemLog();
  const pipeline = usePipeline(addLog);
  const { engines, nudge: nudgeMemory } = useAnimaMemory();
  const uptime = useUptime();
  const contentStageRef = useRef(null);

  // Boot log
  useEffect(() => {
    addLog('Genesis Console v0.1.0 initialized');
    addLog('Connecting to Ollama at localhost:11434...');
  }, [addLog]);

  useEffect(() => {
    if (ollamaStatus.connected) {
      addLog(`Ollama connected — ${ollamaStatus.models.length} model(s) available`, 'success');
    }
  }, [ollamaStatus.connected, ollamaStatus.models.length, addLog]);

  const NAV_ITEMS = [
    { to: '/chat', icon: Bot, label: 'Chat', section: 'CORE', hint: 'Chat with Scout, Maverick, and R1 monitor' },
    { to: '/', icon: MessageSquare, label: 'Mission', section: 'CORE', hint: 'Type intent and run mission orchestration' },
    { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard', section: 'CORE', hint: 'System overview and live status' },
    { to: '/pipeline', icon: Workflow, label: 'Pipeline', section: 'CORE', hint: 'Drop files and run atomization' },
    { to: '/knowledge', icon: Brain, label: 'Knowledge', section: 'CORE', hint: 'Search and inspect stored atoms' },
    { to: '/models', icon: Cpu, label: 'Models', section: 'COGNITION', hint: 'Model routing and load status' },
    { to: '/anima', icon: Heart, label: 'ANIMA', section: 'COGNITION', hint: 'Unified memory engine states' },
    { to: '/actions', icon: Shield, label: 'Actions', section: 'SYSTEM', hint: 'Governance, sentinel, recursive controls' },
    { to: '/watcher', icon: Eye, label: 'Watcher', section: 'SYSTEM', hint: 'Passive atomization — autonomous file monitoring' },
    { to: '/settings', icon: Settings, label: 'Settings', section: 'SYSTEM', hint: 'Infrastructure and policy settings' },
  ];

  const guide = PAGE_GUIDES[location.pathname] || {
    title: 'Genesis Console',
    summary: 'Use the sidebar to navigate major operational surfaces.',
    primaryAction: { label: 'Open Mission', to: '/' },
  };

  let currentSection = '';

  return (
    <div className="app-layout">
      {/* ═══ HEADER ═══ */}
      <header className="app-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <div style={{
            width: 36, height: 36, borderRadius: 10,
            background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontWeight: 900, fontSize: 16, fontFamily: 'var(--font-mono)',
            color: '#fff', flexShrink: 0,
          }}>
            G
          </div>
          <div>
            <div style={{
              fontSize: 15, fontWeight: 800, letterSpacing: 4,
              fontFamily: 'var(--font-mono)', color: '#e5e7eb',
            }}>
              GENESIS
            </div>
            <div style={{
              fontSize: 9, color: '#6b7280', fontFamily: 'var(--font-mono)',
              letterSpacing: 2,
            }}>
              SOVEREIGN MISSION CONTROL
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <div title="System heartbeat process status">
            <Heartbeat active={true} label={false} />
          </div>
          <div style={{
            display: 'flex', alignItems: 'center', gap: 6,
            padding: '4px 10px', borderRadius: 6,
            background: ollamaStatus.backendUp ? 'rgba(16,185,129,0.08)' : 'rgba(239,68,68,0.08)',
            border: `1px solid ${ollamaStatus.backendUp ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.2)'}`,
          }} title="Genesis API server health">
            <div className={`status-dot ${ollamaStatus.backendUp ? 'online' : 'error'}`} />
            <span style={{
              fontSize: 10, fontFamily: 'var(--font-mono)', letterSpacing: 1,
              color: ollamaStatus.backendUp ? '#10b981' : '#ef4444',
            }}>
              {ollamaStatus.backendUp ? 'API' : 'API DOWN'}
            </span>
          </div>
          <div style={{
            display: 'flex', alignItems: 'center', gap: 6,
            padding: '4px 10px', borderRadius: 6,
            background: ollamaStatus.connected ? 'rgba(16,185,129,0.08)' : 'rgba(107,114,128,0.08)',
            border: `1px solid ${ollamaStatus.connected ? 'rgba(16,185,129,0.15)' : 'rgba(107,114,128,0.15)'}`,
          }} title="Connection status to local Ollama runtime">
            <div className={`status-dot ${ollamaStatus.connected ? 'online' : 'offline'}`} />
            <span style={{
              fontSize: 10, fontFamily: 'var(--font-mono)', letterSpacing: 1,
              color: ollamaStatus.connected ? '#10b981' : '#6b7280',
            }}>
              {ollamaStatus.connected ? 'OLLAMA' : 'OFFLINE'}
            </span>
          </div>

          {pipeline.processing && (
            <div style={{
              display: 'flex', alignItems: 'center', gap: 6,
              padding: '4px 10px', borderRadius: 6,
              background: 'rgba(59,130,246,0.08)',
              border: '1px solid rgba(59,130,246,0.15)',
            }} title="Pipeline processing is active">
              <Activity size={12} color="#3b82f6" style={{ animation: 'breathe 1s ease-in-out infinite' }} />
              <span style={{ fontSize: 10, fontFamily: 'var(--font-mono)', color: '#3b82f6', letterSpacing: 1 }}>
                PROCESSING
              </span>
            </div>
          )}

          <div style={{
            fontSize: 11, fontFamily: 'var(--font-mono)', color: '#4b5563',
          }} title="Genesis Console session uptime">
            {uptime}
          </div>

          <div style={{
            fontSize: 13, fontWeight: 700, fontFamily: 'var(--font-mono)',
            color: '#10b981',
          }}>
            $0.00
          </div>
        </div>
      </header>

      {/* ═══ CONTENT ═══ */}
      <div className="app-content">
        {/* ─── SIDEBAR ─── */}
        <nav className="sidebar">
          <div className="sidebar-nav">
            {NAV_ITEMS.map(item => {
              let sectionLabel = null;
              if (item.section !== currentSection) {
                currentSection = item.section;
                sectionLabel = <div key={`sec-${item.section}`} className="sidebar-section-label">{item.section}</div>;
              }
              const Icon = item.icon;
              return (
                <div key={item.to}>
                  {sectionLabel}
                  <NavLink
                    to={item.to}
                    end={item.to === '/'}
                    className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
                    title={item.hint}
                  >
                    <Icon className="icon" size={18} />
                    {item.label}
                  </NavLink>
                </div>
              );
            })}
          </div>

          {/* Sidebar Footer — Sovereignty */}
          <div style={{
            padding: '12px 16px', borderTop: '1px solid var(--genesis-border)',
            background: 'rgba(16,185,129,0.03)',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
              <Zap size={12} color="#10b981" />
              <span style={{ fontSize: 9, fontFamily: 'var(--font-mono)', color: '#10b981', letterSpacing: 2 }}>
                SOVEREIGN
              </span>
            </div>
            <div style={{ fontSize: 10, color: '#6b7280', fontFamily: 'var(--font-mono)' }}>
              1.28TB · 4 NODES
            </div>
            <div style={{ fontSize: 10, color: '#4b5563', fontFamily: 'var(--font-mono)' }}>
              $0.00/day · Open Weight
            </div>
          </div>
        </nav>

        {/* ─── MAIN CONTENT ─── */}
        <div className="content-stage" ref={contentStageRef}>
          <div className="page-guide" title="This strip explains what the current screen does">
            <div className="page-guide-text">
              <div className="page-guide-label">CURRENT SCREEN</div>
              <div className="page-guide-title">{guide.title}</div>
              <div className="page-guide-summary">{guide.summary}</div>
            </div>
            <div className="page-guide-actions">
              <button
                type="button"
                className="page-guide-btn"
                onClick={() => navigate(`/chat?route=${encodeURIComponent(location.pathname)}`)}
                title="Ask the local assistant to explain or troubleshoot this page"
              >
                Ask Chat About This Page
              </button>
              <button
                type="button"
                className="page-guide-btn secondary"
                onClick={() => navigate(guide.primaryAction.to)}
                title="Open the recommended next surface"
              >
                {guide.primaryAction.label}
              </button>
            </div>
          </div>

          <div className="content-routes">
            <Routes>
              <Route path="/" element={<MissionPage apiOnline={ollamaStatus.backendUp !== false} />} />
              <Route path="/dashboard" element={
                <DashboardPage
                  ollamaStatus={ollamaStatus}
                  uptime={uptime}
                  engines={engines}
                  totalAtoms={pipeline.totalAtoms}
                  cascadeCycle={pipeline.cascadeCycle}
                  saturation={pipeline.saturation}
                  log={log}
                  pipelineAtoms={pipeline.atoms}
                />
              } />
              <Route path="/pipeline" element={
                <PipelinePage
                  ollamaStatus={ollamaStatus}
                  pipeline={pipeline}
                  addLog={addLog}
                  engines={engines}
                  log={log}
                  nudgeMemory={nudgeMemory}
                />
              } />
              <Route path="/knowledge" element={<KnowledgePage />} />
              <Route path="/chat" element={<AssistantPage ollamaStatus={ollamaStatus} />} />
              <Route path="/assistant" element={<Navigate to={`/chat${location.search}`} replace />} />
              <Route path="/models" element={<ModelsPage ollamaStatus={ollamaStatus} />} />
              <Route path="/anima" element={<AnimaPage engines={engines} />} />
              <Route path="/actions" element={<ActionsPage />} />
              <Route path="/watcher" element={<WatcherPage />} />
              <Route path="/settings" element={<SettingsPage ollamaStatus={ollamaStatus} />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </div>
          <AnnotationLayer containerRef={contentStageRef} />
        </div>
      </div>
    </div>
  );
}

export default App;
