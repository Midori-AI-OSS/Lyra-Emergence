#!/usr/bin/env python3
"""Test script to reproduce the device_map conflict issue."""

from src.config.model_config import ModelConfig
from src.utils.device_fallback import safe_load_model_with_config
from langchain_huggingface import HuggingFacePipeline
from unittest.mock import Mock, patch

def test_device_map_conflict():
    """Test to reproduce the device_map conflict issue."""
    
    # Create a config with device_map set
    config = ModelConfig(device_map="auto")
    
    # Mock the HuggingFacePipeline.from_model_id to simulate the error
    def mock_from_model_id(*args, **kwargs):
        print(f"Called with args: {args}")
        print(f"Called with kwargs: {kwargs}")
        
        # Check if device_map is in both places
        device_map_in_kwargs = "device_map" in kwargs
        device_map_in_model_kwargs = "model_kwargs" in kwargs and "device_map" in kwargs.get("model_kwargs", {})
        
        if device_map_in_kwargs and device_map_in_model_kwargs:
            raise ValueError("`device_map` is already specified in `model_kwargs`.")
        
        return Mock()
    
    # Test the current implementation
    try:
        with patch.object(HuggingFacePipeline, 'from_model_id', side_effect=mock_from_model_id):
            result = safe_load_model_with_config(
                HuggingFacePipeline.from_model_id,
                config,
                "microsoft/phi-2",
                "text-generation"
            )
            print("Success - no conflict detected")
    except ValueError as e:
        print(f"Error reproduced: {e}")
        return True
    
    return False

if __name__ == "__main__":
    success = test_device_map_conflict()
    if success:
        print("Successfully reproduced the issue!")
    else:
        print("Could not reproduce the issue")