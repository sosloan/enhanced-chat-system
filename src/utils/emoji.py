"""Emoji dictionary for test feedback and status indicators."""

from typing import Dict, Any

# Test status emojis
TEST_STATUS = {
    'pass': '✅',
    'fail': '❌',
    'skip': '⏭️',
    'error': '💥',
    'warning': '⚠️',
    'running': '🔄',
    'timeout': '⏰',
    'debug': '🔍',
}

# Code generation emojis
CODE_GEN = {
    'start': '🎯',
    'success': '🎉',
    'error': '💣',
    'improve': '📈',
    'complexity': '🧮',
    'creativity': '🎨',
    'pattern': '🔰',
    'mutation': '🧬',
}

# Processing status emojis
PROCESSING = {
    'loading': '⌛',
    'computing': '🔄',
    'saving': '💾',
    'analyzing': '🔬',
    'optimizing': '⚡',
    'complete': '✨',
    'cached': '📦',
    'error': '🚨',
}

# AI/ML emojis
AI_ML = {
    'model': '🤖',
    'train': '🏋️',
    'evaluate': '📊',
    'predict': '🎯',
    'accuracy': '🎯',
    'dataset': '📚',
    'neural': '🧠',
    'evolve': '🦋',
}

# Development emojis
DEV = {
    'code': '💻',
    'debug': '🐛',
    'fix': '🔧',
    'build': '🏗️',
    'deploy': '🚀',
    'config': '⚙️',
    'docs': '📝',
    'test': '🧪',
}

# File operations emojis
FILES = {
    'read': '📖',
    'write': '✍️',
    'delete': '🗑️',
    'copy': '📋',
    'move': '📦',
    'search': '🔍',
    'compress': '🗜️',
    'encrypt': '🔒',
}

# System status emojis
SYSTEM = {
    'online': '🟢',
    'offline': '🔴',
    'warning': '🟡',
    'error': '🔥',
    'memory': '💾',
    'cpu': '⚡',
    'network': '🌐',
    'security': '🔐',
}

# Progress indicators
PROGRESS = {
    'start': '🚦',
    'step': '👣',
    'milestone': '🏁',
    'blocked': '🚧',
    'review': '👀',
    'approved': '👍',
    'rejected': '👎',
    'pending': '⏳',
}

# Quality indicators
QUALITY = {
    'excellent': '🌟',
    'good': '👍',
    'average': '👌',
    'poor': '👎',
    'bug': '🐞',
    'secure': '🔒',
    'fast': '⚡',
    'slow': '🐌',
}

def get_emoji(category: str, key: str, default: str = '❓') -> str:
    """Get emoji by category and key with fallback."""
    categories = {
        'test': TEST_STATUS,
        'code': CODE_GEN,
        'process': PROCESSING,
        'ai': AI_ML,
        'dev': DEV,
        'file': FILES,
        'system': SYSTEM,
        'progress': PROGRESS,
        'quality': QUALITY,
    }
    
    if category not in categories:
        return default
        
    return categories[category].get(key, default)

def format_with_emoji(text: str, category: str, key: str) -> str:
    """Format text with emoji prefix."""
    emoji = get_emoji(category, key)
    return f"{emoji} {text}"

def get_status_emoji(success: bool, skip: bool = False, error: bool = False) -> str:
    """Get appropriate status emoji based on condition."""
    if skip:
        return TEST_STATUS['skip']
    if error:
        return TEST_STATUS['error']
    return TEST_STATUS['pass'] if success else TEST_STATUS['fail']

def get_quality_indicator(score: float) -> str:
    """Get quality indicator emoji based on score (0-1)."""
    if score >= 0.9:
        return QUALITY['excellent']
    elif score >= 0.7:
        return QUALITY['good']
    elif score >= 0.5:
        return QUALITY['average']
    else:
        return QUALITY['poor'] 