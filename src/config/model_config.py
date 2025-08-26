"""Model configuration management for HuggingFace models."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict

from src.utils.system_info import get_available_memory, get_memory_tier, detect_optimal_memory_config
from src.config.model_recommendations import recommend_model, get_model_info

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Configuration class for HuggingFace model loading parameters.
    
    This class defines the configurable parameters for model loading,
    including device mapping, memory management, and quantization options.
    """
    # Model identification
    model_id: str = "microsoft/phi-2"
    task: str = "text-generation"
    
    # Device and memory configuration
    device_map: Optional[str] = None  # "auto", "cpu", or custom mapping
    max_memory: Optional[Dict[str, str]] = None  # e.g., {"0": "8GB", "cpu": "16GB"}
    low_cpu_mem_usage: bool = True
    
    # Progressive fallback configuration
    gpu_layers_fallback: Optional[int] = None  # Number of layers to keep on GPU during fallback
    enable_progressive_fallback: bool = True
    
    # Quantization options
    load_in_8bit: bool = False
    load_in_4bit: bool = False
    
    # Pipeline-specific parameters
    pipeline_kwargs: Optional[Dict[str, Any]] = None
    
    def to_model_kwargs(self) -> Dict[str, Any]:
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
    
    def to_pipeline_kwargs(self) -> Dict[str, Any]:
        """Get pipeline-specific kwargs.
        
        Returns:
            Dictionary of pipeline kwargs
        """
        return self.pipeline_kwargs or {}


def load_config(config_path: Optional[Path] = None, auto_select: bool = False) -> ModelConfig:
    """Load model configuration from file or return default.
    
    Args:
        config_path: Path to configuration file. If None, looks for default locations.
        auto_select: If True, automatically select optimal model based on system resources.
        
    Returns:
        ModelConfig instance with loaded or default configuration
    """
    if config_path is None:
        # Look for default config file locations
        possible_paths = [
            Path("config/model_config.json"),
            Path("data/model_config.json"),
            Path("model_config.json"),
        ]
        
        for path in possible_paths:
            if path.exists():
                config_path = path
                break
    
    base_config = ModelConfig()
    
    # Load from file if available
    if config_path and config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            logger.info(f"Loaded model configuration from {config_path}")
            base_config = ModelConfig(**config_data)
            
        except Exception as e:
            logger.warning(f"Failed to load config from {config_path}: {e}. Using defaults.")
    
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
            if vram_gb < recommended.recommended_vram_gb and "8bit" in recommended.quantization_support:
                base_config.load_in_8bit = True
                logger.info("Enabled 8-bit quantization due to limited VRAM")
            elif vram_gb < recommended.min_vram_gb and "4bit" in recommended.quantization_support:
                base_config.load_in_4bit = True
                logger.info("Enabled 4-bit quantization due to very limited VRAM")
            
            # Set device map based on available resources
            if vram_gb > 1.0:
                base_config.device_map = "auto"
            else:
                base_config.device_map = "cpu"
                logger.info("Using CPU-only mode due to insufficient VRAM")
            
            logger.info(f"Auto-selected model: {recommended.model_id} ({recommended.parameter_count})")
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
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(asdict(config), f, indent=2)
    
    logger.info(f"Saved model configuration to {config_path}")


# Default configuration instance for convenience
DEFAULT_CONFIG = ModelConfig()