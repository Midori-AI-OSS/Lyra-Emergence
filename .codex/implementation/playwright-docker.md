# Playwright Tools in Docker/PixelArch

The Playwright tools require browser binaries to be installed. This document describes how to handle this in different environments.

## Docker Environment (PixelArch)

The `Dockerfile` has been updated to:

1. Install system dependencies required by Playwright browsers
2. Copy project files and install Python dependencies with `uv sync`
3. Install Chromium browser binary with `uv run playwright install chromium`

### Building Docker Image

```bash
docker build -t lyra .
```

**Note**: The Docker build process downloads ~100MB of browser binaries, so ensure you have adequate internet connectivity and build timeout.

### Running in Docker

```bash
# Standard run
docker run --rm -it -v $(pwd):/app lyra

# With Docker Compose
docker compose up -d --build
```

## Local Development

For local development outside Docker:

```bash
# Install dependencies
uv sync

# Install Playwright browsers
uv run playwright install

# Or install only Chromium
uv run playwright install chromium
```

## System Dependencies

Playwright requires several system libraries. On PixelArch/Arch Linux:

```bash
yay -S nss atk at-spi2-atk gtk3 cups-libs drm libxss libgconf alsa-lib
```

## Tool Behavior

The Playwright tools will:

- Work normally when browsers are properly installed
- Return clear error messages when browsers are missing
- Gracefully handle import errors if Playwright package is unavailable
- Respect environment-based tool enabling (PixelArch + network required)

## Troubleshooting

### Browser Not Found Error

```
BrowserType.launch: Executable doesn't exist at /home/user/.cache/ms-playwright/...
```

**Solution**: Run `uv run playwright install chromium`

### System Dependencies Missing

```
...libX11.so.6: cannot open shared object file...
```

**Solution**: Install system dependencies as listed above

### Permission Issues in Docker

If you encounter permission issues, ensure the Docker container user has proper permissions:

```bash
# In Dockerfile
RUN sudo chown -R $(whoami):$(whoami) /app
```

## Performance Considerations

- Browser downloads are ~100MB per browser type
- First-time tool usage may be slower due to browser startup
- Consider using headless mode for better performance in containers
- Tools automatically clean up browser instances after use