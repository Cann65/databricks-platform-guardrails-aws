# Databricks Auditor

Python-based compliance auditor for Databricks workspaces with dry-run support.

## Overview

The auditor validates that Databricks workspaces comply with platform guardrails:

- Cluster policies enforce cost controls and tagging
- No all-purpose clusters running (prefer job clusters)
- Secret scopes properly configured
- Workspace settings follow baseline security

## Key Features

### Dry-Run Mode

Run without Databricks credentials using fixture data:

```bash
python -m databricks_auditor.cli audit --out reports --format html,md,json
```

Dry-run mode:
- Uses JSON fixtures in `databricks_auditor/fixtures/`
- Enables CI/CD without credentials
- Returns warnings for checks that need real data

### Real Mode

Run against live Databricks workspace:

```bash
export DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
export DATABRICKS_TOKEN=dapi...
python -m databricks_auditor.cli audit --out reports --format html,md,json
```

Real mode:
- Calls Databricks REST APIs
- Validates actual workspace configuration
- Returns definitive PASS/FAIL results

## Development

### Setup

```bash
cd auditor
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Lint

```bash
ruff check .
```

### Project Structure

```
databricks_auditor/
├── __init__.py
├── cli.py              # CLI entry point
├── client.py           # Databricks API client
├── config.py           # Configuration management
├── report.py           # Report generation (JSON/MD/HTML)
├── checks/
│   ├── __init__.py
│   ├── cluster_policies.py     # Policy compliance
│   ├── tags_cost_controls.py   # Tag/cost checks
│   ├── clusters.py             # Active cluster checks
│   ├── secrets.py              # Secret scope checks
│   └── workspace_settings.py   # Workspace config checks
└── fixtures/
    ├── sample_policies.json
    ├── sample_clusters.json
    ├── sample_secrets.json
    └── sample_workspace_conf.json
```

## How Fixtures Work

Fixtures simulate Databricks API responses for dry-run mode:

1. **sample_policies.json**: Contains `guardrails-default` cluster policy with all required controls
2. **sample_clusters.json**: Sample running cluster (job cluster, not all-purpose)
3. **sample_secrets.json**: Platform secret scope
4. **sample_workspace_conf.json**: Basic workspace configuration settings

When `DATABRICKS_HOST` and `DATABRICKS_TOKEN` are not set, the client automatically uses fixtures instead of making API calls.

### Updating Fixtures

To update fixtures with real data:

```bash
# Export real data from Databricks
export DATABRICKS_HOST=...
export DATABRICKS_TOKEN=...

# Get cluster policies
curl -H "Authorization: Bearer $DATABRICKS_TOKEN" \
  $DATABRICKS_HOST/api/2.0/policies/clusters/list \
  > databricks_auditor/fixtures/sample_policies.json

# Get clusters
curl -H "Authorization: Bearer $DATABRICKS_TOKEN" \
  $DATABRICKS_HOST/api/2.0/clusters/list \
  > databricks_auditor/fixtures/sample_clusters.json

# Get secret scopes
curl -H "Authorization: Bearer $DATABRICKS_TOKEN" \
  $DATABRICKS_HOST/api/2.0/secrets/scopes/list \
  > databricks_auditor/fixtures/sample_secrets.json
```

## How to Run in Real Mode

### Prerequisites

1. Databricks workspace (AWS, Azure, or GCP)
2. Personal access token with workspace admin permissions

### Steps

1. **Create token**:
   - In Databricks workspace: Settings → User Settings → Access Tokens
   - Generate new token, copy value

2. **Set environment variables**:
   ```bash
   export DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
   export DATABRICKS_TOKEN=dapi123456789...
   ```

3. **Run audit**:
   ```bash
   python -m databricks_auditor.cli audit --out reports --format html,md,json
   ```

4. **Review reports**:
   - `reports/audit_report.json` - Machine-readable
   - `reports/audit_report.md` - Human-readable summary
   - `reports/audit_report.html` - Visual dashboard

## Compliance Checks

| Check Name                        | Severity | Description                                      |
|-----------------------------------|----------|--------------------------------------------------|
| cluster_policy_exists             | FAIL     | Guardrails policy must exist                     |
| auto_termination_enforced         | FAIL     | Auto-termination must be ≤15 minutes             |
| max_workers_enforced              | FAIL     | Max workers must be ≤8                           |
| required_tags_enforced            | FAIL     | Tags (owner, cost_center, env) must be enforced  |
| no_all_purpose_clusters           | FAIL/WARN| No all-purpose clusters should be running        |
| platform_secret_scope_exists      | FAIL     | Platform secret scope must exist                 |
| workspace_configuration_baseline  | WARN     | Workspace config should follow baseline          |

## Exit Codes

- **0**: All checks passed (OK)
- **2**: At least one WARNING
- **3**: At least one FAILURE

Use in CI/CD:

```bash
python -m databricks_auditor.cli audit || exit $?
```

## Security Notes

- **Never log tokens**: Client redacts tokens in logs
- **Never commit credentials**: Use environment variables only
- **Use short-lived tokens**: Rotate tokens regularly
- **Least privilege**: Token only needs read permissions for audit

## Extending the Auditor

To add a new check:

1. Create new file in `databricks_auditor/checks/`
2. Implement check function returning `List[Finding]`
3. Add to `checks/__init__.py`
4. Add to `cli.py` check function list
5. Add fixture data if needed
6. Write tests in `tests/test_checks.py`

Example:

```python
# databricks_auditor/checks/my_check.py

from databricks_auditor.client import DatabricksClient
from databricks_auditor.report import Finding, Severity

def check_my_feature(client: DatabricksClient) -> List[Finding]:
    findings = []

    # Get data
    data = client.get_some_data()

    # Validate
    if data.meets_requirement():
        findings.append(Finding(
            check_name="my_feature_check",
            severity=Severity.OK,
            message="Feature configured correctly"
        ))
    else:
        findings.append(Finding(
            check_name="my_feature_check",
            severity=Severity.FAIL,
            message="Feature not configured"
        ))

    return findings
```

## Troubleshooting

### Error: "Failed to fetch workspace config"

**Cause**: Workspace config endpoint requires admin permissions

**Solution**: This check returns WARN instead of FAIL. Run with admin token for full validation.

### Error: "API request failed"

**Cause**: Token expired or invalid

**Solution**: Generate new token and update `DATABRICKS_TOKEN`

### Reports not generated

**Cause**: Output directory doesn't exist or no write permissions

**Solution**: Ensure output directory exists and is writable

## Performance

- Dry-run: <1 second (no API calls)
- Real mode: 2-5 seconds (depends on workspace size)
- Timeout: 30 seconds per API call (configurable)

## Dependencies

- `requests`: HTTP client for Databricks API
- `pydantic`: Data validation and serialization
- `pytest`: Testing framework
- `ruff`: Linting and formatting

All dependencies pinned in `pyproject.toml`.

## License

MIT License - see LICENSE file in repository root.
