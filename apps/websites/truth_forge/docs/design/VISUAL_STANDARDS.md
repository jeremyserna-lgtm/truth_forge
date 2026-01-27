# Visual Design Standards

**Purpose**: Comprehensive visual design standards for Truth Forge website

**Status**: Active  
**Last Updated**: 2026-01-27

---

## Core Principles

### Visual Identity

**Truth Forge** is:
- **Warm**: Inviting, not cold or sterile
- **Authoritative**: Confident, not arrogant
- **Human**: Real, not corporate speak
- **Professional**: Top-tier, modern, sophisticated

### Design Philosophy

**The Tactile Rebellion**:
- Texture and physicality
- Warmth and humanity
- Crafted intentionality
- Permanent, built-to-last feel

---

## Typography Standards

### Font System

**Display**: Instrument Serif
- Use: Headlines, brand names, hero text
- Weight: 400 (regular)
- Style: Serif, mechanical, premium

**Mono**: JetBrains Mono
- Use: Technical details, specifications, code
- Weight: 400 (regular)
- Style: Monospaced, technical

**Body**: Inter
- Use: Paragraphs, descriptions, UI text
- Weight: 400-500 (regular to medium)
- Style: Sans-serif, clean, legible

### Type Scale (Major Third: 1.25)

| Name | Size | Use | Line Height |
|------|------|-----|------------|
| Hero | clamp(3rem, 8vw, 5rem) | Landing headlines | 1.1 |
| H1 | clamp(2rem, 5vw, 3rem) | Page titles | 1.2 |
| H2 | clamp(1.5rem, 4vw, 2.25rem) | Section headers | 1.3 |
| H3 | clamp(1.25rem, 3vw, 1.75rem) | Subsections | 1.4 |
| H4 | clamp(1.125rem, 2.5vw, 1.5rem) | Card titles | 1.5 |
| Body | 18px | Paragraphs | 1.6 |
| Small | 16px | Captions, labels | 1.6 |
| Micro | 14px | Technical specs | 1.5 |

### Typography Rules

**DO**:
- Use fluid typography (clamp())
- Maintain consistent line height (1.5-1.7 for body)
- Use proper letter spacing (0.05em for display)
- Scale responsively across devices

**DON'T**:
- Use font weights below 400
- Mix more than 3 typefaces
- Use decorative or script fonts
- Reduce body text below 16px

---

## Color Standards

### Foundation Colors

| Name | Hex | RGB | Use |
|------|-----|-----|-----|
| Black | `#0D0D0D` | 13, 13, 13 | Primary background, text |
| Charcoal | `#1A1A1A` | 26, 26, 26 | Secondary backgrounds |
| Graphite | `#2D2D2D` | 45, 45, 45 | Tertiary backgrounds |
| Steel | `#4A4A4A` | 74, 74, 74 | Borders, muted elements |
| Warm White | `#F5F0E6` | 245, 240, 230 | Primary accent, light text |
| Cream | `#EDE8DE` | 237, 232, 222 | Secondary accent |

### Accent Colors

**Truth Forge - Source White**:
- Primary: `#F5F0E6` (Warm White)
- Glow: `#FFFEF5` (Highlights)
- Dim: `#E8E3D9` (Muted states)

### Color Usage Rules

**DO**:
- Use warm white as primary accent
- Maintain high contrast (4.5:1 minimum)
- Use color strategically (not everywhere)
- Test color combinations for accessibility

**DON'T**:
- Use pure white (`#FFFFFF`) as background
- Use multiple accent colors together
- Use color alone to convey meaning
- Apply accent to logo mark

---

## Spacing Standards

### 8-Point Grid System

| Name | Value | Use |
|------|-------|-----|
| XS | 4px | Tight spacing, icons |
| SM | 8px | Small gaps, compact layouts |
| MD | 16px | Standard spacing, padding |
| LG | 24px | Section spacing, margins |
| XL | 32px | Large sections, hero padding |
| 2XL | 48px | Extra large sections |
| 3XL | 64px | Maximum spacing |

### Spacing Rules

**DO**:
- Use 8-point grid multiples
- Maintain consistent spacing
- Use larger spacing for separation
- Use smaller spacing for grouping

**DON'T**:
- Use arbitrary spacing values
- Mix spacing systems
- Overcrowd elements
- Under-space important content

---

## Layout Standards

### Container Widths

| Breakpoint | Max Width | Padding |
|------------|-----------|---------|
| Mobile | 100% | 16px |
| Tablet | 100% | 24px |
| Desktop | 1200px | 32px |
| Wide | 1200px | 48px |

### Grid System

