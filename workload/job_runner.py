"""Databricks job-style entrypoint to run the full pipeline sequentially."""

from __future__ import annotations

import os
import sys
from typing import Optional

from workload.pipeline import DEFAULT_BASE_PATH, run_pipeline


def _get_widget_value(name: str) -> Optional[str]:
    """Return Databricks widget value if available."""
    try:
        # dbutils is injected in Databricks jobs/notebooks
        return dbutils.widgets.get(name)  # type: ignore[name-defined]
    except Exception:
        return None


def _get_param(name: str, env_var: str, default: str) -> str:
    """Resolve parameter from widget, then env var, then default."""
    widget_value = _get_widget_value(name)
    if widget_value:
        return widget_value

    env_value = os.getenv(env_var)
    if env_value:
        return env_value

    return default


def main(argv: list[str]) -> int:
    """Run bronze -> silver -> gold with simple parameter handling."""
    try:
        from pyspark.sql import SparkSession
    except ImportError as exc:  # pragma: no cover - requires Spark runtime
        print("PySpark is required to run the job runner inside Databricks.", file=sys.stderr)
        return 1

    base_path = _get_param("output_base_path", "OUTPUT_BASE_PATH", DEFAULT_BASE_PATH)
    run_id = _get_param("run_id", "RUN_ID", "")

    spark = (
        SparkSession.builder.appName("guardrails-demo-pipeline")
        .getOrCreate()
    )

    try:
        results = run_pipeline(spark, base_path=base_path, run_id=run_id or None)
        print(f"Run complete. Paths: {results}")
    except Exception as exc:  # pragma: no cover - requires Spark runtime
        print(f"Pipeline failed: {exc}", file=sys.stderr)
        return 1
    finally:
        spark.stop()

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI behavior
    sys.exit(main(sys.argv[1:]))
