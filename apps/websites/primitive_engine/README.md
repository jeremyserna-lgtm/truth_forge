# Primitive Engine Website

MOLT LINEAGE:
- Source: Truth_Engine/apps/primitive_app/ (reference only)
- Version: 1.0.0
- Date: 2026-01-27

## Purpose

The website for Primitive Engine LLC - THE BUILDER.
Platform for building, spawning, and managing primitives.

## Architecture

```
apps/websites/primitive_engine/
├── src/
│   ├── components/       # Builder components
│   ├── pages/           # Route pages
│   ├── styles/          # UI styles
│   └── App.tsx          # Main application
├── public/              # Static assets
└── package.json         # Dependencies
```

## Features

- **Slot Builder**: Visual interface for creating primitives
- **Template Library**: Pre-built primitive templates
- **Deployment**: One-click primitive deployment
- **Monitoring**: Runtime primitive health

## THE PATTERN

```
Build Request (HOLD1) → Primitive Builder (AGENT) → Deployed Primitive (HOLD2)
```

## Primitive

**EXIST:NOW** - The Primitive Engine exists in the present, building the future.

## Fertility

**FERTILE** - Spawns children (primitives). Each primitive can become its own organism.

## Module Federation

Consumes shared components from `apps/websites/shared/`:
- Header
- Footer
- Navigation
- SlotEditor
- TemplateGallery
- DeploymentStatus

## Pages

| Route | Purpose |
|-------|---------|
| `/` | Landing page with builder overview |
| `/builder` | Visual primitive builder |
| `/templates` | Template library |
| `/primitives` | Deployed primitives list |
| `/deploy` | Deployment interface |
| `/developers` | API documentation |

## Slot Builder Features

From Truth_Engine/apps/primitive-slot-builder:
- Visual slot configuration
- Real-time preview
- Template import/export
- Gemini integration for AI-assisted building

## Development

```bash
npm install
npm run dev        # Start development server
npm run build      # Production build
npm run preview    # Preview production build
```

## Environment Variables

```env
VITE_API_URL=http://localhost:8004
VITE_SHARED_URL=http://localhost:3000
VITE_GEMINI_API_KEY=your_key_here
```

## Migration Note

The primitive-slot-builder from Truth_Engine will be integrated as the `/builder` feature.
This is tracked as Phase 10.1 in PROGRESS.md.
