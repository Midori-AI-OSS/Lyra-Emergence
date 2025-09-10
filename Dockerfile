# PixelArch-based runtime for Lyra
#
# Build with:
#   docker build -t lyra .
# Run with:
#   docker run --rm -it -v $(pwd):/app lyra

FROM lunamidori5/pixelarch:quartz

# Rename distribution for clarity
RUN sudo sed -i 's/Quartz/Lyra-Runner/g' /etc/os-release

# Install utilities and clean cache
RUN yay -Syu --noconfirm wget && yay -Yccc --noconfirm
RUN yay -Syu --noconfirm unzip && yay -Yccc --noconfirm
RUN yay -Syu --noconfirm uv && yay -Yccc --noconfirm

# Install system dependencies for Playwright browsers
RUN yay -Syu --noconfirm nss atk at-spi2-atk gtk3 cups-libs drm \
    libxss libgconf alsa-lib && yay -Yccc --noconfirm

# Show build-time user info
RUN echo "User: $(whoami), UID: $(id -u), GID: $(id -g)"

WORKDIR /app

# Ensure proper ownership and permissions
RUN sudo chown -R $(whoami):$(whoami) /app && sudo chmod -R 755 /app

# Copy project files and install dependencies
COPY pyproject.toml ./
RUN uv sync

# Install Playwright browsers (this may take some time)
RUN uv run playwright install chromium

CMD ["uv", "run", "lyra.py"]
