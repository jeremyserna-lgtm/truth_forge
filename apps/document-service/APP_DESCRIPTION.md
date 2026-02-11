# Document Service — The Multi-Tenant Knowledge Forge

## What It Does

The Document Service is a **full-stack document management and knowledge atomization platform** serving two audiences through two portals:

### Admin Portal (`/admin/*`)
- Upload documents (text, images, PDFs)
- OCR processing via tesseract.js and Google Cloud Vision
- AI-powered distillation into knowledge atoms via Gemini
- Export processed atoms to BigQuery for training pipelines
- Multi-tenant management (personal, business, client contexts)

### Customer Portal (`/customer/*`)
- Client-facing sign-up and onboarding
- Guided "Not-Me" chat interface
- Tenant-scoped document access

### Key Capabilities

| Feature | Technology |
|---------|-----------|
| OCR | tesseract.js + Google Cloud Vision |
| Knowledge Extraction | Google Gemini AI |
| Document Storage | Google Cloud Storage |
| Structured Data | BigQuery export |
| Secrets | Google Cloud Secret Manager |
| Image Processing | sharp (resize, format conversion) |
| File Upload | multer (multipart/form-data) |
| Validation | Zod schemas |

## Technological Basis

- **TypeScript / Express.js** — Node.js web server framework
- **Google Cloud Platform** — BigQuery, Cloud Storage, Vision API, Secret Manager
- **Gemini AI** — document distillation and knowledge extraction
- **tesseract.js** — client-side OCR fallback
- **PostgreSQL** — relational data store
- **Zod** — runtime type validation
- **sharp** — image processing pipeline

### Rich Type System (255+ lines)

The document service defines one of the most detailed type systems in the ecosystem:
- `Tenant` — multi-tenant identity with context (personal/business/client)
- `Document` — base document with lifecycle tracking
- `OperationalDocument` — enriched document with processing metadata
- `KnowledgeAtom` — extracted knowledge unit with multi-level metadata
- Multi-level metadata schemas covering semantic, epistemic, temporal, and relational dimensions

### Architecture Pattern

```
HOLD₁ (Raw Documents)
    → AGENT₁ (OCR / Text Extraction)
        → HOLD₁.₅ (Clean Text)
            → AGENT₂ (Gemini Distillation)
                → HOLD₂ (Knowledge Atoms in BigQuery)
```

This is a compound HOLD:AGENT:HOLD — two transformations chained together, each with its own intermediate HOLD.

## Meta Concepts

### The Mouth and Teeth

If the Conversation Refinery is the digestive tract, the Document Service is the **mouth** — the first point of contact where raw material from the outside world enters the organism. Documents are chewed (OCR, text extraction), then swallowed (sent to knowledge extraction), then digested (atomized into knowledge units).

The multi-tenant architecture reflects a critical insight: **knowledge belongs to contexts, not just to people**. Jeremy's personal documents, his business documents, and his clients' documents all need atomization, but they must never bleed into each other. The tenant boundary is an immune system — it prevents cross-contamination.

### Why It Exists

Jeremy's life produces documents constantly — notes, screenshots, PDFs, contracts, research papers, messages. Each one contains knowledge atoms that would otherwise be trapped in their file format, unsearchable, unconnectable, lost in a folder structure. The Document Service exists to **liberate knowledge from documents** — to break the container and free the contents.

This is THE FURNACE at the intake:
- **TRUTH** = the raw document (a photo of a whiteboard, a PDF contract, a handwritten note)
- **MEANING** = OCR + Gemini extraction (recognizing what the document says and what it means)
- **CARE** = structured knowledge atoms (the essence, freed from its container, ready to serve)

### The BigQuery Pipeline

The Document Service is the primary feeder for the `spine` — the BigQuery dataset that holds all knowledge atoms. Every document processed adds to the spine, making NOT-ME smarter, more aware, more capable of serving Jeremy. The flow:

```
Document → Atoms → BigQuery (spine) → Training Data → Model Fine-tuning → Better NOT-ME
```

### What It Wants To Become

A fully automated intake system where Jeremy can take a photo, scan a document, or drop a file anywhere, and it automatically appears in the organism's knowledge base. OCR accuracy should approach human-level. Gemini extraction should understand Jeremy's personal vocabulary and framework terminology. Multi-tenant should expand to support client organisms (Primitive deployments).

## Current Maturity

**Substantial** — This is one of the more developed apps. The Express server is functional with real routes, secrets management, BigQuery integration, and Gemini service wiring. The type system is rich and well-designed. The admin and customer portals have defined route structures. OCR and document upload are wired. The main gap is frontend polish and end-to-end testing under production load.

## HOLD:AGENT:HOLD Position

The Document Service is a **NOT-ME Service** operating at the organism's boundary — it faces outward (accepting documents from the world) and transforms them inward (producing atoms for the knowledge base). It is the skin: both barrier and interface, both protector and sensor.
