# Website Design Standards

**Version:** 1.0
**Created:** January 24, 2026
**Scope:** All Truth Engine family websites

---

## Core Principle

Every website should feel like **a physical space**—not a digital interface. Visitors should feel they've entered somewhere crafted, warm, and permanent.

---

## Design Philosophy

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

## Page Templates

### 1. Homepage

**Structure:**
```
┌─────────────────────────────────────────────────────────────┐
│ NAVIGATION (sticky)                                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    HERO SECTION                             │
│          [Logo Mark - textured, prominent]                  │
│          [Tagline - Instrument Serif]                       │
│          [Single CTA - accent color]                        │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    VALUE PROPOSITION                        │
│          [3-4 core benefits, icon + text]                   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    PRODUCT/SERVICE GRID                     │
│          [Cards with hover states]                          │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    SOCIAL PROOF                             │
│          [Testimonials or metrics]                          │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    FINAL CTA                                │
│          [Strong call to action]                            │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                    FOOTER                                   │
│          [Family brands + legal + contact]                  │
└─────────────────────────────────────────────────────────────┘
```

### 2. Product/Service Page

**Structure:**
```
┌─────────────────────────────────────────────────────────────┐
│ NAVIGATION                                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    PRODUCT HERO                             │
│          [Product name - Instrument Serif]                  │
│          [Descriptor - JetBrains Mono]                      │
│          [Key visual or diagram]                            │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    FEATURES                                 │
│          [Alternating left/right sections]                  │
│          [Image + text blocks]                              │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    SPECIFICATIONS                           │
│          [JetBrains Mono table]                             │
│          [Technical details]                                │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    PRICING                                  │
│          [Tier cards or simple display]                     │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                    CTA + FOOTER                             │
└─────────────────────────────────────────────────────────────┘
```

### 3. About Page

**Structure:**
```
┌─────────────────────────────────────────────────────────────┐
│ NAVIGATION                                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    STORY HERO                               │
│          [Headline - Instrument Serif]                      │
│          [Opening narrative - Inter]                        │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    THE ARCHITECT                            │
│          [Photo/visual of Jeremy]                           │
│          [Bio text]                                         │
│          [Credentials - JetBrains Mono]                     │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    PHILOSOPHY                               │
│          [The Framework essence]                            │
│          [ME / NOT-ME concept]                              │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    BRAND FAMILY                             │
│          [Links to all brands]                              │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                    FOOTER                                   │
└─────────────────────────────────────────────────────────────┘
```

### 4. Contact Page

**Structure:**
```
┌─────────────────────────────────────────────────────────────┐
│ NAVIGATION                                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    CONTACT HERO                             │
│          [Headline - "Let's Talk"]                          │
│          [Brief intro text]                                 │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│     FORM                    │     CONTACT INFO              │
│     [Name]                  │     [Email]                   │
│     [Email]                 │     [Phone]                   │
│     [Subject]               │     [Location]                │
│     [Message]               │                               │
│     [Submit]                │                               │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                    FOOTER                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Navigation

### Header Navigation

**Structure:**
```
[LOGO MARK]  [Brand Name]     [Nav Item]  [Nav Item]  [Nav Item]  [CTA Button]
```

**Behavior:**
- Sticky on scroll (dark background on scroll)
- Mobile: Hamburger menu
- Max 5 navigation items
- CTA always visible

**Styling:**
```css
.nav {
  background: var(--bg-primary);
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav-link {
  font-family: var(--font-mono);
  font-size: 0.875rem;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  color: var(--text-secondary);
}

.nav-link:hover {
  color: var(--accent);
}
```

### Footer Structure

**Standard footer for all sites:**

```
────────────────────────────────────────────────────────────────
TRUTH ENGINE FAMILY
────────────────────────────────────────────────────────────────
Truth Engine    Primitive Engine    Credential Atlas    Stage 5 Mind
────────────────────────────────────────────────────────────────

[Current Brand]              [Resources]           [Connect]
• About                      • Documentation       • Email
• Products                   • Support             • LinkedIn
• Contact

────────────────────────────────────────────────────────────────
© 2026 Truth Engine LLC. All rights reserved.
Privacy Policy  ·  Terms of Service
────────────────────────────────────────────────────────────────
```

---

## Component Library

### Hero Sections

**Full-bleed hero:**
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
  font-size: 4rem;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  margin-bottom: 1rem;
}

.hero-tagline {
  font-family: var(--font-body);
  font-size: 1.25rem;
  color: var(--text-secondary);
  font-style: italic;
  margin-bottom: 2rem;
}
```

### Buttons

**Primary button:**
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
}
```

**Secondary button:**
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

### Cards

**Product/feature card:**
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

### Forms

**Input fields:**
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

### Specification Tables

**For technical details:**
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

## Responsive Breakpoints

| Name | Width | Description |
|------|-------|-------------|
| Mobile | < 640px | Single column, stacked elements |
| Tablet | 640-1024px | Two columns where appropriate |
| Desktop | 1024-1440px | Full layout |
| Wide | > 1440px | Constrained max-width |

**Max content width:** 1200px
**Container padding:** 2rem (desktop), 1rem (mobile)

```css
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

