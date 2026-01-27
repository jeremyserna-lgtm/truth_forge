"""Centralized configuration with validation.

RISK MITIGATION: Replaces 48 scattered environment variables with
a single validated configuration object.

Usage:
    from truth_forge.core.settings import settings

    # Access configuration
    project_id = settings.gcp_project
    api_key = settings.google_api_key

    # For testing, create custom settings
    test_settings = TruthForgeSettings(gcp_project="test-project")
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class TruthForgeSettings(BaseSettings):
    """Centralized configuration for truth_forge.

    All environment variables are documented and validated here.
    Settings are loaded from:
    1. Environment variables
    2. .env file (if exists)
    3. Default values

    Environment variable names are automatically derived from field names
    (uppercase with underscores).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore unknown env vars
    )

    # =========================================================================
    # Project Identity
    # =========================================================================

    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Deployment environment",
    )

    service_version: str = Field(
        default="1.0.0",
        description="Current service version",
    )

    # =========================================================================
    # GCP Configuration
    # =========================================================================

    gcp_project: str = Field(
        default="",
        description="Google Cloud project ID (required for BigQuery/GCS)",
        alias="GCP_PROJECT",
    )

    google_cloud_project: str | None = Field(
        default=None,
        description="Alternate GCP project env var",
        alias="GOOGLE_CLOUD_PROJECT",
    )

    bigquery_location: str = Field(
        default="US",
        description="BigQuery dataset location",
        alias="BIGQUERY_LOCATION",
    )

    bigquery_max_rows: int = Field(
        default=1_000_000,
        description="Maximum rows to return from BigQuery",
        alias="BIGQUERY_MAX_ROWS",
    )

    bigquery_max_timeout: int = Field(
        default=3600,
        description="Maximum BigQuery query timeout in seconds",
        alias="BIGQUERY_MAX_TIMEOUT",
    )

    bigquery_max_query_length: int = Field(
        default=1_000_000,
        description="Maximum query string length",
        alias="BIGQUERY_MAX_QUERY_LENGTH",
    )

    # =========================================================================
    # Session Limits (Cost Governance)
    # =========================================================================

    bq_session_max_bytes: int = Field(
        default=5 * 1024**3,  # 5 GB
        description="Maximum bytes processed per BigQuery session",
        alias="BQ_SESSION_MAX_BYTES",
    )

    bq_session_max_queries: int = Field(
        default=500,
        description="Maximum queries per BigQuery session",
        alias="BQ_SESSION_MAX_QUERIES",
    )

    bq_session_warning_bytes: int = Field(
        default=2 * 1024**3,  # 2 GB
        description="Warning threshold for bytes processed",
        alias="BQ_SESSION_WARNING_BYTES",
    )

    bq_session_warning_queries: int = Field(
        default=20,
        description="Warning threshold for query count",
        alias="BQ_SESSION_WARNING_QUERIES",
    )

    gemini_max_calls_per_session: int = Field(
        default=1000,
        description="Maximum Gemini API calls per session",
        alias="GEMINI_MAX_CALLS_PER_SESSION",
    )

    gemini_max_tokens_per_session: int = Field(
        default=10_000_000,
        description="Maximum tokens per Gemini session",
        alias="GEMINI_MAX_TOKENS_PER_SESSION",
    )

    gemini_max_cost_per_session: float = Field(
        default=10.0,
        description="Maximum cost in USD per Gemini session",
        alias="GEMINI_MAX_COST_PER_SESSION",
    )

    gemini_min_call_interval: float = Field(
        default=0.1,
        description="Minimum seconds between Gemini calls",
        alias="GEMINI_MIN_CALL_INTERVAL",
    )

    # =========================================================================
    # API Keys (Sensitive - Never log these)
    # =========================================================================

    google_api_key: str | None = Field(
        default=None,
        description="Google API key for Gemini, Search, etc.",
        alias="GOOGLE_API_KEY",
    )

    gemini_api_key: str | None = Field(
        default=None,
        description="Gemini-specific API key (falls back to GOOGLE_API_KEY)",
        alias="GEMINI_API_KEY",
    )

    anthropic_api_key: str | None = Field(
        default=None,
        description="Anthropic API key for Claude",
        alias="ANTHROPIC_API_KEY",
    )

    openai_api_key: str | None = Field(
        default=None,
        description="OpenAI API key for GPT models",
        alias="OPENAI_API_KEY",
    )

    serpapi_key: str | None = Field(
        default=None,
        description="SerpAPI key for web search",
        alias="SERPAPI_KEY",
    )

    github_token: str | None = Field(
        default=None,
        description="GitHub personal access token",
        alias="GITHUB_TOKEN",
    )

    primitive_engine_api_key: str | None = Field(
        default=None,
        description="Primitive Engine API key",
        alias="PRIMITIVE_ENGINE_API_KEY",
    )

    # =========================================================================
    # External Services
    # =========================================================================

    google_cse_id: str | None = Field(
        default=None,
        description="Google Custom Search Engine ID",
        alias="GOOGLE_CSE_ID",
    )

    mw_dictionary_key: str | None = Field(
        default=None,
        description="Merriam-Webster Dictionary API key",
        alias="MW_DICTIONARY_KEY",
    )

    mw_thesaurus_key: str | None = Field(
        default=None,
        description="Merriam-Webster Thesaurus API key",
        alias="MW_THESAURUS_KEY",
    )

    twenty_base_url: str = Field(
        default="https://api.twenty.com",
        description="Twenty CRM base URL",
        alias="TWENTY_BASE_URL",
    )

    # =========================================================================
    # Federation
    # =========================================================================

    federation_hub: str | None = Field(
        default=None,
        description="Federation hub URL for organism sync",
        alias="FEDERATION_HUB",
    )

    federation_key: str | None = Field(
        default=None,
        description="Federation API key",
        alias="FEDERATION_KEY",
    )

    organism_id: str | None = Field(
        default=None,
        description="This organism's unique identifier",
        alias="ORGANISM_ID",
    )

    # =========================================================================
    # Governance
    # =========================================================================

    governance_enable_alerts: bool = Field(
        default=False,
        description="Enable governance alerts",
        alias="GOVERNANCE_ENABLE_ALERTS",
    )

    governance_alert_pubsub_topic: str | None = Field(
        default=None,
        description="PubSub topic for governance alerts",
        alias="GOVERNANCE_ALERT_PUBSUB_TOPIC",
    )

    budget_cache_ttl_seconds: int = Field(
        default=300,
        description="Budget cache TTL in seconds",
        alias="BUDGET_CACHE_TTL_SECONDS",
    )

    # =========================================================================
    # Paths (Override detection)
    # =========================================================================

    truth_forge_root: str | None = Field(
        default=None,
        description="Override for project root detection",
        alias="TRUTH_FORGE_ROOT",
    )

    # =========================================================================
    # Computed Properties
    # =========================================================================

    @property
    def effective_gcp_project(self) -> str | None:
        """Get effective GCP project ID from multiple sources."""
        return self.gcp_project or self.google_cloud_project or None

    @property
    def effective_gemini_key(self) -> str | None:
        """Get effective Gemini API key."""
        return self.gemini_api_key or self.google_api_key

    @field_validator("gcp_project")
    @classmethod
    def validate_gcp_project(cls, v: str) -> str:
        """Warn if using default project ID."""
        if v == "flash-clover-464719-g1":
            import warnings

            warnings.warn(
                "Using default GCP project ID. Set GCP_PROJECT environment variable.",
                UserWarning,
                stacklevel=2,
            )
        return v

    def get_project_root(self) -> Path:
        """Get project root path."""
        if self.truth_forge_root:
            return Path(self.truth_forge_root)

        # Import here to avoid circular dependency
        from truth_forge.core.paths import get_project_root

        return get_project_root()


@lru_cache(maxsize=1)
def get_settings() -> TruthForgeSettings:
    """Get cached settings instance.

    Returns:
        TruthForgeSettings instance.
    """
    return TruthForgeSettings()


# Singleton instance for convenience
settings = get_settings()


def clear_settings_cache() -> None:
    """Clear settings cache (for testing)."""
    get_settings.cache_clear()
