variable "policy_name" {
  description = "Name of the cluster policy"
  type        = string
  default     = "guardrails-default"
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

variable "default_owner_tag" {
  description = "Default value for owner tag"
  type        = string
  default     = "platform-team"
}

variable "default_cost_center_tag" {
  description = "Default value for cost_center tag"
  type        = string
  default     = "data-platform"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "secret_scope_name" {
  description = "Name of the platform secret scope"
  type        = string
  default     = "platform"
}

variable "enable_demo_job" {
  description = "Whether to create a demo job for testing"
  type        = bool
  default     = false
}

variable "spark_version" {
  description = "Spark version for demo job (if enabled)"
  type        = string
  default     = "13.3.x-scala2.12"
}

variable "demo_notebook_path" {
  description = "Notebook path for demo job (if enabled)"
  type        = string
  default     = "/Shared/demo-compliance-check"
}
