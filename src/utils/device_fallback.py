"""Device fallback utilities for handling VRAM OOM errors."""

import logging
from typing import Any
from typing import Callable
from typing import TypeVar

import torch
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFacePipeline

logger = logging.getLogger(__name__)

T = TypeVar("T")


def safe_load_model(
    model_loader: Callable[..., T], 
    *args: Any, 
    **kwargs: Any
) -> T:
    """
    Safely load a model with automatic CPU fallback on CUDA OOM.
    
    Tries to load the model on GPU first, then falls back to CPU if VRAM runs out.
    
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
    except (torch.cuda.OutOfMemoryError, RuntimeError) as e:
        # Check if it's a CUDA OOM error
        if "out of memory" in str(e).lower() or "cuda" in str(e).lower():
            logger.warning(
                f"CUDA OOM error encountered: {e}. Falling back to CPU device."
            )
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
    model_id: str,
    task: str, 
    **kwargs: Any
) -> HuggingFacePipeline:
    """
    Safely load HuggingFace pipeline with CPU fallback on CUDA OOM.
    
    Args:
        model_id: Model identifier
        task: Task type (e.g., "text-generation")
        **kwargs: Additional arguments to pass to HuggingFacePipeline.from_model_id
        
    Returns:
        HuggingFacePipeline instance
    """
    return safe_load_model(
        HuggingFacePipeline.from_model_id,
        model_id,
        task,
        **kwargs
    )