# Document Docker and uv run guide in README

## Problem
Users lack clear instructions for running Lyra via Docker and uv. README does not explain how to build or use the Docker image provided by the repository.

## Tasks
- [ ] Add a "Run with Docker" section to README covering:
  - Building the image with `docker build -t lyra .`
  - Running the container with volume mounts and `uv run lyra.py`
  - Using `docker compose up -d --build` per `docker-compose.yml`
- [ ] Ensure Quickstart keeps `uv run` examples for direct execution outside Docker.
- [ ] Mention required tools (`docker`, `docker compose`, `uv`) in prerequisites.
- [ ] Cross-reference `Dockerfile` comments for build/run usage.
- [ ] Confirm README changes follow repository style and pass `uv run pytest`.

## Acceptance Criteria
- README clearly explains both local `uv` execution and Docker-based execution.
- Examples include exact commands for building and running the container.
- Instructions align with existing `Dockerfile` and `docker-compose.yml`.
- Tests still pass after documentation update.
