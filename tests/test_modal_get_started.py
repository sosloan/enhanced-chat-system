"""Tests for Modal GPU functionality."""

import pytest
import modal
import asyncio
import subprocess
from unittest.mock import patch, MagicMock

# Create test app
test_app = modal.App("test-gpu")

@test_app.function(gpu="A10G")
def test_gpu_function():
    """Test function that runs on GPU."""
    try:
        subprocess.run(["nvidia-smi", "--list-gpus"], check=True, capture_output=True)
        return True
    except Exception:
        return False

@pytest.fixture
def mock_gpu_output():
    """Mock GPU output for testing."""
    return """GPU 0: NVIDIA A10G (UUID: GPU-...)
GPU 1: NVIDIA A10G (UUID: GPU-...)"""

@pytest.mark.asyncio
async def test_gpu_detection():
    """Test that GPU is properly detected."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        result = await test_gpu_function.remote()
        assert result is True
        mock_run.assert_called_once_with(
            ["nvidia-smi", "--list-gpus"],
            check=True,
            capture_output=True
        )

@pytest.mark.asyncio
async def test_gpu_not_available():
    """Test handling when GPU is not available."""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, "nvidia-smi")
        result = await test_gpu_function.remote()
        assert result is False

@pytest.mark.asyncio
async def test_gpu_computation():
    """Test actual GPU computation using PyTorch."""
    code = """
import torch
if not torch.cuda.is_available():
    raise RuntimeError("CUDA not available")
    
x = torch.randn(1000, 1000, device='cuda')
y = torch.matmul(x, x)
assert y.shape == (1000, 1000)
"""
    
    # Use our code execution module to run on GPU
    from src.lib.code_execution import execute_code_async
    
    result = await execute_code_async(code, use_gpu=True)
    assert result.success
    assert result.metrics["executed_on_gpu"]
    assert "RuntimeError" not in result.error

@pytest.mark.asyncio
async def test_gpu_memory():
    """Test GPU memory reporting."""
    code = """
import torch
torch.cuda.empty_cache()
total_memory = torch.cuda.get_device_properties(0).total_memory
free_memory = torch.cuda.memory_allocated()
print(f"Total GPU memory: {total_memory}")
print(f"Currently allocated: {free_memory}")
"""
    
    from src.lib.code_execution import execute_code_async
    
    result = await execute_code_async(code, use_gpu=True)
    assert result.success
    assert "Total GPU memory:" in result.output
    assert "Currently allocated:" in result.output

@pytest.mark.asyncio
async def test_multiple_gpu_ops():
    """Test multiple GPU operations in sequence."""
    code = """
import torch
import time

def benchmark_gpu():
    start = time.time()
    x = torch.randn(2000, 2000, device='cuda')
    y = torch.randn(2000, 2000, device='cuda')
    for _ in range(10):
        z = torch.matmul(x, y)
    torch.cuda.synchronize()
    return time.time() - start

time_taken = benchmark_gpu()
print(f"Time taken: {time_taken:.2f} seconds")
"""
    
    from src.lib.code_execution import execute_code_async
    
    result = await execute_code_async(code, use_gpu=True, timeout=30)
    assert result.success
    assert "Time taken:" in result.output
    assert result.metrics["executed_on_gpu"]
    
@pytest.mark.asyncio
async def test_gpu_error_handling():
    """Test handling of GPU-specific errors."""
    code = """
import torch
# Try to allocate more memory than available
x = torch.randn(1000000, 1000000, device='cuda')  # Should fail
"""
    
    from src.lib.code_execution import execute_code_async
    
    result = await execute_code_async(code, use_gpu=True)
    assert not result.success
    assert "CUDA" in result.error or "GPU" in result.error

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 