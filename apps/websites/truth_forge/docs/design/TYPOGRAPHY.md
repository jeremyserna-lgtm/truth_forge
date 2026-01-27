# Typography System

**Version:** 1.0  
**Created:** January 24, 2026  
**Selection:** Option A "Industrial Prestige" (Nano Banana Pro recommendation)

---

## Primary Typefaces

### Display: Instrument Serif

**Source:** Google Fonts  
**Use:** Brand names, headlines, section titles, hero text

**Characteristics:**
- Sharp, mechanical serif
- Constructed feel that matches the lightning bolt geometry
- Premium without feeling old or traditional
- Works at large sizes

**Application by Brand:**

| Brand | Treatment | Example |
|-------|-----------|---------|
| Truth Engine | All caps, tracked +50 | `TRUTH ENGINE` |
| Primitive Engine | All caps, tracked +50 | `PRIMITIVE ENGINE` |
| Credential Atlas | All caps, tracked +50 | `CREDENTIAL ATLAS` |
| Stage 5 Mind | Title case, tracked +25 | `Stage 5 Mind` |

**CSS:**
```css
font-family: 'Instrument Serif', serif;
font-weight: 400;
letter-spacing: 0.05em; /* for all caps */
text-transform: uppercase; /* except Stage 5 Mind */
```

---

### Body/Technical: JetBrains Mono

**Source:** Google Fonts / JetBrains  
**Use:** Specifications, pricing, technical details, unit designations, code, data

**Characteristics:**
- Monospaced (all characters same width)
- Designed for code readability
- Signals "technical hardware" and "engineering"
- Grounds the premium feel in reality

**Application:**

| Context | Example |
|---------|---------|
| Unit designation | `UNIT 01 / PERSONAL AI SYSTEM` |
| Pricing | `$12,500` |
| Specifications | `1.28TB UNIFIED MEMORY` |
| Data points | `130,000+ CONVERSATIONS` |
| Technical labels | `BUILD SYSTEMS` |

**CSS:**
```css
font-family: 'JetBrains Mono', monospace;
font-weight: 400;
letter-spacing: 0.02em;
text-transform: uppercase;
font-size: 0.75em; /* typically smaller than display */
```

---

### Body Copy: Inter

**Source:** Google Fonts  
**Use:** Paragraphs, descriptions, long-form content

**Characteristics:**
- Clean, highly legible
- Neutral but not cold
- Designed for screens
- Variable font with many weights

**Application:**
- Website body text
- Product descriptions
- Documentation
- UI elements

**CSS:**
```css
font-family: 'Inter', sans-serif;
font-weight: 400;
line-height: 1.6;
```

---

## Type Scale

Based on 16px base, using 1.25 ratio (Major Third):

| Name | Size | Use |
|------|------|-----|
| Hero | 64px / 4rem | Landing page headlines |
| H1 | 40px / 2.5rem | Page titles |
| H2 | 32px / 2rem | Section headers |
| H3 | 25px / 1.563rem | Subsection headers |
| H4 | 20px / 1.25rem | Card titles |
| Body | 16px / 1rem | Paragraphs |
| Small | 14px / 0.875rem | Captions, labels |
| Micro | 12px / 0.75rem | Technical specs |

---

## Pairing Examples

### Hero Lockup
```
TRUTH ENGINE                    ← Instrument Serif, 64px, tracked
UNIT 01 / PERSONAL AI SYSTEM    ← JetBrains Mono, 14px, tracked
```

### Product Card
```
PRIMITIVE ENGINE                ← Instrument Serif, 32px
BUILD SYSTEMS                   ← JetBrains Mono, 12px
                               
The infrastructure layer...     ← Inter, 16px
```

### Pricing Display
```
SOLDIER TIER                    ← Instrument Serif, 24px
$12,500                         ← JetBrains Mono, 48px
One-time investment             ← Inter, 14px
```

### Technical Specification
```
MEMORY           1.28TB UNIFIED     ← JetBrains Mono, all
PROCESSING       M4 ULTRA × 4
STORAGE          8TB NVMe
```

---

## Brand-Specific Rules

### Truth Engine (Holding Company)
- Most authoritative treatment
- Instrument Serif always ALL CAPS
- Heaviest weight where variable
- Maximum tracking (+50)

### Primitive Engine (Builder)
- Industrial, workshop feel
- Same typography but can use bolder weights
- May appear with more texture/distress

### Credential Atlas (Seer)
- Precision, clarity
- Same typography but lighter touch
- Clean, minimal texture

### Stage 5 Mind (Consumer)
- Warmest, most human
- Instrument Serif in TITLE CASE (not all caps)
- Reduced tracking (+25)
- Inter for body at warmer weight (450)

---

## Loading Fonts

### Google Fonts Import
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

### CSS Variables
```css
:root {
  --font-display: 'Instrument Serif', serif;
  --font-mono: 'JetBrains Mono', monospace;
  --font-body: 'Inter', sans-serif;
  
  --tracking-wide: 0.05em;
  --tracking-normal: 0.02em;
  --tracking-tight: -0.01em;
}
```

---

## Forbidden Patterns

- Never use Instrument Serif for body copy (too decorative at small sizes)
- Never use JetBrains Mono for headlines (loses premium feel)
- Never mix more than these three typefaces
- Never use decorative or script fonts
- Never use default system fonts for branded materials
- Never reduce tracking below normal for display text

---

*Typography is credibility. These fonts signal: permanent, technical, premium, human.*
