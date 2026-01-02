"""Report generation for audit findings."""

import json
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel


class Severity(str, Enum):
    """Finding severity levels."""

    OK = "OK"
    WARN = "WARN"
    FAIL = "FAIL"


class Finding(BaseModel):
    """Individual audit finding."""

    check_name: str
    severity: Severity
    message: str
    details: dict[str, Any] = {}


class AuditReport(BaseModel):
    """Complete audit report."""

    timestamp: str
    environment: str
    dry_run: bool
    findings: list[Finding]
    summary: dict[str, int]

    @classmethod
    def create(
        cls, findings: list[Finding], dry_run: bool
    ) -> "AuditReport":
        """Create report from findings."""
        summary = {
            "total": len(findings),
            "ok": sum(1 for f in findings if f.severity == Severity.OK),
            "warn": sum(1 for f in findings if f.severity == Severity.WARN),
            "fail": sum(1 for f in findings if f.severity == Severity.FAIL),
        }

        return cls(
            timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            environment="DRY-RUN" if dry_run else "REAL",
            dry_run=dry_run,
            findings=findings,
            summary=summary,
        )

    def exit_code(self) -> int:
        """Determine exit code based on findings."""
        if self.summary["fail"] > 0:
            return 3
        elif self.summary["warn"] > 0:
            return 2
        return 0

    def to_json(self) -> str:
        """Export report as JSON."""
        return self.model_dump_json(indent=2)

    def to_markdown(self) -> str:
        """Export report as Markdown."""
        lines = [
            "# Databricks Compliance Audit Report",
            "",
            f"**Timestamp:** {self.timestamp}",
            f"**Environment:** {self.environment}",
            f"**Mode:** {'DRY-RUN (using fixtures)' if self.dry_run else 'REAL'}",
            "",
            "## Summary",
            "",
            f"- Total Checks: {self.summary['total']}",
            f"- ✅ OK: {self.summary['ok']}",
            f"- ⚠️  WARN: {self.summary['warn']}",
            f"- ❌ FAIL: {self.summary['fail']}",
            "",
            "## Findings",
            "",
        ]

        # Group by severity
        for severity in [Severity.FAIL, Severity.WARN, Severity.OK]:
            severity_findings = [
                f for f in self.findings if f.severity == severity
            ]
            if not severity_findings:
                continue

            emoji = {"FAIL": "❌", "WARN": "⚠️", "OK": "✅"}[severity.value]
            lines.append(f"### {emoji} {severity.value}")
            lines.append("")

            for finding in severity_findings:
                lines.append(f"**{finding.check_name}**")
                lines.append(f"- {finding.message}")
                if finding.details:
                    lines.append(f"- Details: {json.dumps(finding.details, indent=2)}")
                lines.append("")

        return "\n".join(lines)

    def to_html(self) -> str:
        """Export report as HTML."""
        severity_colors = {
            "FAIL": "#dc3545",
            "WARN": "#ffc107",
            "OK": "#28a745",
        }

        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<meta charset='utf-8'>",
            "<title>Databricks Compliance Audit Report</title>",
            "<style>",
            "body { font-family: Arial, sans-serif; max-width: 1200px; "
            "margin: 40px auto; padding: 20px; }",
            "h1 { color: #333; }",
            ".header { background: #f8f9fa; padding: 20px; border-radius: 5px; "
            "margin-bottom: 30px; }",
            ".summary { display: flex; gap: 20px; margin: 20px 0; }",
            ".summary-card { flex: 1; padding: 20px; border-radius: 5px; text-align: center; }",
            ".summary-card h3 { margin: 0; font-size: 32px; }",
            ".summary-card p { margin: 5px 0 0 0; color: #666; }",
            ".findings { margin-top: 30px; }",
            ".finding { padding: 15px; margin: 10px 0; border-left: 4px solid; "
            "border-radius: 3px; background: #f8f9fa; }",
            ".finding-ok { border-color: #28a745; }",
            ".finding-warn { border-color: #ffc107; }",
            ".finding-fail { border-color: #dc3545; }",
            ".finding h4 { margin: 0 0 10px 0; }",
            ".severity { display: inline-block; padding: 2px 8px; border-radius: 3px; "
            "color: white; font-size: 12px; font-weight: bold; }",
            "pre { background: #f4f4f4; padding: 10px; border-radius: 3px; overflow-x: auto; }",
            "</style>",
            "</head>",
            "<body>",
            "<h1>Databricks Compliance Audit Report</h1>",
            "<div class='header'>",
            f"<p><strong>Timestamp:</strong> {self.timestamp}</p>",
            f"<p><strong>Environment:</strong> {self.environment}</p>",
            f"<p><strong>Mode:</strong> "
            f"{'DRY-RUN (using fixtures)' if self.dry_run else 'REAL'}</p>",
            "</div>",
            "<h2>Summary</h2>",
            "<div class='summary'>",
            f"<div class='summary-card' style='background: {severity_colors['OK']}20;'>",
            f"<h3>{self.summary['ok']}</h3><p>OK</p></div>",
            f"<div class='summary-card' style='background: {severity_colors['WARN']}20;'>",
            f"<h3>{self.summary['warn']}</h3><p>WARN</p></div>",
            f"<div class='summary-card' style='background: {severity_colors['FAIL']}20;'>",
            f"<h3>{self.summary['fail']}</h3><p>FAIL</p></div>",
            "</div>",
            "<h2>Findings</h2>",
            "<div class='findings'>",
        ]

        for finding in self.findings:
            severity_class = f"finding-{finding.severity.value.lower()}"
            severity_bg = severity_colors[finding.severity.value]
            html_parts.extend(
                [
                    f"<div class='finding {severity_class}'>",
                    f"<h4>{finding.check_name} "
                    f"<span class='severity' style='background: {severity_bg};'>"
                    f"{finding.severity.value}</span></h4>",
                    f"<p>{finding.message}</p>",
                ]
            )
            if finding.details:
                html_parts.append(
                    f"<pre>{json.dumps(finding.details, indent=2)}</pre>"
                )
            html_parts.append("</div>")

        html_parts.extend(["</div>", "</body>", "</html>"])

        return "\n".join(html_parts)

    def save(self, output_dir: Path, formats: list[str]):
        """Save report to files in specified formats."""
        output_dir.mkdir(parents=True, exist_ok=True)

        for fmt in formats:
            if fmt == "json":
                output_file = output_dir / "audit_report.json"
                output_file.write_text(self.to_json(), encoding="utf-8")
            elif fmt == "md":
                output_file = output_dir / "audit_report.md"
                output_file.write_text(self.to_markdown(), encoding="utf-8")
            elif fmt == "html":
                output_file = output_dir / "audit_report.html"
                output_file.write_text(self.to_html(), encoding="utf-8")
            else:
                raise ValueError(f"Unknown format: {fmt}")

            print(f"Report saved: {output_file}")
