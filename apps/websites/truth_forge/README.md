# Truth Forge Website

MOLT LINEAGE:
- Source: New creation (no prior source)
- Version: 1.0.0
- Date: 2026-01-27

## Purpose

The primary website for Truth Forge - THE GENESIS holding company.
Central hub for framework documentation, organism status, and governance visibility.

## Architecture

```
apps/websites/truth_forge/
├── src/
│   ├── components/       # Page-specific components
│   ├── pages/           # Route pages
│   ├── styles/          # Page-specific styles
│   └── App.tsx          # Main application
├── public/              # Static assets
└── package.json         # Dependencies
```

## Features

- **Framework Overview**: THE PATTERN, THE GRAMMAR, THE PILLARS
- **Organism Status**: Real-time health of child organisms
- **Governance Dashboard**: Cost tracking, audit trails
- **Documentation**: Standards, decisions, guidelines

## THE PATTERN

```
Website Request (HOLD1) → Content Server (AGENT) → Rendered Page (HOLD2)
```

## Module Federation

Consumes shared components from `apps/websites/shared/`:
- Header
- Footer
- Navigation
- ThePattern
- CostBadge
- OrganismTree

## Pages

| Route | Purpose |
|-------|---------|
| `/` | Landing page with framework overview |
| `/framework` | Detailed framework documentation |
| `/organisms` | Child organism status and health |
| `/governance` | Cost and audit dashboard |
| `/standards` | Code quality standards |
| `/decisions` | Architecture Decision Records |

## Development

```bash
npm install
npm run dev        # Start development server
npm run build      # Production build
npm run preview    # Preview production build
```

## Environment Variables

```env
VITE_API_URL=http://localhost:8000
VITE_SHARED_URL=http://localhost:3000
```

## Deployment

Deploys to Vercel/Cloudflare Pages. Uses Module Federation for shared components.
