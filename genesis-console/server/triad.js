// Genesis Console — The Three Ontological Roles (META LAYER)
// =============================================================
// This module encodes the complete ontological framework from three research papers:
//
//   1. "The Architectural Triad" .............. STRUCTURE (Anatomy)
//      Core / Supportive / Meta
//      Answers: "Is this robust?"
//
//   2. "Recursive Magnification" .............. ENERGY (Metabolism)
//      Self-spawning agents, sequential thinking, surplus value generation
//      Answers: "Is this alive?"
//
//   3. "The Federation of Sovereigns" ......... AGENCY (Who acts)
//      Truth Forge / Primitive Engine / Credential Atlas
//      Answers: "Who is acting?"
//
// Together they form the complete DNA of sovereign intelligence.
// Every service declares all three dimensions.
// The system knows how it's built, how it grows, and who is doing the work.

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { logEvent } from './store.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA_DIR = path.join(__dirname, '..', 'data');
const TRIAD_FILE = path.join(DATA_DIR, 'triad.json');

// ═══════════════════════════════════════════════════════
// PILLAR 1: THE ARCHITECTURAL TRIAD — STRUCTURE (Anatomy)
// "Is this robust?"
// ═══════════════════════════════════════════════════════

export const TRIAD_LAYERS = {
    CORE: {
        name: 'Core',
        definition: 'Foundational Infrastructure',
        function: 'Immutable anchor and execution sandbox',
        metaphor: 'The skeleton and organs — the thing itself',
        principles: [
            'Provides the immutable substrate upon which all else runs',
            'Environment isolation — rogue code cannot compromise the host',
            'Sovereign operation without external interference',
            'Append-only data stores (HOLD₁, HOLD₂) ensure truth persistence',
            'The Core cannot be changed by the Supportive or Meta layers',
        ],
        strategic_imperative: 'Core implementation addresses the duality of sovereignty: '
            + 'Global Truth through distributed ledgering, Local Safety through sandboxed execution.',
    },
    SUPPORTIVE: {
        name: 'Supportive',
        definition: 'Specialized Task-Layers',
        function: 'Marketplace for specialized AI commodities and coverage assurance',
        metaphor: 'The muscles and circulation — the functional capacity',
        principles: [
            'Distills generalized intelligence into high-performance specialized value',
            'Prevents monopolies by creating permissionless competition on merit',
            'Modular: niche high-performance nodes out-compete generalized models',
            'Coverage assessment ensures the Core layer reaches everywhere it should',
            'Quality scoring validates that production meets target thresholds',
        ],
        strategic_imperative: 'By modularizing the Supportive layer, we move away from black-box '
            + 'monolithic models. Utility remains the primary driver of the ecosystem.',
    },
    META: {
        name: 'Meta',
        definition: 'Governing Logic',
        function: 'Incentive protocols, behavioral alignment, and self-awareness',
        metaphor: 'The nervous system and conscience — the governor',
        principles: [
            'The connective tissue ensuring alignment between participants and objectives',
            'Governs interactions through mathematically enforced incentives',
            'Behavioral constraints via authoritative Markdown: the .md file is sovereign',
            'Self-spawning capability: the system can modify its own architecture',
            'The Meta layer handles bad actors through consensus-alignment and behavioral rules',
            'Human intervention remains prerequisite for high-stakes decisions',
        ],
        strategic_imperative: 'Sovereign intelligence acts as a verifiable agent. '
            + 'The machine must tell how it gets to its conclusions.',
    },
};

// ═══════════════════════════════════════════════════════════
// PILLAR 2: RECURSIVE MAGNIFICATION — ENERGY (Metabolism)
// "Is this alive?"
// ═══════════════════════════════════════════════════════════

