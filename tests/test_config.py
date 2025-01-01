"""Tests for configuration module."""

import pytest
import os
import logging
from src.config import (
    Settings,
    Config,
    GPUConfig,
    CacheConfig,
    MonitoringConfig,
    SecurityConfig
)

@pytest.fixture
def settings():
    """Create test settings."""
    return Settings()

@pytest.fixture
def config(settings):
    """Create test configuration."""
    return Config(settings)

def test_settings_defaults(settings):
    """Test default settings values."""
    assert settings.HOST == "0.0.0.0"
    assert settings.PORT == 8000
    assert settings.WORKERS == 1
    assert not settings.DEBUG
    assert not settings.RELOAD
    
    assert settings.API_VERSION == "1.0.0"
    assert settings.API_TITLE == "GPU Analytics Platform"
    assert settings.API_PREFIX == "/api"
    
    assert settings.CACHE_MAX_SIZE == 10000
    assert settings.CACHE_TTL == 3600
    assert settings.CACHE_CLEANUP_INTERVAL == 300
    
    assert settings.GPU_ENABLED
    assert settings.GPU_MEMORY_FRACTION == 0.8
    assert settings.GPU_ALLOW_GROWTH
    
    assert settings.LOG_LEVEL == "INFO"
    assert settings.METRICS_ENABLED
    assert settings.METRICS_INTERVAL == 60

def test_settings_from_env():
    """Test loading settings from environment."""
    # Set test environment variables
    os.environ["HOST"] = "localhost"
    os.environ["PORT"] = "9000"
    os.environ["DEBUG"] = "true"
    
    settings = Settings()
    assert settings.HOST == "localhost"
    assert settings.PORT == 9000
    assert settings.DEBUG
    
    # Clean up
    del os.environ["HOST"]
    del os.environ["PORT"]
    del os.environ["DEBUG"]

def test_gpu_config():
    """Test GPU configuration."""
    config = GPUConfig(
        enabled=True,
        memory_fraction=0.8,
        allow_growth=True
    )
    
    assert config.enabled
    assert config.memory_fraction == 0.8
    assert config.allow_growth
    
    # Test GPU configuration application
    success = config.apply()
    import torch
    assert success == torch.cuda.is_available()

def test_cache_config():
    """Test cache configuration."""
    config = CacheConfig(
        max_size=1000,
        ttl=3600,
        cleanup_interval=300,
        compression_threshold=1024 * 1024
    )
    
    assert config.max_size == 1000
    assert config.ttl == 3600
    assert config.cleanup_interval == 300
    assert config.compression_threshold == 1024 * 1024

def test_monitoring_config():
    """Test monitoring configuration."""
    config = MonitoringConfig(
        metrics_enabled=True,
        metrics_interval=60,
        log_level="INFO",
        log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    assert config.metrics_enabled
    assert config.metrics_interval == 60
    assert config.log_level == "INFO"
    assert "%(asctime)s" in config.log_format

def test_security_config():
    """Test security configuration."""
    config = SecurityConfig(
        cors_origins=["*"],
        cors_methods=["*"],
        cors_headers=["*"]
    )
    
    assert config.cors_origins == ["*"]
    assert config.cors_methods == ["*"]
    assert config.cors_headers == ["*"]

def test_config_initialization(config):
    """Test configuration initialization."""
    assert isinstance(config.gpu, GPUConfig)
    assert isinstance(config.cache, CacheConfig)
    assert isinstance(config.monitoring, MonitoringConfig)
    assert isinstance(config.security, SecurityConfig)

def test_config_logging(config):
    """Test logging configuration."""
    # Configure logging
    config.configure_logging()
    
    # Get root logger
    root_logger = logging.getLogger()
    
    # Check log level
    assert root_logger.level == getattr(logging, config.monitoring.log_level)
    
    # Check handler format
    handler = root_logger.handlers[0]
    assert isinstance(handler, logging.StreamHandler)
    assert handler.formatter._fmt == config.monitoring.log_format

def test_config_gpu(config):
    """Test GPU configuration."""
    success = config.configure_gpu()
    import torch
    assert success == (torch.cuda.is_available() and config.gpu.enabled)

def test_api_settings(config):
    """Test API settings."""
    settings = config.get_api_settings()
    
    assert settings["title"] == config.settings.API_TITLE
    assert settings["description"] == config.settings.API_DESCRIPTION
    assert settings["version"] == config.settings.API_VERSION
    assert settings["prefix"] == config.settings.API_PREFIX

def test_server_settings(config):
    """Test server settings."""
    settings = config.get_server_settings()
    
    assert settings["host"] == config.settings.HOST
    assert settings["port"] == config.settings.PORT
    assert settings["workers"] == config.settings.WORKERS
    assert settings["reload"] == config.settings.RELOAD
    assert settings["debug"] == config.settings.DEBUG

def test_config_from_env():
    """Test configuration from environment file."""
    # Create temporary .env file
    with open(".env.test", "w") as f:
        f.write("HOST=localhost\n")
        f.write("PORT=9000\n")
        f.write("DEBUG=true\n")
    
    # Load config from env file
    config = Config.from_env(".env.test")
    
    assert config.settings.HOST == "localhost"
    assert config.settings.PORT == 9000
    assert config.settings.DEBUG
    
    # Clean up
    os.remove(".env.test")

def test_config_to_dict(config):
    """Test configuration serialization."""
    data = config.to_dict()
    
    assert "gpu" in data
    assert "cache" in data
    assert "monitoring" in data
    assert "security" in data
    
    assert data["gpu"]["enabled"] == config.gpu.enabled
    assert data["cache"]["max_size"] == config.cache.max_size
    assert data["monitoring"]["metrics_enabled"] == config.monitoring.metrics_enabled
    assert data["security"]["cors_origins"] == config.security.cors_origins

def test_config_validation():
    """Test configuration validation."""
    # Test invalid GPU memory fraction
    with pytest.raises(ValueError):
        GPUConfig(enabled=True, memory_fraction=1.5, allow_growth=True)
    
    # Test invalid cache size
    with pytest.raises(ValueError):
        CacheConfig(max_size=-1, ttl=3600, cleanup_interval=300, compression_threshold=1024)
    
    # Test invalid log level
    with pytest.raises(ValueError):
        MonitoringConfig(
            metrics_enabled=True,
            metrics_interval=60,
            log_level="INVALID",
            log_format=""
        ) 