@media (max-width: 640px) {
  .container {
    padding: 0 1rem;
  }
}
```

---

## Brand-Specific Variations

### Truth Engine (Hub)

| Element | Treatment |
|---------|-----------|
| Hero | Largest, most authoritative |
| Color | Warm white accents |
| Texture | Medium (30%) |
| Typography | Heaviest weights |
| Content | Company-level, hub for all brands |

### Primitive Engine

| Element | Treatment |
|---------|-----------|
| Hero | Industrial feel, workshop imagery |
| Color | Forge gold accents |
| Texture | Heavy (60%) |
| Typography | Bold, industrial |
| Content | Technical, developer-focused |

### Credential Atlas

| Element | Treatment |
|---------|-----------|
| Hero | Clean, precise |
| Color | Steel blue accents |
| Texture | Light (15%) |
| Typography | Clean, precise |
| Content | Enterprise, institutional |

### Stage 5 Mind

| Element | Treatment |
|---------|-----------|
| Hero | Warm, inviting |
| Color | Amber accents |
| Texture | Light (15-20%) |
| Typography | Title case, softer |
| Content | Personal, discovery-focused |

---

## Technical Requirements

### Performance

- **Lighthouse score:** Minimum 90 on all metrics
- **First Contentful Paint:** < 1.5s
- **Time to Interactive:** < 3s
- **Image format:** WebP with JPEG fallback
- **Lazy loading:** All below-fold images

### SEO

- **Page titles:** `[Page Name] | [Brand Name]`
- **Meta descriptions:** 150-160 characters, include keywords
- **Heading hierarchy:** Single H1 per page, logical H2-H6
- **Alt text:** All images described
- **Schema markup:** Organization, Product where applicable

### Accessibility

- **WCAG 2.1 AA compliance** minimum
- **Keyboard navigation:** All interactive elements focusable
- **Screen readers:** Semantic HTML, ARIA labels where needed
- **Reduced motion:** Respect `prefers-reduced-motion`
- **Color contrast:** 4.5:1 for text, 3:1 for UI elements

---

## Implementation Stack (Recommended)

### For Marketing Sites

| Layer | Technology | Reasoning |
|-------|------------|-----------|
| Framework | Next.js 14+ | Static generation, performance |
| Styling | Tailwind CSS | Utility-first, consistent |
| Animations | Framer Motion | Accessible, performant |
| CMS | Sanity or Contentful | Headless, flexible |
| Hosting | Vercel | Integrated with Next.js |
| Analytics | GA4 + Plausible | Privacy-respecting option |

### CSS Custom Properties

```css
:root {
  /* Colors - see COLOR_SYSTEM.md */
  --bg-primary: #0D0D0D;
  --bg-secondary: #1A1A1A;
  --bg-tertiary: #2D2D2D;
  --text-primary: #F5F0E6;
  --text-secondary: #B5B5B5;
  --text-muted: #888888;
  --border: #4A4A4A;
  --border-subtle: #2D2D2D;

  /* Typography - see TYPOGRAPHY_SYSTEM.md */
  --font-display: 'Instrument Serif', serif;
  --font-mono: 'JetBrains Mono', monospace;
  --font-body: 'Inter', sans-serif;

  /* Spacing */
  --space-xs: 0.5rem;
  --space-sm: 1rem;
  --space-md: 2rem;
  --space-lg: 4rem;
  --space-xl: 8rem;

  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-normal: 200ms ease;
  --transition-slow: 300ms ease;
}
```

---

## Pre-Launch Checklist

### Design

- [ ] All pages match brand standards
- [ ] Typography correctly applied
- [ ] Colors match brand palette
- [ ] Textures at correct levels
- [ ] Logo used correctly
- [ ] Responsive on all breakpoints

### Content

- [ ] All copy reviewed and approved
- [ ] No placeholder text
- [ ] All images optimized
- [ ] Alt text on all images
- [ ] Contact info correct

### Technical

- [ ] Lighthouse score > 90
- [ ] All links work
- [ ] Forms submit correctly
- [ ] Analytics installed
- [ ] SSL certificate active
- [ ] Meta tags complete

### Legal

- [ ] Privacy policy published
- [ ] Terms of service published
- [ ] Cookie consent if needed
- [ ] Copyright notice correct

---

*A website is a threshold. When visitors cross it, they should feel they've entered somewhere real, crafted, and permanent.*
