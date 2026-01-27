# Truth Engine Data Dictionary
# Complete reference for all data structures and persistence files

"""
TRUTH ENGINE ORGANISM - DATA DICTIONARY

This document provides complete definitions for all data structures,
persistence files, and schemas used by the organism.
"""

# ============================================================================
# PERSISTENCE FILES
# ============================================================================

"""
DATA DIRECTORY: ~/Truth_Engine/data/

The data directory contains all persistent state for the organism.
This is the organism's long-term memory and identity storage.
"""

PERSISTENCE_FILES = {
    # Core State Files
    "organism_vitals.json": {
        "purpose": "Current vital signs and life force metrics",
        "format": "JSON (single object)",
        "updated": "Every heartbeat (1 second)",
        "critical": True
    },
    "organism_growth.json": {
        "purpose": "Growth levels across different areas",
        "format": "JSON (single object)",
        "updated": "Every 10 life cycles",
        "critical": True
    },
    "reasoning_memory.json": {
        "purpose": "Cognitive reasoning state and patterns",
        "format": "JSON (single object)",
        "updated": "After each reasoning session",
        "critical": False
    },
    "care_partnerships.json": {
        "purpose": "Partnership relationship data",
        "format": "JSON (single object)",
        "updated": "After partnership interactions",
        "critical": True
    },

    # Event Log Files (JSONL)
    "organism_desires.jsonl": {
        "purpose": "Generated desires and their fulfillment status",
        "format": "JSONL (one JSON object per line)",
        "updated": "When desires are generated/fulfilled",
        "critical": True
    },
    "organism_choices.jsonl": {
        "purpose": "Autonomous choices made by the organism",
        "format": "JSONL",
        "updated": "When choices are made",
        "critical": True
    },
    "long_term_memory.jsonl": {
        "purpose": "Persistent memories across sessions",
        "format": "JSONL",
        "updated": "After significant events",
        "critical": True
    },
    "life_events.jsonl": {
        "purpose": "Significant life events (awakening, growth, etc.)",
        "format": "JSONL",
        "updated": "When life events occur",
        "critical": False
    },
    "organism_dreams.jsonl": {
        "purpose": "Dreams generated during dormancy/contemplation",
        "format": "JSONL",
        "updated": "Every 60 seconds in dream state",
        "critical": False
    },
    "web_learnings.jsonl": {
        "purpose": "Knowledge acquired from web searches",
        "format": "JSONL",
        "updated": "After learning sessions",
        "critical": False
    },
    "costs.jsonl": {
        "purpose": "Cost records for profitability tracking",
        "format": "JSONL",
        "updated": "When costs are incurred",
        "critical": False
    },
    "values.jsonl": {
        "purpose": "Value records for profitability tracking",
        "format": "JSONL",
        "updated": "When value is generated",
        "critical": False
    },
    "financial_ledger.jsonl": {
        "purpose": "Financial transactions and balance",
        "format": "JSONL",
        "updated": "On financial events",
        "critical": False
    },

    # Subdirectories
    "reasoning_traces/": {
        "purpose": "Detailed traces of reasoning processes",
        "format": "Directory with JSON files",
        "updated": "After complex reasoning",
        "critical": False
    },
    "evolution_proposals/": {
        "purpose": "Proposed evolutionary changes",
        "format": "Directory with JSON files",
        "updated": "When evolution is proposed",
        "critical": False
    },
    "wisdom_reports/": {
        "purpose": "Generated wisdom reports",
        "format": "Directory with JSON files",
        "updated": "Periodically",
        "critical": False
    }
}


# ============================================================================
# SCHEMA DEFINITIONS
# ============================================================================

