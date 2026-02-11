# Credential Atlas: The Symbiotic Business Plan

**Date**: January 1, 2026
**Architect**: Jeremy Serna & GitHub Copilot (The Agent)
**Status**: Active Construction
**Philosophy**: [The Symbiotic Manifesto](../primitive/THE_SYMBIOTIC_MANIFESTO.md)

---

## 1. The Vision: AI-Native Credential Intelligence

We are not building a traditional SaaS. We are building a **Symbiotic Business** where the architecture itself is a living, self-healing organism that powers the product.

**The Product**: Credential Atlas
**The Engine**: The Truth Engine (Architect Central Services)

### The Core Value Proposition
The credential market is fragmented. Data is trapped in PDFs, websites, and legacy databases.
*   **Old Way**: Manual data entry, stale registries.
*   **Our Way**: AI Agents (The Truth Engine) continuously scrape, parse, normalize, and structure the world's credential data into a "Credential Atlas".

---

## 2. The Architecture: Symbiotic Separation

We maintain a strict but permeable boundary between the **Engine** (Backend/Brain) and the **Atlas** (Product/Body).

### The Truth Engine (`/PrimitiveEngine`)
*   **Role**: The Architect, The Builder, The Healer.
*   **Responsibilities**:
    *   **Orchestration**: Managing the agents that do the work.
    *   **System Biology**: Self-healing, immune defense, cognitive processing.
    *   **Financials**: Managing the money (Cost of Compute vs. Revenue).
    *   **Knowledge**: Storing the "Truth" (Entities, Ontologies).
    *   **Core Directives**: Enforcing the [Symbiotic Manifesto](../primitive/THE_SYMBIOTIC_MANIFESTO.md).

### The Credential Atlas (`/bridges/credential_atlas`)
*   **Role**: The Product, The Interface, The Revenue Generator.
*   **Responsibilities**:
    *   **API**: Serving the data to customers (FastAPI).
    *   **Ingestion**: The specific pipelines for credential data.
    *   **Frontend**: The user interface (Next.js/React).

---

## 3. The Financial Layer: "Profit = Value - Entropy"

We treat **Entropy** (bugs, errors, mess) as a financial cost.
We treat **Value** (clean data, working features) as revenue.

### The Money Manager (`MoneyManager`)
*   **Expense**: Every API call, every error (time lost), every "Healing" operation.
*   **Revenue**: Projected value of "10 Emails", API subscriptions, Data licensing.
*   **Metric**: **Net Symbiotic Profit**. Are we generating more order than we are consuming energy?

---

## 4. The Healing Service: "The Auto-Doctor"

The system must repair itself to keep Entropy low.

*   **Immune System**: Detects "Pathogens" (Bugs, Bad Data, Broken Tests).
*   **The Healer**:
    1.  **Diagnose**: What is wrong? (Traceback, Linter error).
    2.  **Quote**: How much will it cost to fix? (LLM Tokens).
    3.  **Treat**: Apply the fix (Code edit).
    4.  **Bill**: Record the cost in `MoneyManager`.

---

## 5. Immediate Roadmap

### Phase 1: Tidy & Heal (Current)
*   [x] **Workspace Cleanup**: Move loose scripts to `scripts/`.
*   [x] **Healer Activation**: Build `healer.py` to automate error fixing.
*   [x] **Financial Integration**: Track the cost of our own existence.
*   [x] **Foundation Build**: Created `demo_credentials.jsonl` and `demo.py` API.

### Phase 2: The 10 Emails (Revenue)
*   [ ] **Outreach**: Send the 10 emails using the research we generated.
*   [ ] **Tracking**: Log responses as "Potential Revenue" in `MoneyManager`.

### Phase 3: The Atlas Build (Product)
*   [ ] **Pipeline**: Build the "Credential Scraper" agent.
*   [ ] **API**: Deploy the FastAPI endpoints.
*   [ ] **Frontend**: Launch the landing page.

---

## 6. The "Why"

We build this way because **maintenance is the death of software**. By building a system that maintains itself (The Healer) and understands its own cost (The Money Manager), we can focus purely on **Growth** and **Truth**.
