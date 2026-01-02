output "s3_bucket_name" {
  description = "Name of the Databricks root storage bucket"
  value       = aws_s3_bucket.databricks_root_storage.bucket
}

output "s3_bucket_arn" {
  description = "ARN of the Databricks root storage bucket"
  value       = aws_s3_bucket.databricks_root_storage.arn
}

output "instance_profile_arn" {
  description = "ARN of the Databricks instance profile"
  value       = aws_iam_instance_profile.databricks.arn
}

output "instance_profile_role_arn" {
  description = "ARN of the IAM role attached to the instance profile"
  value       = aws_iam_role.databricks_instance_profile.arn
}
