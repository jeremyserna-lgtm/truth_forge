import { useState } from 'react'
import { Cpu, Database, Settings, Activity } from 'lucide-react'
import { ClusterStatus } from './components/ClusterStatus'
import { ModelVault } from './components/ModelVault'
import { QuickActions } from './components/QuickActions'

type Tab = 'dashboard' | 'vault' | 'settings'

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('dashboard')

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <Cpu className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">
                  Sovereign Cluster Manager
                </h1>
                <p className="text-xs text-slate-500">
                  1.28 TB Pooled Memory • 4 Nodes
                </p>
              </div>
            </div>

            {/* Tab navigation */}
            <nav className="flex gap-1 bg-slate-800/50 p-1 rounded-lg">
              <button
                onClick={() => setActiveTab('dashboard')}
                className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'dashboard'
                    ? 'bg-slate-700 text-white'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <Activity className="w-4 h-4" />
                Dashboard
              </button>
              <button
                onClick={() => setActiveTab('vault')}
                className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'vault'
                    ? 'bg-slate-700 text-white'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <Database className="w-4 h-4" />
                Model Vault
              </button>
              <button
                onClick={() => setActiveTab('settings')}
                className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'settings'
                    ? 'bg-slate-700 text-white'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <Settings className="w-4 h-4" />
                Settings
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {activeTab === 'dashboard' && (
          <div className="space-y-8">
            <QuickActions />
            <ClusterStatus />
          </div>
        )}

        {activeTab === 'vault' && <ModelVault />}

        {activeTab === 'settings' && (
          <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
            <h2 className="text-xl font-bold text-white mb-4">Settings</h2>
            <p className="text-slate-400">
              Settings panel coming soon. Will include:
            </p>
            <ul className="mt-4 space-y-2 text-slate-500">
              <li>• Memory pool configuration</li>
              <li>• Node management</li>
              <li>• Preset editor</li>
              <li>• Vault path configuration</li>
              <li>• Agent status and logs</li>
            </ul>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-4 mt-auto">
        <div className="max-w-7xl mx-auto px-6 text-center text-slate-600 text-sm">
          Sovereign Cluster Manager • Part of Truth Forge
        </div>
      </footer>
    </div>
  )
}

export default App
