# CTDL ALIGNMENT STRATEGY (High Fidelity)

**Date**: January 7, 2026
**Status**: ACTIVE / DURABLE
**Standard**: Credential Transparency Description Language (CTDL)

---

## 1. THE MANDATE
The Truth Engine and Credential Atlas are hereby aligned with the CTDL Technical Specification. This alignment ensures that our internal Knowledge Atoms and external Marketplace entities speak a unified, global language of transparency.

## 2. SCHEMA MAPPING (The Spine)

| Internal Concept | CTDL Term (URI) | Implementation State |
| :--- | :--- | :--- |
| **Unique Identifier** | `ctid` (`ceterms:ctid`) | **Enforced** as Primary Key |
| **Credential** | `ceterms:Credential` | Table: `credentials` |
| **Organization** | `ceterms:CredentialOrganization` | Table: `organizations` |
| **Learning Opportunity** | `ceterms:LearningOpportunity` | Table: `learning_opportunities` |
| **Assessment** | `ceterms:Assessment` | Table: `assessments` |
| **Competency/Skill** | `ceasn:Competency` | Mapping in Progress (Knowledge Atoms) |
| **Transfer Value** | `ceterms:TransferValueProfile` | Future Ingestion Pillar |

## 3. THE VERSIONING PROTOCOL (Fidelity)
Alignment requires not just structural matching but temporal integrity. We utilize a **Temporal Versioning Pattern** in DuckDB:
- `is_current`: Direct access to the "Single Source of Truth."
- `version_id`: Sequential historical record.
- `valid_from`: Audit-trail timestamp.

## 4. RESONANCE INTEGRATION
The **Resonance Service** (Trinity Matching) is the mechanism that validates internal truths against CTDL-published data.
- **Input**: CTDL JSON-LD / Registry Exports.
- **Agent**: Vector resonance matching against internal Knowledge Atoms.
- **Output**: Verified CTDL-compliant match records.

## 5. DURABILITY COMMITMENT
All future entity creation, enrichment, or ingestion MUST prioritize the use of CTDL property names (e.g., `ceterms:name`, `ceterms:description`, `ceterms:subjectWebpage`). When local extensions are needed, they will be namespaced as `pe:` (Primitive Engine).

---

*This document is a living part of the Framework and must be referenced during every ingestion cycle.*
