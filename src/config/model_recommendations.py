"""Model recommendation database for automatic selection."""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ModelInfo:
    """Information about a language model."""
    model_id: str
    size_category: str  # "small", "medium", "large" 
    parameter_count: str  # Human readable like "2B", "7B", "13B"
    min_ram_gb: float  # Minimum RAM required
    min_vram_gb: float  # Minimum VRAM for full GPU loading
    recommended_ram_gb: float  # Recommended RAM for good performance
    recommended_vram_gb: float  # Recommended VRAM for good performance
    quantization_support: List[str]  # Supported quantization: ["8bit", "4bit"]
    description: str
    license: str = "unknown"


# Curated model database focusing on popular, well-tested models
MODEL_DATABASE: List[ModelInfo] = [
    # Small models (1B - 8B parameters)
    ModelInfo(
        model_id="microsoft/phi-2",
        size_category="small",
        parameter_count="2.7B",
        min_ram_gb=4.0,
        min_vram_gb=3.0,
        recommended_ram_gb=8.0,
        recommended_vram_gb=4.0,
        quantization_support=["8bit", "4bit"],
        description="Efficient 2.7B parameter model with strong reasoning capabilities",
        license="MIT"
    ),
    ModelInfo(
        model_id="microsoft/DialoGPT-medium",
        size_category="small", 
        parameter_count="355M",
        min_ram_gb=2.0,
        min_vram_gb=0.5,  # Can run with very little VRAM
        recommended_ram_gb=4.0,
        recommended_vram_gb=2.0,
        quantization_support=["8bit", "4bit"],
        description="Conversational AI model optimized for dialogue",
        license="MIT"
    ),
    ModelInfo(
        model_id="google/flan-t5-large",
        size_category="small",
        parameter_count="770M",
        min_ram_gb=3.0,
        min_vram_gb=0.5,  # Can run with very little VRAM
        recommended_ram_gb=6.0,
        recommended_vram_gb=3.0,
        quantization_support=["8bit", "4bit"],
        description="Instruction-tuned T5 model for various tasks",
        license="Apache 2.0"
    ),
    ModelInfo(
        model_id="stabilityai/stablelm-2-1_6b",
        size_category="small",
        parameter_count="1.6B",
        min_ram_gb=3.0,
        min_vram_gb=2.0,
        recommended_ram_gb=6.0,
        recommended_vram_gb=3.0,
        quantization_support=["8bit", "4bit"],
        description="Efficient 1.6B parameter model with good performance",
        license="Stability AI"
    ),
    
    # Medium models (10B - 32B parameters)
    ModelInfo(
        model_id="microsoft/phi-3-medium",
        size_category="medium",
        parameter_count="14B",
        min_ram_gb=16.0,
        min_vram_gb=8.0,
        recommended_ram_gb=24.0,
        recommended_vram_gb=12.0,
        quantization_support=["8bit", "4bit"],
        description="Powerful 14B parameter model with excellent capabilities",
        license="MIT"
    ),
    ModelInfo(
        model_id="meta-llama/Llama-2-13b-chat-hf",
        size_category="medium",
        parameter_count="13B",
        min_ram_gb=16.0,
        min_vram_gb=8.0,
        recommended_ram_gb=24.0,
        recommended_vram_gb=12.0,
        quantization_support=["8bit", "4bit"],
        description="Popular 13B chat model with strong performance",
        license="Custom Llama"
    ),
    ModelInfo(
        model_id="mistralai/Mistral-7B-Instruct-v0.3",
        size_category="medium", 
        parameter_count="7B",
        min_ram_gb=8.0,
        min_vram_gb=4.0,
        recommended_ram_gb=16.0,
        recommended_vram_gb=8.0,
        quantization_support=["8bit", "4bit"],
        description="High-quality 7B instruction model",
        license="Apache 2.0"
    ),
    
    # Large models (33B+ parameters)  
    ModelInfo(
        model_id="meta-llama/Llama-2-70b-chat-hf",
        size_category="large",
        parameter_count="70B",
        min_ram_gb=64.0,
        min_vram_gb=24.0,
        recommended_ram_gb=128.0,
        recommended_vram_gb=48.0,
        quantization_support=["8bit", "4bit"],
        description="Large 70B model with exceptional capabilities",
        license="Custom Llama"
    ),
    ModelInfo(
        model_id="mistralai/Mixtral-8x7B-Instruct-v0.1",
        size_category="large",
        parameter_count="46.7B",
        min_ram_gb=48.0,
        min_vram_gb=20.0,
        recommended_ram_gb=96.0,
        recommended_vram_gb=40.0,
        quantization_support=["8bit", "4bit"],
        description="Mixture of experts model with strong performance",
        license="Apache 2.0"
    ),
]


def get_models_by_category(category: str) -> List[ModelInfo]:
    """Get all models in a specific size category.
    
    Args:
        category: Size category ("small", "medium", "large")
        
    Returns:
        List of ModelInfo objects for the category
    """
    return [model for model in MODEL_DATABASE if model.size_category == category]


def recommend_model(ram_gb: float, vram_gb: float, prefer_performance: bool = True) -> Optional[ModelInfo]:
    """Recommend the best model based on available resources.
    
    Args:
        ram_gb: Available system RAM in GB
        vram_gb: Available GPU VRAM in GB
        prefer_performance: If True, prefer larger models when resources allow
        
    Returns:
        Recommended ModelInfo or None if no suitable model found
    """
    suitable_models = []
    
    for model in MODEL_DATABASE:
        # Check if we meet minimum requirements
        if ram_gb >= model.min_ram_gb:
            # For GPU models, either have enough VRAM or can run with quantization/CPU
            if vram_gb >= model.min_vram_gb or vram_gb == 0.0 or model.quantization_support:
                suitable_models.append(model)
    
    if not suitable_models:
        logger.warning(f"No suitable models found for {ram_gb:.1f}GB RAM, {vram_gb:.1f}GB VRAM")
        return None
    
    # Sort by category preference and then by parameter count
    category_order = {"large": 3, "medium": 2, "small": 1}
    
    def model_score(model: ModelInfo) -> tuple:
        # Extract numeric parameter count for sorting
        param_str = model.parameter_count.replace("B", "").replace("M", "")
        try:
            if "M" in model.parameter_count:
                param_count = float(param_str) / 1000  # Convert M to B
            else:
                param_count = float(param_str)
        except ValueError:
            param_count = 0
        
        if prefer_performance:
            return (category_order[model.size_category], param_count)
        else:
            return (-category_order[model.size_category], -param_count)
    
    suitable_models.sort(key=model_score, reverse=prefer_performance)
    
    recommended = suitable_models[0]
    logger.info(f"Recommended model: {recommended.model_id} ({recommended.parameter_count})")
    return recommended


def get_model_info(model_id: str) -> Optional[ModelInfo]:
    """Get information about a specific model.
    
    Args:
        model_id: HuggingFace model identifier
        
    Returns:
        ModelInfo object or None if not found
    """
    for model in MODEL_DATABASE:
        if model.model_id == model_id:
            return model
    return None