variable "enable_workload_job" {
  description = "Whether to create the Databricks workload job"
  type        = bool
  default     = false
}

variable "job_name" {
  description = "Name of the Databricks job"
  type        = string
  default     = "guardrails-demo-pipeline"
}

variable "notebook_base_path" {
  description = "Workspace path containing the workload notebooks"
  type        = string
}

variable "output_base_path" {
  description = "DBFS base path for Delta outputs"
  type        = string
  default     = "dbfs:/tmp/guardrails_demo"
}

variable "cluster_policy_id" {
  description = "Optional cluster policy ID to attach to the job cluster"
  type        = string
  default     = null
}

variable "spark_version" {
  description = "Spark runtime version"
  type        = string
  default     = "13.3.x-scala2.12"
}

variable "node_type_id" {
  description = "Node type for the job cluster"
  type        = string
  default     = "i3.xlarge"
}

variable "num_workers" {
  description = "Worker count for the job cluster"
  type        = number
  default     = 2
}

variable "owner_tag" {
  description = "Owner tag applied to job cluster"
  type        = string
  default     = "platform-team"
}

variable "cost_center_tag" {
  description = "Cost center tag applied to job cluster"
  type        = string
  default     = "data-platform"
}

variable "environment" {
  description = "Environment label for tagging"
  type        = string
  default     = "dev"
}
