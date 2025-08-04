# Lyra Project

## Overview
Lyra Project is an experimental AGI agent framework designed for research and prototyping in emergent intelligence, language processing, and agent-based systems. It leverages modern Python libraries for deep learning, vector search, and rich console output.

## Features
- Modular agent architecture (see `lyra.py`)
- Uses FAISS for vector search and sentence-transformers for embeddings
- Integrates with LangChain and HuggingFace tools
- Rich console output for interactive development

## Quickstart
1. **Clone the repository**
2. **Run the main agent**:
   ```bash
   uv run lyra.py
   ```

## Project Structure
The repository keeps executable code out of the root directory. All implementations live under `src/`, with tests in `src/tests/`.

- `lyra.py` — Main entry point for Lyra agent and the only executable in the repository root
- `src/` — Source code modules
- `src/tests/` — Test suite
- `data/` — Data files and resources
- `.codex/` — Contributor docs and instructions
- `AGENTS.md` — Contributor guide and development practices
- `pyproject.toml` — Python dependencies and project metadata

## Contributor Guidelines
See `AGENTS.md` for full details. Highlights:
- Use `uv` for Python environment management
- Follow import and code style conventions
- Commit with `[TYPE] Title` format
- Review and update your contributor mode cheat sheet in `.codex/notes/`
- Run tests before committing (pytest recommended)
- Ensure all code is fully type safe, memory safe, and thoroughly commented

## Requirements
- `uv`

## License
See `LICENSE` for details.

## Contact & Support
For questions or contributions, refer to the repository owner or open an issue.