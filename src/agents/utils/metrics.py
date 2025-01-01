"""Utility functions for metrics collection"""
import time
from typing import Dict

def calculate_uptime(start_time: float) -> float:
    """Calculate system uptime"""
    return time.time() - start_time

def format_metrics(metrics: Dict) -> Dict:
    """Format metrics for output"""
    return {
        'status': 'success',
        'uptime': calculate_uptime(metrics['start_time']),
        'metrics': metrics
    }