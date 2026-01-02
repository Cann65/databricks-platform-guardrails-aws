# Databricks Delta Pipeline with Guardrails (AWS)

Primary goal: a real Databricks workload (bronze → silver → gold Delta pipeline) that you can run as notebooks or as a Databricks Job. Guardrails and the auditor stay as supporting safety nets.

## What this builds
- **Workload:** PySpark pipeline with synthetic data, Delta outputs in `dbfs:/tmp/guardrails_demo/{bronze,silver,gold}`, metrics in `dbfs:/tmp/guardrails_demo/metrics`, SQL analytics queries.
- **Jobs:** Optional Databricks Job (Terraform) chaining the three notebooks; optional Python job runner to execute the pipeline in one task.
- **Guardrails:** Cluster policy, tagging, secret scope (Terraform modules). Reused by the job cluster when enabled.
- **Compliance check:** Python auditor (dry-run by default) that reports WARN/FAIL/OK and exports HTML/MD/JSON.
- **CI/CD:** GitHub Actions runs lint + tests + Terraform fmt/validate + dry-run audit artifact.

## Run the workload in Databricks
1) **Import repo into Databricks Repos** (or upload notebooks to `/Shared/guardrails_demo`).  
2) **Run notebooks manually** (widgets default to `dbfs:/tmp/guardrails_demo`):  
   - `workload/notebooks/01_ingest_bronze.py`  
   - `workload/notebooks/02_transform_silver.py` (depends on 01)  
   - `workload/notebooks/03_aggregate_gold.py` (depends on 02)  
   Each step writes Delta + appends metrics.
3) **Or run as a Databricks Job** (UI or Terraform module `databricks_jobs`): tasks 1→2→3 with `output_base_path=dbfs:/tmp/guardrails_demo`. Task dependencies are already encoded.
4) **Single-task option:** set a Python task to `workload/job_runner.py`; parameters via widgets/env (`RUN_ID`, `OUTPUT_BASE_PATH`).  
5) **Query results:** run `workload/sql/analytics_queries.sql` in Databricks SQL to create/read the gold table and refund ratios.

## Terraform (optional)
- `modules/aws_baseline`: S3 (encrypted, TLS-only) + IAM role/profile.  
- `modules/databricks_guardrails`: Cluster policy (auto-termination ≤15m, max workers ≤8, required tags, node allowlist) + secret scope.  
- `modules/databricks_jobs`: Optional job chaining the three notebooks; reuses the guardrails policy if present.  
- `envs/dev`: Wires modules; toggle job creation with `enable_workload_job`.

## Auditor (supporting role)
- Lives in `auditor/`; still dry-run capable with fixtures.  
- Exit codes: `0` OK, `2` WARN (CI still green), `3` FAIL (CI red).  
- Reports saved as HTML/MD/JSON; CI uploads them as artifacts.  
- Run locally:  
  ```bash
  cd auditor
  pip install -e ".[dev]"
  python -m databricks_auditor.cli audit --out ../reports --format html,md,json
  ```

## Evidence (what to show)
- **CI run proof:** add your CI screenshot to `examples/pipeline_run_screenshot.png` (placeholder file is present). This shows the pipeline + checks ran in GitHub Actions.  
- **HTML report proof:** `examples/audit_report.html` (pre-generated from dry-run) demonstrates the compliance report artifact. Explain that WARNs clear once pointed at a real workspace.

## Trade-offs
- Synthetic data only; plug in a real source by replacing `workload/pipeline.py` ingest logic.  
- Job paths assume you imported the repo to Repos or `/Shared`; update `notebook_base_path` accordingly.  
- Guardrails are minimal (policy + tags + secret scope); networking, workspace creation, and budgets are out-of-scope but easy to add.  
- PySpark is required inside Databricks; local unit tests target pure-Python helpers to avoid heavy deps.

## Repo layout
```
workload/            # Databricks pipeline + notebooks + SQL + job runner
terraform/           # AWS baseline, guardrails, optional job wiring
auditor/             # Compliance checker (secondary, CI safety net)
sql/                 # Legacy cost/usage SQL templates (still available)
.github/workflows/   # CI: lint, tests, terraform validate, audit artifact
examples/            # Evidence (audit reports + pipeline screenshot placeholder)
```

## Quick commands (local)
- Python lint/tests (includes workload helper tests):  
  `cd auditor && PYTHONPATH=.. ruff check . && PYTHONPATH=.. pytest`
- Terraform validate (no creds needed):  
  `cd terraform/envs/dev && terraform init -backend=false && terraform validate`

