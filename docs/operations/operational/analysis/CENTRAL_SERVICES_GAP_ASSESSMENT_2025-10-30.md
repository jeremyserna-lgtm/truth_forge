# Central Services Gap Assessment & Emergent Tool Alignment
**Date:** 2025-10-30
**Audience:** Claude Code implementation lead
**Prepared by:** Codex (Codex CLI)

---

## 1. Executive Summary

Central services now provide stable identity, logging, configuration, and enrichment foundations, yet critical control and integration gaps remain. Emergent tooling across the workspace (Layered Reasoning Engine, Reasoning Trace Analyzer, Emergent Asset Detector, etc.) operates without centralized governance, validation, or safe execution guarantees. This document catalogs the issues, maps them to required central-service extensions, and provides concrete implementation recommendations for Claude Code to execute.

---

## 2. Current Central Service Footprint

| Service | Status | Notes |
|---------|--------|-------|
| `identity_service` | ✅ Production | Hierarchical ID generation; BigQuery-backed registry. |
| `log_service` | ✅ Production | Structured JSON logging to local file; BigQuery export pending. |
| `config_service` | ✅ Production | TOML-based config with BigQuery client singleton. |
| `feedback_service` | ✅ Production (80%) | Multi-tier enrichment (Tier 1 → Flash → Pro); calibration loop pending. |
| `document_service` | 🚧 In Progress | Markdown shredding + ingestion; Universal Spine integration unfinished. |
| `attribution_service` | 🚧 In Progress | Tool usage extraction and authorship classification; no downstream integration yet. |
| `validation_service` | 🟡 Stub | Only design prompts; no executable validation routines. |
| `security_service` | 🟡 Stub | Enforcement concepts only. |
| `governance_service` | 🟡 Stub | Policy definitions planned. |
| `planning_service` | 🟡 Stub | Task planning unimplemented. |
| `orchestration_service` | 🟡 Stub | Multi-agent coordination requirements documented but inactive. |
| `query_service` | 🟡 Stub | Unified read interface not implemented. |

Supporting documentation confirms these statuses (`architect_central_services/docs/STATUS.md`).

---

## 3. Workspace Risk & Issue Inventory

### 3.1 Emergent Tooling Without Safety Rails
- **Layered Reasoning & Tool Development Engines** (`tools/layered_reasoning_engine.py`, `tools/tool_development_engine.py`) call Vertex AI directly with hard-coded project/location/model values and manual credential handling. No central quota or logging oversight exists.
- **Universal Pattern Detector** (`tools/universal_pattern_detector/pattern_detector.py`) defaults to scanning the entire home directory and lacks allowlists or dry-run enforcement for potentially destructive moves.
- **Emergent Asset Detector** (`tools/emergent_asset_detector.py`) performs wide filesystem sweeps and writes results without routing telemetry through central logging.
- **Reasoning Trace Suite** (`tools/reasoning_trace_analyzer.py`, `tools/reasoning_trace_loader.py`) generates governance-critical data, yet there is no validation or schema enforcement before data touches BigQuery.

### 3.2 Incomplete Document Management
- `_holding/` and other staging directories accumulate emergent artefacts; `document_service` is not yet processing or organizing them into the canonical document spine.

### 3.3 Missing Validation & Security Controls
- `validation_service` is a documentation placeholder; there is no central schema validation for conversation or emergent tool outputs.
- `security_service` doesn't enforce path allowlists, sensitive-zone restrictions, or destructive-operation approvals.

### 3.4 No Emergent Tool Registry
- The curated manifest at `policy/emergent_tools_manifest.json` is disconnected from central services; no service consumes it to track tool health, install status, or telemetry.

---

## 4. Required Central Service Enhancements

### 4.1 Emergent Tool Service (New module: `architect_central_services/emergent_service/`)
**Purpose:** Act as the central registry and control plane for emergent tooling.
- Ingest `policy/emergent_tools_manifest.json` and store tool metadata (version, path, status, integration targets).
- Provide registration APIs (CLI + Python) for tools to announce themselves and receive configuration (log destinations, allowed paths, BigQuery datasets).
- Emit structured telemetry (`log_service.log_event`) for tool runs, health checks, and installation status.
- Offer installation hooks (`pip install -e`) and dependency verification for each tool family.

**Implementation Notes for Claude Code:**
1. Create `src/architect_central_services/emergent_service/__init__.py` with a registry interface.
2. Add manifest parsing + validation (JSON schema in `/docs/schemas/emergent_tool_manifest.json`).
3. Extend `central_config.toml` with emergent service settings and default paths.

### 4.2 Model Runtime Gateway (Extend `feedback_service` or add `model_runtime_service`)
**Purpose:** Centralize AI model usage (Vertex, Claude, Copilot) to enforce quotas, log usage, and standardize credentials.
- Wrap Vertex AI initialization; provide a factory that returns authorized clients while logging each invocation.
- Support opt-in cost tracking and rate limiting per tool slug.
- Expose safe default models and allow override via config service.

**Implementation Notes:**
1. Add `architect_central_services/model_runtime_service.py` with a `ModelRuntimeGateway` class.
2. Replace direct `vertexai.init` calls in tooling with gateway usage (update manifest accordingly).

