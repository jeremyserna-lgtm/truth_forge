"""Claude Code Pipeline - Logging bridge.

Uses Primitive.core structured logging when available, otherwise
central_services. All stages use this module for consistent logging.

OPERATIONAL_STANDARDS: Use structured logging (event names + kwargs).
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root on path before any Primitive/src imports
_br = Path(__file__).resolve()
_scripts_dir = _br.parent.parent
_pipeline_dir = _scripts_dir.parent
_project_root = _pipeline_dir.parent.parent
_src_path = _project_root / "src"
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

try:
    from truth_forge.core.structured_logging import (
        get_logger,
        bind_context,
        set_run_id,
    )
    from truth_forge.core._core_utils import get_current_run_id
    _USE_PRIMITIVE = True
except Exception:
    # Fallback: use standard logging and uuid for run_id
    import logging
    import uuid
    logging.basicConfig(level=logging.INFO)
    
    def get_logger(name: str):
        return logging.getLogger(name)
    
    def get_current_run_id() -> str:
        return f"run_{uuid.uuid4().hex[:12]}"

    def bind_context(**kwargs: object) -> None:
        pass

    def set_run_id(_: str) -> None:
        pass

    _USE_PRIMITIVE = False


def ensure_stage_logging_context(
    stage: int,
    run_id: str,
    pipeline_name: str,
) -> None:
    """Set run_id and bind stage/pipeline context for structured logging."""
    if _USE_PRIMITIVE:
        set_run_id(run_id)
        bind_context(stage=stage, pipeline=pipeline_name)
