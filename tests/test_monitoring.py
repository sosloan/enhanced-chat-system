"""Tests for monitoring module."""

import pytest
import os
import json
import time
from src.lib.monitoring import (
    AnalyticsMonitor,
    OperationMetrics,
    OperationTimer
)

@pytest.fixture
def test_log_dir(tmp_path):
    """Create temporary log directory."""
    log_dir = tmp_path / "test_logs"
    log_dir.mkdir()
    return str(log_dir)

@pytest.fixture
def monitor(test_log_dir):
    """Create analytics monitor instance."""
    return AnalyticsMonitor(
        log_dir=test_log_dir,
        metrics_file="test_metrics.json",
        debug=True
    )

def test_operation_metrics():
    """Test OperationMetrics dataclass."""
    metrics = OperationMetrics(
        operation="test_op",
        success=True,
        execution_time=1.0,
        gpu_used=False,
        data_points=100,
        memory_used=1024,
        warnings=["Test warning"]
    )
    
    assert metrics.operation == "test_op"
    assert metrics.success
    assert metrics.execution_time == 1.0
    assert not metrics.gpu_used
    assert metrics.data_points == 100
    assert metrics.memory_used == 1024
    assert metrics.warnings == ["Test warning"]
    assert metrics.error is None
    
    # Test conversion to dict
    data = metrics.to_dict()
    assert isinstance(data, dict)
    assert data["operation"] == "test_op"
    assert data["success"]
    assert data["execution_time"] == 1.0

def test_monitor_initialization(monitor, test_log_dir):
    """Test monitor initialization."""
    assert os.path.exists(test_log_dir)
    assert os.path.exists(os.path.join(test_log_dir, "analytics.log"))
    assert isinstance(monitor.metrics, list)

def test_gpu_metrics(monitor):
    """Test GPU metrics collection."""
    metrics = monitor.get_gpu_metrics()
    assert isinstance(metrics, dict)
    assert "gpu_available" in metrics
    assert isinstance(metrics["gpu_available"], bool)
    assert "gpu_count" in metrics
    assert isinstance(metrics["gpu_count"], int)

def test_system_metrics(monitor):
    """Test system metrics collection."""
    metrics = monitor.get_system_metrics()
    assert isinstance(metrics, dict)
    assert "cpu_percent" in metrics
    assert "memory_rss" in metrics
    assert "thread_count" in metrics
    assert "system_memory" in metrics
    assert all(key in metrics["system_memory"]
              for key in ["total", "available", "percent"])

def test_record_operation(monitor):
    """Test recording operation metrics."""
    metrics = OperationMetrics(
        operation="test_operation",
        success=True,
        execution_time=0.5,
        gpu_used=False,
        data_points=50,
        memory_used=1024
    )
    
    monitor.record_operation(metrics)
    
    assert len(monitor.metrics) == 1
    record = monitor.metrics[0]
    assert "timestamp" in record
    assert "operation" in record
    assert "system" in record
    assert "gpu" in record
    
    # Check metrics file
    with open(monitor.metrics_file, "r") as f:
        saved_metrics = json.load(f)
    assert len(saved_metrics) == 1
    assert saved_metrics[0]["operation"]["operation"] == "test_operation"

def test_operation_stats(monitor):
    """Test operation statistics calculation."""
    # Record multiple operations
    for i in range(5):
        metrics = OperationMetrics(
            operation="test_op",
            success=i < 4,  # Make one operation fail
            execution_time=0.1 * (i + 1),
            gpu_used=i % 2 == 0,
            data_points=100,
            memory_used=1024,
            error="Test error" if i == 4 else None
        )
        monitor.record_operation(metrics)
    
    stats = monitor.get_operation_stats("test_op")
    assert stats["count"] == 5
    assert stats["success_rate"] == 0.8  # 4/5 successful
    assert stats["gpu_usage_rate"] == 0.6  # 3/5 used GPU
    assert "execution_time" in stats
    assert all(key in stats["execution_time"]
              for key in ["mean", "std", "min", "max"])

def test_system_stats(monitor):
    """Test system statistics calculation."""
    # Record multiple operations
    for _ in range(3):
        metrics = OperationMetrics(
            operation="test_op",
            success=True,
            execution_time=0.1,
            gpu_used=False,
            data_points=100,
            memory_used=1024
        )
        monitor.record_operation(metrics)
    
    stats = monitor.get_system_stats()
    assert "cpu_usage" in stats
    assert "memory_usage" in stats
    assert all(key in stats["cpu_usage"] for key in ["mean", "max"])
    assert all(key in stats["memory_usage"] for key in ["mean", "max"])

def test_clear_metrics(monitor):
    """Test clearing metrics."""
    # Add some metrics
    metrics = OperationMetrics(
        operation="test_op",
        success=True,
        execution_time=0.1,
        gpu_used=False,
        data_points=100,
        memory_used=1024
    )
    monitor.record_operation(metrics)
    assert len(monitor.metrics) > 0
    
    # Clear metrics
    monitor.clear_metrics()
    assert len(monitor.metrics) == 0
    assert os.path.exists(monitor.metrics_file)
    with open(monitor.metrics_file, "r") as f:
        assert json.load(f) == []

def test_operation_timer(monitor):
    """Test operation timer context manager."""
    with OperationTimer(monitor, "test_timer") as timer:
        time.sleep(0.1)  # Simulate work
        timer.warnings.append("Test warning")
    
    assert len(monitor.metrics) == 1
    record = monitor.metrics[0]
    assert record["operation"]["operation"] == "test_timer"
    assert record["operation"]["success"]
    assert record["operation"]["execution_time"] >= 0.1
    assert record["operation"]["warnings"] == ["Test warning"]

def test_operation_timer_error(monitor):
    """Test operation timer with error."""
    try:
        with OperationTimer(monitor, "test_error"):
            raise ValueError("Test error")
    except ValueError:
        pass
    
    assert len(monitor.metrics) == 1
    record = monitor.metrics[0]
    assert record["operation"]["operation"] == "test_error"
    assert not record["operation"]["success"]
    assert "Test error" in record["operation"]["error"]

def test_monitor_with_multiple_operations(monitor):
    """Test monitor with multiple different operations."""
    operations = ["op1", "op2", "op3"]
    
    # Record different operations
    for op in operations:
        for i in range(2):
            metrics = OperationMetrics(
                operation=op,
                success=True,
                execution_time=0.1,
                gpu_used=False,
                data_points=100,
                memory_used=1024
            )
            monitor.record_operation(metrics)
    
    # Test filtering by operation
    for op in operations:
        stats = monitor.get_operation_stats(op)
        assert stats["count"] == 2
        assert stats["success_rate"] == 1.0
    
    # Test getting stats for last N operations
    stats = monitor.get_operation_stats(last_n=3)
    assert stats["count"] == 3 