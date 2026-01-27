"""Tests for cost enforcer module.

Tests the budget gate enforcement functionality.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from truth_forge.governance.cost_enforcer import (
    BudgetConfig,
    CostAction,
    CostEnforcer,
    CostRecord,
)


class TestCostAction:
    """Tests for CostAction enum."""

    def test_action_values(self) -> None:
        """Test cost action values."""
        assert CostAction.ALLOW.value == "allow"
        assert CostAction.WARN.value == "warn"
        assert CostAction.DENY.value == "deny"
        assert CostAction.THROTTLE.value == "throttle"


class TestCostRecord:
    """Tests for CostRecord dataclass."""

    def test_default_values(self) -> None:
        """Test default cost record values."""
        record = CostRecord()
        assert record.service == ""
        assert record.operation == ""
        assert record.cost_usd == Decimal("0")
        assert record.tokens_in == 0
        assert record.tokens_out == 0

    def test_custom_values(self) -> None:
        """Test custom cost record values."""
        record = CostRecord(
            service="openai",
            operation="completion",
            cost_usd=Decimal("0.05"),
            tokens_in=100,
            tokens_out=200,
        )
        assert record.service == "openai"
        assert record.operation == "completion"
        assert record.cost_usd == Decimal("0.05")
        assert record.tokens_in == 100
        assert record.tokens_out == 200

    def test_to_dict(self) -> None:
        """Test converting record to dictionary."""
        record = CostRecord(
            service="anthropic",
            operation="message",
            cost_usd=Decimal("0.10"),
        )
        data = record.to_dict()

        assert data["service"] == "anthropic"
        assert data["operation"] == "message"
        assert data["cost_usd"] == "0.10"
        assert "timestamp" in data


class TestBudgetConfig:
    """Tests for BudgetConfig dataclass."""

    def test_default_values(self) -> None:
        """Test default budget config values."""
        config = BudgetConfig()
        assert config.daily_budget_usd == Decimal("10.00")
        assert config.monthly_budget_usd == Decimal("100.00")
        assert config.per_run_budget_usd == Decimal("1.00")
        assert config.soft_limit_threshold == 0.8
        assert config.hard_limit_threshold == 1.0

    def test_custom_values(self) -> None:
        """Test custom budget config values."""
        config = BudgetConfig(
            daily_budget_usd=Decimal("5.00"),
            monthly_budget_usd=Decimal("50.00"),
            per_run_budget_usd=Decimal("0.50"),
        )
        assert config.daily_budget_usd == Decimal("5.00")
        assert config.monthly_budget_usd == Decimal("50.00")
        assert config.per_run_budget_usd == Decimal("0.50")


class TestCostEnforcer:
    """Tests for CostEnforcer class."""

    def test_init_creates_storage_directory(self) -> None:
        """Test that init creates storage directory."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "cost" / "records.jsonl"
            enforcer = CostEnforcer(storage_path=path)

            assert path.parent.exists()
            assert enforcer.storage_path == path

    def test_check_within_budget_returns_true(self) -> None:
        """Test check returns True when within budget."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "cost.jsonl"
            enforcer = CostEnforcer(storage_path=path)

            result = enforcer.check("openai", "completion", 0.01)

            assert result is True

    def test_check_exceeding_daily_budget_returns_false(self) -> None:
        """Test check returns False when exceeding daily budget."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "cost.jsonl"
            config = BudgetConfig(daily_budget_usd=Decimal("1.00"))
            enforcer = CostEnforcer(config=config, storage_path=path)

            # This should exceed daily budget
            result = enforcer.check("openai", "completion", 1.50)

            assert result is False

    def test_check_with_details_returns_action_and_reason(self) -> None:
        """Test check_with_details returns detailed info."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "cost.jsonl"
            enforcer = CostEnforcer(storage_path=path)

            allowed, action, reason = enforcer.check_with_details(
                "openai", "completion", 0.01
            )

            assert allowed is True
            assert action == CostAction.ALLOW
            assert reason == "within_budget"

    def test_record_updates_totals(self) -> None:
        """Test record method updates all totals."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "cost.jsonl"
            enforcer = CostEnforcer(storage_path=path)

            enforcer.record("openai", "completion", 0.05)

            assert enforcer.get_daily_total() == Decimal("0.05")
            assert enforcer.get_monthly_total() == Decimal("0.05")
            assert enforcer.get_service_total("openai") == Decimal("0.05")

    def test_record_persists_to_file(self) -> None:
        """Test record writes to file."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "cost.jsonl"
            enforcer = CostEnforcer(storage_path=path)

            enforcer.record("openai", "completion", 0.05, tokens_in=100, tokens_out=50)

            assert path.exists()
            content = path.read_text()
            assert "openai" in content
            assert "completion" in content

    def test_get_budget_status(self) -> None:
        """Test get_budget_status returns correct structure."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "cost.jsonl"
            enforcer = CostEnforcer(storage_path=path)

            enforcer.record("openai", "completion", 2.50)

            status = enforcer.get_budget_status()

            assert "daily" in status
            assert "monthly" in status
            assert "services" in status
            assert status["daily"]["spent"] == "2.5"

    def test_get_stats(self) -> None:
        """Test get_stats returns correct structure."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "cost.jsonl"
            enforcer = CostEnforcer(storage_path=path)

            enforcer.record("openai", "completion", 1.00)

            stats = enforcer.get_stats()

            assert stats["total_cost_usd"] == 1.0
            assert stats["total_operations"] == 1
            assert stats["daily_budget"] == 10.0

    def test_within_budget_returns_true_when_ok(self) -> None:
        """Test within_budget returns True when under limits."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "cost.jsonl"
            enforcer = CostEnforcer(storage_path=path)

            assert enforcer.within_budget() is True

    def test_within_budget_returns_false_when_exceeded(self) -> None:
        """Test within_budget returns False when over limits."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "cost.jsonl"
            config = BudgetConfig(daily_budget_usd=Decimal("1.00"))
            enforcer = CostEnforcer(config=config, storage_path=path)

            enforcer.record("openai", "completion", 1.50)

            assert enforcer.within_budget() is False

    def test_service_specific_budget(self) -> None:
        """Test service-specific budget enforcement."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "cost.jsonl"
            config = BudgetConfig(
                daily_budget_usd=Decimal("100.00"),
                service_budgets={"openai": Decimal("1.00")},
            )
            enforcer = CostEnforcer(config=config, storage_path=path)

            # Record cost that exceeds service budget
            enforcer.record("openai", "completion", 0.80)

            # Check should fail for this service
            result = enforcer.check("openai", "completion", 0.30)

            assert result is False

    def test_per_run_budget(self) -> None:
        """Test per-run budget enforcement."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "cost.jsonl"
            config = BudgetConfig(
                daily_budget_usd=Decimal("100.00"),
                per_run_budget_usd=Decimal("0.50"),
            )
            enforcer = CostEnforcer(config=config, storage_path=path)

            # Record cost
            enforcer.record("openai", "completion", 0.40)

            # Next check should fail due to per-run limit
            result = enforcer.check("openai", "completion", 0.20)

            assert result is False

    def test_soft_limit_warning(self) -> None:
        """Test soft limit triggers warning but allows."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "cost.jsonl"
            config = BudgetConfig(
                daily_budget_usd=Decimal("10.00"),
                per_run_budget_usd=Decimal("10.00"),  # High per-run limit
                soft_limit_threshold=0.5,  # Warn at 50%
            )
            enforcer = CostEnforcer(config=config, storage_path=path)

            # Record cost that triggers soft limit (50% of 10)
            enforcer.record("openai", "completion", 4.00)

            # Should still allow but warn (6.00 is 60% - above soft limit but below hard)
            allowed, action, reason = enforcer.check_with_details(
                "openai", "completion", 2.00
            )

            # Still allowed, soft limit warning
            assert allowed is True

    def test_load_recent_costs_from_file(self) -> None:
        """Test loading recent costs from existing file."""
        import json
        from datetime import UTC, datetime

        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "cost.jsonl"

            # Create a cost file with recent records
            now = datetime.now(UTC)
            records = [
                {
                    "timestamp": now.isoformat(),
                    "run_id": "test-run-1",
                    "service": "openai",
                    "operation": "completion",
                    "cost_usd": "0.50",
                    "tokens_in": 100,
                    "tokens_out": 50,
                    "context": {},
                },
                {
                    "timestamp": now.isoformat(),
                    "run_id": "test-run-2",
                    "service": "anthropic",
                    "operation": "message",
                    "cost_usd": "0.30",
                    "tokens_in": 200,
                    "tokens_out": 100,
                    "context": {},
                },
            ]

            with open(path, "w", encoding="utf-8") as f:
                for record in records:
                    f.write(json.dumps(record) + "\n")

            # Initialize enforcer - should load existing records
            enforcer = CostEnforcer(storage_path=path)

            # Daily total should include loaded records
            assert enforcer.get_daily_total() == Decimal("0.80")
            assert enforcer.get_service_total("openai") == Decimal("0.50")
            assert enforcer.get_service_total("anthropic") == Decimal("0.30")

    def test_load_recent_costs_handles_invalid_file(self) -> None:
        """Test loading handles invalid JSON gracefully."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "cost.jsonl"

            # Write invalid content
            with open(path, "w", encoding="utf-8") as f:
                f.write("not valid json\n")
                f.write("{}\n")  # Empty but valid JSON

            # Should not raise, just log warning
            enforcer = CostEnforcer(storage_path=path)
            assert enforcer is not None

    def test_load_recent_costs_empty_lines(self) -> None:
        """Test loading skips empty lines."""
        import json
        from datetime import UTC, datetime

        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "cost.jsonl"

            now = datetime.now(UTC)
            record = {
                "timestamp": now.isoformat(),
                "run_id": "test-run",
                "service": "openai",
                "cost_usd": "0.25",
            }

            with open(path, "w", encoding="utf-8") as f:
                f.write("\n")  # Empty line
                f.write(json.dumps(record) + "\n")
                f.write("   \n")  # Whitespace line
                f.write("\n")  # Another empty line

            enforcer = CostEnforcer(storage_path=path)
            assert enforcer.get_daily_total() == Decimal("0.25")

    def test_monthly_budget_exceeded_denial(self) -> None:
        """Test monthly budget exceeded results in denial."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "cost.jsonl"
            config = BudgetConfig(
                daily_budget_usd=Decimal("100.00"),  # High daily
                monthly_budget_usd=Decimal("1.00"),  # Low monthly
                per_run_budget_usd=Decimal("100.00"),  # High per-run
            )
            enforcer = CostEnforcer(config=config, storage_path=path)

            # Should be denied due to monthly budget
            allowed, action, reason = enforcer.check_with_details(
                "openai", "completion", 1.50
            )

            assert allowed is False
            assert action == CostAction.DENY
            assert "Monthly budget exceeded" in reason

    def test_get_run_total_with_default_run_id(self) -> None:
        """Test get_run_total uses current run_id when not specified."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "cost.jsonl"
            enforcer = CostEnforcer(storage_path=path)

            # Record some costs (will use current run_id)
            enforcer.record("openai", "completion", 0.25)
            enforcer.record("anthropic", "message", 0.15)

            # Get run total without specifying run_id
            total = enforcer.get_run_total()

            assert total == Decimal("0.40")

    def test_default_storage_path(self) -> None:
        """Test enforcer uses default storage path when not specified."""
        from unittest.mock import patch

        with TemporaryDirectory() as tmpdir:
            with patch("truth_forge.governance.cost_enforcer.DATA_ROOT", Path(tmpdir)):
                enforcer = CostEnforcer()

                expected_path = Path(tmpdir) / "local" / "cost" / "cost_records.jsonl"
                assert enforcer.storage_path == expected_path
                assert enforcer.storage_path.parent.exists()
