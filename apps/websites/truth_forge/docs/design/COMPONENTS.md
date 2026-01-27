# Component Design Patterns

**Purpose**: Reusable UI component patterns for the Truth Forge website

**Status**: Active  
**Last Updated**: 2026-01-27

---

## Overview

This document defines the visual design patterns for reusable UI components. For technical implementation standards, see [standards/COMPONENTS.md](../standards/COMPONENTS.md).

---

## Hero Sections

### Full-Bleed Hero

**Use**: Landing pages, major section introductions

**Structure**:
```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                    [Logo Mark - textured]                    │
│                    [Tagline - Instrument Serif]              │
│                    [Description - Inter]                     │
│                    [CTA Button - accent color]              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Styling**:
```css
.hero-full {
  min-height: 90vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  background: var(--bg-primary);
  background-image: url('texture.png');
  background-blend-mode: overlay;
}

.hero-title {
  font-family: var(--font-display);
  font-size: clamp(3rem, 8vw, 5rem);
  letter-spacing: 0.05em;
  text-transform: uppercase;
  margin-bottom: 1rem;
}

.hero-tagline {
  font-family: var(--font-mono);
  font-size: clamp(0.875rem, 2vw, 1.125rem);
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--accent-dim);
  margin-bottom: 2rem;
}
```

---

## Buttons

### Primary Button

**Use**: Main call-to-action

**Styling**:
```css
.btn-primary {
  font-family: var(--font-mono);
  font-size: 0.875rem;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  padding: 1rem 2rem;
  background: var(--accent);
  color: var(--bg-primary);
  border: none;
  cursor: pointer;
  transition: all 200ms ease;
}

.btn-primary:hover {
  background: var(--accent-glow);
  transform: translateY(-2px);
}
```

### Secondary Button

**Use**: Secondary actions, links styled as buttons

**Styling**:
```css
.btn-secondary {
  font-family: var(--font-mono);
  font-size: 0.875rem;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  padding: 1rem 2rem;
  background: transparent;
  color: var(--text-primary);
  border: 1px solid var(--border);
  cursor: pointer;
  transition: all 200ms ease;
}

.btn-secondary:hover {
  border-color: var(--accent);
  color: var(--accent);
}
```

---

## Cards

### Product/Feature Card

**Use**: Product showcases, feature highlights

**Structure**:
```
┌─────────────────────────────────────┐
│ [Meta - JetBrains Mono, small]      │
│                                     │
│ [Title - Instrument Serif]         │
│                                     │
│ [Description - Inter]               │
│                                     │
│ [Link - optional]                   │
└─────────────────────────────────────┘
```

**Styling**:
```css
.card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  padding: 2rem;
  transition: all 200ms ease;
}

.card:hover {
  border-color: var(--accent);
  transform: translateY(-2px);
}

.card-title {
  font-family: var(--font-display);
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.card-meta {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  margin-bottom: 1rem;
}

.card-body {
  font-family: var(--font-body);
  font-size: 1rem;
  line-height: 1.6;
  color: var(--text-secondary);
}
```

---

## Forms

### Input Fields

**Styling**:
```css
.form-input {
  width: 100%;
  font-family: var(--font-body);
  font-size: 1rem;
  padding: 1rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  color: var(--text-primary);
  transition: border-color 200ms ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--accent);
}

.form-label {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.02em;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
  display: block;
}
```

---

## Navigation

### Header Navigation

**Structure**:
```
[LOGO MARK]  [Brand Name]     [Nav Item]  [Nav Item]  [Nav Item]  [CTA Button]
```

**Styling**:
```css
.nav {
  background: var(--bg-primary);
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-link {
  font-family: var(--font-mono);
  font-size: 0.875rem;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  color: var(--text-secondary);
  text-decoration: none;
  transition: color 200ms ease;
}

.nav-link:hover {
  color: var(--accent);
}
```

---

## Specification Tables

**Use**: Technical details, pricing, specifications

**Styling**:
```css
.spec-table {
  font-family: var(--font-mono);
  font-size: 0.875rem;
  width: 100%;
  border-collapse: collapse;
}

.spec-table th,
.spec-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border-subtle);
}

.spec-table th {
  text-transform: uppercase;
  letter-spacing: 0.02em;
  color: var(--text-muted);
}
```

---

## Grid Layouts

### Product Grid

```css
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-lg);
}
```

### Feature Grid

```css
.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--space-xl);
}
```

---

## UP

[INDEX.md](INDEX.md)
