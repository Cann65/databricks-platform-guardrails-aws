"""Tag and cost control compliance checks."""

import json
import logging

from databricks_auditor.client import DatabricksClient
from databricks_auditor.report import Finding, Severity

logger = logging.getLogger(__name__)


def check_tags_cost_controls(client: DatabricksClient) -> list[Finding]:
    """Check that required tags and cost controls are enforced."""
    findings: list[Finding] = []

    try:
        policies_response = client.get_cluster_policies()
        policies = policies_response.get("policies", [])

        guardrails_policy = None
        for policy in policies:
            if policy.get("name") == "guardrails-default":
                guardrails_policy = policy
                break

        if not guardrails_policy:
            # Already reported by cluster_policies check
            return findings

        definition_str = guardrails_policy.get("definition", "{}")
        try:
            definition = json.loads(definition_str)
        except json.JSONDecodeError:
            return findings

        # Check 3: Max workers <= 8
        max_workers_configs = [
            definition.get("autoscale.max_workers", {}),
            definition.get("num_workers", {}),
        ]

        max_workers_values = []
        for config in max_workers_configs:
            if isinstance(config, dict) and "maxValue" in config:
                max_workers_values.append(config["maxValue"])

        if not max_workers_values:
            findings.append(
                Finding(
                    check_name="max_workers_enforced",
                    severity=Severity.WARN,
                    message="Max workers not enforced in policy",
                    details={"policy_sections": max_workers_configs},
                )
            )
        elif all(v <= 8 for v in max_workers_values):
            findings.append(
                Finding(
                    check_name="max_workers_enforced",
                    severity=Severity.OK,
                    message=f"Max workers enforced at {max(max_workers_values)} (≤8)",
                    details={"max_values": max_workers_values},
                )
            )
        else:
            findings.append(
                Finding(
                    check_name="max_workers_enforced",
                    severity=Severity.FAIL,
                    message=f"Max workers {max(max_workers_values)} exceeds 8",
                    details={"max_values": max_workers_values, "expected": "≤8"},
                )
            )

        # Check 4: Required tags enforced
        required_tags = ["owner", "cost_center", "env"]
        tag_checks = {}

        for tag in required_tags:
            tag_key = f"custom_tags.{tag}"
            tag_config = definition.get(tag_key, {})
            tag_checks[tag] = tag_config

        missing_tags = [tag for tag in required_tags if not tag_checks.get(tag)]

        if not missing_tags:
            findings.append(
                Finding(
                    check_name="required_tags_enforced",
                    severity=Severity.OK,
                    message=f"All required tags enforced: {', '.join(required_tags)}",
                    details={"tags": tag_checks},
                )
            )
        else:
            findings.append(
                Finding(
                    check_name="required_tags_enforced",
                    severity=Severity.FAIL,
                    message=f"Missing required tags in policy: {', '.join(missing_tags)}",
                    details={
                        "missing_tags": missing_tags,
                        "configured_tags": tag_checks,
                    },
                )
            )

    except Exception as e:
        logger.error(f"Error checking tags and cost controls: {e}")
        findings.append(
            Finding(
                check_name="tags_cost_controls_check",
                severity=Severity.FAIL,
                message=f"Failed to check tags and cost controls: {str(e)}",
                details={"error": str(e)},
            )
        )

    return findings
