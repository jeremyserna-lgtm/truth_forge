# Credential Atlas LLC — Reference

**Last Updated**: January 20, 2026

---

## 🔑 MASTER SPECIFICATION

**For complete architecture, Definition of Done, and spawn protocol:**

→ **[.agent/CREDENTIAL_ATLAS_MASTER_SPEC.md](/.agent/CREDENTIAL_ATLAS_MASTER_SPEC.md)**

This document contains:
- The DIVIDE (Primitive BUILDS, Credential Atlas SEES)
- Complete architecture (19 intelligence modules, 7 engagement modules)
- Federation protocol (CloudEvents + W3C DIDs)
- Definition of Done — Primitive Engine (20 items)
- Definition of Done — Credential Atlas (14 items)
- Spawn protocol and benchmark test

---

## The Divide

```
┌─────────────────────────────────────────────────────────────────┐
│                        TRUTH ENGINE                              │
│                                                                  │
│   ┌─────────────────────┐     ┌─────────────────────┐          │
│   │  Primitive Engine   │     │  Credential Atlas   │          │
│   │     (Genesis)       │────▶│    (Daughter)       │          │
│   │                     │     │                     │          │
│   │      BUILDS         │     │       SEES          │          │
│   │   Creates structure │     │   Creates insight   │          │
│   │   Implements        │     │   Verifies          │          │
│   │   FERTILE           │     │   STERILE           │          │
│   └─────────────────────┘     └─────────────────────┘          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Repository Locations

| Repository | Path | Purpose |
|------------|------|---------|
| **Truth Engine** | `/Users/jeremyserna/Truth_Engine/` | Infrastructure / Organism |
| **Credential Atlas** | `/Users/jeremyserna/credential_atlas/` | Product / Business |

### Truth Engine (Infrastructure)

Contains:
- Primitive Engine (the nucleus)
- Seeding machinery (`Primitive/seed/`)
- Daughter templates (`Primitive/seed/templates/credential_atlas/`)
- Federation protocol
- Master specification (`.agent/CREDENTIAL_ATLAS_MASTER_SPEC.md`)

### Credential Atlas (Product)

Contains:
- Business documentation (`docs/`)
- API implementation (`credential_bridge/`)
- Customer-facing product code

---

## Authoritative Business Documents

All business documentation lives in:

```
/Users/jeremyserna/credential_atlas/docs/
```

| Document | Purpose |
|----------|---------|
| `BUSINESS_PLAN.md` | Complete business strategy |
| `ONE_PAGER.md` | Outreach document |
| `THE_VISION.md` | Product architecture |
| `THE_PRODUCT.md` | "AI Comes With" concept |
| `EVERYONE_WINS.md` | Stakeholder value map |
| `STATUS.md` | Current build status |

---

## Authoritative Technical Documents

Architecture and spawn specifications live in:

```
/Users/jeremyserna/Truth_Engine/.agent/
```

| Document | Purpose |
|----------|---------|
| `CREDENTIAL_ATLAS_MASTER_SPEC.md` | Complete architecture specification |
| `INDEX.md` | Agent Knowledge Center navigation |
| `ACTIVE_PROCESSES.md` | What's in progress |

---

## Quick Navigation

| If You Need | Go To |
|-------------|-------|
| Architecture / Spawn Protocol | `.agent/CREDENTIAL_ATLAS_MASTER_SPEC.md` |
| Business Plan | `/credential_atlas/docs/BUSINESS_PLAN.md` |
| Product Vision | `/credential_atlas/docs/THE_VISION.md` |
| Seeding Code | `Primitive/seed/seed_project.py` |
| Federation Protocol | `Primitive/seed/federation.py` |
| Intelligence Modules | `Primitive/seed/templates/credential_atlas/src/intelligence/` |

---

*For all architectural questions, refer to `.agent/CREDENTIAL_ATLAS_MASTER_SPEC.md`*
*For all business questions, refer to `/credential_atlas/docs/`*
