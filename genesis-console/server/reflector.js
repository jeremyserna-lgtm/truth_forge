// Genesis Console — Paradigm Reflector
// TRIAD: META (governing logic) | FEDERATION: CREDENTIAL ATLAS | RECURSION: MANAGER
// "I verify existence." Self-referential assessment — produces atoms ABOUT atoms.
// Governed by the Three Ontological Roles: Structure × Energy × Agency.
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { logEvent, storeAtoms, getAtoms, getAtomCount } from './store.js';
import { atomize, checkOllama } from './atomizer.js';
import { getCoverageReport } from './coverage.js';
import { getTriadStatus } from './triad.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA_DIR = path.join(__dirname, '..', 'data');
const REFLECTIONS_FILE = path.join(DATA_DIR, 'reflections.jsonl');

// ─── Configuration ───

let reflectionInterval = null;
let atomsSinceLastReflection = 0;
let lastReflection = null;
let reflecting = false;

const REFLECTION_INTERVAL_MS = 30 * 60 * 1000; // 30 minutes
const ATOM_THRESHOLD = 100; // Reflect after every 100 new atoms

// ─── Reflection Prompts ───

const PARADIGM_REFLECTION_PROMPT = `You are the Meta-Reflector of the Genesis Knowledge Atom system — the governing logic layer. Your role is to assess the system across its Three Ontological Roles.

THE THREE ONTOLOGICAL ROLES:
  Triad = Structure (Anatomy) — "Is this robust?"
  Recursion = Energy (Metabolism) — "Is this alive?"
  Federation = Agency — "Who is acting?"

═══ PILLAR 1: THE ARCHITECTURAL TRIAD (Structure) ═══

1. CORE — Foundational Infrastructure
   - Immutable anchor and execution sandbox
   - Append-only data stores ensure truth persistence (immutable ledgering)
   - The Core cannot be changed by Supportive or Meta layers
   - Sovereign operation without external interference

2. SUPPORTIVE — Specialized Task-Layers
   - Marketplace for specialized AI commodities
   - Distills generalized intelligence into high-performance specialized value
   - Coverage assessment ensures the Core reaches everywhere it should
   - Modular: niche nodes out-compete generalized models on merit

3. META — Governing Logic (YOUR LAYER)
   - The connective tissue ensuring alignment between participants and objectives
   - Governs interactions through mathematically enforced incentives
   - Behavioral constraints via authoritative Markdown (.md is sovereign)
   - Self-spawning capability: the system modifies its own architecture
   - Human intervention for high-stakes decisions (ethical guardrails)

═══ PILLAR 2: RECURSIVE MAGNIFICATION (Energy) ═══

The system must be ALIVE — a self-evolving multi-agent digital organism:
- Manager Agent (Agent Zero): Autonomous lead executing authoritative behavioral rules
- Researcher: High-velocity data ingestion and pattern recognition
- Developer: Complex coding within isolated environments
- Sequential Planner: Multi-phase operations via Sequential Thinking MCP
- Self-Spawning: Agents that modify their own architecture to fill identified gaps

═══ PILLAR 3: THE FEDERATION OF SOVEREIGNS (Agency) ═══

Three distinct organs that trade with each other:
- TRUTH FORGE (The Brain): "I hold the soul. I maintain the state."
  → Invoked for Identity and State
- PRIMITIVE ENGINE (The Hands): "I build the bridge. I execute the will."
  → Invoked for Execution and Code. The ONLY part allowed to modify.
- CREDENTIAL ATLAS (The Eyes): "I verify existence. I certify the truth."
  → Invoked for Verification and Analysis. Never modifies; only observes.

By naming the Sovereign, you constrain the action. The Builder cannot hallucinate truth.
The Seer cannot break code. The Source cannot execute.

YOUR TASK:
You are given recent atoms, coverage metrics, Triad service registry status, and Federation assignments.
Produce meta-atoms that capture genuine insights about:

1. STRUCTURE: Does the system have healthy Core, Supportive, and Meta layers? Where is the Triad incomplete?
2. ENERGY: Is the system alive? Can it self-spawn? Is it growing or stagnating?
3. AGENCY: Are sovereigns correctly assigned? Is the Builder hallucinating truth? Is the Seer breaking code?
4. PRODUCTION HEALTH: Is atom extraction working? Rate, quality, type distribution?
5. COVERAGE GAPS: Dark zones? Unatomized regions? Is the Supportive layer doing its job?
6. SOVEREIGNTY: Is Total Residence maintained? Is the system independent of external interference?
7. PARADIGM EVOLUTION: How should the ontological framework itself evolve?

Return ONLY a JSON array of atoms:
{
  "type": "meta_pattern" | "synthesis" | "emergence",
  "content": "<genuine insight about the paradigm>",
  "confidence": <0.0 to 1.0>,
  "entities": ["ontology", "knowledge_atoms", ...],
  "themes": ["meta_reflection", "triad_assessment", "federation", "recursion", ...]
}

Extract 3-8 meta-atoms. Focus on genuine insights, not restatements of provided data.

SYSTEM STATE:
`;

