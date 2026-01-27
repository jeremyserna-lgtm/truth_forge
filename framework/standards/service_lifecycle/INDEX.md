# Service Lifecycle Standard

**The Standard** | Every service must proceed through a defined lifecycle.

**Status**: ACTIVE
**Owner**: US
**Last Updated**: 2026-01-26

---

## Purpose

To provide a structured, predictable, and governed lifecycle for all technical services, from initial idea to final retirement. This ensures that development effort is aligned, and services are managed sustainably.

---

## Quick Reference

**The Five Phases of a Service's Life:**

1.  **PROPOSAL:** An idea is formally documented, including its `product/` definition. **Gate:** Approval by `ME`.
    -   **Special Requirement:** For "genesis" class organisms, the proposal MUST include an **Observation Plan** detailing how the organism's creation will be recorded from inception.

2.  **PROTOTYPE:** An experimental version is built to test core hypotheses. **Gate:** Validation of assumptions.
3.  **ACTIVE:** The service is built to production standards and fully supported. **Gate:** Passes all `validation/` checks.
4.  **DEPRECATED:** The service is marked for retirement; a migration plan is communicated. **Gate:** `molt` plan is in place.
5.  **SUNSET:** The service is shut down, and its resources are archived. **Gate:** All users migrated.

---

## Documents

| Document | Purpose |
|----------|---------|
| [PROPOSAL.md](PROPOSAL.md) | The template for proposing a new service. |
| [ACTIVE_REQUIREMENTS.md](ACTIVE_REQUIREMENTS.md) | The checklist for a service to be considered "production-ready".|
| [SUNSET_PLAN.md](SUNSET_PLAN.md) | The template for planning the retirement of a service. |

---

## Convergence

### Top-Down (Theory Shapes This)

-   [05_EXTENSION](../../05_EXTENSION.md) - The "Molt" is the trigger for `DEPRECATED` and `SUNSET` phases.
-   [02_PERCEPTION](../../02_PERCEPTION.md) - `SEE:SEE:DO:DONE` aligns with `PROPOSAL` -> `PROTOTYPE` -> `ACTIVE`.

### Bottom-Up (This Requires)

-   [product/](../product/) - A `PROPOSAL` is incomplete without a product definition.
-   [operations/](../operations/) - `ACTIVE_REQUIREMENTS` must include operational readiness.
-   [validation/](../validation/) - A service cannot become `ACTIVE` without passing validation gates.

---
## UP

[../INDEX.md](../INDEX.md)
