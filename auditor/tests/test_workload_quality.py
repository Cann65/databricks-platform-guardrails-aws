"""Lightweight tests for workload metric helpers (pure Python, no Spark required)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from workload.quality import (  # noqa: E402
    build_metric_record,
    evaluate_non_null,
    evaluate_uniqueness,
    rate,
)


def test_rate_handles_zero_division():
    assert rate(1, 0) == 0.0
    assert rate(2, 4) == 0.5


def test_evaluate_non_null_and_uniqueness():
    non_null = evaluate_non_null("id", total_rows=5, null_rows=0)
    assert non_null["status"] == "OK"
    assert non_null["details"]["null_rate"] == 0.0

    unique = evaluate_uniqueness("id", total_rows=5, distinct_rows=4)
    assert unique["status"] == "FAIL"
    assert "distinct_rate" in unique["details"]


def test_build_metric_record_shapes_output():
    metric = build_metric_record(
        run_id="run123",
        layer="bronze",
        metric_name="row_count",
        status="OK",
        value=10,
        details={"note": "test"},
    )

    assert metric["run_id"] == "run123"
    assert metric["layer"] == "bronze"
    assert metric["metric"] == "row_count"
    assert metric["status"] == "OK"
    assert metric["value"] == 10
    assert metric["details"]["note"] == "test"
