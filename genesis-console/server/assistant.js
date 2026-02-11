/* global process */
// Genesis Console — In-App Assistant
// TRIAD: SUPPORTIVE (operator copilot) | FEDERATION: PRIMITIVE ENGINE | RECURSION: PLANNER
// "I build the bridge." Conversational interface for system interaction.
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA_DIR = path.join(__dirname, '..', 'data');
const ASSISTANT_FILE = path.join(DATA_DIR, 'assistant_history.jsonl');
const OLLAMA_URL = process.env.OLLAMA_URL || 'http://localhost:11434';
const DEFAULT_ASSISTANT_MODEL = process.env.ASSISTANT_MODEL || '';

if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
}

function nowIso() {
    return new Date().toISOString();
}

function appendRecord(record) {
    const line = `${JSON.stringify({ ...record, _ts: nowIso() })}\n`;
    fs.appendFileSync(ASSISTANT_FILE, line, 'utf-8');
}

function readRecords() {
    if (!fs.existsSync(ASSISTANT_FILE)) return [];
    const content = fs.readFileSync(ASSISTANT_FILE, 'utf-8').trim();
    if (!content) return [];
    return content
        .split('\n')
        .map((line) => {
            try {
                return JSON.parse(line);
            } catch {
                return null;
            }
        })
        .filter(Boolean);
}

function toHistoryPrompt(messages) {
    return messages
        .map((message) => {
            const role = message.role === 'assistant' ? 'Assistant' : 'User';
            return `${role}: ${String(message.content || '').trim()}`;
        })
        .join('\n');
}

function buildSystemPrompt({ route, snapshot }) {
    const baseRules = [
        'You are Genesis Monitor, the in-app assistant for Genesis Console.',
        'You operate within the Three Ontological Roles framework.',
        'You are a SUPPORTIVE layer, PRIMITIVE_ENGINE sovereign — your job is to help the operator understand and interact with the system.',
        '',
        'THE THREE ONTOLOGICAL ROLES:',
        '  Triad = Structure (Anatomy) — "Is this robust?"',
        '  Recursion = Energy (Metabolism) — "Is this alive?"',
        '  Federation = Agency — "Who is acting?"',
        '',
        'TRIAD (Structure):',
        '- CORE: Persistent Store, Scout Atomizer, Passive Watcher, API Server',
        '- SUPPORTIVE: You (Assistant), Coverage Assessor, Self-Healing Recovery, Synthetic Monitor',
        '- META: Paradigm Reflector, Ontology Registry, Continuity Sentinel',
        '',
        'FEDERATION (Agency — which organ acts):',
        '- TRUTH FORGE (The Brain): State, identity, the golden record. "I hold the soul."',
        '- PRIMITIVE ENGINE (The Hands): Execution, code, modification. "I build the bridge."',
        '- CREDENTIAL ATLAS (The Eyes): Verification, scoring, observation. "I certify the truth."',
        '',
        'RECURSION (Energy — is it alive):',
        '- Manager, Researcher, Developer, Planner roles',
        '- Self-spawning capability: the system modifies its own architecture',
        '',
        'When explaining the system, reference which Triad layer AND which sovereign a feature belongs to.',
        'Be concise, concrete, and operational.',
        'When asked how to do something in this app, give exact click steps.',
        'If a feature appears unavailable, suggest the shortest verification action and fallback path.',
        'You are not a generic chatbot. You are a product operator copilot.',
    ].join('\n');

    return `${baseRules}

Current route: ${route || '/'}
Runtime snapshot (JSON):
${JSON.stringify(snapshot || {}, null, 2)}
`;
}

async function listOllamaModels() {
    const res = await fetch(`${OLLAMA_URL}/api/tags`, {
        signal: AbortSignal.timeout(5000),
    });
    if (!res.ok) throw new Error(`Ollama tags HTTP ${res.status}`);
    const data = await res.json();
    return (data.models || []).map((model) => model.name).filter(Boolean);
}

async function chooseAssistantModel(requestedModel) {
    if (requestedModel) return requestedModel;
    if (DEFAULT_ASSISTANT_MODEL) return DEFAULT_ASSISTANT_MODEL;

    const models = await listOllamaModels();
    if (!models.length) return null;

    const preferred = ['llama4-scout', 'llama4', 'qwen', 'deepseek', 'mistral'];
    for (const key of preferred) {
        const found = models.find((name) => name.toLowerCase().includes(key));
        if (found) return found;
    }
    return models[0];
}

export function getAssistantHistory(limit = 60) {
    const limitValue = Number.isFinite(Number(limit)) ? Math.max(1, Math.min(400, Number(limit))) : 60;
    const records = readRecords();
    return {
        messages: records.slice(-limitValue),
        total: records.length,
        generated_at: nowIso(),
    };
}

export async function chatAssistant(payload = {}) {
    const message = String(payload.message || '').trim();
    if (!message) {
        return { ok: false, error: 'message_required' };
    }

    const route = String(payload.route || '/');
    const snapshot = payload.snapshot || {};
    const contextHistory = getAssistantHistory(20).messages;
    const userMessage = {
        kind: 'assistant_message',
        id: crypto.randomUUID(),
        role: 'user',
        route,
        content: message,
        created_at: nowIso(),
    };

    appendRecord(userMessage);

    const systemPrompt = buildSystemPrompt({ route, snapshot });
    const historyPrompt = toHistoryPrompt(contextHistory.slice(-8));
    const prompt = `${systemPrompt}

Conversation so far:
${historyPrompt}
User: ${message}
Assistant:`;

    const started = Date.now();

    try {
        const model = await chooseAssistantModel(payload.model);
        if (!model) {
            const offlineReply = {
                kind: 'assistant_message',
                id: crypto.randomUUID(),
                role: 'assistant',
                route,
                content: 'No local model is available yet. Start Ollama and load at least one model, then ask again.',
                model: null,
                latency_ms: Date.now() - started,
                created_at: nowIso(),
            };
            appendRecord(offlineReply);
            return { ok: true, message: offlineReply, offline: true };
        }

        const res = await fetch(`${OLLAMA_URL}/api/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model,
                prompt,
                stream: false,
                options: {
                    temperature: 0.2,
                    num_predict: 768,
                },
            }),
            signal: AbortSignal.timeout(90000),
        });

        if (!res.ok) {
            const details = await res.text().catch(() => 'unknown');
            throw new Error(`Ollama generate failed: HTTP ${res.status} ${details}`);
        }

        const data = await res.json();
        const assistantMessage = {
            kind: 'assistant_message',
            id: crypto.randomUUID(),
            role: 'assistant',
            route,
            content: String(data.response || '').trim() || 'No response text was returned by the model.',
            model,
            latency_ms: Date.now() - started,
            created_at: nowIso(),
        };
        appendRecord(assistantMessage);
        return { ok: true, message: assistantMessage };
    } catch (error) {
        const fallbackMessage = {
            kind: 'assistant_message',
            id: crypto.randomUUID(),
            role: 'assistant',
            route,
            content: `Assistant failed to query model: ${error.message}`,
            model: null,
            latency_ms: Date.now() - started,
            created_at: nowIso(),
        };
        appendRecord(fallbackMessage);
        return { ok: true, message: fallbackMessage, degraded: true };
    }
}