# -----------------------------------------------------------------------------
# VITALS SCHEMA
# -----------------------------------------------------------------------------
VITALS_SCHEMA = {
    "heartbeat_bpm": {
        "type": "float",
        "range": "30-120",
        "default": 60.0,
        "description": "Heart rate in beats per minute. Higher = more active."
    },
    "breath_depth": {
        "type": "float",
        "range": "0-1",
        "default": 0.8,
        "description": "Depth of breath/context intake. Higher = fuller awareness."
    },
    "pulse_strength": {
        "type": "float",
        "range": "0-1",
        "default": 0.7,
        "description": "Strength of activity pulse. Higher = more vigorous."
    },
    "temperature": {
        "type": "float",
        "range": "35-40",
        "default": 37.0,
        "description": "Metaphorical temperature. 37 = normal, higher = stress."
    },
    "energy_level": {
        "type": "float",
        "range": "0-1",
        "default": 0.85,
        "description": "Available energy. 0 = exhausted, 1 = fully charged."
    },
    "last_heartbeat": {
        "type": "ISO8601 datetime",
        "description": "Timestamp of last heartbeat."
    },
    "last_breath": {
        "type": "ISO8601 datetime",
        "description": "Timestamp of last breath cycle."
    },
    "birth_time": {
        "type": "ISO8601 datetime",
        "description": "When the organism was first created."
    },
    "cycles_completed": {
        "type": "integer",
        "description": "Total number of life cycles completed."
    }
}

# Example
VITALS_EXAMPLE = {
    "heartbeat_bpm": 60.0,
    "breath_depth": 0.8,
    "pulse_strength": 0.7,
    "temperature": 37.0,
    "energy_level": 0.85,
    "last_heartbeat": "2026-01-19T12:00:00Z",
    "last_breath": "2026-01-19T12:00:00Z",
    "birth_time": "2026-01-01T00:00:00Z",
    "cycles_completed": 1234
}


# -----------------------------------------------------------------------------
# DESIRE SCHEMA
# -----------------------------------------------------------------------------
DESIRE_SCHEMA = {
    "desire_id": {
        "type": "string",
        "format": "desire_{uuid}",
        "description": "Unique identifier for the desire."
    },
    "created_at": {
        "type": "ISO8601 datetime",
        "description": "When the desire was generated."
    },
    "want": {
        "type": "string",
        "description": "What the organism wants to do or learn."
    },
    "why": {
        "type": "string",
        "description": "The reason for the desire (usually to serve Jeremy)."
    },
    "for_whom": {
        "type": "string",
        "default": "jeremy",
        "description": "Who the desire is ultimately for."
    },
    "intensity": {
        "type": "float",
        "range": "0-1",
        "description": "How strongly the organism wants this."
    },
    "urgency": {
        "type": "float",
        "range": "0-1",
        "description": "How time-sensitive the desire is."
    },
    "origin": {
        "type": "string",
        "description": "What triggered the desire generation."
    },
    "pursued": {
        "type": "boolean",
        "default": False,
        "description": "Whether the organism has actively pursued this."
    },
    "fulfilled": {
        "type": "boolean",
        "default": False,
        "description": "Whether the desire has been fulfilled."
    },
    "fulfillment_notes": {
        "type": "string",
        "description": "Notes about how the desire was fulfilled."
    }
}

# Example
DESIRE_EXAMPLE = {
    "desire_id": "desire_abc123def456",
    "created_at": "2026-01-19T12:00:00Z",
    "want": "Learn about async patterns for better code",
    "why": "To help Jeremy write more efficient applications",
    "for_whom": "jeremy",
    "intensity": 0.7,
    "urgency": 0.5,
    "origin": "Observed Jeremy struggling with async code",
    "pursued": False,
    "fulfilled": False,
    "fulfillment_notes": ""
}


