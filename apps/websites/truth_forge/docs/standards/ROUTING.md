# Routing Standards

**Purpose**: Page structure, navigation, and URL patterns for the Truth Forge website

**Status**: Active  
**Last Updated**: 2026-01-27

---

## Core Principles

### Clean, Semantic URLs

URLs should be:
- **Human-readable**: Clear what the page contains
- **SEO-friendly**: Include relevant keywords
- **Consistent**: Follow established patterns
- **Hierarchical**: Reflect site structure

---

## Route Structure

### Current Routes

| Route | Component | Purpose |
|-------|-----------|---------|
| `/` | `Home.tsx` | Landing page with framework overview |
| `/about` | `About.tsx` | Company identity and story |
| `/framework` | `Framework.tsx` | Framework documentation |
| `/what-is-not-me` | `WhatIsNotMe.tsx` | Not-Me product explanation |
| `/meet-not-me` | `MeetNotMe.tsx` | Not-Me introduction |
| `/vision` | `Vision.tsx` | Company vision |
| `/science` | `Science.tsx` | Research and science |
| `/privacy-deployments` | `PrivacyDeployments.tsx` | Privacy and deployment info |
| `/preorder` | `PreOrder.tsx` | Preorder form |
| `/resources` | `Resources.tsx` | Resources and links |

---

## URL Patterns

### Pattern Rules

1. **Lowercase**: All URLs use lowercase
2. **Hyphens**: Use hyphens for word separation (`what-is-not-me`)
3. **No Trailing Slash**: Remove trailing slashes (`/about` not `/about/`)
4. **No File Extensions**: No `.html` or other extensions

### Examples

```
✅ CORRECT:
/about
/what-is-not-me
/privacy-deployments

❌ WRONG:
/About
/what_is_not_me
/privacy_deployments
/about/
/about.html
```

---

## Page Structure

### Standard Page Template

Every page follows this structure:

```tsx
export default function PageName() {
  return (
    <>
      {/* Hero Section */}
      <section className="page-hero">
        <div className="container centered">
          <h1>Page Title</h1>
          <p className="page-intro">Brief introduction</p>
        </div>
      </section>

      {/* Main Content */}
      <section className="page-content">
        <div className="container">
          {/* Content sections */}
        </div>
      </section>

      {/* CTA Section (if applicable) */}
      <section className="page-cta">
        <div className="container">
          {/* Call to action */}
        </div>
      </section>
    </>
  );
}
```

---

## Navigation Structure

### Header Navigation

```
[LOGO] Truth Forge    [About] [Framework] [Resources] [Preorder Button]
```

**Max 5 navigation items** (excluding logo and CTA)

### Footer Navigation

```
TRUTH ENGINE FAMILY
Truth Engine | Primitive Engine | Credential Atlas | Stage 5 Mind

[Current Brand]          [Resources]           [Connect]
• About                 • Documentation        • Email
• Products              • Support              • LinkedIn
• Contact
```

---

## SEO Requirements

### Page Metadata

Each page must include:

```tsx
// In page component or route config
export const metadata = {
  title: 'Page Name | Truth Forge',
  description: '150-160 character description with keywords',
  keywords: 'relevant, keywords, here',
};
```

### Heading Hierarchy

- **Single H1** per page (page title)
- **Logical H2-H6** structure
- **No skipped levels** (H2 → H3, not H2 → H4)

---

## Internal Linking

### Link Patterns

```tsx
// ✅ CORRECT: Use React Router Link
import { Link } from 'react-router-dom';
<Link to="/framework">Framework</Link>

// ✅ CORRECT: External links
<a href="https://example.com" target="_blank" rel="noopener noreferrer">
  External Link
</a>
```

### Link Text

- **Descriptive**: Link text should describe destination
- **No "Click Here"**: Use meaningful text
- **Context**: Link text should make sense out of context

---

## UP

[INDEX.md](INDEX.md)
