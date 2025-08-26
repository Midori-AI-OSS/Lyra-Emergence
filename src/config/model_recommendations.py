"""Model recommendation database for automatic selection."""

import logging
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
    quantization_support: list[str]  # Supported quantization: ["8bit", "4bit"]
    description: str
    license: str = "unknown"


# Curated model database focusing on the latest, highest-performing models
MODEL_DATABASE: list[ModelInfo] = [
    # Small models (1B - 8B parameters) - 2024/2025 latest models
    ModelInfo(
        model_id="Qwen/Qwen2.5-7B-Instruct",
        size_category="small",
        parameter_count="7B",
        min_ram_gb=6.0,
        min_vram_gb=4.0,
        recommended_ram_gb=12.0,
        recommended_vram_gb=8.0,
        quantization_support=["8bit", "4bit"],
        description="State-of-the-art 7B model from Alibaba with excellent reasoning capabilities (2024)",
        license="Apache 2.0",
    ),
    ModelInfo(
        model_id="meta-llama/Llama-3.2-3B-Instruct",
        size_category="small",
        parameter_count="3B",
        min_ram_gb=4.0,
        min_vram_gb=2.0,
        recommended_ram_gb=8.0,
        recommended_vram_gb=4.0,
        quantization_support=["8bit", "4bit"],
        description="Meta's latest small instruction-tuned model with strong performance (2024)",
        license="Llama 3.2",
    ),
    ModelInfo(
        model_id="microsoft/Phi-3.5-mini-instruct",
        size_category="small",
        parameter_count="3.8B",
        min_ram_gb=4.0,
        min_vram_gb=2.5,
        recommended_ram_gb=8.0,
        recommended_vram_gb=5.0,
        quantization_support=["8bit", "4bit"],
        description="Microsoft's latest efficient small model with excellent reasoning (2024)",
        license="MIT",
    ),
    ModelInfo(
        model_id="google/gemma-2-9b-it",
        size_category="small",
        parameter_count="9B",
        min_ram_gb=8.0,
        min_vram_gb=5.0,
        recommended_ram_gb=16.0,
        recommended_vram_gb=10.0,
        quantization_support=["8bit", "4bit"],
        description="Google's latest Gemma 2 instruction-tuned model with strong capabilities (2024)",
        license="Gemma",
    ),
    ModelInfo(
        model_id="HuggingFaceTB/SmolLM-1.7B-Instruct",
        size_category="small",
        parameter_count="1.7B",
        min_ram_gb=2.0,
        min_vram_gb=1.0,
        recommended_ram_gb=4.0,
        recommended_vram_gb=2.0,
        quantization_support=["8bit", "4bit"],
        description="HuggingFace's efficient small model optimized for resource-constrained environments (2024)",
        license="Apache 2.0",
    ),
    # Medium models (10B - 32B parameters) - 2024/2025 latest models
    ModelInfo(
        model_id="Qwen/Qwen2.5-14B-Instruct",
        size_category="medium",
        parameter_count="14B",
        min_ram_gb=16.0,
        min_vram_gb=8.0,
        recommended_ram_gb=28.0,
        recommended_vram_gb=16.0,
        quantization_support=["8bit", "4bit"],
        description="Top-tier 14B model with exceptional reasoning and coding capabilities (2024)",
        license="Apache 2.0",
    ),
    ModelInfo(
        model_id="meta-llama/Meta-Llama-3.1-8B-Instruct",
        size_category="medium",
        parameter_count="8B",
        min_ram_gb=8.0,
        min_vram_gb=4.0,
        recommended_ram_gb=16.0,
        recommended_vram_gb=8.0,
        quantization_support=["8bit", "4bit"],
        description="Meta's latest 8B model with 128k context and strong performance (2024)",
        license="Llama 3.1",
    ),
    ModelInfo(
        model_id="mistralai/Mistral-Nemo-Instruct-2407",
        size_category="medium",
        parameter_count="12B",
        min_ram_gb=12.0,
        min_vram_gb=6.0,
        recommended_ram_gb=24.0,
        recommended_vram_gb=12.0,
        quantization_support=["8bit", "4bit"],
        description="Mistral's powerful 12B model with 128k context window (2024)",
        license="Apache 2.0",
    ),
    ModelInfo(
        model_id="google/gemma-2-27b-it",
        size_category="medium",
        parameter_count="27B",
        min_ram_gb=32.0,
        min_vram_gb=16.0,
        recommended_ram_gb=48.0,
        recommended_vram_gb=24.0,
        quantization_support=["8bit", "4bit"],
        description="Google's large Gemma 2 model with excellent reasoning capabilities (2024)",
        license="Gemma",
    ),
    ModelInfo(
        model_id="Qwen/Qwen2.5-32B-Instruct",
        size_category="medium",
        parameter_count="32B",
        min_ram_gb=32.0,
        min_vram_gb=16.0,
        recommended_ram_gb=64.0,
        recommended_vram_gb=32.0,
        quantization_support=["8bit", "4bit"],
        description="High-performance 32B model with state-of-the-art capabilities (2024)",
        license="Apache 2.0",
    ),
    # Large models (33B+ parameters) - 2024/2025 latest models
    ModelInfo(
        model_id="meta-llama/Meta-Llama-3.1-70B-Instruct",
        size_category="large",
        parameter_count="70B",
        min_ram_gb=64.0,
        min_vram_gb=32.0,
        recommended_ram_gb=128.0,
        recommended_vram_gb=64.0,
        quantization_support=["8bit", "4bit"],
        description="Meta's flagship 70B model with 128k context and exceptional capabilities (2024)",
        license="Llama 3.1",
    ),
    ModelInfo(
        model_id="Qwen/Qwen2.5-72B-Instruct",
        size_category="large",
        parameter_count="72B",
        min_ram_gb=64.0,
        min_vram_gb=32.0,
        recommended_ram_gb=144.0,
        recommended_vram_gb=72.0,
        quantization_support=["8bit", "4bit"],
        description="Alibaba's top-tier 72B model with state-of-the-art performance across domains (2024)",
        license="Apache 2.0",
    ),
    ModelInfo(
        model_id="meta-llama/Llama-3.3-70B-Instruct",
        size_category="large",
        parameter_count="70B",
        min_ram_gb=64.0,
        min_vram_gb=32.0,
        recommended_ram_gb=128.0,
        recommended_vram_gb=64.0,
        quantization_support=["8bit", "4bit"],
        description="Meta's latest 70B model with improved capabilities and efficiency (2024)",
        license="Llama 3.3",
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
        description="Mixture of experts model with efficient computation and strong performance",
        license="Apache 2.0",
    ),
    ModelInfo(
        model_id="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
        size_category="large",
        parameter_count="32B",
        min_ram_gb=32.0,
        min_vram_gb=16.0,
        recommended_ram_gb=64.0,
        recommended_vram_gb=32.0,
        quantization_support=["8bit", "4bit"],
        description="DeepSeek's reasoning-optimized model with advanced problem-solving capabilities (2025)",
        license="DeepSeek",
    ),
]


def get_models_by_category(category: str) -> list[ModelInfo]:
    """Get all models in a specific size category.

    Args:
        category: Size category ("small", "medium", "large")

    Returns:
        List of ModelInfo objects for the category
    """
    return [model for model in MODEL_DATABASE if model.size_category == category]


def recommend_model(
    ram_gb: float, vram_gb: float, prefer_performance: bool = True
) -> ModelInfo | None:
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
            if (
                vram_gb >= model.min_vram_gb
                or vram_gb == 0.0
                or model.quantization_support
            ):
                suitable_models.append(model)

    if not suitable_models:
        logger.warning(
            f"No suitable models found for {ram_gb:.1f}GB RAM, {vram_gb:.1f}GB VRAM"
        )
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
    logger.info(
        f"Recommended model: {recommended.model_id} ({recommended.parameter_count})"
    )
    return recommended


def get_model_info(model_id: str) -> ModelInfo | None:
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
