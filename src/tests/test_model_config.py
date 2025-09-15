"""Tests for model configuration and sharding functionality."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

import pytest

from src.config.model_config import ModelConfig, load_config, save_config
from src.utils.device_fallback import (
    _create_progressive_device_map,
    safe_load_model_with_config,
    safe_load_pipeline,
)


class TestModelConfig:
    """Test cases for ModelConfig class."""

    def test_default_config(self) -> None:
        """Test that default configuration is created correctly."""
        config = ModelConfig()
        assert config.model_id == "Qwen/Qwen2.5-7B-Instruct"
        assert config.task == "text-generation"
        assert config.device_map is None
        assert config.enable_progressive_fallback is True

    def test_to_model_kwargs(self) -> None:
        """Test conversion to model kwargs."""
        config = ModelConfig(
            device_map="auto",
            max_memory={"0": "8GB"},
            load_in_8bit=True,
            low_cpu_mem_usage=False,
        )

        kwargs = config.to_model_kwargs()
        assert kwargs["device_map"] == "auto"
        assert kwargs["max_memory"] == {"0": "8GB"}
        assert kwargs["load_in_8bit"] is True
        assert "low_cpu_mem_usage" not in kwargs  # False should not be included

    def test_to_pipeline_kwargs(self) -> None:
        """Test conversion to pipeline kwargs."""
        config = ModelConfig(
            pipeline_kwargs={"max_new_tokens": 100, "temperature": 0.8}
        )

        kwargs = config.to_pipeline_kwargs()
        assert kwargs["max_new_tokens"] == 100
        assert kwargs["temperature"] == 0.8

    def test_to_pipeline_kwargs_none(self) -> None:
        """Test pipeline kwargs when None."""
        config = ModelConfig()
        kwargs = config.to_pipeline_kwargs()
        assert kwargs == {}


class TestConfigLoading:
    """Test cases for configuration loading and saving."""

    def test_load_config_default(self) -> None:
        """Test loading default config when no file exists."""
        with TemporaryDirectory() as temp_dir:
            allowed_dir = Path(temp_dir).resolve()
            with patch(
                "src.config.model_config.APPROVED_CONFIG_DIRS",
                [allowed_dir],
            ):
                config = load_config()
                assert config.model_id == "Qwen/Qwen2.5-7B-Instruct"

    def test_load_config_from_file(self) -> None:
        """Test loading config from JSON file."""
        with TemporaryDirectory() as temp_dir:
            allowed_dir = Path(temp_dir).resolve()
            config_path = allowed_dir / "test_config.json"
            config_data = {
                "model_id": "test/model",
                "device_map": "auto",
                "gpu_layers_fallback": 20,
            }

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f)

            with patch(
                "src.config.model_config.APPROVED_CONFIG_DIRS",
                [allowed_dir],
            ):
                config = load_config(config_path)
            assert config.model_id == "test/model"
            assert config.device_map == "auto"
            assert config.gpu_layers_fallback == 20

    def test_save_config(self) -> None:
        """Test saving config to file."""
        with TemporaryDirectory() as temp_dir:
            allowed_dir = Path(temp_dir).resolve()
            config_path = allowed_dir / "test_config.json"
            config = ModelConfig(
                model_id="test/model", device_map="auto", gpu_layers_fallback=16
            )

            with patch(
                "src.config.model_config.APPROVED_CONFIG_DIRS",
                [allowed_dir],
            ):
                save_config(config, config_path)

            # Verify file was created and contents are correct
            assert config_path.exists()
            with open(config_path, encoding="utf-8") as f:
                saved_data = json.load(f)

            assert saved_data["model_id"] == "test/model"
            assert saved_data["device_map"] == "auto"
            assert saved_data["gpu_layers_fallback"] == 16

    def test_load_config_rejects_parent_escape(self) -> None:
        """Paths that escape approved directories should raise an error."""

        with pytest.raises(ValueError):
            load_config(Path("../secret.json"))

    def test_save_config_rejects_parent_escape(self) -> None:
        """Saving to escaped paths should raise an error before writing."""

        with pytest.raises(ValueError):
            save_config(ModelConfig(), Path("../secret.json"))


class TestProgressiveDeviceMap:
    """Test cases for progressive device mapping."""

    @patch("src.utils.device_fallback._detect_available_devices")
    def test_create_progressive_device_map_basic(self, mock_detect_devices) -> None:
        """Test basic progressive device map creation."""
        # Mock GPU being available for testing
        mock_detect_devices.return_value = {"cuda": True, "mps": False, "cpu": True}
        
        device_map = _create_progressive_device_map(gpu_layers=4, total_layers=8)

        # Check embedding layer on GPU
        assert device_map["model.embed_tokens"] == 0

        # Check first 4 layers on GPU
        for i in range(4):
            assert device_map[f"model.layers.{i}"] == 0

        # Check remaining layers on CPU
        for i in range(4, 8):
            assert device_map[f"model.layers.{i}"] == "cpu"

        # Output layers should be on CPU (since not all layers on GPU)
        assert device_map["model.norm"] == "cpu"
        assert device_map["lm_head"] == "cpu"

    @patch("src.utils.device_fallback._detect_available_devices")
    def test_create_progressive_device_map_all_gpu(self, mock_detect_devices) -> None:
        """Test device map when all layers fit on GPU."""
        # Mock GPU being available for testing
        mock_detect_devices.return_value = {"cuda": True, "mps": False, "cpu": True}
        
        device_map = _create_progressive_device_map(gpu_layers=8, total_layers=8)

        # All layers should be on GPU
        for i in range(8):
            assert device_map[f"model.layers.{i}"] == 0

        # Output layers should also be on GPU
        assert device_map["model.norm"] == 0
        assert device_map["lm_head"] == 0

    @patch("src.utils.device_fallback._detect_available_devices")
    def test_create_progressive_device_map_default_layers(self, mock_detect_devices) -> None:
        """Test device map with default layer count."""
        # Mock GPU being available for testing
        mock_detect_devices.return_value = {"cuda": True, "mps": False, "cpu": True}
        
        device_map = _create_progressive_device_map(gpu_layers=16)

        # Should default to 32 total layers
        assert "model.layers.15" in device_map
        assert device_map["model.layers.15"] == 0
        assert "model.layers.16" in device_map
        assert device_map["model.layers.16"] == "cpu"


class TestSafeLoadModelWithConfig:
    """Test cases for safe_load_model_with_config function."""

    @patch("src.utils.device_fallback._detect_available_devices")
    @patch("src.utils.device_fallback.load_config")
    def test_safe_load_model_with_config_success(self, mock_load_config, mock_detect_devices) -> None:
        """Test successful model loading with config."""
        # Mock GPU being available for testing
        mock_detect_devices.return_value = {"cuda": True, "mps": False, "cpu": True}
        
        mock_config = ModelConfig(device_map="auto")
        mock_load_config.return_value = mock_config

        mock_loader = Mock(return_value="model")
        result = safe_load_model_with_config(mock_loader, mock_config)

        assert result == "model"
        # Check that device_map was set from config
        mock_loader.assert_called_once()
        args, kwargs = mock_loader.call_args
        assert kwargs.get("device_map") == "auto"

    @patch("src.utils.device_fallback.load_config")
    @patch("src.utils.device_fallback._create_progressive_device_map")
    def test_progressive_fallback(self, mock_create_map, mock_load_config) -> None:
        """Test progressive fallback on OOM."""
        mock_config = ModelConfig(
            enable_progressive_fallback=True, gpu_layers_fallback=16
        )
        mock_load_config.return_value = mock_config
        mock_create_map.return_value = {"test": "map"}

        mock_loader = Mock()
        mock_loader.side_effect = [
            RuntimeError("CUDA out of memory"),  # First attempt fails
            "model_partial_gpu",  # Progressive fallback succeeds
        ]

        result = safe_load_model_with_config(mock_loader, mock_config)

        assert result == "model_partial_gpu"
        assert mock_loader.call_count == 2
        mock_create_map.assert_called_once_with(16)


class TestSafeLoadPipeline:
    """Test cases for enhanced safe_load_pipeline function."""

    @patch("src.utils.device_fallback.safe_load_model_with_config")
    @patch("src.utils.device_fallback.load_config")
    def test_safe_load_pipeline_with_config(
        self, mock_load_config, mock_safe_load
    ) -> None:
        """Test pipeline loading with configuration."""
        mock_config = ModelConfig()
        mock_load_config.return_value = mock_config
        mock_safe_load.return_value = "pipeline"

        result = safe_load_pipeline("test/model", "text-generation")

        assert result == "pipeline"
        mock_load_config.assert_called_once_with(None)
        mock_safe_load.assert_called_once()

        # Verify config was updated with provided model_id and task
        assert mock_config.model_id == "test/model"
        assert mock_config.task == "text-generation"

    def test_device_map_conflict_resolution(self) -> None:
        """Test that device_map conflicts are resolved properly."""
        from unittest.mock import Mock
        
        def mock_loader(*args, **kwargs):
            # Verify device_map is not in both places
            device_map_in_kwargs = "device_map" in kwargs
            device_map_in_model_kwargs = (
                "model_kwargs" in kwargs 
                and "device_map" in kwargs.get("model_kwargs", {})
            )
            
            if device_map_in_kwargs and device_map_in_model_kwargs:
                raise ValueError("`device_map` is already specified in `model_kwargs`.")
            
            return "success"
        
        config = ModelConfig(device_map="auto")
        
        # This should not raise a ValueError
        result = safe_load_model_with_config(mock_loader, config, "test-model", "task")
        assert result == "success"

    @patch("src.utils.device_fallback._detect_available_devices")
    def test_device_map_priority_logic(self, mock_detect_devices) -> None:
        """Test the priority logic for device_map handling."""
        # Mock GPU being available for testing
        mock_detect_devices.return_value = {"cuda": True, "mps": False, "cpu": True}
        
        from unittest.mock import Mock
        
        captured_kwargs = {}
        
        def mock_loader(*args, **kwargs):
            nonlocal captured_kwargs
            captured_kwargs = kwargs
            return "success"
        
        # Test 1: Explicit device_map="cpu" should be removed to avoid accelerate requirement
        config = ModelConfig(device_map="auto", load_in_8bit=True)
        result = safe_load_model_with_config(
            mock_loader, config, "test-model", "task", device_map="cpu"
        )
        assert result == "success"
        assert "device_map" not in captured_kwargs  # CPU device_map should be removed
        assert "device_map" not in captured_kwargs["model_kwargs"]  # Should not be in model_kwargs
        assert captured_kwargs["model_kwargs"]["load_in_8bit"] is True  # Other config items still present
        
        # Test 2: Config device_map="auto" should be preserved when GPU is available
        captured_kwargs = {}
        result = safe_load_model_with_config(
            mock_loader, config, "test-model", "task"
        )
        assert result == "success"
        assert captured_kwargs["device_map"] == "auto"  # From config, GPU available
        assert "device_map" not in captured_kwargs["model_kwargs"]  # Should not be in model_kwargs
        assert captured_kwargs["model_kwargs"]["load_in_8bit"] is True  # Other config items still present
        
        # Test 3: No device_map anywhere
        config_no_device = ModelConfig(load_in_8bit=True)  # No device_map set
        captured_kwargs = {}
        result = safe_load_model_with_config(
            mock_loader, config_no_device, "test-model", "task"
        )
        assert result == "success"
        assert "device_map" not in captured_kwargs  # No device_map in top level
        assert "device_map" not in captured_kwargs["model_kwargs"]  # No device_map in model_kwargs either

    @patch("src.utils.device_fallback._detect_available_devices")
    def test_device_map_removed_when_no_gpu(self, mock_detect_devices) -> None:
        """Test that device_map='auto' is removed when no GPU is available."""
        # Mock no GPU being available
        mock_detect_devices.return_value = {"cuda": False, "mps": False, "cpu": True}
        
        from unittest.mock import Mock
        
        captured_kwargs = {}
        
        def mock_loader(*args, **kwargs):
            nonlocal captured_kwargs
            captured_kwargs = kwargs
            return "success"
        
        # device_map="auto" should be removed when no GPU available
        config = ModelConfig(device_map="auto", load_in_8bit=True)
        result = safe_load_model_with_config(
            mock_loader, config, "test-model", "task"
        )
        assert result == "success"
        assert "device_map" not in captured_kwargs  # Should be removed when no GPU
        assert captured_kwargs["model_kwargs"]["load_in_8bit"] is True  # Other config items still present
        assert captured_kwargs["model_kwargs"]["load_in_8bit"] is True  # Other config items still present
