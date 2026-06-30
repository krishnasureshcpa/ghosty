.PHONY: install dev test lint typecheck clean build publish

# ─── Install ────────────────────────────────────────────────────────────────

install:  ## Install ghosty globally via uv tool (available everywhere)
	uv tool install . --force
	@echo ""
	@echo "  ✓ ghosty installed. Run: ghosty"

dev:  ## Install with dev dependencies in local venv
	uv sync --all-extras
	@echo ""
	@echo "  ✓ Dev env ready. Run: uv run ghosty"

# ─── Quality ─────────────────────────────────────────────────────────────────

test:  ## Run tests
	uv run pytest

lint:  ## Lint with ruff
	uv run ruff check src/

typecheck:  ## Type check with mypy
	uv run mypy src/

check: lint typecheck test  ## Run all checks

# ─── Build & Publish ─────────────────────────────────────────────────────────

build:  ## Build wheel + source dist
	uv build

publish: build  ## Build & publish to PyPI (requires PYPI_TOKEN or trusted publishing)
	uv publish

# ─── Clean ───────────────────────────────────────────────────────────────────

clean:  ## Remove build artifacts
	rm -rf dist/ build/ *.egg-info .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# ─── Help ────────────────────────────────────────────────────────────────────

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*##' Makefile | sort | \
		awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
