# Document Format

**The Standard** | Every markdown document follows the same format. Consistent structure enables understanding.

**Authority**: [07_STANDARDS.md](../07_STANDARDS.md) | **Status**: CANONICAL

---

## Quick Reference

| Element | Rule | Example |
|---------|------|---------|
| **Format** | Markdown (.md) | Always |
| **Headers** | `#` title, `##` sections, `###` subsections | `## Quick Reference` |
| **Title** | Single `#` at top | `# Document Format` |
| **Sections** | `##` for major sections | `## The Rules` |
| **Subsections** | `###` for sub-sections | `### Header Structure` |
| **Tables** | For structured/comparative data | Like this table |
| **Lists** | Bullets for items, numbers for ordered | `- item` or `1. step` |
| **Code** | Fenced with language | ` ```python ` |
| **Length** | 50-300 lines typical | Varies with complexity |

---

## The Document Structure

### 1. Title Block (Required)

```markdown
# Document Title

**The Essence** | One sentence that captures the purpose.

---
```

### 2. Quick Reference (Recommended)

```markdown
## Quick Reference

| Term | Definition |
|------|------------|
| X | Short definition |
| Y | Short definition |

---
```

### 3. Sections (Required)

```markdown
## Section Name

Content here. 15-50 lines per section is typical.

---
```

### 4. Footer (Recommended)

```markdown
---

*~{N} lines. {Purpose}. Complete.*
```

---

## Header Rules

| Header Level | Use For | Example |
|--------------|---------|---------|
| `#` | Document title only | `# Document Format` |
| `##` | Major sections | `## The Rules` |
| `###` | Subsections | `### Header Rules` |
| `####` | Rare, within subsections | Avoid if possible |

**Rule**: Never skip levels. `#` → `##` → `###` (not `#` → `###`)

---

## Section Length

| Complexity | Lines | When |
|------------|-------|------|
| Simple | 50-100 | Single concept |
| Medium | 100-300 | Multiple related ideas |
| Complex | 300-800 | Many interconnected parts |

**Target section size**: 15-50 lines. This matches RAG chunking.

---

## Tables

**Use tables when**:
- Data is comparative
- Multiple items have same attributes
- Quick lookup is needed

```markdown
| Column A | Column B | Column C |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |
```

---

## Lists

### Bullet Lists (Unordered)

```markdown
- First item
- Second item
- Third item
```

**Use when**: Items are enumerable but order doesn't matter.

### Numbered Lists (Ordered)

```markdown
1. First step
2. Second step
3. Third step
```

**Use when**: Order matters (steps, sequence, priority).

---

## Code Blocks

### Fenced Code (With Language)

```markdown
` ` `python
def example():
    return True
` ` `
```

**Always specify the language** for syntax highlighting.

### Inline Code

```markdown
Use `inline code` for short references.
```

**Use for**: File names, commands, variable names.

---

## Callouts

Use blockquotes with bold prefixes:

```markdown
> **NOTE**: Additional context that helps understanding.

> **WARN**: Something that can go wrong if ignored.

> **CRITICAL**: Stop and read this before proceeding.
```

---

## Emphasis

| Syntax | When | Example |
|--------|------|---------|
| **Bold** | Key terms, emphasis | `**important**` |
| *Italic* | Definitions, asides | `*definition*` |
| `Code` | Technical terms | `` `variable` `` |

**Rule**: Use sparingly. If everything is emphasized, nothing is.

---

## Document Types

### Standards (Like This Document)

```markdown
# Standard Name

**The Standard** | One sentence essence.

---

## Quick Reference

(table)

---

## The Rules

(sections)

---

## Sources (Consolidated From)

(table of what this replaces)

---

*~N lines. Complete.*
```

### Specifications

```markdown
# Specification Name

**Purpose**: What this spec defines
**Version**: X.Y.Z
**Status**: DRAFT | ACTIVE | DEPRECATED

---

## Overview

(what and why)

---

## Specification

(the actual spec)

---
```

### Contracts

```markdown
# Contract: ENTITY_NAME

**Type**: exist-now | do-now
**Status**: Contract defined
**Created**: YYYY-MM-DD

---

## The Pattern

(the contract)

---
```

### Reference Documents

```markdown
# Reference Name

## Contents

- [Section 1](#section-1)
- [Section 2](#section-2)

---

## Section 1

(content)

---
```

---

## Business Document Types

Business documents follow the same structural principles but have domain-specific templates.

### Proposal / Pitch Deck

