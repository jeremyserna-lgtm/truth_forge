---
title: "Federation Atom Alignment Standard"
description: "How knowledge atom schemas and types are aligned across organisms in the federation"
version: "1.0.0"
status: "published"
last_updated: "2026-01-22"
author: "Genesis"
tags:
  - federation
  - knowledge-atoms
  - schema
  - alignment
category: "Standards"
---

# Federation Atom Alignment Standard

**The Essence** | Universal knowledge atom schema that all organisms inherit, with organism-specific type extensions federated via CloudEvents.

**Authority**: [07_STANDARDS.md](../07_STANDARDS.md) | **Status**: CANONICAL

---

## Overview

This standard defines how knowledge atom schemas are:
1. **Inherited** - All organisms use the same 7-column universal schema
2. **Extended** - Organisms define domain-specific atom types
3. **Federated** - Type definitions sync via CE_TYPE_LEARNING CloudEvents
4. **Aligned** - Changes propagate through the federation

**Key Principle**: One schema, many types. The schema is universal. The types are domain-specific.

---

## Quick Reference

| Concept | Definition |
|---------|------------|
| **Universal Schema** | 7-column structure all atoms share |
| **Type Registry** | Organism-specific atom type definitions |
| **CE_TYPE_LEARNING** | CloudEvent type for syncing type definitions |
| **MOLT** | Organisms extend types from Genesis, not create from scratch |

---

## The Universal Schema

All organisms in the federation use this 7-column schema:

| Column | Type | Description |
|--------|------|-------------|
| `atom_id` | VARCHAR (PK) | Unique identifier (format: `atom:xxxxxxxxxxxx`) |
| `type` | VARCHAR | Atom type from organism's type registry |
| `content` | TEXT | The atomic knowledge statement |
| `source_name` | VARCHAR | Source organism or agent |
| `source_id` | VARCHAR | Run/session/extraction ID for tracing |
| `timestamp` | TIMESTAMP | When the atom was created |
| `metadata` | JSON | Flexible JSON for extended fields |
| `hash` | VARCHAR | SHA256 content hash (first 16 chars) for deduplication |

**Canonical Location**: `Primitive/system_elements/schema_registry/knowledge_atoms.json`

---

## Type Registries by Organism

### Genesis (Truth Engine)

**Core Types** - The foundation all organisms inherit:

| Type | Purpose |
|------|---------|
| `fact` | Verified factual statement |
| `belief` | Held-to-be-true statement |
| `decision` | Choice that was made |
| `pattern` | Recurring structure identified |
| `dependency` | Relationship between entities |
| `structure` | Organizational/architectural observation |
| `conversion_target` | Something to be transformed |
| `observation` | Raw perception |
| `insight` | Derived understanding |
| `session` | Session-level metadata |
| `backlog` | Task or work item |

### Credential Atlas

**Seeing Types** - Organized by the 5-phase seeing methodology:

#### Phase 1: Preparation
| Type | Purpose |
|------|---------|
| `preparation_atom` | Entity preparation summary |
| `question_atom` | Key questions to investigate |
| `inventory_atom` | Codebase file inventory |

#### Phase 1.5: External Seeing (OSINT + Due Diligence)

**OSINT Cycle:**
| Type | Purpose |
|------|---------|
| `intelligence_req_atom` | Intelligence requirements |
| `raw_intelligence_atom` | Raw collected intelligence |
| `processed_intel_atom` | Filtered/categorized intel |
| `osint_finding_atom` | Analyzed intelligence findings |
| `intelligence_report_atom` | OSINT cycle report |

**Public Presence:**
| Type | Purpose |
|------|---------|
| `repository_health_atom` | GitHub/source health metrics |
| `community_atom` | Community engagement findings |
| `adoption_atom` | Adoption signals and evidence |
| `documentation_atom` | Documentation quality assessment |
| `media_atom` | Media mentions and coverage |
| `ecosystem_atom` | Ecosystem position analysis |

**OSS Evaluation (QSOS):**
| Type | Purpose |
|------|---------|
| `oss_evaluation_atom` | Full QSOS evaluation |
| `dimension_score_atom` | Individual dimension scores |

**Strategic Early Warning:**
| Type | Purpose |
|------|---------|
| `weak_signal_atom` | Strategic early warning signals |
| `risk_indicator_atom` | Risk indicators identified |
| `opportunity_atom` | Opportunity indicators |

**World Perception:**
| Type | Purpose |
|------|---------|
| `world_perception_atom` | How the world sees entity |

#### Phase 2-3: Internal Seeing (Code Analysis)

**Primary Seeing:**
| Type | Purpose |
|------|---------|
| `observation_atom` | Raw code observations |
| `finding_atom` | Derived findings |
| `pattern_atom` | Patterns discovered |
| `capability_atom` | Capabilities identified |
| `absence_atom` | What's missing |

**Anti-Truth Seeing:**
| Type | Purpose |
|------|---------|
| `anti_truth_atom` | Anti-truth findings |
| `blindspot_atom` | Blindspot revelations |
| `revelation_atom` | Insights from comparison |

