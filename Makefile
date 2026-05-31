# Convenience targets that mirror the CI pipeline (.github/workflows/ci.yml).
# Run `make help` for the list. These assume a POSIX shell (Linux/macOS/WSL/Git Bash).

.DEFAULT_GOAL := help
SHELL := /usr/bin/env bash

.PHONY: help install lint compile compose-validate shell-lint yaml-lint secrets ci clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

install: ## Install the dev tooling used by the pipeline
	pip install "ruff==0.15.15" yamllint pre-commit
	pre-commit install

lint: ## Lint the Python exploit clients with ruff
	ruff check .

compile: ## Byte-compile every first-party Python file
	bash scripts/compile-clients.sh

compose-validate: ## Validate every docker-compose.yml (requires Docker)
	bash scripts/validate-compose.sh

shell-lint: ## Run shellcheck on repo-owned shell scripts
	shellcheck scripts/*.sh

yaml-lint: ## Lint repository-owned YAML
	yamllint -c .yamllint.yml .github .yamllint.yml .pre-commit-config.yaml

secrets: ## Scan the working tree for leaked secrets (requires Docker)
	docker run --rm -v "$$PWD:/repo" ghcr.io/gitleaks/gitleaks:latest \
		detect --source /repo --config /repo/.gitleaks.toml --redact --no-banner --verbose

ci: lint compile shell-lint yaml-lint compose-validate secrets ## Run the full local pipeline

clean: ## Remove Python/tooling caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .ruff_cache