export const RECURSIVE_MAGNIFICATION = {
    definition: 'The process by which a lead agent autonomously spawns specialized subordinate agents, '
        + 'transforming the Not-Me from a static tool into a self-evolving, multi-agent digital organism.',
    question: 'Is this alive?',
    metaphor: 'Metabolism — the generation and spending of energy to create surplus value',
    roles: {
        MANAGER: {
            name: 'Manager Agent (Agent Zero)',
            function: 'Autonomous, JSON-driven lead. Executes authoritative behavioral rules to manage the overarching mission.',
        },
        RESEARCHER: {
            name: 'Researcher',
            function: 'High-velocity data ingestion and pattern recognition.',
        },
        DEVELOPER: {
            name: 'Developer',
            function: 'Complex coding within isolated, root-permissioned environments.',
        },
        PLANNER: {
            name: 'Sequential Planner',
            function: 'Lead strategist for multi-phase operations using Sequential Thinking MCP.',
        },
    },
    drivers: {
        technical_persistence: 'Restart-always flags and recurring task schedules — the system operates even when the user is offline.',
        economic_persistence: 'Tokenomics with 21M cap and stock-to-flow predictability ensure incentives remain viable over decades.',
        self_spawning: 'Agents that modify their own architecture. The system evolves its logic and task-layers without manual reconfiguration.',
    },
    engine: 'Sequential Thinking Model Context Protocol (MCP) — breaks Grand Challenges into distinct phases, '
        + 'executing a self-coding loop where the agent spawns infrastructure to audit its own research.',
    strategic_imperative: 'Sovereignty is dynamic. The Not-Me must manage escalating complexity without granular human intervention. '
        + 'Static tools die. Recursive organisms adapt.',
};

// ═════════════════════════════════════════════════════════════
// PILLAR 3: THE FEDERATION OF SOVEREIGNS — AGENCY (Who Acts)
// "Who is acting?"
// ═════════════════════════════════════════════════════════════

export const FEDERATION_OF_SOVEREIGNS = {
    definition: 'The system is not one company; it is an organism with three distinct organs that trade with each other. '
        + 'Each sovereign dictates the Cognitive Stance of the Not-Me in any given moment.',
    question: 'Who is acting?',
    metaphor: 'Agency — the assignment of responsibility to a specific organ of the organism',
    sovereigns: {
        TRUTH_FORGE: {
            name: 'Truth Forge',
            role: 'The Source (The Brain)',
            title: 'The Unmoved Mover',
            function: 'Holds the Golden Record and the Frozen Core (Genesis). '
                + 'Provides the Substrate (Hardware/Empire Cluster) and the Life (Heartbeat). '
                + 'It does not "do" the work; it IS the existence.',
            stance: 'I hold the soul. I maintain the state.',
            cognitive_domain: 'Identity and State',
        },
        PRIMITIVE_ENGINE: {
            name: 'Primitive Engine',
            role: 'The Builder (The Hands)',
            title: 'The Active Principle',
            function: 'Executes Inter-AI Labor. When code needs writing, files need moving, or architectures '
                + 'need constructing (The Anvil), this entity clocks in. '
                + 'The only part of the system allowed to modify the world.',
            stance: 'I build the bridge. I execute the will.',
            cognitive_domain: 'Execution and Code',
        },
        CREDENTIAL_ATLAS: {
            name: 'Credential Atlas',
            role: 'The Seer (The Eyes)',
            title: 'The Truth Principle',
            function: 'Certifies that the Builder did the job correctly. '
                + 'Provides the Metacognitive Credential and the Proof of State. '
                + 'Never modifies; only observes and scores.',
            stance: 'I verify existence. I certify the truth.',
            cognitive_domain: 'Verification and Analysis',
        },
    },
    departure_protocol: {
        directive: 'Do not just ask the system to "do X." Name the Sovereign.',
        identity_state: 'Invoke Truth Forge',
        execution_code: 'Invoke Primitive Engine',
        verification_analysis: 'Invoke Credential Atlas',
        why: 'By naming the Sovereign, you constrain the action. '
            + 'You prevent the Builder from hallucinating truth, '
            + 'and you prevent the Seer from breaking code.',
    },
    strategic_imperative: 'You are not running one company; you are running an organism. '
        + 'The three sovereigns trade with each other, each constrained to its cognitive domain.',
};

