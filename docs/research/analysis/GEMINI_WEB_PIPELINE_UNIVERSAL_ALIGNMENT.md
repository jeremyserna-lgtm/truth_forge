# Gemini Web Pipeline - Universal Pipeline Alignment Analysis

**Date:** January 6, 2025
**Purpose:** Analyze Gemini Web pipeline status and alignment with Universal Pipeline Pattern

---

## Executive Summary

**Current Status:** ⚠️ **Stage 0 Complete, No Implementation Yet**

The Gemini Web pipeline has:
- ✅ **Stage 0 Assessment:** Complete and documented
- ❌ **Stage 1+ Implementation:** Not yet started
- 📋 **Status:** Ready for Stage 1 implementation

**Alignment with Universal Pattern:** The Stage 0 assessment follows the universal pattern correctly and provides a clear roadmap for implementation.

---

## Current State

### What Exists

1. **Stage 0 Assessment** ✅
   - **Location:** `src/services/_archive_architect_central_removed_20260106/docs/STAGE_0_GEMINI_WEB.md`
   - **Script:** `src/services/_archive_architect_central_removed_20260106/scripts/stage_0_gemini_web.py`
   - **Status:** Complete assessment with full central services integration
   - **Pattern Identified:** Web Export - Activity Log Variant

2. **Data Dictionary** ✅
   - **Location:** `src/services/_archive_architect_central_removed_20260106/docs/GEMINI_WEB_DATA_DICTIONARY.md`
   - **Status:** Complete recursive field discovery

3. **Supporting Services** (in archived services)
   - `gemini_web_loader.py` - Data loader
   - `gemini_web_splitter.py` - Content splitter
   - `gemini_web_gcs_worker.py` - GCS operations
   - Various staging scripts

### What's Missing

1. **Pipeline Directory Structure** ❌
   - No `pipelines/gemini_web/` directory
   - No stage scripts (Stage 1+)
   - No documentation structure
   - No SQL definitions

2. **Stage 1+ Implementation** ❌
   - No source ingestion script
   - No normalization script
   - No ID generation script
   - No LLM processing script
   - No NLP processing script

---

## Universal Pipeline Pattern Requirements

### Required Directory Structure

According to `UNIVERSAL_PIPELINE_PATTERN.md`, Gemini Web needs:

```
pipelines/gemini_web/
├── README.md                      # Pipeline overview
├── scripts/
│   ├── stage_0/                  # ✅ Exists (in archived)
│   │   └── gemini_web_stage_0.py
│   ├── stage_1/                   # ❌ Missing
│   │   └── gemini_web_stage_1.py
│   ├── stage_2/                   # ❌ Missing
│   │   └── gemini_web_stage_2.py
│   ├── stage_3/                   # ❌ Missing
│   │   └── gemini_web_stage_3.py
│   ├── stage_4/                   # ❌ Missing
│   │   └── gemini_web_stage_4.py
│   ├── stage_5/                   # ❌ Missing
│   │   └── gemini_web_stage_5.py
│   ├── validation/                # ❌ Missing
│   │   └── validate_promotion.py
│   ├── promotion/                  # ❌ Missing
│   │   └── promote_to_entity_unified.py
│   └── utilities/                 # ❌ Missing
│       └── common_functions.py
├── docs/
│   ├── INDEX.md                   # ❌ Missing
│   ├── STAGES.md                  # ❌ Missing
│   ├── SCHEMA.md                  # ❌ Missing
│   └── TROUBLESHOOTING.md         # ❌ Missing
├── sql/
│   ├── tables/                    # ❌ Missing
│   │   └── stage_tables_with_labels.sql
│   └── views/                     # ❌ Missing
│       └── monitoring_views.sql
└── config/                        # ❌ Missing
    └── pipeline_config.yaml
```

### Required Stages (Per Universal Pattern)

| Stage | Purpose | Status | Notes |
|-------|---------|--------|-------|
| **Stage 0** | Source Assessment | ✅ Complete | Assessment done, needs migration to new structure |
| **Stage 1** | Source Ingestion | ❌ Missing | Extract activities, group into conversations |
| **Stage 2** | Source Normalization | ❌ Missing | Extract text from HTML, normalize timestamps |
| **Stage 3** | System ID Generation | ❌ Missing | Generate Truth Engine IDs |
| **Stage 4** | LLM Processing | ❌ Missing | Text correction, readiness check |
| **Stage 5** | NLP Processing | ❌ Missing | spaCy processing, entity extraction |
| **Stage 6+** | Enrichment | ❌ Missing | Follow universal pattern |

