import React, { useMemo, useState } from 'react';
import { KnowledgeAtom, Cluster } from '../../../types';
import { clusterAtoms } from '../../../services/clusterService';
import { CubeTransparentIcon, ArrowPathRoundedSquareIcon } from '@heroicons/react/24/solid';

interface ClusterViewProps {
    atoms: KnowledgeAtom[];
    onNormalize: (normalizedAtoms: KnowledgeAtom[]) => void;
}

const ClusterView: React.FC<ClusterViewProps> = ({ atoms, onNormalize }) => {
    const [threshold, setThreshold] = useState(0.85);

    // Memoize clustering to avoid recalc on every render unless atoms/threshold change
    const clusters = useMemo(() => {
        return clusterAtoms(atoms, threshold);
    }, [atoms, threshold]);

    const handleNormalize = () => {
        const normalized: KnowledgeAtom[] = [];
        const outliers = new Set(atoms.map(a => a.id));

        clusters.forEach((c: Cluster) => {
            normalized.push(c.centroid);
            outliers.delete(c.centroid.id);
            c.items.forEach((i: KnowledgeAtom) => outliers.delete(i.id));
        });

        // Add remaining outliers
        atoms.forEach(a => {
            if (outliers.has(a.id)) normalized.push(a);
        });

        if (confirm(`Normalize will reduce ${atoms.length} atoms to ${normalized.length} core truths. Continue?`)) {
            onNormalize(normalized);
        }
    };

    if (atoms.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-slate-500 p-8">
                <CubeTransparentIcon className="w-24 h-24 mb-4 opacity-50" />
                <p>No Knowledge Atoms available to cluster.</p>
            </div>
        );
    }

    return (
        <div className="h-full flex flex-col p-6 md:p-10 max-w-7xl mx-auto w-full">
            <div className="mb-8 flex flex-col md:flex-row justify-between items-end">
                <div>
                    <h1 className="text-3xl font-black text-white mb-2 flex items-center">
                        <CubeTransparentIcon className="w-8 h-8 mr-3 text-cyan-400" />
                        Similarity Clusters
                    </h1>
                    <p className="text-slate-400">
                        Analyzing <strong>{atoms.length}</strong> atoms. Found <strong>{clusters.length}</strong> distinct semantic clusters.
                    </p>
                </div>
                <div className="flex items-center space-x-4 mt-4 md:mt-0 bg-slate-900 p-2 rounded-xl border border-slate-800">
                    <div className="flex flex-col px-2">
                        <label className="text-[10px] text-slate-500 font-bold uppercase">Similarity Threshold: {threshold.toFixed(2)}</label>
                        <input
                            type="range"
                            min="0.7"
                            max="0.99"
                            step="0.01"
                            value={threshold}
                            onChange={(e) => setThreshold(parseFloat(e.target.value))}
                            className="w-32 md:w-48 accent-cyan-500"
                            title="Adjust clustering strictness"
                        />
                    </div>
                    <button
                        onClick={handleNormalize}
                        title="Deduplicate atoms based on clusters"
                        className="flex items-center space-x-2 bg-cyan-900/30 hover:bg-cyan-800/50 text-cyan-400 px-4 py-2 rounded-lg border border-cyan-800/50 transition-colors"
                    >
                        <ArrowPathRoundedSquareIcon className="w-5 h-5" />
                        <span>Normalize Core Truths</span>
                    </button>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto pr-2 scrollbar-thin space-y-6">
                {clusters.map((cluster: Cluster) => (
                    <div key={cluster.id} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-lg">
                        <div className="flex items-center mb-4">
                            <div className="w-3 h-3 rounded-full bg-cyan-500 mr-3 shadow-[0_0_10px_rgba(34,211,238,0.5)]"></div>
                            <h3 className="text-white font-bold text-lg">{cluster.label} Cluster</h3>
                            <span className="ml-3 text-xs bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full">
                                {cluster.items.length + 1} items
                            </span>
                        </div>

                        {/* Centroid */}
                        <div className="mb-4 bg-cyan-950/20 border-l-4 border-cyan-500 p-4 rounded-r-lg">
                            <div className="flex justify-between items-start mb-1">
                                <span className="text-[10px] text-cyan-400 uppercase font-bold tracking-wider">Cluster Centroid (Core Truth)</span>
                            </div>
                            <p className="text-slate-200 text-sm md:text-base font-medium">{cluster.centroid.content}</p>
                        </div>

                        {/* Items */}
                        {cluster.items.length > 0 && (
                            <div className="space-y-2 pl-4 border-l border-slate-800">
                                {cluster.items.map(item => (
                                    <div key={item.id} className="text-slate-400 text-sm font-light hover:text-slate-300 transition-colors">
                                        • {item.content}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                ))}

                {/* Unclustered (Visualized implicitly as separate small blocks or handled via filtering) */}
            </div>
        </div>
    );
};

export default ClusterView;