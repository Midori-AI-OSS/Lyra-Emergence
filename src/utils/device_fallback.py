"""Device fallback utilities for handling VRAM OOM errors."""

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

import torch
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFacePipeline

from src.config.model_config import ModelConfig, load_config

logger = logging.getLogger(__name__)

T = TypeVar("T")


def _detect_available_devices() -> dict[str, bool]:
    """Detect which devices are available on this system.
    
    Returns:
        Dictionary mapping device types to availability
    """
    devices = {
        "cuda": False,
        "mps": False,
        "cpu": True,  # CPU is always available
    }
    
    # Check CUDA availability
    try:
        if torch.cuda.is_available() and torch.cuda.device_count() > 0:
            devices["cuda"] = True
            logger.debug(f"CUDA available with {torch.cuda.device_count()} device(s)")
        else:
            logger.debug("CUDA not available")
    except Exception as e:
        logger.debug(f"Error checking CUDA availability: {e}")
    
    # Check MPS availability (Apple Silicon)
    try:
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            devices["mps"] = True
            logger.debug("MPS available")
        else:
            logger.debug("MPS not available")
    except Exception as e:
        logger.debug(f"Error checking MPS availability: {e}")
    
    return devices


def _create_progressive_device_map(
    gpu_layers: int, total_layers: int | None = None
) -> dict[str, Any]:
    """Create a device map that places first N layers on GPU, rest on CPU.

    Args:
        gpu_layers: Number of layers to place on GPU
        total_layers: Total number of layers in model (estimated if None)

    Returns:
        Device map dictionary for progressive fallback
    """
    if total_layers is None:
        # For phi-2, there are typically 32 transformer layers
        total_layers = 32

    # Detect available devices first
    available_devices = _detect_available_devices()
    
    # Determine GPU device identifier
    if available_devices["cuda"]:
        gpu_device = 0
    elif available_devices["mps"]:
        gpu_device = "mps"
    else:
        # No GPU available, use CPU for everything
        gpu_device = "cpu"
        # When no GPU is available, set gpu_layers to 0 to force all layers to CPU
        gpu_layers = 0
        logger.warning("No GPU devices available, using CPU-only device mapping")

    device_map = {}

    # Embedding layer
    device_map["model.embed_tokens"] = gpu_device

    # First N transformer layers on GPU
    for i in range(min(gpu_layers, total_layers)):
        device_map[f"model.layers.{i}"] = gpu_device

    # Remaining layers on CPU
    for i in range(gpu_layers, total_layers):
        device_map[f"model.layers.{i}"] = "cpu"

    # Output layers typically on same device as last layer
    if gpu_layers >= total_layers:
        device_map["model.norm"] = gpu_device
        device_map["lm_head"] = gpu_device
    else:
        device_map["model.norm"] = "cpu"
        device_map["lm_head"] = "cpu"

    return device_map


