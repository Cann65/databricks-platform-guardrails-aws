"""Configuration management for the auditor."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class AuditorConfig:
    """Configuration for Databricks auditor."""

    databricks_host: Optional[str]
    databricks_token: Optional[str]
    dry_run: bool
    timeout_seconds: int = 30

    @classmethod
    def from_env(cls) -> "AuditorConfig":
        """Create config from environment variables."""
        host = os.getenv("DATABRICKS_HOST")
        token = os.getenv("DATABRICKS_TOKEN")

        # Dry-run mode if credentials not provided
        dry_run = not (host and token)

        return cls(
            databricks_host=host,
            databricks_token=token,
            dry_run=dry_run,
        )

    def is_dry_run(self) -> bool:
        """Check if running in dry-run mode."""
        return self.dry_run

    def redacted_host(self) -> str:
        """Return host with sensitive info redacted."""
        if not self.databricks_host:
            return "DRY-RUN"
        return self.databricks_host
