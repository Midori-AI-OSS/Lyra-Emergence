# Model Sharding and Configuration

This document describes the model sharding and configuration features added to support efficient GPU memory usage and progressive fallback strategies.

## Overview

The Lyra-Emergence project now supports:
- **Model Sharding**: Distribute model layers across GPU and CPU
- **Progressive Fallback**: Gracefully reduce GPU usage when running out of memory
- **Configuration-Based Setup**: Tune parameters via JSON configuration files
- **Backward Compatibility**: Existing code continues to work unchanged

## Features

### Model Sharding
- Uses HuggingFace's `device_map` parameter for automatic or custom layer distribution
- Supports memory limits per device via `max_memory` configuration
- Enables model quantization (8-bit, 4-bit) for reduced memory usage

### Progressive Fallback Strategy
1. **Full GPU**: Attempts to load model entirely on GPU
2. **Partial GPU**: On OOM, moves some layers to CPU (configurable count)
3. **Full CPU**: Final fallback to CPU-only execution

### Configuration System
- JSON-based configuration files
- Automatic discovery of config files in standard locations
- Override via command line arguments

## Configuration

### Configuration File

Create a `config/model_config.json` file:

```json
{
  "model_id": "microsoft/phi-2",
  "task": "text-generation",
  "device_map": "auto",
  "max_memory": {
    "0": "6GB",
    "cpu": "16GB"
  },
  "low_cpu_mem_usage": true,
  "gpu_layers_fallback": 16,
  "enable_progressive_fallback": true,
  "load_in_8bit": false,
  "load_in_4bit": false,
  "pipeline_kwargs": {
    "max_new_tokens": 4000,
    "do_sample": true,
    "temperature": 0.7
  }
}
```

### Configuration Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `model_id` | string | HuggingFace model identifier |
| `task` | string | Task type (e.g., "text-generation") |
| `device_map` | string/null | Device mapping strategy ("auto", "cpu", or custom) |
| `max_memory` | object/null | Memory limits per device |
| `low_cpu_mem_usage` | boolean | Enable efficient CPU memory usage |
| `gpu_layers_fallback` | integer/null | Number of layers to keep on GPU during fallback |
| `enable_progressive_fallback` | boolean | Enable progressive fallback strategy |
| `load_in_8bit` | boolean | Enable 8-bit quantization |
| `load_in_4bit` | boolean | Enable 4-bit quantization |
| `pipeline_kwargs` | object/null | Additional pipeline parameters |

## Usage

### Command Line

```bash
# Use default configuration
uv run lyra.py

# Use custom configuration file
uv run lyra.py --model-config path/to/config.json

# Other existing options work as before
uv run lyra.py --rerank --journal data/journal/sample.json
```

### Programmatic Usage

```python
from src.utils.device_fallback import safe_load_pipeline
from src.config.model_config import ModelConfig

# Using configuration file
llm = safe_load_pipeline(
    model_id="microsoft/phi-2",
    task="text-generation",
    config_path="config/model_config.json"
)

# Using configuration object
config = ModelConfig(
    device_map="auto",
    gpu_layers_fallback=16,
    max_memory={"0": "8GB", "cpu": "16GB"}
)

from src.utils.device_fallback import safe_load_model_with_config
from langchain_huggingface import HuggingFacePipeline

llm = safe_load_model_with_config(
    HuggingFacePipeline.from_model_id,
    config,
    "microsoft/phi-2",
    "text-generation"
)
```

## Progressive Fallback Example

When GPU memory is insufficient:

1. **Initial attempt**: Load with `device_map="auto"`
2. **Progressive fallback**: Create custom device map with first N layers on GPU
3. **CPU fallback**: Move entire model to CPU

```
Initial: All layers on GPU (requires ~3GB VRAM)
    ↓ (OOM Error)
Fallback: 16 layers on GPU, rest on CPU (requires ~1.5GB VRAM)
    ↓ (OOM Error)
Final: All layers on CPU (no VRAM required)
```

## Device Map Examples

### Automatic Sharding
```json
{
  "device_map": "auto",
  "max_memory": {"0": "8GB", "cpu": "16GB"}
}
```

### Custom Layer Distribution
Progressive fallback automatically creates device maps like:
```python
{
  "model.embed_tokens": 0,
  "model.layers.0": 0,
  "model.layers.1": 0,
  # ... first N layers on GPU
  "model.layers.16": "cpu",
  "model.layers.17": "cpu",
  # ... remaining layers on CPU
  "model.norm": "cpu",
  "lm_head": "cpu"
}
```

## Configuration File Locations

The system searches for configuration files in this order:
1. Path specified via `--model-config` argument
2. `config/model_config.json`
3. `data/model_config.json`
4. `model_config.json` (current directory)

If no configuration file is found, default settings are used.

## Backward Compatibility

All existing code continues to work without changes:
- `safe_load_pipeline()` now supports configuration but maintains the same interface
- Legacy behavior available via `safe_load_pipeline_legacy()`
- Original `safe_load_model()` function unchanged

## Testing

Run the test suite to verify functionality:

```bash
# Test configuration system
uv run pytest src/tests/test_model_config.py -v

# Test device fallback (including new features)
uv run pytest src/tests/test_device_fallback.py -v

# Run all tests
uv run pytest -v
```

## Troubleshooting

### Common Issues

**Configuration not loading**: Check file paths and JSON syntax
```bash
# Verify config file exists and is valid JSON
cat config/model_config.json | python -m json.tool
```

**OOM errors persist**: Reduce `gpu_layers_fallback` count or enable quantization
```json
{
  "gpu_layers_fallback": 8,
  "load_in_8bit": true
}
```

**Slow performance**: Increase GPU layer count if memory allows
```json
{
  "gpu_layers_fallback": 24,
  "max_memory": {"0": "12GB"}
}
```

### Debug Logging

Enable debug logging to see fallback behavior:
```python
import logging
logging.getLogger('src.utils.device_fallback').setLevel(logging.DEBUG)
```

## Performance Considerations

- **GPU layers**: More GPU layers = faster inference, more VRAM usage
- **Quantization**: Reduces memory but may impact quality slightly
- **Progressive fallback**: Adds minimal overhead, only triggered on OOM
- **Configuration loading**: Cached after first load, negligible performance impact