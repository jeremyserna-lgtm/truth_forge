# Document

**The Standard** | Documents are the universal primitive. Eight primitives govern all documents.

**Authority**: [07_STANDARDS.md](../../07_STANDARDS.md) | **Status**: CANONICAL

---

## THIS IS THE HUB

```
            ┌───────────────────────────────────────┐
            │        document/INDEX.md              │
            │     START/END for document layer      │
            └─────────────────┬─────────────────────┘
                              │
   ┌───────┬───────┬───────┬──┴──┬───────┬───────┬───────┐
   ▼       ▼       ▼       ▼     ▼       ▼       ▼       ▼
LENGTH  ANCHOR  NAVIG.  STRUCT  GRAM.  LAYER  LINKS  COMPLETE
   │       │       │       │     │       │       │       │
   └───────┴───────┴───────┴──┬──┴───────┴───────┴───────┘
                              │
                         UP → INDEX (to move layers)
```

| Direction | Where It Goes |
|-----------|---------------|
| **UP** | [standards/INDEX.md](../INDEX.md) (parent layer) |
| **DOWN** | Eight primitives (see Quick Reference) |
| **ACROSS** | [code_quality/](../code_quality/), [planning/](../planning/) |

---

## Quick Reference (Assessment Criteria)

| Primitive | Should Cover | Go Here |
|-----------|--------------|---------|
| Length | 300-line limit, split patterns, compress vs expand, storage vs reading | [LENGTH.md](LENGTH.md) |
| Anchor | One topic rule, limits/envelopes, exclusion test, split signal | [ANCHOR.md](ANCHOR.md) |
| Navigation | UP-only rule, why not mesh, hub pattern, HOLD:AGENT parallel | [NAVIGATION.md](NAVIGATION.md) |
| Structure | Primitive structure, INDEX structure, section limits, checklist | [STRUCTURE.md](STRUCTURE.md) |
| Grammar | Three marks (`:` `-` `_`), document naming, folder naming, descent | [GRAMMAR.md](GRAMMAR.md) |
| Layer | Four layers, layer locations, determining layer, bleed test | [LAYER.md](LAYER.md) |
| Links | Hub vs mesh, the pattern, HOLD:AGENT parallel, structure changes | [LINKS.md](LINKS.md) |
| Completeness | 5W+H, WHO/WHAT/WHEN/WHERE/WHY/HOW, three-part form | [COMPLETENESS.md](COMPLETENESS.md) |

---

## Documents

| Document | Lines | Purpose |
|----------|-------|---------|
| [LENGTH.md](LENGTH.md) | 93 | Line limits, split patterns |
| [ANCHOR.md](ANCHOR.md) | 64 | One topic, exclusion test |
| [NAVIGATION.md](NAVIGATION.md) | 59 | UP link pattern |
| [STRUCTURE.md](STRUCTURE.md) | 80 | Section requirements |
| [GRAMMAR.md](GRAMMAR.md) | 69 | Naming conventions |
| [LAYER.md](LAYER.md) | 58 | Content layer rules |
| [LINKS.md](LINKS.md) | 68 | Hub vs mesh navigation |
| [COMPLETENESS.md](COMPLETENESS.md) | 150 | 5W+H completeness |

---

## Layer Definition

For WHY this layer exists and WHAT a document primitive IS, see [README.md](README.md).

---

## Convergence

### Bottom-Up (requires these meta-standards)

- [STANDARD_LIMIT](../STANDARD_LIMIT.md) - Line and section limits
- [STANDARD_ANCHOR](../STANDARD_ANCHOR.md) - One topic per document
- [STANDARD_NAMING](../STANDARD_NAMING.md) - THE GRAMMAR
- [STANDARD_STRUCTURE](../STANDARD_STRUCTURE.md) - INDEX vs primitive roles

### Top-Down (shaped by theory)

- [00_GENESIS](../../00_GENESIS.md) - Documents as universal primitive
- [01_IDENTITY](../../01_IDENTITY.md) - ME:NOT-ME dual reader
- [04_ARCHITECTURE](../../04_ARCHITECTURE.md) - HOLD:AGENT:HOLD pattern

---

## Related Standards

| Standard | Relationship |
|----------|--------------|
| [code_quality/](../code_quality/) | Docstrings follow document standard |
| [planning/](../planning/) | Plans are documents |
| [deprecation/](../deprecation/) | Deprecated documents follow lifecycle |

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-01-26 | Added assessment criteria to Quick Reference | Claude |
| 2026-01-26 | Reduced to navigation per STANDARD_STRUCTURE | Claude |
| 2026-01-26 | Expanded to full format | Claude |
| 2026-01-25 | Initial 8 primitives | Claude |

---

*Documents are the universal primitive. INDEX navigates AND assesses.*
