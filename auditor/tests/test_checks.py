"""Tests for compliance checks."""

from databricks_auditor.checks import (
    check_cluster_policies,
    check_clusters,
    check_secret_scopes,
    check_tags_cost_controls,
    check_workspace_settings,
)
from databricks_auditor.client import DatabricksClient
from databricks_auditor.config import AuditorConfig
from databricks_auditor.report import Severity


def get_dry_run_client():
    """Get a client in dry-run mode."""
    config = AuditorConfig(
        databricks_host=None, databricks_token=None, dry_run=True
    )
    return DatabricksClient(config)


def test_check_cluster_policies():
    """Test cluster policy checks."""
    client = get_dry_run_client()
    findings = check_cluster_policies(client)

    assert len(findings) > 0

    # Should find the guardrails-default policy in fixtures
    policy_exists = any(
        f.check_name == "cluster_policy_exists" for f in findings
    )
    assert policy_exists


def test_check_tags_cost_controls():
    """Test tags and cost control checks."""
    client = get_dry_run_client()
    findings = check_tags_cost_controls(client)

    assert len(findings) >= 0

    # Should check max_workers and required tags
    check_names = [f.check_name for f in findings]
    assert (
        "max_workers_enforced" in check_names
        or "required_tags_enforced" in check_names
    )


def test_check_clusters():
    """Test cluster checks."""
    client = get_dry_run_client()
    findings = check_clusters(client)

    assert len(findings) > 0

    # Should check for all-purpose clusters
    cluster_check = any(
        f.check_name == "no_all_purpose_clusters" for f in findings
    )
    assert cluster_check


def test_check_secret_scopes():
    """Test secret scope checks."""
    client = get_dry_run_client()
    findings = check_secret_scopes(client)

    assert len(findings) > 0

    # Should find the platform secret scope
    scope_check = any(
        f.check_name == "platform_secret_scope_exists" for f in findings
    )
    assert scope_check


def test_check_workspace_settings():
    """Test workspace settings checks."""
    client = get_dry_run_client()
    findings = check_workspace_settings(client)

    assert len(findings) > 0


def test_all_checks_complete():
    """Test that all checks can run without errors."""
    client = get_dry_run_client()

    all_findings = []
    all_findings.extend(check_cluster_policies(client))
    all_findings.extend(check_tags_cost_controls(client))
    all_findings.extend(check_clusters(client))
    all_findings.extend(check_secret_scopes(client))
    all_findings.extend(check_workspace_settings(client))

    # Should have multiple findings
    assert len(all_findings) >= 5

    # All findings should have required fields
    for finding in all_findings:
        assert finding.check_name
        assert finding.severity in [Severity.OK, Severity.WARN, Severity.FAIL]
        assert finding.message
