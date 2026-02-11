import { useState, useEffect, useRef } from "react";
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from "recharts";

const DIMENSIONS = [
  { key: "semantic", label: "Semantic", color: "#6366f1" },
  { key: "significance", label: "Significance", color: "#f59e0b" },
  { key: "epistemic", label: "Epistemic", color: "#10b981" },
  { key: "temporal", label: "Temporal", color: "#3b82f6" },
  { key: "relational", label: "Relational", color: "#8b5cf6" },
  { key: "dialectical", label: "Dialectical", color: "#ec4899" },
  { key: "affective", label: "Affective", color: "#ef4444" },
  { key: "pragmatic", label: "Pragmatic", color: "#f97316" },
  { key: "structural", label: "Structural", color: "#14b8a6" },
  { key: "ontological", label: "Ontological", color: "#6b7280" },
  { key: "normative", label: "Normative", color: "#a855f7" },
  { key: "enrichment", label: "Enrichment", color: "#22d3ee" },
];

const SAMPLE_ATOMS = [
  {
    id: "a1", content: "SafeBigQueryWriter is the ONLY approved method for writing to BigQuery in truth_forge",
    category: "fact", sourceFile: "session-3c247.jsonl",
    dimensions: { semantic: 0.9, significance: 1.0, epistemic: 1.0, temporal: 0.7, relational: 0.6, dialectical: 0.3, affective: 0.5, pragmatic: 1.0, structural: 0.8, ontological: 0.7, normative: 1.0, enrichment: 0.82 },
    meta: { theme: "Data Pipeline", certainty: "fact", tier: "Foundational", sentiment: 0.1, stakes: "high" }
  },
  {
    id: "a2", content: "Streaming inserts caused 8.9 million duplicate rows in spine.entity_unified in January 2026",
    category: "problem", sourceFile: "session-3c247.jsonl",
    dimensions: { semantic: 0.9, significance: 1.0, epistemic: 1.0, temporal: 1.0, relational: 0.8, dialectical: 0.7, affective: 0.9, pragmatic: 0.9, structural: 0.7, ontological: 0.5, normative: 0.8, enrichment: 0.88 },
    meta: { theme: "Data Corruption", certainty: "fact", tier: "Foundational", sentiment: -0.8, stakes: "existential" }
  },
  {
    id: "a3", content: "The Knowledge Atom system can replace the spine decomposition pipeline by going directly from raw data to 12-dimensional atoms",
    category: "insight", sourceFile: "session-3c247.jsonl",
    dimensions: { semantic: 1.0, significance: 1.0, epistemic: 0.7, temporal: 0.8, relational: 0.9, dialectical: 0.8, affective: 0.6, pragmatic: 0.9, structural: 0.9, ontological: 0.8, normative: 0.6, enrichment: 0.83 },
    meta: { theme: "Architecture", certainty: "claim", tier: "Foundational", sentiment: 0.9, stakes: "high" }
  },
  {
    id: "a4", content: "The Four Pillars (Fail-Safe, No Magic, Observability, Idempotency) govern all architecture decisions at Truth Forge",
    category: "pattern", sourceFile: "rules/03-pillars.md",
    dimensions: { semantic: 0.8, significance: 1.0, epistemic: 0.9, temporal: 0.9, relational: 0.7, dialectical: 0.4, affective: 0.3, pragmatic: 0.8, structural: 1.0, ontological: 0.6, normative: 1.0, enrichment: 0.77 },
    meta: { theme: "Governance", certainty: "fact", tier: "Foundational", sentiment: 0.7, stakes: "high" }
  },
  {
    id: "a5", content: "Jeremy expressed frustration when the pipeline corrupted production data for the third time, leading to the creation of strict data enforcement rules",
    category: "emotion", sourceFile: "session-a8f91.jsonl",
    dimensions: { semantic: 0.7, significance: 0.8, epistemic: 0.8, temporal: 0.9, relational: 0.7, dialectical: 0.5, affective: 1.0, pragmatic: 0.6, structural: 0.5, ontological: 0.4, normative: 0.7, enrichment: 0.72 },
    meta: { theme: "Data Enforcement", certainty: "fact", tier: "Insight", sentiment: -0.7, stakes: "high" }
  },
  {
    id: "a6", content: "The decision to skip the spine and go directly to knowledge atoms eliminates 6 pipeline stages and replaces mechanical NLP with LLM understanding",
    category: "decision", sourceFile: "session-3c247.jsonl",
    dimensions: { semantic: 0.9, significance: 1.0, epistemic: 0.6, temporal: 0.8, relational: 0.9, dialectical: 0.9, affective: 0.7, pragmatic: 1.0, structural: 0.8, ontological: 0.7, normative: 0.5, enrichment: 0.80 },
    meta: { theme: "Architecture", certainty: "decision", tier: "Foundational", sentiment: 0.8, stakes: "high" }
  },
];

