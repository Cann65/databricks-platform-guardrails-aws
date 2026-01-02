variable "aws_region" {
  description = "AWS region for infrastructure"
  type        = string
  default     = "us-east-1"
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket for Databricks root storage"
  type        = string
}

variable "s3_force_destroy" {
  description = "Allow terraform destroy to delete bucket even if not empty (useful for dev)"
  type        = bool
  default     = true # Safe for dev environment, set to false for prod
}

variable "instance_profile_role_name" {
  description = "Name of the IAM role and instance profile"
  type        = string
  default     = "databricks-dev-instance-profile"
}

variable "owner_tag" {
  description = "Owner tag for resources"
  type        = string
  default     = "platform-team"
}

variable "cost_center_tag" {
  description = "Cost center tag for resources"
  type        = string
  default     = "data-platform"
}

variable "max_workers" {
  description = "Maximum number of workers allowed in clusters"
  type        = number
  default     = 8
}

variable "max_autotermination_minutes" {
  description = "Maximum auto-termination timeout in minutes"
  type        = number
  default     = 15
}

variable "allowed_node_types" {
  description = "Allowlist of node types for cost control"
  type        = list(string)
  default = [
    "i3.xlarge",
    "i3.2xlarge",
    "m5d.large",
    "m5d.xlarge"
  ]
}

variable "default_node_type" {
  description = "Default node type for clusters"
  type        = string
  default     = "i3.xlarge"
}

variable "enable_demo_job" {
  description = "Whether to create a demo job for testing"
  type        = bool
  default     = false
}

variable "spark_version" {
  description = "Spark runtime version for Databricks jobs"
  type        = string
  default     = "13.3.x-scala2.12"
}

variable "enable_workload_job" {
  description = "Whether to create the Databricks workload job"
  type        = bool
  default     = false
}

variable "workload_job_name" {
  description = "Name of the Databricks workload job"
  type        = string
  default     = "guardrails-demo-pipeline"
}

variable "notebook_base_path" {
  description = "Workspace path for workload notebooks (e.g., /Repos/<user>/databricks-platform-guardrails-aws/workload/notebooks)"
  type        = string
  default     = "/Repos/<user>/databricks-platform-guardrails-aws/workload/notebooks"
}

variable "output_base_path" {
  description = "DBFS base path for Delta outputs"
  type        = string
  default     = "dbfs:/tmp/guardrails_demo"
}

variable "workload_job_workers" {
  description = "Worker count for workload job cluster"
  type        = number
  default     = 2
}

variable "workload_autotermination_minutes" {
  description = "Auto-termination timeout for workload job cluster"
  type        = number
  default     = 15
}
