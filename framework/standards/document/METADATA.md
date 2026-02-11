# METADATA

**Document metadata via YAML frontmatter. Every document is typed, related, and discoverable.**

---

## The Rule

Every document MUST have YAML frontmatter. Frontmatter enables:
- Machine parsing by AI agents
- Relationship tracking
- Automated index generation
- Knowledge graph construction
- Obsidian compatibility

---

## Required Frontmatter

```yaml
---
id: NOT_ME_ARCHITECTURAL_CONSIDERATIONS           # Unique identifier (no extension)
title: "NOT-ME Architectural Considerations"      # Human-readable title
type: specification                               # Document type (see taxonomy)
status: canonical                                 # Lifecycle status
domain: not-me                                    # Business domain
created: 2026-01-15                               # ISO date
updated: 2026-02-01                               # Last modification
author: jeremy                                    # Original author
---
```

---

## Optional Frontmatter

```yaml
---
# LLM ALIGNMENT (Critical for machine access)
summary: |                                        # 2-3 sentence TL;DR for LLM triage
  Defines hardware tiers (Drummer/Soldier/King/Empire), deployment
  tiers (Hosted/Hybrid/Sovereign), and technical constraints for
  building LLM-embodied kiosk infrastructure on macOS.
answers:                                          # Questions this document answers
  - "What are the hardware tiers?"
  - "How does Hybrid sync work?"
  - "What memory does Drummer Boy need?"
  - "How do I deploy headless on macOS?"
embedding_hash: null                              # Hash of content when last embedded

# Relationships
supersedes:                                       # Documents this replaces
  - NOT_ME_OLD_SPEC
superseded_by: null                               # Document that replaced this (when deprecated)
related:                                          # Related documents (bidirectional preferred)
  - NOT_ME_CORE_SPECIFICATION
  - NOT_ME_INFRASTRUCTURE_PLAN
  - TRUTH_ENGINE_BUSINESS_PLAN
blocks:                                           # Documents that must be read first
  - 00_GENESIS
implements:                                       # Standards/ADRs this implements
  - ADR-0001

# Discovery
tags:                                             # Searchable tags
  - hardware-tiers
  - deployment-tiers
  - kiosk
  - macos
aliases:                                          # Alternative names for search
  - "Not-Me Architecture"
  - "Kiosk Spec"

# Quality
confidence: 0.9                                   # 0.0-1.0, how settled is this?
review_cycle: quarterly                           # never | monthly | quarterly | annual
last_reviewed: 2026-02-01                         # Last human review date
reviewers:                                        # Who reviewed
  - jeremy

# Obsidian (optional, for human visualization)
cssclass: specification                           # Obsidian CSS class
publish: true                                     # Include in published vault
---
```

---

## LLM Alignment Fields

These fields optimize documents for LLM consumption:

| Field | Purpose | Who Writes |
|-------|---------|------------|
| `summary` | 2-3 sentence TL;DR for quick triage | LLM generates, human approves |
| `answers` | Questions this document answers | LLM extracts, human refines |
| `embedding_hash` | Content hash when last embedded | System auto-updates |

### Why These Matter

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      LLM DOCUMENT TRIAGE                                     │
│                                                                              │
│   User: "How does Hybrid sync work?"                                        │
│                                                                              │
│   LLM Process:                                                               │
│   1. Search `answers` field across all docs                                 │
│      → Match: NOT_ME_ARCHITECTURAL_CONSIDERATIONS                           │
│                                                                              │
│   2. Read `summary` to confirm relevance                                    │
│      → "...deployment tiers (Hosted/Hybrid/Sovereign)..."                   │
│      → Confirmed relevant                                                   │
│                                                                              │
│   3. Read full document OR specific section                                 │
│      → Section 14.3: Hybrid Sync Architecture                               │
│                                                                              │
│   4. Answer with citation                                                   │
│      → "Hybrid sync works as follows... (Section 14.3)"                     │
│                                                                              │
│   WITHOUT these fields:                                                     │
│   LLM must read EVERY document to find the answer                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Summary Guidelines

| Criterion | Requirement |
|-----------|-------------|
| Length | 2-3 sentences, max 100 words |
| Content | WHAT the doc covers, not WHY it matters |
| Keywords | Include searchable terms |
| Format | Plain text, no markdown |

### Answers Guidelines

| Criterion | Requirement |
|-----------|-------------|
| Format | Natural questions users would ask |
| Count | 3-10 questions per document |
| Specificity | Specific enough to match, general enough to find |
| Coverage | Cover main sections of the document |

---

## Document Types (Taxonomy)

