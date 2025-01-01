"""Tests for code execution module."""

import pytest
import asyncio
from src.lib.code_execution import CodeExecutor, execute_code_async

@pytest.fixture
def executor():
    """Create code executor instance."""
    return CodeExecutor(gpu_enabled=True)

def test_is_valid_python(executor):
    """Test Python code validation."""
    assert executor.is_valid_python("x = 1 + 2")
    assert executor.is_valid_python("def test(): pass")
    assert not executor.is_valid_python("x = 1 +")
    assert not executor.is_valid_python("def test(: pass")

def test_calculate_complexity(executor):
    """Test code complexity calculation."""
    # Simple code
    assert executor.calculate_complexity("x = 1") < 0.2
    
    # Medium complexity
    code = """
    def test(x):
        if x > 0:
            return x + 1
        return x - 1
    """
    assert 0.2 <= executor.calculate_complexity(code) <= 0.5
    
    # High complexity
    code = """
    class Test:
        def __init__(self):
            self.x = 0
            
        def process(self, data):
            result = []
            for item in data:
                try:
                    if item > 0:
                        while item > 10:
                            item -= 1
                        result.append(item)
                except Exception as e:
                    print(f"Error: {e}")
            return result
    """
    assert executor.calculate_complexity(code) > 0.5

@pytest.mark.asyncio
async def test_basic_execution(executor):
    """Test basic code execution."""
    code = """
    x = 1 + 2
    result = x
    """
    result = await executor.execute_code_async(code)
    assert result.success
    assert result.output == "3"
    assert result.error is None
    assert result.execution_time > 0

@pytest.mark.asyncio
async def test_syntax_error():
    """Test handling of syntax errors."""
    code = "x = 1 +"
    result = await execute_code_async(code)
    assert not result.success
    assert "SyntaxError" in result.error

@pytest.mark.asyncio
async def test_runtime_error():
    """Test handling of runtime errors."""
    code = """
    x = 1 / 0
    result = x
    """
    result = await execute_code_async(code)
    assert not result.success
    assert "ZeroDivisionError" in result.error

@pytest.mark.asyncio
async def test_timeout():
    """Test code execution timeout."""
    code = """
    import time
    while True:
        time.sleep(0.1)
    """
    result = await execute_code_async(code, timeout=1)
    assert not result.success
    assert "timed out" in result.error.lower()

@pytest.mark.asyncio
async def test_complex_code():
    """Test execution of more complex code."""
    code = """
    def factorial(n):
        if n <= 1:
            return 1
        return n * factorial(n - 1)
        
    result = factorial(5)
    """
    result = await execute_code_async(code)
    assert result.success
    assert result.output == "120"
    assert result.complexity_score > 0.2

@pytest.mark.asyncio
async def test_gpu_numpy():
    """Test GPU-accelerated NumPy operations."""
    code = """
    import numpy as np
    import torch
    
    # Create random matrix
    data = np.random.randn(100, 100)
    tensor = torch.tensor(data, device=device)
    
    # Perform matrix multiplication
    result = float(torch.matmul(tensor, tensor).mean().cpu().numpy())
    """
    result = await execute_code_async(code, use_gpu=True)
    assert result.success
    assert result.used_gpu
    assert float(result.output) != 0  # Should be some non-zero value

@pytest.mark.asyncio
async def test_concurrent_execution():
    """Test concurrent code execution."""
    code1 = """
    import time
    time.sleep(0.1)
    result = 1
    """
    
    code2 = """
    import time
    time.sleep(0.1)
    result = 2
    """
    
    # Run both codes concurrently
    results = await asyncio.gather(
        execute_code_async(code1),
        execute_code_async(code2)
    )
    
    assert all(r.success for r in results)
    assert results[0].output == "1"
    assert results[1].output == "2"

@pytest.mark.asyncio
async def test_output_capture():
    """Test capturing of code output."""
    code = """
    print("test output")
    result = 42
    """
    result = await execute_code_async(code)
    assert result.success
    assert result.output == "42"  # Only final result is captured

@pytest.mark.asyncio
async def test_globals_dict():
    """Test using custom globals dictionary."""
    globals_dict = {
        "custom_var": 42,
        "custom_func": lambda x: x * 2
    }
    
    code = """
    result = custom_func(custom_var)
    """
    
    result = await execute_code_async(code, globals_dict=globals_dict)
    assert result.success
    assert result.output == "84" 