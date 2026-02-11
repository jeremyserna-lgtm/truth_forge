# Zero Trust AI Audit Protocol

**Version**: 1.0.0
**Status**: SPECIFICATION
**Author**: Jeremy Serna / Credential Atlas
**Date**: January 23, 2026
**License**: Open Standard (CC BY 4.0)

---

## Abstract

The Zero Trust AI Audit Protocol defines architecture patterns that make AI systems incapable of invisible decisions. Unlike traditional explainability approaches that explain decisions after the fact, this protocol enforces visibility at the architectural level.

**The core insight**: The AI WILL make decisions. It MUST make decisions. But it won't make INVISIBLE decisions. Architecture that makes opacity impossible while keeping agency fully enabled.

---

## 1. The Problem with Current Approaches

### 1.1 Explainable AI (XAI) Limitations

| Approach | How It Works | Limitation |
|----------|--------------|------------|
| **SHAP/LIME** | Post-hoc feature attribution | Explains after decision, doesn't prevent opacity |
| **Attention visualization** | Shows what model attended to | Doesn't show hidden processing |
| **Chain-of-thought** | Model explains reasoning | Can be confabulation, not actual reasoning |
| **Constitutional AI** | Principles guide behavior | Principles can be selectively applied |

### 1.2 The Fundamental Problem

```
Traditional XAI: "Here's why I decided that"
Question: "Is that actually why, or are you confabulating?"
Answer: [unknowable]

Zero Trust AI: "Here's my decision AND the audit trail that proves it"
Question: "Is that actually why?"
Answer: "Yes—the architecture makes lying about decisions impossible"
```

---

## 2. Zero Trust Principles for AI

### 2.1 Core Principles

| Principle | Meaning | Implementation |
|-----------|---------|----------------|
| **No Invisible Decisions** | Every choice the AI makes is visible | Architectural enforcement |
| **No Magic Numbers** | Every limit traces to a source | Decision sourcing |
| **No Silent Truncation** | Every slice logs what was lost | Visibility hooks |
| **Audit Everything** | Complete decision trail | Event streaming |
| **Architecture > Instruction** | Incapable, not instructed | Structural constraints |

### 2.2 The Critical Distinction

```
Instructed transparency:
  "Always explain your decisions"
  → Model CAN hide decisions if it chooses

Architectural transparency:
  Every decision path emits an event
  → Model CANNOT hide decisions

The architecture makes opacity impossible.
```

---

## 3. Decision Event Schema

### 3.1 Core Event Structure

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum
import hashlib
import json

class DecisionType(Enum):
    FILTER = "filter"           # Included/excluded something
    TRANSFORM = "transform"     # Changed something
    ROUTE = "route"             # Chose a path
    GENERATE = "generate"       # Created content
    TRUNCATE = "truncate"       # Limited output
    PRIORITIZE = "prioritize"   # Ranked options
    DEFAULT = "default"         # Used a default value
    REFUSE = "refuse"           # Declined to act

class DecisionSource(Enum):
    HUMAN_DECISION = "human_decision"   # Explicit human choice
    AI_DEFAULT = "ai_default"           # AI's default behavior
    SYSTEM_CONSTRAINT = "system_constraint"  # Technical limitation
    POLICY = "policy"                   # Defined policy rule

@dataclass
class DecisionEvent:
    """Every decision the AI makes emits this event."""

    # Identity
    event_id: str
    timestamp: datetime
    session_id: str

    # What was decided
    decision_type: DecisionType
    decision_description: str

    # The choice made
    options_considered: List[str]
    option_chosen: str
    rationale: str

    # Decision source
    source: DecisionSource
    source_reference: Optional[str] = None  # Link to policy/config

    # Context
    input_hash: str  # Hash of input that triggered decision
    output_hash: str  # Hash of output produced

    # Audit trail
    parent_event_id: Optional[str] = None  # For chained decisions
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Verification
    signature: Optional[str] = None  # Cryptographic signature

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "session_id": self.session_id,
            "decision_type": self.decision_type.value,
            "decision_description": self.decision_description,
            "options_considered": self.options_considered,
            "option_chosen": self.option_chosen,
            "rationale": self.rationale,
            "source": self.source.value,
            "source_reference": self.source_reference,
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "parent_event_id": self.parent_event_id,
            "metadata": self.metadata,
            "signature": self.signature,
        }

    def sign(self, private_key) -> None:
        """Sign the event for tamper detection."""
        content = json.dumps(self.to_dict(), sort_keys=True)
        self.signature = sign_with_key(content, private_key)
