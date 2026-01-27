# Operations Standard

**The Standard** | Every active service must be deployable, observable, cost-managed, and supportable.

**Status**: ACTIVE
**Owner**: NOT-ME
**Last Updated**: 2026-01-26

---

## Purpose

To ensure that all `ACTIVE` services are reliable, sustainable, and manageable in a production environment. This standard is the embodiment of `CARE` for the `NOT-ME` system itself.

---

## Quick Reference

**Every `ACTIVE` service MUST:**

1.  Have an automated **Deployment** process ([DEPLOYMENT.md](DEPLOYMENT.md)).
2.  Implement structured **Observability** (logs, metrics, traces) ([OBSERVABILITY.md](OBSERVABILITY.md)).
3.  Include **Cost Management** controls and reporting ([COST_MANAGEMENT.md](COST_MANAGEMENT.md)).
4.  Have a defined **Incident Response** plan ([INCIDENT_RESPONSE.md](INCIDENT_RESPONSE.md)).

---

## Documents

| Document | Purpose |
|----------|---------|
| [DEPLOYMENT.md](DEPLOYMENT.md) | Standards for CI/CD, infrastructure-as-code. |
| [OBSERVABILITY.md](OBSERVABILITY.md) | Requirements for structured logging, metrics, and tracing. |
| [COST_MANAGEMENT.md](COST_MANAGEMENT.md) | Rules for cost estimation, budget alerts, and resource tagging. |
| [INCIDENT_RESPONSE.md](INCIDENT_RESPONSE.md)| Defines on-call rotation, alert severity, and postmortem process. |

---

## Convergence

### Top-Down (Theory Shapes This)

-   [01_IDENTITY](../../01_IDENTITY.md) - The "Protocol of Dual Reality" is the primary driver.
-   [06_LAW](../../06_LAW.md) - The "Pillar of Observability" is directly implemented here.
-   [03_METABOLISM](../../03_METABOLISM.md) - An "incident" is a "crisis" to be metabolized by the furnace.

### Bottom-Up (This Requires)

-   [service_lifecycle/](../service_lifecycle/) - A service must meet these standards to become `ACTIVE`.
-   [logging/](../logging/) - Provides the specific implementation for `OBSERVABILITY.md`.
-   [configuration/](../configuration/) - Essential for managing deployments across environments.

---
## UP

[../INDEX.md](../INDEX.md)
