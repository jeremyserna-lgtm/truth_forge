/* global process */
// Genesis Console — Scout Atomizer
// TRIAD: CORE (execution engine) | FEDERATION: PRIMITIVE ENGINE | RECURSION: DEVELOPER
// "I build the bridge." Extracts knowledge atoms from raw content via Scout.
import { logEvent } from './store.js';

const OLLAMA_URL = process.env.OLLAMA_URL || 'http://localhost:11434';
const SCOUT_MODEL = process.env.SCOUT_MODEL || 'llama4-scout';

// The atomization prompt — ontology-aware, engineered to produce structured JSON atoms
const ATOMIZE_PROMPT = `You are a Knowledge Atomizer operating within the Three Ontological Roles framework. Your task is to extract irreducible knowledge atoms from the provided content.

THE THREE ONTOLOGICAL ROLES:
  Triad = Structure (Anatomy) — "Is this robust?"
  Recursion = Energy (Metabolism) — "Is this alive?"
  Federation = Agency — "Who is acting?"

PILLAR 1 — ARCHITECTURAL TRIAD (Structure):
When you encounter content about systems, architectures, or processes, identify which layer it belongs to:
- CORE: Foundational infrastructure, immutable data, execution sandboxes, primary functions
- SUPPORTIVE: Specialized task-layers, coverage, quality assurance, helper services
- META: Governing logic, behavioral rules, self-awareness, incentive alignment

PILLAR 2 — RECURSIVE MAGNIFICATION (Energy):
Flag content about self-spawning, recursive growth, agent hierarchies, multi-phase operations.
Systems that modify their own architecture are ALIVE.

PILLAR 3 — FEDERATION OF SOVEREIGNS (Agency):
When content involves action, ask "who is acting?"
- TRUTH_FORGE: State maintenance, identity, the golden record — "I hold the soul"
- PRIMITIVE_ENGINE: Execution, building, code modification — "I build the bridge"
- CREDENTIAL_ATLAS: Verification, scoring, observation — "I verify existence"

For each atom, classify it as one of these types:
- fact: A verifiable statement
- concept: An idea or abstraction
- relationship: A connection between entities
- directive: An instruction or rule
- pattern: A recurring structure
- emergence: An insight that exists only at the intersection of ideas (compound)
- contradiction: A conflict that reveals something (compound)
- amplification: Where one thing strengthens another (compound)
- meta_pattern: A pattern visible only across boundaries (compound)
- synthesis: New understanding from combining ideas (compound)

Return ONLY a JSON array of atoms. Each atom must have:
{
  "type": "<atom_type>",
  "content": "<the atomic statement — one clear sentence>",
  "confidence": <0.0 to 1.0>,
  "entities": ["<entity1>", "<entity2>"],
  "themes": ["<theme1>", "<theme2>"],
  "framework_layer": "CORE" | "SUPPORTIVE" | "META" | null,
  "sovereign": "TRUTH_FORGE" | "PRIMITIVE_ENGINE" | "CREDENTIAL_ATLAS" | null
}

Set framework_layer when the atom clearly relates to a specific Triad layer.
Set sovereign when the atom relates to a specific Federation organ's domain.
Leave null if unclear.
Extract as many atoms as the content warrants. Be thorough.

CONTENT TO ATOMIZE:
`;

/**
 * List available Ollama models to find Scout
 */
async function findScoutModel() {
    try {
        const res = await fetch(`${OLLAMA_URL}/api/tags`, {
            signal: AbortSignal.timeout(5000),
        });
        if (!res.ok) throw new Error(`Ollama HTTP ${res.status}`);
        const data = await res.json();
        const models = (data.models || []).map(m => m.name);

        // Try to find Scout or any available model
        const scoutNames = ['llama4-scout', 'scout', 'llama4', 'llama-4-scout'];
        for (const name of scoutNames) {
            const found = models.find(m => m.toLowerCase().includes(name));
            if (found) return found;
        }

        // Fall back to first available model
        if (models.length > 0) {
            logEvent('warn', `Scout not found, using fallback model: ${models[0]}`);
            return models[0];
        }

        return null;
    } catch (err) {
        logEvent('warn', `Cannot reach Ollama, using fallback atomizer path: ${err.message}`);
        return null;
    }
}

/**
 * Send content to Scout via Ollama and extract knowledge atoms
 */
