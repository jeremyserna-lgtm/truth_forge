---
title: "Dimension Registry - Living Registry of All Dimensions"
description: "Extensible registry system for discovering, registering, and using all dimensions"
version: "1.0.0"
status: "published"
last_updated: "2026-01-21"
author: "Genesis"
tags:
  - framework
  - dimensions
  - registry
  - extensible
category: "Standards"
---

# Dimension Registry

**The Essence** | A living, extensible registry of all dimensions, enabling discovery, extension, and comprehensive dimensional thinking.

**Authority**: [07_STANDARDS.md](07_STANDARDS.md) | **Status**: CANONICAL

---

## Overview

The Dimension Registry is a **living system** that captures all dimensions discovered through thinking, analysis, and experience. It enables:

- **Discovery**: Find dimensions by searching
- **Extension**: Register new dimensions as they're discovered
- **Comprehensive Analysis**: Use all registered dimensions in analysis
- **Knowledge Sharing**: Share dimensions across the federation

---

## Core Dimensions (12)

The 12 core dimensions are automatically registered:

1. **SPATIAL_SCOPE**: Where? (FEDERATION, GENESIS, ORGANISM, LOCAL)
2. **TEMPORAL_SCOPE**: When? (PAST, PRESENT, FUTURE)
3. **DOMAIN_SCOPE**: What domain? (FRAMEWORK, STANDARDS, SERVICES)
4. **TECHNOLOGY_SCOPE**: What technology? (PYTHON, MARKDOWN, API)
5. **AGENT_SCOPE**: Who uses? (AI_AGENT, DEVELOPER, SYSTEM)
6. **AUTHORITY_SCOPE**: Who controls? (FEDERATION, GENESIS, ORGANISM)
7. **LIFECYCLE_SCOPE**: What stage? (DESIGN, DEVELOPMENT, RUNTIME)
8. **INTERFACE_SCOPE**: How accessed? (CLI, API, FILE_SYSTEM)
9. **GRANULARITY_SCOPE**: What level? (SYSTEM, SERVICE, MODULE)
10. **PERSISTENCE_SCOPE**: How stored? (FILE, DATABASE, VERSIONED)
11. **CHANGE_SCOPE**: Can it change? (IMMUTABLE, MUTABLE, VERSIONED)
12. **PURPOSE_SCOPE**: Why exists? (GOVERNANCE, SECURITY, LEARNING)

---

## User-Discovered Dimensions

Dimensions discovered through thinking and experience:

### 1. Theory vs Practice

**Dimension ID**: `theory_practice`

**Question**: Is this theoretical/conceptual or practical/implemented?

**Values**:
- `THEORY`: Conceptual, abstract, not yet implemented
- `PRACTICE`: Implemented, concrete, operational
- `BOTH`: Both theoretical and practical aspects
- `BRIDGE`: Bridging theory to practice

**Example**: A framework document is THEORY, an implemented service is PRACTICE.

**Related**: TEMPORAL_SCOPE (FUTURE vs PRESENT), LIFECYCLE_SCOPE (DESIGN vs RUNTIME)

### 2. Human vs AI

**Dimension ID**: `human_ai`

**Question**: Is this for humans or AI agents?

**Values**:
- `HUMAN`: For human understanding/use
- `AI`: For AI agent understanding/use
- `BOTH`: For both humans and AI
- `COMMUNICATION`: How humans communicate to AI

**Example**: Documentation for humans is HUMAN, agent instructions are AI.

**Related**: AGENT_SCOPE

### 3. Coder vs Non-Coder

**Dimension ID**: `coder_capability`

**Question**: Does this require coding capability?

**Values**:
- `CODER`: Requires coding capability
- `NON_CODER`: Does not require coding capability
- `BOTH`: Works for both coders and non-coders
- `BRIDGE`: Bridges coder and non-coder understanding

**Example**: Code reviews require CODER, documentation can be NON_CODER.

**Related**: AGENT_SCOPE, INTERFACE_SCOPE

### 4. Right vs Wrong

**Dimension ID**: `correctness`

**Question**: Is this correct/valid or incorrect/invalid?

**Values**:
- `RIGHT`: Correct, valid, accurate
- `WRONG`: Incorrect, invalid, inaccurate
- `UNKNOWN`: Correctness not yet determined
- `CONTEXT_DEPENDENT`: Correctness depends on context

**Example**: Validated code is RIGHT, untested code is UNKNOWN.

**Related**: PURPOSE_SCOPE

### 5. Hidden vs Visible

**Dimension ID**: `visibility`

**Question**: Is this hidden or visible?

**Values**:
- `HIDDEN`: Not visible, concealed, implicit
- `VISIBLE`: Visible, explicit, transparent
- `PARTIALLY_VISIBLE`: Some aspects visible, some hidden
- `CONTEXT_DEPENDENT`: Visibility depends on context

**Example**: Internal implementation is HIDDEN, API is VISIBLE.

**Related**: INTERFACE_SCOPE, PURPOSE_SCOPE

### 6. Known vs Unknown

**Dimension ID**: `knowledge`

