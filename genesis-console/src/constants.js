// Genesis Console — Constants & Configuration
// All data definitions extracted from GENESIS_CONSOLE.jsx

export const ATOM_TYPES = {
    fact: { color: '#3b82f6', label: 'FACT' },
    concept: { color: '#8b5cf6', label: 'CONCEPT' },
    relationship: { color: '#06b6d4', label: 'RELATIONSHIP' },
    directive: { color: '#f59e0b', label: 'DIRECTIVE' },
    pattern: { color: '#10b981', label: 'PATTERN' },
    emergence: { color: '#ec4899', label: 'EMERGENCE' },
    contradiction: { color: '#ef4444', label: 'CONTRADICTION' },
    amplification: { color: '#84cc16', label: 'AMPLIFICATION' },
    meta_pattern: { color: '#d946ef', label: 'META-PATTERN' },
    synthesis: { color: '#14b8a6', label: 'SYNTHESIS' },
};

export const FILE_TYPE_MAP = {
    py: { type: 'CODE', icon: '⚡', color: '#3b82f6' },
    js: { type: 'CODE', icon: '⚡', color: '#3b82f6' },
    ts: { type: 'CODE', icon: '⚡', color: '#3b82f6' },
    jsx: { type: 'CODE', icon: '⚡', color: '#3b82f6' },
    tsx: { type: 'CODE', icon: '⚡', color: '#3b82f6' },
    go: { type: 'CODE', icon: '⚡', color: '#3b82f6' },
    rs: { type: 'CODE', icon: '⚡', color: '#3b82f6' },
    sh: { type: 'CODE', icon: '⚡', color: '#3b82f6' },
    json: { type: 'DATA', icon: '◈', color: '#f59e0b' },
    csv: { type: 'DATA', icon: '◈', color: '#f59e0b' },
    yaml: { type: 'DATA', icon: '◈', color: '#f59e0b' },
    yml: { type: 'DATA', icon: '◈', color: '#f59e0b' },
    toml: { type: 'DATA', icon: '◈', color: '#f59e0b' },
    xml: { type: 'DATA', icon: '◈', color: '#f59e0b' },
    md: { type: 'DOCUMENT', icon: '◻', color: '#10b981' },
    txt: { type: 'DOCUMENT', icon: '◻', color: '#10b981' },
    pdf: { type: 'DOCUMENT', icon: '◻', color: '#10b981' },
    docx: { type: 'DOCUMENT', icon: '◻', color: '#10b981' },
    html: { type: 'DOCUMENT', icon: '◻', color: '#10b981' },
    mp3: { type: 'AUDIO', icon: '♫', color: '#8b5cf6' },
    wav: { type: 'AUDIO', icon: '♫', color: '#8b5cf6' },
    m4a: { type: 'AUDIO', icon: '♫', color: '#8b5cf6' },
    ogg: { type: 'AUDIO', icon: '♫', color: '#8b5cf6' },
    mp4: { type: 'VIDEO', icon: '▶', color: '#ec4899' },
    mov: { type: 'VIDEO', icon: '▶', color: '#ec4899' },
    webm: { type: 'VIDEO', icon: '▶', color: '#ec4899' },
    png: { type: 'IMAGE', icon: '◐', color: '#06b6d4' },
    jpg: { type: 'IMAGE', icon: '◐', color: '#06b6d4' },
    jpeg: { type: 'IMAGE', icon: '◐', color: '#06b6d4' },
    svg: { type: 'IMAGE', icon: '◐', color: '#06b6d4' },
    gif: { type: 'IMAGE', icon: '◐', color: '#06b6d4' },
};

export function getFileInfo(filename) {
    const ext = filename.split('.').pop()?.toLowerCase() || '';
    return FILE_TYPE_MAP[ext] || { type: 'UNKNOWN', icon: '?', color: '#6b7280' };
}