// ═══════════════════════════════════════════════
// THE THREE ONTOLOGICAL ROLES — UNIFIED FRAMEWORK
// ═══════════════════════════════════════════════

export const ONTOLOGY = {
    name: 'The Three Ontological Roles',
    summary: 'Triad = Structure. Recursion = Energy. Federation = Agency.',
    roles: {
        STRUCTURE: {
            framework: 'Architectural Triad',
            question: 'Is this robust?',
            metaphor: 'Anatomy',
            detail: TRIAD_LAYERS,
        },
        ENERGY: {
            framework: 'Recursive Magnification',
            question: 'Is this alive?',
            metaphor: 'Metabolism',
            detail: RECURSIVE_MAGNIFICATION,
        },
        AGENCY: {
            framework: 'Federation of Sovereigns',
            question: 'Who is acting?',
            metaphor: 'Agency',
            detail: FEDERATION_OF_SOVEREIGNS,
        },
    },
    sources: [
        'The Architectural Triad: A Framework for Autonomous and Persistent AI Systems',
        'The Architecture of Sovereignty: Recursive Synthesis and the Governance of the Not-Me',
        'The Federation of Sovereigns: The Agency of Truth',
    ],
    axioms: {
        total_residence: 'True sovereignty mandates Total Residence — the Not-Me must reside within locally controlled infrastructure.',
        intention_driven: 'The Not-Me is a Partner, not a Truth Engine. A high-agency Me provides the North Star.',
        multi_instance_review: 'Deploy two Not-Mes to audit each other — the hallucination guardrail.',
        transparency: 'The machine must tell how it gets to its conclusions. Provide the audit trail.',
        ethical_guardrails: 'Human intervention remains prerequisite for high-stakes decisions.',
    },
};

// ─── Service Registry ───
// Every service declares three dimensions:
//   1. Triad layer (Structure)
//   2. Federation sovereign (Agency)
//   3. Recursive role (Energy)

const registry = new Map();

/**
 * Register a service with the full ontological framework.
 * Every service must declare its Triad layer, and may optionally
 * declare its Federation sovereign and recursive role.
 */
export function registerService(id, config) {
    const {
        layer,           // Triad: CORE | SUPPORTIVE | META
        name,
        purpose,
        sovereign,       // Federation: TRUTH_FORGE | PRIMITIVE_ENGINE | CREDENTIAL_ATLAS
        recursiveRole,   // Magnification: MANAGER | RESEARCHER | DEVELOPER | PLANNER | null
        healthCheck,
        dependencies,
    } = config;

    if (!TRIAD_LAYERS[layer]) {
        throw new Error(`Invalid Triad layer: ${layer}. Must be CORE, SUPPORTIVE, or META.`);
    }

    registry.set(id, {
        id,
        layer,
        name,
        purpose,
        sovereign: sovereign || null,
        recursiveRole: recursiveRole || null,
        healthCheck: healthCheck || (() => ({ healthy: true })),
        dependencies: dependencies || [],
        registered_at: new Date().toISOString(),
        status: 'registered',
    });

    const sovLabel = sovereign ? ` sovereign=${sovereign}` : '';
    const recLabel = recursiveRole ? ` recursive=${recursiveRole}` : '';
    logEvent('info', `Ontology: ${layer}/${name} registered (${id})${sovLabel}${recLabel}`);
    return registry.get(id);
}

/**
 * Get the full ontological status — covering all three pillars.
 */
