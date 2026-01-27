# Pipeline Documents Deprecation Plan

**Date**: 2026-01-27  
**Status**: Planning  
**Purpose**: Consolidate, deprecate, and archive duplicate/out-of-date pipeline documents

---

## Analysis Summary

### Document Counts
- **Total markdown files**: 239
- **Report files**: 81 (many duplicates across stages)
- **Status files**: 21
- **Assessment files**: 15

### Duplicate Patterns Identified

1. **Stage Reports** (4 reports × 17 stages = 68 files)
   - FIDELITY_REPORT.md
   - TRUST_REPORT.md
   - COMPLIANCE_REPORT.md
   - HONESTY_REPORT.md
   - **Action**: These are likely out-of-date snapshots. Consolidate into single status document per stage or archive all.

2. **Status Files** (21 files)
   - Multiple status files with similar names
   - **Action**: Consolidate into single current status document, archive old ones.

3. **Assessment Files** (15 files)
   - Various assessment documents
   - **Action**: Review and consolidate where possible.

---

## Consolidation Strategy

### 1. Stage Reports
**Current**: 68 report files (4 types × 17 stages)  
**Proposed**: Archive all stage-specific reports, create consolidated pipeline status document

**Rationale**: 
- Stage reports are snapshots at a point in time
- Current pipeline status should be in single location
- Historical reports belong in archive

### 2. Status Files
**Current**: 21 status files  
**Proposed**: 
- Keep most recent comprehensive status
- Archive all others

### 3. Assessment Files
**Current**: 15 assessment files  
**Proposed**: 
- Review for duplicates
- Consolidate similar assessments
- Archive outdated ones

---

## Archive Plan

### GCS Bucket Structure
```
gs://truth-engine-archive/
└── pipelines/
    └── adapters/
        └── claude_code/
            ├── scripts/
            │   └── archive/
            │       └── 2026_01_27_consolidation/
            │           ├── stage_reports/ (68 files)
            │           ├── status_files/ (20 files)
            │           └── assessments/ (TBD)
            └── reports/
                └── archive/
                    └── 2026_01_27_consolidation/
                        └── (consolidated reports)
```

---

## Execution Steps

1. ✅ Update deprecation standards (remove redirect stubs)
2. ⏳ Identify all duplicate/out-of-date documents
3. ⏳ Create consolidated documents where appropriate
4. ⏳ Add deprecation headers to files to be archived
5. ⏳ Upload to GCS bucket `gs://truth-engine-archive/`
6. ⏳ Remove files from source locations
7. ⏳ Update archive INDEX.md files

---

*Plan ready for execution.*
