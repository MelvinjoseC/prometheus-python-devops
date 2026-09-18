.PHONY: help install dev-install lint format test test-cov docker-build docker-run compose-up compose-down security-check clean

# Default shell
SHELL := /bin/bash

help: ## Display available make commands
	@echo "========================================================================"
	@echo "Prometheus Python Client - DevOps & Developer Automation"
	@echo "========================================================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install package in editable mode
	python -m pip install --upgrade pip
	python -m pip install -e .

dev-install: install ## Install all development and test dependencies
	python -m pip install tox pytest coverage flake8 isort mypy pip-audit pre-commit
	pre-commit install

lint: ## Run code linters (flake8, isort check, mypy)
	flake8 prometheus_client/ tests/
	isort --check prometheus_client/ tests/
	mypy --install-types --non-interactive prometheus_client/ tests/

format: ## Format codebase automatically using isort
	isort prometheus_client/ tests/

test: ## Run unit tests with pytest
	pytest -v tests/

test-cov: ## Run unit tests with coverage report
	coverage run -m pytest tests/
	coverage report -m

docker-build: ## Build production Docker container image
	docker build -t prometheus-python-app:latest -f Dockerfile .

docker-run: ## Run container image locally on port 8000
	docker run --rm -p 8000:8000 --name prometheus-python-app prometheus-python-app:latest

compose-up: ## Spin up local observability stack (App + Prometheus + Grafana + Alertmanager)
	docker compose up -d --build
	@echo "========================================================================"
	@echo "Observability sandbox is running:"
	@echo "  * Application & Metrics : http://localhost:8000/metrics"
	@echo "  * Prometheus UI         : http://localhost:9090"
	@echo "  * Grafana Dashboard     : http://localhost:3000 (admin / admin)"
	@echo "  * Alertmanager UI       : http://localhost:9093"
	@echo "========================================================================"

compose-down: ## Tear down local observability stack and clean volumes
	docker compose down -v

security-check: ## Scan dependencies and container for known CVEs
	pip-audit --desc

clean: ## Remove build, test, and python bytecode artifacts
	rm -rf build/ dist/ *.egg-info .tox/ .pytest_cache/ .mypy_cache/ .coverage htmlcov/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
