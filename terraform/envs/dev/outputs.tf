output "s3_bucket_name" {
  description = "Name of the Databricks root storage bucket"
  value       = module.aws_baseline.s3_bucket_name
}

output "instance_profile_arn" {
  description = "ARN of the Databricks instance profile"
  value       = module.aws_baseline.instance_profile_arn
}

output "cluster_policy_id" {
  description = "ID of the guardrails cluster policy"
  value       = module.databricks_guardrails.cluster_policy_id
}

output "cluster_policy_name" {
  description = "Name of the guardrails cluster policy"
  value       = module.databricks_guardrails.cluster_policy_name
}

output "secret_scope_name" {
  description = "Name of the platform secret scope"
  value       = module.databricks_guardrails.secret_scope_name
}

output "workload_job_id" {
  description = "ID of the workload job (if enabled)"
  value       = var.enable_workload_job ? module.databricks_jobs.job_id : null
}

output "workload_job_name" {
  description = "Name of the workload job"
  value       = module.databricks_jobs.job_name
}
