"""CLI for Databricks compliance auditor."""

import argparse
import logging
import sys
from pathlib import Path

from databricks_auditor.checks import (
    check_cluster_policies,
    check_clusters,
    check_secret_scopes,
    check_tags_cost_controls,
    check_workspace_settings,
)
from databricks_auditor.client import DatabricksClient
from databricks_auditor.config import AuditorConfig
from databricks_auditor.report import AuditReport, Finding, save

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_audit(config: AuditorConfig) -> list[Finding]:
    """Run all compliance checks."""
    client = DatabricksClient(config)
    findings: list[Finding] = []

    logger.info(f"Running audit in {'DRY-RUN' if config.is_dry_run() else 'REAL'} mode")

    # Run all checks
    check_functions = [
        check_cluster_policies,
        check_tags_cost_controls,
        check_clusters,
        check_secret_scopes,
        check_workspace_settings,
    ]

    for check_func in check_functions:
        try:
            logger.info(f"Running check: {check_func.__name__}")
            check_findings = check_func(client)
            findings.extend(check_findings)
        except Exception as e:
            logger.error(f"Check {check_func.__name__} failed: {e}")
            from databricks_auditor.report import Severity

            findings.append(
                Finding(
                    check_name=check_func.__name__,
                    severity=Severity.FAIL,
                    message=f"Check execution failed: {str(e)}",
                    details={"error": str(e)},
                )
            )

    return findings


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Databricks compliance auditor with dry-run support"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Audit command
    audit_parser = subparsers.add_parser(
        "audit", help="Run compliance audit"
    )
    audit_parser.add_argument(
        "--out",
        type=str,
        default="reports",
        help="Output directory for reports (default: reports)",
    )
    audit_parser.add_argument(
        "--format",
        type=str,
        default="html,md,json",
        help="Report formats (comma-separated: html,md,json)",
    )

    args = parser.parse_args()

    if args.command != "audit":
        parser.print_help()
        sys.exit(1)

    # Load configuration
    config = AuditorConfig.from_env()

    # Run audit
    findings = run_audit(config)

    # Generate report
    report = AuditReport.create(findings, dry_run=config.is_dry_run())

    # Save reports
    output_dir = Path(args.out)
    formats = [fmt.strip() for fmt in args.format.split(",")]
    save(report, output_dir, formats)

    # Print summary (avoid emojis for Windows compatibility)
    print("\n" + "=" * 60)
    print("AUDIT SUMMARY")
    print("=" * 60)
    print(f"Total checks: {report.summary['total']}")
    print(f"[OK]   {report.summary['ok']}")
    print(f"[WARN] {report.summary['warn']}")
    print(f"[FAIL] {report.summary['fail']}")
    print("=" * 60)

    # Exit with appropriate code
    exit_code = report.exit_code()
    if exit_code == 0:
        print("[PASS] All checks passed!")
    elif exit_code == 2:
        print("[WARN] Some checks returned warnings")
    else:
        print("[FAIL] Some checks failed!")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
