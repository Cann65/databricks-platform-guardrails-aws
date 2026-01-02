# Databricks Job to run the bronze → silver → gold workload

terraform {
  required_providers {
    databricks = {
      source = "databricks/databricks"
    }
  }
}

resource "databricks_job" "workload" {
  count = var.enable_workload_job ? 1 : 0

  name        = var.job_name
  description = "Runs the guardrails demo pipeline notebooks (bronze -> silver -> gold)"

  job_cluster {
    job_cluster_key = "guardrails_demo_cluster"

    new_cluster {
      num_workers   = var.num_workers
      spark_version = var.spark_version
      node_type_id  = var.node_type_id
      policy_id     = var.cluster_policy_id

      custom_tags = {
        owner       = var.owner_tag
        cost_center = var.cost_center_tag
        env         = var.environment
      }
    }
  }

  task {
    task_key        = "01_ingest_bronze"
    description     = "Generate synthetic data into bronze Delta"
    job_cluster_key = "guardrails_demo_cluster"

    notebook_task {
      notebook_path = "${var.notebook_base_path}/01_ingest_bronze.py"
      base_parameters = {
        output_base_path = var.output_base_path
      }
    }
  }

  task {
    task_key        = "02_transform_silver"
    description     = "Cleanse bronze -> silver Delta"
    job_cluster_key = "guardrails_demo_cluster"
    depends_on {
      task_key = "01_ingest_bronze"
    }

    notebook_task {
      notebook_path = "${var.notebook_base_path}/02_transform_silver.py"
      base_parameters = {
        output_base_path = var.output_base_path
      }
    }
  }

  task {
    task_key        = "03_aggregate_gold"
    description     = "Aggregate silver -> gold Delta"
    job_cluster_key = "guardrails_demo_cluster"
    depends_on {
      task_key = "02_transform_silver"
    }

    notebook_task {
      notebook_path = "${var.notebook_base_path}/03_aggregate_gold.py"
      base_parameters = {
        output_base_path = var.output_base_path
      }
    }
  }

  tags = {
    environment = var.environment
    managed_by  = "terraform"
  }
}
