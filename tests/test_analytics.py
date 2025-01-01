"""Tests for analytics API endpoints."""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app, DataPoint, AnalyticsRequest

@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)

@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    return [
        DataPoint(id=i, value=float(i), metadata={"test": True})
        for i in range(4)  # 4 points for 2x2 matrix operations
    ]

@pytest.fixture
def sample_request(sample_data):
    """Create sample analytics request."""
    return AnalyticsRequest(
        data=sample_data,
        operation="mean",
        gpu_enabled=True
    )

def test_root(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to the Analytics Platform"
    assert data["gpu_enabled"] is True
    assert "supported_operations" in data
    assert len(data["supported_operations"]) > 0

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert isinstance(data["gpu_available"], bool)

def test_get_sample_data(client):
    """Test sample data endpoint."""
    response = client.get("/data")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10
    assert all(isinstance(d["id"], int) for d in data)
    assert all(isinstance(d["value"], float) for d in data)
    assert all(isinstance(d["metadata"], dict) for d in data)

@pytest.mark.parametrize("operation", ["mean", "correlation", "matrix_multiply", "pca"])
def test_analyze_cpu(client, sample_data, operation):
    """Test analytics operations on CPU."""
    request = AnalyticsRequest(
        data=sample_data,
        operation=operation,
        gpu_enabled=False
    )
    
    response = client.post("/analyze", json=request.dict())
    assert response.status_code == 200
    result = response.json()
    assert isinstance(result["result"], float)
    assert isinstance(result["computation_time"], float)
    assert result["used_gpu"] is False
    assert result["operation"] == operation

@pytest.mark.parametrize("operation", ["mean", "correlation", "matrix_multiply", "pca"])
def test_analyze_gpu(client, sample_data, operation):
    """Test analytics operations on GPU."""
    request = AnalyticsRequest(
        data=sample_data,
        operation=operation,
        gpu_enabled=True
    )
    
    response = client.post("/analyze", json=request.dict())
    assert response.status_code == 200
    result = response.json()
    assert isinstance(result["result"], float)
    assert isinstance(result["computation_time"], float)
    assert result["used_gpu"] is True
    assert result["operation"] == operation

def test_invalid_operation(client, sample_data):
    """Test error handling for invalid operations."""
    request = AnalyticsRequest(
        data=sample_data,
        operation="invalid_op",
        gpu_enabled=False
    )
    
    response = client.post("/analyze", json=request.dict())
    assert response.status_code == 400
    assert "Unsupported operation" in response.json()["detail"]

def test_empty_data(client):
    """Test error handling for empty data."""
    request = AnalyticsRequest(
        data=[],
        operation="mean",
        gpu_enabled=False
    )
    
    response = client.post("/analyze", json=request.dict())
    assert response.status_code == 500
    assert "Empty data" in response.json()["detail"]

def test_malformed_data(client):
    """Test error handling for malformed data."""
    response = client.post(
        "/analyze",
        json={"data": "not_a_list", "operation": "mean"}
    )
    assert response.status_code == 422  # Pydantic validation error

@pytest.mark.asyncio
async def test_concurrent_requests(client, sample_data):
    """Test handling of concurrent analytics requests."""
    import asyncio
    import httpx
    
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        # Create multiple concurrent requests
        tasks = []
        for op in ["mean", "correlation"]:
            request = AnalyticsRequest(
                data=sample_data,
                operation=op,
                gpu_enabled=True
            )
            tasks.append(ac.post("/analyze", json=request.dict()))
        
        # Run requests concurrently
        responses = await asyncio.gather(*tasks)
        
        # Verify all requests succeeded
        assert all(r.status_code == 200 for r in responses)
        results = [r.json() for r in responses]
        assert all(isinstance(r["result"], float) for r in results)
        assert all(r["used_gpu"] for r in results)

def test_large_dataset(client):
    """Test handling of large datasets."""
    import numpy as np
    
    # Create large dataset
    data = [
        DataPoint(
            id=i,
            value=float(np.random.randn()),
            metadata={"batch": i // 100}
        )
        for i in range(1000)
    ]
    
    request = AnalyticsRequest(
        data=data,
        operation="matrix_multiply",  # Operation that benefits from GPU
        gpu_enabled=True
    )
    
    response = client.post("/analyze", json=request.dict())
    assert response.status_code == 200
    result = response.json()
    assert isinstance(result["result"], float)
    assert result["used_gpu"] is True
    assert result["computation_time"] > 0

def test_result_consistency(client, sample_data):
    """Test consistency of results between CPU and GPU."""
    operations = ["mean", "correlation"]
    
    for op in operations:
        # CPU request
        cpu_request = AnalyticsRequest(
            data=sample_data,
            operation=op,
            gpu_enabled=False
        )
        cpu_response = client.post("/analyze", json=cpu_request.dict())
        cpu_result = cpu_response.json()["result"]
        
        # GPU request
        gpu_request = AnalyticsRequest(
            data=sample_data,
            operation=op,
            gpu_enabled=True
        )
        gpu_response = client.post("/analyze", json=gpu_request.dict())
        gpu_result = gpu_response.json()["result"]
        
        # Results should be close (allowing for floating-point differences)
        assert abs(cpu_result - gpu_result) < 1e-5 