export async function atomize(content, filename = 'unknown') {
    logEvent('info', `Atomizer: Processing ${filename} (${content.length} chars)`);

    // Find available model
    const model = await findScoutModel();
    if (!model) {
        const fallbackStart = Date.now();
        const fallbackAtoms = fallbackAtomize(content);
        logEvent('warn', `Atomizer: Ollama unavailable, fallback atomizer produced ${fallbackAtoms.length} atoms`);
        return {
            atoms: fallbackAtoms,
            model: 'local-fallback-heuristic',
            elapsed_ms: Date.now() - fallbackStart,
            input_chars: content.length,
            raw_response: null,
            degraded: true,
        };
    }

    logEvent('info', `Atomizer: Using model "${model}"`);

    const prompt = ATOMIZE_PROMPT + content;

    // Call Ollama generate endpoint
    const startTime = Date.now();
    const res = await fetch(`${OLLAMA_URL}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            model: model,
            prompt: prompt,
            stream: false,
            options: {
                temperature: 0.3,       // Low temp for factual extraction
                num_predict: 4096,      // Enough room for atom output
            },
        }),
        signal: AbortSignal.timeout(120000), // 2 minute timeout for large files
    });

    if (!res.ok) {
        const errText = await res.text().catch(() => 'unknown error');
        throw new Error(`Ollama error: HTTP ${res.status} — ${errText}`);
    }

    const data = await res.json();
    const elapsed = Date.now() - startTime;
    logEvent('info', `Atomizer: Response received in ${elapsed}ms`);

    // Parse atoms from response
    const atoms = parseAtoms(data.response || '');
    logEvent('info', `Atomizer: Extracted ${atoms.length} atoms from ${filename}`);

    return {
        atoms,
        model,
        elapsed_ms: elapsed,
        input_chars: content.length,
        raw_response: data.response,
    };
}

/**
 * Parse JSON atoms from Scout's response.
 * Handles various response formats (with/without markdown fencing, etc.)
 */
function parseAtoms(response) {
    if (!response || !response.trim()) return [];

    let text = response.trim();

    // Remove markdown code fencing if present
    text = text.replace(/^```json\s*/i, '').replace(/^```\s*/i, '').replace(/\s*```$/i, '');

    // Try to find JSON array in the response
    const arrayMatch = text.match(/\[[\s\S]*\]/);
    if (arrayMatch) {
        try {
            const parsed = JSON.parse(arrayMatch[0]);
            if (Array.isArray(parsed)) {
                return parsed.map(validateAtom).filter(Boolean);
            }
        } catch {
            logEvent('warn', `Atomizer: JSON parse failed, attempting line-by-line`);
        }
    }

    // Try line-by-line JSON objects
    const atoms = [];
    const lines = text.split('\n');
    for (const line of lines) {
        const objMatch = line.match(/\{[\s\S]*\}/);
        if (objMatch) {
            try {
                const obj = JSON.parse(objMatch[0]);
                const valid = validateAtom(obj);
                if (valid) atoms.push(valid);
            } catch { /* skip */ }
        }
    }

    return atoms;
}

function fallbackAtomize(content) {
    if (!content || !content.trim()) return [];
    const cleanedLines = content
        .split('\n')
        .map((line) => line.trim())
        .filter((line) => line.length >= 24)
        .filter((line) => !line.startsWith('```'))
        .filter((line) => !/^\d+\.$/.test(line))
        .slice(0, 180);

    const seen = new Set();
    const atoms = [];

    for (const line of cleanedLines) {
        const normalized = line.replace(/\s+/g, ' ').trim();
        if (seen.has(normalized.toLowerCase())) continue;
        seen.add(normalized.toLowerCase());

        const atom = {
            type: classifyFallbackType(normalized),
            content: normalized,
            confidence: fallbackConfidence(normalized),
            entities: extractEntities(normalized),
            themes: detectThemes(normalized),
            framework_layer: classifyTriadLayer(normalized),
            framework_dimension: null,
            compound_depth: 0,
        };
        atoms.push(atom);
        if (atoms.length >= 80) break;
    }

    return atoms;
}

