"""Tests for caching module."""

import pytest
import asyncio
import time
import numpy as np
import torch
from src.lib.caching import (
    CacheConfig,
    CacheEntry,
    AnalyticsCache,
    cached
)

@pytest.fixture
def cache_config():
    """Create test cache configuration."""
    return CacheConfig(
        max_size=10,
        ttl=1.0,  # 1 second for testing
        cleanup_interval=0.1,
        eviction_policy="lru",
        compression_threshold=100  # Small threshold for testing
    )

@pytest.fixture
def cache(cache_config):
    """Create test cache instance."""
    return AnalyticsCache(config=cache_config)

def test_cache_config():
    """Test cache configuration."""
    config = CacheConfig()
    assert config.max_size == 1000
    assert config.ttl == 3600
    assert config.cleanup_interval == 300
    assert config.eviction_policy == "lru"
    assert config.compression_threshold == 1024 * 1024

def test_cache_entry():
    """Test cache entry creation."""
    entry = CacheEntry(
        value="test",
        timestamp=time.time(),
        ttl=60,
        hits=1,
        computation_time=0.1,
        size_bytes=100
    )
    assert entry.value == "test"
    assert entry.hits == 1
    assert entry.computation_time == 0.1
    assert entry.size_bytes == 100

@pytest.mark.asyncio
async def test_cache_basic_operations(cache):
    """Test basic cache operations."""
    # Set value
    await cache.set("key1", "value1")
    assert len(cache.cache) == 1
    
    # Get value
    value = await cache.get("key1")
    assert value == "value1"
    assert cache.get_stats()["hits"] == 1
    
    # Get non-existent value
    value = await cache.get("key2")
    assert value is None
    assert cache.get_stats()["misses"] == 1
    
    # Delete value
    await cache.delete("key1")
    assert len(cache.cache) == 0

@pytest.mark.asyncio
async def test_cache_expiration(cache):
    """Test cache entry expiration."""
    await cache.set("key", "value", ttl=0.1)
    
    # Value should be available immediately
    value = await cache.get("key")
    assert value == "value"
    
    # Wait for expiration
    await asyncio.sleep(0.2)
    
    # Value should be expired
    value = await cache.get("key")
    assert value is None

@pytest.mark.asyncio
async def test_cache_eviction(cache):
    """Test cache eviction."""
    # Fill cache
    for i in range(cache.config.max_size + 1):
        await cache.set(f"key{i}", f"value{i}")
    
    # Cache should not exceed max size
    assert len(cache.cache) == cache.config.max_size
    assert cache.get_stats()["evictions"] > 0

@pytest.mark.asyncio
async def test_cache_cleanup(cache):
    """Test cache cleanup."""
    # Add entries
    await cache.set("key1", "value1", ttl=0.1)
    await cache.set("key2", "value2", ttl=0.2)
    
    # Start cleanup
    cache.start_cleanup()
    
    # Wait for cleanup
    await asyncio.sleep(0.3)
    
    # Entries should be cleaned up
    assert len(cache.cache) == 0
    
    # Stop cleanup
    cache.stop_cleanup()

@pytest.mark.asyncio
async def test_cache_compression(cache):
    """Test value compression."""
    # Create large value
    large_value = "x" * 1000
    
    # Set value (should be compressed)
    await cache.set("key", large_value)
    
    # Get value (should be decompressed)
    value = await cache.get("key")
    assert value == large_value

@pytest.mark.asyncio
async def test_cache_with_numpy_arrays(cache):
    """Test caching numpy arrays."""
    array = np.random.randn(10, 10)
    
    # Cache array
    await cache.set("array", array)
    
    # Retrieve array
    cached_array = await cache.get("array")
    assert np.array_equal(cached_array, array)

@pytest.mark.asyncio
async def test_cache_with_torch_tensors(cache):
    """Test caching PyTorch tensors."""
    tensor = torch.randn(10, 10)
    
    # Cache tensor
    await cache.set("tensor", tensor)
    
    # Retrieve tensor
    cached_tensor = await cache.get("tensor")
    assert torch.equal(cached_tensor, tensor)

@pytest.mark.asyncio
async def test_cached_decorator():
    """Test cached decorator."""
    call_count = 0
    
    @cached(ttl=1.0)
    async def test_func(x):
        nonlocal call_count
        call_count += 1
        return x * 2
    
    # First call should compute
    result1 = await test_func(5)
    assert result1 == 10
    assert call_count == 1
    
    # Second call should use cache
    result2 = await test_func(5)
    assert result2 == 10
    assert call_count == 1
    
    # Different argument should compute
    result3 = await test_func(6)
    assert result3 == 12
    assert call_count == 2

@pytest.mark.asyncio
async def test_cache_stats(cache):
    """Test cache statistics."""
    # Add some entries
    await cache.set("key1", "value1")
    await cache.set("key2", "value2")
    
    # Perform some operations
    await cache.get("key1")
    await cache.get("key1")
    await cache.get("key3")  # Miss
    
    # Check stats
    stats = cache.get_stats()
    assert stats["hits"] == 2
    assert stats["misses"] == 1
    assert stats["size"] == 2
    assert stats["hit_ratio"] == 2/3

@pytest.mark.asyncio
async def test_custom_key_generator():
    """Test cached decorator with custom key generator."""
    def key_generator(*args, **kwargs):
        return f"custom_key_{args[0]}"
    
    @cached(key_generator=key_generator)
    async def test_func(x):
        return x * 2
    
    # Test with custom key
    result = await test_func(5)
    assert result == 10
    assert "custom_key_5" in test_func.cache.cache

@pytest.mark.asyncio
async def test_concurrent_access(cache):
    """Test concurrent cache access."""
    async def access_cache(key, value):
        await cache.set(key, value)
        result = await cache.get(key)
        return result
    
    # Create multiple concurrent operations
    tasks = [
        access_cache(f"key{i}", f"value{i}")
        for i in range(5)
    ]
    
    # Run concurrently
    results = await asyncio.gather(*tasks)
    
    # Verify results
    assert all(results[i] == f"value{i}" for i in range(5))
    assert len(cache.cache) == 5 