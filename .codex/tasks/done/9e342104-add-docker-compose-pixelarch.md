# Add Docker Compose configuration for PixelArch

## Problem
There is no Docker Compose file to orchestrate the PixelArch container.

## Tasks
- [x] Create `docker-compose.yml` at the repository root that builds the image from the local `Dockerfile`.
- [x] Define a service named `lyra` with `container_name: lyra`, `command: uv run lyra.py`, and mount the repository into `/app`.
- [x] Ensure the compose file uses standard Docker Compose directives.
- [x] Add comments describing how to start and stop the service, e.g., `docker compose up -d --build` and `docker compose down`.

## Acceptance Criteria
- Running `docker compose up -d --build` builds and starts the service without errors.
- Service uses the local `Dockerfile` and runs `uv run lyra.py`.
- Comments clearly explain start and stop commands.