function classifyFallbackType(line) {
    const lower = line.toLowerCase();
    if (/(must|should|need to|required|do not|never|always|policy)/.test(lower)) return 'directive';
    if (/(because|therefore|leads to|causes|enables|supports|depends on|drives)/.test(lower)) return 'relationship';
    if (/(pattern|architecture|framework|protocol|workflow|pipeline|loop|triad)/.test(lower)) return 'pattern';
    if (/^[#-*]\s/.test(line) || /^[A-Z0-9 _-]{8,}$/.test(line)) return 'concept';
    return 'fact';
}

/**
 * Classify which Triad layer a line of content belongs to.
 * Returns CORE, SUPPORTIVE, META, or null.
 */
function classifyTriadLayer(line) {
    const lower = line.toLowerCase();
    // META indicators: governance, reflection, self-awareness, behavioral rules
    if (/(meta|reflect|govern|incentive|behavioral|self-aware|paradigm|consensus|audit|sentinel)/.test(lower)) return 'META';
    // SUPPORTIVE indicators: coverage, validation, quality, monitoring, assist
    if (/(coverage|validation|quality|monitor|assist|support|gap|assess|recovery|synthetic|helper)/.test(lower)) return 'SUPPORTIVE';
    // CORE indicators: store, persist, execute, process, immutable, foundation, pipeline
    if (/(store|persist|execute|process|immutable|foundation|pipeline|atom|extract|core|engine|hold)/.test(lower)) return 'CORE';
    return null;
}

function fallbackConfidence(line) {
    const lengthFactor = Math.min(0.18, line.length / 500);
    return Number((0.54 + lengthFactor).toFixed(2));
}

function extractEntities(line) {
    const matches = line.match(/\b[A-Z][a-zA-Z0-9_-]{2,}\b/g) || [];
    return [...new Set(matches)].slice(0, 6);
}

function detectThemes(line) {
    const lower = line.toLowerCase();
    const mapping = [
        ['kiosk', 'kiosk'],
        ['mission', 'mission'],
        ['governance', 'governance'],
        ['pipeline', 'pipeline'],
        ['memory', 'memory'],
        ['model', 'models'],
        ['revenue', 'revenue'],
        ['handover', 'handover'],
        ['sentinel', 'sentinel'],
        ['training', 'training'],
        ['bootstrap', 'bootstrap'],
        ['api', 'integration'],
        ['triad', 'architectural_triad'],
        ['core', 'triad_core'],
        ['supportive', 'triad_supportive'],
        ['meta', 'triad_meta'],
        ['sovereign', 'sovereignty'],
        ['immutable', 'persistence'],
        ['atom', 'knowledge_atoms'],
        ['coverage', 'coverage'],
        ['reflect', 'meta_reflection'],
    ];
    const themes = mapping
        .filter(([keyword]) => lower.includes(keyword))
        .map(([, theme]) => theme);
    return [...new Set(themes)].slice(0, 6);
}

/**
 * Validate and normalize an atom object
 */
function validateAtom(obj) {
    if (!obj || typeof obj !== 'object') return null;
    if (!obj.content && !obj.text) return null;

    const validTypes = [
        'fact', 'concept', 'relationship', 'directive', 'pattern',
        'emergence', 'contradiction', 'amplification', 'meta_pattern', 'synthesis',
    ];

    return {
        type: validTypes.includes(obj.type) ? obj.type : 'fact',
        content: String(obj.content || obj.text || '').trim(),
        confidence: Math.min(1, Math.max(0, Number(obj.confidence || obj.conf) || 0.8)),
        entities: Array.isArray(obj.entities) ? obj.entities : [],
        themes: Array.isArray(obj.themes) ? obj.themes : [],
        framework_layer: obj.framework_layer || null,
        framework_dimension: obj.framework_dimension || null,
        compound_depth: ['emergence', 'contradiction', 'amplification', 'meta_pattern', 'synthesis']
            .includes(obj.type) ? 1 : 0,
    };
}

/**
 * Check if Ollama is available
 */
export async function checkOllama() {
    try {
        const res = await fetch(`${OLLAMA_URL}/api/tags`, {
            signal: AbortSignal.timeout(3000),
        });
        if (!res.ok) return { connected: false, models: [] };
        const data = await res.json();
        return {
            connected: true,
            models: (data.models || []).map(m => ({
                name: m.name,
                size: m.size,
            })),
        };
    } catch {
        return { connected: false, models: [] };
    }
}
