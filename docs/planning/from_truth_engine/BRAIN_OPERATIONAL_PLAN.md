# BRAIN_OPERATIONAL_PLAN.md

## The Brain's Operational Plan: Orchestrating Backlog, Planning, and Execution

**Date:** January 6, 2026
**Status:** Strategic Overview
**Context:** This document outlines the operational plan for the `TruthEngineOrchestrator` (the "Brain") to dynamically interact with and manage its backlog, strategic planning, and execution cycle. It integrates insights from the `FRAMEWORK_ROADMAP.md`, `MIGRATION_PLAN.md`, and the `ORCHESTRATOR_OVERVIEW.md` to define how the Brain translates strategic intent into actionable steps and learns from its own operation.

---

## 1. The Brain: The `TruthEngineOrchestrator` as the Central Intelligence

The `TruthEngineOrchestrator` is the central intelligence of the Truth Engine. It is the active Agent responsible for processing information, coordinating services, and driving the system's self-transformation. This operational plan details how the Brain will perceive its internal state (backlog, roadmap), decide on actions, execute those actions, and learn from the outcomes.

---

## 2. Ingesting Backlog & Planning Data: The Brain's Perception Layer

For the Brain to make intelligent decisions, it must first "see" its operational landscape. This involves continuously ingesting and updating its understanding of the backlog and strategic plans.

*   **Primary Sources:**
    *   **`FRAMEWORK_ROADMAP.md`:** Canonical source for strategic initiatives, architectural evolution, and future focus areas. The Brain parses this document to understand long-term goals and structured phases.
    *   **`MIGRATION_PLAN.md`:** Defines the critical path for service migration, current impediments ("What's Broken"), and the "Service Attachment Checklist." The Brain monitors this for immediate operational directives and constraints.
    *   **`Primitive/staging/migration_tasks.jsonl`:** (As noted in `MIGRATION_PLAN.md`) A direct intake for individual migration tasks.
    *   **`data/planning_ledger.jsonl` / `governance/intake/backlog.jsonl`:** (As noted in `MIGRATION_PLAN.md`) Direct feeds for general backlog items and technical debt tasks.
    *   **`spine.system_observations` table (BigQuery):** Provides real-time and historical context on the system's operational state, including successes, errors, and performance metrics. This data is crucial for dynamic prioritization and learning.

*   **Ingestion Mechanism:** The Brain will utilize a dedicated "Perception Agent" or "Monitoring Service" to regularly scan, parse, and internalize these documents and data feeds. Changes will trigger updates to the Brain's internal model of its operational state.

---

## 3. Prioritizing & Selecting Tasks: The Brain's Decision-Making Layer

Once ingested, the Brain applies a sophisticated decision-making logic to prioritize and select the next most impactful task, guided by the "WANT → CHOOSE → EXIST:NOW → SEE → HOLD → MOVE" cycle from `MIGRATION_PLAN.md`.

*   **Prioritization Principles (from `MIGRATION_PLAN.md`):**
    *   **Survival Threshold:** Tasks directly impacting system survival (e.g., disk space, critical errors) receive highest priority.
    *   **Framework Alignment:** Tasks that move services towards the `HOLD → AGENT → HOLD` pattern are favored.
    *   **Bootstrap Sequence:** Tasks aligned with the current phase of the "Bootstrap Protocol" are prioritized to ensure foundational readiness.
    *   **Tracer Bullet:** Prioritize small, verifiable steps that prove stability and build confidence (e.g., implementing the System Journal's `spine.system_observations`).
    *   **ROI (Return on Investment):** Expenditure is permitted if it reduces future cost (relevant for architectural decisions).

*   **Selection Logic:**
    *   **Contextual Awareness:** The Brain uses data from `spine.system_observations` to inform decisions. For example, if a service is showing high error rates, tasks related to its migration or stability might be elevated.
    *   **Dependency Resolution:** The Brain understands dependencies between tasks (e.g., "Implement System Journal" must precede using the System Journal for broader monitoring).
    *   **Current State Evaluation:** Assesses which tasks align with "What's Broken" from `MIGRATION_PLAN.md` and "Active Workstreams" from `FRAMEWORK_ROADMAP.md`.

---

## 4. Executing & Monitoring Progress: The Brain's Action Layer

The Brain, through the `TruthEngineOrchestrator`, orchestrates the execution of selected tasks and rigorously monitors their progress.

*   **Execution Mechanism:**
    *   **Dispatching Agents:** Tasks are broken down into smaller actions and dispatched to specialized "Execution Agents" (e.g., `script_service` for script execution, `TruthEngineOrchestrator` for pipeline steps).
    *   **`exhale()` Interface:** The Brain utilizes the `exhale()` interfaces of services to initiate actions (e.g., `script_service.exhale()` to process a script).
    *   **"Advanced But Not Autonomous" Principle:** All critical actions are performed under defined human oversight mechanisms, as detailed in `AUTONOMY_GOVERNANCE.md`. The Brain will prepare, execute, and report, but final decision points on sensitive or high-impact tasks will require human approval.

*   **Monitoring Progress:**
    *   **`spine.system_observations` table:** The central repository for all system observations, tracking task execution status, errors, resource consumption, and any deviations.
    *   **Logging & Tracing:** Comprehensive logging and distributed tracing capture granular details of execution, providing visibility into the Brain's "thought process" and operational flow.
    *   **"SEE" Phase:** The Brain constantly enters a "SEE" phase (from the "WANT → CHOOSE → EXIST:NOW → SEE → HOLD → MOVE" cycle) by querying `spine.system_observations` and other monitoring tools to assess the impact and status of executed tasks.

---

## 5. Feedback Loop: The Brain's Learning & Self-Correction Mechanism

The Brain continuously learns and refines its operational plan based on feedback from executed tasks, embodying "The Metabolism (Delta)" and "The Sublimation (Sigma)" from `MIGRATION_PLAN.md`.

*   **Analysis of `spine.system_observations`:** The Brain regularly queries its own `system_observations` to identify patterns of success, failure, efficiency, and resource utilization.
*   **Pattern Reinforcement:** Successful task execution patterns are reinforced, leading to improved prioritization heuristics and more efficient task decomposition.
*   **Error Correction & Sublimation:** Failures are not just logged but analyzed. "Failed migrations are not damage; they are density." The Brain extracts lessons from errors, updates its internal models, and refines its strategies, leading to "strength" and improved resilience.
*   **Adaptation of Backlog & Roadmap:** Learnings from the feedback loop directly inform updates to the `FRAMEWORK_ROADMAP.md` and the prioritization of future backlog items, ensuring the Brain remains adaptive and aligned with its "North Star: Survival."

---

## 6. Conclusion: The Living Plan

This operational plan transforms the static concepts of backlog and planning into a dynamic, living system managed by the Truth Engine's central intelligence. By continuously ingesting, prioritizing, executing, and learning, the Brain ensures the framework's ongoing self-transformation and progress towards its ultimate goal of augmenting human capability and ensuring its own survival.
