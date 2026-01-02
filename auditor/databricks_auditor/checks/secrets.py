"""Secret scope compliance checks."""

import logging

from databricks_auditor.client import DatabricksClient
from databricks_auditor.report import Finding, Severity

logger = logging.getLogger(__name__)


def check_secret_scopes(client: DatabricksClient) -> list[Finding]:
    """Check that platform secret scope exists."""
    findings: list[Finding] = []

    try:
        scopes_response = client.list_secret_scopes()
        scopes = scopes_response.get("scopes", [])

        # Check 6: Platform secret scope exists
        platform_scope = None
        for scope in scopes:
            if scope.get("name") == "platform":
                platform_scope = scope
                break

        if not platform_scope:
            findings.append(
                Finding(
                    check_name="platform_secret_scope_exists",
                    severity=Severity.FAIL,
                    message="Platform secret scope 'platform' not found",
                    details={"available_scopes": [s.get("name") for s in scopes]},
                )
            )
        else:
            findings.append(
                Finding(
                    check_name="platform_secret_scope_exists",
                    severity=Severity.OK,
                    message="Platform secret scope 'platform' exists",
                    details={
                        "scope_name": platform_scope.get("name"),
                        "backend_type": platform_scope.get("backend_type"),
                    },
                )
            )

    except Exception as e:
        logger.error(f"Error checking secret scopes: {e}")
        findings.append(
            Finding(
                check_name="secret_scopes_check",
                severity=Severity.FAIL,
                message=f"Failed to check secret scopes: {str(e)}",
                details={"error": str(e)},
            )
        )

    return findings
