# Databricks Guardrails Module
# Enforces security, cost, and governance policies

terraform {
  required_providers {
    databricks = {
      source = "databricks/databricks"
    }
  }
}

# Cluster policy enforcing guardrails
resource "databricks_cluster_policy" "guardrails_default" {
  name = var.policy_name

  definition = templatefile("${path.module}/policy.json.tpl", {
    max_workers                 = var.max_workers
    max_autotermination_minutes = var.max_autotermination_minutes
    allowed_node_types          = var.allowed_node_types
    default_node_type           = var.default_node_type
    default_owner_tag           = var.default_owner_tag
    default_cost_center_tag     = var.default_cost_center_tag
    environment                 = var.environment
  })

  description = "Platform guardrails policy: enforces cost controls, auto-termination, and required tagging"
}

# Managed secret scope for platform secrets
resource "databricks_secret_scope" "platform" {
  name = var.secret_scope_name
}

# Optional: Demo job (disabled by default)
resource "databricks_job" "demo_compliance_check" {
  count = var.enable_demo_job ? 1 : 0

  name = "demo-compliance-check"

  task {
    task_key = "compliance_check"

    new_cluster {
      num_workers   = 1
      spark_version = var.spark_version
      node_type_id  = var.default_node_type
      policy_id     = databricks_cluster_policy.guardrails_default.id


      custom_tags = {
        owner       = var.default_owner_tag
        cost_center = var.default_cost_center_tag
        env         = var.environment
      }
    }

    notebook_task {
      notebook_path = var.demo_notebook_path
    }
  }

  timeout_seconds = 3600

  tags = {
    environment = var.environment
    managed_by  = "terraform"
  }
}
