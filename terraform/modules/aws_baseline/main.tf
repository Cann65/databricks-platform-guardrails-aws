# AWS Baseline Infrastructure for Databricks
# Provides minimal, cost-effective foundational resources

resource "aws_s3_bucket" "databricks_root_storage" {
  bucket        = var.s3_bucket_name
  force_destroy = var.s3_force_destroy

  tags = merge(
    var.common_tags,
    {
      Name        = var.s3_bucket_name
      Description = "Root storage bucket for Databricks workspace"
    }
  )
}

resource "aws_s3_bucket_server_side_encryption_configuration" "databricks_root_storage" {
  bucket = aws_s3_bucket.databricks_root_storage.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "databricks_root_storage" {
  bucket = aws_s3_bucket.databricks_root_storage.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# IAM role for Databricks instance profile
resource "aws_iam_role" "databricks_instance_profile" {
  name               = var.instance_profile_role_name
  assume_role_policy = data.aws_iam_policy_document.ec2_assume_role.json

  tags = merge(
    var.common_tags,
    {
      Name        = var.instance_profile_role_name
      Description = "IAM role for Databricks cluster instances"
    }
  )
}

data "aws_iam_policy_document" "ec2_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

# Basic policy allowing S3 access to the root bucket
resource "aws_iam_role_policy" "databricks_s3_access" {
  name   = "databricks-s3-access"
  role   = aws_iam_role.databricks_instance_profile.id
  policy = data.aws_iam_policy_document.databricks_s3_access.json
}

data "aws_iam_policy_document" "databricks_s3_access" {
  statement {
    sid = "S3BucketAccess"
    actions = [
      "s3:ListBucket",
      "s3:GetBucketLocation"
    ]
    resources = [
      aws_s3_bucket.databricks_root_storage.arn
    ]
  }

  statement {
    sid = "S3ObjectAccess"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject"
    ]
    resources = [
      "${aws_s3_bucket.databricks_root_storage.arn}/*"
    ]
  }
}

resource "aws_iam_instance_profile" "databricks" {
  name = var.instance_profile_role_name
  role = aws_iam_role.databricks_instance_profile.name

  tags = var.common_tags
}

# S3 bucket policy: Require TLS for all requests
resource "aws_s3_bucket_policy" "databricks_root_storage_tls" {
  bucket = aws_s3_bucket.databricks_root_storage.id
  policy = data.aws_iam_policy_document.databricks_s3_tls_only.json
}

data "aws_iam_policy_document" "databricks_s3_tls_only" {
  statement {
    sid    = "DenyInsecureTransport"
    effect = "Deny"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions = ["s3:*"]

    resources = [
      aws_s3_bucket.databricks_root_storage.arn,
      "${aws_s3_bucket.databricks_root_storage.arn}/*"
    ]

    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }
}
