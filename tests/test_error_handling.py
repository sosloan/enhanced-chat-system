"""Tests for error handling module."""

import pytest
import logging
import asyncio
from src.lib.error_handling import (
    ErrorSeverity,
    ErrorContext,
    AnalyticsError,
    ValidationError,
    ComputationError,
    ResourceError,
    RecoveryStrategy,
    with_error_handling,
    ErrorHandler
)

@pytest.fixture
def error_context():
    """Create test error context."""
    return ErrorContext(
        operation="test_operation",
        input_data={"test": "data"},
        severity=ErrorSeverity.MEDIUM
    )

@pytest.fixture
def error_handler():
    """Create test error handler."""
    return ErrorHandler()

def test_error_severity():
    """Test error severity enum."""
    assert ErrorSeverity.LOW.value < ErrorSeverity.MEDIUM.value
    assert ErrorSeverity.MEDIUM.value < ErrorSeverity.HIGH.value
    assert ErrorSeverity.HIGH.value < ErrorSeverity.FATAL.value

def test_error_context():
    """Test error context creation."""
    context = ErrorContext(operation="test")
    assert context.operation == "test"
    assert context.severity == ErrorSeverity.MEDIUM
    assert context.retry_count == 0
    assert isinstance(context.error_chain, list)
    assert len(context.error_chain) == 0

def test_analytics_error():
    """Test analytics error creation."""
    context = ErrorContext(operation="test")
    cause = ValueError("Original error")
    error = AnalyticsError("Test error", context, cause)
    
    assert str(error) == "Test error"
    assert error.context == context
    assert error.cause == cause
    assert cause in error.context.error_chain

def test_error_hierarchy():
    """Test error class hierarchy."""
    context = ErrorContext(operation="test")
    
    validation_error = ValidationError("Invalid data", context)
    assert isinstance(validation_error, AnalyticsError)
    
    computation_error = ComputationError("Computation failed", context)
    assert isinstance(computation_error, AnalyticsError)
    
    resource_error = ResourceError("Resource unavailable", context)
    assert isinstance(resource_error, AnalyticsError)

@pytest.mark.asyncio
async def test_recovery_strategy():
    """Test recovery strategy execution."""
    strategy = RecoveryStrategy(
        max_retries=2,
        retry_delay=0.1,
        exponential_backoff=True
    )
    
    # Test successful execution
    async def success_func():
        return "success"
    
    result = await strategy.execute_with_recovery(success_func)
    assert result == "success"
    
    # Test failed execution with retries
    attempt_count = 0
    async def failing_func():
        nonlocal attempt_count
        attempt_count += 1
        raise ValueError("Test error")
    
    with pytest.raises(ComputationError):
        await strategy.execute_with_recovery(failing_func)
    assert attempt_count == 3  # Initial attempt + 2 retries

@pytest.mark.asyncio
async def test_recovery_with_fallback():
    """Test recovery strategy with fallback."""
    async def fallback_func(*args, **kwargs):
        return "fallback"
    
    strategy = RecoveryStrategy(
        max_retries=1,
        retry_delay=0.1,
        fallback_function=fallback_func
    )
    
    async def failing_func():
        raise ValueError("Test error")
    
    result = await strategy.execute_with_recovery(failing_func)
    assert result == "fallback"

@pytest.mark.asyncio
async def test_error_handling_decorator():
    """Test error handling decorator."""
    strategy = RecoveryStrategy(max_retries=1, retry_delay=0.1)
    
    @with_error_handling(
        error_severity=ErrorSeverity.HIGH,
        recovery_strategy=strategy
    )
    async def test_func():
        raise ValueError("Test error")
    
    with pytest.raises(ComputationError) as exc_info:
        await test_func()
    
    assert "Test error" in str(exc_info.value)
    assert exc_info.value.context.severity == ErrorSeverity.HIGH

def test_error_handler_initialization(error_handler):
    """Test error handler initialization."""
    assert isinstance(error_handler.logger, logging.Logger)
    assert error_handler.error_counts == {}
    assert error_handler.recovery_strategies == {}

def test_register_strategy(error_handler):
    """Test strategy registration."""
    strategy = RecoveryStrategy()
    error_handler.register_strategy("test_op", strategy)
    assert error_handler.get_strategy("test_op") == strategy
    assert error_handler.get_strategy("unknown_op") is None

@pytest.mark.asyncio
async def test_handle_error(error_handler, error_context):
    """Test error handling."""
    error = ValueError("Test error")
    
    # Handle regular exception
    result = await error_handler.handle_error(error, error_context)
    assert result is None
    assert error_handler.error_counts["test_operation"] == 1
    
    # Handle analytics error
    analytics_error = ComputationError("Test error", error_context)
    result = await error_handler.handle_error(analytics_error)
    assert result is None
    assert error_handler.error_counts["test_operation"] == 2

@pytest.mark.asyncio
async def test_handle_fatal_error(error_handler):
    """Test handling of fatal errors."""
    context = ErrorContext(
        operation="fatal_op",
        severity=ErrorSeverity.FATAL
    )
    error = ResourceError("Fatal error", context)
    
    with pytest.raises(ResourceError):
        await error_handler.handle_error(error)

@pytest.mark.asyncio
async def test_error_recovery_flow():
    """Test complete error recovery flow."""
    handler = ErrorHandler()
    
    # Create a strategy with a fallback
    async def fallback_func(*args, **kwargs):
        return "recovered"
    
    strategy = RecoveryStrategy(
        max_retries=1,
        retry_delay=0.1,
        fallback_function=fallback_func
    )
    
    handler.register_strategy("test_recovery", strategy)
    
    # Create a failing operation
    @with_error_handling(recovery_strategy=strategy)
    async def failing_operation():
        raise ValueError("Operation failed")
    
    # Execute with recovery
    try:
        result = await failing_operation()
        assert result == "recovered"
    except Exception as e:
        pytest.fail(f"Recovery should have succeeded but got error: {e}")

def test_error_stats(error_handler, error_context):
    """Test error statistics collection."""
    # Generate some errors
    error1 = ValueError("Error 1")
    error2 = RuntimeError("Error 2")
    
    asyncio.run(error_handler.handle_error(error1, error_context))
    asyncio.run(error_handler.handle_error(error2, error_context))
    
    stats = error_handler.get_error_stats()
    assert stats["total_errors"] == 2
    assert stats["error_counts"]["test_operation"] == 2
    assert "test_operation" in stats["operations_with_errors"]

@pytest.mark.asyncio
async def test_concurrent_error_handling(error_handler):
    """Test handling concurrent errors."""
    async def generate_error(i):
        context = ErrorContext(operation=f"op_{i}")
        error = ValueError(f"Error {i}")
        await error_handler.handle_error(error, context)
    
    # Generate multiple errors concurrently
    await asyncio.gather(*[
        generate_error(i) for i in range(5)
    ])
    
    stats = error_handler.get_error_stats()
    assert stats["total_errors"] == 5
    assert len(stats["operations_with_errors"]) == 5 