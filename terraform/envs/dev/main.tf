# Development Environment Configuration
# This config assumes Databricks workspace already exists

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = "dev"
      ManagedBy   = "terraform"
      Project     = "databricks-platform-guardrails"
    }
  }
}

# Databricks provider configuration
# Expects DATABRICKS_HOST and DATABRICKS_TOKEN environment variables
provider "databricks" {
  # host  = var.databricks_host  # Set via DATABRICKS_HOST env var
  # token = var.databricks_token # Set via DATABRICKS_TOKEN env var
}

# AWS baseline infrastructure
module "aws_baseline" {
  source = "../../modules/aws_baseline"

  s3_bucket_name             = var.s3_bucket_name
  s3_force_destroy           = var.s3_force_destroy
  instance_profile_role_name = var.instance_profile_role_name

  common_tags = {
    Environment = "dev"
    Owner       = var.owner_tag
    CostCenter  = var.cost_center_tag
  }
}

# Databricks guardrails
module "databricks_guardrails" {
  source = "../../modules/databricks_guardrails"

  environment                 = "dev"
  max_workers                 = var.max_workers
  max_autotermination_minutes = var.max_autotermination_minutes
  allowed_node_types          = var.allowed_node_types
  default_node_type           = var.default_node_type
  default_owner_tag           = var.owner_tag
  default_cost_center_tag     = var.cost_center_tag
  enable_demo_job             = var.enable_demo_job
}