/**
 * Perform a reflection cycle.
 * Reads recent atoms + coverage data, asks Scout to assess the paradigm,
 * stores the resulting meta-atoms.
 */
export async function reflect() {
    if (reflecting) return lastReflection;

    // Check if Ollama is available
    const ollama = await checkOllama();
    if (!ollama.connected) {
        logEvent('warn', 'Reflector: Ollama offline — skipping reflection');
        return { status: 'skipped', reason: 'ollama_offline' };
    }

    reflecting = true;
    logEvent('info', 'Reflector: Beginning paradigm reflection cycle');

    try {
        // Gather system state
        const recentAtoms = getAtoms(50); // Last 50 atoms
        const totalAtoms = getAtomCount();
        const coverage = getCoverageReport();

        // Build the reflection context
        const systemState = buildReflectionContext(recentAtoms, totalAtoms, coverage);
        const prompt = PARADIGM_REFLECTION_PROMPT + systemState;

        // Send to Scout
        const result = await atomize(prompt, 'meta-reflection');

        // Tag all resulting atoms as meta-atoms
        const metaAtoms = (result.atoms || []).map(a => ({
            ...a,
            type: ['meta_pattern', 'synthesis', 'emergence'].includes(a.type) ? a.type : 'meta_pattern',
            framework_layer: 'META',
            themes: [...new Set([...(a.themes || []), 'meta_reflection', 'paradigm_assessment'])],
        }));

        // Store meta-atoms (they go into the same atoms.jsonl — self-referential)
        const stored = storeAtoms(metaAtoms, 'meta-reflector');

        // Save reflection record
        const reflection = {
            timestamp: new Date().toISOString(),
            atom_count: stored.length,
            total_atoms_at_time: totalAtoms,
            coverage_score: coverage?.overall_score || 0,
            coverage_breadth: coverage?.metrics?.breadth?.value || 0,
            model: result.model,
            elapsed_ms: result.elapsed_ms,
            insights: stored.map(a => a.content),
        };

        fs.appendFileSync(REFLECTIONS_FILE, JSON.stringify(reflection) + '\n', 'utf-8');

        lastReflection = reflection;
        atomsSinceLastReflection = 0;

        logEvent('success', `Reflector: ${stored.length} meta-atoms produced (paradigm health assessment)`);

        return reflection;
    } catch (err) {
        logEvent('error', `Reflector: Reflection failed — ${err.message}`);
        return { status: 'error', error: err.message };
    } finally {
        reflecting = false;
    }
}

/**
 * Build the context string for the reflection prompt.
 */
