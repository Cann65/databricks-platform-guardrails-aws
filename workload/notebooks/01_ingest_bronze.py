# Databricks notebook source

# COMMAND ----------
# Parameters
import datetime as dt

try:
    dbutils.widgets.text("output_base_path", "dbfs:/tmp/guardrails_demo", "Output base path")
    dbutils.widgets.text("run_id", "", "Run ID (optional)")
except NameError:
    pass

base_path = "dbfs:/tmp/guardrails_demo"
run_id = ""

try:
    base_path = dbutils.widgets.get("output_base_path")  # type: ignore[name-defined]
    run_id = dbutils.widgets.get("run_id")  # type: ignore[name-defined]
except Exception:
    pass

if not base_path:
    base_path = "dbfs:/tmp/guardrails_demo"

if not run_id:
    run_id = dt.datetime.utcnow().strftime("%Y%m%d%H%M%S")

# COMMAND ----------
# Ingest synthetic data to bronze
from workload.pipeline import ingest_bronze

bronze_path = ingest_bronze(spark, base_path=base_path, run_id=run_id)

try:
    dbutils.jobs.taskValues.set(key="bronze_path", value=bronze_path)  # type: ignore[name-defined]
    dbutils.jobs.taskValues.set(key="run_id", value=run_id)  # type: ignore[name-defined]
except Exception:
    pass

# COMMAND ----------
# Finish
dbutils.notebook.exit(bronze_path)