export function getTriadStatus() {
    const services = {};

    for (const [layer, definition] of Object.entries(TRIAD_LAYERS)) {
        const layerServices = [...registry.values()].filter(s => s.layer === layer);
        services[layer] = {
            ...definition,
            services: layerServices.map(s => ({
                id: s.id,
                name: s.name,
                purpose: s.purpose,
                status: s.status,
                sovereign: s.sovereign,
                recursiveRole: s.recursiveRole,
                registered_at: s.registered_at,
            })),
            service_count: layerServices.length,
        };
    }

    // Triad completeness
    const coreSvc = services.CORE.service_count;
    const suppSvc = services.SUPPORTIVE.service_count;
    const metaSvc = services.META.service_count;
    const hasAll = coreSvc > 0 && suppSvc > 0 && metaSvc > 0;
    const balance = hasAll
        ? Math.round((Math.min(coreSvc, suppSvc, metaSvc) / Math.max(coreSvc, suppSvc, metaSvc)) * 100)
        : 0;

    // Federation coverage
    const allServices = [...registry.values()];
    const federationCoverage = {
        truth_forge: allServices.filter(s => s.sovereign === 'TRUTH_FORGE').length,
        primitive_engine: allServices.filter(s => s.sovereign === 'PRIMITIVE_ENGINE').length,
        credential_atlas: allServices.filter(s => s.sovereign === 'CREDENTIAL_ATLAS').length,
        unassigned: allServices.filter(s => !s.sovereign).length,
    };

    // Recursive role distribution
    const recursiveRoles = {
        manager: allServices.filter(s => s.recursiveRole === 'MANAGER').length,
        researcher: allServices.filter(s => s.recursiveRole === 'RESEARCHER').length,
        developer: allServices.filter(s => s.recursiveRole === 'DEVELOPER').length,
        planner: allServices.filter(s => s.recursiveRole === 'PLANNER').length,
        unassigned: allServices.filter(s => !s.recursiveRole).length,
    };

    return {
        framework: 'The Three Ontological Roles',
        source: 'Triad = Structure. Recursion = Energy. Federation = Agency.',
        sources: ONTOLOGY.sources,
        pillars: services,
        health: {
            complete: hasAll,
            balance_score: balance,
            total_services: registry.size,
            core_count: coreSvc,
            supportive_count: suppSvc,
            meta_count: metaSvc,
        },
        federation: {
            ...federationCoverage,
            complete: federationCoverage.truth_forge > 0
                && federationCoverage.primitive_engine > 0
                && federationCoverage.credential_atlas > 0,
        },
        recursion: {
            ...recursiveRoles,
            has_manager: recursiveRoles.manager > 0,
            total_assigned: allServices.length - recursiveRoles.unassigned,
        },
        strategic_requirements: {
            verification: 'Atomic Fact-Checking — map claims against peer-reviewed data',
            resilience: 'Stake cap at 88th percentile for consensus protection',
            transparency: 'The system must be explainable. Provide the audit trail.',
            ethical_guardrails: 'Human intervention for high-stakes decisions',
            total_residence: 'The Not-Me must reside within locally controlled infrastructure',
            multi_instance_review: 'Deploy twin Not-Mes to audit each other',
        },
        builders_checklist: {
            define_intention: 'Use Intention-Driven Development to bound agent objectives',
            secure_the_core: 'Deploy in sandboxed execution environments',
            establish_meta_rules: 'Author behavior.md that dictates model choice and governance',
            mcp_integration: 'Connect specialized tools via Model Context Protocol',
            name_the_sovereign: 'Before acting, declare which sovereign is responsible',
        },
        axioms: ONTOLOGY.axioms,
    };
}

/**
 * Get the full ontological framework for API consumers.
 */
export function getOntology() {
    return ONTOLOGY;
}

/**
 * Run health checks across all registered services.
 */
