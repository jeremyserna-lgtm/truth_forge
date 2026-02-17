# 10_SERVICE_SPECIFICATIONS

**The blueprints for each organ.**

*This document provides the technical contract for each service in the `truth_forge` organism.*

---

## Core Principle

Each service is a specialized cell with a **Membrane** (its public API) and a **Nucleus** (its private `HOLD_2` state). Communication happens via the `ServiceMediator` (the bloodstream), and no service ever accesses another's internal state.

---

### `KnowledgeService` (The Digestive System)

*   **Role:** Catabolism. Breaks raw data into Knowledge Atoms.
*   **Public API:**
    *   `inhale(data: dict)`: Receives raw data from the `ServiceMediator`. Writes to its `HOLD_1` intake file.
    *   `query(query: str, ...)`: Allows other services to retrieve processed Knowledge Atoms from its `HOLD_2`.
*   **`HOLD_2` Schema (`knowledge.duckdb`):**
    *   `id`: Unique ID for the Knowledge Atom.
    *   `data`: JSON object containing the full atom (source, content, extraction, llm_model, etc.).

---

### `ServiceMediator` (The Circulatory System)

*   **Role:** Resilient Transport. Routes events between services.
*   **Public API:**
    *   `publish(topic: str, data: dict)`: Publishes an event to the system. If the consumer is unavailable, the event is written to a Dead Letter Queue (DLQ).
*   **`HOLD_2` Schema:** N/A. Its resilience mechanism is its DLQ file, not a queryable state database.

---

### `GovernanceService` (The DNA & Immune System)

*   **Role:** Records the immutable history of the organism and enforces boundaries.
*   **Public API:**
    *   `inhale(data: dict)`: Receives event data from the `ServiceMediator`.
    *   `query_events(...)`: Allows other services to query the historical event log.
    *   `gate_operation(operation, source, target)`: Gates operations through governance checks.
    *   `check_cost(service, operation, estimated_cost)`: Validates budget before expensive operations.
    *   `record_cost(service, operation, actual_cost)`: Records actual cost after completion.
*   **`HOLD_2` Schema (`governance.duckdb`):**
    *   `id`: Unique ID for the event.
    *   `data`: JSON object containing the full event record.
    *   Indexed fields: `event_type`, `source`, `timestamp`.

#### Governance Subsystems

| Subsystem | Role | Biological Metaphor |
|-----------|------|---------------------|
| **UnifiedGovernance** | Orchestrates all governance components | Cell membrane (complete) |
| **HoldIsolation** | Enforces HOLD₁/HOLD₂ boundary integrity | Selective permeability |
| **AuditTrail** | Records all operations for compliance | Cellular memory (epigenetics) |
| **CostEnforcer** | Gates operations based on budget | Metabolic regulation |

#### HoldIsolation: The Membrane

Enforces the sacred boundaries of THE_PATTERN:
- HOLD₁ (intake) can only be written by external sources
- AGENT transforms HOLD₁ → HOLD₂
- HOLD₂ (processed) is the output, protected from direct writes

```
External → HOLD₁ → AGENT → HOLD₂ → Consumers
```

#### CostEnforcer: Metabolic Regulation

Every operation that consumes resources must pass through the cost gate:
- **BudgetConfig**: Daily, monthly, and per-run limits
- **CostAction**: ALLOW (soft limit), WARN, DENY, THROTTLE
- **CostRecord**: Tracks service, operation, cost_usd, tokens

#### AuditTrail: Cellular Memory

Every operation is recorded with:
- **AuditLevel**: DEBUG, INFO, WARNING, ERROR, CRITICAL, VIOLATION
- **AuditCategory**: HOLD_OPERATION, AGENT_ACTION, GOVERNANCE, COST, FEDERATION, SYSTEM
- **AuditRecord**: Immutable record with timestamp, run_id, context

---

### `LoggingService` (Internal Sense)

