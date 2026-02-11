"""Framework Pattern Registry.

This module provides access to the canonical framework patterns that serve
as the ultimate molt sources for all code in the organism.

CANONICAL PATTERNS:
- genesis: THE_DIVIDE, THE_STRUCTURE, THE_CYCLE
- architecture: SERVICE_STRUCTURE, HOLD_PATTERN, BREATHING_INTERFACE
- standards: The 11 canonical standards as validatable rules

Usage:
    from framework.patterns import load_pattern, validate_against_pattern

    # Load a pattern schema
    genesis = load_pattern("genesis")

    # Validate code against a pattern
    result = validate_against_pattern(service_path, "architecture")
"""
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import yaml


PATTERNS_DIR = Path(__file__).parent


@dataclass(slots=True)
class PatternValidation:
    """Result of validating code against a framework pattern."""
    pattern_name: str
    passed: bool
    violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_name": self.pattern_name,
            "passed": self.passed,
            "violations": self.violations,
            "warnings": self.warnings,
        }


def load_pattern(pattern_name: str) -> Dict[str, Any]:
    """Load a framework pattern schema.

    Args:
        pattern_name: One of 'genesis', 'architecture', 'standards'

    Returns:
        Parsed YAML schema as dictionary

    Raises:
        FileNotFoundError: If pattern schema doesn't exist
        ValueError: If pattern name is invalid
    """
    valid_patterns = ["genesis", "architecture", "standards"]
    if pattern_name not in valid_patterns:
        raise ValueError(f"Invalid pattern: {pattern_name}. Must be one of {valid_patterns}")

    schema_path = PATTERNS_DIR / f"{pattern_name}.schema.yaml"
    if not schema_path.exists():
        raise FileNotFoundError(f"Pattern schema not found: {schema_path}")

    with open(schema_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def list_patterns() -> List[str]:
    """List all available framework patterns."""
    return [
        p.stem.replace(".schema", "")
        for p in PATTERNS_DIR.glob("*.schema.yaml")
    ]


def get_pattern_provides(pattern_name: str) -> List[str]:
    """Get what a pattern provides (its key concepts)."""
    pattern = load_pattern(pattern_name)
    return pattern.get("provides", [])


def validate_against_pattern(
    file_path: Path,
    pattern_name: str,
) -> PatternValidation:
    """Validate a file against a framework pattern.

    Args:
        file_path: Path to the file to validate
        pattern_name: Pattern to validate against

    Returns:
        PatternValidation result
    """
    violations = []
    warnings = []

    pattern = load_pattern(pattern_name)
    requirements = pattern.get("requirements", {})

    # Read file content
    if not file_path.exists():
        return PatternValidation(
            pattern_name=pattern_name,
            passed=False,
            violations=[f"File not found: {file_path}"],
        )

    content = file_path.read_text()

    # Check required markers
    if "markers" in requirements:
        for marker in requirements["markers"]:
            if marker not in content:
                violations.append(f"Missing required marker: {marker}")

    # Check required methods (for Python files)
    if file_path.suffix == ".py" and "methods" in requirements:
        for method in requirements["methods"]:
            if f"def {method}" not in content:
                violations.append(f"Missing required method: {method}")

    # Check for MOLT_SOURCE
    if requirements.get("molt_source_required", False):
        if "MOLT_SOURCE" not in content:
            violations.append("Missing MOLT_SOURCE declaration")

    return PatternValidation(
        pattern_name=pattern_name,
        passed=len(violations) == 0,
        violations=violations,
        warnings=warnings,
    )


# Canonical pattern names
GENESIS = "genesis"
ARCHITECTURE = "architecture"
STANDARDS = "standards"

# All patterns
ALL_PATTERNS = [GENESIS, ARCHITECTURE, STANDARDS]
