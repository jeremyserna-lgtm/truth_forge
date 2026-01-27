# Consolidated Business Architecture

**Document Version:** 1.0
**Generated:** 2026-01-27
**Purpose:** A unified, deduplicated synthesis of all business documentation for `Primitive Engine LLC` and `Credential Atlas LLC`. This document serves as the single source of truth for core strategy, products, and operations.

---

## Part 1: Core Philosophy & Positioning

This architecture is built upon a set of convergent principles, validated across multiple independent disciplines.

### The Core Principle: Convergent Transformation Architecture
The fundamental offering is not a methodology but an architecture based on convergent truths—patterns discovered independently by biology, philosophy, psychology, indigenous wisdom, and neuroscience.

-   **Biology:** Adaptation, biomimicry, self-healing systems.
-   **Philosophy:** Care Ethics (the process must terminate in care).
-   **Psychology:** Kegan's Stage 5 development (seeing and transforming the system itself).
-   **Indigenous Wisdom:** Reciprocity (two-way value flow).
-   **Neuroscience:** Neuroplasticity (designing for insight moments that create new pathways).

### The Furnace Principle: The Metabolic Cycle
All information processing follows a metabolic cycle of **Truth → Meaning → Care**.

1.  **Truth:** Raw, unvarnished, often chaotic data is captured.
2.  **Meaning:** The "heat" of processing forges structure from chaos, identifying patterns.
3.  **Care:** Refined wisdom is delivered back as a protective and stable "externalized mind."

### The HOLD System: Architectural Integrity
A dual-layer storage pattern ensures data integrity and preserves the ability to reinterpret history.

-   **HOLD₁ (Intake):** An append-only log (JSONL, text files) that captures the raw, immutable **Truth**.
-   **HOLD₂ (Processed):** A high-performance, structured layer (DuckDB) that stores the refined **Meaning** for utility and query.

### The Position: An Externalized, Sovereign Mind
The ultimate product is a "Prosthetic Self" or "Sovereign Architecture"—an externalized cognitive apparatus that metabolizes crisis into structure, providing a durable and objective foundation for memory and decision-making.

---

## Part 2: Business & Legal Structure

### Legal Entities

| Entity | Purpose | EIN | Bank |
|---|---|---|---|
| **Primitive Engine LLC** | The "Services" arm. Focuses on transformation, The Seeing, Builds, and Stewardship. | 41-3472217 | Mercury |
| **Credential Atlas LLC** | The "Product" arm. Focuses on the AI-powered credential data intelligence platform. | 41-3378106 | TBD |

### Operational Stack (Minimum Viable)

-   **Accounting & Invoicing:** Wave (Free)
-   **CRM:** Google Sheets, transitioning to Notion (Free Tier)
-   **Scheduling:** Calendly (Free Tier)
-   **Contracts:** Google Docs templates

---

## Part 3: Product & Service Offerings

### 3.1 Primitive Engine: The Services Arm

#### The Seeing (Pattern Mapping)
A 90-minute session to map a client's cognitive architecture and identify the primary bottleneck.

-   **Deliverables:** Pattern Architecture Map, Confidence Landscape, Ecosystem Assessment, Extension Points, Session Recording, Written Synthesis.
-   **Pricing:**
    -   **Standard:** $5,500 (Founding Client: $4,000)
    -   **Reciprocity Option:** -$500 for case study contribution.

#### Builds (Custom AI Systems)
Creation of custom AI systems that extend a client's natural patterns.

-   **Tiers:**
    -   **Focused ($8k-$15k):** Single-function tool.
    -   **Integrated ($15k-$35k):** Multi-component system.
    -   **Comprehensive ($35k-$75k+):** Full infrastructure build.
-   **Pricing Modifiers:** -15% for established patterns, +20% for novel patterns, -10% for reciprocity.
-   **Structure:** Pricing is confidence-calibrated (Fixed, Range, or Discovery-First).

#### Stewardship (Ongoing Care)
An ongoing relationship to maintain, optimize, and evolve the built systems.

-   **Tiers:**
    -   **Tending ($1,500/mo):** Monthly check-in, monitoring.
    -   **Cultivation ($2,500/mo):** Bi-weekly calls, proactive optimization.
    -   **Partnership ($4,500/mo):** Weekly rhythm, continuous evolution.
