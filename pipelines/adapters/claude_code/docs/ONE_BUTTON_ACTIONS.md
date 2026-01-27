# One Button Actions - Product Improvement Roadmap

## 🎯 Overview

This document outlines all the "one button" actions that customers would want to perform in the Truth Engine product. These are single-click operations that automate complex workflows or provide instant value.

---

## 📊 Category 1: Pipeline Execution

### 1. **"Run Full Pipeline"** 🚀
**What it does:** Executes all stages (0 → 1 → 3 → 4 → 6) in sequence automatically.
**Current state:** Script exists (`run_full_pipeline.py`) but requires terminal execution.
**Customer value:** Process all data from start to finish with one click.

### 2. **"Process New Data"** ✨
**What it does:** Detects unprocessed messages since last run and processes only those.
**Current state:** Manual checking required.
**Customer value:** Incremental updates without reprocessing everything.

### 3. **"Continue From Failure"** 🔄
**What it does:** Automatically detects where pipeline failed and resumes from that stage.
**Current state:** Manual identification and restart required.
**Customer value:** Self-healing pipelines that recover automatically.

### 4. **"Run Stage X"** 🎯
**What it does:** Execute a specific pipeline stage independently.
**Current state:** Manual script execution.
**Customer value:** Targeted reprocessing of specific stages.

### 5. **"Restart Failed Items"** 🔁
**What it does:** Re-process only the records that failed in previous runs.
**Current state:** Manual error identification required.
**Customer value:** Efficient error recovery without full re-runs.

---

## 📈 Category 2: Status & Monitoring

### 6. **"Check Pipeline Status"** 📊
**What it does:** Shows current state across all stages with counts and progress percentages.
**Current state:** Script exists (`check_pipeline_status.py`) but terminal-only.
**Customer value:** Instant visibility into pipeline health.

### 7. **"Show Health Dashboard"** 💚
**What it does:** Comprehensive system health view with alerts and warnings.
**Current state:** Distributed across multiple utilities.
**Customer value:** Single view of overall system status.

### 8. **"View Errors"** ⚠️
**What it does:** Lists all current errors, failed records, and blocking issues.
**Current state:** Errors scattered in logs.
**Customer value:** Centralized error visibility with context.

### 9. **"Show Pipeline Progress"** 📈
**What it does:** Visual progress bar showing completion percentage across all stages.
**Current state:** Calculated manually from status check.
**Customer value:** Clear progress indication for long-running pipelines.

### 10. **"View Recent Activity"** 🕐
**What it does:** Timeline of recent pipeline runs, successes, and failures.
**Current state:** Requires log digging.
**Customer value:** Historical context and pattern identification.

---

## ✅ Category 3: Quality & Validation

### 11. **"Assess Data Quality"** 🔍
**What it does:** Runs quality checks on extracted text (whitespace, formatting, completeness).
**Current state:** Script exists (`assess_text_quality.py`) but terminal-only.
**Customer value:** Instant quality metrics and recommendations.

### 12. **"Validate Pipeline"** ✔️
**What it does:** Checks pipeline integrity, data consistency, and schema compliance.
**Current state:** Validation script exists but requires manual execution.
**Customer value:** Confidence that pipeline is working correctly.

### 13. **"Fix Common Issues"** 🔧
**What it does:** Automatically fixes known problems (whitespace, formatting, etc.).
**Current state:** Manual intervention required.
**Customer value:** Self-healing data quality.

### 14. **"Recommend Next Steps"** 💡
**What it does:** Analyzes current state and suggests what to do next.
**Current state:** Manual assessment required.
**Customer value:** Guidance for non-expert users.

### 15. **"Compare Stages"** 🔄
**What it does:** Shows differences between stages (counts, data quality, transformations).
**Current state:** Manual querying required.
**Customer value:** Understand impact of each stage.

---

## 💾 Category 4: Data Management

### 16. **"Export Results"** 📥
**What it does:** Downloads processed data in selected format (CSV, JSONL, BigQuery export).
**Current state:** Manual BigQuery exports required.
**Customer value:** Easy data extraction for analysis.

### 17. **"View Insights"** 📊
**What it does:** Generates analytics and reports from processed data.
**Current state:** Manual querying required.
**Customer value:** Instant insights without SQL knowledge.

### 18. **"Search Messages"** 🔎
**What it does:** Search across all processed messages with filters.
**Current state:** Manual BigQuery queries required.
**Customer value:** Quick data discovery.

### 19. **"Filter by Source"** 🏷️
**What it does:** View data filtered by source (claude_code, codex, github).
**Current state:** Manual queries required.
**Customer value:** Source-specific analysis.

### 20. **"View Sample Data"** 👁️
**What it does:** Shows sample records from any stage for inspection.
**Current state:** Manual queries required.
**Customer value:** Quick data inspection without writing queries.

---

## 🛠️ Category 5: Configuration & Setup

