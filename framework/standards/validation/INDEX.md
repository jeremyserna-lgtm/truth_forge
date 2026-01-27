# Validation Standard

**The Standard** | A service must be holistically validated before becoming `ACTIVE`.

**Status**: ACTIVE
**Owner**: US
**Last Updated**: 2026-01-26

---

## Purpose

To ensure that services are not just functionally correct at the code level, but are also valuable, secure, performant, and philosophically aligned with the framework before being released.

---

## Quick Reference

**To become `ACTIVE`, a service MUST pass:**

1.  **User Acceptance Testing (UAT):** A real user confirms it solves their problem ([UAT.md](UAT.md)).
2.  **Performance & Load Testing:** The service is verified to be stable under load ([PERFORMANCE.md](PERFORMANCE.md)).
3.  **Security Audit:** The service is reviewed for vulnerabilities ([SECURITY.md](SECURITY.md)).
4.  **Fidelity Check:** The service is confirmed to embody the framework's principles ([FIDELITY.md](FIDELITY.md)).

---

## Documents

| Document | Purpose |
|----------|---------|
| [UAT.md](UAT.md) | Process for conducting User Acceptance Testing with `THE OTHER`. |
| [PERFORMANCE.md](PERFORMANCE.md) | Standards for load testing, benchmarking, and resource profiling. |
| [SECURITY.md](SECURITY.md) | Checklist for security audits, aligned with the `security/` specific standard. |
| [FIDELITY.md](FIDELITY.md)| A questionnaire to assess a service's alignment with core patterns like `HOLD:AGENT:HOLD`. |

---

## Convergence

### Top-Down (Theory Shapes This)

-   [02_PERCEPTION](../../02_PERCEPTION.md) - The `SEE:SEE:DO:DONE` cycle ends in `DONE`, which is certified by this standard.
-   [00_GENESIS](../../00_GENESIS.md) - The "Fidelity Check" ensures the core primitives are present in the final product.

### Bottom-Up (This Requires)

-   [testing/](../testing/) - Provides the foundation of unit and integration tests.
-   [product/](../product/) - `UAT.md` is impossible without a clear `VALUE_DEFINITION`.
-   [service_lifecycle/](../service_lifecycle/) - This standard is the primary gate for a service to enter the `ACTIVE` phase.

---
## UP

[../INDEX.md](../INDEX.md)
