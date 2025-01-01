"""Configuration module."""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """Application settings."""
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    DEBUG: bool = False
    RELOAD: bool = False
    
    # API settings
    API_VERSION: str = "1.0.0"
    API_TITLE: str = "GPU Analytics Platform"
    API_DESCRIPTION: str = "High-performance analytics with GPU acceleration"
    API_PREFIX: str = "/api"
    
    # Cache settings
    CACHE_MAX_SIZE: int = 10000
    CACHE_TTL: int = 3600  # 1 hour
    CACHE_CLEANUP_INTERVAL: int = 300  # 5 minutes
    CACHE_COMPRESSION_THRESHOLD: int = 1024 * 1024  # 1MB
    
    # GPU settings
    GPU_ENABLED: bool = True
    GPU_MEMORY_FRACTION: float = 0.8
    GPU_ALLOW_GROWTH: bool = True
    
    # Error handling settings
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0
    EXPONENTIAL_BACKOFF: bool = True
    
    # Monitoring settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    METRICS_ENABLED: bool = True
    METRICS_INTERVAL: int = 60  # 1 minute
    
    # Security settings
    CORS_ORIGINS: list = ["*"]
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = True

@dataclass
class GPUConfig:
    """GPU configuration."""
    enabled: bool
    memory_fraction: float
    allow_growth: bool
    
    def apply(self):
        """Apply GPU configuration."""
        if self.enabled:
            try:
                import torch
                if torch.cuda.is_available():
                    # Set memory fraction
                    torch.cuda.set_per_process_memory_fraction(
                        self.memory_fraction
                    )
                    
                    # Allow memory growth
                    if self.allow_growth:
                        torch.cuda.empty_cache()
                        
                    return True
            except Exception as e:
                print(f"Error configuring GPU: {e}")
        return False

@dataclass
class CacheConfig:
    """Cache configuration."""
    max_size: int
    ttl: int
    cleanup_interval: int
    compression_threshold: int

@dataclass
class MonitoringConfig:
    """Monitoring configuration."""
    metrics_enabled: bool
    metrics_interval: int
    log_level: str
    log_format: str

@dataclass
class SecurityConfig:
    """Security configuration."""
    cors_origins: list
    cors_methods: list
    cors_headers: list

class Config:
    """Application configuration."""
    
    def __init__(self, settings: Optional[Settings] = None):
        """Initialize configuration."""
        self.settings = settings or Settings()
        
        # Initialize components
        self.gpu = GPUConfig(
            enabled=self.settings.GPU_ENABLED,
            memory_fraction=self.settings.GPU_MEMORY_FRACTION,
            allow_growth=self.settings.GPU_ALLOW_GROWTH
        )
        
        self.cache = CacheConfig(
            max_size=self.settings.CACHE_MAX_SIZE,
            ttl=self.settings.CACHE_TTL,
            cleanup_interval=self.settings.CACHE_CLEANUP_INTERVAL,
            compression_threshold=self.settings.CACHE_COMPRESSION_THRESHOLD
        )
        
        self.monitoring = MonitoringConfig(
            metrics_enabled=self.settings.METRICS_ENABLED,
            metrics_interval=self.settings.METRICS_INTERVAL,
            log_level=self.settings.LOG_LEVEL,
            log_format=self.settings.LOG_FORMAT
        )
        
        self.security = SecurityConfig(
            cors_origins=self.settings.CORS_ORIGINS,
            cors_methods=self.settings.CORS_METHODS,
            cors_headers=self.settings.CORS_HEADERS
        )
    
    def configure_logging(self):
        """Configure logging."""
        import logging
        
        logging.basicConfig(
            level=getattr(logging, self.monitoring.log_level),
            format=self.monitoring.log_format
        )
    
    def configure_gpu(self) -> bool:
        """Configure GPU settings."""
        return self.gpu.apply()
    
    def get_api_settings(self) -> Dict[str, Any]:
        """Get API settings."""
        return {
            "title": self.settings.API_TITLE,
            "description": self.settings.API_DESCRIPTION,
            "version": self.settings.API_VERSION,
            "prefix": self.settings.API_PREFIX
        }
    
    def get_server_settings(self) -> Dict[str, Any]:
        """Get server settings."""
        return {
            "host": self.settings.HOST,
            "port": self.settings.PORT,
            "workers": self.settings.WORKERS,
            "reload": self.settings.RELOAD,
            "debug": self.settings.DEBUG
        }
    
    @classmethod
    def from_env(cls, env_file: str = ".env") -> "Config":
        """Create configuration from environment file."""
        settings = Settings(_env_file=env_file)
        return cls(settings)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "gpu": {
                "enabled": self.gpu.enabled,
                "memory_fraction": self.gpu.memory_fraction,
                "allow_growth": self.gpu.allow_growth
            },
            "cache": {
                "max_size": self.cache.max_size,
                "ttl": self.cache.ttl,
                "cleanup_interval": self.cache.cleanup_interval,
                "compression_threshold": self.cache.compression_threshold
            },
            "monitoring": {
                "metrics_enabled": self.monitoring.metrics_enabled,
                "metrics_interval": self.monitoring.metrics_interval,
                "log_level": self.monitoring.log_level,
                "log_format": self.monitoring.log_format
            },
            "security": {
                "cors_origins": self.security.cors_origins,
                "cors_methods": self.security.cors_methods,
                "cors_headers": self.security.cors_headers
            }
        } 