### 21. **"Add New Source"** ➕
**What it does:** Wizard to onboard a new data source to pipeline.
**Current state:** Manual configuration and code changes required.
**Customer value:** Easy source expansion.

### 22. **"Configure Pipeline"** ⚙️
**What it does:** Edit pipeline settings (batch sizes, limits, model parameters).
**Current state:** Code/config file editing required.
**Customer value:** Easy parameter tuning.

### 23. **"Set Processing Limits"** 🎚️
**What it does:** Configure test mode, batch sizes, and processing limits.
**Current state:** Command-line arguments required.
**Customer value:** Control processing scale easily.

### 24. **"Manage Identity Mappings"** 👤
**What it does:** View and edit identity service registrations.
**Current state:** Manual checks via utilities.
**Customer value:** Identity data management.

### 25. **"Sync Identity Data"** 🔄
**What it does:** Refresh identity mappings from identity service.
**Current state:** Manual stage 3 re-run required.
**Customer value:** Keep identity data current.

---

## 🔧 Category 6: Recovery & Maintenance

### 26. **"Reset Stage X"** 🔄
**What it does:** Clear and restart a specific pipeline stage.
**Current state:** Manual table truncation and re-run required.
**Customer value:** Clean slate for reprocessing.

### 27. **"Clear Staging Data"** 🗑️
**What it does:** Remove HOLD₁ and HOLD₂ staging files to free space.
**Current state:** Manual file deletion.
**Customer value:** Storage management.

### 28. **"Backup Current State"** 💾
**What it does:** Creates snapshot of current pipeline state for recovery.
**Current state:** Manual BigQuery exports required.
**Customer value:** Safety net before changes.

### 29. **"Restore From Backup"** 🔙
**What it does:** Restores pipeline to a previous state.
**Current state:** Manual restoration required.
**Customer value:** Undo mistakes safely.

### 30. **"Validate Before Run"** ✅
**What it does:** Pre-flight checks before pipeline execution (uncommitted changes, errors, etc.).
**Current state:** Manual checks required.
**Customer value:** Prevent avoidable failures.

---

## 📱 Category 7: Notifications & Alerts

### 31. **"Set Up Alerts"** 🔔
**What it does:** Configure notifications for pipeline failures, completions, or thresholds.
**Current state:** Manual log monitoring required.
**Customer value:** Stay informed without watching.

### 32. **"View Notifications"** 📬
**What it does:** See all recent alerts and notifications.
**Current state:** No centralized notification system.
**Customer value:** Consolidated alert management.

### 33. **"Test Notification"** 🧪
**What it does:** Send a test alert to verify notification setup.
**Current state:** N/A.
**Customer value:** Verify alert configuration works.

---

## 🎓 Category 8: Learning & Documentation

### 34. **"Show What This Does"** ❓
**What it does:** Explains what each stage does in plain language.
**Current state:** Documentation exists but scattered.
**Customer value:** Understand pipeline without reading code.

### 35. **"View Documentation"** 📚
**What it does:** Contextual help and documentation for current view.
**Current state:** README files exist.
**Customer value:** Integrated help system.

### 36. **"Show Example Workflow"** 📖
**What it does:** Demonstrates typical usage patterns with examples.
**Current state:** Documentation exists separately.
**Customer value:** Learn by example.

---

## 🚀 Priority Recommendations

### **Must Have (MVP):**
1. **"Run Full Pipeline"** - Core value proposition
2. **"Check Pipeline Status"** - Essential visibility
3. **"View Errors"** - Critical for debugging
4. **"Assess Data Quality"** - Important validation
5. **"Process New Data"** - Efficiency gain

### **Should Have (V2):**
6. **"Continue From Failure"** - Self-healing
7. **"Export Results"** - Data access
8. **"View Insights"** - Value delivery
9. **"Fix Common Issues"** - Self-healing
10. **"Restart Failed Items"** - Error recovery

### **Nice to Have (V3):**
11. **"Add New Source"** - Expansion
12. **"Configure Pipeline"** - Flexibility
13. **"Backup/Restore"** - Safety
14. **"Set Up Alerts"** - Monitoring
15. **"Show What This Does"** - Education

---

## 🎯 Implementation Notes

### Frontend Integration
- Most buttons should be added to `primitive_app/components/PipelineView.tsx`
- Create new component: `primitive_app/components/PipelineActions.tsx`
- Add backend API endpoints in `primitive_app/server/index.ts`

### Backend Requirements
- Wrap existing Python scripts in API endpoints
- Add status tracking for async operations
- Create unified error reporting system
- Implement progress tracking for long-running operations

### User Experience
- Show loading states for long-running operations
- Provide progress indicators
- Display results inline where possible
- Offer undo/rollback for destructive actions
- Clear success/error messages

---

## 📝 Next Steps

1. **Prioritize** buttons based on customer feedback
2. **Design** UI/UX for button placement and interaction
3. **Implement** MVP buttons first (Run, Status, Errors)
4. **Test** with actual users
5. **Iterate** based on usage patterns
