"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app, DataPoint, AnalyticsRequest

@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)

@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    return [
        DataPoint(id=i, value=float(i), metadata={"test": True})
        for i in range(4)
    ]

@pytest.fixture
def sample_request(sample_data):
    """Create a sample analytics request."""
    return AnalyticsRequest(
        data=sample_data,
        operation="mean",
        gpu_enabled=True
    )

@pytest.fixture
def operations():
    """List of supported operations."""
    return ["mean", "correlation", "matrix_multiply", "pca"]

@pytest.fixture
def invalid_operations():
    """List of invalid operations for testing error handling."""
    return ["median", "mode", "invalid_op", "unknown"]

@pytest.fixture
def malformed_data():
    """Create malformed data for testing error handling."""
    return [
        {"not_id": 1, "wrong_value": "string"},
        {"missing_value": True},
        {"id": "not_int", "value": None}
    ] 