---

## Stage 0 Assessment Analysis

### ✅ What Stage 0 Got Right

1. **Complete Assessment**
   - Analyzed all 751 activities (no sampling)
   - Recursive field discovery
   - Complete data dictionary

2. **Pattern Identification**
   - Correctly identified: Web Export - Activity Log Variant
   - Documented differences from ChatGPT Web and Claude Web
   - Established grouping strategy (time-based)

3. **Central Services Integration**
   - Uses `get_logger` (not print)
   - Uses `get_current_run_id`
   - Uses `get_unified_governance`
   - Records audit trail
   - Requires diagnostics on errors

4. **Source-to-Target Mapping**
   - Clear mapping to universal pattern stages
   - Identified special requirements (HTML parsing, time-based grouping)

### ⚠️ What Needs Attention

1. **Location**
   - Stage 0 script is in archived services
   - Should be moved to `pipelines/gemini_web/scripts/stage_0/`

2. **Documentation Location**
   - Assessment doc is in archived services
   - Should be moved to `pipelines/gemini_web/docs/`

3. **Integration**
   - Needs to be integrated with new pipeline structure
   - Should follow text_messages pipeline as reference

---

## Alignment with Universal Pattern

### ✅ Alignment Score: 75%

**What Aligns:**
- ✅ Stage 0 assessment follows universal pattern
- ✅ Central services integration correct
- ✅ Pattern identification complete
- ✅ Source-to-target mapping documented

**What Doesn't Align:**
- ❌ No pipeline directory structure
- ❌ No stage implementations
- ❌ No SQL definitions
- ❌ No documentation structure
- ❌ Stage 0 in wrong location (archived services)

---

## Stage 0 Assessment Findings (Key Points)

### Data Structure

**Format:** Google Takeout Activity Log
- Array of activity items (not conversations)
- Each item = one interaction (prompt + response)
- HTML content in `safeHtmlItem`
- No explicit conversation/message IDs

**Key Differences from Other Web Pipelines:**
- **ChatGPT Web:** Pre-grouped conversations with IDs
- **Claude Web:** Pre-grouped conversations with IDs
- **Gemini Web:** Activity log requiring time-based grouping

### Special Requirements

1. **Time-Based Grouping** (Stage 1)
   - Activities must be grouped into conversations
   - Use time proximity algorithm
   - No explicit conversation structure

2. **HTML Parsing** (Stage 2)
   - Response content is HTML, not plain text
   - Must extract text from `safeHtmlItem` array
   - Requires HTML parsing library

3. **ID Generation** (Stage 3)
   - Must generate conversation IDs (from grouped activities)
   - Must generate message IDs (2 per activity: prompt + response)
   - No source IDs to preserve

### Universal Pattern Adaptation

**Stage 1 (Source Ingestion):**
- Extract: Activities from JSON array
- Group: Activities into conversations (time-based)
- Store: Complete raw activity data in metadata JSON
- Output: `gemini_web_stage_1` table

**Stage 2 (Source Normalization):**
- Extract: Prompt text (from `title` field)
- Extract: Response text (from `safeHtmlItem` HTML - **requires HTML parsing**)
- Normalize: Timestamps
- Output: `gemini_web_stage_2` table

**Stage 3 (System ID Generation):**
- Generate: Truth Engine system IDs
- Map: Activities → conversation IDs (grouped)
- Map: Activities → message IDs (2 per activity)
- Output: `gemini_web_stage_3` table

**Stage 4 (LLM Processing):**
- Required: Yes (text correction)
- Process: Corrected text, skip classification
- Output: `gemini_web_stage_4` and `stage_5` tables

**Stage 5 (NLP Processing):**
- Process: L5 messages → L1 tokens (spaCy)
- Expansion: ~970x (1 message → ~970 entities)
- Output: `gemini_web_stage_7` table

---

## Comparison with Text Messages Pipeline

### Text Messages Pipeline (Reference)

**Status:** ✅ Stages 1-7 complete, Stages 8-16 pending