export const PIPELINE_STAGES = [
    { id: 'intake', label: 'INTAKE', desc: 'Classify & Wrap', color: '#6b7280' },
    { id: 'atomize', label: 'ATOMIZE', desc: 'Extract Knowledge', color: '#3b82f6' },
    { id: 'compound', label: 'COMPOUND', desc: 'Cross-Artifact', color: '#ec4899' },
    { id: 'synthesize', label: 'SYNTHESIZE', desc: 'Generate Docs', color: '#8b5cf6' },
    { id: 'forge', label: 'FORGE', desc: 'Narratives', color: '#f59e0b' },
    { id: 'podcast', label: 'PODCAST', desc: 'Audio', color: '#10b981' },
];

export const MODELS = [
    { id: 'scout', name: 'SCOUT', sub: 'Llama 4 · 17B-16E', role: 'THE SEER', desc: '10M context window', color: '#3b82f6', mem: '169GB' },
    { id: 'maverick', name: 'MAVERICK', sub: 'Llama 4 · 17B-128E', role: 'THE REASONER', desc: '128 expert mixture', color: '#8b5cf6', mem: '210GB' },
    { id: 'r1', name: 'R1', sub: 'DeepSeek · 671B', role: 'THE ARCHITECT', desc: 'Deep reasoning', color: '#ef4444', mem: '76GB' },
];

export const MEMORY_ENGINES = [
    { id: 'somatic', label: 'SOMATIC', desc: 'Physical State', fill: 0.45 },
    { id: 'symbolic', label: 'SYMBOLIC', desc: 'Language & Metaphor', fill: 0.62 },
    { id: 'narrative', label: 'NARRATIVE', desc: 'Timeline & Story', fill: 0.78 },
    { id: 'relational', label: 'RELATIONAL', desc: 'Bonds & Trust', fill: 0.33 },
    { id: 'strategic', label: 'STRATEGIC', desc: 'Goals & Plans', fill: 0.55 },
];

export const SAMPLE_ATOMS = [
    { type: 'fact', text: 'EXO cluster allocates 1.28TB across 4 Mac Studio nodes', conf: 0.97 },
    { type: 'pattern', text: 'HOLD₁ → AGENT → HOLD₂ pattern enforced at every service boundary', conf: 0.95 },
    { type: 'concept', text: 'Sovereignty means $0.00/day operation with no cloud dependency', conf: 0.92 },
    { type: 'relationship', text: 'Scout routes fast tasks, Maverick handles reasoning, R1 does architecture', conf: 0.94 },
    { type: 'directive', text: 'No new service may exist without inheriting BaseService', conf: 0.99 },
    { type: 'emergence', text: 'Diagram shows 4 nodes but config references only 3 endpoints — gap detected', conf: 0.85 },
    { type: 'contradiction', text: "Meeting audio says 'R1 full 8-bit' but capacity analysis proves it won't fit", conf: 0.91 },
    { type: 'meta_pattern', text: 'Every artifact assumes a 4th orchestration layer but none names it explicitly', conf: 0.78 },
    { type: 'amplification', text: 'CSV benchmarks confirm cognitive_bridge.py routing logic — data validates code', conf: 0.88 },
    { type: 'fact', text: 'KnowledgeService follows HOLD₁(JSONL) → process() → HOLD₂(DuckDB) pattern', conf: 0.96 },
    { type: 'pattern', text: 'Cost governance gate at $0.50/session enforced before every LLM call', conf: 0.93 },
    { type: 'concept', text: 'Capability Manifest — autonomy earned through proof, never granted by permission', conf: 0.90 },
    { type: 'synthesis', text: 'NotebookLM dual-host format and Scout/Maverick/R1 triad are structurally isomorphic', conf: 0.87 },
    { type: 'emergence', text: 'Claude Desktop MCP protocol is structural isomorphism of THE PATTERN (HOLD→AGENT→HOLD)', conf: 0.93 },
];

export const SOVEREIGNTY_ITEMS = [
    { label: 'HARDWARE', value: '4 Nodes', status: true },
    { label: 'MODELS', value: 'Open Weight', status: true },
    { label: 'STORAGE', value: 'DuckDB Local', status: true },
    { label: 'INFERENCE', value: 'EXO + Ollama', status: true },
    { label: 'CLOUD COST', value: '$0.00/day', status: true },
    { label: 'AUTONOMY', value: 'PROVE', status: true },
];

// Ollama API endpoints
export const OLLAMA_BASE = 'http://localhost:11434';
export const EXO_BASE = 'http://localhost:8000';
