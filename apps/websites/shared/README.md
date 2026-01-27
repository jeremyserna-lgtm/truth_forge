# Shared Website Components

MOLT LINEAGE:
- Source: Truth_Engine/apps/websites/shared/
- Version: 2.0.0
- Date: 2026-01-26

## Purpose

Shared components, utilities, and styles used across all truth_forge websites.
Implements Module Federation for micro-frontend architecture.

## Structure

```
apps/websites/shared/
├── components/           # Shared React components
│   ├── Header/
│   ├── Footer/
│   ├── Navigation/
│   └── ThePattern/      # Visual THE PATTERN component
├── hooks/               # Shared React hooks
├── utils/               # Utility functions
├── styles/              # Shared CSS/Tailwind styles
└── types/               # Shared TypeScript types
```

## Module Federation

This package is exposed via Module Federation for consumption by:
- truth_forge website
- credential_atlas website
- not_me website
- primitive_engine website

## Key Components

### ThePattern
Visual representation of HOLD → AGENT → HOLD pattern.

### CostBadge
Displays current cost governance status.

### OrganismTree
Hierarchical view of the organism structure.

## Usage

```tsx
// In consuming app
import { Header, ThePattern } from 'shared/components';

function App() {
  return (
    <>
      <Header title="Truth Forge" />
      <ThePattern />
    </>
  );
}
```

## Development

```bash
npm install
npm run dev
npm run build
```
