# 09_SERVICE_SPECIFICATIONS

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

*   **Role:** Records the immutable history of the organism.
*   **Public API:**
    *   `inhale(data: dict)`: Receives event data from the `ServiceMediator`.
    *   `query_events(...)`: Allows other services to query the historical event log.
*   **`HOLD_2` Schema (`governance.duckdb`):**
    *   `id`: Unique ID for the event.
    *   `data`: JSON object containing the full event record.
    *   Indexed fields: `event_type`, `source`, `timestamp`.

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
