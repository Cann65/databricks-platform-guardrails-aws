"""Workspace configuration compliance checks."""

import logging

from databricks_auditor.client import DatabricksClient
from databricks_auditor.report import Finding, Severity

logger = logging.getLogger(__name__)


def check_workspace_settings(client: DatabricksClient) -> list[Finding]:
    """Check workspace configuration baseline."""
    findings: list[Finding] = []

    try:
        workspace_conf = client.get_workspace_conf()

        # Check 7: Workspace configuration baseline
        if not workspace_conf:
            if client.config.is_dry_run():
                findings.append(
                    Finding(
                        check_name="workspace_configuration_baseline",
                        severity=Severity.WARN,
                        message="DRY-RUN: Workspace config check using fixture data",
                        details={"note": "In real mode, would check actual workspace settings"},
                    )
                )
            else:
                findings.append(
                    Finding(
                        check_name="workspace_configuration_baseline",
                        severity=Severity.WARN,
                        message=(
                            "Unable to retrieve workspace configuration "
                            "(may require admin permissions)"
                        ),
                        details={},
                    )
                )
        else:
            # In a real implementation, check specific settings
            # For now, just confirm we can retrieve config
            findings.append(
                Finding(
                    check_name="workspace_configuration_baseline",
                    severity=Severity.OK,
                    message="Workspace configuration retrieved successfully",
                    details={
                        "config_count": len(workspace_conf),
                        "mode": "DRY-RUN" if client.config.is_dry_run() else "REAL",
                    },
                )
            )

    except Exception as e:
        logger.error(f"Error checking workspace settings: {e}")
        findings.append(
            Finding(
                check_name="workspace_settings_check",
                severity=Severity.WARN,
                message=f"Could not check workspace settings: {str(e)}",
                details={"error": str(e)},
            )
        )

    return findings
