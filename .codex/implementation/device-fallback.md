# VRAM OOM Device Fallback

Automatic fallback mechanism for handling VRAM (GPU memory) out-of-memory errors by retrying model loading on CPU.

## Overview

When GPU memory runs out during model loading, the system automatically falls back to CPU processing. This prevents crashes and ensures the application continues to function, albeit with potentially slower performance.

## Implementation

### Core Module: `src/utils/device_fallback.py`

- **`safe_load_model()`**: Generic wrapper that catches CUDA OOM errors and retries with CPU device
- **`safe_load_embeddings()`**: Wrapper for HuggingFace embeddings with OOM fallback  
- **`safe_load_pipeline()`**: Wrapper for HuggingFace pipelines with OOM fallback

### Applied To

1. **Embedding Models** (`src/vectorstore/chroma.py`)
   - `sentence-transformers/all-MiniLM-L6-v2` model used for vector embeddings
   - Falls back to CPU if GPU VRAM is insufficient

2. **Language Models** (`lyra.py`, `src/integrations/discord_bot.py`)
   - `microsoft/phi-2` model used for text generation
   - Falls back to CPU if GPU VRAM is insufficient

## Error Handling

The fallback mechanism catches:
- `torch.cuda.OutOfMemoryError` - Direct CUDA OOM errors
- `RuntimeError` containing "out of memory" or "cuda" - Runtime OOM errors

Non-OOM errors are re-raised unchanged.

## Device Configuration

On fallback, the following parameters are updated to force CPU usage:
- `device="cpu"` 
- `model_kwargs={"device": "cpu"}`
- `device_map="cpu"`

## Logging

- Debug: Initial model loading attempt
- Warning: CUDA OOM error detected with fallback message  
- Info: Retrying model loading on CPU

## Testing

Comprehensive test suite in `src/tests/test_device_fallback.py` covers:
- Normal operation (no OOM)
- CUDA OOM fallback scenarios
- RuntimeError OOM fallback
- Non-OOM error re-raising
- Device parameter handling