const CATEGORY_COLORS = {
  fact: "#10b981", decision: "#3b82f6", problem: "#ef4444", solution: "#22c55e",
  pattern: "#8b5cf6", emotion: "#ec4899", insight: "#f59e0b", action: "#f97316", context: "#6b7280"
};

function AtomCard({ atom, isSelected, onClick }) {
  const sentimentColor = atom.meta.sentiment > 0 ? "text-emerald-400" : atom.meta.sentiment < 0 ? "text-red-400" : "text-gray-400";
  const catColor = CATEGORY_COLORS[atom.category] || "#6b7280";

  return (
    <div onClick={onClick} className={`p-3 rounded-lg cursor-pointer transition-all duration-200 border ${isSelected ? "border-indigo-500 bg-gray-800 shadow-lg shadow-indigo-500/20" : "border-gray-700 bg-gray-850 hover:border-gray-600"}`}>
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xs px-2 py-0.5 rounded-full font-medium" style={{ backgroundColor: catColor + "22", color: catColor }}>{atom.category}</span>
        <span className="text-xs text-gray-500">{atom.meta.tier}</span>
        <span className={`text-xs ml-auto ${sentimentColor}`}>{atom.meta.sentiment > 0 ? "+" : ""}{atom.meta.sentiment.toFixed(1)}</span>
      </div>
      <p className="text-sm text-gray-200 leading-relaxed">{atom.content}</p>
      <div className="flex items-center gap-2 mt-2">
        <span className="text-xs text-gray-500">{atom.sourceFile}</span>
        <div className="ml-auto flex gap-1">
          {Object.entries(atom.dimensions).slice(0, 5).map(([k, v]) => (
            <div key={k} className="w-1.5 h-4 rounded-full" style={{ backgroundColor: DIMENSIONS.find(d => d.key === k)?.color + Math.round(v * 255).toString(16).padStart(2, "0") }} title={`${k}: ${(v * 100).toFixed(0)}%`} />
          ))}
        </div>
      </div>
    </div>
  );
}

function DimensionRadar({ atom }) {
  const data = DIMENSIONS.map(d => ({
    dimension: d.label,
    value: Math.round((atom.dimensions[d.key] || 0) * 100),
    fullMark: 100,
  }));

  return (
    <ResponsiveContainer width="100%" height={280}>
      <RadarChart data={data} cx="50%" cy="50%" outerRadius="70%">
        <PolarGrid stroke="#374151" />
        <PolarAngleAxis dataKey="dimension" tick={{ fill: "#9ca3af", fontSize: 10 }} />
        <PolarRadiusAxis angle={90} domain={[0, 100]} tick={false} axisLine={false} />
        <Radar name="Coverage" dataKey="value" stroke="#6366f1" fill="#6366f1" fillOpacity={0.3} strokeWidth={2} />
      </RadarChart>
    </ResponsiveContainer>
  );
}

