"""Tests for main application."""

import pytest
from fastapi.testclient import TestClient
import torch
from src.main import app, cache, error_handler

@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)

def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    
    assert data["name"] == "GPU Analytics Platform"
    assert data["version"] == "1.0.0"
    assert isinstance(data["gpu_available"], bool)
    assert len(data["endpoints"]) == 3
    
    # Verify endpoints
    endpoints = {ep["path"] for ep in data["endpoints"]}
    assert "/api" in endpoints
    assert "/docs" in endpoints
    assert "/stats" in endpoints

def test_stats_endpoint(client):
    """Test statistics endpoint."""
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    
    # Check cache stats
    assert "cache" in data
    assert "hits" in data["cache"]
    assert "misses" in data["cache"]
    assert "size" in data["cache"]
    
    # Check error stats
    assert "errors" in data
    assert "total_errors" in data["errors"]
    assert "error_counts" in data["errors"]
    
    # Check GPU stats
    assert "gpu" in data
    assert "available" in data["gpu"]
    assert "device_count" in data["gpu"]
    assert "memory_allocated" in data["gpu"]
    assert "memory_reserved" in data["gpu"]

def test_api_mount(client):
    """Test API mounting."""
    # Test API root
    response = client.get("/api/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "gpu_enabled" in data
    
    # Test API health check
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_startup_shutdown():
    """Test application startup and shutdown events."""
    # Get startup event handler
    startup_handler = None
    shutdown_handler = None
    
    for event in app.router.on_startup:
        if event.__name__ == "startup":
            startup_handler = event
    
    for event in app.router.on_shutdown:
        if event.__name__ == "shutdown":
            shutdown_handler = event
    
    assert startup_handler is not None
    assert shutdown_handler is not None
    
    # Run startup
    await startup_handler()
    
    # Verify initialization
    assert cache._cleanup_task is not None
    assert len(error_handler.recovery_strategies) == 2
    assert "compute" in error_handler.recovery_strategies
    assert "resource" in error_handler.recovery_strategies
    
    # Run shutdown
    await shutdown_handler()
    
    # Verify cleanup
    assert cache._cleanup_task is None

def test_gpu_detection():
    """Test GPU detection."""
    response = TestClient(app).get("/stats")
    data = response.json()
    
    if torch.cuda.is_available():
        assert data["gpu"]["available"]
        assert data["gpu"]["device_count"] > 0
        assert isinstance(data["gpu"]["memory_allocated"], int)
        assert isinstance(data["gpu"]["memory_reserved"], int)
    else:
        assert not data["gpu"]["available"]
        assert data["gpu"]["device_count"] == 0
        assert data["gpu"]["memory_allocated"] == 0
        assert data["gpu"]["memory_reserved"] == 0

def test_error_handling(client):
    """Test error handling in endpoints."""
    # Test non-existent endpoint
    response = client.get("/nonexistent")
    assert response.status_code == 404
    
    # Test invalid method
    response = client.post("/")
    assert response.status_code == 405
    
    # Test invalid API endpoint
    response = client.get("/api/invalid")
    assert response.status_code == 404

def test_documentation_endpoints(client):
    """Test API documentation endpoints."""
    # OpenAPI schema
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "GPU Analytics Platform"
    
    # Swagger UI
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger-ui" in response.text.lower()
    
    # ReDoc
    response = client.get("/redoc")
    assert response.status_code == 200
    assert "redoc" in response.text.lower()

def test_concurrent_requests(client):
    """Test handling of concurrent requests."""
    import asyncio
    import httpx
    
    async def make_request():
        async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/stats")
            return response.status_code
    
    # Run multiple requests concurrently
    responses = asyncio.run(asyncio.gather(*[
        make_request() for _ in range(10)
    ]))
    
    # All requests should succeed
    assert all(status == 200 for status in responses)

def test_cache_integration(client):
    """Test cache integration."""
    # Make multiple requests to trigger caching
    for _ in range(3):
        response = client.get("/stats")
        assert response.status_code == 200
    
    # Check cache stats
    cache_stats = cache.get_stats()
    assert cache_stats["size"] >= 0
    assert cache_stats["hits"] >= 0
    assert cache_stats["misses"] >= 0

def test_error_handler_integration(client):
    """Test error handler integration."""
    # Initial error count
    initial_stats = error_handler.get_error_stats()
    initial_count = initial_stats["total_errors"]
    
    # Trigger some errors
    for _ in range(3):
        client.get("/nonexistent")
    
    # Check error stats
    final_stats = error_handler.get_error_stats()
    assert final_stats["total_errors"] >= initial_count 