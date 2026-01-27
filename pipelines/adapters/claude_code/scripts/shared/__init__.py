"""Claude Code Pipeline - Shared Module

Centralized constants, utilities, and configuration for all pipeline stages.
Following the Universal Pipeline Pattern and Definition of Done standards.

Usage:
    from shared import (
        PROJECT_ID, DATASET_ID, PIPELINE_NAME,
        get_stage_table, get_logger, get_current_run_id,
        retry_with_backoff, validate_input_table_exists,
    )
"""
from __future__ import annotations

"""Claude Code Pipeline - Shared Module

Centralized constants, utilities, and configuration for all pipeline stages.
Following the Universal Pipeline Pattern and Definition of Done standards.

Usage:
    from shared import (
        PROJECT_ID, DATASET_ID, PIPELINE_NAME,
        get_stage_table, get_logger, get_current_run_id,
        retry_with_backoff, validate_input_table_exists,
    )
"""
# Use logging bridge for consistent logging across all environments
try:
    from .logging_bridge import get_logger as _get_logger
except Exception:
    # Fallback if logging_bridge not available
    try:
        from truth_forge.core.structured_logging import get_logger as _get_logger
    except Exception:
        # Final fallback: create a simple logger
        import logging
        logging.basicConfig(level=logging.INFO)
        def _get_logger(name: str):
            return logging.getLogger(name)

_LOGGER = _get_logger(__name__)
script_id = "pipelines.claude_code.scripts.shared.__init__.py"

from .constants import (
    # Project configuration
    PROJECT_ID,
    DATASET_ID,
    PIPELINE_NAME,
    SOURCE_NAME,
    # Table names
    TABLE_STAGE_0,
    TABLE_STAGE_1,
    TABLE_STAGE_2,
    TABLE_STAGE_3,
    TABLE_STAGE_4,
    TABLE_STAGE_5,
    TABLE_STAGE_6,
    TABLE_STAGE_7,
    TABLE_STAGE_8,
    TABLE_STAGE_9,
    TABLE_STAGE_10,
    TABLE_STAGE_11,
    TABLE_STAGE_12,
    TABLE_STAGE_13,
    TABLE_STAGE_14,
    TABLE_STAGE_15,
    TABLE_ENTITY_UNIFIED,
    # Entity levels
    LEVEL_TOKEN,
    LEVEL_SENTENCE,
    LEVEL_MESSAGE,
    LEVEL_CONVERSATION,
    # Utility functions
    get_stage_table,
    get_full_table_id,
)

from .config import (
    get_config,
    get_stage_config,
)

from .utilities import (
    retry_with_backoff,
    is_retryable_error,
    validate_input_table_exists,
    validate_gate_no_null_identity,
    verify_row_counts,
    create_fingerprint,
    get_pipeline_hold2_path,
)

__all__ = [
    # Constants
    "PROJECT_ID",
    "DATASET_ID",
    "PIPELINE_NAME",
    "SOURCE_NAME",
    # Tables
    "TABLE_STAGE_0",
    "TABLE_STAGE_1",
    "TABLE_STAGE_2",
    "TABLE_STAGE_3",
    "TABLE_STAGE_4",
    "TABLE_STAGE_5",
    "TABLE_STAGE_6",
    "TABLE_STAGE_7",
    "TABLE_STAGE_8",
    "TABLE_STAGE_9",
    "TABLE_STAGE_10",
    "TABLE_STAGE_11",
    "TABLE_STAGE_12",
    "TABLE_STAGE_13",
    "TABLE_STAGE_14",
    "TABLE_STAGE_15",
    "TABLE_ENTITY_UNIFIED",
    # Levels
    "LEVEL_TOKEN",
    "LEVEL_SENTENCE",
    "LEVEL_MESSAGE",
    "LEVEL_CONVERSATION",
    # Functions
    "get_stage_table",
    "get_full_table_id",
    "get_config",
    "get_stage_config",
    "retry_with_backoff",
    "is_retryable_error",
    "validate_input_table_exists",
    "validate_gate_no_null_identity",
    "verify_row_counts",
    "create_fingerprint",
    "get_pipeline_hold2_path",
]