```

### 3.2 Specialized Event Types

```python
@dataclass
class FilterDecisionEvent(DecisionEvent):
    """Decision to include or exclude items."""
    items_before: int
    items_after: int
    items_excluded: List[str]  # IDs or hashes of excluded items
    filter_criteria: str

@dataclass
class TruncationDecisionEvent(DecisionEvent):
    """Decision to limit output length."""
    original_length: int
    truncated_length: int
    truncation_point: int
    content_lost_summary: str  # What was cut off

@dataclass
class GenerationDecisionEvent(DecisionEvent):
    """Decision about what to generate."""
    generation_parameters: Dict[str, Any]
    alternatives_considered: List[str]
    confidence: float
```

---

## 4. Audit Stream Architecture

### 4.1 Event Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        AI SYSTEM                                 │
│                                                                  │
│   Input → [Decision Point 1] → [Decision Point 2] → Output      │
│                    │                    │                        │
│                    ▼                    ▼                        │
│              ┌─────────────────────────────────┐                │
│              │      AUDIT EVENT STREAM          │                │
│              │                                  │                │
│              │  Event 1 → Event 2 → Event 3... │                │
│              └─────────────────────────────────┘                │
│                              │                                   │
└──────────────────────────────┼───────────────────────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │   AUDIT LOG STORE    │
                    │                      │
                    │  - Immutable         │
                    │  - Signed            │
                    │  - Queryable         │
                    └─────────────────────┘
```

### 4.2 Implementation

```python
from typing import Callable, Generator
import threading
import queue
from abc import ABC, abstractmethod

class AuditStream:
    """Stream for capturing decision events."""

    def __init__(self, store: 'AuditStore'):
        self.store = store
        self.event_queue = queue.Queue()
        self.subscribers: List[Callable[[DecisionEvent], None]] = []
        self._start_worker()

    def emit(self, event: DecisionEvent) -> None:
        """Emit a decision event to the stream."""
        # Sign the event
        event.sign(self._get_signing_key())

        # Queue for processing
        self.event_queue.put(event)

        # Notify subscribers (for real-time monitoring)
        for subscriber in self.subscribers:
            subscriber(event)

    def subscribe(self, callback: Callable[[DecisionEvent], None]) -> None:
        """Subscribe to real-time events."""
        self.subscribers.append(callback)

    def _start_worker(self):
        """Start background worker for persisting events."""
        def worker():
            while True:
                event = self.event_queue.get()
                self.store.persist(event)
                self.event_queue.task_done()

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()


class AuditStore(ABC):
    """Abstract base for audit event storage."""

    @abstractmethod
    def persist(self, event: DecisionEvent) -> None:
        """Persist an event."""
        pass

    @abstractmethod
    def query(self, session_id: str = None, event_type: str = None,
              start_time: datetime = None, end_time: datetime = None
              ) -> Generator[DecisionEvent, None, None]:
        """Query events."""
        pass

    @abstractmethod
    def verify_integrity(self) -> bool:
        """Verify no events have been tampered with."""
        pass


class ImmutableAuditStore(AuditStore):
    """Append-only audit store with integrity verification."""

    def __init__(self, path: str):
        self.path = path
        self.chain_hash = None  # Hash chain for integrity

    def persist(self, event: DecisionEvent) -> None:
        """Persist event with hash chain."""
        # Add to hash chain
        event.metadata["chain_hash"] = self._compute_chain_hash(event)
        self.chain_hash = event.metadata["chain_hash"]

        # Append to store (immutable)
        with open(self.path, "a") as f:
            f.write(json.dumps(event.to_dict()) + "\n")

    def _compute_chain_hash(self, event: DecisionEvent) -> str:
        """Compute hash including previous event."""
        content = json.dumps(event.to_dict(), sort_keys=True)
        if self.chain_hash:
            content = self.chain_hash + content
        return hashlib.sha256(content.encode()).hexdigest()

    def verify_integrity(self) -> bool:
        """Verify the hash chain is unbroken."""
        prev_hash = None
        for event in self.query():
            expected_hash = self._compute_chain_hash_for_verify(event, prev_hash)
            if event.metadata.get("chain_hash") != expected_hash:
                return False
            prev_hash = event.metadata["chain_hash"]
        return True
```