**12-Column Grid**:
```css
.container {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: var(--space-lg);
  max-width: 1200px;
  margin: 0 auto;
}
```

### Layout Rules

**DO**:
- Use consistent max-width (1200px)
- Maintain proper padding
- Use grid for complex layouts
- Center content horizontally

**DON'T**:
- Exceed max-width
- Use fixed widths
- Mix layout systems
- Ignore responsive breakpoints

---

## Component Standards

### Buttons

**Primary Button**:
- Background: Warm White (`#F5F0E6`)
- Text: Black (`#0D0D0D`)
- Padding: 16px 32px
- Border: None
- Border Radius: 4px
- Font: JetBrains Mono, 0.875rem, uppercase
- Transition: 200ms ease

**Hover State**:
- Background: Warm White Glow (`#FFFEF5`)
- Transform: translateY(-2px)

**Secondary Button**:
- Background: Transparent
- Text: Warm White
- Border: 1px solid Steel
- Padding: 16px 32px
- Border Radius: 4px

**Hover State**:
- Border Color: Warm White
- Color: Warm White

### Cards

**Standard Card**:
- Background: Charcoal (`#1A1A1A`)
- Border: 1px solid Graphite
- Padding: 32px
- Border Radius: 4px
- Box Shadow: 0 2px 8px rgba(0, 0, 0, 0.1)
- Transition: 200ms ease

**Hover State**:
- Border Color: Warm White
- Box Shadow: 0 4px 16px rgba(0, 0, 0, 0.15)
- Transform: translateY(-2px)

### Forms

**Input Field**:
- Background: Charcoal
- Border: 1px solid Graphite
- Padding: 16px
- Border Radius: 4px
- Font: Inter, 18px
- Color: Warm White

**Focus State**:
- Border Color: Warm White
- Box Shadow: 0 0 0 3px rgba(245, 240, 230, 0.1)
- Outline: None

---

## Animation Standards

### Transition Timing

| Name | Duration | Easing | Use |
|------|----------|--------|-----|
| Fast | 150ms | ease | Quick feedback |
| Normal | 200ms | ease | Standard transitions |
| Slow | 300ms | ease | Deliberate animations |

### Animation Rules

**DO**:
- Use consistent timing (200ms standard)
- Use ease easing function
- Animate transform and opacity
- Respect reduced motion preference

**DON'T**:
- Animate layout properties
- Use long durations (> 500ms)
- Use complex easing
- Ignore performance

---

## Shadow Standards

### Shadow Levels

| Name | Value | Use |
|------|-------|-----|
| Small | `0 1px 2px rgba(0, 0, 0, 0.1)` | Subtle elevation |
| Medium | `0 2px 8px rgba(0, 0, 0, 0.1)` | Standard cards |
| Large | `0 4px 16px rgba(0, 0, 0, 0.15)` | Hover states |

### Shadow Rules

**DO**:
- Use subtle shadows
- Elevate on hover
- Maintain consistency
- Use sparingly

**DON'T**:
- Use heavy shadows
- Over-shadow elements
- Mix shadow styles
- Ignore depth hierarchy

---

## Border Radius Standards

| Name | Value | Use |
|------|-------|-----|
| Small | 2px | Subtle rounding |
| Medium | 4px | Standard (buttons, cards) |
| Large | 8px | Prominent rounding |

### Border Radius Rules

**DO**:
- Use consistent radius (4px standard)
- Round buttons and cards
- Maintain subtlety
- Match brand aesthetic

**DON'T**:
- Use excessive rounding
- Mix radius sizes
- Round everything
- Ignore consistency

---

## Accessibility Standards

### Color Contrast

- **Normal text**: 4.5:1 minimum
- **Large text**: 3:1 minimum
- **UI components**: 3:1 minimum

### Focus States

- Visible focus indicators
- 2px outline offset
- Warm White color
- Smooth transitions

### Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Quality Checklist

### Visual Consistency
- [ ] Typography scale applied consistently
- [ ] Spacing system (8-point grid) used throughout
- [ ] Color palette applied correctly
- [ ] Component styles consistent
- [ ] Animation timing standardized
- [ ] Shadow levels appropriate
- [ ] Border radius consistent

### Professional Polish
- [ ] Smooth transitions
- [ ] Proper hover states
- [ ] Loading states
- [ ] Error states
- [ ] Empty states
- [ ] Focus indicators
- [ ] Responsive design

### Accessibility
- [ ] Color contrast (WCAG AA)
- [ ] Keyboard navigation
- [ ] Screen reader support
- [ ] Focus indicators
- [ ] Reduced motion support

---

*These visual standards ensure a consistent, professional, and accessible design system across the Truth Forge website.*