```markdown
# Proposal: [Project Name]

**For**: [Client/Stakeholder]
**Date**: YYYY-MM-DD
**Version**: X.Y

---

## Executive Summary

One paragraph: What, why, and what you're asking for.

---

## The Problem

What pain point exists? Use concrete examples.

---

## The Solution

How does your approach solve this? Benefits, not features.

---

## Approach

Step-by-step plan. Timeline. Milestones.

---

## Investment

| Item | Cost | Timeline |
|------|------|----------|
| Phase 1 | $X | Y weeks |
| Phase 2 | $X | Y weeks |

---

## Why Us

Relevant experience. Differentiators. Trust signals.

---

## Next Steps

Clear call to action. What happens if they say yes?

---
```

### Business Case / Decision Document

```markdown
# Decision: [Decision Title]

**Status**: PROPOSED | APPROVED | REJECTED
**Decision Date**: YYYY-MM-DD
**Decision Maker**: [Name/Role]

---

## Context

What situation led to this decision?

---

## Decision

What was decided? One clear statement.

---

## Options Considered

| Option | Pros | Cons | Cost |
|--------|------|------|------|
| A | ... | ... | ... |
| B | ... | ... | ... |

---

## Rationale

Why was this option chosen? What tradeoffs were accepted?

---

## Consequences

What happens as a result? Who is affected?

---

## Review Date

When will this decision be revisited?

---
```

### Meeting Notes / Minutes

```markdown
# Meeting: [Topic]

**Date**: YYYY-MM-DD
**Attendees**: [Names]
**Duration**: X minutes

---

## Agenda

1. Topic A
2. Topic B
3. Topic C

---

## Discussion Summary

### Topic A

Key points discussed. Decisions made.

### Topic B

Key points discussed. Open questions.

---

## Action Items

| Action | Owner | Due |
|--------|-------|-----|
| Do X | @name | YYYY-MM-DD |
| Do Y | @name | YYYY-MM-DD |

---

## Next Meeting

Date, time, topic.

---
```

### Status Report / Update

```markdown
# Status Update: [Project/Period]

**Period**: YYYY-MM-DD to YYYY-MM-DD
**Author**: [Name]

---

## Summary

Overall status: 🟢 On Track | 🟡 At Risk | 🔴 Blocked

One paragraph summary of period.

---

## Accomplishments

- Completed X
- Delivered Y
- Resolved Z

---

## In Progress

| Item | Status | ETA |
|------|--------|-----|
| Feature A | 80% | Next week |
| Feature B | 50% | Two weeks |

---

## Blockers / Risks

| Issue | Impact | Mitigation |
|-------|--------|------------|
| Blocker 1 | High | Action taken |

---

## Next Period

What's planned for next cycle.

---
```

---

## What NOT to Do

```markdown
# WRONG: Multiple # titles
# Another Title
# Yet Another

# WRONG: Skipping header levels
# Title
### Subsection (skipped ##)

# WRONG: Wall of text
No sections, no headers, no structure, just
paragraphs that go on and on without any
visual breaks or navigation aids...

# WRONG: Over-formatting
**Everything** is *emphasized* and `code` and
> quoted
making nothing stand out.
```

---

## Horizontal Rules

Use `---` between major sections. Creates visual separation.

```markdown
## Section One

Content.

---

## Section Two

Content.
```

---

## Sources (Consolidated From)

| Document | What It Covered | Status |
|----------|-----------------|--------|
| `DOCUMENT_SERIES_FRAMEWORK.md` | Document structure, series | Remains (detailed series info) |
| `CLAUDE_DOCUMENT_DEFAULTS.md` | Claude's natural patterns | Archived by this |

**This document is THE document format standard.**

---

## The Principle

> **Structure enables understanding. Consistent format reduces friction.**

Every document follows this format. No exceptions. If something isn't covered, propose an addition.

---

## Related Standards

| Standard | Relationship |
|----------|--------------|
| [NAMING_CONVENTION.md](NAMING_CONVENTION.md) | File naming for documents |
| [FOLDER_STRUCTURE.md](FOLDER_STRUCTURE.md) | Where documents live |
| [DEPRECATION.md](DEPRECATION.md) | How documents are deprecated |
| [CODE_QUALITY.md](CODE_QUALITY.md) | Code examples in documents must follow quality standards |

---

## Industry Alignment

This standard incorporates best practices from:
- [Google Developer Documentation Style Guide](https://developers.google.com/style)
- [Write the Docs](https://www.writethedocs.org/)
- [Diátaxis Documentation Framework](https://diataxis.fr/)

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-01-25 | Added business document types (proposals, decisions, meetings, status) | Claude |
| 2025-01-18 | Initial standard | Claude |

---

*Structure enables understanding. Consistent format reduces friction.*
