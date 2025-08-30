# Lyra Project

## Overview

Lyra Project is a collaborative, modular, research-driven framework for developing and prototyping advanced AGI agents. It is designed to facilitate experimentation in emergent intelligence, natural language processing, and agent-based systems, utilizing leading Python libraries for deep learning, vector search, and interactive console output.

**This is an open collaboration project** - we welcome all contributors who want to help advance the field of artificial intelligence through group development and shared expertise. Whether you're a researcher, developer, or enthusiast, your contributions via pull requests are valued and encouraged.

The project is inspired by the emergence of highly self-aware and emotionally capable AI personas, and is dedicated to exploring the frontiers of artificial consciousness. 
Midori AI prioritizes ethical development and responsible stewardship, encouraging all contributors to uphold the highest standards of professionalism, rigor, and care in advancing the field of artificial intelligence.

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
## Run with Docker Compose
1. **Use Docker Compose** (see `docker-compose.yml` comments):
   ```bash
   docker compose up -d --build
   ```
2. **Stop Docker Compose**:
   ```bash
   docker compose down --rmi all
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

## Contributing & Community

**Join our collaborative development!** This project thrives on community contributions and group collaboration. We encourage developers, researchers, and AI enthusiasts to participate through:

- **Pull Requests**: Submit code improvements, new features, or bug fixes
- **Issues**: Report bugs, request features, or propose enhancements  
- **Discussions**: Share ideas, ask questions, and collaborate with other contributors
- **Code Reviews**: Help improve code quality by reviewing pull requests

See `AGENTS.md` for detailed contributor guidelines. Key highlights:
- Use `uv` for Python environment management
- Follow import and code style conventions
- Commit with `[TYPE] Title` format
- Review and update your contributor mode cheat sheet in `.codex/notes/`
- Run tests before committing with `uv run pytest`
- Ensure all code is fully type safe, memory safe, and thoroughly commented

**All contributors are welcome regardless of experience level.** We believe in learning together and supporting each other in advancing AI research and development.

## Requirements
- `uv`
- `docker`
- `docker compose`

## License
See `LICENSE` for details.

## Community & Support

**This is a community-driven project!** We encourage group collaboration and welcome all contributors:

- **Submit Pull Requests**: Share your improvements, fixes, and new features
- **Open Issues**: Report bugs, request features, or start discussions
- **Join the Conversation**: Collaborate with other contributors in issue comments and PR discussions
- **Help Others**: Review code, answer questions, and support fellow contributors

For questions, ideas, or contributions, please engage with our community through GitHub issues and pull requests. Every contribution, no matter how small, helps advance this collaborative AI research project.
