variable "s3_bucket_name" {
  description = "Name of the S3 bucket for Databricks root storage"
  type        = string
}

variable "s3_force_destroy" {
  description = "Allow terraform destroy to delete bucket even if not empty (useful for dev, dangerous for prod)"
  type        = bool
  default     = false
}

variable "instance_profile_role_name" {
  description = "Name of the IAM role and instance profile for Databricks clusters"
  type        = string
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}
