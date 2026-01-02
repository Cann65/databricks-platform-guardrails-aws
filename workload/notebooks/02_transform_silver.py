# Databricks notebook source

# COMMAND ----------
# Parameters
import datetime as dt

try:
    dbutils.widgets.text("output_base_path", "dbfs:/tmp/guardrails_demo", "Output base path")
    dbutils.widgets.text("bronze_path", "", "Bronze path (optional)")
    dbutils.widgets.text("run_id", "", "Run ID (optional)")
except NameError:
    pass

base_path = "dbfs:/tmp/guardrails_demo"
bronze_path = ""
run_id = ""

try:
    base_path = dbutils.widgets.get("output_base_path")  # type: ignore[name-defined]
    bronze_path = dbutils.widgets.get("bronze_path")  # type: ignore[name-defined]
    run_id = dbutils.widgets.get("run_id")  # type: ignore[name-defined]
except Exception:
    pass

if not bronze_path:
    try:
        bronze_path = dbutils.jobs.taskValues.get("01_ingest_bronze", "bronze_path", default="")  # type: ignore[name-defined]
    except Exception:
        bronze_path = ""

if not base_path:
    base_path = "dbfs:/tmp/guardrails_demo"

if not run_id:
    try:
        run_id = dbutils.jobs.taskValues.get("01_ingest_bronze", "run_id", default="")  # type: ignore[name-defined]
    except Exception:
        run_id = ""

if not run_id:
    run_id = dt.datetime.utcnow().strftime("%Y%m%d%H%M%S")

if not bronze_path:
    bronze_path = f"{base_path}/bronze"

# COMMAND ----------
# Transform bronze -> silver
from workload.pipeline import transform_silver

silver_path = transform_silver(
    spark,
    bronze_path=bronze_path,
    base_path=base_path,
    run_id=run_id,
)

try:
    dbutils.jobs.taskValues.set(key="silver_path", value=silver_path)  # type: ignore[name-defined]
    dbutils.jobs.taskValues.set(key="run_id", value=run_id)  # type: ignore[name-defined]
except Exception:
    pass

# COMMAND ----------
# Finish
dbutils.notebook.exit(silver_path)

