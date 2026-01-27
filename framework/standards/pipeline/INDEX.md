# Pipeline Standard

**The Standard** | HOLD → AGENT → HOLD at every stage. Batch only. Never drop data.

**Status**: ACTIVE
**Owner**: Framework
**Last Updated**: 2026-01-26

---

## Purpose

This standard defines how all pipelines are built in truth_forge. Every pipeline follows the same universal pattern, the same batch loading approach, and the same quality gates.

---

## Quick Reference

**Every pipeline MUST:**

1. Follow `HOLD → AGENT → HOLD` pattern at every stage
2. Use **batch loading only** - no streaming
3. Connect stages at HOLDs, never at AGENTs
4. Use `identity_service` for all ID generation (THE GATE - Stage 3)
5. Include Stage Five Grounding documentation
6. Register with PipelineTracker for monitoring
7. Apply THE FURNACE PRINCIPLE: Truth → Meaning → Care
8. Use **type hints** on all functions (PEP 484)
9. Implement **retry logic with exponential backoff** for external calls
10. Use **structured logging** with key-value pairs
11. Quarantine failures to **dead letter queue** (never drop data)
12. Pass **mypy, ruff, pytest** before merge

**This is not optional. This is the standard.**

---

## Layer Definition

For WHY this layer exists and WHAT a pipeline primitive IS, see [README.md](README.md).

---

## Documents

| Document | Purpose | Lines |
|----------|---------|-------|
| [CORE_PATTERN.md](CORE_PATTERN.md) | HOLD:AGENT:HOLD, batch loading, connection rules | ~120 |
| [STAGES.md](STAGES.md) | 16-stage architecture, THE GATE | ~150 |
| [TEMPLATES.md](TEMPLATES.md) | Stage script template, configuration | ~150 |
| [QUALITY.md](QUALITY.md) | Quality gates, error handling, logging | ~180 |
| [VERIFICATION.md](VERIFICATION.md) | Testing, data quality, reference | ~150 |

---

## The Universal Pattern

```
HOLD₁ (input)  →  AGENT (process)  →  HOLD₂ (output)
```

**Every stage. Every pipeline. Every time.**

See [CORE_PATTERN.md](CORE_PATTERN.md) for details.

---

## The 16 Stages

| Phase | Stages | Purpose |
|-------|--------|---------|
| **Ingestion** | 0-4 | Raw → Cleaned → Validated |
| **Entity Creation** | 5-8 | L1 Tokens → L8 Conversations |
| **Enrichment** | 9-13 | Embeddings → Relationships |
| **Finalization** | 14-16 | Validation → Promotion |

See [STAGES.md](STAGES.md) for details.

---

## Folder Structure

```
pipelines/{pipeline_name}/
├── __init__.py
├── config.yaml
├── stage_0_assessment.py
├── ...
├── stage_16_promotion.py
├── run_pipeline.py
└── tests/
```

---

## Pattern Coverage

### ME:NOT-ME

Pipeline development serves both:
- **ME** (human): Readable templates, navigable structure
- **NOT-ME** (AI): Consistent patterns, searchable conventions

### HOLD:AGENT:HOLD

This standard IS THE PATTERN. Every section, every document, every stage follows HOLD:AGENT:HOLD.

### TRUTH:MEANING:CARE

| Phase | Application |
|-------|-------------|
| **TRUTH** | Raw data exists (input HOLD) |
| **MEANING** | Transform adds understanding (AGENT) |
| **CARE** | Output is usable (output HOLD) |

### SEE:SEE:DO

| Phase | Application |
|-------|-------------|
| **SEE** | "I see data needs processing" |
| **SEE:SEE** | "I recognize this needs 16 stages" |
| **DO** | Build pipeline following standard |
| **SEE:DO** | Verify all quality gates pass |

---

## Convergence

### Bottom-Up Validation

This standard requires meta-standards:
- [STANDARD_STRUCTURE](../STANDARD_STRUCTURE.md) - Three-tiered structure
- [STANDARD_OPTIMIZATION](../STANDARD_OPTIMIZATION.md) - Document splitting
- [STANDARD_COMPLETION](../STANDARD_COMPLETION.md) - Definition of done

### Top-Down Validation

This standard is shaped by theory:
- [04_ARCHITECTURE](../../04_ARCHITECTURE.md) - HOLD:AGENT:HOLD
- [03_METABOLISM](../../03_METABOLISM.md) - TRUTH:MEANING:CARE
- [06_LAW](../../06_LAW.md) - Fail-Safe, Idempotency

---

## Related Standards

| Standard | Relationship |
|----------|--------------|
| [code_quality/](../code_quality/) | Code quality for pipeline scripts |
| [error_handling/](../error_handling/) | DLQ and retry patterns |
| [logging/](../logging/) | Structured logging requirements |
| [testing/](../testing/) | Test requirements for pipelines |

---

## Definition of Done (This Iteration)

- [x] Split from 1136 lines to 5 documents
- [x] Each document under 200 lines
- [x] Navigation document created
- [x] Pattern coverage section added
- [x] Convergence section added

*This iteration is DONE. The loop continues.*

**Next SEE**: Apply same splitting to other oversized standards

---

*HOLD → AGENT → HOLD. Batch only. Never drop data.*