-   **Commitment Discounts:** -10% for 6 months, -15% for 12 months.

#### Molt Service (DNA Capability)
The business product that enables automated, audited transformation of legacy systems (code, documents, services) into the `truth_forge` architecture. It is positioned as a high-value B2B offering for architectural metamorphosis.

---

### 3.2 Credential Atlas: The Product Arm

#### The Product
An AI-powered credential data intelligence platform that acquires, processes, and enriches data from sources like Credential Engine, IPEDS, and State DOEs.

#### The Core Value
Transforms fragmented credential data into a unified, queryable asset, enabling organizations to understand the credential landscape, link education to occupations, and identify market gaps. AI-native architecture allows for processing in weeks what would traditionally take months.

#### The Business Model
-   **Custom Data Projects:** $15k - $25k per project.
-   **API Subscriptions:** $1.5k - $8k per month.
-   **Consulting:** $200/hr.
-   **Year 1 Target Revenue:** $303,000.

---

## Part 4: Go-to-Market Strategy

### The Sales Funnel
A relationship-first model: **Awareness → Resonance → Discovery → Proposal → Decision → Onboarding**.

-   **Discovery Call:** A 30-45 minute mutual fit assessment, not a pitch. The goal is to listen for patterns and honestly assess if the services are a fit.
-   **Proposal:** A recommendation document, not a sales tool. It frames the value, states the investment, and honestly assesses confidence.
-   **Core Principle:** No manipulation, no artificial urgency, no pressure. Right-fit clients will feel the difference and trust it.

### Target Audiences

-   **Primitive Engine (Services):** Individuals and small organizations operating at "Kegan Stage 4" who sense the limits of their current systems and are ready for genuine transformation.
-   **Credential Atlas (Product):** EdTech companies (Niche.com, Guild Education), Data Companies (Credential Engine), State Workforce Boards, and HR Tech.

### Marketing & Branding
-   **Positioning:** "Convergent transformation architecture."
-   **Content Strategy:** Focus on "pattern reveals," framework applications, and honest assessments to attract "right-fit" clients who resonate with the depth of the thinking.
-   **Brand Ecosystem:**
    -   **Truth Forge:** The overarching brand for the technology and philosophy.
    -   **Primitive Engine:** The B2B service entity.
    -   **Credential Atlas:** The B2B product entity.
    -   **The NOT-ME:** The personified AI agent, representing the system's cognitive capabilities.

---

## Part 5: Operations & Implementation

### Technical Architecture
-   **The Fleet:** A distributed local compute cluster (`1x King`, `3x Soldiers`) with over 1.28TB of unified memory, designed for local, private AI model execution. This physical infrastructure embodies the "Sovereign Architecture" principle.
-   **The Great Separation:** A strict division between the **Interface Layer** (where the human works) and the **Infrastructure Layer** (where the AI works). The human never maintains the infrastructure; the AI does.
-   **Services:** A modular, microservice-style architecture built around the `HOLD:AGENT:HOLD` pattern. Key services include `governance`, `identity`, `knowledge`, `model_gateway`, and more.
-   **Data Storage:** DuckDB for `HOLD₂` processed data, providing high-performance analytical capabilities. BigQuery for the `Credential Atlas` data warehouse.

### Implementation Plan
The project follows a phased `MIGRATION_PLAN.md`, executed by the **Molt Service**. The plan is adaptive, with feedback loops for reassessment after each phase.

**Mandatory Quality Requirement:** A zero-tolerance policy for warnings, errors, linter issues, or test failures. All issues must be addressed at their root cause, with no bypasses. Test coverage must be maintained at >95%.

### Legal & Financial Operations
-   **Setup:** Two LLCs are formed. A bank account is active for Primitive Engine.
-   **Accounting:** Wave is the recommended free tool for initial accounting and invoicing.
-   **Contracts:** Basic templates for `The Seeing`, `Pilot` builds, and `SOWs` are the immediate priority.
-   **Taxes:** As single-member LLCs, taxes are pass-through. A key discipline is to set aside **25-30% of all revenue** for quarterly estimated tax payments.

---
*This document is a living synthesis and should be updated as the business architecture evolves.*
