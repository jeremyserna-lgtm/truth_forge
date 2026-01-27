# Component Standards

**Purpose**: Standards for building React components for the Truth Forge website

**Status**: Active  
**Last Updated**: 2026-01-27

---

## Core Principles

### HOLD:AGENT:HOLD Pattern

All components follow the universal pattern:

```
HOLD₁ (Props/Input) → AGENT (Component Logic) → HOLD₂ (Rendered Output)
```

**Example**:
```tsx
// HOLD₁: Props define input
interface HeroProps {
  title: string;
  tagline: string;
  ctaText: string;
}

// AGENT: Component transforms input to output
export function Hero({ title, tagline, ctaText }: HeroProps) {
  return (
    // HOLD₂: Rendered JSX
    <header className="hero">
      <h1>{title}</h1>
      <p>{tagline}</p>
      <button>{ctaText}</button>
    </header>
  );
}
```

---

## Component Structure

### File Organization

```
components/
├── layout/          # Layout components (Header, Footer, Layout)
├── sections/        # Page sections (Hero, Features, CTA)
├── cards/           # Card components (ProductCard, FeatureCard)
├── forms/           # Form components (ContactForm, PreOrderForm)
└── ui/              # Base UI components (Button, Input, Link)
```

### Component File Template

```tsx
/**
 * Component Name
 * 
 * Purpose: [What this component does]
 * Usage: [When to use this component]
 */

import { ComponentProps } from 'react';

// HOLD₁: Props interface
export interface ComponentNameProps {
  // Props here
}

// AGENT: Component function
export function ComponentName({ ...props }: ComponentNameProps) {
  // Component logic
  
  // HOLD₂: Return JSX
  return (
    <div className="component-name">
      {/* Component content */}
    </div>
  );
}
```

---

## Design System Integration

### Using CSS Variables

All components use design system tokens:

```tsx
// ✅ CORRECT: Use CSS variables
<div style={{ color: 'var(--accent)' }}>

// ❌ WRONG: Hard-coded colors
<div style={{ color: '#F5F0E6' }}>
```

### Typography Classes

```tsx
// Display text (Instrument Serif)
<h1 className="display-text">TRUTH FORGE</h1>

// Mono text (JetBrains Mono)
<p className="mono-text">UNIT 01 / PERSONAL AI SYSTEM</p>

// Body text (Inter)
<p className="body-text">The source of all systems.</p>
```

---

## Component Patterns

### Hero Component

```tsx
interface HeroProps {
  title: string;
  tagline: string;
  description?: string;
  ctaText: string;
  ctaLink: string;
}

export function Hero({ title, tagline, description, ctaText, ctaLink }: HeroProps) {
  return (
    <header className="hero">
      <div className="hero-content">
        <h1 className="brand-mark">{title}</h1>
        <p className="tagline">{tagline}</p>
        {description && <p className="hero-description">{description}</p>}
        <Link to={ctaLink} className="cta-button">{ctaText}</Link>
      </div>
    </header>
  );
}
```

### Card Component

```tsx
interface CardProps {
  title: string;
  meta?: string;
  description: string;
  link?: string;
  linkText?: string;
}

export function Card({ title, meta, description, link, linkText }: CardProps) {
  const content = (
    <div className="card">
      {meta && <p className="card-meta">{meta}</p>}
      <h3 className="card-title">{title}</h3>
      <p className="card-body">{description}</p>
      {link && linkText && (
        <Link to={link} className="card-link">{linkText}</Link>
      )}
    </div>
  );

  return link ? <Link to={link}>{content}</Link> : content;
}
```

---

## Accessibility Requirements

### Required Attributes

- **Semantic HTML**: Use proper elements (`<header>`, `<nav>`, `<main>`, etc.)
- **ARIA Labels**: When semantic HTML isn't sufficient
- **Keyboard Navigation**: All interactive elements must be keyboard accessible
- **Focus States**: Visible focus indicators
- **Alt Text**: All images must have descriptive alt text

### Example

```tsx
<button 
  className="cta-button"
  aria-label="Preorder your Not-Me"
  onClick={handleClick}
>
  Preorder Your Not-Me
</button>
```

---

## Responsive Design

### Mobile-First Approach

```tsx
// ✅ CORRECT: Mobile-first classes
<div className="grid grid-mobile md:grid-tablet lg:grid-desktop">

// ❌ WRONG: Desktop-first
<div className="grid-desktop mobile:grid-mobile">
```

### Breakpoints

| Name | Width | Usage |
|------|-------|-------|
| Mobile | < 640px | Default styles |
| Tablet | 640-1024px | `md:` prefix |
| Desktop | 1024-1440px | `lg:` prefix |
| Wide | > 1440px | `xl:` prefix |

---

## Performance Requirements

### Code Splitting

- Use React.lazy() for route-level components
- Lazy load images below the fold
- Split large components into smaller chunks

### Optimization

- Memoize expensive computations
- Use React.memo() for pure components
- Avoid unnecessary re-renders

---

## Testing Standards

### Component Tests

```tsx
import { render, screen } from '@testing-library/react';
import { Hero } from './Hero';

describe('Hero', () => {
  it('renders title and tagline', () => {
    render(<Hero title="Test" tagline="Tagline" ctaText="Click" ctaLink="/" />);
    expect(screen.getByText('Test')).toBeInTheDocument();
    expect(screen.getByText('Tagline')).toBeInTheDocument();
  });
});
```

---

## UP

[INDEX.md](INDEX.md)
