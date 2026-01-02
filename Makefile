.PHONY: help init fmt validate plan apply destroy audit test lint ci clean install

# Default target
help:
	@echo "Databricks Platform Guardrails - Makefile"
	@echo ""
	@echo "Terraform targets:"
	@echo "  make init      - Initialize Terraform"
	@echo "  make fmt       - Format Terraform files"
	@echo "  make validate  - Validate Terraform configuration"
	@echo "  make plan      - Show Terraform plan"
	@echo "  make apply     - Apply Terraform changes"
	@echo "  make destroy   - Destroy Terraform resources"
	@echo ""
	@echo "Python auditor targets:"
	@echo "  make install   - Install auditor dependencies"
	@echo "  make audit     - Run compliance audit"
	@echo "  make test      - Run Python tests"
	@echo "  make lint      - Run Python linter (ruff)"
	@echo ""
	@echo "CI/CD targets:"
	@echo "  make ci        - Run all CI checks (lint + test + terraform checks)"
	@echo "  make clean     - Clean generated files"

# Terraform directory
TF_DIR = terraform/envs/dev

# Python auditor directory
AUDITOR_DIR = auditor

# === Terraform targets ===

init:
	cd $(TF_DIR) && terraform init

fmt:
	cd $(TF_DIR) && terraform fmt -recursive ../../

validate: init
	cd $(TF_DIR) && terraform validate

plan: init
	cd $(TF_DIR) && terraform plan

apply: init
	cd $(TF_DIR) && terraform apply

destroy: init
	cd $(TF_DIR) && terraform destroy

# === Python auditor targets ===

install:
	cd $(AUDITOR_DIR) && pip install -e ".[dev]"

audit:
	cd $(AUDITOR_DIR) && python -m databricks_auditor.cli audit --out ../reports --format html,md,json

test:
	cd $(AUDITOR_DIR) && PYTHONPATH=.. pytest

lint:
	cd $(AUDITOR_DIR) && ruff check .

# === CI/CD targets ===

ci: lint test
	@echo "Running Terraform format check..."
	cd $(TF_DIR) && terraform fmt -check -recursive ../../
	@echo "Running Terraform validate..."
	cd $(TF_DIR) && terraform init -backend=false
	cd $(TF_DIR) && terraform validate
	@echo ""
	@echo "✅ All CI checks passed!"

clean:
	rm -rf reports/
	rm -rf $(AUDITOR_DIR)/.pytest_cache
	rm -rf $(AUDITOR_DIR)/databricks_auditor.egg-info
	rm -rf $(AUDITOR_DIR)/dist
	rm -rf $(AUDITOR_DIR)/build
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
