# Databricks Platform Guardrails for AWS

**Enterprise-grade governance, cost controls, and compliance automation for Databricks on AWS.**

> **Portfolio Note**: This is a demonstration repository showcasing production-grade platform engineering. See [examples/](examples/) for sample audit reports and terraform outputs.

## Elevator Pitch

This repository provides production-ready infrastructure-as-code and compliance tooling to operate Databricks on AWS with secure-by-default settings, automated cost controls, and continuous compliance validation. Focus on data engineering, not runaway cloud bills.

## Why

**Real Industry Problem:** Databricks workspaces without guardrails lead to:

- **Cost overruns**: All-purpose clusters left running indefinitely, oversized clusters, no auto-termination
- **Security gaps**: Unencrypted data, missing IAM boundaries, secrets in plain text
- **Compliance failures**: Missing audit trails, no tag enforcement, uncontrolled resource sprawl
- **Operational chaos**: No standardization, manual compliance checks, lack of reproducibility

This project solves these problems with:

1. Terraform modules for baseline AWS infrastructure and Databricks policies
2. Python auditor CLI with dry-run support and CI-friendly exit codes
3. SQL templates for cost allocation and usage analysis
4. GitHub Actions CI for continuous compliance validation

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Actions CI                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Terraform    │  │ Python       │  │ Audit        │      │
│  │ fmt/validate │  │ lint/test    │  │ (dry-run)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Terraform Deployment                       │
│                                                             │
│  ┌──────────────────────┐      ┌──────────────────────┐    │
│  │  AWS Baseline        │      │ Databricks Guardrails│    │
│  │  - S3 bucket         │──────│ - Cluster policy     │    │
│  │  - IAM role/profile  │      │ - Secret scope       │    │
│  │  - Encryption        │      │ - Tag enforcement    │    │
│  └──────────────────────┘      └──────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Python Auditor (Real/Dry-run)                  │
│                                                             │
│  Checks:                        Reports:                    │
│  ✓ Policy exists                - JSON (CI integration)    │
│  ✓ Auto-terminate ≤15min        - Markdown (readable)      │
│  ✓ Max workers ≤8               - HTML (dashboard)         │
│  ✓ Required tags enforced       Exit: 0=OK, 2=WARN, 3=FAIL │
│  ✓ No all-purpose clusters                                 │
│  ✓ Secret scope exists                                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  SQL Analytics (Unity)                      │
│  - Top users by DBU consumption                            │
│  - Job failure analysis                                    │
│  - Cost allocation by tag (cost_center, env)              │
└─────────────────────────────────────────────────────────────┘
```

## Guardrails

### Cluster Policy: `guardrails-default`

| Control                  | Setting              | Rationale                              |
|--------------------------|----------------------|----------------------------------------|
| Auto-termination         | ≤ 15 minutes         | Prevent idle clusters from running    |
| Max workers              | ≤ 8 workers          | Cap cluster size for cost control     |
| Node types               | Allowlist (i3/m5d)   | Restrict to cost-effective instances  |
| Required tags            | owner, cost_center, env | Enable cost allocation and tracking |
| Cluster type preference  | Job clusters         | Discourage all-purpose clusters       |

### AWS Security Baseline

- **S3 bucket**: Server-side encryption (AES256), public access blocked, TLS-only policy
- **IAM role**: Least-privilege access to S3, EC2 assume role only
- **Secret scope**: Managed secrets in Databricks (not plain text)

### Tag Enforcement Strategy

**Important**: Tag enforcement relies on both policy configuration AND auditor validation:

- **Policy layer**: Tags are defined in cluster policy with varying enforcement levels:
  - `owner`: Fixed value (enforced by policy)
  - `env`: Fixed value (enforced by policy)
  - `cost_center`: Unlimited type with default value (user can override)

- **Auditor layer**: Validates that all required tags are present in policy definition
- **Source of truth**: The auditor check is the definitive compliance validation

This dual-layer approach ensures:
1. Policy guides users toward compliant configurations
2. Auditor catches policy drift or misconfigurations
3. CI/CD blocks deployments with missing tag enforcement

## Auditor Usage

### Installation

```bash
make install  # Install Python dependencies
```

### Run Audit

```bash
# Dry-run mode (no credentials needed, uses fixtures)
make audit