**Question**: Is this known or unknown?

**Values**:
- `KNOWN`: Known, understood, documented
- `UNKNOWN`: Unknown, not understood, undocumented
- `PARTIALLY_KNOWN`: Some aspects known, some unknown
- `KNOWABLE`: Can be known, discoverable

**Example**: Documented knowledge is KNOWN, blind spots are UNKNOWN.

**Related**: PURPOSE_SCOPE, TEMPORAL_SCOPE

---

## Using the Registry

### Register a New Dimension

```python
from Primitive.governance.dimensional_analysis.registry import register_dimension

register_dimension(
    dimension_id="my_dimension",
    name="My Dimension",
    description="Description of what this dimension captures",
    question="What question does this dimension answer?",
    values=[
        {"value": "VALUE1", "description": "Description of value 1"},
        {"value": "VALUE2", "description": "Description of value 2"},
    ],
    category="cognitive",  # or "framework", "industry", "general"
    source="user",  # or "truth_engine", "industry"
    discovered_by="Jeremy",
    related_dimensions=["spatial_scope", "temporal_scope"],
)
```

### Search Dimensions

```python
from Primitive.governance.dimensional_analysis.registry import get_registry

registry = get_registry()

# Search by query
results = registry.search("theory")

# Get by category
cognitive_dims = registry.get_by_category("cognitive")

# Get related dimensions
related = registry.get_related("theory_practice")
```

### List All Dimensions

```python
all_dimensions = registry.list_all()
for dim in all_dimensions:
    print(f"{dim.name}: {dim.question}")
```

---

## Dimension Categories

| Category | Description | Examples |
|----------|-------------|----------|
| **framework** | Core framework dimensions | SPATIAL_SCOPE, TEMPORAL_SCOPE |
| **cognitive** | Cognitive/thinking dimensions | THEORY_PRACTICE, KNOWN_UNKNOWN |
| **industry** | Industry-standard dimensions | TOGAF dimensions, Zachman dimensions |
| **general** | General-purpose dimensions | CORRECTNESS, VISIBILITY |

---

## Dimension Discovery Process

### 1. Notice a Dimension

When thinking about concepts, notice dimensions:
- "I'm thinking about the difference between X and Y..."
- "There's a dimension between A and B..."
- "I need to consider C vs D..."

### 2. Formalize the Dimension

- **Name**: What is this dimension called?
- **Question**: What question does it answer?
- **Values**: What are the possible values?
- **Description**: What does it capture?

### 3. Register the Dimension

```python
register_dimension(
    dimension_id="my_dimension",
    name="My Dimension",
    # ... (see above)
)
```

### 4. Use in Analysis

The dimension is now available for automatic analysis:

```python
analysis = auto_analyze_concept(
    concept_name="my_concept",
    context=context,
)
# Analysis now includes my_dimension
```

---

## Examples of Dimension Discovery

### Example 1: Theory vs Practice

**Discovery**: "I am currently thinking about the dimension between theory and practice and how I take the conceptual notions you just formalized and implement them into architecture."

**Formalization**:
- **Name**: Theory vs Practice
- **Question**: Is this theoretical/conceptual or practical/implemented?
- **Values**: THEORY, PRACTICE, BOTH, BRIDGE

**Registration**: ✅ Registered as `theory_practice`

### Example 2: Human vs AI

**Discovery**: "I'm thinking about the difference between me being a human and you being an AI and how I communicate this to you."

**Formalization**:
- **Name**: Human vs AI
- **Question**: Is this for humans or AI agents?
- **Values**: HUMAN, AI, BOTH, COMMUNICATION

**Registration**: ✅ Registered as `human_ai`

### Example 3: Known vs Unknown

**Discovery**: "I think that if I just tell you all this it won't be hidden to you and that you can incorporate it into what you know, and that is the dimension of known and unknown."

**Formalization**:
- **Name**: Known vs Unknown
- **Question**: Is this known or unknown?
- **Values**: KNOWN, UNKNOWN, PARTIALLY_KNOWN, KNOWABLE

**Registration**: ✅ Registered as `knowledge`

---

## Integration with Dimensional Analysis

Registered dimensions are automatically available for analysis:

```python
from Primitive.governance.dimensional_analysis import auto_analyze_concept

# Analysis includes all registered dimensions
analysis = auto_analyze_concept(
    concept_name="my_concept",
    context=context,
)

# Check for user-discovered dimensions
if hasattr(analysis.coordinates, 'theory_practice'):
    print(f"Theory vs Practice: {analysis.coordinates.theory_practice}")
```

---

## Related Documents

- [DIMENSIONAL_FRAMEWORK.md](DIMENSIONAL_FRAMEWORK.md) - Framework specification
- [DIMENSIONAL_FRAMEWORK_INTEGRATION.md](DIMENSIONAL_FRAMEWORK_INTEGRATION.md) - Integration details

---

## The Principle

> **The Dimension Registry is a living system that grows as new dimensions are discovered. Every dimension you think about can be registered and used in analysis.**

The registry makes dimensional thinking extensible and discoverable.

---

*Dimension Registry - Living System*
