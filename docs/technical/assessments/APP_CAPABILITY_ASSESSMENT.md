# Application Capability Assessment & Roadmap

**Date**: January 29, 2026
**Status**: ANALYSIS_COMPLETE
**Objective**: Assessment of the current application portfolio (`/truth_forge/apps`) against the Federation Business Plans.

---

## 1. Current Application Portfolio

We have analyzed the existing artifacts in `truth_forge/apps`.

### 1.1 The Document Service (`/apps/document-service`)
*   **Role**: The Librarian.
*   **Tech**: Node.js/Express, Google Cloud (BigQuery, Storage, Vision), Tesseract OCR.
*   **Capability**: Ingests static files (PDFs, Images), extracts text, and stores them.
*   **Status**: **Operational**. It serves the "Knowledge Atomization" need for *documents*.

### 1.2 The Chat Interface (`/apps/not_me_chat`)
*   **Role**: The Mouth/Ears.
*   **Tech**: Python/FastAPI (Backend) + Next.js (Frontend).
*   **Capability**: Real-time websocket communication between User and AI. Checks "Cost Governance".
*   **Status**: **Operational**. It serves the "Relationship" need.

### 1.3 The Nexus User Portal (`/apps/nexus-user-portal-extracted`)
*   **Role**: The Mirror.
*   **Tech**: React/Vite.
*   **Capability**: Visualizes the user's developmental state (Kegan Stages).
*   **Status**: **Prototype/MVP**. Built by Claude Code (Orchestration POC).

### 1.4 The Knowledge Atomizer (`/apps/knowledge-atomizer`)
*   **Role**: The Dissolver.
*   **Tech**: React/Vite + Google GenAI.
*   **Capability**: Frontend-focused tool for breaking concepts down.
*   **Status**: **Lightweight/Client-Side**. Not a robust backend pipeline.

---

## 2. The Critical Gap: Conversation Data Pipeline

**The Problem**:
*   We have a way to *chat* (`not_me_chat`).
*   We have a way to *process PDFs* (`document-service`).
*   **We DO NOT have a way to process the Chat Logs themselves into Wisdom.**

**The Missing Link**:
The "Universal 16-Stage Pipeline" for conversation data is currently missing as a standalone application.
*   *Current State*: Chat logs likely sit in a database or raw text files. Useable for replay, but not for "Stage 5 Identity Construction."
*   *Requirement*: A "Refinery" that takes raw conversation logs, applies the 16-stage enrichment (Entity extraction, Sentiment analysis, Narrative arc detection), and deposits them into `spine.entity_unified`.

---

## 3. The Orchestration Build Recommendation

**We need to build:** `apps/conversation-refinery`

### The Specification (For the Builder AI)
1.  **Name**: Conversation Refinery
2.  **Architecture**: Python (for heavy NLP/spaCy) or Node.js (for consistency with Document Service). *Recommendation: Python (Primitive Engine standard).*
3.  **Input**: Raw Chat Logs (from `not_me_chat` storage).
4.  **Process**:
    *   **Stage 1-5**: Extraction (Entities, Dates, Claims).
    *   **Stage 6-10**: Analysis (Sentiment, Dialectical Tension).
    *   **Stage 11-16**: Synthesis (Meaning Maps, Knowledge Atoms).
5.  **Output**: Structured JSON -> BigQuery (`spine.conversation_atoms`).

### The Plan of Action
1.  **Orchestrator (You)**: Define the "Refinery" spec.
2.  **Builder (VS Code + AI)**: Scaffold the Python application.
3.  **Seer (You)**: Verify that raw text enters and "Wisdom" exits.
