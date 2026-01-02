"""Databricks API client with dry-run support."""

import json
import logging
from pathlib import Path
from typing import Any

import requests

from databricks_auditor.config import AuditorConfig

logger = logging.getLogger(__name__)


class DatabricksClient:
    """Client for Databricks API with dry-run fixture support."""

    def __init__(self, config: AuditorConfig):
        self.config = config
        self.fixtures_dir = Path(__file__).parent / "fixtures"

    def _get_fixture(self, fixture_name: str) -> dict[str, Any]:
        """Load fixture data for dry-run mode."""
        fixture_path = self.fixtures_dir / fixture_name
        if not fixture_path.exists():
            logger.warning(f"Fixture not found: {fixture_name}")
            return {}

        with open(fixture_path) as f:
            return json.load(f)

    def _make_request(
        self, method: str, endpoint: str, **kwargs
    ) -> dict[str, Any]:
        """Make HTTP request to Databricks API."""
        if not self.config.databricks_host or not self.config.databricks_token:
            raise ValueError("Databricks host and token required for real mode")

        url = f"{self.config.databricks_host}/api/2.0/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.config.databricks_token}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                timeout=self.config.timeout_seconds,
                **kwargs,
            )
            response.raise_for_status()
            return response.json() if response.text else {}
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise

    def get_cluster_policies(self) -> dict[str, Any]:
        """Get cluster policies (uses fixture in dry-run mode)."""
        if self.config.is_dry_run():
            logger.info("DRY-RUN: Using fixture for cluster policies")
            return self._get_fixture("sample_policies.json")

        return self._make_request("GET", "policies/clusters/list")

    def list_clusters(self) -> dict[str, Any]:
        """List all clusters (uses fixture in dry-run mode)."""
        if self.config.is_dry_run():
            logger.info("DRY-RUN: Using fixture for clusters")
            return self._get_fixture("sample_clusters.json")

        return self._make_request("GET", "clusters/list")

    def list_secret_scopes(self) -> dict[str, Any]:
        """List secret scopes (uses fixture in dry-run mode)."""
        if self.config.is_dry_run():
            logger.info("DRY-RUN: Using fixture for secret scopes")
            return self._get_fixture("sample_secrets.json")

        return self._make_request("GET", "secrets/scopes/list")

    def get_workspace_conf(self) -> dict[str, Any]:
        """Get workspace configuration (uses fixture in dry-run mode)."""
        if self.config.is_dry_run():
            logger.info("DRY-RUN: Using fixture for workspace config")
            return self._get_fixture("sample_workspace_conf.json")

        # Note: This endpoint may require admin permissions
        try:
            return self._make_request("GET", "workspace-conf")
        except Exception as e:
            logger.warning(f"Failed to fetch workspace config: {e}")
            return {}
