"""Tests for VRAM OOM fallback functionality."""

import pytest
import torch
from unittest.mock import Mock
from unittest.mock import patch

from src.utils.device_fallback import safe_load_model
from src.utils.device_fallback import safe_load_embeddings
from src.utils.device_fallback import safe_load_pipeline


def test_safe_load_model_success() -> None:
    """Test that safe_load_model works normally when no OOM occurs."""
    mock_loader = Mock(return_value="model")
    result = safe_load_model(mock_loader, "arg1", kwarg1="value1")
    
    assert result == "model"
    mock_loader.assert_called_once_with("arg1", kwarg1="value1")


def test_safe_load_model_cuda_oom_fallback() -> None:
    """Test that safe_load_model falls back to CPU on CUDA OOM."""
    mock_loader = Mock()
    # First call raises CUDA OOM, second call succeeds
    mock_loader.side_effect = [
        torch.cuda.OutOfMemoryError("CUDA out of memory"),
        "model_on_cpu"
    ]
    
    result = safe_load_model(mock_loader, device="cuda")
    
    assert result == "model_on_cpu"
    assert mock_loader.call_count == 2
    # First call with original args
    mock_loader.assert_any_call(device="cuda")
    # Second call with CPU device
    mock_loader.assert_any_call(device="cpu")


def test_safe_load_model_runtime_error_oom_fallback() -> None:
    """Test that safe_load_model falls back on RuntimeError with OOM message."""
    mock_loader = Mock()
    mock_loader.side_effect = [
        RuntimeError("CUDA out of memory. Tried to allocate..."),
        "model_on_cpu"
    ]
    
    result = safe_load_model(mock_loader, model_kwargs={"device": "cuda"})
    
    assert result == "model_on_cpu"
    assert mock_loader.call_count == 2
    # Second call should have CPU device in model_kwargs
    mock_loader.assert_any_call(model_kwargs={"device": "cpu"})


def test_safe_load_model_non_oom_error_reraises() -> None:
    """Test that non-OOM errors are re-raised."""
    mock_loader = Mock()
    mock_loader.side_effect = ValueError("Some other error")
    
    with pytest.raises(ValueError, match="Some other error"):
        safe_load_model(mock_loader)


def test_safe_load_model_device_map_fallback() -> None:
    """Test that device_map is also set to CPU on fallback."""
    mock_loader = Mock()
    mock_loader.side_effect = [
        torch.cuda.OutOfMemoryError("CUDA out of memory"),
        "model_on_cpu"
    ]
    
    result = safe_load_model(mock_loader, device_map="auto")
    
    assert result == "model_on_cpu"
    # Second call should have CPU device_map
    mock_loader.assert_any_call(device_map="cpu", model_kwargs={"device": "cpu"})


@patch('src.utils.device_fallback.HuggingFaceEmbeddings')
def test_safe_load_embeddings(mock_hf_embeddings) -> None:
    """Test safe_load_embeddings wrapper."""
    mock_hf_embeddings.return_value = "embeddings"
    
    result = safe_load_embeddings(model_name="test-model")
    
    assert result == "embeddings"
    mock_hf_embeddings.assert_called_once_with(model_name="test-model")


@patch('src.utils.device_fallback.HuggingFacePipeline')
def test_safe_load_pipeline(mock_hf_pipeline) -> None:
    """Test safe_load_pipeline wrapper."""
    mock_hf_pipeline.from_model_id.return_value = "pipeline"
    
    result = safe_load_pipeline("model-id", "text-generation", device="cuda")
    
    assert result == "pipeline"
    mock_hf_pipeline.from_model_id.assert_called_once_with(
        "model-id", "text-generation", device="cuda"
    )