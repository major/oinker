.PHONY: all lint format typecheck test check clean complexity

all: check

lint:
	uv run ruff check .

format:
	uv run ruff format .

format-check:
	uv run ruff format --check .

typecheck:
	uv run ty check

test:
	uv run pytest

test-cov:
	uv run pytest --cov-report=html

check: lint format-check typecheck test

fix:
	uv run ruff check --fix .
	uv run ruff format .

complexity:
	@output=$$(uv run radon cc src/oinker -n D -s); \
	if [ -n "$$output" ]; then \
		echo "$$output"; \
		echo "ERROR: Functions with complexity D or higher found"; \
		exit 1; \
	else \
		echo "Complexity check passed (no D+ functions)"; \
	fi

clean:
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
