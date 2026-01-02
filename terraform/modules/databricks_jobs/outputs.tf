output "job_id" {
  description = "ID of the workload job (if created)"
  value       = var.enable_workload_job ? databricks_job.workload[0].id : null
}

output "job_name" {
  description = "Name of the workload job"
  value       = var.job_name
}