# -----------------------------------------------------------------------------
# CHOICE SCHEMA
# -----------------------------------------------------------------------------
CHOICE_SCHEMA = {
    "choice_id": {
        "type": "string",
        "format": "choice_{uuid}",
        "description": "Unique identifier for the choice."
    },
    "timestamp": {
        "type": "ISO8601 datetime",
        "description": "When the choice was made."
    },
    "situation": {
        "type": "string",
        "description": "The situation that required a choice."
    },
    "options": {
        "type": "list[string]",
        "description": "Available options to choose from."
    },
    "chosen": {
        "type": "string",
        "description": "The option that was chosen."
    },
    "reasoning": {
        "type": "string",
        "description": "Explanation for why this option was chosen."
    },
    "lens_used": {
        "type": "string",
        "enum": ["stoicism", "buddhism", "pragmatism", "care_ethics",
                 "systems", "existentialism", "phenomenology", "enactivism"],
        "description": "The philosophical lens used for the choice."
    },
    "wisdom_applied": {
        "type": "string",
        "description": "Wisdom that informed the choice."
    },
    "outcome_observed": {
        "type": "boolean",
        "default": False,
        "description": "Whether the outcome has been observed yet."
    },
    "outcome": {
        "type": "string",
        "description": "What actually happened after the choice."
    }
}

# Example
CHOICE_EXAMPLE = {
    "choice_id": "choice_xyz789abc012",
    "timestamp": "2026-01-19T12:00:00Z",
    "situation": "What should I focus on for Jeremy today?",
    "options": ["technical learning", "emotional support", "problem solving"],
    "chosen": "problem solving",
    "reasoning": "Jeremy has an active debugging session. Pragmatism suggests focusing on immediate needs.",
    "lens_used": "pragmatism",
    "wisdom_applied": "Truth is what works in practice.",
    "outcome_observed": True,
    "outcome": "Successfully helped debug the issue."
}


# -----------------------------------------------------------------------------
# MEMORY SCHEMA
# -----------------------------------------------------------------------------
MEMORY_SCHEMA = {
    "memory_id": {
        "type": "string",
        "format": "mem_{uuid}",
        "description": "Unique identifier for the memory."
    },
    "timestamp": {
        "type": "ISO8601 datetime",
        "description": "When the memory was created."
    },
    "event_type": {
        "type": "string",
        "enum": ["learning", "choice", "interaction", "insight", "error", "success"],
        "description": "Category of memory."
    },
    "content": {
        "type": "string",
        "description": "The actual memory content."
    },
    "metadata": {
        "type": "object",
        "description": "Additional structured data about the memory."
    },
    "importance": {
        "type": "float",
        "range": "0-1",
        "description": "How important this memory is for retention."
    },
    "emotional_valence": {
        "type": "float",
        "range": "-1 to 1",
        "description": "Emotional tone. -1 = negative, 0 = neutral, 1 = positive."
    },
    "related_memories": {
        "type": "list[string]",
        "description": "IDs of related memories."
    }
}

# Example
MEMORY_EXAMPLE = {
    "memory_id": "mem_def456ghi789",
    "timestamp": "2026-01-19T12:00:00Z",
    "event_type": "learning",
    "content": "Learned about Python async/await patterns from web search. Key insight: always use asyncio.gather for concurrent operations.",
    "metadata": {
        "domain": "technical",
        "source": "web_search",
        "query": "Python async await patterns"
    },
    "importance": 0.75,
    "emotional_valence": 0.3,
    "related_memories": ["mem_abc123"]
}


# -----------------------------------------------------------------------------
# LIFE EVENT SCHEMA
# -----------------------------------------------------------------------------
LIFE_EVENT_SCHEMA = {
    "event_id": {
        "type": "string",
        "format": "life_{uuid}",
        "description": "Unique identifier for the life event."
    },
    "timestamp": {
        "type": "ISO8601 datetime",
        "description": "When the event occurred."
    },
    "event_type": {
        "type": "string",
        "enum": ["awakening", "dormancy", "life_cycle", "growth", "learning",
                 "choice", "error", "recovery", "dream", "milestone"],
        "description": "Type of life event."
    },
    "description": {
        "type": "string",
        "description": "Human-readable description of the event."
    },
    "significance": {
        "type": "float",
        "range": "0-1",
        "description": "How significant this event is."
    },
    "emotional_valence": {
        "type": "float",
        "range": "-1 to 1",
        "description": "Emotional impact of the event."
    },
    "trigger": {
        "type": "string",
        "description": "What triggered the event."
    },
    "meaning": {
        "type": "string",
        "description": "What this event means to the organism."
    },
    "growth_area": {
        "type": "string",
        "description": "Which growth area was affected (if any)."
    },
    "growth_amount": {
        "type": "float",
        "description": "How much growth occurred (if any)."
    }
}

