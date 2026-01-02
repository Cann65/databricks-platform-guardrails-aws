# Databricks Compliance Audit Report

**Timestamp:** 2026-01-01T23:53:49.510562Z
**Environment:** DRY-RUN
**Mode:** DRY-RUN (using fixtures)

## Summary

- Total Checks: 7
- ✅ OK: 6
- ⚠️  WARN: 1
- ❌ FAIL: 0

## Findings

### ⚠️ WARN

**no_all_purpose_clusters**
- DRY-RUN: Cannot validate cluster types from fixture data
- Details: {
  "cluster_count": 1
}

### ✅ OK

**cluster_policy_exists**
- Guardrails cluster policy 'guardrails-default' exists
- Details: {
  "policy_id": "mock-policy-001"
}

**auto_termination_enforced**
- Auto-termination enforced at 15 minutes (≤15)
- Details: {
  "max_value": 15
}

**max_workers_enforced**
- Max workers enforced at 8 (≤8)
- Details: {
  "max_values": [
    8,
    8
  ]
}

**required_tags_enforced**
- All required tags enforced: owner, cost_center, env
- Details: {
  "tags": {
    "owner": {
      "type": "fixed",
      "value": "platform-team"
    },
    "cost_center": {
      "type": "unlimited",
      "defaultValue": "data-platform"
    },
    "env": {
      "type": "fixed",
      "value": "dev"
    }
  }
}

**platform_secret_scope_exists**
- Platform secret scope 'platform' exists
- Details: {
  "scope_name": "platform",
  "backend_type": "DATABRICKS"
}

**workspace_configuration_baseline**
- Workspace configuration retrieved successfully
- Details: {
  "config_count": 3,
  "mode": "DRY-RUN"
}
