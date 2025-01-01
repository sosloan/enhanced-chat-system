"""Tests for data validation module."""

import pytest
import numpy as np
from src.lib.data_validation import (
    DataPoint,
    DataValidator,
    ValidationResult,
    validate_operation,
    validate_gpu_config
)

@pytest.fixture
def validator():
    """Create data validator instance."""
    return DataValidator(
        min_points=2,
        max_points=100,
        require_square_matrix=False
    )

@pytest.fixture
def valid_data():
    """Create valid test data."""
    return [
        {"id": i, "value": float(i), "metadata": {"test": True}}
        for i in range(10)
    ]

@pytest.fixture
def invalid_data():
    """Create invalid test data."""
    return [
        {"id": -1, "value": 1.0},  # Invalid ID
        {"id": 1, "value": float("inf")},  # Invalid value
        {"id": 2},  # Missing value
        {"not_id": 3, "not_value": 4.0},  # Missing required fields
        {"id": "invalid", "value": "not_float"}  # Invalid types
    ]

def test_data_point_model():
    """Test DataPoint model validation."""
    # Valid data
    point = DataPoint(id=1, value=2.0, metadata={"test": True})
    assert point.id == 1
    assert point.value == 2.0
    assert point.metadata == {"test": True}
    
    # Invalid ID
    with pytest.raises(ValueError):
        DataPoint(id=-1, value=1.0)
    
    # Invalid value
    with pytest.raises(ValueError):
        DataPoint(id=1, value=float("inf"))

def test_validation_result():
    """Test ValidationResult dataclass."""
    result = ValidationResult(
        is_valid=True,
        errors=[],
        warnings=["Warning 1"],
        stats={"count": 10}
    )
    assert result.is_valid
    assert len(result.errors) == 0
    assert len(result.warnings) == 1
    assert result.stats["count"] == 10

def test_validate_valid_data(validator, valid_data):
    """Test validation of valid data."""
    result = validator.validate_data_points(valid_data)
    assert result.is_valid
    assert len(result.errors) == 0
    assert result.stats["count"] == len(valid_data)
    assert "mean" in result.stats
    assert "std" in result.stats
    assert "min" in result.stats
    assert "max" in result.stats

def test_validate_invalid_data(validator, invalid_data):
    """Test validation of invalid data."""
    result = validator.validate_data_points(invalid_data)
    assert not result.is_valid
    assert len(result.errors) > 0
    assert result.stats["missing_values"] > 0
    assert result.stats["infinite_values"] > 0

def test_validate_data_size(validator):
    """Test data size validation."""
    # Too few points
    result = validator.validate_data_points([{"id": 0, "value": 1.0}])
    assert not result.is_valid
    assert any("Too few data points" in error for error in result.errors)
    
    # Too many points
    large_data = [
        {"id": i, "value": float(i)}
        for i in range(validator.max_points + 1)
    ]
    result = validator.validate_data_points(large_data)
    assert not result.is_valid
    assert any("Too many data points" in error for error in result.errors)

def test_validate_square_matrix():
    """Test square matrix validation."""
    validator = DataValidator(require_square_matrix=True)
    
    # Valid square matrix (4 points = 2x2)
    data = [{"id": i, "value": float(i)} for i in range(4)]
    result = validator.validate_data_points(data)
    assert result.is_valid
    
    # Invalid matrix size (3 points)
    data = [{"id": i, "value": float(i)} for i in range(3)]
    result = validator.validate_data_points(data)
    assert not result.is_valid
    assert any("perfect square" in error for error in result.errors)

def test_duplicate_ids(validator):
    """Test duplicate ID detection."""
    data = [
        {"id": 1, "value": 1.0},
        {"id": 2, "value": 2.0},
        {"id": 1, "value": 3.0}  # Duplicate ID
    ]
    result = validator.validate_data_points(data)
    assert result.is_valid  # Duplicates are warnings, not errors
    assert result.stats["duplicate_ids"] == 1
    assert any("Duplicate ID" in warning for warning in result.warnings)

def test_preprocess_data(validator, valid_data):
    """Test data preprocessing."""
    values, metadata = validator.preprocess_data(valid_data)
    
    assert len(values) == len(valid_data)
    assert all(isinstance(v, float) for v in values)
    assert all(0 <= v <= 1 for v in values)  # Normalized values
    
    assert "preprocessing_steps" in metadata
    assert "original_stats" in metadata
    assert "processed_stats" in metadata
    assert len(metadata["original_ids"]) == len(valid_data)

def test_preprocess_with_outliers(validator):
    """Test preprocessing with outliers."""
    data = [
        {"id": i, "value": float(i)}
        for i in range(10)
    ]
    # Add outliers
    data.append({"id": 10, "value": 1000.0})
    data.append({"id": 11, "value": -1000.0})
    
    values, metadata = validator.preprocess_data(data)
    assert metadata["outliers_clipped"] == 2
    assert all(0 <= v <= 1 for v in values)

def test_preprocess_with_missing_values(validator):
    """Test preprocessing with missing values."""
    data = [
        {"id": 0, "value": 1.0},
        {"id": 1},  # Missing value
        {"id": 2, "value": float("inf")},  # Invalid value
        {"id": 3, "value": 2.0}
    ]
    
    values, metadata = validator.preprocess_data(data)
    assert metadata["missing_replaced"] == 2
    assert len(values) == len(data)
    assert all(np.isfinite(v) for v in values)

def test_validate_operation():
    """Test operation validation."""
    supported_ops = ["mean", "sum", "max"]
    
    # Valid operation
    is_valid, error = validate_operation("mean", supported_ops)
    assert is_valid
    assert error is None
    
    # Invalid operation
    is_valid, error = validate_operation("invalid_op", supported_ops)
    assert not is_valid
    assert "Unsupported operation" in error
    
    # Empty operation
    is_valid, error = validate_operation("", supported_ops)
    assert not is_valid
    assert "cannot be empty" in error

def test_validate_gpu_config():
    """Test GPU configuration validation."""
    # GPU disabled
    is_valid, error = validate_gpu_config(False)
    assert is_valid
    assert error is None
    
    # GPU enabled (result depends on hardware)
    is_valid, error = validate_gpu_config(True)
    if np.cuda.is_available():
        assert is_valid
        assert error is None
    else:
        assert not is_valid
        assert "GPU requested but not available" in error 