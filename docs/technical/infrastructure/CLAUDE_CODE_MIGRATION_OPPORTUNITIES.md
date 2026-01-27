# Claude Code Migration Opportunities

**Discovery Date**: 2025-01-01
**Potential Impact**: Significant cost savings + unified LLM interface
**Files Identified**: 461 files using LLM APIs

---

## The Opportunity

Every script that calls Gemini, Vertex AI, or any LLM API can potentially use `claude -p` instead:
- **Cost**: FREE (included in Claude Code subscription)
- **Setup**: None (already installed)
- **Quality**: Same Claude model you're chatting with

---

## High-Priority Migration Targets

### 1. Knowledge Atom Extraction (HIGHEST IMPACT)

**Current**: Gemini Flash/Pro → costs money per document
**Files**:
- `scripts/knowledge/process_documents_to_atoms.py`
- `scripts/knowledge/extract_knowledge_atoms_batch.py`
- `scripts/knowledge/document_knowledge_extraction.py`
- `architect_central_services/scripts/extract_knowledge_atoms_from_documents.py`
- `architect_central_services/scripts/extract_email_knowledge_atoms.py`

**Volume**: Thousands of documents
**Estimated Current Cost**: $10-50/month
**After Migration**: $0

### 2. Content Categorization/Classification

**Current**: Gemini Flash → costs per classification
**Files**:
- `architect_central_services/scripts/clean_and_relabel_sources.py`
- `architect_central_services/scripts/synthesize_domain_categories.py`
- `architect_central_services/scripts/detect_persona_signals.py`
- `tools/document-organizer/scripts/intelligent_document_organizer.py`

**After Migration**: $0

### 3. Document Analysis & Enrichment

**Current**: Gemini Flash/Pro
**Files**:
- `architect_central_services/scripts/deep_work_content_analysis.py`
- `architect_central_services/scripts/comprehensive_job_prep_analysis.py`
- `architect_central_services/scripts/analyze_email_history_llm.py`
- `architect_central_services/scripts/analyze_search_history_llm.py`
- `architect_central_services/scripts/enrich_browser_history_with_flash_lite.py`

**After Migration**: $0

### 4. Pipeline Stage Processing

**Current**: Gemini for L4-L8 processing
**Files**:
- `architect_central_services/pipelines/chatgpt/scripts/stage_4/*.py`
- `architect_central_services/pipelines/chatgpt/scripts/stage_9/*.py`
- `architect_central_services/pipelines/text_messages/scripts/stage_4/*.py`

**After Migration**: $0

### 5. Validation & Quality Checks

**Current**: Flash for validation
**Files**:
- `architect_central_services/scripts/validate_gemini_with_flash.py`
- `architect_central_services/scripts/validate_staging_to_production.py`
- `architect_central_services/scripts/detect_and_validate_l7_l8_with_flash.py`

**After Migration**: $0

### 6. Narrative/Furnace Engine

**Current**: Gemini for narrative generation
**Files**:
- `architect_central_services/src/architect_central_services/narrative_core/furnace_engine.py`
- `architect_central_services/src/architect_central_services/narrative_core/narrative_service.py`

**After Migration**: $0

---

## Medium-Priority Targets

### 7. Governance & Review

- `architect_central_services/src/.../governance/governance_service/flash_ddl_reviewer.py`
- `architect_central_services/src/.../governance/governance_service/ide_development_reviewer.py`
- `architect_central_services/src/.../governance/seeing/perspectives.py`

### 8. Developer Insights

- `architect_central_services/src/.../developer_insights_system/academic_insights_generator.py`
- `architect_central_services/src/.../developer_insights_system/browser_history_content_analyzer.py`
- `architect_central_services/src/.../developer_insights_system/browser_history_insights.py`

### 9. Tool-Specific Analysis

