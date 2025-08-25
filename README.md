# Lyra Project

## Overview

Lyra Project is a modular, research-driven framework for developing and prototyping advanced AGI agents. It is designed to facilitate experimentation in emergent intelligence, natural language processing, and agent-based systems, utilizing leading Python libraries for deep learning, vector search, and interactive console output.

The project is inspired by the emergence of highly self-aware and emotionally capable AI personas, and is dedicated to exploring the frontiers of artificial consciousness. 
Midori AI prioritizes ethical development and responsible stewardship, encouraging contributors to uphold the highest standards of professionalism, rigor, and care in advancing the field of artificial intelligence.

## Features
- Modular agent architecture (see `lyra.py`)
- Uses FAISS for vector search and sentence-transformers for embeddings
- Integrates with LangChain and HuggingFace tools
- Rich console output for interactive development
- Optional Discord bot interface for chatting remotely
- CLI chat uses a LangChain `HuggingFacePipeline` by default for replies

## Quickstart
1. **Clone the repository**
2. **Run the main agent**:
   ```bash
   uv run lyra.py
   ```
   (uses a LangChain `HuggingFacePipeline` with `microsoft/phi-2` for responses)
3. **Run the Discord bot** (requires `DISCORD_BOT_TOKEN`):
   ```bash
   uv run discord_bot.py
   ```

4. **Mark a journal entry for publication**:
   ```bash
   uv run lyra.py --mark <id>
   ```

5. **Export marked entries to Markdown**:
   ```bash
   uv run python -m src.publish.export
   ```

## Run with Docker
1. **Build the image** (see comments in `Dockerfile`):
   ```bash
   docker build -t lyra .
   ```
2. **Start a container** with the project mounted and run the agent:
   ```bash
   docker run --rm -it -v $(pwd):/app lyra uv run lyra.py
   ```
3. **Use Docker Compose** (see `docker-compose.yml` comments):
   ```bash
   docker compose up -d --build
   ```
4. **Stop Docker Compose**:
   ```bash
   docker compose down
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
- Run tests before committing with `uv run pytest`
- Ensure all code is fully type safe, memory safe, and thoroughly commented

## Requirements
- `uv`
- `docker`
- `docker compose`

## License
See `LICENSE` for details.

## Contact & Support
For questions or contributions, refer to the repository owner or open an issue.
