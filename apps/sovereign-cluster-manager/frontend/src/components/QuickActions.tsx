import { useEffect, useState } from 'react'
import { Loader2, Zap, Brain, PenTool, FlaskConical, Dumbbell, Square } from 'lucide-react'
import {
  type Preset,
  getPresets,
  applyPreset,
  unloadModel,
} from '../lib/supabase'

const iconMap: Record<string, React.ElementType> = {
  '🧠': Brain,
  '✍️': PenTool,
  '🔬': FlaskConical,
  '🏋️': Dumbbell,
}

export function QuickActions() {
  const [presets, setPresets] = useState<Preset[]>([])
  const [loading, setLoading] = useState(true)
  const [applying, setApplying] = useState<string | null>(null)

  useEffect(() => {
    async function fetchPresets() {
      const presetList = await getPresets()
      setPresets(presetList.filter((p) => p.is_quick_action))
      setLoading(false)
    }
    fetchPresets()
  }, [])

  async function handleApply(preset: Preset) {
    setApplying(preset.id)
    try {
      await applyPreset(preset.id)
    } finally {
      setApplying(null)
    }
  }

  async function handleUnload() {
    setApplying('unload')
    try {
      await unloadModel()
    } finally {
      setApplying(null)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-24">
        <Loader2 className="w-6 h-6 animate-spin text-slate-400" />
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold text-slate-300 flex items-center gap-2">
        <Zap className="w-5 h-5 text-amber-400" />
        Quick Actions
      </h2>

      <div className="flex gap-3 flex-wrap">
        {presets.map((preset) => {
          const Icon = iconMap[preset.icon || ''] || Brain
          const isApplying = applying === preset.id

          return (
            <button
              key={preset.id}
              onClick={() => handleApply(preset)}
              disabled={applying !== null}
              className={`
                flex flex-col items-center gap-2 p-4 rounded-xl
                border border-slate-700 bg-slate-800/50
                hover:bg-slate-800 hover:border-slate-600
                transition-all
                disabled:opacity-50
                min-w-[120px]
              `}
            >
              {isApplying ? (
                <Loader2 className="w-8 h-8 animate-spin text-slate-400" />
              ) : (
                <Icon className="w-8 h-8 text-slate-300" />
              )}
              <span className="font-medium text-white text-sm">
                {preset.name}
              </span>
              <span className="text-xs text-slate-500">
                {preset.deployment_mode === 'cluster' ? 'Full Cluster' : 'King Only'}
              </span>
            </button>
          )
        })}

        {/* Unload button */}
        <button
          onClick={handleUnload}
          disabled={applying !== null}
          className={`
            flex flex-col items-center gap-2 p-4 rounded-xl
            border border-red-900/50 bg-red-950/30
            hover:bg-red-950/50 hover:border-red-800
            transition-all
            disabled:opacity-50
            min-w-[120px]
          `}
        >
          {applying === 'unload' ? (
            <Loader2 className="w-8 h-8 animate-spin text-red-400" />
          ) : (
            <Square className="w-8 h-8 text-red-400" />
          )}
          <span className="font-medium text-red-400 text-sm">Stop</span>
          <span className="text-xs text-slate-500">Unload Model</span>
        </button>
      </div>
    </div>
  )
}