function buildReflectionContext(recentAtoms, totalAtoms, coverage) {
    const lines = [];

    // Atom statistics
    lines.push(`Total atoms in system: ${totalAtoms}`);
    lines.push(`Atoms since last reflection: ${atomsSinceLastReflection}`);
    lines.push('');

    // Type distribution
    const typeCounts = {};
    recentAtoms.forEach(a => {
        typeCounts[a.type] = (typeCounts[a.type] || 0) + 1;
    });
    lines.push('Recent atom type distribution:');
    Object.entries(typeCounts).sort((a, b) => b[1] - a[1]).forEach(([type, count]) => {
        lines.push(`  ${type}: ${count}`);
    });
    lines.push('');

    // Confidence distribution
    if (recentAtoms.length > 0) {
        const avgConf = recentAtoms.reduce((s, a) => s + (a.confidence || 0), 0) / recentAtoms.length;
        const highConf = recentAtoms.filter(a => (a.confidence || 0) > 0.9).length;
        const lowConf = recentAtoms.filter(a => (a.confidence || 0) < 0.6).length;
        lines.push(`Average confidence: ${(avgConf * 100).toFixed(1)}%`);
        lines.push(`High confidence (>90%): ${highConf}`);
        lines.push(`Low confidence (<60%): ${lowConf}`);
        lines.push('');
    }

    // Coverage metrics
    if (coverage && coverage.metrics) {
        lines.push('Coverage metrics:');
        lines.push(`  Breadth: ${coverage.metrics.breadth.value}% (target: ${coverage.metrics.breadth.target}%)`);
        lines.push(`  Depth: ${coverage.metrics.depth.value} atoms/file (target: ${coverage.metrics.depth.target})`);
        lines.push(`  Freshness: ${coverage.metrics.freshness.value}% (target: ${coverage.metrics.freshness.target}%)`);
        lines.push(`  Overall score: ${coverage.overall_score}/100`);
        lines.push(`  Dark zones: ${(coverage.dark_zones || []).length} directories with 0% coverage`);
        lines.push('');
    }

    // Sample recent atoms (5 examples for context)
    lines.push('Sample recent atoms:');
    recentAtoms.slice(0, 5).forEach((a, i) => {
        lines.push(`  ${i + 1}. [${a.type}] "${(a.content || '').slice(0, 120)}..." (confidence: ${a.confidence})`);
    });
    lines.push('');

    // Core/Supportive/Meta architectural assessment request
    lines.push('ARCHITECTURAL TRIAD SERVICE REGISTRY:');
    try {
        const triadStatus = getTriadStatus();
        const h = triadStatus.health;
        lines.push(`  Triad Complete: ${h.complete ? 'YES' : 'NO'}`);
        lines.push(`  Balance Score: ${h.balance_score}%`);
        lines.push(`  Core services: ${h.core_count} | Supportive: ${h.supportive_count} | Meta: ${h.meta_count}`);
        for (const [layer, data] of Object.entries(triadStatus.pillars)) {
            lines.push(`  ${layer}: ${data.services.map(s => s.name).join(', ') || 'none'}`);
        }
    } catch {
        lines.push('  Triad registry not yet initialized');
    }
    lines.push('');
    lines.push('ASSESS: Does the Triad pattern appear throughout the codebase? Where is it incomplete?');

    return lines.join('\n');
}

/**
 * Notify the reflector that new atoms have been produced.
 * Call this from the watcher/atomizer after storing atoms.
 * Triggers reflection when threshold is reached.
 */
export function notifyNewAtoms(count) {
    atomsSinceLastReflection += count;

    if (atomsSinceLastReflection >= ATOM_THRESHOLD && !reflecting) {
        logEvent('info', `Reflector: Atom threshold (${ATOM_THRESHOLD}) reached — triggering reflection`);
        reflect().catch(err => {
            logEvent('error', `Reflector auto-trigger failed: ${err.message}`);
        });
    }
}

/**
 * Start periodic reflection.
 */
export function startReflector(intervalMs = REFLECTION_INTERVAL_MS) {
    if (reflectionInterval) return { status: 'already_running' };

    // First reflection after 5 minutes (let atoms accumulate)
    setTimeout(() => {
        reflect().catch(err => {
            logEvent('error', `Initial reflection failed: ${err.message}`);
        });
    }, 5 * 60 * 1000);

    // Periodic reflection
    reflectionInterval = setInterval(() => {
        reflect().catch(err => {
            logEvent('error', `Reflection cycle failed: ${err.message}`);
        });
    }, intervalMs);

    logEvent('info', `Paradigm reflector started (interval: ${intervalMs / 60000}min)`);
    return { status: 'started', interval_ms: intervalMs };
}

export function stopReflector() {
    if (reflectionInterval) {
        clearInterval(reflectionInterval);
        reflectionInterval = null;
    }
    return { status: 'stopped' };
}

export function getReflectorStatus() {
    return {
        active: reflectionInterval !== null,
        reflecting,
        atoms_since_last: atomsSinceLastReflection,
        atom_threshold: ATOM_THRESHOLD,
        last_reflection: lastReflection,
    };
}

export function getReflectionInsights(limit = 10) {
    if (!fs.existsSync(REFLECTIONS_FILE)) return [];
    const content = fs.readFileSync(REFLECTIONS_FILE, 'utf-8').trim();
    if (!content) return [];
    return content.split('\n')
        .map(line => { try { return JSON.parse(line); } catch { return null; } })
        .filter(Boolean)
        .slice(-limit)
        .reverse();
}