**Structure:**
```
pipelines/text_messages/
├── scripts/
│   ├── stage_0/          ✅
│   ├── stage_1/          ✅
│   ├── stage_2/          ✅
│   ├── stage_3/          ✅
│   ├── stage_4/          ✅
│   ├── stage_5/          ✅
│   ├── stage_6/          ✅
│   ├── stage_7/          ✅
│   ├── stage_8/          ✅
│   ├── stage_9/          ✅
│   ├── stage_10/         ✅
│   ├── stage_11/         ✅
│   ├── stage_12/         ✅
│   ├── stage_13/         ✅
│   ├── stage_14/         ✅
│   ├── stage_15/         ✅
│   ├── shared/           ✅
│   ├── validation/       ✅
│   └── utilities/        ✅
```

**What Gemini Web Can Learn:**
- Directory structure pattern
- Shared utilities pattern
- Stage implementation pattern
- Validation approach
- Documentation structure

---

## Recommendations

### Immediate Actions

1. **Create Pipeline Directory Structure**
   ```bash
   mkdir -p pipelines/gemini_web/{scripts,docs,sql/{tables,views},config}
   ```

2. **Migrate Stage 0**
   - Move script from archived services
   - Move documentation
   - Update paths

3. **Start Stage 1 Implementation**
   - Use text_messages pipeline as reference
   - Implement activity extraction
   - Implement time-based grouping
   - Follow universal pattern requirements

### Implementation Priority

1. **Phase 1: Foundation** (Week 1)
   - Create directory structure
   - Migrate Stage 0
   - Implement Stage 1 (Source Ingestion)

2. **Phase 2: Core Processing** (Week 2)
   - Implement Stage 2 (Normalization with HTML parsing)
   - Implement Stage 3 (ID Generation)

3. **Phase 3: LLM & NLP** (Week 3)
   - Implement Stage 4 (LLM Processing)
   - Implement Stage 5 (NLP Processing)

4. **Phase 4: Enrichment** (Week 4+)
   - Follow universal pattern for remaining stages
   - Implement validation
   - Implement promotion

### Key Implementation Notes

1. **HTML Parsing Library**
   - Need to choose: BeautifulSoup, lxml, or html.parser
   - Extract text from `safeHtmlItem` array
   - Handle nested HTML structures

2. **Time-Based Grouping Algorithm**
   - Define time threshold (e.g., 30 minutes between activities)
   - Group activities into conversations
   - Handle edge cases (single activities, long gaps)

3. **ID Generation Strategy**
   - Generate deterministic conversation IDs from grouped activities
   - Generate message IDs for prompt + response pairs
   - Maintain sequence numbers

---

## Gap Analysis

### Missing Components

| Component | Status | Priority |
|-----------|--------|----------|
| Pipeline directory | ❌ Missing | HIGH |
| Stage 1 script | ❌ Missing | HIGH |
| Stage 2 script | ❌ Missing | HIGH |
| Stage 3 script | ❌ Missing | HIGH |
| Stage 4 script | ❌ Missing | HIGH |
| Stage 5 script | ❌ Missing | HIGH |
| SQL table definitions | ❌ Missing | HIGH |
| Documentation structure | ❌ Missing | MEDIUM |
| Validation scripts | ❌ Missing | MEDIUM |
| Promotion scripts | ❌ Missing | LOW |

### Alignment Gaps

| Gap | Impact | Fix Required |
|-----|--------|--------------|
| No pipeline structure | Cannot implement stages | Create directory structure |
| Stage 0 in wrong location | Hard to find | Move to pipelines/gemini_web/ |
| No stage implementations | No processing | Implement stages 1-5 |
| No SQL definitions | No data storage | Create table definitions |
| No HTML parsing | Cannot extract text | Implement HTML parser |

---

## Next Steps

1. **Review this analysis** with Jeremy
2. **Decide on implementation priority**
3. **Create pipeline directory structure**
4. **Migrate Stage 0 to new location**
5. **Start Stage 1 implementation**
6. **Follow text_messages pipeline as reference**

---

## References

- **Universal Pipeline Pattern:** `src/services/_archive_architect_central_removed_20260106/pipelines/UNIVERSAL_PIPELINE_PATTERN.md`
- **Stage 0 Assessment:** `src/services/_archive_architect_central_removed_20260106/docs/STAGE_0_GEMINI_WEB.md`
- **Text Messages Pipeline:** `pipelines/text_messages/` (reference implementation)
- **Universal Processing Architecture:** `framework/architecture/UNIVERSAL_PROCESSING_ARCHITECTURE.md`

---

**Analysis Complete:** January 6, 2025