- `tools/zoom-watcher/scripts/ai_behavioral_synthesis.py`
- `tools/sniffies-chat-extractor/scripts/analysis/tiered_ai_analysis.py`
- `tools/iphone-extractor/scripts/ai_review_unnamed_contacts.py`

---

## NOT Suitable for Migration

### Embeddings (Keep Vertex AI)
- `architect_central_services/src/.../embedding_service/service.py`
- `scripts/knowledge/generate_knowledge_atom_embeddings.py`

**Why**: Claude Code doesn't generate embeddings. Keep using Vertex AI embedding models.

### Cloud Run Jobs (No Claude Code available)
- `deployments/cloud_run_jobs/*`
- `architect_central_services/deployments/*`

**Why**: Claude Code is a local CLI tool. Server-side needs API.

### High-Volume Production Pipelines
- Anything with >1000 items/hour throughput

**Why**: Claude Code is single-threaded. Use API for parallel processing.

---

## Migration Pattern

### Before (Gemini):
```python
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

response = model.generate_content(prompt)
result = response.text
```

### After (Claude Code):
```python
from architect_central_services.core.shared.claude_code_client import (
    ask_claude,
    ask_claude_json,
)

# Simple text response
result = ask_claude(prompt)

# JSON response
result = ask_claude_json(prompt, schema={"type": "object", ...})
```

---

## Hybrid Pattern (Local + Cloud)

```python
from architect_central_services.core.shared.claude_code_client import (
    get_llm_client,
    ClaudeCodeNotAvailable,
)
from architect_central_services.core.shared.gemini_client import get_gemini_client

def get_llm_response(prompt: str) -> str:
    """Use Claude Code locally, fall back to Gemini in cloud."""
    client = get_llm_client()

    if client:
        # Running locally - FREE
        return client["ask"](prompt)
    else:
        # Running in cloud - PAID
        gemini = get_gemini_client()
        return gemini.generate_content(prompt).text
```

---

## New Use Cases (Previously Too Expensive)

With free LLM calls, you can now:

### 1. Real-Time Quality Checks
- Check every file write for quality
- Validate every commit message
- Review every PR automatically

### 2. Continuous Document Enrichment
- Extract entities from every new document
- Categorize every file as it's created
- Summarize every long document automatically

### 3. Enhanced Governance
- AI review of every code change
- Automatic security scanning
- Compliance checking on all files

### 4. Personal Analytics
- Daily work pattern analysis
- Communication style feedback
- Learning progress tracking

### 5. Proactive Assistance
- Anticipate what you need
- Suggest improvements continuously
- Flag issues before they become problems

---

## Implementation Priority

### Phase 1: Document Processing (Immediate)
1. `extract_knowledge_atoms_from_documents.py`
2. `document_knowledge_extraction.py`
3. `analyze_email_history_llm.py`

### Phase 2: Pipeline Stages (Week 1)
1. Stage 4 processors
2. Stage 9 processors
3. Validation scripts

### Phase 3: Governance & Quality (Week 2)
1. DDL reviewer
2. IDE reviewer
3. Perspectives

### Phase 4: Everything Else (Ongoing)
- Tool-specific analysis
- Insights generators
- Ad-hoc scripts

---

## Tracking Migration

| Category | Files | Migrated | Remaining |
|----------|-------|----------|-----------|
| Knowledge Atoms | 12 | 0 | 12 |
| Categorization | 8 | 0 | 8 |
| Document Analysis | 15 | 0 | 15 |
| Pipeline Stages | 10 | 0 | 10 |
| Validation | 6 | 0 | 6 |
| Narrative | 2 | 0 | 2 |
| **Total** | **53** | **0** | **53** |

---

## The Bottom Line

**461 files** reference LLM APIs.
**53 high-priority** files can be migrated to Claude Code.
**Estimated savings**: $50-200/month in API costs.
**New capability**: Unlimited LLM processing for local workflows.

**Action**: Start with knowledge atom extraction - highest volume, clearest path.