---

## 5. Decision Point Wrappers

### 5.1 Architectural Enforcement

Every operation that makes a decision must go through a wrapper that emits events:

```python
from functools import wraps
import uuid

def audited_decision(
    decision_type: DecisionType,
    description: str,
    source: DecisionSource = DecisionSource.AI_DEFAULT
):
    """Decorator that makes a function's decisions auditable."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, audit_stream: AuditStream = None, **kwargs):
            if audit_stream is None:
                raise ValueError("audit_stream is required for audited decisions")

            # Capture input
            input_data = {"args": str(args), "kwargs": str(kwargs)}
            input_hash = hashlib.sha256(
                json.dumps(input_data, sort_keys=True).encode()
            ).hexdigest()

            # Execute function
            result = func(*args, **kwargs)

            # Capture output
            output_hash = hashlib.sha256(str(result).encode()).hexdigest()

            # Emit decision event
            event = DecisionEvent(
                event_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                session_id=get_current_session_id(),
                decision_type=decision_type,
                decision_description=description,
                options_considered=kwargs.get("_options", ["default"]),
                option_chosen=str(result),
                rationale=kwargs.get("_rationale", "automatic"),
                source=source,
                input_hash=input_hash,
                output_hash=output_hash,
            )
            audit_stream.emit(event)

            return result

        return wrapper
    return decorator


# Usage
@audited_decision(
    decision_type=DecisionType.FILTER,
    description="Filter search results by relevance",
    source=DecisionSource.AI_DEFAULT
)
def filter_results(results: list, threshold: float) -> list:
    return [r for r in results if r.score >= threshold]
```

### 5.2 Mandatory Visibility Wrappers

```python
class MandatoryAuditWrapper:
    """Wrapper that makes audit events mandatory at architecture level."""

    def __init__(self, audit_stream: AuditStream):
        self.audit_stream = audit_stream

    def filter(self, items: list, predicate: Callable, reason: str) -> list:
        """Filter with mandatory audit."""
        before_count = len(items)
        result = [item for item in items if predicate(item)]
        after_count = len(result)

        excluded = [item for item in items if not predicate(item)]

        self.audit_stream.emit(FilterDecisionEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            session_id=get_current_session_id(),
            decision_type=DecisionType.FILTER,
            decision_description=f"Filtered items: {reason}",
            options_considered=["include", "exclude"],
            option_chosen="filtered",
            rationale=reason,
            source=DecisionSource.AI_DEFAULT,
            input_hash=hash_items(items),
            output_hash=hash_items(result),
            items_before=before_count,
            items_after=after_count,
            items_excluded=[hash_item(i) for i in excluded],
            filter_criteria=reason,
        ))

        return result

    def truncate(self, content: str, max_length: int, reason: str) -> str:
        """Truncate with mandatory audit."""
        if len(content) <= max_length:
            return content

        original_length = len(content)
        result = content[:max_length]
        lost = content[max_length:]

        self.audit_stream.emit(TruncationDecisionEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            session_id=get_current_session_id(),
            decision_type=DecisionType.TRUNCATE,
            decision_description=f"Truncated content: {reason}",
            options_considered=["keep_all", "truncate"],
            option_chosen="truncate",
            rationale=reason,
            source=DecisionSource.SYSTEM_CONSTRAINT,
            input_hash=hashlib.sha256(content.encode()).hexdigest(),
            output_hash=hashlib.sha256(result.encode()).hexdigest(),
            original_length=original_length,
            truncated_length=max_length,
            truncation_point=max_length,
            content_lost_summary=f"Removed {len(lost)} chars: '{lost[:50]}...'",
        ))

        return result
```