# Real mode (requires DATABRICKS_HOST and DATABRICKS_TOKEN)
export DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
export DATABRICKS_TOKEN=dapi...
make audit
```

### Exit Codes

| Code | Meaning                          | CI Behavior    |
|------|----------------------------------|----------------|
| 0    | All checks passed (OK)           | ✅ Pass        |
| 2    | At least one WARNING             | ⚠️ Pass        |
| 3    | At least one FAILURE             | ❌ Fail        |

### Report Formats

```bash
python -m databricks_auditor.cli audit --out reports --format html,md,json
```

- **JSON**: Machine-readable, CI integration
- **Markdown**: Readable summary for pull requests
- **HTML**: Standalone dashboard (open in browser)

## Proof Steps (Evidence)

### 1. Terraform Plan (Infrastructure)

```bash
make init
make plan
```

Expected output:
```
Terraform will perform the following actions:

  # module.aws_baseline.aws_s3_bucket.databricks_root_storage will be created
  # module.databricks_guardrails.databricks_cluster_policy.guardrails_default will be created
  # module.databricks_guardrails.databricks_secret_scope.platform will be created

Plan: 3 to add, 0 to change, 0 to destroy.
```

### 2. Audit Report Generation (Dry-run)

```bash
make audit
```

Expected output:
```
Report saved: reports/audit_report.json
Report saved: reports/audit_report.md
Report saved: reports/audit_report.html

