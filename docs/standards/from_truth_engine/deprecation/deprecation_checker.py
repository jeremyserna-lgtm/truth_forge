"""Pylint plugin for enforcing deprecation standards.

This module provides custom pylint checkers to ensure deprecations follow
the project's deprecation standard.

Installation:
    Add to your pylintrc or pyproject.toml:

    [MASTER]
    load-plugins=framework.standards.deprecation.deprecation_checker

    Or in pyproject.toml:

    [tool.pylint.master]
    load-plugins = ["framework.standards.deprecation.deprecation_checker"]

Usage:
    pylint --load-plugins=framework.standards.deprecation.deprecation_checker your_module.py
"""
from __future__ import annotations

"""Pylint plugin for enforcing deprecation standards.

This module provides custom pylint checkers to ensure deprecations follow
the project's deprecation standard.

Installation:
    Add to your pylintrc or pyproject.toml:

    [MASTER]
    load-plugins=framework.standards.deprecation.deprecation_checker

    Or in pyproject.toml:

    [tool.pylint.master]
    load-plugins = ["framework.standards.deprecation.deprecation_checker"]

Usage:
    pylint --load-plugins=framework.standards.deprecation.deprecation_checker your_module.py
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
script_id = "framework.standards.deprecation.deprecation_checker.py"

import re
from typing import TYPE_CHECKING

from astroid import nodes
from pylint.checkers import BaseChecker

if TYPE_CHECKING:
    from pylint.lint import PyLinter

class DeprecationStandardChecker(BaseChecker):
    """Check that deprecations follow the project standard."""

    name = "deprecation-standard"
    priority = -1

    msgs = {
        "W9001": (
            "Deprecation decorator missing 'since' parameter",
            "deprecation-missing-since",
            "All @deprecated decorators must specify the 'since' version.",
        ),
        "W9002": (
            "Deprecation decorator missing 'removal' parameter",
            "deprecation-missing-removal",
            "All @deprecated decorators must specify the 'removal' version.",
        ),
        "W9003": (
            "Deprecation decorator missing 'reason' parameter",
            "deprecation-missing-reason",
            "All @deprecated decorators must explain why code is deprecated.",
        ),
        "W9004": (
            "Deprecation decorator missing 'replacement' parameter",
            "deprecation-missing-replacement",
            "Specify a replacement or explicitly set replacement=None.",
        ),
        "W9005": (
            "Deprecated %s missing docstring deprecation notice",
            "deprecation-missing-docstring",
            "Deprecated code should have '.. deprecated::' in docstring.",
        ),
        "W9006": (
            "Invalid version format '%s' in deprecation",
            "deprecation-invalid-version",
            "Version should follow semver format (e.g., '2.3.0').",
        ),
        "W9007": (
            "Removal version '%s' should be greater than since version '%s'",
            "deprecation-version-order",
            "The removal version must be later than the since version.",
        ),
        "W9010": (
            "Using deprecated %s '%s' (deprecated since %s, removal in %s)",
            "deprecated-usage",
            "Code is using a deprecated function, class, or method.",
        ),
    }

    options = (
        (
            "check-deprecated-usage",
            {
                "default": True,
                "type": "yn",
                "metavar": "<y or n>",
                "help": "Check for usage of deprecated code",
            },
        ),
        (
            "deprecation-min-versions",
            {
                "default": 2,
                "type": "int",
                "metavar": "<int>",
                "help": "Minimum minor versions between since and removal",
            },
        ),
    )

    # Track deprecated items found during analysis
    _deprecated_items: dict[str, dict] = {}

    def visit_functiondef(self, node: nodes.FunctionDef) -> None:
        """Check function/method deprecation decorators."""
        self._check_deprecation_decorator(node, "function")

    def visit_asyncfunctiondef(self, node: nodes.AsyncFunctionDef) -> None:
        """Check async function deprecation decorators."""
        self._check_deprecation_decorator(node, "async function")

    def visit_classdef(self, node: nodes.ClassDef) -> None:
        """Check class deprecation decorators."""
        self._check_deprecation_decorator(node, "class")

    def _check_deprecation_decorator(
        self, node: nodes.FunctionDef | nodes.ClassDef, obj_type: str
    ) -> None:
        """Check if deprecation decorator follows standards."""
        for decorator in node.decorators.nodes if node.decorators else []:
            if not self._is_deprecated_decorator(decorator):
                continue

            # Extract decorator arguments
            args = self._get_decorator_args(decorator)

            # Check required parameters
            if "since" not in args:
                self.add_message("deprecation-missing-since", node=decorator)
            elif not self._is_valid_version(args["since"]):
                self.add_message(
                    "deprecation-invalid-version",
                    node=decorator,
                    args=(args["since"],),
                )

            if "removal" not in args:
                self.add_message("deprecation-missing-removal", node=decorator)
            elif not self._is_valid_version(args["removal"]):
                self.add_message(
                    "deprecation-invalid-version",
                    node=decorator,
                    args=(args["removal"],),
                )

            if "reason" not in args:
                self.add_message("deprecation-missing-reason", node=decorator)

            # Check version ordering
            if "since" in args and "removal" in args:
                if self._is_valid_version(args["since"]) and self._is_valid_version(
                    args["removal"]
                ):
                    if not self._version_greater(args["removal"], args["since"]):
                        self.add_message(
                            "deprecation-version-order",
                            node=decorator,
                            args=(args["removal"], args["since"]),
                        )

            # Check docstring has deprecation notice
            if node.doc_node:
                docstring = node.doc_node.value
                if ".. deprecated::" not in docstring.lower():
                    self.add_message(
                        "deprecation-missing-docstring",
                        node=node,
                        args=(obj_type,),
                    )
            else:
                self.add_message(
                    "deprecation-missing-docstring",
                    node=node,
                    args=(obj_type,),
                )

            # Track this deprecated item
            self._deprecated_items[node.name] = {
                "since": args.get("since", "unknown"),
                "removal": args.get("removal", "unknown"),
                "type": obj_type,
            }

    def _is_deprecated_decorator(self, decorator: nodes.NodeNG) -> bool:
        """Check if decorator is a deprecation decorator."""
        if isinstance(decorator, nodes.Call):
            func = decorator.func
            if isinstance(func, nodes.Name):
                return func.name in ("deprecated", "pending_deprecation")
            if isinstance(func, nodes.Attribute):
                return func.attrname in ("deprecated", "pending_deprecation")
        elif isinstance(decorator, nodes.Name):
            return decorator.name in ("deprecated", "pending_deprecation")
        return False

    def _get_decorator_args(self, decorator: nodes.NodeNG) -> dict[str, str]:
        """Extract arguments from decorator call."""
        args = {}
        if isinstance(decorator, nodes.Call):
            # Handle keyword arguments
            for keyword in decorator.keywords:
                if keyword.arg and isinstance(keyword.value, nodes.Const):
                    args[keyword.arg] = keyword.value.value
        return args

    def _is_valid_version(self, version: str) -> bool:
        """Check if version follows semver format."""
        pattern = r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$"
        return bool(re.match(pattern, str(version)))

    def _version_greater(self, v1: str, v2: str) -> bool:
        """Check if v1 > v2 using semver comparison."""
        try:

            def parse(v: str) -> tuple[int, ...]:
                # Strip any pre-release suffix for comparison
                base = v.split("-")[0]
                return tuple(int(x) for x in base.split("."))

            return parse(v1) > parse(v2)
        except (ValueError, AttributeError):
            return False

class DeprecatedUsageChecker(BaseChecker):
    """Check for usage of deprecated code."""

    name = "deprecated-usage"
    priority = -1

    msgs = {
        "W9010": (
            "Using deprecated %s '%s'",
            "deprecated-usage",
            "Code is using a deprecated function, class, or method.",
        ),
    }

    # Known deprecated items (can be configured or detected)
    _known_deprecated: dict[str, dict] = {}

    def visit_call(self, node: nodes.Call) -> None:
        """Check if a call invokes deprecated code."""
        func_name = None

        if isinstance(node.func, nodes.Name):
            func_name = node.func.name
        elif isinstance(node.func, nodes.Attribute):
            func_name = node.func.attrname

        if func_name and func_name in self._known_deprecated:
            info = self._known_deprecated[func_name]
            self.add_message(
                "deprecated-usage",
                node=node,
                args=(info.get("type", "function"), func_name),
            )

def register(linter: PyLinter) -> None:
    """Register the checker with pylint."""
    linter.register_checker(DeprecationStandardChecker(linter))
    linter.register_checker(DeprecatedUsageChecker(linter))
