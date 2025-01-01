"""Tests for FastAPI analytics endpoints."""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app, DataPoint, AnalyticsRequest

client = TestClient(app)

def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to the Analytics Platform"
    assert data["gpu_enabled"] is True
    assert "supported_operations" in data
    assert len(data["supported_operations"]) > 0

def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["gpu_available"] is True

def test_get_sample_data():
    """Test sample data endpoint."""
    response = client.get("/data")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10
    assert all(isinstance(d["id"], int) for d in data)
    assert all(isinstance(d["value"], float) for d in data)
    assert all(isinstance(d["metadata"], dict) for d in data)

@pytest.mark.parametrize("operation", ["mean", "correlation", "matrix_multiply", "pca"])
def test_analyze_cpu(operation):
    """Test analytics operations on CPU."""
    # Create test data
    data = [
        DataPoint(id=i, value=float(i), metadata={"test": True})
        for i in range(4)  # 4 points for 2x2 matrix operations
    ]
    
    request = AnalyticsRequest(
        data=data,
        operation=operation,
        gpu_enabled=False
    )
    
    response = client.post("/analyze", json=request.dict())
    assert response.status_code == 200
    result = response.json()
    assert isinstance(result["result"], float)
    assert isinstance(result["computation_time"], float)
    assert result["used_gpu"] is False

@pytest.mark.parametrize("operation", ["mean", "correlation", "matrix_multiply", "pca"])
def test_analyze_gpu(operation):
    """Test analytics operations on GPU."""
    # Create test data
    data = [
        DataPoint(id=i, value=float(i), metadata={"test": True})
        for i in range(4)  # 4 points for 2x2 matrix operations
    ]
    
    request = AnalyticsRequest(
        data=data,
        operation=operation,
        gpu_enabled=True
    )
    
    response = client.post("/analyze", json=request.dict())
    assert response.status_code == 200
    result = response.json()
    assert isinstance(result["result"], float)
    assert isinstance(result["computation_time"], float)
    assert result["used_gpu"] is True

def test_invalid_operation():
    """Test error handling for invalid operations."""
    data = [DataPoint(id=0, value=1.0)]
    request = AnalyticsRequest(
        data=data,
        operation="invalid_op",
        gpu_enabled=False
    )
    
    response = client.post("/analyze", json=request.dict())
    assert response.status_code == 400
    assert "Unsupported operation" in response.json()["detail"]

def test_empty_data():
    """Test error handling for empty data."""
    request = AnalyticsRequest(
        data=[],
        operation="mean",
        gpu_enabled=False
    )
    
    response = client.post("/analyze", json=request.dict())
    assert response.status_code == 500  # Should fail with empty data

def test_malformed_data():
    """Test error handling for malformed data."""
    response = client.post(
        "/analyze",
        json={"data": "not_a_list", "operation": "mean"}  # Invalid data format
    )
    assert response.status_code == 422  # Pydantic validation error

@pytest.mark.asyncio
async def test_concurrent_requests():
    """Test handling of concurrent analytics requests."""
    import asyncio
    import httpx
    
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        # Create multiple concurrent requests
        tasks = []
        for op in ["mean", "correlation"]:
            data = [DataPoint(id=i, value=float(i)) for i in range(4)]
            request = AnalyticsRequest(
                data=data,
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