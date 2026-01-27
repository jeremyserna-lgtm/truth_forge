"""Claude Code Pipeline - Shared Constants

Single source of truth for all pipeline configuration.
NO hardcoded values in stage scripts - import from here.

🧠 STAGE FIVE GROUNDING
This module exists to centralize all configuration for the Claude Code pipeline.

Structure: Define → Export → Validate (on import)
Purpose: Prevent configuration drift and hardcoded values across stages
Boundaries: Configuration only, no business logic
Control: All stages must import from here, enforced by architecture tests

⚠️ WHAT THIS MODULE CANNOT SEE
- Runtime environment differences
- Stage-specific overrides (use get_stage_config for those)
- External service availability

🔥 THE FURNACE PRINCIPLE
- Truth (input): Environment variables, defaults
- Heat (processing): Validation, assembly
- Meaning (output): Typed configuration constants
- Care (delivery): Fail-fast on misconfiguration
"""
from __future__ import annotations

"""Claude Code Pipeline - Shared Constants

Single source of truth for all pipeline configuration.
NO hardcoded values in stage scripts - import from here.

🧠 STAGE FIVE GROUNDING
This module exists to centralize all configuration for the Claude Code pipeline.

Structure: Define → Export → Validate (on import)
Purpose: Prevent configuration drift and hardcoded values across stages
Boundaries: Configuration only, no business logic
Control: All stages must import from here, enforced by architecture tests

⚠️ WHAT THIS MODULE CANNOT SEE
- Runtime environment differences
- Stage-specific overrides (use get_stage_config for those)
- External service availability

🔥 THE FURNACE PRINCIPLE
- Truth (input): Environment variables, defaults
- Heat (processing): Validation, assembly
- Meaning (output): Typed configuration constants
- Care (delivery): Fail-fast on misconfiguration
"""
# Use logging bridge or fallback
try:
    from .logging_bridge import get_logger as _get_logger
except Exception:
    try:
        from truth_forge.core.structured_logging import get_logger as _get_logger
    except Exception:
        import logging
        logging.basicConfig(level=logging.INFO)
        def _get_logger(name: str):
            return logging.getLogger(name)

_LOGGER = _get_logger(__name__)
script_id = "pipelines.claude_code.scripts.shared.constants.py"

import os
from typing import Optional

# =============================================================================
# PROJECT CONFIGURATION
# =============================================================================

PROJECT_ID: str = os.environ.get("BIGQUERY_PROJECT_ID", "flash-clover-464719-g1")
DATASET_ID: str = os.environ.get("BIGQUERY_DATASET", "spine")
PIPELINE_NAME: str = "claude_code"
SOURCE_NAME: str = "claude_code"

# =============================================================================
# TABLE NAMES (without project.dataset prefix)
# =============================================================================

# Stage tables follow pattern: {pipeline}_stage_{N}
TABLE_STAGE_0: str = f"{PIPELINE_NAME}_stage_0"
TABLE_STAGE_1: str = f"{PIPELINE_NAME}_stage_1"
TABLE_STAGE_2: str = f"{PIPELINE_NAME}_stage_2"
TABLE_STAGE_3: str = f"{PIPELINE_NAME}_stage_3"
TABLE_STAGE_4: str = f"{PIPELINE_NAME}_stage_4"
TABLE_STAGE_5: str = f"{PIPELINE_NAME}_stage_5"
TABLE_STAGE_6: str = f"{PIPELINE_NAME}_stage_6"
TABLE_STAGE_7: str = f"{PIPELINE_NAME}_stage_7"
TABLE_STAGE_8: str = f"{PIPELINE_NAME}_stage_8"
TABLE_STAGE_9: str = f"{PIPELINE_NAME}_stage_9"
TABLE_STAGE_10: str = f"{PIPELINE_NAME}_stage_10"
TABLE_STAGE_11: str = f"{PIPELINE_NAME}_stage_11"
TABLE_STAGE_12: str = f"{PIPELINE_NAME}_stage_12"
TABLE_STAGE_13: str = f"{PIPELINE_NAME}_stage_13"
TABLE_STAGE_14: str = f"{PIPELINE_NAME}_stage_14"
TABLE_STAGE_15: str = f"{PIPELINE_NAME}_stage_15"

# Final destination
TABLE_ENTITY_UNIFIED: str = "entity_unified"

# =============================================================================
# ENTITY LEVELS (SPINE hierarchy)
# =============================================================================

LEVEL_TOKEN: int = 1       # L1: Individual tokens/words
LEVEL_SENTENCE: int = 3    # L3: Sentences
LEVEL_MESSAGE: int = 5     # L5: Messages (user/assistant turns)
LEVEL_CONVERSATION: int = 8  # L8: Full conversations/sessions

# =============================================================================
# PROCESSING DEFAULTS
# =============================================================================

DEFAULT_BATCH_SIZE: int = 1000
DEFAULT_CHUNK_SIZE: int = 500
DEFAULT_MAX_RETRIES: int = 3
DEFAULT_RETRY_DELAYS: tuple = (1, 2, 4)  # Exponential backoff seconds
DEFAULT_TIMEOUT_SECONDS: int = 300

# =============================================================================
# EMBEDDING CONFIGURATION
# =============================================================================

EMBEDDING_MODEL: str = "gemini-embedding-001"
EMBEDDING_DIMENSIONS: int = 3072

# =============================================================================
# COST LIMITS (USD)
# =============================================================================

COST_LIMIT_PER_STAGE: float = 5.0
COST_LIMIT_TOTAL: float = 80.0

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_stage_table(stage: int) -> str:
    """Get table name for a specific stage.

    Args:
        stage: Stage number (0-15)

    Returns:
        Table name without project.dataset prefix

    Raises:
        ValueError: If stage is out of range
    """
    if stage == 16:
        return TABLE_ENTITY_UNIFIED
    if not 0 <= stage <= 15:
        raise ValueError(f"Stage must be 0-15 or 16, got {stage}")
    return f"{PIPELINE_NAME}_stage_{stage}"

def get_full_table_id(table_name: str, project: Optional[str] = None, dataset: Optional[str] = None) -> str:
    """Get fully qualified table ID.

    Args:
        table_name: Table name (e.g., "claude_code_stage_0")
        project: Optional project override
        dataset: Optional dataset override

    Returns:
        Fully qualified table ID (project.dataset.table)
    """
    p = project or PROJECT_ID
    d = dataset or DATASET_ID
    return f"{p}.{d}.{table_name}"

# =============================================================================
# VALIDATION
# =============================================================================

def _validate_config() -> None:
    """Validate configuration on import. Fail fast on misconfiguration."""
    if not PROJECT_ID:
        raise ValueError("PROJECT_ID not configured")
    if not DATASET_ID:
        raise ValueError("DATASET_ID not configured")

# Run validation on import
_validate_config()
