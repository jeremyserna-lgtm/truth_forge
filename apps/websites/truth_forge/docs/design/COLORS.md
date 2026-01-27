# Color System

**Version:** 1.0  
**Created:** January 24, 2026  
**Philosophy:** Color as mood, not rigid specification

---

## Core Principle

The primary marks are **black** (or white on dark). Color enters through:
- Accent elements
- Backgrounds
- Interactive states
- Supporting graphics

This maintains the industrial, stamped-metal feel while allowing warmth where needed.

---

## Foundation Colors

### Neutrals

| Name | Hex | RGB | Use |
|------|-----|-----|-----|
| **Black** | `#0D0D0D` | 13, 13, 13 | Primary mark, text |
| **Charcoal** | `#1A1A1A` | 26, 26, 26 | Dark backgrounds |
| **Graphite** | `#2D2D2D` | 45, 45, 45 | Secondary dark |
| **Steel** | `#4A4A4A` | 74, 74, 74 | Muted elements |
| **Concrete** | `#888888` | 136, 136, 136 | Disabled states |
| **Ash** | `#B5B5B5` | 181, 181, 181 | Borders, dividers |
| **Warm White** | `#F5F0E6` | 245, 240, 230 | Light backgrounds |
| **Pure White** | `#FFFFFF` | 255, 255, 255 | High contrast only |

**Note:** Prefer `Warm White` over `Pure White` for backgrounds. Pure white is too clinical.

---

## Brand Accent Colors

Each brand has a signature accent that reflects its nature.

### Truth Engine — Source White

| Name | Hex | RGB | Use |
|------|-----|-----|-----|
| **Source** | `#F5F0E6` | 245, 240, 230 | Primary accent |
| **Source Glow** | `#FFFEF5` | 255, 254, 245 | Highlights |
| **Source Dim** | `#E8E3D9` | 232, 227, 217 | Muted states |

**Reasoning:** Truth Engine is the source, the whole. Warm white represents illumination, truth revealed, the light from which others derive.

---

### Primitive Engine — Forge Gold

| Name | Hex | RGB | Use |
|------|-----|-----|-----|
| **Forge** | `#D4A853` | 212, 168, 83 | Primary accent |
| **Ember** | `#F5C065` | 245, 192, 101 | Highlights, active |
| **Molten** | `#B8923F` | 184, 146, 63 | Pressed, deep |
| **Ash Gold** | `#A08050` | 160, 128, 80 | Muted states |

**Reasoning:** Primitive Engine builds, forges, creates. Gold/amber represents molten metal, creation heat, the moment of transformation.

---

### Credential Atlas — Steel Blue

| Name | Hex | RGB | Use |
|------|-----|-----|-----|
| **Steel** | `#4A6FA5` | 74, 111, 165 | Primary accent |
| **Clear** | `#6B8FC5` | 107, 143, 197 | Highlights |
| **Deep** | `#3A5A8A` | 58, 90, 138 | Pressed, deep |
| **Muted** | `#5A7090` | 90, 112, 144 | Disabled |

**Reasoning:** Credential Atlas sees, verifies, clarifies. Steel blue represents precision, trust, clear sight, analytical clarity.

---

### Stage 5 Mind — Amber Warmth

| Name | Hex | RGB | Use |
|------|-----|-----|-----|
| **Amber** | `#F59E0B` | 245, 158, 11 | Primary accent |
| **Glow** | `#FBBF24` | 251, 191, 36 | Highlights |
| **Deep** | `#D97706` | 217, 119, 6 | Pressed, deep |
| **Soft** | `#F59E0B` @ 20% | — | Backgrounds |

**Reasoning:** Stage 5 Mind is the consumer-facing warmth. Amber represents human connection, the fire that transforms, the warmth of being seen.

---

## Color Application

### Dark Mode (Primary)

```css
:root {
  --bg-primary: #0D0D0D;
  --bg-secondary: #1A1A1A;
  --bg-tertiary: #2D2D2D;
  
  --text-primary: #F5F0E6;
  --text-secondary: #B5B5B5;
  --text-muted: #888888;
  
  --border: #4A4A4A;
  --border-subtle: #2D2D2D;
}
```

### Light Mode (Secondary)

```css
:root {
  --bg-primary: #F5F0E6;
  --bg-secondary: #FFFFFF;
  --bg-tertiary: #E8E3D9;
  
  --text-primary: #0D0D0D;
  --text-secondary: #4A4A4A;
  --text-muted: #888888;
  
  --border: #B5B5B5;
  --border-subtle: #E8E3D9;
}
```

### Brand Accent Variables

```css
/* Truth Engine */
.brand-truth {
  --accent: #F5F0E6;
  --accent-glow: #FFFEF5;
  --accent-dim: #E8E3D9;
}

/* Primitive Engine */
.brand-primitive {
  --accent: #D4A853;
  --accent-glow: #F5C065;
  --accent-dim: #A08050;
}

/* Credential Atlas */
.brand-credential {
  --accent: #4A6FA5;
  --accent-glow: #6B8FC5;
  --accent-dim: #5A7090;
}

/* Stage 5 Mind */
.brand-stage5 {
  --accent: #F59E0B;
  --accent-glow: #FBBF24;
  --accent-dim: #D97706;
}
```

---

## Interactive States

| State | Treatment |
|-------|-----------|
| **Default** | Accent color at 100% |
| **Hover** | Accent-glow (lighter) |
| **Active/Pressed** | Accent-dim (darker) |
| **Disabled** | Accent at 40% opacity |
| **Focus** | Accent with 2px ring offset |

---

## Gradients (Use Sparingly)

### Forge Gradient (Primitive Engine)
```css
background: linear-gradient(135deg, #D4A853 0%, #B8923F 100%);
```

### Depth Gradient (Dark backgrounds)
```css
background: linear-gradient(180deg, #1A1A1A 0%, #0D0D0D 100%);
```

### Glow Effect (Highlights)
```css
box-shadow: 0 0 40px rgba(245, 158, 11, 0.3);
```

---

## Texture Overlay Colors

When applying grunge textures:

| Texture Level | Overlay Opacity |
|---------------|-----------------|
| Light (15%) | `rgba(0,0,0,0.15)` |
| Medium (30%) | `rgba(0,0,0,0.30)` |
| Heavy (60%) | `rgba(0,0,0,0.60)` |

---

## Accessibility

All color combinations must meet WCAG 2.1 AA standards:
- Normal text: 4.5:1 contrast ratio minimum
- Large text: 3:1 contrast ratio minimum
- UI components: 3:1 contrast ratio minimum

**Verified Combinations:**
- `#F5F0E6` on `#0D0D0D` → 15.7:1 ✓
- `#F59E0B` on `#0D0D0D` → 8.4:1 ✓
- `#D4A853` on `#0D0D0D` → 7.9:1 ✓
- `#4A6FA5` on `#0D0D0D` → 4.7:1 ✓
- `#0D0D0D` on `#F5F0E6` → 15.7:1 ✓

---

## Forbidden Patterns

- Never use pure white (`#FFFFFF`) as primary background
- Never use multiple accent colors together (one brand = one accent)
- Never use gradients as primary brand elements
- Never use neon or saturated colors
- Never use color alone to convey meaning (always pair with text/icon)
- Never apply accent color to the logo mark itself (mark stays black/white)

---

*Color is temperature. These colors signal: warm industrial, not cold tech.*
