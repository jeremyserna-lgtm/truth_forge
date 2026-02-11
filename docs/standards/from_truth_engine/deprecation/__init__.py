"""Deprecation standard tooling.

Usage:
    from framework.standards.deprecation import deprecated, warn_deprecated_parameter

    @deprecated(
        since="2.3.0",
        removal="3.0.0",
        reason="Replaced by better implementation",
        replacement="new_function"
    )
    def old_function():
        pass
"""
from __future__ import annotations

"""Deprecation standard tooling.

Usage:
    from framework.standards.deprecation import deprecated, warn_deprecated_parameter

    @deprecated(
        since="2.3.0",
        removal="3.0.0",
        reason="Replaced by better implementation",
        replacement="new_function"
    )
    def old_function():
        pass
"""
try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)


try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)
script_id = "framework.standards.deprecation.__init__.py"

from .deprecation_utils import (
    ModuleDeprecationWarning,
    deprecated,
    get_deprecation_info,
    is_deprecated,
    pending_deprecation,
    warn_deprecated_parameter,
)

__all__ = [
    "deprecated",
    "pending_deprecation",
    "warn_deprecated_parameter",
    "get_deprecation_info",
    "is_deprecated",
    "ModuleDeprecationWarning",
]
