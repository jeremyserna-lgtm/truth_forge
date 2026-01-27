# Credential Atlas Website

MOLT LINEAGE:
- Source: Truth_Engine/apps/credential_atlas/ (reference only)
- Version: 1.0.0
- Date: 2026-01-27

## Purpose

The website for Credential Atlas LLC - THE SEER.
Platform for credential verification, identity attestation, and trust certification.

## Architecture

```
apps/websites/credential_atlas/
├── src/
│   ├── components/       # Page-specific components
│   ├── pages/           # Route pages
│   ├── styles/          # Page-specific styles
│   └── App.tsx          # Main application
├── public/              # Static assets
└── package.json         # Dependencies
```

## Features

- **Credential Verification**: Verify digital credentials
- **Trust Scores**: View and generate trust attestations
- **Identity Portal**: Manage identity profiles
- **API Access**: Developer documentation for integration

## THE PATTERN

```
Verification Request (HOLD1) → Credential Validator (AGENT) → Trust Report (HOLD2)
```

## Module Federation

Consumes shared components from `apps/websites/shared/`:
- Header
- Footer
- Navigation
- TrustBadge
- VerificationStatus

## Pages

| Route | Purpose |
|-------|---------|
| `/` | Landing page with service overview |
| `/verify` | Credential verification portal |
| `/trust` | Trust score lookup |
| `/identity` | Identity management |
| `/developers` | API documentation |
| `/about` | About Credential Atlas |

## Primitive

**SEE** - The Credential Atlas sees what cannot be seen. It reveals trust.

## Fertility

**STERILE** - Does not spawn children. Focuses on certification and attestation.

## Development

```bash
npm install
npm run dev        # Start development server
npm run build      # Production build
npm run preview    # Preview production build
```

## Environment Variables

```env
VITE_API_URL=http://localhost:8002
VITE_SHARED_URL=http://localhost:3000
```
