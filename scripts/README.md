# Scripts Directory

This directory contains utility scripts for the Lyra-Emergence project development and CI/CD pipeline.

## Available Scripts

### `validate_json.py`
Validates all JSON files in a directory recursively.

**Usage:**
```bash
python scripts/validate_json.py data/
uv run python scripts/validate_json.py data/
```

**Features:**
- Validates JSON syntax and structure
- Recursive directory traversal
- Detailed error reporting
- Checks for common formatting issues
- Exit codes for CI/CD integration

### `lint.sh`
Runs all Python linting and formatting tools in sequence.

**Usage:**
```bash
./scripts/lint.sh
```

**Includes:**
- Ruff linting with automatic fixes
- Black code formatting
- Isort import sorting
- MyPy type checking

### `test_ci_pipeline.py`
Tests the CI/CD pipeline components locally before pushing to GitHub.

**Usage:**
```bash
python scripts/test_ci_pipeline.py
uv run python scripts/test_ci_pipeline.py
```

**Tests:**
- JSON validation across all data files
- Python test suite execution
- Basic pipeline component validation

### `convert_conversations.py`
Transforms plain-text transcripts of conversations between Brian/Sandi and Lyra
into prompt/response pairs that can be fed into fine-tuning pipelines.

**Usage:**
```bash
uv run python scripts/convert_conversations.py path/to/transcript.txt
uv run python scripts/convert_conversations.py transcript1.txt transcript2.txt -o output.jsonl
```

**Features:**
- Supports one or multiple transcripts at a time
- Emits JSON Lines (default) or JSON arrays via `--format`
- Adds metadata identifying the original speaker and conversation index
- Gracefully reports formatting issues in the source transcript

## CI/CD Integration

These scripts are integrated into the GitHub Actions workflow (`.github/workflows/ci.yml`) to ensure:

1. **JSON Linting**: All JSON files in the `data/` directory are validated
2. **Python Linting**: Code style and quality checks using ruff, black, isort, and mypy
3. **Testing**: Full test suite execution with pytest

The CI pipeline runs on all pushes and pull requests to main and develop branches.

## Development Workflow

1. **Before committing**: Run `./scripts/lint.sh` to fix formatting
2. **Validate changes**: Run `python scripts/test_ci_pipeline.py` to test locally
3. **JSON validation**: Run `python scripts/validate_json.py data/` if you've modified JSON files

## Requirements

All scripts require the project dependencies to be installed:

```bash
uv sync
uv add --dev ruff black isort mypy
```