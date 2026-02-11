"""Configuration for Sovereign Cluster Manager agent."""

from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Agent configuration loaded from environment."""

    # Supabase
    supabase_url: str = Field(..., description="Supabase project URL")
    supabase_key: str = Field(..., description="Supabase anon/service key")

    # EXO
    exo_api_url: str = Field(
        default="http://localhost:8000",
        description="EXO API endpoint",
    )

    # Vault (model storage)
    vault_path: Path = Field(
        default=Path("/Volumes/Vault/models"),
        description="Path to model vault on external drive",
    )

    # Cluster
    node_id: str = Field(
        default="king",
        description="This node's identifier",
    )
    poll_interval_seconds: float = Field(
        default=5.0,
        description="How often to poll EXO and push state",
    )
    command_check_interval_seconds: float = Field(
        default=1.0,
        description="How often to check for pending commands",
    )

    # Nodes (for discovery)
    soldier_hosts: list[str] = Field(
        default=["soldier1.local", "soldier2.local", "soldier3.local"],
        description="Hostnames of soldier nodes",
    )

    model_config = {"env_prefix": "SCM_", "env_file": ".env"}


settings = Settings()
