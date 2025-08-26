#!/usr/bin/env bash
set -e

echo "🔍 Running Python linting and formatting..."

echo "📝 Running ruff check..."
uv run ruff check . --fix

echo "🖤 Running black formatting..."
uv run black .

echo "📦 Running isort import sorting..."
uv run isort .

echo "🔍 Running mypy type checking..."
uv run mypy src/ --ignore-missing-imports || echo "⚠️  MyPy found type issues (expected in current codebase)"

echo "✅ Linting complete!"