export async function auditTriad() {
    const results = {
        timestamp: new Date().toISOString(),
        framework: 'Three Ontological Roles',
        services: [],
        layers: { CORE: [], SUPPORTIVE: [], META: [] },
        federation: { TRUTH_FORGE: [], PRIMITIVE_ENGINE: [], CREDENTIAL_ATLAS: [], UNASSIGNED: [] },
    };

    for (const [id, service] of registry) {
        try {
            const health = await service.healthCheck();
            const entry = {
                id,
                layer: service.layer,
                sovereign: service.sovereign,
                recursiveRole: service.recursiveRole,
                name: service.name,
                healthy: health.healthy !== false,
                details: health,
            };
            results.services.push(entry);
            results.layers[service.layer].push(entry);
            const sovKey = service.sovereign || 'UNASSIGNED';
            if (results.federation[sovKey]) results.federation[sovKey].push(entry);
            service.status = health.healthy !== false ? 'healthy' : 'degraded';
        } catch (err) {
            const entry = {
                id,
                layer: service.layer,
                sovereign: service.sovereign,
                name: service.name,
                healthy: false,
                error: err.message,
            };
            results.services.push(entry);
            results.layers[service.layer].push(entry);
            service.status = 'error';
        }
    }

    // Assess integrity across all three ontological dimensions
    const healthyCount = results.services.filter(s => s.healthy).length;
    results.integrity = {
        healthy_services: healthyCount,
        total_services: results.services.length,
        score: results.services.length > 0
            ? Math.round((healthyCount / results.services.length) * 100)
            : 0,
        // Structure dimension
        all_triad_layers_present: Object.values(results.layers).every(l => l.length > 0),
        all_triad_layers_healthy: Object.values(results.layers).every(l => l.every(s => s.healthy)),
        // Agency dimension
        all_sovereigns_present: ['TRUTH_FORGE', 'PRIMITIVE_ENGINE', 'CREDENTIAL_ATLAS']
            .every(k => (results.federation[k] || []).length > 0),
    };

    // Persist audit
    const auditLine = JSON.stringify(results) + '\n';
    fs.appendFileSync(path.join(DATA_DIR, 'triad-audits.jsonl'), auditLine, 'utf-8');

    logEvent('info', `Ontology audit: ${healthyCount}/${results.services.length} healthy, integrity ${results.integrity.score}%`);
    return results;
}

/**
 * Assess whether a given subsystem follows the Triad pattern.
 */
export function assessTriadCompleteness(subsystemName, components) {
    const assessment = {
        subsystem: subsystemName,
        timestamp: new Date().toISOString(),
        layers: {
            CORE: { present: false, components: [] },
            SUPPORTIVE: { present: false, components: [] },
            META: { present: false, components: [] },
        },
        complete: false,
        missing: [],
        recommendations: [],
    };

    for (const component of components) {
        if (component.layer && assessment.layers[component.layer]) {
            assessment.layers[component.layer].present = true;
            assessment.layers[component.layer].components.push(component.name);
        }
    }

    for (const [layer, data] of Object.entries(assessment.layers)) {
        if (!data.present) {
            assessment.missing.push(layer);
            const layerDef = TRIAD_LAYERS[layer];
            assessment.recommendations.push(
                `${subsystemName} is missing a ${layerDef.name} layer: ${layerDef.function}`
            );
        }
    }

    assessment.complete = assessment.missing.length === 0;
    return assessment;
}

// ─── Bootstrap: Register Genesis Console Services ───
// Every service declares all three ontological dimensions:
//   layer     → Architectural Triad (Structure)
//   sovereign → Federation of Sovereigns (Agency)
//   recursiveRole → Recursive Magnification (Energy)