| Type | Purpose | Example |
|------|---------|---------|
| `framework` | Foundational theory (L0) | 00_GENESIS.md |
| `standard` | Normative rules (L1) | STANDARD_NAMING.md |
| `specification` | Technical design (L2) | NOT_ME_ARCHITECTURAL_CONSIDERATIONS.md |
| `plan` | Business/implementation (L2) | TRUTH_ENGINE_BUSINESS_PLAN.md |
| `adr` | Architectural decision record | 0001-folder-structure.md |
| `guide` | How-to instructions | DEPLOYMENT_GUIDE.md |
| `reference` | Lookup information | API_REFERENCE.md |
| `index` | Navigation hub | INDEX.md |
| `log` | Temporal record | CHANGELOG.md |
| `personal` | Personal context | relationships/haze/*.md |

---

## Status Lifecycle

```
DRAFT → REVIEW → CANONICAL → DEPRECATED → ARCHIVED
  │        │         │            │           │
  └── Work in progress (incomplete)           │
           └── Ready for review               │
                      └── Authoritative source│
                                   └── Superseded, read-only
                                              └── Historical only
```

| Status | Meaning | Agent Behavior |
|--------|---------|----------------|
| `draft` | Incomplete, may change | Warn before citing |
| `review` | Complete, awaiting approval | Include with caveat |
| `canonical` | Authoritative | Trust fully |
| `deprecated` | Superseded | Follow `superseded_by` |
| `archived` | Historical reference only | Read-only, don't cite as current |

---

## Domain Taxonomy

| Domain | Description |
|--------|-------------|
| `framework` | THE FRAMEWORK (theory, identity, philosophy) |
| `not-me` | Not-Me product architecture |
| `primitive-engine` | Primitive Engine product |
| `credential-atlas` | Credential Atlas product |
| `infrastructure` | Shared infrastructure (pipelines, services) |
| `business` | Business planning, strategy |
| `personal` | Personal context, relationships |
| `operations` | Day-to-day operations |

---

## Relationship Types

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        RELATIONSHIP SEMANTICS                                │
│                                                                              │
│   supersedes      "This document REPLACES that document"                    │
│                   → One-directional. Creates deprecation chain.             │
│                                                                              │
│   related         "These documents INFORM each other"                       │
│                   → Bidirectional preferred. Creates graph edges.           │
│                                                                              │
│   blocks          "Read THAT document BEFORE this one"                      │
│                   → One-directional. Creates prerequisite chain.            │
│                                                                              │
│   implements      "This document IMPLEMENTS that standard/decision"         │
│                   → One-directional. Traces to authority.                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Validation Rules

| Rule | Enforcement |
|------|-------------|
| `id` must be unique | Index generator fails on duplicate |
| `type` must be from taxonomy | Schema validation |
| `status` must be valid lifecycle | Schema validation |
| `supersedes` target must exist | Index generator warns |
| `related` should be bidirectional | Index generator warns on orphan |
| `created` ≤ `updated` | Schema validation |

---

## Agent Operations

### Parsing Frontmatter

```python
import yaml
from pathlib import Path

def parse_document(path: Path) -> dict:
    """Parse document, extracting frontmatter and content."""
    content = path.read_text()

    if not content.startswith("---"):
        return {"frontmatter": {}, "content": content, "path": str(path)}

    # Split on second ---
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {"frontmatter": {}, "content": content, "path": str(path)}

    frontmatter = yaml.safe_load(parts[1])
    body = parts[2].strip()

    return {
        "frontmatter": frontmatter or {},
        "content": body,
        "path": str(path),
    }
```

### Updating Frontmatter

```python
def update_frontmatter(path: Path, updates: dict) -> None:
    """Update frontmatter fields without changing content."""
    doc = parse_document(path)

    # Merge updates
    new_frontmatter = {**doc["frontmatter"], **updates}
    new_frontmatter["updated"] = datetime.now().date().isoformat()

    # Rebuild document
    output = "---\n"
    output += yaml.dump(new_frontmatter, default_flow_style=False, sort_keys=False)
    output += "---\n\n"
    output += doc["content"]

    path.write_text(output)
```

---

## Obsidian Compatibility

This frontmatter is fully compatible with Obsidian:

| Feature | Frontmatter Field |
|---------|-------------------|
| Graph view | `related`, `blocks`, `implements` become edges |
| Search | `tags`, `aliases`, `title` are indexed |
| Dataview queries | All fields queryable via Dataview plugin |
| Publish | `publish: true/false` controls inclusion |
| CSS styling | `cssclass` applies custom styles |

### Obsidian Wikilinks

In document body, use wikilinks for relationships:

```markdown
See [[NOT_ME_CORE_SPECIFICATION]] for identity definition.
```

These are parsed by Obsidian AND can be extracted by agents via regex:
```python
import re
wikilinks = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', content)
```

---

## Checklist

- [ ] Frontmatter present
- [ ] `id` unique and matches filename (without extension)
- [ ] `type` from taxonomy
- [ ] `status` from lifecycle
- [ ] `domain` from taxonomy
- [ ] `created` and `updated` present
- [ ] `related` documents exist and are bidirectional
- [ ] `supersedes` documents marked as deprecated

---

## UP

[INDEX.md](INDEX.md)
