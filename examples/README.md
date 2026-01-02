# Example Outputs / Evidence

Portfolio-friendly artifacts that prove the project runs without requiring your credentials.

## Files

- **pipeline_run_screenshot.png** – Placeholder for your Databricks job/notebook run screenshot (drop in your own). Use it to show the bronze→silver→gold job succeeded.
- **audit_report.html / .md / .json** – Pre-generated compliance report (dry-run). Shows what the auditor uploads as a CI artifact.
- **terraform_plan_snippet.txt** – Excerpt from `terraform plan` (what infra would be created).

## How to regenerate

```bash
# Audit reports (dry-run mode, no credentials needed)
cd auditor
python -m databricks_auditor.cli audit --out ../examples --format html,md,json

# Terraform plan (requires AWS creds; optional)
cd terraform/envs/dev
terraform init -backend=false
terraform plan > ../../../examples/terraform_plan_full.txt
```

## View the reports

```bash
# HTML
start examples/audit_report.html   # Windows
open examples/audit_report.html    # macOS
xdg-open examples/audit_report.html # Linux

# Markdown
cat examples/audit_report.md

# JSON
cat examples/audit_report.json | jq .
```

## Reading the audit report
- **OK**: guardrails policy, auto-termination ≤15m, max workers ≤8, required tags, secret scope, workspace config fetched.  
- **WARN**: all-purpose cluster check is a WARN in dry-run (fixtures cannot prove real cluster types).  
- **FAIL**: none in the included example; will surface if your workspace violates a rule.

## Using the screenshot placeholder
- Replace `pipeline_run_screenshot.png` with your screenshot of a successful Databricks job or notebook run (showing the three tasks).  
- Reference it in interviews as “CI run proof” alongside the HTML report.
