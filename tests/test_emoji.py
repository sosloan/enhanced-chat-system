"""Tests for emoji utilities."""

import pytest
from src.utils.emoji import (
    get_emoji,
    format_with_emoji,
    get_status_emoji,
    get_quality_indicator,
    TEST_STATUS,
    CODE_GEN,
    PROCESSING,
    AI_ML,
    DEV,
    FILES,
    SYSTEM,
    PROGRESS,
    QUALITY,
)

def test_emoji_dictionaries():
    """Test that all emoji dictionaries are properly structured."""
    dictionaries = [
        TEST_STATUS,
        CODE_GEN,
        PROCESSING,
        AI_ML,
        DEV,
        FILES,
        SYSTEM,
        PROGRESS,
        QUALITY,
    ]
    
    for d in dictionaries:
        assert isinstance(d, dict)
        assert len(d) > 0
        assert all(isinstance(k, str) for k in d.keys())
        assert all(isinstance(v, str) for v in d.values())
        assert all(len(v) > 0 for v in d.values())

def test_get_emoji():
    """Test emoji retrieval functionality."""
    # Test valid category and key
    assert get_emoji('test', 'pass') == '✅'
    assert get_emoji('code', 'success') == '🎉'
    assert get_emoji('ai', 'model') == '🤖'
    
    # Test invalid category
    assert get_emoji('invalid', 'key') == '❓'
    
    # Test invalid key with valid category
    assert get_emoji('test', 'invalid') == '❓'
    
    # Test custom default
    assert get_emoji('invalid', 'key', '🔵') == '🔵'

def test_format_with_emoji():
    """Test text formatting with emoji."""
    # Test valid formatting
    assert format_with_emoji('Test passed', 'test', 'pass') == '✅ Test passed'
    assert format_with_emoji('Building', 'dev', 'build') == '🏗️ Building'
    
    # Test with invalid category/key
    assert format_with_emoji('Unknown', 'invalid', 'key') == '❓ Unknown'

def test_get_status_emoji():
    """Test status emoji selection."""
    # Test success states
    assert get_status_emoji(True) == '✅'
    assert get_status_emoji(False) == '❌'
    
    # Test skip state
    assert get_status_emoji(True, skip=True) == '⏭️'
    assert get_status_emoji(False, skip=True) == '⏭️'
    
    # Test error state
    assert get_status_emoji(True, error=True) == '💥'
    assert get_status_emoji(False, error=True) == '💥'
    
    # Test priority (error over skip)
    assert get_status_emoji(True, skip=True, error=True) == '💥'

def test_get_quality_indicator():
    """Test quality indicator selection."""
    # Test excellent (>=0.9)
    assert get_quality_indicator(1.0) == '🌟'
    assert get_quality_indicator(0.95) == '🌟'
    assert get_quality_indicator(0.9) == '🌟'
    
    # Test good (>=0.7)
    assert get_quality_indicator(0.8) == '👍'
    assert get_quality_indicator(0.7) == '👍'
    
    # Test average (>=0.5)
    assert get_quality_indicator(0.6) == '👌'
    assert get_quality_indicator(0.5) == '👌'
    
    # Test poor (<0.5)
    assert get_quality_indicator(0.4) == '👎'
    assert get_quality_indicator(0.0) == '👎'
    
    # Test boundary conditions
    assert get_quality_indicator(0.89999) == '👍'
    assert get_quality_indicator(0.69999) == '👌'
    assert get_quality_indicator(0.49999) == '👎'

@pytest.mark.parametrize("category,key,expected", [
    ('test', 'pass', '✅'),
    ('code', 'success', '🎉'),
    ('process', 'loading', '⌛'),
    ('ai', 'model', '🤖'),
    ('dev', 'code', '💻'),
    ('file', 'read', '📖'),
    ('system', 'online', '🟢'),
    ('progress', 'start', '🚦'),
    ('quality', 'excellent', '🌟'),
])
def test_emoji_categories(category, key, expected):
    """Test emoji retrieval across all categories."""
    assert get_emoji(category, key) == expected

@pytest.mark.parametrize("score,expected", [
    (1.0, '🌟'),
    (0.95, '🌟'),
    (0.9, '🌟'),
    (0.8, '👍'),
    (0.7, '👍'),
    (0.6, '👌'),
    (0.5, '👌'),
    (0.4, '👎'),
    (0.0, '👎'),
])
def test_quality_scores(score, expected):
    """Test quality indicator mapping for various scores."""
    assert get_quality_indicator(score) == expected 