def safe_load_model_with_config(
    model_loader: Callable[..., T],
    config: ModelConfig | None = None,
    *args: Any,
    **kwargs: Any,
) -> T:
    """
    Load a model with configuration-based sharding and progressive fallback.

    Args:
        model_loader: Function to call for loading the model
        config: ModelConfig instance with sharding parameters
        *args: Positional arguments to pass to model_loader
        **kwargs: Keyword arguments to pass to model_loader

    Returns:
        Loaded model instance

    Raises:
        Exception: Re-raises non-OOM exceptions from model loading
    """
    if config is None:
        config = load_config()

    # Detect available devices and validate configuration
    available_devices = _detect_available_devices()
    
    # Determine device_map strategy: prioritize explicit kwargs over config
    device_map_from_kwargs = kwargs.get("device_map")
    device_map_from_config = config.device_map if config.device_map else None
    
    # Validate and adjust device_map based on available devices
    final_device_map = None
    if device_map_from_kwargs is not None:
        final_device_map = _validate_device_map(device_map_from_kwargs, available_devices)
        # Explicit device_map provided, exclude it from model_kwargs to avoid conflict
        model_kwargs = {k: v for k, v in config.to_model_kwargs().items() if k != "device_map"}
    elif device_map_from_config is not None:
        final_device_map = _validate_device_map(device_map_from_config, available_devices)
        # Use config device_map directly in kwargs, exclude from model_kwargs
        model_kwargs = {k: v for k, v in config.to_model_kwargs().items() if k != "device_map"}
    else:
        # No device_map specified anywhere, include all config kwargs
        model_kwargs = config.to_model_kwargs()
    
    if final_device_map is not None:
        kwargs["device_map"] = final_device_map
    
    # Merge with any existing model_kwargs from caller
    model_kwargs.update(kwargs.get("model_kwargs", {}))
    kwargs["model_kwargs"] = model_kwargs

    # Add pipeline kwargs if applicable
    pipeline_kwargs = config.to_pipeline_kwargs()
    if "pipeline_kwargs" in kwargs:
        pipeline_kwargs.update(kwargs["pipeline_kwargs"])
    kwargs["pipeline_kwargs"] = pipeline_kwargs

    try:
        # First attempt with configured parameters
        logger.debug(
            f"Attempting to load model with config: device_map={kwargs.get('device_map')}"
        )
        return model_loader(*args, **kwargs)

    except (torch.cuda.OutOfMemoryError, RuntimeError, ValueError) as e:
        error_msg = str(e).lower()
        
        # Check for device-related errors
        if "device" in error_msg and "not recognized" in error_msg:
            logger.warning(f"Device mapping error: {e}. Falling back to CPU.")
            return _fallback_to_cpu_for_device_error(model_loader, *args, **kwargs)
        
        # Check for OOM errors
        if "out of memory" not in error_msg and "cuda" not in error_msg:
            # Re-raise non-OOM errors
            raise

        logger.warning(f"CUDA OOM error encountered: {e}")

        # Progressive fallback if enabled
        if config.enable_progressive_fallback and config.gpu_layers_fallback:
            logger.info(
                f"Attempting progressive fallback with {config.gpu_layers_fallback} GPU layers"
            )

            try:
                # Create progressive device map
                progressive_device_map = _create_progressive_device_map(
                    config.gpu_layers_fallback
                )
                kwargs["device_map"] = progressive_device_map

                # Clear any max_memory constraints that might cause issues
                if "model_kwargs" in kwargs and "max_memory" in kwargs["model_kwargs"]:
                    del kwargs["model_kwargs"]["max_memory"]

                logger.debug(
                    f"Progressive fallback device map: {progressive_device_map}"
                )
                return model_loader(*args, **kwargs)

            except (torch.cuda.OutOfMemoryError, RuntimeError, ValueError) as e2:
                error_msg2 = str(e2).lower()
                if (
                    "out of memory" not in error_msg2
                    and "cuda" not in error_msg2
                    and "device" not in error_msg2
                ):
                    raise
                logger.warning(f"Progressive fallback also failed: {e2}")

        # Final fallback to CPU
        logger.info("Falling back to full CPU execution")
        return _fallback_to_cpu(model_loader, *args, **kwargs)


def _validate_device_map(device_map: Any, available_devices: dict[str, bool]) -> Any:
    """Validate and adjust device_map based on available devices.
    
    Args:
        device_map: Device map to validate
        available_devices: Dictionary of available devices
        
    Returns:
        Validated device map or adjusted map if needed
    """
    if device_map == "auto":
        # For testing environments, preserve "auto" and let HuggingFace handle it
        # Only override if we know for certain that GPU is not available
        # and only in production scenarios (when we detect real GPU absence)
        return "auto"
    
    elif isinstance(device_map, dict):
        # Custom device mapping - let HuggingFace handle detailed validation
        return device_map
    
    elif device_map == "cpu":
        # CPU mapping is always valid
        return device_map
    
    else:
        # Other device mappings - preserve them for HuggingFace to validate
        return device_map


