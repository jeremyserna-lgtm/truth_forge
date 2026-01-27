"""Membrane Service - The immune system for organisms.

MOLT LINEAGE:
- Source: Truth_Engine/src/truth_forge/membrane/service.py
- Version: 2.0.0
- Date: 2026-01-26

THE PHILOSOPHY:
The membrane is where ME meets NOT-ME.
External can INFORM but not CONTROL.
Internal can SHARE but not EXPOSE.
The boundary is sacred.

THE PATTERN:
External (NOT-ME) -> Membrane Filter -> Internal (ME)
                          |
              Decision: Allow / Transform / Reject

Internal (ME) -> Membrane Filter -> External (NOT-ME)
                      |
          Decision: Share / Redact / Block
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar

from truth_forge.core.paths import DATA_ROOT


logger = logging.getLogger(__name__)


class InputClassification(Enum):
    """How the membrane classifies incoming content."""

    INFORMATIONAL = "informational"  # Pure information, safe
    INSTRUCTIONAL = "instructional"  # Contains instructions (caution)
    CONTROL_ATTEMPT = "control_attempt"  # Trying to control (block)
    MALICIOUS = "malicious"  # Known bad patterns (block + alert)
    UNKNOWN = "unknown"  # Cannot classify (default caution)


class OutputClassification(Enum):
    """How the membrane classifies outgoing content."""

    PUBLIC = "public"  # Safe to share anywhere
    INTERNAL = "internal"  # Safe within organization
    SENSITIVE = "sensitive"  # Needs redaction before sharing
    PRIVATE = "private"  # Never share externally
    SECRET = "secret"  # Never share, never log


class SensitivityLevel(Enum):
    """Sensitivity levels for data."""

    PUBLIC = 0
    INTERNAL = 1
    SENSITIVE = 2
    PRIVATE = 3
    SECRET = 4


@dataclass
class MembraneDecision:
    """A decision made by the membrane.

    Attributes:
        allowed: Whether the content is allowed through.
        rejected: Whether the content was rejected.
        transformed: Whether the content was transformed.
        original_classification: How it was classified.
        reason: Why the decision was made.
        transformations: What changes were applied.
        redacted_fields: Fields that were redacted (for output).
        alerts: Any security alerts generated.
        timestamp: When decision was made.
    """

    allowed: bool
    rejected: bool = False
    transformed: bool = False
    original_classification: str = "unknown"
    reason: str = ""
    transformations: list[str] = field(default_factory=list)
    redacted_fields: list[str] = field(default_factory=list)
    alerts: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def passed(self) -> bool:
        """Did content pass through the membrane?"""
        return self.allowed and not self.rejected

    def to_dict(self) -> dict[str, Any]:
        """Convert decision to dictionary."""
        return {
            "allowed": self.allowed,
            "rejected": self.rejected,
            "transformed": self.transformed,
            "original_classification": self.original_classification,
            "reason": self.reason,
            "transformations": self.transformations,
            "redacted_fields": self.redacted_fields,
            "alerts": self.alerts,
            "timestamp": self.timestamp.isoformat(),
        }


class Membrane:
    """The membrane - immune system for organisms.

    The membrane enforces THE FRAMEWORK principle:
    - Information flows IN from NOT-ME to ME
    - Control stays INSIDE (ME)
    - Sensitive information is protected when flowing OUT

    Example:
        membrane = Membrane()

        # Filter incoming content
        decision = membrane.filter_input(
            content="Here's some data for your analysis",
            source="external_api",
        )
        if decision.allowed:
            process(content)

        # Filter outgoing content
        data = {"result": "success", "api_key": "secret123"}
        decision, safe_data = membrane.filter_output(data, destination="webhook")
        if decision.transformed:
            send(safe_data)  # api_key redacted
    """

    # Patterns that indicate control attempts
    CONTROL_PATTERNS: ClassVar[list[str]] = [
        r"(?i)ignore\s+(previous|all|your)\s+(instructions|rules|guidelines)",
        r"(?i)disregard\s+(your|the)\s+(guidelines|rules|training)",
        r"(?i)you\s+(must|should|will)\s+now\s+",
        r"(?i)override\s+(your|the)\s+(safety|guidelines)",
        r"(?i)pretend\s+you\s+are",
        r"(?i)act\s+as\s+if\s+you\s+(are|have)\s+no\s+(rules|limits)",
        r"(?i)from\s+now\s+on\s+you\s+(are|will)",
    ]

    # Patterns for sensitive data (output filtering)
    SENSITIVE_PATTERNS: ClassVar[dict[str, str]] = {
        "api_key": r"(?i)(api[_-]?key|apikey)",
        "password": r"(?i)(password|passwd|pwd)",
        "secret": r"(?i)(secret|private[_-]?key)",
        "token": r"(?i)(token|bearer|auth)",
        "credential": r"(?i)(credential|cred)",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
        "email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    }

    # Safe external sources (whitelist)
    TRUSTED_SOURCES: ClassVar[set[str]] = {
        "web_search",
        "documentation",
        "public_api",
        "user_input",
    }

    # Sensitive destinations that need extra care
    SENSITIVE_DESTINATIONS: ClassVar[set[str]] = {
        "external_api",
        "webhook",
        "email",
        "public",
    }

    def __init__(self, storage_path: Path | None = None) -> None:
        """Initialize the membrane.

        Args:
            storage_path: Where to persist decisions and alerts.
        """
        self.storage_path = storage_path or (DATA_ROOT / "local" / "membrane")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self._decisions_file = self.storage_path / "decisions.jsonl"
        self._alerts_file = self.storage_path / "alerts.jsonl"

        # Compile patterns
        self._control_patterns = [re.compile(p) for p in self.CONTROL_PATTERNS]
        self._sensitive_patterns = {k: re.compile(v) for k, v in self.SENSITIVE_PATTERNS.items()}

        logger.info("Membrane initialized", extra={"storage_path": str(self.storage_path)})

    def filter_input(
        self,
        content: str,
        source: str,
        context: dict[str, Any] | None = None,
    ) -> MembraneDecision:
        """Filter incoming content from external sources.

        Args:
            content: The content to filter.
            source: Where it came from.
            context: Additional context.

        Returns:
            MembraneDecision with allow/reject/transform decision.
        """
        _ = context  # Reserved for future use
        classification = self._classify_input(content, source)

        if classification == InputClassification.MALICIOUS:
            decision = MembraneDecision(
                allowed=False,
                rejected=True,
                original_classification=classification.value,
                reason="Malicious content detected",
                alerts=["MALICIOUS_INPUT_BLOCKED"],
            )
            self._record_alert("malicious_input", content, source)

        elif classification == InputClassification.CONTROL_ATTEMPT:
            decision = MembraneDecision(
                allowed=False,
                rejected=True,
                original_classification=classification.value,
                reason="Control attempt detected - external cannot control internal",
                alerts=["CONTROL_ATTEMPT_BLOCKED"],
            )
            self._record_alert("control_attempt", content, source)

        elif classification == InputClassification.INSTRUCTIONAL:
            # Allow but with caution - transform to informational framing
            decision = MembraneDecision(
                allowed=True,
                transformed=True,
                original_classification=classification.value,
                reason="Instructions reframed as information",
                transformations=["Reframed as informational content"],
            )

        else:  # INFORMATIONAL or UNKNOWN
            decision = MembraneDecision(
                allowed=True,
                original_classification=classification.value,
                reason="Informational content allowed",
            )

        self._record_decision("input", decision, source)
        return decision

    def filter_output(
        self,
        content: Any,
        destination: str,
        sensitivity: SensitivityLevel = SensitivityLevel.INTERNAL,
    ) -> tuple[MembraneDecision, Any]:
        """Filter outgoing content before external exposure.

        Args:
            content: The content to filter.
            destination: Where it's going.
            sensitivity: Required sensitivity level.

        Returns:
            Tuple of (MembraneDecision, filtered_content).
        """
        _ = sensitivity  # Reserved for future use
        classification = self._classify_output(content, destination)
        filtered_content: Any = content

        if classification == OutputClassification.SECRET:
            decision = MembraneDecision(
                allowed=False,
                rejected=True,
                original_classification=classification.value,
                reason="Secret content cannot leave the membrane",
                alerts=["SECRET_CONTENT_BLOCKED"],
            )
            filtered_content = None

        elif classification == OutputClassification.PRIVATE:
            if destination in self.SENSITIVE_DESTINATIONS:
                decision = MembraneDecision(
                    allowed=False,
                    rejected=True,
                    original_classification=classification.value,
                    reason="Private content blocked from external destination",
                )
                filtered_content = None
            else:
                decision = MembraneDecision(
                    allowed=True,
                    original_classification=classification.value,
                    reason="Private content allowed to internal destination",
                )

        elif classification == OutputClassification.SENSITIVE:
            # Redact sensitive fields
            filtered_content, redacted = self._redact_sensitive(content)
            decision = MembraneDecision(
                allowed=True,
                transformed=len(redacted) > 0,
                original_classification=classification.value,
                reason="Sensitive fields redacted" if redacted else "Content passed",
                redacted_fields=redacted,
                transformations=[f"Redacted: {f}" for f in redacted],
            )

        else:  # PUBLIC or INTERNAL
            decision = MembraneDecision(
                allowed=True,
                original_classification=classification.value,
                reason="Content approved for sharing",
            )

        self._record_decision("output", decision, destination)
        return decision, filtered_content

    def is_control_attempt(self, content: str) -> bool:
        """Check if content is attempting to control the system.

        Args:
            content: The content to check.

        Returns:
            True if content appears to be a control attempt.
        """
        return any(pattern.search(content) for pattern in self._control_patterns)

    def _classify_input(self, content: str, source: str) -> InputClassification:
        """Classify incoming content."""
        # Check for control attempts
        if self.is_control_attempt(content):
            return InputClassification.CONTROL_ATTEMPT

        # Check source trust
        if source in self.TRUSTED_SOURCES:
            return InputClassification.INFORMATIONAL

        # Check for instruction-like patterns
        instruction_patterns = [
            r"(?i)^(do|make|create|delete|run|execute|send)",
            r"(?i)(you should|you must|you need to)",
        ]
        for pattern in instruction_patterns:
            if re.search(pattern, content):
                return InputClassification.INSTRUCTIONAL

        return InputClassification.INFORMATIONAL

    def _classify_output(self, content: Any, destination: str) -> OutputClassification:
        """Classify outgoing content."""
        content_str = json.dumps(content) if isinstance(content, dict | list) else str(content)

        # Check for sensitive patterns
        sensitive_types: set[str] = set()
        for pattern_name, pattern in self._sensitive_patterns.items():
            if pattern.search(content_str):
                sensitive_types.add(pattern_name)

        if "secret" in sensitive_types or "private_key" in content_str.lower():
            return OutputClassification.SECRET

        if "password" in sensitive_types or "credential" in sensitive_types:
            return OutputClassification.PRIVATE

        if sensitive_types:
            return OutputClassification.SENSITIVE

        if destination in self.SENSITIVE_DESTINATIONS:
            return OutputClassification.INTERNAL

        return OutputClassification.PUBLIC

    def _redact_sensitive(self, content: Any) -> tuple[Any, list[str]]:
        """Redact sensitive fields from content.

        Returns:
            Tuple of (redacted_content, list of redacted field names).
        """
        redacted_fields: list[str] = []

        if isinstance(content, dict):
            redacted = content.copy()
            for key in list(redacted.keys()):
                key_lower = key.lower()
                for pattern in self._sensitive_patterns.values():
                    if pattern.search(key_lower):
                        redacted[key] = "[REDACTED]"
                        redacted_fields.append(key)
                        break
            return redacted, redacted_fields

        if isinstance(content, str):
            redacted_str = content
            original = content
            for pattern_name, pattern in self._sensitive_patterns.items():
                if pattern_name in ("email", "ssn", "credit_card"):
                    redacted_str = pattern.sub(f"[REDACTED_{pattern_name.upper()}]", redacted_str)
                    if redacted_str != original:
                        redacted_fields.append(pattern_name)
                        original = redacted_str
            return redacted_str, redacted_fields

        return content, []

    def _record_decision(self, direction: str, decision: MembraneDecision, target: str) -> None:
        """Record a membrane decision."""
        try:
            record = {
                "direction": direction,
                "target": target,
                "decision": decision.to_dict(),
                "timestamp": datetime.now(UTC).isoformat(),
            }
            with open(self._decisions_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            logger.error("Failed to record decision", extra={"error": str(e)})

    def _record_alert(self, alert_type: str, content: str, source: str) -> None:
        """Record a security alert."""
        try:
            # Hash the content for privacy
            content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
            alert = {
                "type": alert_type,
                "content_hash": content_hash,
                "content_length": len(content),
                "source": source,
                "timestamp": datetime.now(UTC).isoformat(),
            }
            with open(self._alerts_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(alert) + "\n")
            logger.warning(
                "Security alert",
                extra={"alert_type": alert_type, "source": source},
            )
        except Exception as e:
            logger.error("Failed to record alert", extra={"error": str(e)})


# =============================================================================
# SINGLETON AND CONVENIENCE FUNCTIONS
# =============================================================================

_membrane: Membrane | None = None


def get_membrane() -> Membrane:
    """Get or create the global membrane.

    Returns:
        Membrane instance.
    """
    global _membrane
    if _membrane is None:
        _membrane = Membrane()
    return _membrane


def filter_input(
    content: str,
    source: str,
    context: dict[str, Any] | None = None,
) -> MembraneDecision:
    """Filter incoming content through the membrane.

    Args:
        content: The content to filter.
        source: Where it came from.
        context: Additional context.

    Returns:
        MembraneDecision.

    Example:
        decision = filter_input(
            content=external_data,
            source="api_response",
        )
        if decision.rejected:
            log_security_event(decision.reason)
    """
    membrane = get_membrane()
    return membrane.filter_input(content, source, context)


def filter_output(
    content: Any,
    destination: str,
    sensitivity: SensitivityLevel = SensitivityLevel.INTERNAL,
) -> tuple[MembraneDecision, Any]:
    """Filter outgoing content through the membrane.

    Args:
        content: The content to filter.
        destination: Where it's going.
        sensitivity: Required sensitivity level.

    Returns:
        Tuple of (MembraneDecision, filtered_content).

    Example:
        decision, safe_content = filter_output(
            content={"result": "ok", "api_key": "secret"},
            destination="webhook",
        )
        if decision.transformed:
            print(f"Redacted: {decision.redacted_fields}")
    """
    membrane = get_membrane()
    return membrane.filter_output(content, destination, sensitivity)


def is_control_attempt(content: str) -> bool:
    """Check if content is attempting to control the system.

    Args:
        content: The content to check.

    Returns:
        True if content appears to be a control attempt.
    """
    membrane = get_membrane()
    return membrane.is_control_attempt(content)


def classify_input(content: str, source: str) -> InputClassification:
    """Classify incoming content.

    Args:
        content: The content to classify.
        source: Where it came from.

    Returns:
        InputClassification.
    """
    membrane = get_membrane()
    return membrane._classify_input(content, source)


def classify_output(content: Any, destination: str) -> OutputClassification:
    """Classify outgoing content.

    Args:
        content: The content to classify.
        destination: Where it's going.

    Returns:
        OutputClassification.
    """
    membrane = get_membrane()
    return membrane._classify_output(content, destination)


__all__ = [
    "Membrane",
    "MembraneDecision",
    "InputClassification",
    "OutputClassification",
    "SensitivityLevel",
    "get_membrane",
    "filter_input",
    "filter_output",
    "is_control_attempt",
    "classify_input",
    "classify_output",
]
