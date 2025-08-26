"""System resource detection utilities."""

import logging
import subprocess
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


def get_available_memory() -> Tuple[float, float]:
    """Get available system RAM and GPU VRAM in GB.
    
    Returns:
        Tuple of (ram_gb, vram_gb). VRAM will be 0 if no GPU detected.
    """
    # Get system RAM
    ram_gb = 0.0
    try:
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if line.startswith('MemAvailable:'):
                    # MemAvailable is in kB
                    ram_kb = int(line.split()[1])
                    ram_gb = ram_kb / (1024 * 1024)  # Convert to GB
                    break
        logger.info(f"Detected {ram_gb:.1f}GB available system RAM")
    except Exception as e:
        logger.warning(f"Could not detect system RAM: {e}")
        # Fallback estimate
        ram_gb = 8.0
    
    # Get GPU VRAM
    vram_gb = 0.0
    try:
        # Try nvidia-smi first
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # Get the first GPU's free memory in MB
            vram_mb = int(result.stdout.strip().split('\n')[0])
            vram_gb = vram_mb / 1024  # Convert to GB
            logger.info(f"Detected {vram_gb:.1f}GB available GPU VRAM")
        else:
            logger.info("No NVIDIA GPU detected")
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError, ValueError) as e:
        logger.info(f"Could not detect GPU VRAM: {e}")
    
    return ram_gb, vram_gb


def get_memory_tier(ram_gb: float, vram_gb: float) -> str:
    """Determine memory tier based on available RAM and VRAM.
    
    Args:
        ram_gb: Available system RAM in GB
        vram_gb: Available GPU VRAM in GB
        
    Returns:
        Memory tier: "small", "medium", or "large"
    """
    # Consider both RAM and VRAM for tier determination
    total_memory = ram_gb + (vram_gb * 2)  # Weight GPU memory more heavily
    
    if total_memory >= 32:  # 16GB+ RAM + 8GB+ VRAM, or 32GB+ RAM
        return "large"
    elif total_memory >= 16:  # 8GB+ RAM + 4GB+ VRAM, or 16GB+ RAM
        return "medium" 
    else:
        return "small"


def detect_optimal_memory_config(ram_gb: float, vram_gb: float) -> Dict[str, str]:
    """Create optimal memory configuration based on available resources.
    
    Args:
        ram_gb: Available system RAM in GB
        vram_gb: Available GPU VRAM in GB
        
    Returns:
        Dictionary with max_memory configuration
    """
    config = {}
    
    if vram_gb > 1.0:  # If we have meaningful GPU memory
        # Reserve 1GB for system processes
        usable_vram = max(1.0, vram_gb - 1.0)
        config["0"] = f"{usable_vram:.0f}GB"
    
    # Reserve 4GB of RAM for system processes
    usable_ram = max(4.0, ram_gb - 4.0)
    config["cpu"] = f"{usable_ram:.0f}GB"
    
    return config