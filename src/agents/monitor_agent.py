"""Monitoring agent implementation"""
from .base_agent import BaseAgent
from .utils.metrics import format_metrics
import time

class MonitorAgent(BaseAgent):
    """Agent for monitoring system metrics"""
    
    def __init__(self):
        super().__init__()
        self.metrics = {}
    
    def handle_start_monitoring(self, _):
        """Start collecting metrics"""
        self.metrics['start_time'] = time.time()
        return {'status': 'Monitoring started'}
    
    def handle_get_metrics(self, _):
        """Return current metrics"""
        if 'start_time' in self.metrics:
            return format_metrics(self.metrics)
        return {'status': 'error', 'message': 'Monitoring not started'}