export function bootstrapTriad() {
    // ═══ CORE LAYER ═══

    registerService('store', {
        layer: 'CORE',
        sovereign: 'TRUTH_FORGE',       // "I hold the soul. I maintain the state."
        recursiveRole: null,             // Immutable substrate — does not spawn
        name: 'Persistent Store',
        purpose: 'Append-only JSONL storage — the immutable substrate for all knowledge atoms. The Golden Record.',
        dependencies: [],
    });

    registerService('atomizer', {
        layer: 'CORE',
        sovereign: 'PRIMITIVE_ENGINE',   // "I build the bridge. I execute the will."
        recursiveRole: 'DEVELOPER',      // Produces structured output from raw input
        name: 'Scout Atomizer',
        purpose: 'Sends content to Scout LLM for knowledge extraction (HOLD₁ → AGENT → HOLD₂). The Anvil.',
        dependencies: ['store'],
    });

    registerService('watcher', {
        layer: 'CORE',
        sovereign: 'TRUTH_FORGE',       // Observes but does not modify
        recursiveRole: 'RESEARCHER',     // High-velocity data ingestion
        name: 'Passive Watcher',
        purpose: 'Filesystem observer — monitors truth_forge/ for changes and queues files for atomization.',
        dependencies: ['store', 'atomizer'],
    });

    registerService('api-server', {
        layer: 'CORE',
        sovereign: 'TRUTH_FORGE',       // The substrate — it IS the existence
        recursiveRole: null,             // Infrastructure, not a spawned agent
        name: 'API Server',
        purpose: 'Express HTTP server — the execution sandbox for all client-server interactions.',
        dependencies: ['store'],
    });

    // ═══ SUPPORTIVE LAYER ═══

    registerService('coverage', {
        layer: 'SUPPORTIVE',
        sovereign: 'CREDENTIAL_ATLAS',   // "I verify existence. I certify the truth."
        recursiveRole: 'RESEARCHER',     // Pattern recognition across coverage space
        name: 'Coverage Assessor',
        purpose: 'Scans for dark zones, scores coverage breadth/depth/freshness, fills gaps.',
        dependencies: ['watcher', 'store'],
    });

    registerService('assistant', {
        layer: 'SUPPORTIVE',
        sovereign: 'PRIMITIVE_ENGINE',   // Executes conversational labor
        recursiveRole: 'PLANNER',        // Strategic interface for multi-step queries
        name: 'In-App Assistant',
        purpose: 'Conversational interface for querying the knowledge base and system state.',
        dependencies: ['atomizer'],
    });

    registerService('recovery', {
        layer: 'SUPPORTIVE',
        sovereign: 'PRIMITIVE_ENGINE',   // It fixes things — the Builder
        recursiveRole: 'DEVELOPER',      // Builds repair sequences
        name: 'Self-Healing Recovery',
        purpose: 'Detects failures and queues recovery actions to maintain system health.',
        dependencies: ['api-server'],
    });

    registerService('synthetic', {
        layer: 'SUPPORTIVE',
        sovereign: 'CREDENTIAL_ATLAS',   // Verifies system behavior — the Seer
        recursiveRole: 'RESEARCHER',     // Continuous verification patterns
        name: 'Synthetic User Monitor',
        purpose: 'Continuous E2E validation — simulates user flows to verify system health.',
        dependencies: ['api-server'],
    });

    // ═══ META LAYER ═══

    registerService('reflector', {
        layer: 'META',
        sovereign: 'CREDENTIAL_ATLAS',   // Meta-assessment IS verification
        recursiveRole: 'MANAGER',        // Manages the recursive reflection loop
        name: 'Paradigm Reflector',
        purpose: 'Uses Scout to assess the knowledge atom paradigm itself — produces meta-atoms.',
        dependencies: ['atomizer', 'coverage', 'store'],
    });

    registerService('triad', {
        layer: 'META',
        sovereign: 'TRUTH_FORGE',        // The registry IS state maintenance
        recursiveRole: null,             // Self-referential infrastructure
        name: 'Ontology Registry',
        purpose: 'Self-referential: tracks all services, their Triad layer, Federation sovereign, and recursive role.',
        dependencies: [],
    });

    registerService('sentinel', {
        layer: 'META',
        sovereign: 'CREDENTIAL_ATLAS',   // Sentinel is pure verification
        recursiveRole: 'MANAGER',        // Manages escalation and behavioral enforcement
        name: 'Continuity Sentinel',
        purpose: 'Monitors heartbeats, escalates anomalies, enforces behavioral constraints.',
        dependencies: ['api-server'],
    });

    logEvent('success', `Ontology bootstrapped: ${registry.size} services × 3 dimensions (Structure × Energy × Agency)`);
}
