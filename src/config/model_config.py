"""Model configuration management for HuggingFace models."""

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from src.config.model_recommendations import recommend_model
from src.utils.system_info import detect_optimal_memory_config, get_available_memory

logger = logging.getLogger(__name__)


REPO_ROOT = Path(__file__).resolve().parents[2]
APPROVED_CONFIG_DIRS = [
    (REPO_ROOT / "config").resolve(),
    (REPO_ROOT / "data").resolve(),
]
DEFAULT_CONFIG_FILENAMES = ("model_config.json",)


def _path_is_within_allowed_directory(path: Path) -> bool:
    """Check whether the path is inside one of the approved directories."""

    for allowed_dir in APPROVED_CONFIG_DIRS:
        allowed_dir = allowed_dir.resolve(strict=False)
        try:
            path.relative_to(allowed_dir)
            return True
        except ValueError:
            continue

    return False


def _resolve_and_validate_config_path(config_path: Path) -> Path:
    """Resolve and validate that a config path stays within approved directories."""

    resolved_path = config_path.expanduser().resolve(strict=False)

    if not _path_is_within_allowed_directory(resolved_path):
        allowed_dirs = ", ".join(str(directory) for directory in APPROVED_CONFIG_DIRS)
        raise ValueError(
            "Config path escapes approved directories. "
            f"Resolved path: {resolved_path}. Approved directories: {allowed_dirs}"
        )

    return resolved_path


@dataclass
class ModelConfig:
    """Configuration class for HuggingFace model loading parameters.

    This class defines the configurable parameters for model loading,
    including device mapping, memory management, and quantization options.
    """

    # Model identification
    model_id: str = "Qwen/Qwen2.5-7B-Instruct"
    task: str = "text-generation"

    # Device and memory configuration
    device_map: str | None = None  # "auto", "cpu", or custom mapping
    max_memory: dict[str, str] | None = None  # e.g., {"0": "8GB", "cpu": "16GB"}
    low_cpu_mem_usage: bool = True

    # Progressive fallback configuration
    gpu_layers_fallback: int | None = (
        None  # Number of layers to keep on GPU during fallback
    )
    enable_progressive_fallback: bool = True

    # Quantization options
    load_in_8bit: bool = False
    load_in_4bit: bool = False

    # Pipeline-specific parameters
    pipeline_kwargs: dict[str, Any] | None = None

    def to_model_kwargs(self) -> dict[str, Any]:
        """Convert configuration to model loading kwargs.

        Returns:
            Dictionary of kwargs suitable for HuggingFace model loading
        """
        kwargs = {}

        if self.device_map is not None:
            kwargs["device_map"] = self.device_map

        if self.max_memory is not None:
            kwargs["max_memory"] = self.max_memory

        if self.low_cpu_mem_usage:
            kwargs["low_cpu_mem_usage"] = self.low_cpu_mem_usage

        if self.load_in_8bit:
            kwargs["load_in_8bit"] = self.load_in_8bit

        if self.load_in_4bit:
            kwargs["load_in_4bit"] = self.load_in_4bit

        return kwargs

    def to_pipeline_kwargs(self) -> dict[str, Any]:
        """Get pipeline-specific kwargs.

        Returns:
            Dictionary of pipeline kwargs
        """
        return self.pipeline_kwargs or {}


def load_config(
    config_path: Path | None = None, auto_select: bool = False
) -> ModelConfig:
    """Load model configuration from file or return default.

    Args:
        config_path: Path to configuration file. If None, looks for default locations.
        auto_select: If True, automatically select optimal model based on system resources.

    Returns:
        ModelConfig instance with loaded or default configuration
    """
    resolved_config_path: Path | None = None

    if config_path is None:
        # Look for default config file locations within approved directories
        for directory in APPROVED_CONFIG_DIRS:
            for filename in DEFAULT_CONFIG_FILENAMES:
                candidate_path = directory / filename
                if candidate_path.exists():
                    resolved_config_path = _resolve_and_validate_config_path(
                        candidate_path
                    )
                    break
            if resolved_config_path:
                break
    else:
        resolved_config_path = _resolve_and_validate_config_path(config_path)

    base_config = ModelConfig()

    # Load from file if available
    if resolved_config_path and resolved_config_path.exists():
        try:
            with open(resolved_config_path, encoding="utf-8") as f:
                config_data = json.load(f)

            logger.info(f"Loaded model configuration from {resolved_config_path}")
            base_config = ModelConfig(**config_data)

        except Exception as e:
            logger.warning(
                f"Failed to load config from {resolved_config_path}: {e}. Using defaults."
            )

    # Auto-select model if requested
    if auto_select:
        logger.info("Auto-selecting optimal model based on system resources...")
        ram_gb, vram_gb = get_available_memory()
        recommended = recommend_model(ram_gb, vram_gb)

        if recommended:
            base_config.model_id = recommended.model_id

            # Set optimal memory configuration
            optimal_memory = detect_optimal_memory_config(ram_gb, vram_gb)
            base_config.max_memory = optimal_memory

            # Enable progressive fallback for better resource utilization
            base_config.enable_progressive_fallback = True

            # Auto-configure quantization if needed
            if (
                vram_gb < recommended.recommended_vram_gb
                and "8bit" in recommended.quantization_support
            ):
                base_config.load_in_8bit = True
                logger.info("Enabled 8-bit quantization due to limited VRAM")
            elif (
                vram_gb < recommended.min_vram_gb
                and "4bit" in recommended.quantization_support
            ):
                base_config.load_in_4bit = True
                logger.info("Enabled 4-bit quantization due to very limited VRAM")

            # Set device map based on available resources
            if vram_gb > 1.0:
                base_config.device_map = "auto"
            else:
                base_config.device_map = "cpu"
                logger.info("Using CPU-only mode due to insufficient VRAM")

            logger.info(
                f"Auto-selected model: {recommended.model_id} ({recommended.parameter_count})"
            )
        else:
            logger.warning("Could not auto-select model, using default configuration")

    if base_config.device_map is None:
        logger.info("Using default model configuration")

    return base_config


def save_config(config: ModelConfig, config_path: Path) -> None:
    """Save model configuration to file.

    Args:
        config: ModelConfig instance to save
        config_path: Path where to save the configuration
    """
    resolved_config_path = _resolve_and_validate_config_path(config_path)

    resolved_config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(resolved_config_path, "w", encoding="utf-8") as f:
        json.dump(asdict(config), f, indent=2)

    logger.info(f"Saved model configuration to {resolved_config_path}")


# Default configuration instance for convenience
DEFAULT_CONFIG = ModelConfig()