### 4.3 Validation Service (Activate existing stub)
**Purpose:** Enforce schema and data-quality checks before BigQuery writes or orchestration steps.
- Implement validators for conversation spine tables, reasoning trace payloads, and emergent-tool outputs.
- Provide CLI hooks (`python -m architect_central_services.validation_service validate <schema> <file>`).
- Integrate with conversation pipeline and emergent tools (manifest ties validators to tools).

**Implementation Notes:**
1. Build a `BaseValidator` class with pluggable schema definitions (JSON schema, Pydantic, or custom).
2. Add specific validators for conversation pipeline outputs and reasoning traces.
3. Route validation results to log service + governance service once available.

### 4.4 Security & Governance Enforcement
**Security Service:** Implement path allowlists/denylists and hazardous-operation prompts.
- Provide context managers (`with security_service.safe_operation(tool_slug, path)`) to guard file operations.
- Maintain central safe-path configuration in `central_config.toml`.

**Governance Service:** Define policy templates and ensure emergent tools check policy compliance (naming standards, documentation updates) post-run.

### 4.5 Document Service Completion
**Objective:** Finalize ingestion so `_holding/` and emergent tool outputs flow into the document spine.
- Implement pipeline to read `_holding/` directories, apply validation, shred into spine format, and archive originals.
- Integrate with emergent service to process outputs automatically once registered.

---

## 5. Emergent Tool Deployment Alignment

### Summary of Major Tools (see `docs/analysis/EMERGENT_TOOLS_CATALOG.md`)
| Tool | Control Needs | Central Service Touchpoints |
|------|---------------|-----------------------------|
| Layered Reasoning Engine | Model gateway, logging, manifest registration | `model_runtime_service`, `log_service`, `emergent_service` |
| Tool Development Engine | Same as above | Same as above |
| Reasoning Trace Analyzer Suite | Validation, log routing | `validation_service`, `log_service`, `emergent_service` |
| Emergent Asset Detector | Security guardrails, logging | `security_service`, `log_service`, `emergent_service` |
| Universal Pattern Detector | Security guardrails, config-managed patterns | `security_service`, `config_service`, `emergent_service` |
| Conversation Tagger modules | Validation, conversation pipeline integration | `validation_service`, `conversation_pipeline` |
| Zoom Watcher detectors | Logging, security approval | `log_service`, `security_service` |
| Web Metadata Card Generator | Validation, ingestion to conversation/document pipelines | `validation_service`, `document_service` |

Implementation detail: update the manifest with dependencies and target services for each tool (already added in `policy/emergent_tools_manifest.json`).

---

## 6. Action Plan for Claude Code

1. **Stand Up Emergent Service**
   - Scaffold the new module.
   - Build manifest ingestion, registry APIs, and telemetry hooks.
   - Write smoke tests to confirm manifest parsing and registration flows.

2. **Add Model Runtime Gateway**
   - Implement central Vertex AI client management.
   - Patch emergent tools to route through the gateway (coordinate with tool owners).
   - Log each model invocation with tool slug and cost metadata.

3. **Activate Validation Service**
   - Produce at least two validators (conversation spine, reasoning trace payload).
   - Provide CLI commands and integrate into conversation pipeline tests.
   - Emit validation results to log service for auditing.

4. **Enhance Security Service**
   - Implement safe path allowlists and context managers.
   - Require emergent tools to wrap filesystem operations with security service checks.
   - Log blocked operations for review.

5. **Complete Document Service**
   - Finish ingestion > shredding > storage pipeline.
   - Ensure emergent outputs are routed into managed storage (e.g., `substrate/tier2_infrastructure`).
   - Provide cleanup scripts to empty `_holding/` safely after ingestion.

6. **Testing & Documentation**
   - Extend `tests/` with unit tests for each new service component.
   - Update central service READMEs and `docs/STATUS.md` with new capabilities.
   - Document integration steps for emergent tools in `docs/analysis/EMERGENT_TOOLS_CATALOG.md` and tool-specific READMEs.

---

## 7. Dependencies & Coordination Notes

- Emergent service will depend on the curated manifest staying current; schedule quarterly refreshes (run `tools/emergent_asset_detector.py --json`) followed by manual review.
- All tooling changes must align with `docs/core/ENTERPRISE_ENGINEERING_STANDARD.md` (no shortcuts, evidence-backed results, cross-system updates).
- Coordinate with the conversation pipeline team when introducing validation to avoid breakages.
- Once the emergent service is live, update operational runbooks to register and monitor new tools automatically.

---

## 8. Appendix

- Manifest: `policy/emergent_tools_manifest.json`
- Catalog: `docs/analysis/EMERGENT_TOOLS_CATALOG.md`
- Central Service Status: `architect_central_services/docs/STATUS.md`
- Architectural Review: `architect_central_services/docs/ARCHITECTURAL_REVIEW_2025-10-30.md`
- Enterprise Standard: `docs/core/ENTERPRISE_ENGINEERING_STANDARD.md`

This document should be handed to Claude Code as the implementation brief for the next development cycle.***