*   **Role:** Captures internal log data.
*   **Public API:**
    *   `inhale(data: dict)`: Receives structured log entries.
*   **Internal Logic:** Immediately publishes received log data to the `ServiceMediator` on the `knowledge.process` topic. It has no long-term state of its own.
*   **`HOLD_2` Schema:** Minimal. Only stores intake for short-term audit before passing it on.

---

### `SecretService` (Endocrine System)

*   **Role:** Manages access to external secrets.
*   **Public API:**
    *   `get_secret(secret_id: str)`: Synchronously retrieves a secret.
*   **Communication:** Called directly by services that need immediate access to credentials. This is an exception to the asynchronous default.
*   **`HOLD_2` Schema:** In-memory cache (`_cache` dictionary) backed by GCP Secret Manager.

---
## Proposed New Services
---

### `PerceptionService` (Sensory Organs)

*   **Role:** Perceives the external world.
*   **Public API:** N/A. It has no `inhale` method as it is a primary data source.
*   **Internal Logic:** Contains agents that run on a schedule or trigger.
    *   `scrape_website(url)`
    *   `poll_api(endpoint)`
    *   `watch_filesystem(path)`
*   **Output:** Publishes all findings as standardized "raw sensory data" events to the `ServiceMediator`.
*   **`HOLD_2` Schema:** `perception.duckdb`. Stores a record of what it has perceived and when, to avoid redundant work.

---

### `CognitionService` (The Brain - "ME" Service)

*   **Role:** Architect of the Self. As the primary "ME" service, it assembles Knowledge Atoms into plans, holds paradoxes, and performs self-analysis.
*   **Public API:**
    *   `inhale(data: dict)`: Receives goals from the user or `ServiceMediator`.
    *   `query_thoughts(...)`, `query_plans(...)`: Allows inspection of the organism's mental state.
    *   `query_paradoxes()`: Returns conflicting Knowledge Atoms the service is currently holding, reflecting its Stage 5 cognitive ability.
    *   `run_cognitive_diagnostic()`: Queries the `GovernanceService` for its own event history to analyze its cognitive resilience.
*   **Internal Logic:**
    1.  Continuously queries `KnowledgeService` for new Knowledge Atoms.
    2.  When conflicting atoms are found, it holds them as valid within different contexts rather than forcing resolution.
    3.  Receives goals via `inhale`.
    4.  Consults the `RelationshipService` to understand the relational context of the goal.
    5.  Formulates a plan, defaulting to `prepare_briefing` actions for the user to proxy, embodying the "Trusted System Proxy" pattern.
    6.  Publishes the context-aware plan to the `ServiceMediator`.
*   **`HOLD_2` Schema (`cognition.duckdb`):** A complex database representing the organism's beliefs, plans, active paradoxes, and self-awareness model.

---

### `ActionService` (The Motor System)

*   **Role:** Executes commands on the external world, embodying the "Trusted System Proxy" pattern.
*   **Public API:**
    *   `inhale(data: dict)`: Receives command events from the `ServiceMediator`.
*   **Internal Logic:** Contains a library of motor functions. The default for external communication is `prepare_briefing`.
    *   `prepare_briefing(for_user, content)`: Creates a draft communication for the user to review and send.
    *   `send_notification(to_user, message)`: Sends an *internal* alert to the primary user/operator.
    *   `write_file(path, content)`
*   **Output:** Publishes the result of the action (e.g., "briefing_prepared") back to the `ServiceMediator`.
*   **`HOLD_2` Schema (`action.duckdb`):** Stores an audit log of all actions taken and their outcomes.

---

### `RelationshipService` (Social Bonding System)

*   **Role:** Manages partnerships, trust levels, and interaction context. Embodies the principles of "Cognitive Orthogonality" and "Shared Context."
*   **Public API:**
    *   `get_partnership(partner_id: str)`: Retrieves the full context of a relationship.
    *   `update_interaction(partner_id: str)`: Logs a new interaction, updating metrics like `trust_level` and `interaction_count`.
