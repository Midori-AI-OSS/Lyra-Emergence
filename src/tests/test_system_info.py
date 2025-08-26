"""Tests for system resource detection."""

import pytest
from unittest.mock import patch, mock_open

from src.utils.system_info import get_available_memory, get_memory_tier, detect_optimal_memory_config


class TestSystemInfo:
    """Test system resource detection."""
    
    def test_get_memory_tier_small(self):
        """Test small memory tier classification."""
        assert get_memory_tier(4.0, 0.0) == "small"
        assert get_memory_tier(6.0, 1.0) == "small"
    
    def test_get_memory_tier_medium(self):
        """Test medium memory tier classification."""
        assert get_memory_tier(8.0, 4.0) == "medium"
        assert get_memory_tier(16.0, 0.0) == "medium"
    
    def test_get_memory_tier_large(self):
        """Test large memory tier classification."""
        assert get_memory_tier(16.0, 8.0) == "large"
        assert get_memory_tier(32.0, 0.0) == "large"
    
    def test_detect_optimal_memory_config_with_gpu(self):
        """Test memory configuration with GPU."""
        config = detect_optimal_memory_config(16.0, 8.0)
        assert "0" in config  # GPU memory allocation
        assert "cpu" in config  # CPU memory allocation
        assert config["0"] == "7GB"  # 8GB - 1GB reserve
        assert config["cpu"] == "12GB"  # 16GB - 4GB reserve
    
    def test_detect_optimal_memory_config_cpu_only(self):
        """Test memory configuration without meaningful GPU."""
        config = detect_optimal_memory_config(16.0, 0.5)
        assert "0" not in config  # No GPU allocation
        assert "cpu" in config
        assert config["cpu"] == "12GB"
    
    @patch("builtins.open", mock_open(read_data="MemAvailable:     8388608 kB\n"))
    @patch("subprocess.run")
    def test_get_available_memory_with_gpu(self, mock_subprocess):
        """Test memory detection with GPU."""
        # Mock nvidia-smi output
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "4096\n"  # 4GB VRAM
        
        ram_gb, vram_gb = get_available_memory()
        assert ram_gb == 8.0  # 8388608 kB = 8GB
        assert vram_gb == 4.0  # 4096 MB = 4GB
    
    @patch("builtins.open", mock_open(read_data="MemAvailable:     16777216 kB\n"))
    @patch("subprocess.run")
    def test_get_available_memory_no_gpu(self, mock_subprocess):
        """Test memory detection without GPU."""
        # Mock nvidia-smi failure
        mock_subprocess.return_value.returncode = 1
        
        ram_gb, vram_gb = get_available_memory()
        assert ram_gb == 16.0  # 16777216 kB = 16GB
        assert vram_gb == 0.0  # No GPU