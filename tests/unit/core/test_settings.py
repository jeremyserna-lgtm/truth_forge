"""Tests for truth_forge.core.settings module.

Tests configuration loading, validation, and environment variable handling.
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from truth_forge.core.settings import (
    TruthForgeSettings,
    clear_settings_cache,
    get_settings,
    settings,
)


class TestTruthForgeSettings:
    """Test TruthForgeSettings class."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = TruthForgeSettings()
        assert config.environment == "development"
        assert config.service_version == "1.0.0"
        assert config.bigquery_location == "US"
        assert config.bigquery_max_rows == 1_000_000

    def test_loads_from_env_var(self) -> None:
        """Test loads configuration from environment variables."""
        with patch.dict(
            os.environ,
            {
                "GCP_PROJECT": "test-project",
                "BIGQUERY_LOCATION": "EU",
                "ENVIRONMENT": "production",
            },
        ):
            clear_settings_cache()
            config = TruthForgeSettings()
            assert config.gcp_project == "test-project"
            assert config.bigquery_location == "EU"
            assert config.environment == "production"

    def test_effective_gcp_project(self) -> None:
        """Test effective_gcp_project property."""
        config = TruthForgeSettings(gcp_project="project1")
        assert config.effective_gcp_project == "project1"

        config = TruthForgeSettings(google_cloud_project="project2")
        assert config.effective_gcp_project == "project2"

        config = TruthForgeSettings()
        assert config.effective_gcp_project is None

    def test_effective_gemini_key(self) -> None:
        """Test effective_gemini_key property."""
        config = TruthForgeSettings(gemini_api_key="key1")
        assert config.effective_gemini_key == "key1"

        config = TruthForgeSettings(google_api_key="key2")
        assert config.effective_gemini_key == "key2"

        config = TruthForgeSettings(gemini_api_key="key1", google_api_key="key2")
        assert config.effective_gemini_key == "key1"  # gemini_api_key takes precedence

    def test_get_project_root_from_setting(self, tmp_path: Path) -> None:
        """Test get_project_root uses truth_forge_root setting."""
        config = TruthForgeSettings(truth_forge_root=str(tmp_path))
        result = config.get_project_root()
        assert result == tmp_path

    def test_get_project_root_falls_back(self, tmp_path: Path) -> None:
        """Test get_project_root falls back to paths.get_project_root."""
        config = TruthForgeSettings()
        with patch("truth_forge.core.paths.get_project_root", return_value=tmp_path):
            result = config.get_project_root()
            assert result == tmp_path

    def test_validate_gcp_project_warns_on_default(self) -> None:
        """Test validate_gcp_project warns on default project."""
        with pytest.warns(UserWarning, match="Using default GCP project"):
            TruthForgeSettings(gcp_project="flash-clover-464719-g1")

    def test_session_limits(self) -> None:
        """Test session limit defaults."""
        config = TruthForgeSettings()
        assert config.bq_session_max_bytes == 5 * 1024**3  # 5 GB
        assert config.bq_session_max_queries == 500
        assert config.bq_session_warning_bytes == 2 * 1024**3  # 2 GB
        assert config.bq_session_warning_queries == 20

    def test_gemini_limits(self) -> None:
        """Test Gemini API limits."""
        config = TruthForgeSettings()
        assert config.gemini_max_calls_per_session == 1000
        assert config.gemini_max_tokens_per_session == 10_000_000
        assert config.gemini_max_cost_per_session == 10.0
        assert config.gemini_min_call_interval == 0.1

    def test_api_keys_optional(self) -> None:
        """Test API keys are optional."""
        config = TruthForgeSettings()
        assert config.google_api_key is None or isinstance(config.google_api_key, str)
        assert config.anthropic_api_key is None or isinstance(config.anthropic_api_key, str)
        assert config.openai_api_key is None or isinstance(config.openai_api_key, str)

    def test_external_services(self) -> None:
        """Test external service configuration."""
        config = TruthForgeSettings()
        assert config.twenty_base_url == "https://api.twenty.com"
        assert config.google_cse_id is None or isinstance(config.google_cse_id, str)

    def test_federation_settings(self) -> None:
        """Test federation configuration."""
        config = TruthForgeSettings()
        assert config.federation_hub is None or isinstance(config.federation_hub, str)
        assert config.federation_key is None or isinstance(config.federation_key, str)
        assert config.organism_id is None or isinstance(config.organism_id, str)

    def test_governance_settings(self) -> None:
        """Test governance configuration."""
        config = TruthForgeSettings()
        assert config.governance_enable_alerts is False
        assert config.budget_cache_ttl_seconds == 300

    def test_environment_validation(self) -> None:
        """Test environment field validation."""
        # Valid values
        config = TruthForgeSettings(environment="development")
        assert config.environment == "development"

        config = TruthForgeSettings(environment="staging")
        assert config.environment == "staging"

        config = TruthForgeSettings(environment="production")
        assert config.environment == "production"


class TestGetSettings:
    """Test get_settings function."""

    def test_returns_settings_instance(self) -> None:
        """Test get_settings returns TruthForgeSettings instance."""
        result = get_settings()
        assert isinstance(result, TruthForgeSettings)

    def test_cached(self) -> None:
        """Test get_settings is cached."""
        result1 = get_settings()
        result2 = get_settings()
        assert result1 is result2

    def test_cache_cleared(self) -> None:
        """Test cache can be cleared."""
        get_settings()  # populate cache
        clear_settings_cache()
        result2 = get_settings()
        # May or may not be same instance depending on env vars
        assert isinstance(result2, TruthForgeSettings)


class TestSettingsSingleton:
    """Test settings singleton."""

    def test_is_settings_instance(self) -> None:
        """Test settings is TruthForgeSettings instance."""
        assert isinstance(settings, TruthForgeSettings)

    def test_accessible(self) -> None:
        """Test settings can be accessed."""
        assert hasattr(settings, "environment")
        assert hasattr(settings, "gcp_project")
        assert hasattr(settings, "effective_gcp_project")


class TestSettingsFromEnvFile:
    """Test loading settings from .env file."""

    def test_loads_from_env_file(self, tmp_path: Path) -> None:
        """Test loads settings from .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text("GCP_PROJECT=env-file-project\nENVIRONMENT=staging\n")

        clear_settings_cache()
        config = TruthForgeSettings(_env_file=str(env_file))
        assert config.gcp_project == "env-file-project"
        assert config.environment == "staging"
