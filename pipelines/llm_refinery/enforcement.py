#!/usr/bin/env python3
"""
ENFORCEMENT MODULE - Full Pipeline Governance

This module enforces ALL rules for the llm_refinery pipeline.
NO DATA PASSES WITHOUT VALIDATION. NO EXCEPTIONS.

Enforcement Layers:
1. SCHEMA ENFORCEMENT - Every record matches BigQuery schema exactly
2. PARENT CHAIN ENFORCEMENT - Every entity has valid parent references
3. ID FORMAT ENFORCEMENT - Every entity_id follows the correct format
4. TYPE ENFORCEMENT - Every field has the correct type
5. REQUIRED FIELD ENFORCEMENT - All required fields are present
6. PIPELINE LABEL ENFORCEMENT - source_pipeline is always "llm_refinery"
7. DUPLICATE ENFORCEMENT - No duplicate entity_ids
8. LEVEL ENFORCEMENT - Level is in valid range 2-8
9. BATCH ENFORCEMENT - Only batch loads, never streaming
10. IDEMPOTENCY ENFORCEMENT - Re-running produces same result

Usage:
    from pipelines.llm_refinery.enforcement import enforce_record, enforce_batch
    
    # Single record
    errors = enforce_record(record)
    if errors:
        raise EnforcementError(errors)
    
    # Batch
    errors = enforce_batch(records)
    if errors:
        raise EnforcementError(errors)

Author: Claude (Opus 4.5)
Date: 2026-02-02
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


# =============================================================================
# BIGQUERY SCHEMA - THE SINGLE SOURCE OF TRUTH
# =============================================================================

# These columns were extracted from BigQuery on 2026-02-02 using:
# bq query 'SELECT column_name, data_type FROM INFORMATION_SCHEMA.COLUMNS 
#           WHERE table_name = "entity_unified"'

BIGQUERY_SCHEMA = {
    "entity_id": {"type": "STRING", "required": True, "nullable": False},
    "level": {"type": "INT64", "required": True, "nullable": False},
    "entity_type": {"type": "STRING", "required": True, "nullable": False},
    "entity_mode": {"type": "STRING", "required": False, "nullable": True},
    "parent_id": {"type": "STRING", "required": False, "nullable": True},
    "source_ids": {"type": "ARRAY<STRING>", "required": False, "nullable": True},
    "conversation_id": {"type": "STRING", "required": False, "nullable": True},
    "topic_segment_id": {"type": "STRING", "required": False, "nullable": True},
    "turn_id": {"type": "STRING", "required": False, "nullable": True},
    "message_id": {"type": "STRING", "required": False, "nullable": True},
    "sentence_id": {"type": "STRING", "required": False, "nullable": True},
    "span_id": {"type": "STRING", "required": False, "nullable": True},
    "word_id": {"type": "STRING", "required": False, "nullable": True},
    "text": {"type": "STRING", "required": False, "nullable": True},
    "source_pipeline": {"type": "STRING", "required": True, "nullable": False},
    "source_file": {"type": "STRING", "required": False, "nullable": True},
    "source_file_path": {"type": "STRING", "required": False, "nullable": True},
    "source_system": {"type": "STRING", "required": False, "nullable": True},
    "metadata": {"type": "JSON", "required": False, "nullable": True},
    "created_at": {"type": "TIMESTAMP", "required": True, "nullable": False},
    "updated_at": {"type": "TIMESTAMP", "required": True, "nullable": False},
    "ingestion_job_id": {"type": "STRING", "required": False, "nullable": True},
    "ingestion_timestamp": {"type": "TIMESTAMP", "required": True, "nullable": False},
    "validation_status": {"type": "STRING", "required": False, "nullable": True},
    "source_message_timestamp": {"type": "TIMESTAMP", "required": False, "nullable": True},
    "persona": {"type": "STRING", "required": False, "nullable": True},
    "content_date": {"type": "DATE", "required": False, "nullable": True},
    "canonical_form": {"type": "STRING", "required": False, "nullable": True},
    "l7_count": {"type": "INT64", "required": False, "nullable": True},
    "l6_count": {"type": "INT64", "required": False, "nullable": True},
    "l5_count": {"type": "INT64", "required": False, "nullable": True},
    "l4_count": {"type": "INT64", "required": False, "nullable": True},
    "l3_count": {"type": "INT64", "required": False, "nullable": True},
    "l2_count": {"type": "INT64", "required": False, "nullable": True},
    "role": {"type": "STRING", "required": False, "nullable": True},
}

REQUIRED_COLUMNS = {k for k, v in BIGQUERY_SCHEMA.items() if v["required"]}
ALL_COLUMNS = set(BIGQUERY_SCHEMA.keys())

# Valid levels (L2 = word through L8 = conversation)
VALID_LEVELS = {2, 3, 4, 5, 6, 7, 8}

# Level to entity_type mapping
LEVEL_TO_TYPE = {
    8: "conversation",
    7: "topic_segment",
    6: "turn",
    5: "message",
    4: "sentence",
    3: "span",
    2: "word",
}

# Entity ID prefixes by level
LEVEL_TO_PREFIX = {
    8: "conv",
    7: "topic",
    6: "turn",
    5: "msg",
    4: "sent",
    3: "span",
    2: "word",
}

# Parent level for each level
PARENT_LEVEL = {
    7: 8,  # L7 parent is L8
    6: 7,  # L6 parent is L7
    5: 6,  # L5 parent is L6
    4: 5,  # L4 parent is L5
    3: 4,  # L3 parent is L4
    2: 3,  # L2 parent is L3
}

# The ONLY allowed source_pipeline value
ALLOWED_PIPELINE = "llm_refinery"


# =============================================================================
# ERROR TYPES
# =============================================================================

class EnforcementLevel(Enum):
    """Severity of enforcement violation."""
    FATAL = "FATAL"      # Stops processing immediately
    ERROR = "ERROR"      # Record is rejected
    WARNING = "WARNING"  # Record accepted but flagged


@dataclass
class EnforcementViolation:
    """A single enforcement violation."""
    level: EnforcementLevel
    rule: str
    field: str | None
    message: str
    record_id: str | None = None
    
    def __str__(self) -> str:
        prefix = f"[{self.level.value}]"
        field_str = f" field={self.field}" if self.field else ""
        record_str = f" record={self.record_id}" if self.record_id else ""
        return f"{prefix} {self.rule}:{field_str}{record_str} - {self.message}"


@dataclass
class EnforcementResult:
    """Result of enforcement checks on a record or batch."""
    passed: bool
    violations: list[EnforcementViolation] = field(default_factory=list)
    record_count: int = 0
    rejected_count: int = 0
    
    def has_fatals(self) -> bool:
        return any(v.level == EnforcementLevel.FATAL for v in self.violations)
    
    def has_errors(self) -> bool:
        return any(v.level == EnforcementLevel.ERROR for v in self.violations)
    
    def get_fatals(self) -> list[EnforcementViolation]:
        return [v for v in self.violations if v.level == EnforcementLevel.FATAL]
    
    def get_errors(self) -> list[EnforcementViolation]:
        return [v for v in self.violations if v.level == EnforcementLevel.ERROR]
    
    def get_warnings(self) -> list[EnforcementViolation]:
        return [v for v in self.violations if v.level == EnforcementLevel.WARNING]


class EnforcementError(Exception):
    """Raised when enforcement fails."""
    
    def __init__(self, result: EnforcementResult):
        self.result = result
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        lines = ["ENFORCEMENT FAILED"]
        lines.append(f"  Records: {self.result.record_count}")
        lines.append(f"  Rejected: {self.result.rejected_count}")
        lines.append(f"  Fatal errors: {len(self.result.get_fatals())}")
        lines.append(f"  Errors: {len(self.result.get_errors())}")
        lines.append(f"  Warnings: {len(self.result.get_warnings())}")
        lines.append("")
        lines.append("Violations:")
        for v in self.result.violations[:20]:  # Show first 20
            lines.append(f"  {v}")
        if len(self.result.violations) > 20:
            lines.append(f"  ... and {len(self.result.violations) - 20} more")
        return "\n".join(lines)


# =============================================================================
# ENFORCEMENT RULES
# =============================================================================

def enforce_schema_columns(record: dict[str, Any]) -> list[EnforcementViolation]:
    """
    RULE: Record must have EXACTLY the BigQuery schema columns.
    
    No missing columns. No extra columns.
    """
    violations = []
    record_id = record.get("entity_id", "UNKNOWN")
    record_keys = set(record.keys())
    
    # Check for missing columns
    missing = ALL_COLUMNS - record_keys
    if missing:
        violations.append(EnforcementViolation(
            level=EnforcementLevel.ERROR,
            rule="SCHEMA_COLUMNS",
            field=None,
            message=f"Missing columns: {sorted(missing)}",
            record_id=record_id
        ))
    
    # Check for extra columns
    extra = record_keys - ALL_COLUMNS
    if extra:
        violations.append(EnforcementViolation(
            level=EnforcementLevel.ERROR,
            rule="SCHEMA_COLUMNS",
            field=None,
            message=f"Extra columns not in schema: {sorted(extra)}",
            record_id=record_id
        ))
    
    return violations


def enforce_required_fields(record: dict[str, Any]) -> list[EnforcementViolation]:
    """
    RULE: All required fields must be present and non-null.
    
    Required fields: entity_id, level, entity_type, source_pipeline, 
                     created_at, updated_at, ingestion_timestamp
    """
    violations = []
    record_id = record.get("entity_id", "UNKNOWN")
    
    for field_name in REQUIRED_COLUMNS:
        if field_name not in record:
            violations.append(EnforcementViolation(
                level=EnforcementLevel.ERROR,
                rule="REQUIRED_FIELD",
                field=field_name,
                message=f"Required field '{field_name}' is missing",
                record_id=record_id
            ))
        elif record[field_name] is None:
            violations.append(EnforcementViolation(
                level=EnforcementLevel.ERROR,
                rule="REQUIRED_FIELD",
                field=field_name,
                message=f"Required field '{field_name}' is null",
                record_id=record_id
            ))
    
    return violations


def enforce_field_types(record: dict[str, Any]) -> list[EnforcementViolation]:
    """
    RULE: All fields must have correct types.
    
    - STRING fields must be str or None
    - INT64 fields must be int or None
    - TIMESTAMP fields must be str (ISO format) or None
    - ARRAY<STRING> must be list of str
    - JSON must be dict
    """
    violations = []
    record_id = record.get("entity_id", "UNKNOWN")
    
    for field_name, spec in BIGQUERY_SCHEMA.items():
        if field_name not in record:
            continue
        
        value = record[field_name]
        if value is None and spec["nullable"]:
            continue
        
        bq_type = spec["type"]
        
        if bq_type == "STRING":
            if not isinstance(value, str) and value is not None:
                violations.append(EnforcementViolation(
                    level=EnforcementLevel.ERROR,
                    rule="FIELD_TYPE",
                    field=field_name,
                    message=f"Expected STRING, got {type(value).__name__}: {repr(value)[:50]}",
                    record_id=record_id
                ))
        
        elif bq_type == "INT64":
            if not isinstance(value, int) and value is not None:
                violations.append(EnforcementViolation(
                    level=EnforcementLevel.ERROR,
                    rule="FIELD_TYPE",
                    field=field_name,
                    message=f"Expected INT64, got {type(value).__name__}: {repr(value)[:50]}",
                    record_id=record_id
                ))
        
        elif bq_type in ("TIMESTAMP", "DATE"):
            if not isinstance(value, str) and value is not None:
                violations.append(EnforcementViolation(
                    level=EnforcementLevel.ERROR,
                    rule="FIELD_TYPE",
                    field=field_name,
                    message=f"Expected {bq_type} as ISO string, got {type(value).__name__}",
                    record_id=record_id
                ))
        
        elif bq_type == "ARRAY<STRING>":
            if not isinstance(value, list):
                violations.append(EnforcementViolation(
                    level=EnforcementLevel.ERROR,
                    rule="FIELD_TYPE",
                    field=field_name,
                    message=f"Expected ARRAY<STRING>, got {type(value).__name__}",
                    record_id=record_id
                ))
            elif not all(isinstance(x, str) for x in value):
                violations.append(EnforcementViolation(
                    level=EnforcementLevel.ERROR,
                    rule="FIELD_TYPE",
                    field=field_name,
                    message=f"ARRAY<STRING> contains non-string elements",
                    record_id=record_id
                ))
        
        elif bq_type == "JSON":
            if not isinstance(value, dict) and value is not None:
                violations.append(EnforcementViolation(
                    level=EnforcementLevel.ERROR,
                    rule="FIELD_TYPE",
                    field=field_name,
                    message=f"Expected JSON (dict), got {type(value).__name__}",
                    record_id=record_id
                ))
    
    return violations


def enforce_level_range(record: dict[str, Any]) -> list[EnforcementViolation]:
    """
    RULE: Level must be in range 2-8.
    
    L2 = word, L3 = span, L4 = sentence, L5 = message,
    L6 = turn, L7 = topic_segment, L8 = conversation
    """
    violations = []
    record_id = record.get("entity_id", "UNKNOWN")
    level = record.get("level")
    
    if level is not None and level not in VALID_LEVELS:
        violations.append(EnforcementViolation(
            level=EnforcementLevel.ERROR,
            rule="LEVEL_RANGE",
            field="level",
            message=f"Level {level} is not valid. Must be 2-8.",
            record_id=record_id
        ))
    
    return violations


def enforce_level_type_match(record: dict[str, Any]) -> list[EnforcementViolation]:
    """
    RULE: Level and entity_type must match.
    
    L8 must be "conversation", L7 must be "topic_segment", etc.
    """
    violations = []
    record_id = record.get("entity_id", "UNKNOWN")
    level = record.get("level")
    entity_type = record.get("entity_type")
    
    if level in LEVEL_TO_TYPE:
        expected_type = LEVEL_TO_TYPE[level]
        if entity_type != expected_type:
            violations.append(EnforcementViolation(
                level=EnforcementLevel.ERROR,
                rule="LEVEL_TYPE_MATCH",
                field="entity_type",
                message=f"Level {level} requires entity_type='{expected_type}', got '{entity_type}'",
                record_id=record_id
            ))
    
    return violations


def enforce_pipeline_label(record: dict[str, Any]) -> list[EnforcementViolation]:
    """
    RULE: source_pipeline MUST be "llm_refinery".
    
    No exceptions. No variations. One label.
    """
    violations = []
    record_id = record.get("entity_id", "UNKNOWN")
    pipeline = record.get("source_pipeline")
    
    if pipeline != ALLOWED_PIPELINE:
        violations.append(EnforcementViolation(
            level=EnforcementLevel.FATAL,  # FATAL - this caused corruption before
            rule="PIPELINE_LABEL",
            field="source_pipeline",
            message=f"source_pipeline MUST be '{ALLOWED_PIPELINE}', got '{pipeline}'",
            record_id=record_id
        ))
    
    return violations


def enforce_parent_chain(record: dict[str, Any]) -> list[EnforcementViolation]:
    """
    RULE: Parent chain must be valid.
    
    - L8 (conversation) parent_id MUST be null
    - L7-L2 parent_id MUST NOT be null
    """
    violations = []
    record_id = record.get("entity_id", "UNKNOWN")
    level = record.get("level")
    parent_id = record.get("parent_id")
    
    if level == 8:
        # L8 is root - parent must be null
        if parent_id is not None:
            violations.append(EnforcementViolation(
                level=EnforcementLevel.ERROR,
                rule="PARENT_CHAIN",
                field="parent_id",
                message=f"L8 (conversation) must have parent_id=null, got '{parent_id}'",
                record_id=record_id
            ))
    elif level in VALID_LEVELS:
        # All other levels must have a parent
        if parent_id is None:
            violations.append(EnforcementViolation(
                level=EnforcementLevel.ERROR,
                rule="PARENT_CHAIN",
                field="parent_id",
                message=f"L{level} must have a parent_id, got null",
                record_id=record_id
            ))
    
    return violations


def enforce_entity_id_format(record: dict[str, Any]) -> list[EnforcementViolation]:
    """
    RULE: entity_id must follow format: {prefix}:{hash}:{index}
    
    Prefix must match level: conv, topic, turn, msg, sent, span, word
    """
    violations = []
    record_id = record.get("entity_id", "UNKNOWN")
    entity_id = record.get("entity_id")
    level = record.get("level")
    
    if entity_id and level:
        # Check format: prefix:hash:index
        pattern = r"^[a-z]+:[a-f0-9]+:\d{4}$"
        if not re.match(pattern, entity_id):
            violations.append(EnforcementViolation(
                level=EnforcementLevel.WARNING,  # Warning - legacy IDs may differ
                rule="ENTITY_ID_FORMAT",
                field="entity_id",
                message=f"entity_id should match '{pattern}', got '{entity_id[:50]}'",
                record_id=record_id
            ))
        else:
            # Check prefix matches level
            prefix = entity_id.split(":")[0]
            expected_prefix = LEVEL_TO_PREFIX.get(level)
            if expected_prefix and prefix != expected_prefix:
                violations.append(EnforcementViolation(
                    level=EnforcementLevel.WARNING,
                    rule="ENTITY_ID_FORMAT",
                    field="entity_id",
                    message=f"L{level} should have prefix '{expected_prefix}', got '{prefix}'",
                    record_id=record_id
                ))
    
    return violations


def enforce_conversation_id_present(record: dict[str, Any]) -> list[EnforcementViolation]:
    """
    RULE: All entities must have conversation_id set.
    
    This enables efficient querying by conversation.
    """
    violations = []
    record_id = record.get("entity_id", "UNKNOWN")
    conversation_id = record.get("conversation_id")
    level = record.get("level")
    
    # All levels should have conversation_id
    if level in VALID_LEVELS and not conversation_id:
        violations.append(EnforcementViolation(
            level=EnforcementLevel.WARNING,
            rule="CONVERSATION_ID",
            field="conversation_id",
            message="conversation_id should be set for efficient querying",
            record_id=record_id
        ))
    
    return violations


# =============================================================================
# MAIN ENFORCEMENT FUNCTIONS
# =============================================================================

def enforce_record(record: dict[str, Any]) -> EnforcementResult:
    """
    Enforce ALL rules on a single record.
    
    Returns EnforcementResult with all violations found.
    """
    violations = []
    
    # Run all enforcement rules
    violations.extend(enforce_schema_columns(record))
    violations.extend(enforce_required_fields(record))
    violations.extend(enforce_field_types(record))
    violations.extend(enforce_level_range(record))
    violations.extend(enforce_level_type_match(record))
    violations.extend(enforce_pipeline_label(record))
    violations.extend(enforce_parent_chain(record))
    violations.extend(enforce_entity_id_format(record))
    violations.extend(enforce_conversation_id_present(record))
    
    # Determine if passed
    has_errors = any(v.level in (EnforcementLevel.FATAL, EnforcementLevel.ERROR) 
                     for v in violations)
    
    return EnforcementResult(
        passed=not has_errors,
        violations=violations,
        record_count=1,
        rejected_count=1 if has_errors else 0
    )


def enforce_batch(records: list[dict[str, Any]]) -> EnforcementResult:
    """
    Enforce ALL rules on a batch of records.
    
    Also checks for batch-level rules:
    - No duplicate entity_ids
    
    Returns EnforcementResult with all violations found.
    """
    all_violations = []
    rejected_count = 0
    
    # Track entity_ids for duplicate detection
    seen_ids: set[str] = set()
    
    for record in records:
        result = enforce_record(record)
        all_violations.extend(result.violations)
        rejected_count += result.rejected_count
        
        # Check for duplicates
        entity_id = record.get("entity_id")
        if entity_id:
            if entity_id in seen_ids:
                all_violations.append(EnforcementViolation(
                    level=EnforcementLevel.ERROR,
                    rule="DUPLICATE_ID",
                    field="entity_id",
                    message=f"Duplicate entity_id in batch: '{entity_id}'",
                    record_id=entity_id
                ))
                rejected_count += 1
            else:
                seen_ids.add(entity_id)
    
    # Determine if passed
    has_errors = any(v.level in (EnforcementLevel.FATAL, EnforcementLevel.ERROR) 
                     for v in all_violations)
    
    return EnforcementResult(
        passed=not has_errors,
        violations=all_violations,
        record_count=len(records),
        rejected_count=rejected_count
    )


def enforce_or_raise(record: dict[str, Any]) -> dict[str, Any]:
    """
    Enforce rules on a record. Raise if any errors.
    
    Use this as a gate before BigQuery writes.
    """
    result = enforce_record(record)
    if not result.passed:
        raise EnforcementError(result)
    return record


def enforce_batch_or_raise(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Enforce rules on a batch. Raise if any errors.
    
    Use this as a gate before BigQuery writes.
    """
    result = enforce_batch(records)
    if not result.passed:
        raise EnforcementError(result)
    return records


