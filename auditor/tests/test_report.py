"""Tests for report generation."""


from databricks_auditor.report import (
    AuditReport,
    Finding,
    Severity,
    save,
    to_html,
    to_json,
    to_markdown,
)


def test_finding_creation():
    """Test creating a finding."""
    finding = Finding(
        check_name="test_check",
        severity=Severity.OK,
        message="Test passed",
        details={"key": "value"},
    )

    assert finding.check_name == "test_check"
    assert finding.severity == Severity.OK
    assert finding.message == "Test passed"
    assert finding.details == {"key": "value"}


def test_report_creation():
    """Test creating a report."""
    findings = [
        Finding(
            check_name="check1",
            severity=Severity.OK,
            message="Check 1 passed",
        ),
        Finding(
            check_name="check2",
            severity=Severity.WARN,
            message="Check 2 warning",
        ),
        Finding(
            check_name="check3",
            severity=Severity.FAIL,
            message="Check 3 failed",
        ),
    ]

    report = AuditReport.create(findings, dry_run=True)

    assert report.summary["total"] == 3
    assert report.summary["ok"] == 1
    assert report.summary["warn"] == 1
    assert report.summary["fail"] == 1
    assert report.dry_run is True


def test_exit_codes():
    """Test exit code logic."""
    # All OK
    report_ok = AuditReport.create(
        [
            Finding(
                check_name="check1", severity=Severity.OK, message="OK"
            )
        ],
        dry_run=True,
    )
    assert report_ok.exit_code() == 0

    # Has warnings
    report_warn = AuditReport.create(
        [
            Finding(
                check_name="check1", severity=Severity.OK, message="OK"
            ),
            Finding(
                check_name="check2",
                severity=Severity.WARN,
                message="Warning",
            ),
        ],
        dry_run=True,
    )
    assert report_warn.exit_code() == 2

    # Has failures
    report_fail = AuditReport.create(
        [
            Finding(
                check_name="check1",
                severity=Severity.FAIL,
                message="Failed",
            )
        ],
        dry_run=True,
    )
    assert report_fail.exit_code() == 3


def test_json_export():
    """Test JSON export."""
    finding = Finding(
        check_name="test", severity=Severity.OK, message="Test"
    )
    report = AuditReport.create([finding], dry_run=True)

    json_output = to_json(report)
    assert "test" in json_output
    assert "OK" in json_output
    assert "DRY-RUN" in json_output


def test_markdown_export():
    """Test Markdown export."""
    finding = Finding(
        check_name="test", severity=Severity.OK, message="Test"
    )
    report = AuditReport.create([finding], dry_run=True)

    md_output = to_markdown(report)
    assert "# Databricks Compliance Audit Report" in md_output
    assert "test" in md_output
    assert "OK" in md_output


def test_html_export():
    """Test HTML export."""
    finding = Finding(
        check_name="test", severity=Severity.OK, message="Test"
    )
    report = AuditReport.create([finding], dry_run=True)

    html_output = to_html(report)
    assert "<!DOCTYPE html>" in html_output
    assert "test" in html_output
    assert "OK" in html_output


def test_save_reports(tmp_path):
    """Test saving reports to files."""
    finding = Finding(
        check_name="test", severity=Severity.OK, message="Test"
    )
    report = AuditReport.create([finding], dry_run=True)

    save(report, tmp_path, ["json", "md", "html"])

    assert (tmp_path / "audit_report.json").exists()
    assert (tmp_path / "audit_report.md").exists()
    assert (tmp_path / "audit_report.html").exists()
