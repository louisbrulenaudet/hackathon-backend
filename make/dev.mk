.PHONY: dev prod test sync sync-all check format update pre-commit clean-venv export-requirements install

dev: ## Start development server
	@echo "🚀 Starting development server..."
	uv run fastapi dev $(APP)

prod: ## Start production server
	@echo "🚀 Starting production server..."
	uv run fastapi run $(APP) --host $(HOST) --port $(PORT)

test: ## Run tests
	@echo "🧪 Running tests..."
	uv run pytest

sync: ## Install/sync dependencies (uv.lock + dev extra; matches CI)
	@echo "📦 Syncing project environment..."
	uv sync --extra dev

sync-all: ## Sync with all optional extras from pyproject.toml
	@echo "📦 Syncing project environment with all extras..."
	uv sync --all-extras

install: sync ## Install project dependencies (alias for sync)

check: ## Run code quality checks
	@echo "🔍 Running code analysis..."
	uv run ruff check .

format: ## Format source code
	@echo "🔧 Formatting code..."
	uv run ruff format .
	uv run ruff check . --fix

update: ## Update locked dependencies and apply
	@echo "📡 Upgrading dependencies..."
	uv lock --upgrade
	uv sync --extra dev
	@echo "✅ Dependencies updated successfully"

clean-venv: ## Remove local Python virtual environment (.venv)
	@echo "🧹 Removing virtual environment..."
	rm -rf .venv

pre-commit: ## Run pre-commit checks
	uv run pre-commit run --all-files
