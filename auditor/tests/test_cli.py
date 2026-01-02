"""Tests for CLI functionality."""

import sys
from unittest.mock import patch

import pytest

from databricks_auditor.cli import main, run_audit
from databricks_auditor.config import AuditorConfig


def test_run_audit_dry_run():
    """Test audit runs in dry-run mode without credentials."""
    config = AuditorConfig(
        databricks_host=None, databricks_token=None, dry_run=True
    )

    findings = run_audit(config)

    # Should have findings from all check modules
    assert len(findings) > 0
    assert config.is_dry_run()


def test_run_audit_with_config():
    """Test audit with explicit config."""
    config = AuditorConfig.from_env()
    findings = run_audit(config)

    # Should complete without errors
    assert isinstance(findings, list)


def test_main_no_command(capsys):
    """Test CLI with no command shows help."""
    with patch.object(sys, "argv", ["databricks_auditor"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1


def test_main_audit_command(tmp_path):
    """Test audit command execution."""
    with patch.object(
        sys,
        "argv",
        [
            "databricks_auditor",
            "audit",
            "--out",
            str(tmp_path),
            "--format",
            "json",
        ],
    ):
        # In dry-run mode, should complete with warnings or OK
        with pytest.raises(SystemExit) as exc_info:
            main()

        # Exit code should be 0, 2, or 3
        assert exc_info.value.code in [0, 2, 3]

        # Report should be generated
        report_file = tmp_path / "audit_report.json"
        assert report_file.exists()


def test_config_redaction():
    """Test that config properly redacts sensitive data."""
    config = AuditorConfig(
        databricks_host="https://example.databricks.com",
        databricks_token="dapi123456789",
        dry_run=False,
    )

    # Token should never appear in redacted output
    redacted = config.redacted_host()
    assert "dapi" not in redacted
    assert config.databricks_host in redacted