*   **Internal Logic:**
    1.  Maintains a durable record of all entities the organism interacts with.
    2.  Uses heuristics to update trust scores based on the outcomes of interactions (e.g., successful plan execution, positive feedback).
*   **`HOLD_2` Schema (`relationship.duckdb`):**
    *   `id`: `partner_id` (unique identifier for the person or system).
    *   `data`: JSON object containing the `Partnership` model, including `trust_level`, `interaction_count`, `preferences`, and interaction history.
---
## Agentic Protocol Landscape
---

### External Protocol Integration Architecture

Truth Forge unifies three complementary agentic protocols into a coherent interoperability layer, enabling autonomous agent operations across discovery, payment, and credentialing.

```
┌─────────────────────────────────────────────────────────────────────┐
│                       EXTERNAL AGENT                                 │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 1: MCP (Model Context Protocol)                              │
│  ─────────────────────────────────────                              │
│  Standard: Anthropic (Nov 2024) - adopted by OpenAI, Google, MS     │
│  Purpose: Tool discovery, invocation, and API abstraction           │
│  Truth Forge Tools: verify_claim, issue_credential, query_spine     │
│  Implementation: mcp-servers/truth-engine-mcp/                      │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 2: x402 Protocol (Coinbase)                                  │
│  ────────────────────────────────                                   │
│  Standard: HTTP 402 Payment Required + USDC on Base                 │
│  Purpose: Autonomous agent-to-agent payments without API keys       │
│  Flow: Request → 402 → Sign Payment → Fulfill                       │
│  Implementation: src/truth_engine/x402/payments.py                  │
│  Related: AP2 (Agent Payments Protocol) - Google partnership        │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 3: W3C Verifiable Credentials 2.0                            │
│  ───────────────────────────────────────                            │
│  Standard: W3C Recommendation (May 2025)                            │
│  Purpose: Interoperable credential issuance and verification        │
│  Ecosystem: EU EBSI, MIT Digital Credentials, TruAge                │
│  Role: Credential Atlas as VC Issuer/Verifier                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Protocol Comparison & Selection Rationale

| Protocol | Origin | Purpose | Truth Forge Role |
|----------|--------|---------|------------------|
| **MCP** | Anthropic (2024) | Tool discovery & invocation | Primary agent interface |
| **x402** | Coinbase (2025) | Autonomous micropayments | NOT-ME economic layer |
| **W3C VC 2.0** | W3C (2025) | Credential interoperability | Credential Atlas standard |
| **AP2** | Google + Coinbase | Agent Payments Protocol | Interoperability bridge |

### Competing Standards (Not Adopted)

| Standard | Why Not Selected |
|----------|------------------|
| **OpenAPI + Function Calling** | Vendor-specific, not agent-native |
| **LangChain Tool Standard** | Framework-locked, not protocol |
| **Custom JSON-RPC** | Lacks ecosystem momentum |

### Integration Points

**MCP → x402 Bridge:**
```python
# MCP tool returns 402 if payment required
@server.call_tool("verify_claim")
async def verify_claim(claim: str):
    if not payment_verified():
        return PaymentRequired(
            amount="0.002",
            currency="USDC",
            network="base"
        )
    # ... verification logic
```

**x402 → Credential Atlas Bridge:**
```python
# Payment history builds trust score
class WorkerCredential:
    payment_history: List[PaymentRecord]  # From x402
    trust_score: float                     # Calculated from history
    # Issued as W3C VC 2.0 credential
```

### Resources

- **MCP Docs**: https://modelcontextprotocol.io/
- **x402 Docs**: https://docs.cdp.coinbase.com/x402/
- **W3C VC 2.0**: https://www.w3.org/TR/vc-data-model-2.0/
- **Deep Dives**: `docs/research/deep_dives/01_MCP_Model_Context_Protocol.md`, `docs/research/deep_dives/02_x402_Agentic_Payments.md`