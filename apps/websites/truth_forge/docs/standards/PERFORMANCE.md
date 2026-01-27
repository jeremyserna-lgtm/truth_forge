# Performance Standards

**Purpose**: Performance requirements and optimization standards for the Truth Forge website

**Status**: Active  
**Last Updated**: 2026-01-27

---

## Core Requirements

### Lighthouse Targets

| Metric | Target | Minimum |
|--------|--------|---------|
| **Performance** | 95+ | 90 |
| **Accessibility** | 100 | 95 |
| **Best Practices** | 100 | 95 |
| **SEO** | 100 | 95 |

---

## Key Metrics

### First Contentful Paint (FCP)

**Target**: < 1.5 seconds  
**Minimum**: < 2.5 seconds

**Optimization**:
- Critical CSS inlined
- Fonts preloaded
- Above-fold content prioritized

### Largest Contentful Paint (LCP)

**Target**: < 2.5 seconds  
**Minimum**: < 4.0 seconds

**Optimization**:
- Optimize hero images
- Use WebP format with fallback
- Lazy load below-fold images

### Time to Interactive (TTI)

**Target**: < 3.0 seconds  
**Minimum**: < 5.0 seconds

**Optimization**:
- Code splitting
- Lazy loading
- Minimize JavaScript bundle size

### Cumulative Layout Shift (CLS)

**Target**: < 0.1  
**Minimum**: < 0.25

**Optimization**:
- Set image dimensions
- Reserve space for dynamic content
- Avoid inserting content above existing content

---

## Image Optimization

### Formats

1. **WebP** (primary) - Modern browsers
2. **JPEG/PNG** (fallback) - Legacy browsers

### Sizing

- **Hero images**: Max 1920px width
- **Card images**: Max 800px width
- **Thumbnails**: Max 400px width

### Lazy Loading

```tsx
// ✅ CORRECT: Lazy load below-fold images
<img 
  src={imageSrc} 
  alt={altText}
  loading="lazy"
/>

// ✅ CORRECT: Eager load above-fold images
<img 
  src={heroImageSrc} 
  alt={altText}
  loading="eager"
/>
```

---

## Code Optimization

### Bundle Size

- **Initial bundle**: < 200KB (gzipped)
- **Route chunks**: < 100KB each (gzipped)
- **Total JavaScript**: < 500KB (gzipped)

### Code Splitting

```tsx
// ✅ CORRECT: Lazy load routes
import { lazy } from 'react';
const About = lazy(() => import('./pages/About'));

// ✅ CORRECT: Lazy load heavy components
const HeavyComponent = lazy(() => import('./components/HeavyComponent'));
```

### Tree Shaking

- Use named imports
- Avoid importing entire libraries
- Use ES modules

---

## Font Optimization

### Font Loading

```html
<!-- Preconnect to font CDN -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

<!-- Preload critical fonts -->
<link 
  rel="preload" 
  href="https://fonts.googleapis.com/css2?family=Instrument+Serif&display=swap" 
  as="style"
>

<!-- Load fonts -->
<link 
  href="https://fonts.googleapis.com/css2?family=Instrument+Serif&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" 
  rel="stylesheet"
>
```

### Font Display

```css
@font-face {
  font-family: 'Instrument Serif';
  font-display: swap; /* Show fallback until font loads */
}
```

---

## Caching Strategy

### Static Assets

- **Images**: Cache for 1 year
- **Fonts**: Cache for 1 year
- **CSS/JS**: Cache for 1 year with versioning

### HTML

- **Cache-Control**: `no-cache` (always check for updates)
- **ETag**: Enabled for validation

---

## Monitoring

### Tools

- **Lighthouse CI**: Automated performance checks
- **Web Vitals**: Real user monitoring
- **Bundle Analyzer**: Track bundle size

### Alerts

- Lighthouse score drops below 90
- Bundle size exceeds limits
- Core Web Vitals degrade

---

## UP

[INDEX.md](INDEX.md)
