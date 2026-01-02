"""Lightweight, pure-Python helpers for workload data quality metrics.

These helpers intentionally avoid PySpark dependencies so they can be unit tested
locally and used by both notebooks and the job runner.
"""

from __future__ import annotations

from typing import Dict, Optional


def rate(numerator: int, denominator: int) -> float:
    """Return a safe ratio (0.0 if denominator is zero)."""
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 4)


def evaluate_non_null(column: str, total_rows: int, null_rows: int) -> Dict[str, object]:
    """Return a metric record for non-null enforcement on a column."""
    status = "OK" if null_rows == 0 else "FAIL"
    return {
        "metric_name": f"{column}_non_null",
        "status": status,
        "value": null_rows,
        "details": {
            "null_rows": null_rows,
            "total_rows": total_rows,
            "null_rate": rate(null_rows, total_rows),
        },
    }


def evaluate_uniqueness(
    column: str, total_rows: int, distinct_rows: int
) -> Dict[str, object]:
    """Return a metric record for uniqueness enforcement on a column."""
    status = "OK" if total_rows == distinct_rows else "FAIL"
    return {
        "metric_name": f"{column}_unique",
        "status": status,
        "value": distinct_rows,
        "details": {
            "distinct_rows": distinct_rows,
            "total_rows": total_rows,
            "distinct_rate": rate(distinct_rows, total_rows),
        },
    }


def build_metric_record(
    run_id: str,
    layer: str,
    metric_name: str,
    status: str,
    value: Optional[object] = None,
    details: Optional[Dict[str, object]] = None,
) -> Dict[str, object]:
    """Normalize metric output for persistence to Delta."""
    return {
        "run_id": run_id,
        "layer": layer,
        "metric": metric_name,
        "status": status,
        "value": value,
        "details": details or {},
    }