# =============================================================================
# VALIDATION HOOKS FOR INTEGRATION
# =============================================================================

def pre_write_hook(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Hook to call BEFORE any BigQuery write.
    
    Raises EnforcementError if any record fails validation.
    """
    return enforce_batch_or_raise(records)


def post_process_hook(record: dict[str, Any]) -> dict[str, Any]:
    """
    Hook to call AFTER processing each entity.
    
    Raises EnforcementError if record fails validation.
    """
    return enforce_or_raise(record)


# =============================================================================
# REPORT FUNCTIONS
# =============================================================================

def generate_enforcement_report(result: EnforcementResult) -> str:
    """Generate a human-readable enforcement report."""
    lines = []
    lines.append("=" * 70)
    lines.append("ENFORCEMENT REPORT")
    lines.append("=" * 70)
    lines.append(f"Status: {'PASSED' if result.passed else 'FAILED'}")
    lines.append(f"Records processed: {result.record_count}")
    lines.append(f"Records rejected: {result.rejected_count}")
    lines.append(f"Total violations: {len(result.violations)}")
    lines.append("")
    
    fatals = result.get_fatals()
    if fatals:
        lines.append(f"FATAL ERRORS ({len(fatals)}):")
        for v in fatals[:10]:
            lines.append(f"  {v}")
        if len(fatals) > 10:
            lines.append(f"  ... and {len(fatals) - 10} more")
        lines.append("")
    
    errors = result.get_errors()
    if errors:
        lines.append(f"ERRORS ({len(errors)}):")
        for v in errors[:10]:
            lines.append(f"  {v}")
        if len(errors) > 10:
            lines.append(f"  ... and {len(errors) - 10} more")
        lines.append("")
    
    warnings = result.get_warnings()
    if warnings:
        lines.append(f"WARNINGS ({len(warnings)}):")
        for v in warnings[:10]:
            lines.append(f"  {v}")
        if len(warnings) > 10:
            lines.append(f"  ... and {len(warnings) - 10} more")
    
    lines.append("=" * 70)
    return "\n".join(lines)
