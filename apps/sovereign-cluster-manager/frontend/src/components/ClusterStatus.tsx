import { useEffect, useState } from 'react'
import { Activity, AlertCircle, CheckCircle, Loader2 } from 'lucide-react'
import {
  type ClusterState,
  type Node,
  getClusterState,
  getNodes,
  subscribeToClusterState,
  subscribeToNodes,
} from '../lib/supabase'
import { NodeCard } from './NodeCard'

export function ClusterStatus() {
  const [state, setState] = useState<ClusterState | null>(null)
  const [nodes, setNodes] = useState<Node[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Initial fetch
    async function fetchData() {
      const [clusterState, nodeList] = await Promise.all([
        getClusterState(),
        getNodes(),
      ])
      setState(clusterState)
      setNodes(nodeList)
      setLoading(false)
    }
    fetchData()

    // Subscribe to realtime updates
    const stateSubscription = subscribeToClusterState(setState)
    const nodesSubscription = subscribeToNodes(setNodes)

    return () => {
      stateSubscription.unsubscribe()
      nodesSubscription.unsubscribe()
    }
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-48">
        <Loader2 className="w-8 h-8 animate-spin text-slate-400" />
      </div>
    )
  }

  const StatusIcon = {
    ready: CheckCircle,
    running: Activity,
    loading: Loader2,
    error: AlertCircle,
    unknown: AlertCircle,
  }[state?.status || 'unknown']

  const statusColor = {
    ready: 'text-green-400',
    running: 'text-blue-400',
    loading: 'text-amber-400',
    error: 'text-red-400',
    unknown: 'text-slate-400',
  }[state?.status || 'unknown']

  const availableRam = (state?.total_ram_gb || 0) - (state?.used_ram_gb || 0)

  return (
    <div className="space-y-6">
      {/* Cluster Summary */}
      <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <StatusIcon
              className={`w-6 h-6 ${statusColor} ${
                state?.status === 'loading' ? 'animate-spin' : ''
              }`}
            />
            Sovereign Cluster
          </h2>
          <span
            className={`px-3 py-1 rounded-full text-sm font-medium ${
              state?.status === 'running'
                ? 'bg-blue-500/20 text-blue-400'
                : state?.status === 'ready'
                  ? 'bg-green-500/20 text-green-400'
                  : state?.status === 'error'
                    ? 'bg-red-500/20 text-red-400'
                    : 'bg-slate-500/20 text-slate-400'
            }`}
          >
            {state?.status?.toUpperCase() || 'UNKNOWN'}
          </span>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-slate-900/50 rounded-lg p-4">
            <div className="text-2xl font-bold text-white">
              {state?.nodes_online || 0}
              <span className="text-slate-500 text-lg"> / 4</span>
            </div>
            <div className="text-sm text-slate-400">Nodes Online</div>
          </div>
          <div className="bg-slate-900/50 rounded-lg p-4">
            <div className="text-2xl font-bold text-white">
              {state?.total_ram_gb || 0}
              <span className="text-slate-500 text-lg"> GB</span>
            </div>
            <div className="text-sm text-slate-400">Total RAM</div>
          </div>
          <div className="bg-slate-900/50 rounded-lg p-4">
            <div className="text-2xl font-bold text-green-400">
              {availableRam}
              <span className="text-slate-500 text-lg"> GB</span>
            </div>
            <div className="text-sm text-slate-400">Available</div>
          </div>
        </div>

        {/* Error display */}
        {state?.last_error && (
          <div className="mt-4 p-3 bg-red-950/50 border border-red-900/50 rounded-lg">
            <div className="flex items-start gap-2">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
              <div>
                <div className="text-red-400 font-medium">Error</div>
                <div className="text-red-300/70 text-sm">{state.last_error}</div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Node Grid */}
      <div>
        <h3 className="text-lg font-semibold text-slate-300 mb-3">Nodes</h3>
        <div className="grid grid-cols-4 gap-4">
          {nodes.map((node) => (
            <NodeCard key={node.id} node={node} />
          ))}
        </div>
      </div>
    </div>
  )
}
