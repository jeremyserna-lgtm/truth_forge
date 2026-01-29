/**
 * Temporal Identity Architecture Types
 * 
 * The architecture evolves over time:
 * - New documents → new atoms → architecture updates
 * - Meta-layers shift as life changes
 * - Not-Me identity adapts
 * - Clients see their own evolution
 * 
 * This creates a feedback loop: seeing yourself causes transformation
 */

import { ClientArchitecture, NotMeIdentity, LifePerspective, Anchor } from './types-identity';

// ============================================================================
// TEMPORAL VERSIONING
// ============================================================================

/**
 * Snapshot of architecture at a point in time
 */
export interface ArchitectureSnapshot {
    id: string;
    tenantId: string;
    timestamp: Date;
    architecture: ClientArchitecture;

    // What triggered this snapshot
    trigger: 'upload' | 'monthly' | 'manual' | 'milestone';
    triggerMetadata?: {
        documentsAdded?: number;
        atomsAdded?: number;
        milestone?: string; // e.g., "6 months", "1 year"
    };
}

/**
 * Evolution of a specific meta-layer over time
 */
export interface PerspectiveEvolution {
    perspectiveName: string;
    snapshots: Array<{
        timestamp: Date;
        prominence: number;
        description: string;
    }>;
    trend: 'growing' | 'stable' | 'declining';
    changeRate: number; // How fast it's changing
}

export interface AnchorEvolution {
    anchorValue: string;
    snapshots: Array<{
        timestamp: Date;
        importance: number;
        expression: string;
    }>;
    trend: 'strengthening' | 'stable' | 'weakening';
    changeRate: number;
}

/**
 * How the Not-Me identity has evolved
 */
export interface IdentityEvolution {
    tenantId: string;
    snapshots: ArchitectureSnapshot[];

    // Compare first vs. latest
    comparison: {
        timeSpan: string; // "1 year", "6 months"

        // What changed
        perspectivesAdded: string[];
        perspectivesRemoved: string[];
        perspectivesShifted: Array<{
            name: string;
            oldProminence: number;
            newProminence: number;
            delta: number;
        }>;

        anchorsAdded: string[];
        anchorsRemoved: string[];
        anchorsStrengthened: string[];
        anchorsWeakened: string[];

        // Purpose evolution
        purposesAdded: string[];
        purposesRemoved: string[];
        purposesRefined: Array<{
            old: string;
            new: string;
        }>;

        // Overall coherence trend
        coherenceTrend: {
            initial: number;
            current: number;
            delta: number;
            interpretation: string; // "becoming more unified", "exploring complexity"
        };
    };

    // Key insights about their transformation
    transformationInsights: string[];
}

// ============================================================================
// REFLECTION TYPES
// ============================================================================

/**
 * Reflection - showing them their own growth
 */
export interface SelfReflection {
    tenantId: string;
    generatedAt: Date;

    // "Here's what changed"
    changes: {
        newPerspectives: string[];
        shiftingValues: string[];
        emergingPatterns: string[];
    };

    // "Here's what stayed constant"
    constants: {
        coreAnchors: string[];
        persistentPrimitives: string[];
    };

    // "Here's what we're seeing"
    observations: string[];

    // "Here's what this might mean"
    interpretations: string[];
}

/**
 * Year-over-year comparison
 */
export interface YearOverYearReport {
    tenantId: string;
    yearStart: Date;
    yearEnd: Date;

    summary: {
        documentsProcessed: number;
        atomsCreated: number;
        patternsDiscovered: number;

        biggestShift: {
            type: 'perspective' | 'anchor' | 'purpose';
            name: string;
            change: string;
        };

        biggestConstant: {
            type: 'perspective' | 'anchor' | 'primitive';
            name: string;
            stability: string;
        };
    };

    narrative: string; // AI-generated story of their year
}

// ============================================================================
// SUBSCRIPTION PERSISTENCE
// ============================================================================

/**
 * Subscription tier determines features
 */
export type SubscriptionTier = 'free' | 'standard' | 'premium';

export interface TenantSubscription {
    tenantId: string;
    tier: SubscriptionTier;
    startDate: Date;
    expiresAt?: Date;

    features: {
        maxDocuments: number;
        maxAtoms: number;
        snapshotFrequency: 'upload' | 'weekly' | 'monthly';
        evolutionTracking: boolean;
        yearOverYearReports: boolean;
        exportToFineTuning: boolean;
    };

    usage: {
        documentsStored: number;
        atomsCreated: number;
        snapshotsTaken: number;
        apiCallsThisMonth: number;
    };
}

/**
 * Persistent architecture storage
 */
export interface PersistentArchitecture {
    tenantId: string;
    subscription: TenantSubscription;

    // Current state
    currentArchitecture: ClientArchitecture;

    // Historical snapshots
    snapshots: ArchitectureSnapshot[];

    // Evolution tracking
    evolution: {
        perspectives: PerspectiveEvolution[];
        anchors: AnchorEvolution[];
        identity: IdentityEvolution;
    };

    // Recent reflections
    reflections: SelfReflection[];

    // Milestone reports
    reports: YearOverYearReport[];
}

// ============================================================================
// TRANSFORMATION TRACKING
// ============================================================================

/**
 * Tracks how seeing themselves causes change
 * This is the meta-awareness feedback loop
 */
export interface TransformationTracker {
    tenantId: string;

    // When they view their architecture
    viewEvents: Array<{
        timestamp: Date;
        screenViewed: 1 | 2 | 3 | 4;
        duration: number; // seconds spent
        interactions: string[]; // what they clicked/expanded
    }>;

    // Correlate views with subsequent changes
    viewToChangeCorrelation: Array<{
        viewTimestamp: Date;
        screenViewed: number;
        elementViewed: string; // which perspective/pattern they saw

        subsequentChange?: {
            changeTimestamp: Date;
            changeType: 'new_document' | 'refined_atom' | 'explicit_feedback';
            related: boolean; // was this change related to what they viewed?
        };
    }>;

    // Meta-insight: "Seeing X led to doing Y"
    discoveredLoops: Array<{
        pattern: string;
        description: string;
        confidence: number;
    }>;
}
