# Design System

**Purpose**: Complete design system for the Truth Forge website

**Status**: Active  
**Last Updated**: 2026-01-27

---

## Overview

The Truth Forge design system provides colors, typography, components, and layout standards that create a cohesive, branded experience across the website.

**Philosophy**: Every website should feel like **a physical space**—not a digital interface. Visitors should feel they've entered somewhere crafted, warm, and permanent.

---

## Design Documents

| Document | Purpose | Status |
|----------|---------|--------|
| [COLORS.md](COLORS.md) | Complete color system with brand accents | ✅ Active |
| [TYPOGRAPHY.md](TYPOGRAPHY.md) | Font system: Instrument Serif, JetBrains Mono, Inter | ✅ Active |
| [COMPONENTS.md](COMPONENTS.md) | Reusable UI component patterns | ✅ Active |
| [LAYOUT.md](LAYOUT.md) | Page templates and structure | ✅ Active |
| [BRANDING.md](BRANDING.md) | Truth Forge brand identity | ✅ Active |
| [ENHANCEMENT_STRATEGY.md](ENHANCEMENT_STRATEGY.md) | Modern design patterns and visualizations | ✅ Active |
| [VISUAL_STANDARDS.md](VISUAL_STANDARDS.md) | Comprehensive visual design standards | ✅ Active |

---

## Core Principles

### The Tactile Rebellion

Our websites reject:
- Generic SaaS aesthetics
- Smooth gradients and floating elements
- Cold, sterile interfaces
- AI-generated visual sameness

Our websites embrace:
- Texture and physicality
- Warmth and humanity
- Crafted intentionality
- Permanent, built-to-last feel

---

## Design Tokens

### Colors

**Primary**: Black (#0D0D0D) with Warm White (#F5F0E6) accent  
**See**: [COLORS.md](COLORS.md) for complete system

### Typography

**Display**: Instrument Serif (headlines, brand names)  
**Mono**: JetBrains Mono (technical, specifications)  
**Body**: Inter (paragraphs, descriptions)  
**See**: [TYPOGRAPHY.md](TYPOGRAPHY.md) for complete system

### Spacing

```css
--space-xs: 0.25rem;
--space-sm: 0.5rem;
--space-md: 1rem;
--space-lg: 2rem;
--space-xl: 4rem;
--space-2xl: 8rem;
```

### Layout

```css
--max-width: 1200px;
--header-height: 80px;
```

---

## Component Library

**See**: [COMPONENTS.md](COMPONENTS.md)

**Core Components**:
- Hero sections
- Cards (product, feature)
- Buttons (primary, secondary)
- Forms (inputs, labels)
- Navigation (header, footer)
- Tables (specifications)

---

## Page Templates

**See**: [LAYOUT.md](LAYOUT.md)

**Templates**:
- Homepage
- Product/Service page
- About page
- Contact page

---

## Brand Identity

**See**: [BRANDING.md](BRANDING.md)

**Truth Forge**:
- **Tagline**: "The Source of All Systems"
- **Accent Color**: Source White (#F5F0E6)
- **Mark**: Lightning bolt breaking through circle
- **Texture**: Medium (30%)

---

## Responsive Breakpoints

| Name | Width | Description |
|------|-------|-------------|
| Mobile | < 640px | Single column, stacked elements |
| Tablet | 640-1024px | Two columns where appropriate |
| Desktop | 1024-1440px | Full layout |
| Wide | > 1440px | Constrained max-width |

**Max content width**: 1200px

---

## Source References

**Primary Sources**:
- `docs/business/branding/02_visual_identity/` - Visual identity standards
- `docs/business/branding/04_product_experience/WEBSITE_DESIGN_STANDARDS.md` - Website standards
- `docs/business/branding/one/TRUTH_FORGE.md` - Truth Forge brand

**Implementation**:
- `src/index.css` - CSS custom properties
- `src/components/` - React components

---

## UP

[../INDEX.md](../INDEX.md)
