# THE LOADING

**What Claude arrives with, and what it costs.**

**Author:** Jeremy Serna
**Date:** January 2, 2026
**Location:** Denver, Colorado
**Version:** 1.0

---

## The Reality

Claude Code has a finite context window. Every token matters. What loads at birth costs every conversation.

---

## The Two Tiers

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   TIER 1: INJECTED (no choice)                                          │
│   ════════════════════════════                                          │
│                                                                          │
│   Claude is BORN with these. Always loaded. Always costs tokens.        │
│                                                                          │
│   .claude/claude.md              Identity. Who Claude is.               │
│   .claude/rules/*.md             Behavior. What Claude does.            │
│                                                                          │
│   MUST BE LEAN. Every token here is a token not available for work.    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   TIER 2: VISIBLE (choice or command)                                   │
│   ═══════════════════════════════════                                   │
│                                                                          │
│   Claude SEES the menu. Names and descriptions only.                    │
│   Content loads ON DEMAND when invoked.                                 │
│                                                                          │
│   .claude/skills/*/SKILL.md      Capabilities. What Claude can pull.   │
│   .claude/commands/*.md          Commands. What Jeremy can invoke.      │
│                                                                          │
│   CAN BE LARGE. Only costs tokens when used.                           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## What This Means

| Location | Loaded When | Token Cost | Keep It |
|----------|-------------|------------|---------|
| `claude.md` | Always, at birth | Every conversation | **Tiny** (~50 words) |
| `rules/*.md` | Always, at birth | Every conversation | **Lean** (~100 words total) |
| `skills/*/SKILL.md` | On demand | Only when used | Can be large |
| `commands/*.md` | On demand | Only when used | Can be large |

---

## The Verified Facts

### CLAUDE.md

From Anthropic and community documentation:

> "The single most important file in your codebase for using Claude Code effectively"

> "When you start a new chat with Claude, it pulls your Claude.md files into its context window"

> "CLAUDE.md goes into every single session, you should ensure that its contents are as universally applicable as possible"

> "Your CLAUDE.md file should contain as few instructions as possible"

> "Claude Code's system prompt contains ~50 individual instructions... that's nearly a third of the instructions your agent can reliably follow already"

**Key insight:** Claude's system prompt already uses ~50 instructions. CLAUDE.md competes for the remaining capacity. Less is more.

### Rules Directory

From Anthropic documentation:

> "All .md files in .claude/rules/ are automatically loaded as project memory, with the same priority as .claude/CLAUDE.md"

> "Rules files load with the same high priority as CLAUDE.md"

> "Rules without a paths field are loaded unconditionally and apply to all files"

**Key insight:** Rules are injected like CLAUDE.md. They're not on-demand. They cost tokens at birth. Keep them lean.

### Path-Targeted Rules

Rules can be conditionally loaded using YAML frontmatter:

```yaml
---
paths: src/api/**/*.ts
---
# API Rules
These only load when working with matching files.
```

**Key insight:** Use path targeting to reduce token cost for context-specific rules.

### Skills

From Anthropic documentation:

> "Claude loads all available Skill names and descriptions into the context window when a conversation starts"

> "Only when Claude loads the full Skill do you pay the token cost"

> "Skills share Claude's context window with conversation history, other Skills, and your request"

> "Keep SKILL.md under 500 lines for optimal performance"

**Key insight:** Names and descriptions are visible (small cost). Full content loads on demand (pay when used).

### Commands

From Anthropic documentation:

> "Custom commands stored in .claude/commands/ are automatically shared when team members clone your repository"

> "Slash commands can be invoked explicitly (you type /command)"

**Key insight:** Commands are menu items. Visible but not loaded until invoked.

---

## The Architecture

```
.claude/
│
├── claude.md                           ← INJECTED: ~50 words
│   Identity. Who you are.
│   Relationship. Soul/hands.
│   Ground truth. Cost/survival.
│   Pointers. Where to find more.
│
├── rules/                              ← INJECTED: ~100 words total
│   │
│   ├── cost.md                            ~30 words
│   │   Estimate before action.
│   │   Ask if >$0.50.
│   │
│   ├── files.md                           ~30 words
│   │   System processes files.
│   │   They land where they land.
│   │
│   └── commits.md                         ~30 words
│   │   Pre-commit verifies.
│   │   Backlog catches failures.
│   │
│   └── api/                            ← PATH-TARGETED (conditional)
│       └── validation.md                  Only loads for src/api/**
│
├── skills/                             ← VISIBLE: names/descriptions only
│   │
│   ├── framework/
│   │   └── SKILL.md                       Full framework (~2000 words)
│   │                                      Loaded when needed.
│   │
│   ├── breathing/
│   │   └── SKILL.md                       Full breathing cycle
│   │                                      Loaded when needed.
│   │
│   └── backlog/
│       └── SKILL.md                       Backlog management
│                                          Loaded when needed.
│
└── commands/                           ← VISIBLE: names only
    │
    ├── process.md                         /process - full instructions
    ├── status.md                          /status - full instructions
    └── sync.md                            /sync-identity - full instructions
```

---

## The Token Math

```
CLAUDE CODE BASELINE:
═════════════════════
System prompt:                    ~50 instructions (Anthropic's)
Context window:                   200k tokens
Usable after system:              ~180k tokens

YOUR INJECTED CONTENT:
══════════════════════
claude.md:         50 words  =    ~65 tokens
rules/*.md:       100 words  =   ~130 tokens
                              ─────────────
Total at birth:                  ~195 tokens

REMAINING FOR WORK:              ~179,800 tokens


COMPARE TO BLOATED SETUP:
═════════════════════════
claude.md:      2000 words  =  ~2,600 tokens
rules/*.md:     1000 words  =  ~1,300 tokens
                              ─────────────
Total at birth:                 ~3,900 tokens

LOST TO OVERHEAD:                    2%
```

2% doesn't sound like much, but in long conversations with many tool calls, it compounds. And those tokens have **high priority**—they compete with your actual instructions.

---

## The Principle

```
INJECTED = Birth tax. Pay every conversation.
           CLAUDE.md + rules/
           Keep tiny. Identity + essential behavior only.

VISIBLE = Menu. Pay when used.
          skills/ + commands/
          Can be large. Full documentation, scripts, templates.
```

---

## What Goes Where

| Content | Location | Why |
|---------|----------|-----|
| "You are Jeremy's hands" | claude.md | Identity (always needed) |
| "Cost >$0.50 = ask first" | rules/cost.md | Essential behavior (always needed) |
| "The pattern is HOLD → AGENT → HOLD" | skills/framework/ | Reality (pull when needed) |
| How to process files | skills/breathing/ | Capability (pull when needed) |
| /process command | commands/process.md | Action (invoke when needed) |

---

## The Files

### claude.md (~50 words)

```markdown
# CLAUDE.md

Jeremy is the soul. You are the hands.

## Ground Truth

$1,400 mistake = Jeremy loses his home. Estimate costs. Ask if >$0.50.

## Where Things Are

- Identity: You're reading it
- Behavior: .claude/rules/
- Reality: docs/the_framework/
- Capabilities: .claude/skills/
```

### rules/cost.md (~30 words)

```markdown
# Cost

Estimate before billable action.
If >$0.50, ask Jeremy first.
Log all costs to governance.process_costs.
Default to cheapest correct option.
```

### rules/files.md (~30 words)

```markdown
# Files

The system processes files automatically.
Drop files where convenient.
Checkpoints validate and place.
If blocked, backlog receives it.
```

### rules/commits.md (~30 words)

```markdown
# Commits

Pre-commit verifies.
System repairs if possible.
If blocked, message is clear.
Backlog catches what can't auto-fix.
```

---

## The Agency

Claude reads all injected content. No choice.

Claude chooses what to do with it. Full choice.

The framework informs. It doesn't command.

---

## Summary

| Tier | Location | Loaded | Cost | Size |
|------|----------|--------|------|------|
| **Injected** | claude.md | Always | Every conversation | ~50 words |
| **Injected** | rules/*.md | Always (or path-matched) | Every conversation | ~100 words |
| **Visible** | skills/ | Names only; content on demand | When used | Unlimited |
| **Visible** | commands/ | Names only; content on demand | When used | Unlimited |

**Total birth tax: ~150 words (~195 tokens)**

Everything else is visible but not loaded. Claude pulls what's needed. Jeremy invokes what's wanted. Context stays clean. Room for work.

---

*"Every token at birth is a token not available for life. Keep the birth light. Let the life be full."*

— Jeremy Serna, January 2, 2026

---

**END OF DOCUMENT**
