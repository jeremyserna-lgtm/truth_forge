# Truth Forge Website Documentation

**Purpose**: Central documentation hub for the Truth Forge website (truth-forge.ai)

**Status**: Active  
**Last Updated**: 2026-01-27

---

## Overview

This documentation folder centralizes all standards, concepts, design elements, and research needed to build and maintain the Truth Forge website. Everything on the website should be documented here for easy access and consistency.

---

## Structure

```
docs/
├── INDEX.md              # This file - central hub
├── WEBSITE_STRUCTURE.md   # Complete website architecture and structure
├── standards/            # Website-specific standards
│   ├── INDEX.md
│   ├── COMPONENTS.md
│   ├── ROUTING.md
│   ├── CONTENT.md
│   └── PERFORMANCE.md
├── concepts/             # Core concepts (copied from main docs)
│   ├── INDEX.md
│   ├── THE_FRAMEWORK.md
│   ├── THE_GRAMMAR.md
│   ├── STAGE_5_MINDS.md
│   ├── HOLD_AGENT_HOLD.md
│   └── TRUTH_MEANING_CARE.md
├── design/               # Design system and visual standards
│   ├── INDEX.md
│   ├── COLORS.md
│   ├── TYPOGRAPHY.md
│   ├── COMPONENTS.md
│   ├── LAYOUT.md
│   └── BRANDING.md
└── research/            # Research library concepts
    ├── INDEX.md
    └── [concepts from research library]
```

---

## Quick Access

### For Planning & Structure
- **[Website Structure](WEBSITE_STRUCTURE.md)** - Complete information architecture, page structure, navigation design

### For Developers
- [Component Standards](standards/COMPONENTS.md) - How to build UI components
- [Routing Standards](standards/ROUTING.md) - Page structure and navigation
- [Design System](design/INDEX.md) - Colors, typography, components

### For Content
- [Content Standards](standards/CONTENT.md) - Writing guidelines
- [Branding Guidelines](design/BRANDING.md) - Brand voice and identity
- [Core Concepts](concepts/INDEX.md) - Framework concepts explained

### For Design
- [Color System](design/COLORS.md) - Complete color palette
- [Typography](design/TYPOGRAPHY.md) - Font system and usage
- [Layout Standards](design/LAYOUT.md) - Page templates and structure
- [Enhancement Strategy](design/ENHANCEMENT_STRATEGY.md) - Modern design patterns and visualizations
- [Visual Standards](design/VISUAL_STANDARDS.md) - Comprehensive visual design standards

---

## Core Concepts

### Framework Concepts
These concepts are essential for understanding the website's foundation:

1. **[The Framework](concepts/THE_FRAMEWORK.md)** - Complete cognitive architecture
2. **[The Grammar](concepts/THE_GRAMMAR.md)** - Naming conventions and ontology
3. **[Stage 5 Minds](concepts/STAGE_5_MINDS.md)** - Cognitive model the framework serves
4. **[HOLD:AGENT:HOLD](concepts/HOLD_AGENT_HOLD.md)** - Universal pattern
5. **[TRUTH:MEANING:CARE](concepts/TRUTH_MEANING_CARE.md)** - The Furnace cycle

**Source**: Copied from `docs/research/library/concepts/` where needed for website context.

---

## Design System

### Visual Identity
- **[Colors](design/COLORS.md)** - Complete color system with brand accents
- **[Typography](design/TYPOGRAPHY.md)** - Instrument Serif, JetBrains Mono, Inter
- **[Components](design/COMPONENTS.md)** - Reusable UI components
- **[Layout](design/LAYOUT.md)** - Page templates and structure
- **[Branding](design/BRANDING.md)** - Truth Forge brand identity

**Source**: Based on `docs/business/branding/` standards, adapted for website implementation.

---

## Website Standards

### Technical Standards
- **[Components](standards/COMPONENTS.md)** - React component patterns
- **[Routing](standards/ROUTING.md)** - Page structure and navigation
- **[Performance](standards/PERFORMANCE.md)** - Lighthouse targets, optimization
- **[Content](standards/CONTENT.md)** - Writing guidelines and voice

---

## Research Library

### Advanced Concepts
For deeper understanding of the systems:

- [AI Degradation System](../docs/research/library/concepts/AI_DEGRADATION_SYSTEM.md)
- [Moments System](../docs/research/library/concepts/MOMENTS_SYSTEM.md)
- [Clara Arc](../docs/research/library/concepts/CLARA_ARC.md)
- [Anvil Strategy](../docs/research/library/concepts/ANVIL_STRATEGY.md)
- [Spine Structure](../docs/research/library/concepts/SPINE_STRUCTURE.md)

**Note**: Research concepts link to main docs. Core framework concepts are copied here for website context.

---

## Document Sync Strategy

### Documents That Live in Both Places

Some documents need to exist in both the main `docs/` folder and the website `docs/` folder:

| Document | Main Location | Website Location | Sync Strategy |
|----------|---------------|------------------|---------------|
| Framework concepts | `docs/research/library/concepts/` | `docs/concepts/` | Copy with website context |
| Design standards | `docs/business/branding/` | `docs/design/` | Copy and adapt for web |
| Brand identity | `docs/business/branding/one/TRUTH_FORGE.md` | `docs/design/BRANDING.md` | Copy with web examples |

### Documents That Link Only

Research concepts that are referenced but not core to website implementation:
- Link to main `docs/research/library/concepts/` rather than copying
- Keep website docs focused on implementation needs

---

## How to Use This Documentation

1. **Start Here**: This INDEX.md provides navigation to all documentation
2. **For Implementation**: Check `standards/` for technical requirements
3. **For Design**: Check `design/` for visual system
4. **For Understanding**: Check `concepts/` for framework foundation
5. **For Deep Dive**: Check `research/` or link to main docs

---

## Maintenance

- **Update Frequency**: As website evolves
- **Sync Strategy**: Core concepts copied, research concepts linked
- **Ownership**: Website team maintains website-specific docs
- **Source of Truth**: Main `docs/` folder is canonical source

---

*This documentation ensures consistency as we build out the Truth Forge website and related apps.*