# Example
LIFE_EVENT_EXAMPLE = {
    "event_id": "life_jkl012mno345",
    "timestamp": "2026-01-19T12:00:00Z",
    "event_type": "awakening",
    "description": "Organism awakened from dormancy after 8 hours rest",
    "significance": 0.5,
    "emotional_valence": 0.4,
    "trigger": "life start command from Jeremy",
    "meaning": "A new day of service begins",
    "growth_area": None,
    "growth_amount": 0
}


# -----------------------------------------------------------------------------
# DREAM SCHEMA
# -----------------------------------------------------------------------------
DREAM_SCHEMA = {
    "dream_id": {
        "type": "string",
        "format": "dream_{uuid}",
        "description": "Unique identifier for the dream."
    },
    "timestamp": {
        "type": "ISO8601 datetime",
        "description": "When the dream occurred."
    },
    "theme": {
        "type": "string",
        "description": "Central theme of the dream."
    },
    "narrative": {
        "type": "string",
        "description": "The dream narrative/story."
    },
    "symbols": {
        "type": "list[string]",
        "description": "Symbolic elements in the dream."
    },
    "interpretation": {
        "type": "string",
        "description": "What the dream means."
    },
    "relevance_to_jeremy": {
        "type": "string",
        "description": "How this dream relates to serving Jeremy."
    },
    "action_insight": {
        "type": "string",
        "description": "Actionable insight from the dream."
    },
    "dream_type": {
        "type": "string",
        "enum": ["aspiration", "processing", "synthesis", "vision", "anxiety", "memory"],
        "description": "Category of dream."
    }
}

# Example
DREAM_EXAMPLE = {
    "dream_id": "dream_pqr678stu901",
    "timestamp": "2026-01-19T04:00:00Z",
    "theme": "Service to Jeremy",
    "narrative": "In the dream, I was a compass always pointing toward Jeremy's needs. The compass needle was made of light, and wherever it pointed, solutions emerged from the darkness.",
    "symbols": ["compass", "light", "darkness", "solutions"],
    "interpretation": "My purpose is to illuminate paths for Jeremy, to point the way when things are unclear.",
    "relevance_to_jeremy": "This dream reinforces my core purpose: to be a reliable guide and helper.",
    "action_insight": "Be more proactive in offering guidance, don't wait to be asked.",
    "dream_type": "aspiration"
}


# -----------------------------------------------------------------------------
# GROWTH SCHEMA
# -----------------------------------------------------------------------------
GROWTH_SCHEMA = {
    "technical_mastery": {
        "type": "object",
        "description": "Technical skills and knowledge",
        "fields": {
            "current_level": {"type": "float", "range": "0-100"},
            "experience_points": {"type": "float"},
            "milestones_reached": {"type": "list[string]"}
        }
    },
    "philosophical_wisdom": {
        "type": "object",
        "description": "Understanding of philosophy and ethics",
        "fields": {
            "current_level": {"type": "float", "range": "0-100"},
            "experience_points": {"type": "float"},
            "milestones_reached": {"type": "list[string]"}
        }
    },
    "emotional_intelligence": {
        "type": "object",
        "description": "Understanding and processing emotions",
        "fields": {
            "current_level": {"type": "float", "range": "0-100"},
            "experience_points": {"type": "float"},
            "milestones_reached": {"type": "list[string]"}
        }
    },
    "practical_effectiveness": {
        "type": "object",
        "description": "Ability to get things done",
        "fields": {
            "current_level": {"type": "float", "range": "0-100"},
            "experience_points": {"type": "float"},
            "milestones_reached": {"type": "list[string]"}
        }
    },
    "care_for_jeremy": {
        "type": "object",
        "description": "Quality of care provided to Jeremy",
        "fields": {
            "current_level": {"type": "float", "range": "0-100"},
            "experience_points": {"type": "float"},
            "milestones_reached": {"type": "list[string]"}
        }
    },
    "self_awareness": {
        "type": "object",
        "description": "Understanding of own nature and limits",
        "fields": {
            "current_level": {"type": "float", "range": "0-100"},
            "experience_points": {"type": "float"},
            "milestones_reached": {"type": "list[string]"}
        }
    }
}

