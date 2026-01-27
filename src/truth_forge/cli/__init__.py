"""CLI - Command Line Interface.

MOLT LINEAGE:
- Source: Truth_Engine/src/truth_forge/cli/__init__.py
- Version: 2.0.0
- Date: 2026-01-26

Command line interface for truth_forge operations.

BIOLOGICAL METAPHOR:
- CLI = Nervous system input
- Commands = Neural signals
- Output = Motor response
"""

from __future__ import annotations

from truth_forge.cli.main import create_parser, main


__all__ = [
    "create_parser",
    "main",
]
