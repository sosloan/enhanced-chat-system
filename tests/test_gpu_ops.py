"""Tests for GPU operations module."""

import pytest
import numpy as np
from src.lib.gpu_ops import (
    GPUOperations,
    GPUResult,
    get_available_operations,
    is_gpu_available,
    get_gpu_info
)

@pytest.fixture
def gpu_ops():
    """Create GPU operations instance."""
    return GPUOperations(gpu_enabled=True)

@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    np.random.seed(42)
    return [float(x) for x in np.random.randn(100)]

@pytest.fixture
def matrix_data():
    """Create sample matrix data for testing."""
    np.random.seed(42)
    return [float(x) for x in np.random.randn(100)]  # 10x10 matrix

def test_gpu_result():
    """Test GPUResult dataclass."""
    result = GPUResult(value=1.0, computation_time=0.1)
    assert result.value == 1.0
    assert result.computation_time == 0.1
    assert result.used_gpu is True

def test_initialization(gpu_ops):
    """Test GPU operations initialization."""
    assert isinstance(gpu_ops, GPUOperations)
    assert hasattr(gpu_ops, "device")
    assert gpu_ops.gpu_enabled in [True, False]

def test_available_operations():
    """Test getting available operations."""
    ops = get_available_operations()
    assert isinstance(ops, list)
    assert len(ops) > 0
    assert all(isinstance(op, str) for op in ops)
    assert "mean" in ops
    assert "correlation" in ops
    assert "matrix_multiply" in ops
    assert "pca" in ops

def test_gpu_info():
    """Test getting GPU information."""
    info = get_gpu_info()
    assert isinstance(info, dict)
    assert "available" in info
    if info["available"]:
        assert "device_count" in info
        assert "current_device" in info
        assert "device_name" in info
        assert "memory_allocated" in info
        assert "memory_cached" in info

@pytest.mark.asyncio
async def test_mean(gpu_ops, sample_data):
    """Test mean calculation."""
    result = await gpu_ops.mean.remote(sample_data)
    assert isinstance(result, GPUResult)
    assert abs(result.value - np.mean(sample_data)) < 1e-5
    assert result.computation_time > 0
    assert result.used_gpu == gpu_ops.gpu_enabled

@pytest.mark.asyncio
async def test_correlation(gpu_ops, matrix_data):
    """Test correlation calculation."""
    result = await gpu_ops.correlation.remote(matrix_data)
    assert isinstance(result, GPUResult)
    assert -1 <= result.value <= 1  # Correlation should be between -1 and 1
    assert result.computation_time > 0
    assert result.used_gpu == gpu_ops.gpu_enabled

@pytest.mark.asyncio
async def test_matrix_multiply(gpu_ops, matrix_data):
    """Test matrix multiplication."""
    result = await gpu_ops.matrix_multiply.remote(matrix_data)
    assert isinstance(result, GPUResult)
    assert isinstance(result.value, float)
    assert result.computation_time > 0
    assert result.used_gpu == gpu_ops.gpu_enabled

@pytest.mark.asyncio
async def test_pca(gpu_ops, matrix_data):
    """Test PCA calculation."""
    result = await gpu_ops.pca.remote(matrix_data)
    assert isinstance(result, GPUResult)
    assert result.value > 0  # Eigenvalue should be positive
    assert result.computation_time > 0
    assert result.used_gpu == gpu_ops.gpu_enabled

@pytest.mark.asyncio
async def test_custom_operations(gpu_ops, sample_data):
    """Test custom operations."""
    operations = ["sum", "std", "max", "min", "norm"]
    
    for op in operations:
        result = await gpu_ops.custom_operation.remote(sample_data, op)
        assert isinstance(result, GPUResult)
        assert isinstance(result.value, float)
        assert result.computation_time > 0
        assert result.used_gpu == gpu_ops.gpu_enabled
        
        # Verify results against numpy
        if op == "sum":
            assert abs(result.value - np.sum(sample_data)) < 1e-5
        elif op == "std":
            assert abs(result.value - np.std(sample_data)) < 1e-5
        elif op == "max":
            assert abs(result.value - np.max(sample_data)) < 1e-5
        elif op == "min":
            assert abs(result.value - np.min(sample_data)) < 1e-5
        elif op == "norm":
            assert abs(result.value - np.linalg.norm(sample_data)) < 1e-5

@pytest.mark.asyncio
async def test_invalid_custom_operation(gpu_ops, sample_data):
    """Test invalid custom operation."""
    with pytest.raises(ValueError):
        await gpu_ops.custom_operation.remote(sample_data, "invalid_op")

@pytest.mark.asyncio
async def test_custom_operation_params(gpu_ops, sample_data):
    """Test custom operation with parameters."""
    # Test L1 norm
    result_l1 = await gpu_ops.custom_operation.remote(
        sample_data,
        "norm",
        {"p": 1}
    )
    assert abs(result_l1.value - np.linalg.norm(sample_data, ord=1)) < 1e-5
    
    # Test L2 norm (default)
    result_l2 = await gpu_ops.custom_operation.remote(
        sample_data,
        "norm"
    )
    assert abs(result_l2.value - np.linalg.norm(sample_data)) < 1e-5

@pytest.mark.asyncio
async def test_large_data(gpu_ops):
    """Test operations with large data."""
    large_data = [float(x) for x in np.random.randn(10000)]
    
    # Test mean
    result = await gpu_ops.mean.remote(large_data)
    assert abs(result.value - np.mean(large_data)) < 1e-5
    
    # Test matrix multiply (100x100)
    matrix_data = [float(x) for x in np.random.randn(10000)]
    result = await gpu_ops.matrix_multiply.remote(matrix_data)
    assert isinstance(result.value, float)

@pytest.mark.asyncio
async def test_concurrent_operations(gpu_ops, sample_data):
    """Test concurrent GPU operations."""
    import asyncio
    
    # Create multiple operations
    operations = [
        gpu_ops.mean.remote(sample_data),
        gpu_ops.correlation.remote(sample_data),
        gpu_ops.matrix_multiply.remote(sample_data),
        gpu_ops.pca.remote(sample_data)
    ]
    
    # Run operations concurrently
    results = await asyncio.gather(*operations)
    
    # Verify results
    assert all(isinstance(r, GPUResult) for r in results)
    assert all(isinstance(r.value, float) for r in results)
    assert all(r.computation_time > 0 for r in results)
    assert all(r.used_gpu == gpu_ops.gpu_enabled for r in results) 