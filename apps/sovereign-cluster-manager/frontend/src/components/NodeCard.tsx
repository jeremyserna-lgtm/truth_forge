import { Server, Cpu, HardDrive, Wifi, WifiOff } from 'lucide-react'
import type { Node } from '../lib/supabase'

interface NodeCardProps {
  node: Node
}

export function NodeCard({ node }: NodeCardProps) {
  const isOnline = node.status === 'online'
  const ramUsed = node.ram_total_gb - (node.ram_available_gb || 0)
  const ramPercent = (ramUsed / node.ram_total_gb) * 100

  return (
    <div
      className={`
        rounded-xl border p-4
        ${isOnline
          ? 'border-slate-700 bg-slate-800/50'
          : 'border-red-900/50 bg-red-950/20'
        }
      `}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          {node.role === 'king' ? (
            <Cpu className="w-5 h-5 text-amber-400" />
          ) : (
            <Server className="w-5 h-5 text-slate-400" />
          )}
          <span className="font-semibold text-white uppercase">
            {node.id}
          </span>
        </div>
        <div className="flex items-center gap-1">
          {isOnline ? (
            <Wifi className="w-4 h-4 text-green-400" />
          ) : (
            <WifiOff className="w-4 h-4 text-red-400" />
          )}
          <span
            className={`text-xs ${isOnline ? 'text-green-400' : 'text-red-400'}`}
          >
            {isOnline ? 'Online' : 'Offline'}
          </span>
        </div>
      </div>

      {/* RAM */}
      <div className="mb-3">
        <div className="flex justify-between text-xs text-slate-400 mb-1">
          <span>RAM</span>
          <span>
            {ramUsed.toFixed(0)} / {node.ram_total_gb} GB
          </span>
        </div>
        <div className="h-2 bg-slate-900 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all ${
              ramPercent > 90
                ? 'bg-red-500'
                : ramPercent > 70
                  ? 'bg-amber-500'
                  : 'bg-green-500'
            }`}
            style={{ width: `${Math.min(ramPercent, 100)}%` }}
          />
        </div>
      </div>

      {/* Storage (if available) */}
      {node.storage_total_gb && (
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <HardDrive className="w-3 h-3" />
          <span>
            {node.storage_available_gb?.toFixed(0) || '?'} GB free
          </span>
        </div>
      )}
    </div>
  )
}
