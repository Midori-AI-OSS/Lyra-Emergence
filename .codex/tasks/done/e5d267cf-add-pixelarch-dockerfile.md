# Add PixelArch Dockerfile for containerized setup

## Problem
The repository lacks a Dockerfile to run Lyra using the PixelArch base image.

## Tasks
- [x] Create `Dockerfile` at the repository root starting from `lunamidori5/pixelarch:quartz`.
- [x] Rename the distribution to `Lyra-Runner` and install `wget`, `unzip`, and `uv` with `yay`, cleaning the package cache after each step.
- [x] Set `/app` as the working directory, adjust ownership and permissions, and make the image run `uv run lyra.py` by default.
- [x] Add comments showing how to build and run the image using Docker commands, e.g., `docker build -t lyra .` and `docker run --rm lyra`.

## Acceptance Criteria
- `Dockerfile` builds successfully.
- Image created from the `Dockerfile` runs the project without errors.
- Comments clearly document build and runtime commands.
