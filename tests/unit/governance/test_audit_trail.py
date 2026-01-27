"""Tests for audit trail module.

Tests the audit trail recording and compliance functionality.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from truth_forge.governance.audit_trail import (
    AuditCategory,
    AuditLevel,
    AuditRecord,
    AuditTrail,
    get_current_run_id,
)


class TestAuditLevel:
    """Tests for AuditLevel enum."""

    def test_level_values(self) -> None:
        """Test audit level values."""
        assert AuditLevel.DEBUG.value == "debug"
        assert AuditLevel.INFO.value == "info"
        assert AuditLevel.WARNING.value == "warning"
        assert AuditLevel.ERROR.value == "error"
        assert AuditLevel.CRITICAL.value == "critical"
        assert AuditLevel.VIOLATION.value == "violation"


class TestAuditCategory:
    """Tests for AuditCategory enum."""

    def test_category_values(self) -> None:
        """Test audit category values."""
        assert AuditCategory.HOLD_OPERATION.value == "hold_operation"
        assert AuditCategory.AGENT_ACTION.value == "agent_action"
        assert AuditCategory.GOVERNANCE.value == "governance"
        assert AuditCategory.COST.value == "cost"
        assert AuditCategory.FEDERATION.value == "federation"
        assert AuditCategory.SYSTEM.value == "system"


class TestAuditRecord:
    """Tests for AuditRecord dataclass."""

    def test_default_values(self) -> None:
        """Test default audit record values."""
        record = AuditRecord()
        assert record.audit_id.startswith("audit_")
        assert record.run_id.startswith("run_")
        assert isinstance(record.timestamp, datetime)
        assert record.level == AuditLevel.INFO
        assert record.category == AuditCategory.SYSTEM
        assert record.success is True
        assert record.error_message is None

    def test_custom_values(self) -> None:
        """Test custom audit record values."""
        record = AuditRecord(
            operation="test_op",
            component="test_component",
            target="test_target",
            level=AuditLevel.ERROR,
            category=AuditCategory.GOVERNANCE,
            success=False,
            error_message="test error",
            context={"key": "value"},
        )
        assert record.operation == "test_op"
        assert record.component == "test_component"
        assert record.target == "test_target"
        assert record.level == AuditLevel.ERROR
        assert record.category == AuditCategory.GOVERNANCE
        assert record.success is False
        assert record.error_message == "test error"
        assert record.context == {"key": "value"}

    def test_to_dict(self) -> None:
        """Test converting record to dictionary."""
        record = AuditRecord(
            operation="test",
            component="test",
            level=AuditLevel.WARNING,
            category=AuditCategory.COST,
        )
        data = record.to_dict()

        assert "audit_id" in data
        assert "timestamp" in data
        assert data["level"] == "warning"
        assert data["category"] == "cost"
        assert data["operation"] == "test"

    def test_to_json(self) -> None:
        """Test converting record to JSON."""
        record = AuditRecord(operation="test", component="test")
        json_str = record.to_json()

        assert isinstance(json_str, str)
        assert "test" in json_str
        assert "audit_id" in json_str


class TestAuditTrail:
    """Tests for AuditTrail class."""

    def test_init_creates_storage_directory(self) -> None:
        """Test that init creates storage directory."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "audit" / "trail.jsonl"
            trail = AuditTrail(storage_path=path)

            assert path.parent.exists()
            assert trail.storage_path == path

    def test_record_creates_audit_record(self) -> None:
        """Test record method creates audit record."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "audit.jsonl"
            trail = AuditTrail(storage_path=path)

            record = trail.record(
                operation="test_op",
                component="test_component",
                target="test_target",
            )

            assert record.operation == "test_op"
            assert record.component == "test_component"
            assert record.target == "test_target"

    def test_record_success(self) -> None:
        """Test record_success shorthand."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "audit.jsonl"
            trail = AuditTrail(storage_path=path)

            record = trail.record_success("successful_op", "component")

            assert record.success is True
            assert record.operation == "successful_op"

    def test_record_failure(self) -> None:
        """Test record_failure shorthand."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "audit.jsonl"
            trail = AuditTrail(storage_path=path)

            record = trail.record_failure("failed_op", "error message", "component")

            assert record.success is False
            assert record.error_message == "error message"
            assert record.level == AuditLevel.ERROR

    def test_record_violation(self) -> None:
        """Test record_violation shorthand."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "audit.jsonl"
            trail = AuditTrail(storage_path=path)

            record = trail.record_violation("violation_op", "policy reason")

            assert record.success is False
            assert record.level == AuditLevel.VIOLATION
            assert record.category == AuditCategory.GOVERNANCE

    def test_record_hold_operation(self) -> None:
        """Test record_hold_operation shorthand."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "audit.jsonl"
            trail = AuditTrail(storage_path=path)

            record = trail.record_hold_operation(
                operation="write",
                hold_layer="hold2",
                component="agent",
                records_count=100,
            )

            assert record.category == AuditCategory.HOLD_OPERATION
            assert record.context["hold_layer"] == "hold2"
            assert record.context["records_count"] == 100

    def test_record_cost(self) -> None:
        """Test record_cost shorthand."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "audit.jsonl"
            trail = AuditTrail(storage_path=path)

            record = trail.record_cost(
                service="openai",
                operation="completion",
                cost_usd=0.05,
            )

            assert record.category == AuditCategory.COST
            assert record.context["cost_usd"] == 0.05

    def test_flush_writes_to_file(self) -> None:
        """Test flush writes records to file."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "audit.jsonl"
            trail = AuditTrail(storage_path=path, auto_flush=False)

            trail.record(operation="op1", component="comp1")
            trail.record(operation="op2", component="comp2")

            count = trail.flush()

            assert count == 2
            assert path.exists()
            content = path.read_text()
            assert "op1" in content
            assert "op2" in content

    def test_get_recent(self) -> None:
        """Test get_recent returns recent records."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "audit.jsonl"
            trail = AuditTrail(storage_path=path, auto_flush=False)

            trail.record(operation="op1", component="comp")
            trail.record(operation="op2", component="comp")
            trail.record(operation="op3", component="comp")

            recent = trail.get_recent(limit=2)

            assert len(recent) == 2
            assert recent[0].operation == "op3"  # Newest first
            assert recent[1].operation == "op2"

    def test_get_violations(self) -> None:
        """Test get_violations returns only violations."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "audit.jsonl"
            trail = AuditTrail(storage_path=path, auto_flush=False)

            trail.record(operation="normal", component="comp")
            trail.record_violation("violation1", "reason1")
            trail.record(operation="normal2", component="comp")
            trail.record_violation("violation2", "reason2")

            violations = trail.get_violations()

            assert len(violations) == 2
            assert all(v.level == AuditLevel.VIOLATION for v in violations)

    def test_query_by_category(self) -> None:
        """Test query filtering by category."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "audit.jsonl"
            trail = AuditTrail(storage_path=path, auto_flush=False)

            trail.record(operation="op1", component="comp", category=AuditCategory.COST)
            trail.record(operation="op2", component="comp", category=AuditCategory.SYSTEM)
            trail.record(operation="op3", component="comp", category=AuditCategory.COST)

            results = trail.query(category=AuditCategory.COST)

            assert len(results) == 2
            assert all(r.category == AuditCategory.COST for r in results)

    def test_query_by_component(self) -> None:
        """Test query filtering by component."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "audit.jsonl"
            trail = AuditTrail(storage_path=path, auto_flush=False)

            trail.record(operation="op1", component="agent")
            trail.record(operation="op2", component="gateway")
            trail.record(operation="op3", component="agent")

            results = trail.query(component="agent")

            assert len(results) == 2
            assert all(r.component == "agent" for r in results)

    def test_context_manager(self) -> None:
        """Test context manager flushes on exit."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "audit.jsonl"

            with AuditTrail(storage_path=path, auto_flush=False) as trail:
                trail.record(operation="op1", component="comp")
                trail.record(operation="op2", component="comp")
                assert not path.exists() or path.read_text() == ""

            # After exit, should be flushed
            assert path.exists()
            content = path.read_text()
            assert "op1" in content
            assert "op2" in content


class TestGetCurrentRunId:
    """Tests for get_current_run_id function."""

    def test_returns_string(self) -> None:
        """Test that get_current_run_id returns a string."""
        run_id = get_current_run_id()
        assert isinstance(run_id, str)
        assert run_id.startswith("run_")

    def test_returns_same_id_in_session(self) -> None:
        """Test that multiple calls return the same ID."""
        run_id1 = get_current_run_id()
        run_id2 = get_current_run_id()
        assert run_id1 == run_id2
