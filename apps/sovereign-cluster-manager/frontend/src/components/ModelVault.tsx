import { useEffect, useState } from 'react'
import {
  Database,
  FolderOpen,
  Play,
  Loader2,
  HardDrive,
  RefreshCw,
  ChevronRight,
  ChevronDown,
} from 'lucide-react'
import {
  type Model,
  getModels,
  loadModel,
  scanVault,
} from '../lib/supabase'

interface ModelGroup {
  name: string
  models: Model[]
  isExpanded: boolean
}

export function ModelVault() {
  const [models, setModels] = useState<Model[]>([])
  const [loading, setLoading] = useState(true)
  const [loadingModel, setLoadingModel] = useState<string | null>(null)
  const [scanning, setScanning] = useState(false)
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(
    new Set(['base', 'fine-tuned'])
  )

  useEffect(() => {
    fetchModels()
  }, [])

  async function fetchModels() {
    setLoading(true)
    const modelList = await getModels()
    setModels(modelList)
    setLoading(false)
  }

  async function handleScanVault() {
    setScanning(true)
    try {
      await scanVault()
      // Wait a bit for the scan to complete
      await new Promise((resolve) => setTimeout(resolve, 3000))
      await fetchModels()
    } finally {
      setScanning(false)
    }
  }

  async function handleLoadModel(model: Model, mode: 'single' | 'cluster') {
    setLoadingModel(model.id)
    try {
      await loadModel(model.id, mode)
    } finally {
      setLoadingModel(null)
    }
  }

  function toggleGroup(groupName: string) {
    setExpandedGroups((prev) => {
      const next = new Set(prev)
      if (next.has(groupName)) {
        next.delete(groupName)
      } else {
        next.add(groupName)
      }
      return next
    })
  }

  // Group models by category (based on path)
  const groups: ModelGroup[] = [
    {
      name: 'base',
      models: models.filter((m) => m.tags.includes('base')),
      isExpanded: expandedGroups.has('base'),
    },
    {
      name: 'fine-tuned',
      models: models.filter(
        (m) => !m.tags.includes('base') && !m.tags.includes('checkpoint') && !m.tags.includes('lora')
      ),
      isExpanded: expandedGroups.has('fine-tuned'),
    },
    {
      name: 'checkpoints',
      models: models.filter((m) => m.tags.includes('checkpoint')),
      isExpanded: expandedGroups.has('checkpoints'),
    },
    {
      name: 'lora',
      models: models.filter((m) => m.tags.includes('lora')),
      isExpanded: expandedGroups.has('lora'),
    },
  ].filter((g) => g.models.length > 0)

  if (loading) {
    return (
      <div className="flex items-center justify-center h-48">
        <Loader2 className="w-8 h-8 animate-spin text-slate-400" />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <Database className="w-6 h-6 text-slate-400" />
          Model Vault
        </h2>
        <button
          onClick={handleScanVault}
          disabled={scanning}
          className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-300 text-sm transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${scanning ? 'animate-spin' : ''}`} />
          {scanning ? 'Scanning...' : 'Scan Vault'}
        </button>
      </div>

      {/* Model count */}
      <div className="text-sm text-slate-400">
        {models.length} models in vault
      </div>

      {/* Model groups */}
      <div className="space-y-2">
        {groups.map((group) => (
          <div
            key={group.name}
            className="border border-slate-700 rounded-xl overflow-hidden"
          >
            {/* Group header */}
            <button
              onClick={() => toggleGroup(group.name)}
              className="w-full flex items-center justify-between p-3 bg-slate-800/50 hover:bg-slate-800 transition-colors"
            >
              <div className="flex items-center gap-2">
                {group.isExpanded ? (
                  <ChevronDown className="w-4 h-4 text-slate-400" />
                ) : (
                  <ChevronRight className="w-4 h-4 text-slate-400" />
                )}
                <FolderOpen className="w-4 h-4 text-amber-400" />
                <span className="font-medium text-white">{group.name}/</span>
                <span className="text-slate-500 text-sm">
                  ({group.models.length})
                </span>
              </div>
            </button>

            {/* Model list */}
            {group.isExpanded && (
              <div className="divide-y divide-slate-700/50">
                {group.models.map((model) => (
                  <div
                    key={model.id}
                    className={`p-4 ${
                      model.is_loaded ? 'bg-blue-950/30' : 'bg-slate-900/30'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-white">
                            {model.name}
                          </span>
                          {model.is_loaded && (
                            <span className="px-2 py-0.5 text-xs bg-blue-500/20 text-blue-400 rounded-full">
                              LOADED
                            </span>
                          )}
                          {model.quantization && (
                            <span className="px-2 py-0.5 text-xs bg-slate-700 text-slate-300 rounded">
                              {model.quantization}
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-4 mt-1 text-sm text-slate-400">
                          <span className="flex items-center gap-1">
                            <HardDrive className="w-3 h-3" />
                            {model.size_gb.toFixed(1)} GB
                          </span>
                          <span>{model.format}</span>
                          {model.cluster_required && (
                            <span className="text-amber-400">
                              Cluster Required
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Load buttons */}
                      <div className="flex gap-2">
                        {model.single_node_capable && (
                          <button
                            onClick={() => handleLoadModel(model, 'single')}
                            disabled={loadingModel === model.id}
                            className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-green-600 hover:bg-green-500 text-white text-sm transition-colors disabled:opacity-50"
                          >
                            {loadingModel === model.id ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <Play className="w-4 h-4" />
                            )}
                            Single
                          </button>
                        )}
                        <button
                          onClick={() => handleLoadModel(model, 'cluster')}
                          disabled={loadingModel === model.id}
                          className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-sm transition-colors disabled:opacity-50"
                        >
                          {loadingModel === model.id ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <Play className="w-4 h-4" />
                          )}
                          Cluster
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Empty state */}
      {models.length === 0 && (
        <div className="text-center py-12 text-slate-500">
          <Database className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>No models found in vault</p>
          <p className="text-sm">Click "Scan Vault" to discover models</p>
        </div>
      )}
    </div>
  )
}
