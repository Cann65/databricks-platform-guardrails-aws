# Example Outputs

**Portfolio Evidence: Pre-generated reports showing how compliance checks work**

This directory contains sample outputs demonstrating the repository's functionality:

- ✅ **Generated in DRY-RUN mode** - No credentials required
- ✅ **No live infrastructure needed** - Uses fixture data
- ✅ **Safe to share** - No secrets, tokens, or sensitive data
- ✅ **Shows real output** - Exactly what the auditor produces

Perfect for portfolio reviews without setting up Databricks or AWS.

## Files

### audit_report.md
Markdown format audit report showing compliance check results in dry-run mode. Readable summary format suitable for pull requests or documentation.

**Key highlights:**
- 7 compliance checks executed
- 6 checks passed (OK)
- 1 warning (cannot validate cluster types in dry-run)
- 0 failures

### audit_report.json
Machine-readable JSON format of the same audit report. Suitable for CI/CD integration and programmatic processing.

### audit_report.html
Standalone HTML report with visual dashboard. Open in a browser to see styled results with color-coded findings.

### terraform_plan_snippet.txt
Excerpt from `terraform plan` output showing what infrastructure would be created:
- AWS S3 bucket with encryption and TLS-only policy
- IAM role and instance profile for Databricks clusters
- Databricks cluster policy enforcing guardrails
- Databricks secret scope

## How These Were Generated

```bash
# Audit reports (dry-run mode, no credentials needed)
cd auditor
python -m databricks_auditor.cli audit --out ../examples --format html,md,json

# Terraform plan (requires AWS credentials, not included in examples)
cd terraform/envs/dev
terraform init
terraform plan > ../../../examples/terraform_plan_full.txt
```

## Viewing the Reports

### Markdown Report
```bash
cat examples/audit_report.md
```

### HTML Report
```bash
# Windows
start examples/audit_report.html

# Mac
open examples/audit_report.html

# Linux
xdg-open examples/audit_report.html
```

### JSON Report
```bash
cat examples/audit_report.json | jq .
```

## Portfolio Evidence

These examples demonstrate:

1. **Working software**: All checks execute without errors
2. **CI/CD ready**: Exit codes and JSON output enable automation
3. **Production patterns**: Proper error handling, logging, and reporting
4. **Documentation**: Clear, actionable findings with details
5. **Dry-run capability**: Can validate without live infrastructure

## Understanding the Findings

### Green (OK) Checks
- ✅ **cluster_policy_exists**: Guardrails policy found
- ✅ **auto_termination_enforced**: Max 15 minutes (cost control)
- ✅ **max_workers_enforced**: Max 8 workers (cost control)
- ✅ **required_tags_enforced**: owner, cost_center, env tags present
- ✅ **platform_secret_scope_exists**: Secret scope configured
- ✅ **workspace_configuration_baseline**: Config retrieved

### Yellow (WARN) Checks
- ⚠️ **no_all_purpose_clusters**: Cannot validate from fixture data (expected in dry-run)

### Red (FAIL) Checks
- None in this example (demonstrates compliant configuration)

## Next Steps

To run these checks against a real Databricks workspace:

```bash
export DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
export DATABRICKS_TOKEN=dapi...
cd auditor
python -m databricks_auditor.cli audit --out ../reports --format html,md,json
```

The warning will become either OK or FAIL based on actual cluster data.