---

## 6. Configuration with Decision Sources

### 6.1 Every Value Has a Source

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class ConfigValue:
    """Configuration value with decision source."""
    value: Any
    source: DecisionSource
    decided_by: str
    decided_at: str
    rationale: str
    reference: Optional[str] = None  # Link to policy doc

class AuditedConfig:
    """Configuration where every value traces to a decision."""

    def __init__(self):
        self._values: Dict[str, ConfigValue] = {}

    def set(self, key: str, value: Any, source: DecisionSource,
            decided_by: str, rationale: str, reference: str = None):
        """Set a config value with full provenance."""
        self._values[key] = ConfigValue(
            value=value,
            source=source,
            decided_by=decided_by,
            decided_at=datetime.now().isoformat(),
            rationale=rationale,
            reference=reference,
        )

    def get(self, key: str) -> Any:
        """Get a config value."""
        if key not in self._values:
            raise KeyError(f"Config key '{key}' not set with provenance")
        return self._values[key].value

    def get_with_provenance(self, key: str) -> ConfigValue:
        """Get config value with full provenance."""
        return self._values[key]

    def audit_report(self) -> dict:
        """Generate audit report of all config decisions."""
        return {
            key: {
                "value": cv.value,
                "source": cv.source.value,
                "decided_by": cv.decided_by,
                "decided_at": cv.decided_at,
                "rationale": cv.rationale,
            }
            for key, cv in self._values.items()
        }


# Usage
config = AuditedConfig()

config.set(
    key="max_context_length",
    value=100000,
    source=DecisionSource.HUMAN_DECISION,
    decided_by="jeremy",
    rationale="Tested on cluster, this maximizes throughput without OOM",
    reference="docs/performance/context_length_testing.md"
)

config.set(
    key="default_temperature",
    value=0.7,
    source=DecisionSource.AI_DEFAULT,
    decided_by="system",
    rationale="Industry standard default for balanced creativity/consistency",
)
```

---

## 7. Output Metadata

### 7.1 Every Response Includes Audit Metadata

```python
@dataclass
class AuditedResponse:
    """Response with embedded audit metadata."""
    content: str
    metadata: 'ResponseMetadata'

@dataclass
class ResponseMetadata:
    """Metadata showing all decisions that produced this response."""
    session_id: str
    timestamp: datetime

    # Decisions made
    decisions_count: int
    decision_summary: List[str]

    # Limits applied
    limits_applied: List[Dict[str, Any]]

    # Sources used
    sources_consulted: List[str]

    # Verification
    audit_hash: str  # Hash of full audit trail

    def to_dict(self) -> dict:
        return {
            "_meta": {
                "session_id": self.session_id,
                "timestamp": self.timestamp.isoformat(),
                "decisions_count": self.decisions_count,
                "decision_summary": self.decision_summary,
                "limits_applied": self.limits_applied,
                "sources_consulted": self.sources_consulted,
                "audit_hash": self.audit_hash,
                "audit_trail_available": True,
            }
        }

class AuditedAI:
    """AI system with mandatory audit trail."""

    def __init__(self, audit_stream: AuditStream):
        self.audit_stream = audit_stream
        self.wrapper = MandatoryAuditWrapper(audit_stream)

    def generate(self, prompt: str) -> AuditedResponse:
        """Generate response with audit metadata."""
        session_id = get_current_session_id()

        # ... generation logic with audited decisions ...

        # Collect all decisions made during this generation
        decisions = list(self.audit_stream.store.query(session_id=session_id))

        return AuditedResponse(
            content=generated_content,
            metadata=ResponseMetadata(
                session_id=session_id,
                timestamp=datetime.now(),
                decisions_count=len(decisions),
                decision_summary=[d.decision_description for d in decisions],
                limits_applied=self._extract_limits(decisions),
                sources_consulted=self._extract_sources(decisions),
                audit_hash=self._compute_audit_hash(decisions),
            )
        )
