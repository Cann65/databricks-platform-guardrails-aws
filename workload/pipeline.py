"""PySpark pipeline steps for the Databricks demo workload."""

from __future__ import annotations

import datetime as _dt
from typing import TYPE_CHECKING, Dict, List

from workload.quality import (
    build_metric_record,
    evaluate_non_null,
    evaluate_uniqueness,
)

if TYPE_CHECKING:
    from pyspark.sql import SparkSession


DEFAULT_BASE_PATH = "dbfs:/tmp/guardrails_demo"


def _persist_metrics(
    spark: "SparkSession",
    base_path: str,
    layer: str,
    run_id: str,
    metric_rows: List[Dict[str, object]],
) -> None:
    """Write metric rows to a Delta metrics table."""
    metrics_df = spark.createDataFrame(metric_rows)
    metrics_path = f"{base_path}/metrics"
    metrics_df.write.format("delta").mode("append").save(metrics_path)


def ingest_bronze(
    spark: "SparkSession", base_path: str = DEFAULT_BASE_PATH, run_id: str | None = None
) -> str:
    """Generate synthetic bronze data and write to Delta."""
    from pyspark.sql import functions as F
    from pyspark.sql import types as T

    actual_run_id = run_id or _dt.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    bronze_path = f"{base_path}/bronze"

    sample_data = [
        {"id": 1, "user_id": "u1", "event_type": "purchase", "amount": 42.5, "ts": "2024-10-01T12:00:00Z"},
        {"id": 2, "user_id": "u2", "event_type": "purchase", "amount": 13.0, "ts": "2024-10-01T12:05:00Z"},
        {"id": 3, "user_id": "u1", "event_type": "refund", "amount": -5.0, "ts": "2024-10-01T12:10:00Z"},
        {"id": 4, "user_id": "u3", "event_type": "purchase", "amount": 7.5, "ts": "2024-10-01T12:20:00Z"},
        {"id": 5, "user_id": "u3", "event_type": "purchase", "amount": 7.5, "ts": "2024-10-01T12:20:00Z"},  # duplicate id to exercise dedup
    ]

    schema = T.StructType(
        [
            T.StructField("id", T.IntegerType(), False),
            T.StructField("user_id", T.StringType(), False),
            T.StructField("event_type", T.StringType(), False),
            T.StructField("amount", T.DoubleType(), True),
            T.StructField("ts", T.StringType(), False),
        ]
    )

    bronze_df = spark.createDataFrame(sample_data, schema=schema).withColumn(
        "ingested_at", F.current_timestamp()
    )
    bronze_df = bronze_df.withColumn("run_id", F.lit(actual_run_id))
    bronze_df.write.format("delta").mode("overwrite").save(bronze_path)

    total_rows = bronze_df.count()
    non_null = evaluate_non_null("id", total_rows, 0)
    uniqueness = evaluate_uniqueness("id", total_rows, bronze_df.select("id").distinct().count())

    metrics = [
        build_metric_record(actual_run_id, "bronze", "row_count", "OK", total_rows),
        build_metric_record(
            actual_run_id,
            "bronze",
            non_null["metric_name"],
            non_null["status"],
            non_null["value"],
            non_null["details"],
        ),
        build_metric_record(
            actual_run_id,
            "bronze",
            uniqueness["metric_name"],
            uniqueness["status"],
            uniqueness["value"],
            uniqueness["details"],
        ),
    ]
    _persist_metrics(spark, base_path, "bronze", actual_run_id, metrics)

    return bronze_path


def transform_silver(
    spark: "SparkSession",
    bronze_path: str,
    base_path: str = DEFAULT_BASE_PATH,
    run_id: str | None = None,
) -> str:
    """Cleanse bronze data and write to silver Delta table."""
    from pyspark.sql import functions as F

    actual_run_id = run_id or _dt.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    silver_path = f"{base_path}/silver"

    bronze_df = spark.read.format("delta").load(bronze_path)
    clean_df = (
        bronze_df.dropDuplicates(["id"])
        .filter(F.col("amount").isNotNull())
        .withColumn("event_ts", F.to_timestamp("ts"))
        .withColumn("event_date", F.to_date("ts"))
    )
    clean_df.write.format("delta").mode("overwrite").save(silver_path)

    total_rows = clean_df.count()
    null_amount_rows = clean_df.filter(F.col("amount").isNull()).count()
    non_null = evaluate_non_null("amount", total_rows, null_amount_rows)
    metrics = [
        build_metric_record(actual_run_id, "silver", "row_count", "OK", total_rows),
        build_metric_record(
            actual_run_id,
            "silver",
            non_null["metric_name"],
            non_null["status"],
            non_null["value"],
            non_null["details"],
        ),
    ]
    _persist_metrics(spark, base_path, "silver", actual_run_id, metrics)

    return silver_path


def aggregate_gold(
    spark: "SparkSession",
    silver_path: str,
    base_path: str = DEFAULT_BASE_PATH,
    run_id: str | None = None,
) -> str:
    """Aggregate silver data to gold Delta table."""
    from pyspark.sql import functions as F

    actual_run_id = run_id or _dt.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    gold_path = f"{base_path}/gold"

    silver_df = spark.read.format("delta").load(silver_path)
    gold_df = (
        silver_df.groupBy("event_date", "event_type")
        .agg(
            F.count("*").alias("event_count"),
            F.sum("amount").alias("total_amount"),
            F.countDistinct("user_id").alias("unique_users"),
        )
        .orderBy("event_date", "event_type")
        .withColumn("run_id", F.lit(actual_run_id))
    )

    gold_df.write.format("delta").mode("overwrite").save(gold_path)

    metrics = [
        build_metric_record(actual_run_id, "gold", "row_count", "OK", gold_df.count()),
    ]
    _persist_metrics(spark, base_path, "gold", actual_run_id, metrics)

    return gold_path


def run_pipeline(
    spark: "SparkSession",
    base_path: str = DEFAULT_BASE_PATH,
    run_id: str | None = None,
) -> Dict[str, str]:
    """Execute the full bronze → silver → gold pipeline."""
    actual_run_id = run_id or _dt.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    bronze_path = ingest_bronze(spark, base_path, actual_run_id)
    silver_path = transform_silver(spark, bronze_path, base_path, actual_run_id)
    gold_path = aggregate_gold(spark, silver_path, base_path, actual_run_id)

    return {
        "run_id": actual_run_id,
        "bronze_path": bronze_path,
        "silver_path": silver_path,
        "gold_path": gold_path,
        "metrics_path": f"{base_path}/metrics",
    }