function DimensionBars({ atom }) {
  const data = DIMENSIONS.map(d => ({
    name: d.label.substring(0, 4),
    value: Math.round((atom.dimensions[d.key] || 0) * 100),
    color: d.color,
  }));

  return (
    <ResponsiveContainer width="100%" height={180}>
      <BarChart data={data} margin={{ top: 5, right: 5, bottom: 5, left: 5 }}>
        <XAxis dataKey="name" tick={{ fill: "#6b7280", fontSize: 9 }} />
        <YAxis domain={[0, 100]} tick={{ fill: "#6b7280", fontSize: 9 }} width={25} />
        <Tooltip contentStyle={{ backgroundColor: "#1f2937", border: "1px solid #374151", borderRadius: "8px" }} labelStyle={{ color: "#e5e7eb" }} />
        <Bar dataKey="value" radius={[4, 4, 0, 0]}>
          {data.map((entry, i) => <Cell key={i} fill={entry.color} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

function AtomizeAnimation({ isProcessing, atoms, onComplete }) {
  const [progress, setProgress] = useState(0);
  const [currentLine, setCurrentLine] = useState("");
  const lines = [
    "Reading session JSONL...",
    "Comprehending conversation context...",
    "Identifying participants and roles...",
    "Extracting factual knowledge...",
    "Detecting decisions and rationale...",
    "Analyzing emotional undertones...",
    "Mapping relational connections...",
    "Filling 12 metadata dimensions...",
    "Computing enrichment coverage...",
    "Running Gate 1: SHA-256 hash check...",
    "Running Gate 2: Cosine similarity check...",
    "Running Gate 3: Knowledge graph resolution...",
    "Writing atoms to knowledge base...",
    "Atomization complete.",
  ];

  useEffect(() => {
    if (!isProcessing) { setProgress(0); return; }
    let step = 0;
    const timer = setInterval(() => {
      step++;
      setProgress(Math.min((step / lines.length) * 100, 100));
      setCurrentLine(lines[Math.min(step - 1, lines.length - 1)]);
      if (step >= lines.length) { clearInterval(timer); onComplete?.(); }
    }, 800);
    return () => clearInterval(timer);
  }, [isProcessing]);

  if (!isProcessing && progress === 0) return null;

  return (
    <div className="bg-gray-900 border border-gray-700 rounded-lg p-4 mb-4">
      <div className="flex items-center gap-3 mb-3">
        <div className={`w-3 h-3 rounded-full ${progress < 100 ? "bg-indigo-500 animate-pulse" : "bg-emerald-500"}`} />
        <span className="text-sm font-medium text-gray-200">Atom Forge {progress < 100 ? "Processing" : "Complete"}</span>
        <span className="text-xs text-gray-500 ml-auto">{Math.round(progress)}%</span>
      </div>
      <div className="w-full bg-gray-800 rounded-full h-1.5 mb-2">
        <div className="h-1.5 rounded-full transition-all duration-500" style={{ width: `${progress}%`, background: progress < 100 ? "linear-gradient(90deg, #6366f1, #8b5cf6)" : "#10b981" }} />
      </div>
      <p className="text-xs text-gray-400 font-mono">{currentLine}</p>
    </div>
  );
}

export default function AtomForge() {
  const [atoms, setAtoms] = useState(SAMPLE_ATOMS);
  const [selectedAtom, setSelectedAtom] = useState(SAMPLE_ATOMS[0]);
  const [view, setView] = useState("gallery");
  const [isProcessing, setIsProcessing] = useState(false);
  const [inputText, setInputText] = useState("");
  const [filter, setFilter] = useState("all");
  const textRef = useRef(null);

  const filteredAtoms = filter === "all" ? atoms : atoms.filter(a => a.category === filter);
  const categories = [...new Set(atoms.map(a => a.category))];

  const enrichmentAvg = atoms.length > 0
    ? (atoms.reduce((s, a) => s + (a.dimensions.enrichment || 0), 0) / atoms.length * 100).toFixed(0)
    : 0;

  const handleAtomize = () => {
    if (!inputText.trim()) return;
    setIsProcessing(true);
  };

  const handleProcessingComplete = () => {
    const newAtom = {
      id: "a" + Date.now(),
      content: inputText.substring(0, 200),
      category: "insight",
      sourceFile: "user-input",
      dimensions: Object.fromEntries(DIMENSIONS.map(d => [d.key, 0.3 + Math.random() * 0.7])),
      meta: { theme: "User Input", certainty: "claim", tier: "Insight", sentiment: 0.3, stakes: "medium" }
    };
    setAtoms([newAtom, ...atoms]);
    setSelectedAtom(newAtom);
    setIsProcessing(false);
    setInputText("");
    setView("gallery");
  };

  return (
    <div className="h-screen bg-gray-950 text-gray-100 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-3 border-b border-gray-800 bg-gray-900/50 backdrop-blur">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center font-bold text-sm">A</div>
          <div>
            <h1 className="text-sm font-semibold tracking-tight">Atom Forge</h1>
            <p className="text-xs text-gray-500">Universal Knowledge Atomizer</p>
          </div>
        </div>
        <div className="flex items-center gap-1 bg-gray-800 rounded-lg p-0.5">
          {[{k: "atomize", l: "Atomize"}, {k: "gallery", l: "Gallery"}, {k: "explore", l: "Explore"}].map(v => (
            <button key={v.k} onClick={() => setView(v.k)} className={`px-3 py-1.5 text-xs rounded-md transition-colors ${view === v.k ? "bg-indigo-600 text-white" : "text-gray-400 hover:text-gray-200"}`}>{v.l}</button>
          ))}
        </div>
        <div className="flex items-center gap-4 text-xs text-gray-500">
          <span><span className="text-indigo-400 font-medium">{atoms.length}</span> atoms</span>
          <span><span className="text-emerald-400 font-medium">{enrichmentAvg}%</span> avg enrichment</span>
          <span><span className="text-amber-400 font-medium">{categories.length}</span> categories</span>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Atomize View */}
        {view === "atomize" && (
          <div className="flex-1 flex flex-col p-6 overflow-y-auto">
            <h2 className="text-lg font-semibold mb-1">Atomize</h2>
            <p className="text-sm text-gray-400 mb-4">Paste any text — conversations, documents, notes — and watch knowledge atoms emerge.</p>
            <textarea ref={textRef} value={inputText} onChange={e => setInputText(e.target.value)} placeholder="Paste a conversation, document, or any text here...&#10;&#10;The LLM will read it, understand it, and extract every piece of knowledge as atoms with 12-dimensional metadata." className="flex-1 min-h-[200px] bg-gray-900 border border-gray-700 rounded-lg p-4 text-sm text-gray-200 placeholder-gray-600 resize-none focus:outline-none focus:border-indigo-500 font-mono" />
            <div className="flex items-center gap-3 mt-4">
              <button onClick={handleAtomize} disabled={isProcessing || !inputText.trim()} className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-gray-700 disabled:text-gray-500 rounded-lg text-sm font-medium transition-colors">
                {isProcessing ? "Forging..." : "Forge Atoms"}
              </button>
              <span className="text-xs text-gray-500">{inputText.length > 0 ? `${Math.ceil(inputText.length / 4)} estimated tokens` : "Ready for input"}</span>
            </div>
            <AtomizeAnimation isProcessing={isProcessing} atoms={atoms} onComplete={handleProcessingComplete} />
          </div>
        )}

        {/* Gallery View */}
        {view === "gallery" && (
          <div className="flex-1 flex overflow-hidden">
            {/* Atom List */}
            <div className="w-[420px] border-r border-gray-800 flex flex-col">
              <div className="p-3 border-b border-gray-800">
                <div className="flex items-center gap-2 flex-wrap">
                  <button onClick={() => setFilter("all")} className={`text-xs px-2 py-1 rounded ${filter === "all" ? "bg-gray-700 text-white" : "text-gray-500 hover:text-gray-300"}`}>all</button>
                  {categories.map(c => (
                    <button key={c} onClick={() => setFilter(c)} className={`text-xs px-2 py-1 rounded ${filter === c ? "text-white" : "text-gray-500 hover:text-gray-300"}`} style={filter === c ? { backgroundColor: CATEGORY_COLORS[c] + "44" } : {}}>
                      {c}
                    </button>
                  ))}
                </div>
              </div>
              <div className="flex-1 overflow-y-auto p-3 space-y-2">
                {filteredAtoms.map(atom => (
                  <AtomCard key={atom.id} atom={atom} isSelected={selectedAtom?.id === atom.id} onClick={() => setSelectedAtom(atom)} />
                ))}
              </div>
            </div>

            {/* Detail Panel */}
            {selectedAtom && (
              <div className="flex-1 p-6 overflow-y-auto">
                <div className="flex items-start gap-3 mb-6">
                  <div className="w-10 h-10 rounded-lg flex items-center justify-center text-lg font-bold" style={{ backgroundColor: (CATEGORY_COLORS[selectedAtom.category] || "#6b7280") + "22", color: CATEGORY_COLORS[selectedAtom.category] }}>
                    {selectedAtom.category[0].toUpperCase()}
                  </div>
                  <div className="flex-1">
                    <p className="text-base text-gray-100 leading-relaxed">{selectedAtom.content}</p>
                    <div className="flex items-center gap-3 mt-2">
                      <span className="text-xs px-2 py-0.5 rounded-full bg-gray-800 text-gray-400">{selectedAtom.meta.theme}</span>
                      <span className="text-xs text-gray-500">{selectedAtom.meta.certainty}</span>
                      <span className="text-xs text-gray-500">{selectedAtom.sourceFile}</span>
                    </div>
                  </div>
                </div>

                {/* Radar Chart */}
                <div className="bg-gray-900 border border-gray-800 rounded-lg p-4 mb-4">
                  <h3 className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">12-Dimension Profile</h3>
                  <DimensionRadar atom={selectedAtom} />
                </div>

                {/* Bar Chart */}
                <div className="bg-gray-900 border border-gray-800 rounded-lg p-4 mb-4">
                  <h3 className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">Dimension Strength</h3>
                  <DimensionBars atom={selectedAtom} />
                </div>

                {/* Dimension Details */}
                <div className="grid grid-cols-3 gap-2">
                  {DIMENSIONS.map(d => {
                    const val = selectedAtom.dimensions[d.key] || 0;
                    return (
                      <div key={d.key} className="bg-gray-900 border border-gray-800 rounded-lg p-3">
                        <div className="flex items-center gap-2 mb-1">
                          <div className="w-2 h-2 rounded-full" style={{ backgroundColor: d.color }} />
                          <span className="text-xs font-medium text-gray-300">{d.label}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="flex-1 bg-gray-800 rounded-full h-1">
                            <div className="h-1 rounded-full transition-all" style={{ width: `${val * 100}%`, backgroundColor: d.color }} />
                          </div>
                          <span className="text-xs text-gray-500">{Math.round(val * 100)}%</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Explore View */}
        {view === "explore" && (
          <div className="flex-1 p-6 overflow-y-auto">
            <h2 className="text-lg font-semibold mb-4">Explore Your Knowledge</h2>
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
                <h3 className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-3">By Category</h3>
                {categories.map(c => {
                  const count = atoms.filter(a => a.category === c).length;
                  const pct = (count / atoms.length * 100).toFixed(0);
                  return (
                    <div key={c} className="flex items-center gap-2 mb-2">
                      <div className="w-2 h-2 rounded-full" style={{ backgroundColor: CATEGORY_COLORS[c] }} />
                      <span className="text-xs text-gray-300 flex-1">{c}</span>
                      <span className="text-xs text-gray-500">{count}</span>
                      <div className="w-20 bg-gray-800 rounded-full h-1">
                        <div className="h-1 rounded-full" style={{ width: `${pct}%`, backgroundColor: CATEGORY_COLORS[c] }} />
                      </div>
                    </div>
                  );
                })}
              </div>
              <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
                <h3 className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-3">Sentiment Map</h3>
                <div className="space-y-2">
                  {atoms.map(a => (
                    <div key={a.id} className="flex items-center gap-2">
                      <div className="w-24 text-xs text-gray-400 truncate">{a.content.substring(0, 20)}...</div>
                      <div className="flex-1 relative h-2 bg-gray-800 rounded-full">
                        <div className="absolute top-0 h-2 w-2 rounded-full transform -translate-x-1" style={{ left: `${(a.meta.sentiment + 1) / 2 * 100}%`, backgroundColor: a.meta.sentiment > 0 ? "#10b981" : a.meta.sentiment < 0 ? "#ef4444" : "#6b7280" }} />
                        <div className="absolute top-0 left-1/2 w-px h-2 bg-gray-600" />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
              <h3 className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-3">Knowledge Timeline</h3>
              <div className="relative pl-4 border-l border-gray-700 space-y-4">
                {atoms.map((a, i) => (
                  <div key={a.id} className="relative">
                    <div className="absolute -left-[21px] w-3 h-3 rounded-full border-2 border-gray-950" style={{ backgroundColor: CATEGORY_COLORS[a.category] }} />
                    <p className="text-sm text-gray-300">{a.content}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs" style={{ color: CATEGORY_COLORS[a.category] }}>{a.category}</span>
                      <span className="text-xs text-gray-600">{a.meta.theme}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
