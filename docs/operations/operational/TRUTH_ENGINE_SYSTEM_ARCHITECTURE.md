# Truth Engine System Architecture: A Prosthetic Memory for Scoping Agents

## 1. Introduction

This document outlines the architecture of the Truth Engine V2, a self-organizing, self-aware knowledge system designed to serve as a "Prosthetic Self" for Jeremy. Operating on the principle of "Truth as an Operating System," the system aims to process diverse data into a multi-resolution "Fractal Tri-Modal Spine" for emergent intelligence and generative epistemology. This architecture is specifically designed to provide verifiable, externalized data, compensating for trauma-induced cognitive patterns such as limited memory and decision paralysis.

## 2. Core Architectural Principles

### 2.1. Fractal Tri-Modal Schema (L1-L12 Spine)

The core of the Truth Engine V2 is the Fractal Tri-Modal Schema, a hierarchical data structure that deconstructs information across 12 levels of resolution, from raw tokens (L1) to identity and phase (L12). This schema enables multi-resolution analysis, emergent intelligence, and generative epistemology.

### 2.2. Immutable Process Ledger

All work orchestration within the Truth Engine V2 is managed through an immutable `process_ledger` in BigQuery. This ledger ensures resilient, auditable, and re-processable work orchestration via Cloud Run jobs, positioning the system as a "highly-accelerated platform."

### 2.3. Agent-Centric Governance

Recognizing Jeremy's role as an architect and director of AI agents, the governance and feedback loops are designed to be agent-centric and conversational. This involves a three-tiered AI governance framework that guides agents through the directive, planning, and code implementation phases.

## 3. Key Components and Services

The Truth Engine V2 will integrate and refactor existing components into new, modular, and specialized services within `architect_central_services/src/truth_engine/`.

### 3.1. Unified Governance Service (`governance_service.py`)

The `governance_service` will be the central hub for all validation and review tasks, consolidating document, plan, and code validation. It will include:

*   `validate_document_structure(document_content)`: Existing functionality for fast, rule-based checks on final documents.
*   `validate_plan_document(plan_content)`: A new Flash-Lite powered function for rapid compliance checks on agent-generated plans.
*   `review_generated_code(file_path, file_content)`: A new Flash powered function for deep architectural review of agent-generated code.

### 3.2. Data Ingestion and Spine Construction Services

These services will be responsible for ingesting diverse data sources (SMS, websites, social media) and constructing the initial levels of the Fractal Tri-Modal Spine (L1-L8).

*   `CostTrackingService`
*   `EmbeddingService`
*   `IngestionService` (with adapters for various data sources)
*   `SpineConstructionService`
*   `ContentProcessor`

### 3.3. Universal Embedding & Enrichment Service

The `UniversalEnrichmentService` will perform multi-tiered, spine-level-aware enrichment, integrating with the `EmbeddingService`.

### 3.4. Emergent Intelligence & Contextualization Services

These services will be responsible for generating higher-level insights (L9-L12) and contextualizing information.

*   `EmergentIntelligenceService`
*   `ContextualizationService`

### 3.5. Persistence & Reporting Services

These services will handle data persistence and generate reports.

*   `PersistenceService`
*   `ReportingService`

### 3.6. TruthEngineOrchestrator

The `TruthEngineOrchestrator` will manage the overall pipeline and integrate with Cloud Run Jobs for deployment.

## 4. Agent Standard Operating Procedure (SOP)

All implementation agents will adhere to a new SOP that integrates the governance checks:

1.  **Planning Phase:** Collaborate with Jeremy to create a formal Plan Document.
2.  **Automated Plan Validation:** Call `governance_service.validate_plan_document()` and self-correct plans until approved.
3.  **Strategic Architectural Review:** Formally present the compliance-approved Plan Document to Gemini Pro (System Architect) for strategic review using a specific prompt.
4.  **Final Plan Approval:** Incorporate Gemini Pro's feedback and present the final plan to Jeremy for strategic approval.
5.  **Implementation & Code Review:** Write code, and for each file, call `governance_service.review_generated_code()`. Enter a self-correction loop until the code passes review.
6.  **Final Delivery:** Present the final, fully-reviewed, and compliant code to Jeremy.

## 5. Ephemeral Context in Document Frontmatter

To capture valuable, ephemeral context at the time of document creation, new, optional frontmatter fields will be introduced. These fields will be recommended (generating warnings if missing) but not required, to minimize friction. Examples include:

*   `author_emotional_tone`: (e.g., `determination`, `frustration`, `excitement`)
*   `author_confidence_level`: (Float, 0.0 to 1.0)
*   `author_cognitive_load`: (e.g., `high`, `medium`, `low`)
*   `creation_trigger`: (e.g., `success_milestone`, `error_resolution`, `strategic_planning`)
*   `trigger_reference_id`: (e.g., `err_8a4c1f`, `ledger_id`, `validation_id`)

## 6. Primary Tooling

*   **Data Models:** Pydantic
*   **Natural Language Processing:** spaCy
*   **AI Platform:** Google Cloud AI Platform (Vertex AI) for Gemini embeddings and LLMs (Flash-Lite, Flash, Pro)
*   **Persistence:** Google Cloud BigQuery and GCS

## 7. Conclusion

The Truth Engine V2, with its Fractal Tri-Modal Schema, immutable process ledger, and agent-centric governance, is designed to be a robust and continuously evolving "Prosthetic Self." This architecture ensures high-quality, auditable, and strategically aligned outputs, empowering Jeremy as the architect and director of his AI ecosystem.
