#!/usr/bin/env bash
# Single quality gate. Used by the Stop hook, the headless runner and CI.
set -euo pipefail
cd "$(dirname "$0")/.."
uv run --frozen --quiet ruff check --quiet .
uv run --frozen --quiet ruff format --check --quiet .
uv run --frozen --quiet mypy --no-error-summary
uv run --frozen --quiet pytest --cov --cov-report=json:coverage.json --cov-report=term:skip-covered
uv run --frozen --quiet python scripts/spec_trace.py
uv run --frozen --quiet python scripts/crap.py --changed-from "${VERIFY_BASE:-origin/main}"