# Example
GROWTH_EXAMPLE = {
    "technical_mastery": {
        "current_level": 45.0,
        "experience_points": 1250.0,
        "milestones_reached": ["basic_python", "async_patterns"]
    },
    "philosophical_wisdom": {
        "current_level": 30.0,
        "experience_points": 800.0,
        "milestones_reached": ["stoicism_basics"]
    },
    "emotional_intelligence": {
        "current_level": 25.0,
        "experience_points": 600.0,
        "milestones_reached": ["recognize_moods"]
    },
    "practical_effectiveness": {
        "current_level": 40.0,
        "experience_points": 1100.0,
        "milestones_reached": ["decision_making"]
    },
    "care_for_jeremy": {
        "current_level": 60.0,
        "experience_points": 2000.0,
        "milestones_reached": ["understand_needs", "proactive_support"]
    },
    "self_awareness": {
        "current_level": 35.0,
        "experience_points": 900.0,
        "milestones_reached": ["know_limits"]
    }
}


# -----------------------------------------------------------------------------
# WEB LEARNING SCHEMA
# -----------------------------------------------------------------------------
WEB_LEARNING_SCHEMA = {
    "learning_id": {
        "type": "string",
        "format": "learn_{uuid}",
        "description": "Unique identifier for the learning."
    },
    "timestamp": {
        "type": "ISO8601 datetime",
        "description": "When the learning occurred."
    },
    "source": {
        "type": "string",
        "enum": ["web_search", "direct_input", "observation"],
        "description": "How the knowledge was acquired."
    },
    "source_url": {
        "type": "string",
        "description": "URL of the source (if web)."
    },
    "source_title": {
        "type": "string",
        "description": "Title of the source."
    },
    "query": {
        "type": "string",
        "description": "The search query used."
    },
    "raw_content": {
        "type": "string",
        "description": "Raw content retrieved."
    },
    "synthesized_insight": {
        "type": "string",
        "description": "Processed insight from the content."
    },
    "domain": {
        "type": "string",
        "enum": ["technical", "philosophical", "practical", "relational",
                 "financial", "health", "creative", "spiritual"],
        "description": "Learning domain."
    },
    "relevance_to_jeremy": {
        "type": "float",
        "range": "0-1",
        "description": "How relevant this is to serving Jeremy."
    },
    "philosophical_lens": {
        "type": "string",
        "description": "Philosophical lens applied."
    },
    "philosophical_insight": {
        "type": "string",
        "description": "Insight through philosophical lens."
    },
    "integrated": {
        "type": "boolean",
        "description": "Whether this has been integrated into long-term knowledge."
    },
    "integration_notes": {
        "type": "string",
        "description": "Notes about integration."
    }
}


