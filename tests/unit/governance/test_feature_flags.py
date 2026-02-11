"""Tests for feature flags module."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from truth_forge.governance.feature_flags import FeatureFlags, RiskThresholds, RoutingFlags


class TestFeatureFlags:
    """Test FeatureFlags class."""

    def test_load_from_yaml(self, tmp_path: Path) -> None:
        """Test loading flags from YAML file."""
        flag_file = tmp_path / "flags.yaml"
        flag_file.write_text(
            """
sovereign_mode_enabled: true
cluster_execution_enabled: false
routing:
  safety_floor: 0.8
  require_peer_review_above: 0.9
risk_thresholds:
  servant_prompt: 3
  sovereign_prompt: 4
  irreversible: 5
"""
        )

        flags = FeatureFlags.load(flag_file)
        assert flags.sovereign_mode_enabled is True
        assert flags.cluster_execution_enabled is False
        assert flags.routing.safety_floor == 0.8
        assert flags.risk_thresholds.servant_prompt == 3

    def test_load_missing_file_raises_error(self, tmp_path: Path) -> None:
        """Test loading missing file raises FileNotFoundError."""
        missing_file = tmp_path / "missing.yaml"
        with pytest.raises(FileNotFoundError):
            FeatureFlags.load(missing_file)

    def test_env_override_bool(self, tmp_path: Path) -> None:
        """Test environment variable override for boolean."""
        flag_file = tmp_path / "flags.yaml"
        flag_file.write_text("sovereign_mode_enabled: false\n")

        with patch.dict(os.environ, {"GENESIS_FLAG_SOVEREIGN_MODE_ENABLED": "true"}):
            flags = FeatureFlags.load(flag_file)
            assert flags.sovereign_mode_enabled is True

    def test_env_override_false(self, tmp_path: Path) -> None:
        """Test environment variable override with false."""
        flag_file = tmp_path / "flags.yaml"
        flag_file.write_text("sovereign_mode_enabled: true\n")

        with patch.dict(os.environ, {"GENESIS_FLAG_SOVEREIGN_MODE_ENABLED": "false"}):
            flags = FeatureFlags.load(flag_file)
            assert flags.sovereign_mode_enabled is False

    def test_env_override_variants(self, tmp_path: Path) -> None:
        """Test environment variable override with various true/false values."""
        flag_file = tmp_path / "flags.yaml"
        flag_file.write_text("sovereign_mode_enabled: false\n")

        for value in ["true", "1", "yes", "on"]:
            with patch.dict(os.environ, {"GENESIS_FLAG_SOVEREIGN_MODE_ENABLED": value}):
                flags = FeatureFlags.load(flag_file)
                assert flags.sovereign_mode_enabled is True

        for value in ["false", "0", "no", "off"]:
            with patch.dict(os.environ, {"GENESIS_FLAG_SOVEREIGN_MODE_ENABLED": value}):
                flags = FeatureFlags.load(flag_file)
                assert flags.sovereign_mode_enabled is False

    def test_defaults(self, tmp_path: Path) -> None:
        """Test default values when not specified."""
        flag_file = tmp_path / "flags.yaml"
        flag_file.write_text("routing:\n  safety_floor: 0.8\n")

        flags = FeatureFlags.load(flag_file)
        assert flags.sovereign_mode_enabled is False  # Default
        assert flags.autonomous_loop_enabled is True  # Default


class TestRoutingFlags:
    """Test RoutingFlags dataclass."""

    def test_routing_flags(self) -> None:
        """Test RoutingFlags structure."""
        routing = RoutingFlags(safety_floor=0.8, require_peer_review_above=0.9)
        assert routing.safety_floor == 0.8
        assert routing.require_peer_review_above == 0.9


class TestRiskThresholds:
    """Test RiskThresholds dataclass."""

    def test_risk_thresholds(self) -> None:
        """Test RiskThresholds structure."""
        thresholds = RiskThresholds(servant_prompt=3, sovereign_prompt=4, irreversible=5)
        assert thresholds.servant_prompt == 3
        assert thresholds.sovereign_prompt == 4
        assert thresholds.irreversible == 5