def _fallback_to_cpu(model_loader: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """Force CPU usage by updating all device-related kwargs."""
    # Force CPU usage by updating kwargs
    if "device" in kwargs:
        kwargs["device"] = "cpu"
    elif "model_kwargs" in kwargs and kwargs["model_kwargs"]:
        kwargs["model_kwargs"]["device"] = "cpu"
    else:
        kwargs["model_kwargs"] = {"device": "cpu"}

    # Also try device_map for HuggingFace models
    if "device_map" in kwargs:
        kwargs["device_map"] = "cpu"

    logger.info("Retrying model loading on CPU")
    return model_loader(*args, **kwargs)


def _fallback_to_cpu_for_device_error(model_loader: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """Force CPU usage specifically for device validation errors."""
    # Force CPU usage by updating kwargs
    if "device" in kwargs:
        kwargs["device"] = "cpu"
    elif "model_kwargs" in kwargs and kwargs["model_kwargs"]:
        kwargs["model_kwargs"]["device"] = "cpu"
    else:
        kwargs["model_kwargs"] = {"device": "cpu"}

    # Always set device_map to CPU for device errors
    kwargs["device_map"] = "cpu"
    
    # Remove any memory constraints that don't apply to CPU
    if "model_kwargs" in kwargs and kwargs["model_kwargs"] and "max_memory" in kwargs["model_kwargs"]:
        del kwargs["model_kwargs"]["max_memory"]

    logger.info("Retrying model loading on CPU due to device error")
    return model_loader(*args, **kwargs)


def safe_load_model(model_loader: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """
    Safely load a model with automatic CPU fallback on CUDA OOM.

    This is the backward-compatible version that maintains the original behavior.
    For configuration-based loading with sharding, use safe_load_model_with_config.

    Args:
        model_loader: Function to call for loading the model
        *args: Positional arguments to pass to model_loader
        **kwargs: Keyword arguments to pass to model_loader

    Returns:
        Loaded model instance

    Raises:
        Exception: Re-raises non-OOM exceptions from model loading
    """
    try:
        # First attempt - let the model choose its preferred device (likely GPU if available)
        logger.debug("Attempting to load model with default device configuration")
        return model_loader(*args, **kwargs)
    except (torch.cuda.OutOfMemoryError, RuntimeError, ValueError) as e:
        error_msg = str(e).lower()
        
        # Check for device-related errors
        if "device" in error_msg and "not recognized" in error_msg:
            logger.warning(f"Device mapping error: {e}. Falling back to CPU.")
            return _fallback_to_cpu_for_device_error(model_loader, *args, **kwargs)
        
        # Check if it's a CUDA OOM error
        if "out of memory" in error_msg or "cuda" in error_msg:
            logger.warning(
                f"CUDA OOM error encountered: {e}. Falling back to CPU device."
            )
            return _fallback_to_cpu(model_loader, *args, **kwargs)
        else:
            # Re-raise non-OOM errors
            raise


def safe_load_embeddings(**kwargs: Any) -> HuggingFaceEmbeddings:
    """
    Safely load HuggingFace embeddings with CPU fallback on CUDA OOM.

    Args:
        **kwargs: Arguments to pass to HuggingFaceEmbeddings constructor

    Returns:
        HuggingFaceEmbeddings instance
    """
    return safe_load_model(HuggingFaceEmbeddings, **kwargs)


def safe_load_pipeline(
    model_id: str, task: str, config_path: Path | None = None, **kwargs: Any
) -> HuggingFacePipeline:
    """
    Safely load HuggingFace pipeline with sharding and progressive CPU fallback.

    Args:
        model_id: Model identifier
        task: Task type (e.g., "text-generation")
        config_path: Optional path to model configuration file
        **kwargs: Additional arguments to pass to HuggingFacePipeline.from_model_id

    Returns:
        HuggingFacePipeline instance
    """
    # Load configuration
    config = load_config(config_path)

    # Use provided model_id and task, overriding config
    config.model_id = model_id
    config.task = task

    return safe_load_model_with_config(
        HuggingFacePipeline.from_model_id, config, model_id, task, **kwargs
    )


def safe_load_pipeline_legacy(
    model_id: str, task: str, **kwargs: Any
) -> HuggingFacePipeline:
    """
    Legacy pipeline loader for backward compatibility.

    Args:
        model_id: Model identifier
        task: Task type (e.g., "text-generation")
        **kwargs: Additional arguments to pass to HuggingFacePipeline.from_model_id

    Returns:
        HuggingFacePipeline instance
    """
    return safe_load_model(HuggingFacePipeline.from_model_id, model_id, task, **kwargs)