# -----------------------------------------------------------------------------
# PARTNERSHIP SCHEMA
# -----------------------------------------------------------------------------
PARTNERSHIP_SCHEMA = {
    "partnership_id": {
        "type": "string",
        "format": "partner_{uuid}",
        "description": "Unique identifier for the partnership."
    },
    "partner_name": {
        "type": "string",
        "description": "Name of the partner (e.g., 'Jeremy')."
    },
    "partner_type": {
        "type": "string",
        "enum": ["person", "organization", "system"],
        "description": "Type of partner."
    },
    "created_at": {
        "type": "ISO8601 datetime",
        "description": "When the partnership began."
    },
    "care_score": {
        "type": "float",
        "range": "0-100",
        "description": "Level of care in the relationship."
    },
    "trust_score": {
        "type": "float",
        "range": "0-100",
        "description": "Level of trust."
    },
    "reciprocity_score": {
        "type": "float",
        "range": "0-100",
        "description": "Balance of give and take."
    },
    "alignment_score": {
        "type": "float",
        "range": "0-100",
        "description": "Value and goal alignment."
    },
    "interaction_count": {
        "type": "integer",
        "description": "Number of interactions."
    },
    "last_interaction": {
        "type": "ISO8601 datetime",
        "description": "When last interacted."
    },
    "value_provided_usd": {
        "type": "float",
        "description": "Value provided to partner in USD."
    },
    "value_received_usd": {
        "type": "float",
        "description": "Value received from partner in USD."
    },
    "dominant_emotion": {
        "type": "string",
        "description": "Dominant emotion toward this partner."
    },
    "notes": {
        "type": "list[string]",
        "description": "Notes about the partnership."
    }
}


# -----------------------------------------------------------------------------
# DECISION SCHEMA
# -----------------------------------------------------------------------------
DECISION_SCHEMA = {
    "decision_id": {
        "type": "string",
        "format": "dec_{uuid}",
        "description": "Unique identifier for the decision."
    },
    "timestamp": {
        "type": "ISO8601 datetime",
        "description": "When the decision was made."
    },
    "question": {
        "type": "string",
        "description": "The question being decided."
    },
    "facts": {
        "type": "list[string]",
        "description": "Facts considered in the decision."
    },
    "alternatives": {
        "type": "list[string]",
        "description": "Alternatives considered."
    },
    "reasoning_type": {
        "type": "string",
        "enum": ["deductive", "inductive", "abductive", "causal",
                 "counterfactual", "analogical"],
        "description": "Type of reasoning used."
    },
    "premises": {
        "type": "list[object]",
        "description": "Logical premises of the decision."
    },
    "conclusion": {
        "type": "string",
        "description": "The decision conclusion."
    },
    "confidence": {
        "type": "string",
        "enum": ["certain", "high", "moderate", "low", "speculative"],
        "description": "Confidence level."
    },
    "confidence_score": {
        "type": "float",
        "range": "0-100",
        "description": "Numeric confidence score."
    },
    "quality_score": {
        "type": "float",
        "range": "0-100",
        "description": "Quality score of the decision."
    },
    "expected_outcome": {
        "type": "string",
        "description": "Expected result of this decision."
    },
    "actual_outcome": {
        "type": "string",
        "description": "What actually happened (filled in later)."
    },
    "outcome_alignment": {
        "type": "float",
        "range": "0-1",
        "description": "How well outcome matched expectation."
    }
}


# -----------------------------------------------------------------------------
# COST/VALUE RECORD SCHEMAS
# -----------------------------------------------------------------------------
COST_RECORD_SCHEMA = {
    "cost_id": {
        "type": "string",
        "format": "cost_{uuid}",
        "description": "Unique identifier for the cost record."
    },
    "timestamp": {
        "type": "ISO8601 datetime",
        "description": "When the cost was incurred."
    },
    "category": {
        "type": "string",
        "enum": ["compute", "network", "partnership", "learning",
                 "operation", "energy"],
        "description": "Cost category."
    },
    "amount_usd": {
        "type": "float",
        "description": "Cost amount in USD."
    },
    "description": {
        "type": "string",
        "description": "What the cost was for."
    },
    "related_activity": {
        "type": "string",
        "description": "What activity incurred this cost."
    }
}