============================================================
AUDIT SUMMARY
============================================================
Total checks: 7
✅ OK:   5
⚠️  WARN: 2
❌ FAIL: 0
============================================================
⚠️  Some checks returned warnings
```

Open `reports/audit_report.html` in a browser to see visual report.

### 3. Fail → Fix → Pass Narrative (Simulated)

**Scenario**: Policy missing required tags

1. **FAIL state**: Run audit, get exit code 3
   ```
   ❌ FAIL: Missing required tags in policy: cost_center
   ```

2. **Fix**: Update `terraform/modules/databricks_guardrails/policy.json.tpl`
   ```json
   "custom_tags.cost_center": {
     "type": "unlimited",
     "defaultValue": "data-platform"
   }
   ```

3. **Apply fix**: `make apply`

4. **PASS state**: Run audit again
   ```
   ✅ OK: All required tags enforced: owner, cost_center, env
   Exit code: 0
   ```

### 4. CI Pipeline

```bash
make ci
```

Runs:
- `ruff check` (Python linting)
- `pytest` (unit tests)
- `terraform fmt -check` (formatting)
- `terraform validate` (validation)

All checks pass without Databricks credentials (dry-run mode).

## Cost Strategy

### Design for Low Cost

1. **Job clusters over all-purpose**: Enforce via policy + auditor check
2. **Auto-termination ≤15 min**: Clusters shut down quickly when idle
3. **Worker limits**: Max 8 workers prevents runaway scaling
4. **Node type allowlist**: Restricts to cost-effective instance types
5. **Destroy when not needed**: `make destroy` tears down all resources

### Cost Allocation

SQL templates (`sql/cost_allocation.sql`) enable chargeback by:
- Cost center
- Environment (dev/prod)
- Owner

Requires Unity Catalog enabled (see Limitations).

### Estimated Monthly Costs

**Infrastructure only** (no active workloads):
- S3 bucket: ~$1-5/month (storage + requests)
- IAM resources: $0 (no charge)
- **Total**: <$10/month

**With workloads** (example):
- 1 job cluster, 4 workers, i3.xlarge, 2 hours/day
- AWS EC2: ~$50-100/month
- Databricks DBUs: ~$100-200/month
- **Total**: ~$150-300/month

Actual costs vary by usage. **Always** run `terraform plan` and review before apply.

## Trade-offs & Limitations

### What This Project Does NOT Include

1. **Databricks workspace creation**: Assumes workspace already exists (managed separately, often via Databricks account console or separate Terraform). You must provide `DATABRICKS_HOST` and `DATABRICKS_TOKEN`.

2. **Unity Catalog setup**: SQL queries assume Unity Catalog enabled. If not available, queries will fail. Workaround: Adapt queries to legacy `audit_logs` or custom tables.

3. **Network/VPC configuration**: No VPC peering, private subnets, or PrivateLink. Add in production.

4. **Budget alerts**: No AWS Budgets or CloudWatch alarms. Recommended to add.

5. **Advanced RBAC**: Basic tagging only. For fine-grained access control, add Unity Catalog grants.

### Design Choices

| Choice                     | Why                                    | Trade-off                                |
|----------------------------|----------------------------------------|------------------------------------------|
| Dry-run mode              | CI passes without credentials          | Fixture data may drift from reality      |
| Cluster policy only       | Simplest enforcement mechanism         | Doesn't prevent manual non-compliant clusters |
| No workspace creation     | Complex, multi-account setup           | Requires manual workspace provisioning   |
| Fixed node types          | Cost control                          | May not fit all workloads                |
| Max 8 workers             | Prevents runaway costs                 | May be too small for large jobs          |

## Roadmap

Future enhancements:

- [ ] Unity Catalog table/schema policies
- [ ] VPC/PrivateLink setup for production
- [ ] AWS Budgets + SNS alerts
- [ ] Multi-environment promotion (dev → staging → prod)
- [ ] Advanced RBAC with groups and service principals
- [ ] Job orchestration examples (Airflow/Dagster)
- [ ] Databricks Asset Bundles (DABs) integration

## Quick Start

### Prerequisites

- Terraform >= 1.5.0
- Python >= 3.9
- AWS credentials configured (`~/.aws/credentials` or env vars)
- **Optional**: Databricks workspace + token (for real mode)

### Setup

1. **Clone repository**
   ```bash
   git clone https://github.com/yourorg/databricks-platform-guardrails-aws.git
   cd databricks-platform-guardrails-aws
   ```

2. **Configure Terraform**
   ```bash
   cd terraform/envs/dev
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars: set unique S3 bucket name
   ```

3. **Install auditor**
   ```bash
   make install
   ```

4. **Run CI checks (dry-run, no credentials needed)**
   ```bash
   make ci
   ```

5. **Run audit (dry-run)**
   ```bash
   make audit
   ```

6. **Deploy infrastructure (requires AWS + Databricks credentials)**
   ```bash
   export DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
   export DATABRICKS_TOKEN=dapi...
   make plan
   make apply
   ```

7. **Run audit in real mode**
   ```bash
   make audit
   ```

8. **View HTML report**
   ```bash
   open reports/audit_report.html
   ```

## Repository Structure

```
databricks-platform-guardrails-aws/
├── terraform/
│   ├── modules/
│   │   ├── aws_baseline/          # S3 bucket, IAM role
│   │   └── databricks_guardrails/ # Cluster policy, secret scope
│   └── envs/
│       └── dev/                   # Dev environment config
├── auditor/
│   ├── databricks_auditor/
│   │   ├── cli.py                 # CLI entry point
│   │   ├── client.py              # Databricks API client
│   │   ├── config.py              # Configuration
│   │   ├── report.py              # Report generation
│   │   ├── checks/                # Compliance check modules
│   │   └── fixtures/              # Dry-run test data
│   └── tests/                     # Unit tests
├── sql/                           # Usage/cost analysis queries
├── .github/workflows/ci.yml       # GitHub Actions CI
├── Makefile                       # One-command workflows
└── README.md                      # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Run `make ci` to verify
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file.

## Support

For issues or questions:
- Open an issue on GitHub
- Contact: platform-team@example.com

---

**Built with ❤️ by the Platform Team**
