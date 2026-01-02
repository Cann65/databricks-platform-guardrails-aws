"""Report generation for audit findings.

Design:
- Prefer pydantic when available (nice validation/serialization).
- Fall back to dataclasses on platforms where pydantic-core wheels are not available.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

# Optional pydantic support
try:
    from pydantic import BaseModel  # type: ignore

    _HAS_PYDANTIC = True
except Exception:  # pragma: no cover
    BaseModel = object  # type: ignore
    _HAS_PYDANTIC = False


class Severity(str, Enum):
    OK = "OK"
    WARN = "WARN"
    FAIL = "FAIL"


# ---- Shared data structures (pydantic OR dataclasses) ----

if _HAS_PYDANTIC:

    class Finding(BaseModel):
        check_name: str
        severity: Severity
        message: str
        details: dict[str, Any] = {}

    class AuditReport(BaseModel):
        timestamp: str
        environment: str
        dry_run: bool
        findings: list[Finding]
        summary: dict[str, int]

        @classmethod
        def create(cls, findings: list[Finding], dry_run: bool) -> AuditReport:
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
            if self.summary["fail"] > 0:
                return 3
            if self.summary["warn"] > 0:
                return 2
            return 0

        def to_json(self) -> str:
            return self.model_dump_json(indent=2)

        def _as_plain(self) -> dict[str, Any]:
            return self.model_dump()

else:

    @dataclass
    class Finding:
        check_name: str
        severity: Severity
        message: str
        details: dict[str, Any] = field(default_factory=dict)

    @dataclass
    class AuditReport:
        timestamp: str
        environment: str
        dry_run: bool
        findings: list[Finding]
        summary: dict[str, int]

        @classmethod
        def create(cls, findings: list[Finding], dry_run: bool) -> AuditReport:
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
            if self.summary["fail"] > 0:
                return 3
            if self.summary["warn"] > 0:
                return 2
            return 0

        def _as_plain(self) -> dict[str, Any]:
            return {
                "timestamp": self.timestamp,
                "environment": self.environment,
                "dry_run": self.dry_run,
                "findings": [asdict(f) for f in self.findings],
                "summary": self.summary,
            }

        def to_json(self) -> str:
            return json.dumps(self._as_plain(), indent=2)


# ---- Rendering / export: same for both paths ----


def _finding_to_dict(f: Any) -> dict[str, Any]:
    if _HAS_PYDANTIC:
        return f.model_dump()
    return asdict(f)


def _report_to_dict(r: Any) -> dict[str, Any]:
    if _HAS_PYDANTIC:
        return r.model_dump()
    return r._as_plain()


def _mode_label(dry_run: bool) -> str:
    return "DRY-RUN (using fixtures)" if dry_run else "REAL"


def _json_pretty(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


def to_markdown(report: AuditReport) -> str:
    lines = [
        "# Databricks Compliance Audit Report",
        "",
        f"**Timestamp:** {report.timestamp}",
        f"**Environment:** {report.environment}",
        f"**Mode:** {_mode_label(report.dry_run)}",
        "",
        "## Summary",
        "",
        f"- Total Checks: {report.summary['total']}",
        f"- OK:   {report.summary['ok']}",
        f"- WARN: {report.summary['warn']}",
        f"- FAIL: {report.summary['fail']}",
        "",
        "## Findings",
        "",
    ]

    for severity in [Severity.FAIL, Severity.WARN, Severity.OK]:
        sev_findings = [f for f in report.findings if f.severity == severity]
        if not sev_findings:
            continue

        lines.append(f"### {severity.value}")
        lines.append("")

        for f in sev_findings:
            fd = _finding_to_dict(f)
            lines.append(f"**{fd['check_name']}**")
            lines.append(f"- {fd['message']}")
            if fd.get("details"):
                lines.append(f"- Details: {_json_pretty(fd['details'])}")
            lines.append("")

    return "\n".join(lines)


def to_html(report: AuditReport) -> str:
    data = _report_to_dict(report)
    severity_colors = {"FAIL": "#dc3545", "WARN": "#ffc107", "OK": "#28a745"}

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
        ".severity { display: inline-block; padding: 2px 8px; border-radius: 3px; "
        "color: white; font-size: 12px; font-weight: bold; }",
        "pre { background: #f4f4f4; padding: 10px; border-radius: 3px; overflow-x: auto; }",
        "</style>",
        "</head>",
        "<body>",
        "<h1>Databricks Compliance Audit Report</h1>",
        "<div class='header'>",
        f"<p><strong>Timestamp:</strong> {data['timestamp']}</p>",
        f"<p><strong>Environment:</strong> {data['environment']}</p>",
        f"<p><strong>Mode:</strong> {_mode_label(data['dry_run'])}</p>",
        "</div>",
        "<h2>Summary</h2>",
        "<div class='summary'>",
        f"<div class='summary-card' style='background: {severity_colors['OK']}20;'>"
        f"<h3>{data['summary']['ok']}</h3><p>OK</p></div>",
        f"<div class='summary-card' style='background: {severity_colors['WARN']}20;'>"
        f"<h3>{data['summary']['warn']}</h3><p>WARN</p></div>",
        f"<div class='summary-card' style='background: {severity_colors['FAIL']}20;'>"
        f"<h3>{data['summary']['fail']}</h3><p>FAIL</p></div>",
        "</div>",
        "<h2>Findings</h2>",
        "<div class='findings'>",
    ]

    for f in data["findings"]:
        sev = f["severity"]
        html_parts.append(f"<div class='finding finding-{sev.lower()}'>")
        html_parts.append(
            f"<h4>{f['check_name']} "
            f"<span class='severity' style='background: {severity_colors[sev]};'>"
            f"{sev}</span></h4>"
        )
        html_parts.append(f"<p>{f['message']}</p>")
        if f.get("details"):
            html_parts.append(f"<pre>{_json_pretty(f['details'])}</pre>")
        html_parts.append("</div>")

    html_parts.extend(["</div>", "</body>", "</html>"])
    return "\n".join(html_parts)


def to_json(report: AuditReport) -> str:
    """Convert report to JSON string."""
    if _HAS_PYDANTIC:
        return report.to_json()  # type: ignore
    else:
        # Dataclasses fallback
        data = _report_to_dict(report)
        return json.dumps(data, indent=2)


def save(report: AuditReport, output_dir: Path, formats: list[str]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    for fmt in formats:
        if fmt == "json":
            (output_dir / "audit_report.json").write_text(
                to_json(report), encoding="utf-8"
            )
            print(f"Report saved: {output_dir / 'audit_report.json'}")
        elif fmt == "md":
            (output_dir / "audit_report.md").write_text(
                to_markdown(report), encoding="utf-8"
            )
            print(f"Report saved: {output_dir / 'audit_report.md'}")
        elif fmt == "html":
            (output_dir / "audit_report.html").write_text(
                to_html(report), encoding="utf-8"
            )
            print(f"Report saved: {output_dir / 'audit_report.html'}")
        else:
            raise ValueError(f"Unknown format: {fmt}")