#### Phase 4: Synthesis
| Type | Purpose |
|------|---------|
| `thesis_atom` | Primary perspective |
| `antithesis_atom` | Anti-truth perspective |
| `synthesis_atom` | Overall synthesis |
| `fuller_truth_atom` | Dialectical resolution |
| `perception_gap_atom` | World vs internal gap |
| `gap_insight_atom` | Insights from the gap |
| `implication_atom` | What it means for CA |

#### Phase 5: Documentation
| Type | Purpose |
|------|---------|
| `report_atom` | Final seeing report |
| `state_change_atom` | Registry state changes |

**Canonical Location**: `credential_atlas/src/schemas/seeing_atoms.py`

---

## Federation Protocol

### Type Definition Sync

When an organism creates or modifies atom types, it broadcasts via CloudEvents:

```python
# CloudEvent for type learning
{
    "specversion": "1.0",
    "type": "org.truthengine.federation.type_learning",
    "source": "did:web:credential-atlas.truthengine.org",
    "id": "type-sync-{uuid}",
    "time": "2026-01-22T00:00:00Z",
    "datacontenttype": "application/json",
    "data": {
        "organism": "credential_atlas",
        "type_registry": {
            "preparation": ["preparation_atom", "question_atom", "inventory_atom"],
            "external_seeing": [...],
            "internal_seeing": [...],
            "synthesis": [...],
            "documentation": [...]
        },
        "canonical_location": "credential_atlas/src/schemas/seeing_atoms.py",
        "version": "1.0.0"
    }
}
```

### Receiving Type Updates

Genesis (Truth Engine) maintains the master type registry:

1. Receives `CE_TYPE_LEARNING` event
2. Updates `knowledge_atoms.json` → `type_registries` section
3. Broadcasts confirmation to federation
4. Other organisms can query Genesis for latest type definitions

---

## The MOLT Principle

**Organisms MOLT types from Genesis, not create from scratch.**

When Credential Atlas needed seeing-specific atom types:

1. **Started from Genesis types** - `observation`, `pattern`, `finding` inherited
2. **Extended with domain specifics** - Added `osint_finding_atom`, `world_perception_atom`
3. **Documented lineage** - `seeing_atoms.py` references Genesis canonical schema
4. **Registered with federation** - Types added to `knowledge_atoms.json` registry

```python
# seeing_atoms.py header
"""
MOLT from: Truth_Engine/Primitive/system_elements/schema_registry/knowledge_atoms.json
ALIGNED WITH: SEEING_PLAN.md methodology
FEDERATION: Types shared via CE_TYPE_LEARNING CloudEvents
"""
```

---

## Alignment Verification

### Cross-Reference Check

| Source | Location | Must Match |
|--------|----------|------------|
| Genesis Schema | `knowledge_atoms.json` | Universal 7-column structure |
| Genesis Types | `knowledge_atoms.json` → `type_registries.genesis` | Core types |
| CA Types | `seeing_atoms.py` | Types listed in `type_registries.credential_atlas` |
| SEEING_PLAN.md | `registry/SEEING_PLAN.md` | All atom types mentioned |

### Validation Script

```python
# Validate alignment
from Primitive.system_elements.schema_registry import knowledge_atoms
from credential_atlas.src.schemas import seeing_atoms

def validate_alignment():
    genesis_types = knowledge_atoms["type_registries"]["genesis"]["types"]
    ca_types = knowledge_atoms["type_registries"]["credential_atlas"]["phases"]

    # Flatten CA types
    all_ca_types = []
    for phase, phase_data in ca_types.items():
        all_ca_types.extend(phase_data["types"])

    # Check against seeing_atoms.py enum
    enum_types = [t.value for t in seeing_atoms.SeeingAtomType]

    missing = set(all_ca_types) - set(enum_types)
    if missing:
        raise ValueError(f"Missing types in seeing_atoms.py: {missing}")

    return True
```

---

## Implementation Files

| File | Purpose | Organism |
|------|---------|----------|
| `Primitive/system_elements/schema_registry/knowledge_atoms.json` | Universal schema + type registries | Genesis |
| `credential_atlas/src/schemas/seeing_atoms.py` | CA seeing atom types | Credential Atlas |
| `Primitive/seed/federation.py` | Federation protocol | Genesis |
| `credential_atlas/registry/SEEING_PLAN.md` | CA seeing methodology | Credential Atlas |

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-22 | Initial standard - aligned CA seeing atoms with Genesis |

---

## Related Documents

- [FEDERATION_DOCUMENT_STANDARD.md](FEDERATION_DOCUMENT_STANDARD.md) - Document format
- [FEDERATION_FOLDER_STRUCTURE.md](FEDERATION_FOLDER_STRUCTURE.md) - Folder organization
- [FEDERATION_FRAMEWORK_ACCESS.md](FEDERATION_FRAMEWORK_ACCESS.md) - Framework access patterns
- [PRIMITIVE_PATTERN_SPECIFICATION.md](PRIMITIVE_PATTERN_SPECIFICATION.md) - THE PATTERN

---

## The Principle

> **One schema, many types. The schema is universal. The types are domain-specific. The federation keeps them aligned.**

Every organism inherits the universal schema. Every organism extends with domain-specific types. The federation ensures alignment.

---

*~250 lines. Federation atom alignment standard. Complete.*
