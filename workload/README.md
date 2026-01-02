# Databricks Workload (Bronze → Silver → Gold)

Primary deliverable for this repo: a small, runnable Databricks data pipeline with Delta Lake, data quality metrics, and job wiring.

## What it does
- Generates synthetic transactions → writes **bronze** Delta table at `dbfs:/tmp/guardrails_demo/bronze`
- Cleans/deduplicates → writes **silver** Delta table at `dbfs:/tmp/guardrails_demo/silver`
- Aggregates → writes **gold** Delta table at `dbfs:/tmp/guardrails_demo/gold`
- Captures lightweight metrics (row counts, non-null, uniqueness) in `dbfs:/tmp/guardrails_demo/metrics`
- Provides simple SQL analytics in `workload/sql/analytics_queries.sql`

## Artifacts
- `notebooks/01_ingest_bronze.py` – create synthetic data, enforce uniqueness
- `notebooks/02_transform_silver.py` – cleanse/dedupe, add dates
- `notebooks/03_aggregate_gold.py` – aggregate to gold
- `job_runner.py` – sequential runner for Databricks job task (Python task)
- `pipeline.py` – reusable PySpark functions for the steps
- `quality.py` – pure-Python metric helpers (unit tested)
- `sql/analytics_queries.sql` – sample queries on the gold table

## How to run in Databricks
1. **Import repo into Repos** (recommended) or upload notebooks into `/Shared/guardrails_demo`.
2. Open each notebook and click “Run All” (widgets default to `dbfs:/tmp/guardrails_demo`).
3. Or create a Databricks Job:
   - Task 1: Notebook `notebooks/01_ingest_bronze.py`
   - Task 2: Notebook `notebooks/02_transform_silver.py` (depends on Task 1)
   - Task 3: Notebook `notebooks/03_aggregate_gold.py` (depends on Task 2)
   - Base parameters: `output_base_path=dbfs:/tmp/guardrails_demo`
4. For a single-task pipeline, set task type to **Python** and point to `workload/job_runner.py`; optional params via widgets/env (`run_id`, `OUTPUT_BASE_PATH`).

## Data quality
- Non-null check on `id` (bronze) and `amount` (silver)
- Uniqueness check on `id` (bronze)
- Metrics written to Delta for observability (`metrics` path)

## SQL analytics
Run `workload/sql/analytics_queries.sql` in Databricks SQL to create a table on top of the gold Delta output and explore aggregates/refund ratios.

