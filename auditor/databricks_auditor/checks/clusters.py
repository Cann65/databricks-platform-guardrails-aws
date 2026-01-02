"""Active cluster compliance checks."""

import logging

from databricks_auditor.client import DatabricksClient
from databricks_auditor.report import Finding, Severity

logger = logging.getLogger(__name__)


def check_clusters(client: DatabricksClient) -> list[Finding]:
    """Check for non-compliant running clusters."""
    findings: list[Finding] = []

    try:
        clusters_response = client.list_clusters()
        clusters = clusters_response.get("clusters", [])

        if not clusters:
            findings.append(
                Finding(
                    check_name="no_all_purpose_clusters",
                    severity=Severity.OK,
                    message="No clusters currently running",
                    details={"cluster_count": 0},
                )
            )
            return findings

        # Check 5: No all-purpose clusters running
        # Note: In dry-run mode, we can only warn based on fixture data
        all_purpose_clusters = []
        for cluster in clusters:
            cluster_source = cluster.get("cluster_source")
            # All-purpose clusters typically have cluster_source "UI" or null
            # Job clusters have cluster_source "JOB"
            if cluster_source != "JOB":
                all_purpose_clusters.append(
                    {
                        "cluster_id": cluster.get("cluster_id"),
                        "cluster_name": cluster.get("cluster_name"),
                        "state": cluster.get("state"),
                        "cluster_source": cluster_source,
                    }
                )

        if client.config.is_dry_run() and clusters:
            findings.append(
                Finding(
                    check_name="no_all_purpose_clusters",
                    severity=Severity.WARN,
                    message="DRY-RUN: Cannot validate cluster types from fixture data",
                    details={"cluster_count": len(clusters)},
                )
            )
        elif all_purpose_clusters:
            findings.append(
                Finding(
                    check_name="no_all_purpose_clusters",
                    severity=Severity.FAIL,
                    message=f"Found {len(all_purpose_clusters)} all-purpose cluster(s)",
                    details={"clusters": all_purpose_clusters},
                )
            )
        else:
            findings.append(
                Finding(
                    check_name="no_all_purpose_clusters",
                    severity=Severity.OK,
                    message="No all-purpose clusters detected",
                    details={"cluster_count": len(clusters)},
                )
            )

    except Exception as e:
        logger.error(f"Error checking clusters: {e}")
        findings.append(
            Finding(
                check_name="clusters_check",
                severity=Severity.FAIL,
                message=f"Failed to check clusters: {str(e)}",
                details={"error": str(e)},
            )
        )

    return findings