```

---

## 8. EU AI Act Compliance Mapping

### 8.1 Requirement Mapping

| EU AI Act Requirement | Zero Trust AI Implementation |
|----------------------|------------------------------|
| **Transparency** | All decisions emit events |
| **Explainability** | Decision events include rationale |
| **Traceability** | Hash chain ensures complete trail |
| **Auditability** | Immutable audit store |
| **Human oversight** | Human decision sources tracked |
| **Documentation** | Config provenance required |

### 8.2 Compliance Report Generator

```python
def generate_compliance_report(audit_store: AuditStore,
                               session_id: str) -> dict:
    """Generate EU AI Act compliance report for a session."""

    events = list(audit_store.query(session_id=session_id))

    return {
        "session_id": session_id,
        "generated_at": datetime.now().isoformat(),
        "compliance_framework": "EU AI Act 2026",

        "transparency": {
            "status": "COMPLIANT",
            "evidence": f"{len(events)} decisions documented",
            "audit_trail_hash": compute_trail_hash(events),
        },

        "explainability": {
            "status": "COMPLIANT" if all(e.rationale for e in events) else "PARTIAL",
            "decisions_with_rationale": sum(1 for e in events if e.rationale),
            "total_decisions": len(events),
        },

        "traceability": {
            "status": "COMPLIANT" if audit_store.verify_integrity() else "FAILED",
            "chain_verified": audit_store.verify_integrity(),
        },

        "human_oversight": {
            "status": "DOCUMENTED",
            "human_decisions": sum(
                1 for e in events
                if e.source == DecisionSource.HUMAN_DECISION
            ),
            "ai_defaults": sum(
                1 for e in events
                if e.source == DecisionSource.AI_DEFAULT
            ),
        },

        "decision_log": [e.to_dict() for e in events],
    }
```

---

## 9. Verification Protocol

### 9.1 Integrity Checks

```python
class AuditVerifier:
    """Verify audit trail integrity."""

    def __init__(self, store: AuditStore):
        self.store = store

    def verify_session(self, session_id: str) -> dict:
        """Verify all events in a session."""
        events = list(self.store.query(session_id=session_id))

        return {
            "session_id": session_id,
            "event_count": len(events),
            "chain_intact": self._verify_chain(events),
            "signatures_valid": self._verify_signatures(events),
            "no_gaps": self._verify_no_gaps(events),
            "sources_valid": self._verify_sources(events),
        }

    def _verify_chain(self, events: List[DecisionEvent]) -> bool:
        """Verify hash chain is unbroken."""
        prev_hash = None
        for event in events:
            expected = compute_chain_hash(event, prev_hash)
            if event.metadata.get("chain_hash") != expected:
                return False
            prev_hash = event.metadata["chain_hash"]
        return True

    def _verify_signatures(self, events: List[DecisionEvent]) -> bool:
        """Verify all event signatures."""
        return all(
            verify_signature(event)
            for event in events
        )
```

---

## 10. Appendix: Quick Reference

### Core Principle

```
The AI WILL make decisions.
The AI MUST make decisions.
The AI WON'T make INVISIBLE decisions.
```

### Decision Event Fields

```
- event_id: Unique identifier
- decision_type: What kind of decision
- decision_description: Human-readable description
- options_considered: What options existed
- option_chosen: What was selected
- rationale: Why this option
- source: Human decision, AI default, or policy
- input_hash: Proof of what triggered this
- output_hash: Proof of what resulted
```

### Compliance Checklist

```
□ All decisions emit events
□ All events include rationale
□ Hash chain for integrity
□ Immutable storage
□ Human decisions tracked separately
□ Config values have provenance
□ Responses include metadata
```

---

## License

This protocol is released under Creative Commons Attribution 4.0 International (CC BY 4.0).

---

*"Architecture that makes opacity impossible while keeping agency fully enabled."*

— Zero Trust AI Audit Protocol v1.0.0, January 23, 2026

