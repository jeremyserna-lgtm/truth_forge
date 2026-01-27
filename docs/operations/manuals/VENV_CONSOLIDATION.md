---
document_id: doc:87f21e96ae46
processed_at: '2026-01-03T23:59:22.247800+00:00'
source_path: /Users/jeremyserna/PrimitiveEngine/VENV_CONSOLIDATION.md
current_path: /Users/jeremyserna/PrimitiveEngine/VENV_CONSOLIDATION.md
changelog:
- timestamp: '2026-01-03T23:59:22.247800+00:00'
  action: stamped
  by: frontmatter_service
  details: 'Initial processing, ID issued. Run: 58ecaf51'
---

# Virtual Environment Consolidation

**Date:** 2026-01-03
**Action:** Consolidated virtual environments to reduce redundancy

## Current Virtual Environment Structure

### ✅ Primary Development Environment
- **`architect_central_services/.venv`** (Python 3.12.8, ~1.2GB)
  - Main development environment for Truth Engine
  - Contains all dependencies from `architect_central_services/requirements.txt`
  - Used by scripts (e.g., `calculate_tfidf_scores.sh`)

### ✅ Separate Project Environments (kept for isolation)
- **`venvs/credential_atlas`** (Python 3.13.7, ~16MB)
  - Isolated environment for Credential Atlas project
- **`venvs/sovereign_agent`** (Python 3.13.7, ~182MB)
  - Isolated environment for Sovereign Agent project

### ❌ Removed (redundant)
- **`venv/`** (root, Python 3.13.7, 202MB)
  - Was not actively referenced by any scripts
  - Dependencies overlapped with `architect_central_services/.venv`
  - **Freed 202MB**

## Usage

### Activate Main Development Environment
```bash
cd architect_central_services
source .venv/bin/activate
```

### Activate Separate Project Environments
```bash
# Credential Atlas
source venvs/credential_atlas/bin/activate

# Sovereign Agent
source venvs/sovereign_agent/bin/activate
```

## Rationale

1. **Main venv**: `architect_central_services/.venv` is the primary development environment used by scripts and contains the comprehensive dependency set.

2. **Separate project venvs**: Kept `venvs/credential_atlas` and `venvs/sovereign_agent` for project isolation - different projects may have different dependency requirements.

3. **Removed root venv**: The root `venv/` was redundant - it used Python 3.13 while the main development uses Python 3.12, and wasn't referenced by any active scripts.

## Space Savings

- **Before**: ~1.6GB total (1.2GB + 202MB + 182MB + 16MB)
- **After**: ~1.4GB total (1.2GB + 182MB + 16MB)
- **Freed**: ~202MB

## Notes

- All venvs can be regenerated from their respective `requirements.txt` files if needed
- The main environment should be used for Truth Engine development
- Separate project venvs provide isolation for different codebases
