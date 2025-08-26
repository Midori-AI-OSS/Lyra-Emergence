# Lyra-Emergence Development Instructions

**CRITICAL**: Always follow these instructions first. Only fallback to additional search and context gathering if the information here is incomplete or found to be in error.

## Bootstrap & Setup

Install required tools and dependencies:

```bash
# Install uv (Python package manager) - REQUIRED
pip install uv

# Install project dependencies - takes ~6 minutes to download all ML packages
# NEVER CANCEL: Set timeout to 10+ minutes
uv sync

# Verify installation
uv run pytest --version
```

**Dependencies installed**: The project uses heavy ML packages (torch, transformers, langchain, etc.) so initial `uv sync` takes 5-6 minutes to download ~850MB of packages.

## Building & Testing

This is a Python project with no traditional build step:

```bash
# Run all tests - completes in ~3 seconds, NEVER CANCEL anyway
# Always run before committing changes
uv run pytest -v

# Check application help (works offline)
uv run lyra.py --help

# Verify basic imports work
uv run python -c "import src.cli.chat; print('Imports working')"
```

**Test timing**: Test suite completes in 2-3 seconds and includes 12 tests covering journal parsing, embeddings, search, reranking, and Discord bot functionality.

## Running the Application

**CRITICAL NETWORK REQUIREMENT**: The application requires internet connectivity to download HuggingFace models on first run.

```bash
# Main interactive chat (requires internet for model download)
# NEVER CANCEL: First run downloads microsoft/phi-2 model - can take 10+ minutes
# Set timeout to 30+ minutes for first run
uv run lyra.py

# Discord bot (requires DISCORD_BOT_TOKEN environment variable)
uv run discord_bot.py

# Journal operations (also require internet for embedding models)
uv run lyra.py --ingest data/journal/2025-07-17.json
uv run lyra.py --mark <entry-id>
uv run python -m src.publish.export
```

**Expected failures without internet**: All main functionality will fail with `LocalEntryNotFoundError` or connection errors when trying to download models from huggingface.co.

## Docker Execution

```bash
# Build Docker image - NEVER CANCEL: Takes 5-15 minutes depending on base image pull
# Set timeout to 30+ minutes
docker build -t lyra .

# Run with project mounted
docker run --rm -it -v $(pwd):/app lyra uv run lyra.py

# Using Docker Compose - NEVER CANCEL: Similar timing to docker build
# Set timeout to 30+ minutes  
docker compose up -d --build
docker compose down --rmi all
```

**Docker limitations**: Docker build fails without internet connectivity due to package repository access required by the PixelArch base image (`lunamidori5/pixelarch:quartz`).

## Validation Scenarios

**ALWAYS validate changes using these scenarios**:

1. **Test suite validation**:
   ```bash
   uv run pytest -v
   # Expect: 12 passed in ~3 seconds
   ```

2. **Basic CLI validation**:
   ```bash
   uv run lyra.py --help
   # Expect: Usage message with --ingest, --mark, --journal, --rerank options
   ```

3. **Import validation**:
   ```bash
   uv run python -c "from src.cli.chat import ChatSession; print('Core imports work')"
   # Expect: "Core imports work" message
   ```

4. **With internet connection** (if available):
   ```bash
   # Start interactive chat - NEVER CANCEL: Model download takes 10+ minutes first time
   timeout 30 uv run lyra.py
   # Expect: "Lyra Project startup initialized." then model download progress
   ```

5. **Docker validation** (if Docker available):
   ```bash
   docker build -t lyra . && echo "Docker build successful"
   # NOTE: Fails without internet due to package repository access in base image
   ```

## Project Structure & Navigation

**Repository layout** (keep all code out of root):
- `lyra.py` — Main entry point (only executable in repository root)
- `discord_bot.py` — Discord bot entry point  
- `src/` — All source code modules
- `src/tests/` — Test suite (12 test files)
- `src/cli/` — Command-line interface implementation
- `src/vectorstore/` — ChromaDB integration and journal ingestion
- `src/journal/` — Journal parsing and data structures  
- `src/publish/` — Publishing and export functionality
- `src/integrations/` — Discord bot and external integrations
- `src/rerank/` — CPU-based result reranking
- `data/journal/` — Sample journal files in JSON format
- `.codex/` — Contributor documentation and process notes
- `AGENTS.md` — Contributor guidelines and development practices

**Key files to check when making changes**:
- Always run `uv run pytest` after any code changes
- Check `src/tests/` for existing test patterns when adding new tests
- Review `AGENTS.md` for coding standards (type safety, memory safety, comments required)
- Update `.codex/implementation/` docs when adding new features

## Common Commands Reference

```bash
# Quick validation workflow
uv run pytest && echo "Tests pass"

# Development dependency management  
uv add <package>     # Add new dependency
uv remove <package>  # Remove dependency
uv sync             # Sync dependencies from pyproject.toml

# Project inspection
find src/ -name "*.py" | head -10    # Browse source files
ls data/journal/                     # See sample journal data
cat pyproject.toml                   # Check dependencies
```

## Limitations & Known Issues

- **Internet required**: Application fails without internet connectivity due to HuggingFace model downloads
- **Docker network dependency**: Docker build fails without internet due to package repository access in PixelArch base image
- **No linting tools**: No ruff, black, or flake8 configured - follow manual style guidelines in AGENTS.md
- **Model download timing**: First run of main application can take 10+ minutes to download microsoft/phi-2 model  
- **Heavy dependencies**: ML packages total ~850MB, initial sync takes 5-6 minutes
- **25-second test limit**: Repository enforces 25-second test timeout, but current tests complete in 3 seconds

## Timing Expectations

- **Tests**: 2-3 seconds (always safe to run)
- **uv sync**: 5-6 minutes first time (dependency download)
- **First lyra.py run**: 10+ minutes (model download) - **NEVER CANCEL**
- **Docker build**: 5-15 minutes (base image + setup) - **NEVER CANCEL**
- **Subsequent runs**: ~10 seconds (models cached)

## Emergency Recovery

If builds or commands hang:
```bash
# Reset virtual environment
rm -rf .venv
uv sync

# Clear any partial model downloads
rm -rf ~/.cache/huggingface/

# Docker cleanup
docker system prune -f
```

**Remember**: Follow repository coding standards from AGENTS.md - all code must be fully type safe, memory safe, and thoroughly commented.