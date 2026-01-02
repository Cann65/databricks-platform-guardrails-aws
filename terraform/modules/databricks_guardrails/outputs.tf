output "cluster_policy_id" {
  description = "ID of the guardrails cluster policy"
  value       = databricks_cluster_policy.guardrails_default.id
}

output "cluster_policy_name" {
  description = "Name of the guardrails cluster policy"
  value       = databricks_cluster_policy.guardrails_default.name
}

output "secret_scope_name" {
  description = "Name of the platform secret scope"
  value       = databricks_secret_scope.platform.name
}

output "demo_job_id" {
  description = "ID of the demo job (if enabled)"
  value       = var.enable_demo_job ? databricks_job.demo_compliance_check[0].id : null
}
