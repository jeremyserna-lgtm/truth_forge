# Truth Engine Developer Manual

**Version**: 1.0.0
**Last Updated**: 2025-01-XX
**For**: Developers working on Truth Engine

---

## 📖 Table of Contents

1. [Introduction](#introduction)
2. [System Architecture](#system-architecture)
3. [Getting Started as a Developer](#getting-started-as-a-developer)
4. [Pipeline Development](#pipeline-development)
5. [Running Pipelines](#running-pipelines)
6. [Monitoring and Status](#monitoring-and-status)
7. [Data Quality and Validation](#data-quality-and-validation)
8. [Error Handling and Debugging](#error-handling-and-debugging)
9. [Configuration Management](#configuration-management)
10. [Adding New Data Sources](#adding-new-data-sources)
11. [Central Services](#central-services)
12. [Governance and Standards](#governance-and-standards)
13. [Testing and Validation](#testing-and-validation)
14. [Deployment and Operations](#deployment-and-operations)
15. [Reference](#reference)

---

## 🎯 Introduction

### What is Truth Engine (Developer Perspective)

Truth Engine is a data processing framework built on the **HOLD₁ → AGENT → HOLD₂** pattern (Primitive Pattern). It processes conversations from various sources (Claude Code, Codex, GitHub, text messages) through multiple stages to produce insights for end users.

### Core Principles

1. **HOLD Pattern**: All data flows through HOLD stages (persistent storage)
2. **Governance First**: Universal governance policies applied to all operations
3. **Stage Five Alignment**: Cognitive architecture aligned with Stage 5 thinking
4. **Fail-Safe Operations**: Idempotent, observable, and fail-safe by design
5. **Central Services**: Shared services for logging, identity, governance

### Key Concepts

- **Pipeline**: A series of stages that transform data from source to destination
- **Stage**: A single transformation step (Extraction, Enrichment, Registration, Correction, etc.)
- **HOLD₁**: Input data storage (source data)
- **AGENT**: Transformation logic (the actual processing)
- **HOLD₂**: Output data storage (processed data)
- **Entity Unified**: Final destination table where all processed data converges

---

## 🏗️ System Architecture

### High-Level Architecture

```
Source Files (JSONL/CSV/etc.)
    ↓
Stage 0: Extraction (HOLD₁ → AGENT → HOLD₂)
    ↓
Stage 1: Enrichment (HOLD₁ → AGENT → HOLD₂)
    ↓
Stage 3: ID Registration "THE GATE" (HOLD₁ → AGENT → HOLD₂)
    ↓
Stage 4: LLM Text Correction (HOLD₁ → AGENT → HOLD₂)
    ↓
Stage 5: Ready Messages (automatic from Stage 4)
    ↓
Stage 6: Write to entity_unified (HOLD₁ → AGENT → HOLD₂)
    ↓
entity_unified (Final Destination)
```

### Pipeline Structure

Each pipeline follows this structure:

```
pipelines/
└── pipeline_name/
    ├── README.md
    ├── docs/
    │   └── PIPELINE_PLAN.md
    ├── scripts/
    │   ├── stage_0/
    │   │   └── pipeline_name_stage_0.py
    │   ├── stage_1/
    │   ├── stage_3/
    │   ├── stage_4/
    │   ├── stage_6/
    │   ├── utilities/
    │   │   ├── run_full_pipeline.py
    │   │   └── check_pipeline_status.py
    │   └── validation/
    └── sql/
        └── tables/
            ├── stage_0_table.sql
            └── ...
```

### Data Flow

1. **Extraction (Stage 0)**: Read from source files or `entity_unified`, filter by source
2. **Enrichment (Stage 1)**: Add sentiment, entities, topics, quality scores
3. **ID Registration (Stage 3)**: Register entity_ids with identity service (THE GATE)
4. **Text Correction (Stage 4)**: LLM-based text cleaning and correction
5. **Ready Messages (Stage 5)**: Automatic output from Stage 4 (ready for final storage)
6. **Final Write (Stage 6)**: Transform and write to `entity_unified` table

---

## 🚀 Getting Started as a Developer

### Prerequisites

- **Python 3.10+**: Required for all scripts
- **Google Cloud SDK**: For BigQuery access
- **BigQuery Dataset**: Access to `flash-clover-464719-g1.spine` dataset
- **Local Ollama**: For Stage 4 LLM processing (local, free)
- **IDE**: VS Code or similar with Python support

### Development Environment Setup

1. **Clone Repository**:
   ```bash
   cd /Users/jeremyserna/PrimitiveEngine
   ```

2. **Set Up Python Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Google Cloud**:
   ```bash
   gcloud auth application-default login
   gcloud config set project flash-clover-464719-g1
   ```

4. **Verify BigQuery Access**:
   ```bash
   python -c "from google.cloud import bigquery; print('✅ BigQuery access OK')"
   ```

5. **Start Ollama** (for Stage 4):
   ```bash
   ollama serve
   ```

### Project Structure

```
PrimitiveEngine/
├── pipelines/              # Pipeline implementations
│   ├── claude_codex_github/
│   ├── gemini_web/
│   └── text_messages/
├── src/                    # Source code
│   └── services/
│       └── central_services/  # Shared services
├── docs/                   # Documentation
│   └── manuals/           # This manual and User Manual
├── Primitive/             # Primitive Pattern implementations
└── scripts/               # Utility scripts
```

---

## 🔧 Pipeline Development

### Creating a New Pipeline Stage

1. **Create Stage Directory**:
   ```bash
   mkdir -p pipelines/my_pipeline/scripts/stage_0
   ```

2. **Create Stage Script** (template):
   ```python
   #!/usr/bin/env python3
   """Stage 0: Description - Pipeline Name

   🧠 STAGE FIVE GROUNDING:
   ========================
   [Explain the stage's purpose in Stage 5 terms]

   ⚠️ WHAT THIS SCRIPT CANNOT SEE:
   [Document blind spots]

   🔥 THE FURNACE PRINCIPLE:
   - Truth (Input): [What comes in]
   - Heat (Processing): [What happens]
   - Meaning (Output): [What comes out]
   - Care (Delivery): [How it's delivered safely]
   """

   import sys
   from pathlib import Path

   # Add project root to path
   PROJECT_ROOT = Path(__file__).resolve().parents[4]
   sys.path.append(str(PROJECT_ROOT))
   sys.path.append(str(PROJECT_ROOT / "src"))

   from src.services.central_services.core import (
       get_current_run_id,
       get_logger,
       get_correlation_ids,
   )
   from src.services.central_services.core.config import get_bigquery_client
   from src.services.central_services.governance.governance import (
       get_unified_governance,
       require_diagnostic_on_error,
   )

   logger = get_logger(__name__)

   # Configuration
   PROJECT_ID = "flash-clover-464719-g1"
   DATASET_ID = "spine"

   def main():
       """Main execution function."""
       run_id = get_current_run_id()
       correlation_ids = get_correlation_ids()
       governance = get_unified_governance()

       logger.info(
           "Starting Stage 0",
           extra={
               "run_id": run_id,
               **correlation_ids,
           },
       )

       try:
           client = get_bigquery_client()
           # Your stage logic here
           return 0
       except Exception as e:
           logger.error(f"Error in Stage 0: {e}", exc_info=True)
           require_diagnostic_on_error(e, "main")
           return 1

   if __name__ == "__main__":
       exit(main())
   ```

3. **Follow Required Patterns**:
   - Use `get_logger(__name__)` (NOT `print()`)
   - Use `get_current_run_id()` for traceability
   - Use `get_unified_governance()` for audit trails
   - Use `require_diagnostic_on_error()` for error handling
   - Include Stage Five Grounding comments
   - Document blind spots
   - Follow HOLD₁ → AGENT → HOLD₂ pattern

### Stage Requirements Checklist

- [ ] Stage Five Grounding section
- [ ] Blind spots documented
- [ ] Furnace Principle explained
- [ ] Central services integration
- [ ] Governance integration
- [ ] Error handling with diagnostics
- [ ] Audit trail recording
- [ ] Structured logging
- [ ] Traceability (run_id, correlation_ids)
- [ ] HOLD pattern implementation

---

## 🏃 Running Pipelines

### Running Individual Stages

```bash
# Stage 0 (Extraction)
cd pipelines/claude_codex_github/scripts/stage_0
python claude_codex_github_stage_0.py

# Stage 1 (Enrichment)
cd ../stage_1
python claude_codex_github_stage_1.py

# Stage 3 (ID Registration)
cd ../stage_3
python claude_codex_github_stage_3.py

# Stage 4 (LLM Text Correction)
cd ../stage_4
python claude_codex_github_stage_4.py

# Stage 6 (Final Write)
cd ../stage_6
python claude_codex_github_stage_6.py
```

### Running Full Pipeline

```bash
cd pipelines/claude_codex_github/scripts/utilities
python run_full_pipeline.py
```

### Stage 4 Options

Stage 4 supports several options:

```bash
python claude_codex_github_stage_4.py \
    --batch-size 1000 \      # PrimitivePattern batch size
    --limit 100 \            # Limit records (for testing)
    --restart \              # Restart from beginning
    --test \                 # Test mode (100 records)
    --skip-pattern           # Skip PrimitivePattern (load HOLD₂ only)
```

### Common Commands

**Test Mode** (100 records):
```bash
python claude_codex_github_stage_4.py --test
```

**Restart from Beginning**:
```bash
python claude_codex_github_stage_4.py --restart
```

**Check Status First**:
```bash
python check_pipeline_status.py
```

---

## 📊 Monitoring and Status

### Check Pipeline Status

```bash
cd pipelines/claude_codex_github/scripts/utilities
python check_pipeline_status.py
```

Output shows:
- Message counts per stage
- Source breakdown
- Progress percentages
- Recommendations for next steps

### View Errors

Errors are logged to:
- **Central Logging**: `architect_central_services/logs/central.log`
- **Pipeline Tracker**: `logs/pipelines/claude_codex_github.jsonl`
- **Console**: Script output

### Health Dashboard

Monitor system health through:
1. **Pipeline Status**: `check_pipeline_status.py`
2. **BigQuery Console**: View table row counts
3. **Central Logs**: Review `central.log` for issues

### One-Button Operations (Developer)

See `pipelines/claude_codex_github/docs/ONE_BUTTON_ACTIONS.md` for:
- Run Full Pipeline
- Check Pipeline Status
- View Errors
- Assess Data Quality
- Process New Data
- Continue From Failure
- And more...

---

## ✅ Data Quality and Validation

### Assess Data Quality

```bash
cd pipelines/claude_codex_github/scripts/assessment
python assess_text_quality.py
```

Checks for:
- Whitespace issues (double spaces, tabs)
- Leading/trailing whitespace
- Text length statistics
- Empty/null text
- Recommendations for normalization

### Validate Pipeline

```bash
cd pipelines/claude_codex_github/scripts/validation
python validate_claude_codex_github_pipeline.py
```

Validates:
- Pipeline integrity
- Data consistency
- Schema compliance
- Stage connections

### Fix Common Issues

Common data quality issues:
1. **Whitespace**: Stage 4 LLM correction handles most whitespace issues
2. **Encoding**: Ensure UTF-8 encoding throughout
3. **Schema Mismatches**: Check BigQuery schema matches expectations
4. **Missing Data**: Verify source data completeness

---

## 🐛 Error Handling and Debugging

### Error Handling Pattern

All stages must use:
```python
try:
    # Your code here
    pass
except Exception as e:
    logger.error(f"Error in operation: {e}", exc_info=True)
    require_diagnostic_on_error(e, "operation_name")
    raise  # Or return error code
```

### Diagnostic Requirements

All errors must trigger diagnostics:
- Root cause analysis
- Remediation steps
- Prevention measures
- Block operations until resolved

### Debugging Tips

1. **Check Logs First**:
   ```bash
   tail -f architect_central_services/logs/central.log
   ```

2. **Run in Test Mode**:
   ```bash
   python stage_X.py --test
   ```

3. **Check BigQuery Tables**:
   - Verify data exists in source tables
   - Check row counts match expectations
   - Verify schema matches

4. **Review HOLD Files**:
   - Check `Primitive/staging/pipeline_name_stage_X/`
   - Inspect `hold1_input.jsonl` and `hold2_output.jsonl`

5. **Validate Before Run**:
   - Check for uncommitted changes
   - Verify no blocking errors
   - Confirm dependencies are met

### Common Errors

**"Table not found"**:
- Check table name spelling
- Verify BigQuery dataset access
- Confirm table was created

**"No data exported"**:
- Verify source data exists
- Check WHERE clause filters
- Review extraction queries

**"LLM processing failed"**:
- Check Ollama is running
- Verify model is available
- Review batch size (may be too large)

---

## ⚙️ Configuration Management

### Pipeline Configuration

Pipeline-specific configs in:
- `pipelines/pipeline_name/config/` (if exists)
- Script-level constants (PROJECT_ID, DATASET_ID, etc.)

### Central Configuration

Central config in:
- `central_config.toml`: Global configuration
- Environment variables: Secrets and credentials

### BigQuery Configuration

- **Project ID**: `flash-clover-464719-g1`
- **Dataset**: `spine`
- **Tables**: Pipeline-specific (e.g., `claude_codex_github_stage_0`)

### Environment Setup

Required environment variables:
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to GCP credentials (or use `gcloud auth application-default login`)
- `PROJECT_ROOT`: Usually set automatically

---

## ➕ Adding New Data Sources

### Steps to Add a New Source

1. **Create Pipeline Directory**:
   ```bash
   mkdir -p pipelines/new_source/scripts/stage_0
   ```

2. **Create Stage 0** (Extraction):
   - Read from source (files, API, database)
   - Filter by source_name
   - Extract level 5 entities (messages)
   - Write to `new_source_stage_0` table

3. **Follow Standard Stages**:
   - Stage 1: Enrichment
   - Stage 3: ID Registration (THE GATE)
   - Stage 4: LLM Text Correction
   - Stage 6: Write to entity_unified

4. **Update Utilities**:
   - Add to `run_full_pipeline.py`
   - Add to `check_pipeline_status.py`
   - Create validation scripts

5. **Document**:
   - Create README.md
   - Document data source structure
   - Add to system catalog

### Example: Adding a New Source

See existing pipelines for reference:
- `pipelines/claude_codex_github/` (JSONL source)
- `pipelines/gemini_web/` (different source format)
- `pipelines/text_messages/` (different structure)

---

## 🏛️ Central Services

### Core Services

Located in `src/services/central_services/`:

- **core/**: Logging, configuration, BigQuery client, run IDs
- **governance/**: Universal governance, hooks, diagnostics
- **identity_service/**: Entity ID registration (THE GATE)
- **truth_service/**: Entity unified table operations
- **schema_service/**: Schema validation and registry

### Using Central Services

**Logging**:
```python
from src.services.central_services.core import get_logger
logger = get_logger(__name__)
logger.info("Message", extra={"key": "value"})
```

**Run ID and Correlation**:
```python
from src.services.central_services.core import (
    get_current_run_id,
    get_correlation_ids,
)
run_id = get_current_run_id()
correlation_ids = get_correlation_ids()
```

**BigQuery Client**:
```python
from src.services.central_services.core.config import get_bigquery_client
client = get_bigquery_client()
```

**Governance**:
```python
from src.services.central_services.governance.governance import (
    get_unified_governance,
    require_diagnostic_on_error,
)
governance = get_unified_governance()
# Record audit, enforce policies, etc.
```

### Service Documentation

See individual service READMEs:
- `src/services/central_services/core/README.md`
- `src/services/central_services/governance/README.md`
- `src/services/central_services/identity_service/README.md`

---

## 🛡️ Governance and Standards

### Universal Governance

All operations must follow:
- **Traceability**: run_id, correlation_ids in all logs
- **Audit Trail**: Record all operations via governance.record_audit()
- **Structured Logging**: Use get_logger(), never print()
- **Error Handling**: require_diagnostic_on_error() for all errors
- **Pre-Run Validation**: validate_before_run() before execution

### Required Patterns

**HOLD Pattern**:
- HOLD₁: Input storage (BigQuery table or JSONL)
- AGENT: Transformation logic
- HOLD₂: Output storage (BigQuery table or JSONL)

**Stage Five Alignment**:
- Stage Five Grounding comments
- Blind spot documentation
- Furnace Principle explanation

**Four Pillars**:
- Fail-Safe: Idempotent operations
- No Magic: Clear, explicit logic
- Observability: Comprehensive logging
- Idempotency: Safe to re-run

### Code Standards

See `.cursor/rules/` for:
- Stage Five Cognitive Alignment
- Cost Protection
- Logging Governance
- Code Examples
- Universal Governance Enforcement

---

## 🧪 Testing and Validation

### Local Testing

1. **Test Mode**:
   ```bash
   python stage_X.py --test
   ```
   Limits to 100 records

2. **Dry Run** (if supported):
   ```bash
   python stage_X.py --dry-run
   ```

3. **Check Results**:
   - Verify row counts
   - Check data quality
   - Validate schema

### Validation Scripts

Each pipeline should have:
- `scripts/validation/validate_pipeline.py`
- `scripts/assessment/assess_quality.py`

### Pre-Deployment Validation

Before deploying:
1. Run validation scripts
2. Check for errors
3. Verify governance compliance
4. Test in dry-run mode
5. Review audit logs

---

## 🚢 Deployment and Operations

### Pre-Deployment Checklist

- [ ] All tests pass
- [ ] Validation scripts pass
- [ ] No uncommitted changes
- [ ] Governance compliance verified
- [ ] Documentation updated
- [ ] Logging verified
- [ ] Error handling tested

### Deployment Process

1. **Commit Changes**:
   ```bash
   git add .
   git commit -m "Description"
   ```

2. **Run Pre-Deployment Hook**:
   ```python
   from architect_central_services.governance.pre_deployment_hook import pre_deployment_hook
   result = pre_deployment_hook()
   if result['blocked']:
       # Fix issues
   ```

3. **Deploy**:
   - Push to repository
   - Run in production environment
   - Monitor logs

### Operations

**Monitoring**:
- Check pipeline status regularly
- Monitor error logs
- Review audit trails
- Track processing times

**Maintenance**:
- Clear staging files periodically
- Backup important state
- Update documentation
- Review and optimize queries

---

## 📚 Reference

### Key Documents

- **System Catalogue**: `docs/COMPLETE_SYSTEM_CATALOGUE.md`
- **Framework Specs**: `docs/FRAMEWORK_TECHNICAL_SPECIFICATIONS.md`
- **One Button Actions**: `pipelines/claude_codex_github/docs/ONE_BUTTON_ACTIONS.md`
- **Pipeline Pattern Spec**: `framework/standards/PIPELINE_PATTERN_SPECIFICATION.md`

### BigQuery Tables

- **entity_unified**: Final destination for all processed data
- **Pipeline Stage Tables**: `pipeline_name_stage_X` (e.g., `claude_codex_github_stage_0`)

### Important Paths

- **Pipelines**: `pipelines/pipeline_name/`
- **Central Services**: `src/services/central_services/`
- **Staging Files**: `Primitive/staging/pipeline_name_stage_X/`
- **Logs**: `architect_central_services/logs/central.log`

### Quick Commands Reference

```bash
# Check status
python check_pipeline_status.py

# Run full pipeline
python run_full_pipeline.py

# Run single stage
python stage_X.py

# Test mode
python stage_X.py --test

# Assess quality
python assess_text_quality.py

# Validate pipeline
python validate_pipeline.py
```

---

## 📝 Notes

This manual is a living document. As Truth Engine evolves, this manual will be updated. Check version number for latest updates.

**For End Users**: See `docs/manuals/USER_MANUAL.md`

**Questions?**: Review documentation in `docs/` or check service READMEs.

---

## 🤝 Contributing

When adding features:
1. Follow governance standards
2. Update this manual
3. Add tests
4. Document in pipeline README
5. Update system catalog if needed

Thank you for contributing to Truth Engine!
