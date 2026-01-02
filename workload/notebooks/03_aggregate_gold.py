# Databricks notebook source

# COMMAND ----------
# Parameters
import datetime as dt

try:
    dbutils.widgets.text("output_base_path", "dbfs:/tmp/guardrails_demo", "Output base path")
    dbutils.widgets.text("silver_path", "", "Silver path (optional)")
    dbutils.widgets.text("run_id", "", "Run ID (optional)")
except NameError:
    pass

base_path = "dbfs:/tmp/guardrails_demo"
silver_path = ""
run_id = ""

try:
    base_path = dbutils.widgets.get("output_base_path")  # type: ignore[name-defined]
    silver_path = dbutils.widgets.get("silver_path")  # type: ignore[name-defined]
    run_id = dbutils.widgets.get("run_id")  # type: ignore[name-defined]
except Exception:
    pass

if not silver_path:
    try:
        silver_path = dbutils.jobs.taskValues.get("02_transform_silver", "silver_path", default="")  # type: ignore[name-defined]
    except Exception:
        silver_path = ""

if not base_path:
    base_path = "dbfs:/tmp/guardrails_demo"

if not run_id:
    try:
        run_id = dbutils.jobs.taskValues.get("01_ingest_bronze", "run_id", default="")  # type: ignore[name-defined]
    except Exception:
        run_id = ""

if not run_id:
    run_id = dt.datetime.utcnow().strftime("%Y%m%d%H%M%S")

if not silver_path:
    silver_path = f"{base_path}/silver"

# COMMAND ----------
# Aggregate silver -> gold
from workload.pipeline import aggregate_gold

gold_path = aggregate_gold(
    spark,
    silver_path=silver_path,
    base_path=base_path,
    run_id=run_id,
)

try:
    dbutils.jobs.taskValues.set(key="gold_path", value=gold_path)  # type: ignore[name-defined]
    dbutils.jobs.taskValues.set(key="run_id", value=run_id)  # type: ignore[name-defined]
except Exception:
    pass

# COMMAND ----------
# Finish
dbutils.notebook.exit(gold_path)

