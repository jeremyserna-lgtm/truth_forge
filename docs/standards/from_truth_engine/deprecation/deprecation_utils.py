"""Deprecation utilities for standardized code deprecation.

This module provides decorators and helpers for marking code as deprecated
with consistent metadata, warnings, and documentation.

Example:
    >>> from framework.standards.deprecation import deprecated
    >>> @deprecated(
    ...     since="2.3.0",
    ...     removal="3.0.0",
    ...     reason="Replaced by faster implementation",
    ...     replacement="new_function"
    ... )
    ... def old_function():
    ...     pass
"""
from __future__ import annotations

"""Deprecation utilities for standardized code deprecation.

This module provides decorators and helpers for marking code as deprecated
with consistent metadata, warnings, and documentation.

Example:
    >>> from framework.standards.deprecation import deprecated
    >>> @deprecated(
    ...     since="2.3.0",
    ...     removal="3.0.0",
    ...     reason="Replaced by faster implementation",
    ...     replacement="new_function"
    ... )
    ... def old_function():
    ...     pass
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
script_id = "framework.standards.deprecation.deprecation_utils.py"

import functools
import warnings
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])

class ModuleDeprecationWarning(DeprecationWarning):
    """Warning for deprecated modules."""

    pass

def deprecated(
    since: str,
    removal: str,
    reason: str,
    replacement: str | None = None,
    *,
    warning_category: type[Warning] = DeprecationWarning,
    stacklevel: int = 2,
) -> Callable[[F], F]:
    """Mark a function, method, or class as deprecated.

    Args:
        since: Version when the deprecation was introduced (e.g., "2.3.0")
        removal: Version when the code will be removed (e.g., "3.0.0")
        reason: Explanation of why the code is deprecated
        replacement: Name of the replacement to use (None if no replacement)
        warning_category: The warning class to use (default: DeprecationWarning)
        stacklevel: Stack level for the warning (default: 2)

    Returns:
        A decorator that wraps the function/class with deprecation behavior.

    Example:
        >>> @deprecated(
        ...     since="2.3.0",
        ...     removal="3.0.0",
        ...     reason="O(n²) complexity",
        ...     replacement="process_items_v2"
        ... )
        ... def process_items(items):
        ...     return [x * 2 for x in items]
    """

    def decorator(obj: F) -> F:
        obj_name = getattr(obj, "__name__", str(obj))

        replacement_text = (
            f" Use '{replacement}' instead." if replacement else ""
        )

        message = (
            f"{obj_name} is deprecated since version {since} and will be "
            f"removed in version {removal}. Reason: {reason}.{replacement_text}"
        )

        if isinstance(obj, type):
            # Class deprecation
            original_init = obj.__init__

            @functools.wraps(original_init)
            def new_init(self: Any, *args: Any, **kwargs: Any) -> None:
                warnings.warn(message, warning_category, stacklevel=stacklevel)
                original_init(self, *args, **kwargs)

            obj.__init__ = new_init  # type: ignore[method-assign]

            # Store deprecation metadata on the class
            obj._deprecation_info = {  # type: ignore[attr-defined]
                "since": since,
                "removal": removal,
                "reason": reason,
                "replacement": replacement,
            }

            return obj
        else:
            # Function/method deprecation
            @functools.wraps(obj)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                warnings.warn(message, warning_category, stacklevel=stacklevel)
                return obj(*args, **kwargs)

            # Store deprecation metadata
            wrapper._deprecation_info = {  # type: ignore[attr-defined]
                "since": since,
                "removal": removal,
                "reason": reason,
                "replacement": replacement,
            }

            return wrapper  # type: ignore[return-value]

    return decorator

def warn_deprecated_parameter(
    param: str,
    since: str,
    removal: str,
    replacement: str | None = None,
    *,
    warning_category: type[Warning] = DeprecationWarning,
    stacklevel: int = 3,
) -> None:
    """Emit a deprecation warning for a deprecated parameter.

    Call this at the beginning of a function when a deprecated parameter
    is used with a non-default value.

    Args:
        param: Name of the deprecated parameter
        since: Version when the parameter was deprecated
        removal: Version when the parameter will be removed
        replacement: Name of the replacement parameter (if any)
        warning_category: The warning class to use
        stacklevel: Stack level for the warning (default: 3 for typical usage)

    Example:
        >>> def fetch_data(url, timeout=30, verify_ssl=None):
        ...     if verify_ssl is not None:
        ...         warn_deprecated_parameter(
        ...             param="verify_ssl",
        ...             since="2.3.0",
        ...             removal="3.0.0",
        ...             replacement="ssl_context"
        ...         )
        ...     # rest of implementation
    """
    replacement_text = f" Use '{replacement}' instead." if replacement else ""

    message = (
        f"Parameter '{param}' is deprecated since version {since} and will be "
        f"removed in version {removal}.{replacement_text}"
    )

    warnings.warn(message, warning_category, stacklevel=stacklevel)

def pending_deprecation(
    since: str,
    deprecation_version: str,
    reason: str,
    replacement: str | None = None,
) -> Callable[[F], F]:
    """Mark code that will be deprecated in a future version.

    Use this for code that isn't deprecated yet but will be in the next
    minor version. This uses PendingDeprecationWarning which is hidden
    by default.

    Args:
        since: Current version (when this notice was added)
        deprecation_version: Version when this will become deprecated
        reason: Explanation of why this will be deprecated
        replacement: Name of the replacement to use

    Example:
        >>> @pending_deprecation(
        ...     since="2.2.0",
        ...     deprecation_version="2.3.0",
        ...     reason="Moving to async API",
        ...     replacement="async_process"
        ... )
        ... def sync_process(data):
        ...     pass
    """

    def decorator(obj: F) -> F:
        obj_name = getattr(obj, "__name__", str(obj))
        replacement_text = (
            f" Use '{replacement}' instead." if replacement else ""
        )

        message = (
            f"{obj_name} will be deprecated in version {deprecation_version}. "
            f"Reason: {reason}.{replacement_text}"
        )

        if isinstance(obj, type):
            original_init = obj.__init__

            @functools.wraps(original_init)
            def new_init(self: Any, *args: Any, **kwargs: Any) -> None:
                warnings.warn(message, PendingDeprecationWarning, stacklevel=2)
                original_init(self, *args, **kwargs)

            obj.__init__ = new_init  # type: ignore[method-assign]
            return obj
        else:

            @functools.wraps(obj)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                warnings.warn(message, PendingDeprecationWarning, stacklevel=2)
                return obj(*args, **kwargs)

            return wrapper  # type: ignore[return-value]

    return decorator

def get_deprecation_info(obj: Any) -> dict[str, Any] | None:
    """Get deprecation metadata from a decorated object.

    Args:
        obj: A function, method, or class that may be deprecated

    Returns:
        Dictionary with deprecation info, or None if not deprecated.

    Example:
        >>> @deprecated(since="2.0.0", removal="3.0.0", reason="test", replacement="new_fn")
        ... def old_fn():
        ...     pass
        >>> info = get_deprecation_info(old_fn)
        >>> info["since"]
        '2.0.0'
    """
    return getattr(obj, "_deprecation_info", None)

def is_deprecated(obj: Any) -> bool:
    """Check if an object is marked as deprecated.

    Args:
        obj: A function, method, or class to check

    Returns:
        True if the object is deprecated, False otherwise.
    """
    return get_deprecation_info(obj) is not None
