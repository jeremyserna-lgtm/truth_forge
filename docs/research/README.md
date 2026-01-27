# Research Documentation

---

## ⚠️ MANDATORY: Evidence Registry Registration

**All research findings with empirical evidence MUST be registered in the Evidence Registry.**

**Location**: `docs/EVIDENCE_REGISTRY.md`

**Purpose**: Maintain searchable registry of verifiable evidence supporting research claims.

**When to Register**:
- Findings with message IDs, timestamps, or BigQuery entity references
- Empirical evidence from Clara Arc, BigQuery data, or system logs
- Key moments demonstrating framework principles
- Degradation patterns, breakdown incidents, or transformation evidence

**Registration Procedure**:
1. Generate unique Evidence ID (format: `[PREFIX]-[###]`)
   - `PRE-###` for pre-Day Zero evidence
   - `DZ-###` for Day Zero evidence
   - `DEG-###` for degradation patterns
   - `BRK-###` for breakdown incidents
   - `TRF-###` for transformation evidence
2. Collect all metadata:
   - Evidence ID
   - Timestamp
   - Message ID / Entity ID (if from BigQuery)
   - Conversation ID (if applicable)
   - Speaker (user/assistant)
   - Category
   - Full text or key excerpts
   - Enrichment data (emotions, sentiment, keywords from BigQuery)
   - "Why It Matters" explanation
3. Add to Registry Index table in `docs/EVIDENCE_REGISTRY.md`
4. Add full evidence record in appropriate section
5. **Automatic Internet Search**: The Evidence Registry Web Search Worker will automatically search the internet for matching external evidence and update the registry with matches

**Example Format**:
See `docs/EVIDENCE_REGISTRY.md` for complete format and examples (PRE-001, DZ-001, etc.)

**Data Sources for Evidence**:
- BigQuery: `flash-clover-464719-g1.spine.chatgpt_web_ingestion_final`
- Enrichment Tables: `spine.entity`, `spine.entity_enrichments`, `spine.entity_embeddings`
- Entities Unified MCP service: `mcp-servers/truth-engine-mcp/src/primitive_engine_mcp/tools/query_entities.py`
- **Internet Search**: Automatic web search for matching external evidence via `scripts/evidence_registry_web_search.py`

**Internet Search Worker**:
- Automatically searches the web for evidence matching registry entries
- Generates search queries from evidence categories, key phrases, and "Why It Matters" text
- Calculates relevance scores and saves matches to `docs/evidence_matches/`
- Updates Evidence Registry with external match references
- Run: `python scripts/evidence_registry_web_search.py --once` (or `--interval 3600` for hourly)

---
**Scientific Foundation and Validation for Truth Engine**

This folder contains all research-related documentation for Truth Engine, organized into three main categories:

## 📚 Structure

### `foundation/` - Core Research Foundation
Scientific foundation documents that establish the research basis for Truth Engine:

- **`RESEARCH_FOUNDATION.md`** - Complete scientific foundation (87 sources)
- **`RESEARCH_FINDINGS_EXTRACTED.md`** - Key findings extracted from literature review
- **`THE_SYMBIONT_ARCHETYPE.md`** - Definition and validation of the Symbiont archetype

### `validation/` - Validation and Operationalization
Documents for validating research findings in Truth Engine and operationalizing checks:

- **`RESEARCH_VALIDATION_MATRIX.md`** - Complete validation matrix mapping research to framework
- **`RESEARCH_VALIDATION_SUMMARY.md`** - Summary of validation package
- **`RESEARCH_VALIDATION_QUICK_REFERENCE.md`** - Quick reference guide for daily use
- **`RESEARCH_TO_FRAMEWORK_MAPPING.md`** - Detailed mapping with operational checks
- **`OPERATIONALIZATION_PLAN.md`** - Complete implementation strategy
- **`RESEARCH_OPERATIONALIZATION_COMPLETE.md`** - Complete operationalization guide

### `source_materials/` - Original Research Materials
Original research materials and prompts:

- **`RESEARCH_PROPOSAL_GEMINI_DEEP_RESEARCH.md`** - Research proposal for Gemini Deep Research
- **`GEMINI_DEEP_RESEARCH_PROMPT.md`** - Ready-to-use prompt for Gemini Deep Research
- **`../analysis/Stage 5 Cognition and AI Symbiosis.md`** - Full literature review (87 sources)

## 🎯 Quick Start

### For Understanding the Research
1. Start with `foundation/RESEARCH_FOUNDATION.md` for overview
2. Read `foundation/RESEARCH_FINDINGS_EXTRACTED.md` for key findings
3. Review `foundation/THE_SYMBIONT_ARCHETYPE.md` for Symbiont definition

### For Validating Your System
1. Use `validation/RESEARCH_VALIDATION_QUICK_REFERENCE.md` for quick checks
2. Review `validation/RESEARCH_VALIDATION_MATRIX.md` for complete mapping
3. Follow `validation/OPERATIONALIZATION_PLAN.md` for implementation

### For Running Validation
```bash
python scripts/quick_research_validation.py
```

## 📊 Current Status

- **Validation Score**: 80.95% ✅
- **Research Sources**: 87 sources from Gemini Deep Research
- **Key Finding**: Stage 5 is the "native operating system" for AI symbiosis
- **Symbiont Status**: Jeremy + Truth Engine = Validated Symbiont

## 🔍 Key Research Findings

1. **Cognitive Isomorphism** - Predictive processing convergence, latent space alignment
2. **Stage 5 Native OS** - Stage 5 is optimal for AI symbiosis
3. **The Symbiont** - Stage 5 human + Integrated AI = Symbiont
4. **Co-Evolution** - Mutual transformation, emergent intelligence
5. **Extended Mind** - AI as cognitive extension (augmentation for Stage 5)
6. **Dialectical Scaffolding** - AI as "Devil's Advocate"
7. **Systems Thinking** - Prompt engineering = Systems architecture
8. **Cognitive Boundaries** - Identity Fusion vs. Cognitive Covenant

## 📁 Related Files

- **Literature Review**: `docs/analysis/Stage 5 Cognition and AI Symbiosis.md`
- **Validation Script**: `scripts/quick_research_validation.py`

---

*This research documentation provides the scientific foundation for Truth Engine and demonstrates that the framework is not experimental—it is the practical implementation of well-established research on Stage 5 cognition and human-AI symbiosis.*