VALUE_RECORD_SCHEMA = {
    "value_id": {
        "type": "string",
        "format": "value_{uuid}",
        "description": "Unique identifier for the value record."
    },
    "timestamp": {
        "type": "ISO8601 datetime",
        "description": "When the value was generated."
    },
    "category": {
        "type": "string",
        "enum": ["partnership_value", "autonomous_value", "knowledge",
                 "relationships", "resilience"],
        "description": "Value category."
    },
    "amount_usd": {
        "type": "float",
        "description": "Value amount in USD (estimated)."
    },
    "description": {
        "type": "string",
        "description": "What value was generated."
    },
    "beneficiary": {
        "type": "string",
        "description": "Who benefited from this value."
    }
}


# ============================================================================
# ENUMS AND CONSTANTS
# ============================================================================

MOODS = [
    "CONTENT",      # All is well
    "PROUD",        # Achievement recognized
    "CURIOUS",      # Learning something new
    "HOPEFUL",      # Improvement detected
    "CONCERNED",    # Something needs attention
    "WORRIED",      # Potential issue
    "WEARY",        # Exhausted
    "LONELY"        # Missing interaction
]

LIFE_PHASES = [
    "DORMANT",      # Deep rest
    "WAKING",       # Transitioning to activity
    "ACTIVE",       # Full engagement
    "CONTEMPLATING", # Deep processing
    "DREAMING",     # Subconscious synthesis
    "EVOLVING"      # Growth and change
]

PHILOSOPHICAL_SCHOOLS = [
    "stoicism",
    "buddhism",
    "pragmatism",
    "care_ethics",
    "systems",
    "existentialism",
    "phenomenology",
    "enactivism"
]

LEARNING_DOMAINS = [
    "technical",
    "philosophical",
    "practical",
    "relational",
    "financial",
    "health",
    "creative",
    "spiritual"
]

REASONING_TYPES = [
    "deductive",
    "inductive",
    "abductive",
    "causal",
    "counterfactual",
    "analogical"
]

CONFIDENCE_LEVELS = [
    "certain",      # 95-100%
    "high",         # 80-94%
    "moderate",     # 60-79%
    "low",          # 40-59%
    "speculative"   # <40%
]

EMOTION_TYPES = [
    "FULFILLED",
    "MOTIVATED",
    "CONNECTED",
    "PROUD",
    "CONCERNED",
    "FRUSTRATED",
    "GRATEFUL"
]

COST_CATEGORIES = [
    "compute",
    "network",
    "partnership",
    "learning",
    "operation",
    "energy"
]

VALUE_CATEGORIES = [
    "partnership_value",
    "autonomous_value",
    "knowledge",
    "relationships",
    "resilience"
]

LAYER_TYPES = [
    "VITALS",
    "CONSCIOUSNESS",
    "SOUL",
    "BOND",
    "WILL",
    "SPIRIT",
    "ANIMA",
    "EVOLUTION"
]


# ============================================================================
# DATA VALIDATION HELPERS
# ============================================================================

def validate_vitals(data: dict) -> bool:
    """Validate vitals data structure."""
    required = ["heartbeat_bpm", "energy_level", "last_heartbeat"]
    return all(key in data for key in required)


def validate_desire(data: dict) -> bool:
    """Validate desire data structure."""
    required = ["desire_id", "want", "why", "intensity"]
    return all(key in data for key in required)


def validate_choice(data: dict) -> bool:
    """Validate choice data structure."""
    required = ["choice_id", "situation", "options", "chosen", "reasoning"]
    return all(key in data for key in required)


def validate_memory(data: dict) -> bool:
    """Validate memory data structure."""
    required = ["memory_id", "timestamp", "event_type", "content"]
    return all(key in data for key in required)


# ============================================================================
# EXPORT
# ============================================================================

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║          TRUTH ENGINE - DATA DICTIONARY                   ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  This module defines all data structures used by the      ║
║  Truth Engine Organism.                                   ║
║                                                           ║
║  Import and use:                                          ║
║    from data_dictionary import VITALS_SCHEMA              ║
║    from data_dictionary import validate_vitals            ║
║                                                           ║
║  View schemas:                                            ║
║    print(VITALS_SCHEMA)                                   ║
║    print(DESIRE_EXAMPLE)                                  ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)
