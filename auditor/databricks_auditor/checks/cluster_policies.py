"""Cluster policy compliance checks."""

import json
import logging

from databricks_auditor.client import DatabricksClient
from databricks_auditor.report import Finding, Severity

logger = logging.getLogger(__name__)


def check_cluster_policies(client: DatabricksClient) -> list[Finding]:
    """Check that guardrails cluster policy exists with correct settings."""
    findings: list[Finding] = []

    try:
        policies_response = client.get_cluster_policies()
        policies = policies_response.get("policies", [])

        # Check 1: Policy exists
        guardrails_policy = None
        for policy in policies:
            if policy.get("name") == "guardrails-default":
                guardrails_policy = policy
                break

        if not guardrails_policy:
            findings.append(
                Finding(
                    check_name="cluster_policy_exists",
                    severity=Severity.FAIL,
                    message="Guardrails cluster policy 'guardrails-default' not found",
                    details={"available_policies": [p.get("name") for p in policies]},
                )
            )
            return findings

        findings.append(
            Finding(
                check_name="cluster_policy_exists",
                severity=Severity.OK,
                message="Guardrails cluster policy 'guardrails-default' exists",
                details={"policy_id": guardrails_policy.get("policy_id")},
            )
        )

        # Parse policy definition
        definition_str = guardrails_policy.get("definition", "{}")
        try:
            definition = json.loads(definition_str)
        except json.JSONDecodeError:
            findings.append(
                Finding(
                    check_name="cluster_policy_definition",
                    severity=Severity.FAIL,
                    message="Failed to parse cluster policy definition",
                    details={"definition": definition_str},
                )
            )
            return findings

        # Check 2: Auto-termination <= 15 minutes
        auto_term = definition.get("autotermination_minutes", {})
        max_auto_term = auto_term.get("maxValue")

        if max_auto_term is None:
            findings.append(
                Finding(
                    check_name="auto_termination_enforced",
                    severity=Severity.WARN,
                    message="Auto-termination not enforced in policy",
                    details={"policy_section": auto_term},
                )
            )
        elif max_auto_term <= 15:
            findings.append(
                Finding(
                    check_name="auto_termination_enforced",
                    severity=Severity.OK,
                    message=f"Auto-termination enforced at {max_auto_term} minutes (≤15)",
                    details={"max_value": max_auto_term},
                )
            )
        else:
            findings.append(
                Finding(
                    check_name="auto_termination_enforced",
                    severity=Severity.FAIL,
                    message=f"Auto-termination max value {max_auto_term} exceeds 15 minutes",
                    details={"max_value": max_auto_term, "expected": "≤15"},
                )
            )

    except Exception as e:
        logger.error(f"Error checking cluster policies: {e}")
        findings.append(
            Finding(
                check_name="cluster_policy_check",
                severity=Severity.FAIL,
                message=f"Failed to check cluster policies: {str(e)}",
                details={"error": str(e)},
            )
        )

    return findings
