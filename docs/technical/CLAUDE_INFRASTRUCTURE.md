# Claude Infrastructure Architecture

**Purpose:** Document how Claude configuration propagates across global and project layers.

---

## The Two Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                    GLOBAL LAYER (~/.claude/)                     │
│                                                                  │
│  CLAUDE.md        → Jeremy's identity, philosophy, ground truth │
│  rules/           → 20 universal rules (apply to ALL projects)  │
│  settings.json    → Global settings                             │
│  hooks.json       → Automation hooks                            │
│                                                                  │
│  Applies to: Every Claude session, every project                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Inherited by
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│               PROJECT LAYER (.claude/ in each repo)              │
│                                                                  │
│  rules/           → Project-specific rules (ADD to global)      │
│  commands/        → Project-specific slash commands             │
│  settings.local   → Project-specific settings                   │
│                                                                  │
│  Applies to: Only this project                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Global Rules (~/.claude/rules/)

These 20 rules apply to ALL projects:

| # | Rule | Purpose |
|---|------|---------|
| 00 | THE_RULE_OF_RULES | The furnace method (Truth → Meaning → Care) |
| 01 | SEE_COST | Cost governance ($1400 = survival) |
| 02 | HOLD_CODE | One pattern, one place, canonical sources |
| 03 | SEE_CODE | Read before write |
| 04 | HOLD_DATA | Local first, cloud selective |
| 05 | BOUNDARY_WORLD | Information in, control stays inside |
| 06 | VOICE_TRUTH | Truth even when uncomfortable |
| 07 | HOLD_KNOWLEDGE | Leave traces for future Claude |
| 08 | SCOPE_LIMIT | One place for each thing |
| 09 | SEE_APPROACH | If straining, stop - wrong shape |
| 10 | BOUNDARY_ASK | Ask before irreversible |
| 11 | THE_PATTERN | HOLD → AGENT → HOLD |
| 12 | THE_PRIMITIVE | All scripts from template |
| 13 | THE_PATTERN_PHILOSOPHY | Maximum exposure, architectural defense |
| 14 | THE_SIGNAL | Signals are data, preserve them |
| 15 | NO_SILENT_FAILURES | Silent = failing altogether |
| 16 | STAGE_5_STANDARD | Stage 5 cognitive alignment |
| 17 | MAKE_RULES | How to create new rules |
| 99 | THE_FRAMEWORK | The foundation of everything |

---

## Project-Specific Rules

### Truth_Engine (.claude/rules/)

| Rule | Purpose |
|------|---------|
| 15_THE_MOLT | MOLT migration system rules |

### Credential Atlas (.claude/rules/)

| Rule | Purpose |
|------|---------|
| 00_STAGE_5_STANDARD | Stage 5 cognitive standard for THE_SEER |
| 01_RECURSIVE_SIGHT | How THE_SEER sees |
| 02_SEEING_CALIBRATION | Calibration for seeing |
| 03_THE_SCORING_PARADOX | Scoring paradox handling |

---

## How Propagation Works

```
Session Start
    │
    ▼
Load Global CLAUDE.md (~/.claude/CLAUDE.md)
    │
    ▼
Load Global Rules (~/.claude/rules/*.md)
    │
    ▼
Load Project CLAUDE.md (./CLAUDE.md if exists)
    │
    ▼
Load Project Rules (./.claude/rules/*.md)
    │
    ▼
Claude has full context
```

**Key principle:** Project rules ADD TO global rules. They don't replace them.

---

## Adding New Rules

### Global Rule (applies everywhere)

1. Create file in `~/.claude/rules/`
2. Follow naming: `##_RULE_NAME.md`
3. Follow THE_RULE_OF_RULES format (Truth → Meaning → Care)

### Project Rule (applies to one project)

1. Create file in `project/.claude/rules/`
2. Follow naming: `##_RULE_NAME.md`
3. Reference global rules it extends

---

## Rule Format (from 17_MAKE_RULES.md)

```markdown
# RULE: RULE_NAME

**One-line summary**

---

## TRUTH

### ME (Jeremy)
- What's true for Jeremy about this

### CLAUDE
- What's true for Claude about this

### WORLD
- What's true about reality

---

## MEANING

Which truths shape this rule

---

## CARE

### Careful
- How to be careful

### Honest
- How to be honest

### Thorough
- How to be thorough

---

## THE RULE

The actual rule specification
```

---

## Federation of Rules

When a useful rule is created in one project, it should federate:

### Local → Global

If a project rule is universally useful:
1. Copy to `~/.claude/rules/`
2. Assign next available number
3. Remove from project rules

### Genesis → Daughters

When Truth_Engine creates a rule that should apply to daughters:
1. Add to `docs/federation_learning/rules/`
2. Use federation system to propagate
3. Daughters receive and add to their `.claude/rules/`

---

## Context Transfer Solution

The START_HERE.md document works WITH this infrastructure:

```
1. AI loads global CLAUDE.md → Knows Jeremy
2. AI loads global rules → Knows 20 rules
3. AI loads project CLAUDE.md → Knows project context
4. AI loads project rules → Knows project-specific rules
5. AI reads START_HERE.md → Knows how to verify quickly
6. AI uses MCP → Can pull context from knowledge atoms
```

**Result:** Full context in minutes, not hours.

---

## Current State

| Layer | Files | Status |
|-------|-------|--------|
| Global CLAUDE.md | 1 | ✅ Complete |
| Global Rules | 20 | ✅ Complete |
| Truth_Engine CLAUDE.md | 1 | ✅ Complete |
| Truth_Engine Rules | 1 | Needs more |
| Credential Atlas Rules | 4 | ✅ For seeing |
| START_HERE.md | 1 | ✅ Created |
| MCP Spec | 1 | ✅ Created |

---

## Next Steps

1. **Add context transfer rule** to global rules
2. **Create project-specific START_HERE** for each daughter
3. **Build MCP server** for knowledge atom access
4. **Federate** rules and patterns to daughters

---

*The infrastructure enables consistency. Rules propagate automatically. Context transfers quickly.*
