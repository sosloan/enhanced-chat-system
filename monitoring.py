import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict
from dataclasses import dataclass
from collections import deque

@dataclass
class SystemMetrics:
    quality: List[float]
    reliability: List[float]
    throughput: List[float]
    error_rate: List[float]
    
class MetricsVisualizer:
    def __init__(self, history_size: int = 100):
        self.history_size = history_size
        self.metrics_history = {
            'quality': deque(maxlen=history_size),
            'reliability': deque(maxlen=history_size),
            'throughput': deque(maxlen=history_size),
            'error_rate': deque(maxlen=history_size)
        }
        
    def update_metrics(self, metrics: Dict[str, float]):
        for key, value in metrics.items():
            if key in self.metrics_history:
                self.metrics_history[key].append(value)
                
    def plot_metrics(self, save_path: str = 'system_metrics.png'):
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        
        x = range(len(self.metrics_history['quality']))
        
        # Quality trend
        ax1.plot(x, list(self.metrics_history['quality']), 'b-', label='Quality')
        ax1.set_title('Processing Quality')
        ax1.set_ylim(0, 1)
        ax1.grid(True)
        
        # Reliability trend
        ax2.plot(x, list(self.metrics_history['reliability']), 'g-', label='Reliability')
        ax2.set_title('System Reliability')
        ax2.set_ylim(0, 1)
        ax2.grid(True)
        
        # Throughput trend
        ax3.plot(x, list(self.metrics_history['throughput']), 'r-', label='Throughput')
        ax3.set_title('Processing Throughput')
        ax3.set_ylim(0, 1)
        ax3.grid(True)
        
        # Error rate trend
        ax4.plot(x, list(self.metrics_history['error_rate']), 'm-', label='Error Rate')
        ax4.set_title('Error Rate')
        ax4.set_ylim(0, 1)
        ax4.grid(True)
        
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()
        
    def generate_report(self) -> str:
        report = []
        report.append("System Performance Report")
        report.append("=" * 25)
        
        for metric, values in self.metrics_history.items():
            if values:
                avg = sum(values) / len(values)
                min_val = min(values)
                max_val = max(values)
                
                report.append(f"\n{metric.title()}")
                report.append(f"Average: {avg:.3f}")
                report.append(f"Min: {min_val:.3f}")
                report.append(f"Max: {max_val:.3f}")
                
        return "\n".join(report)
        
    def analyze_trends(self) -> List[str]:
        insights = []
        
        if len(self.metrics_history['quality']) > 1:
            quality_trend = list(self.metrics_history['quality'])
            reliability_trend = list(self.metrics_history['reliability'])
            throughput_trend = list(self.metrics_history['throughput'])
            
            # Analyze quality trend
            if quality_trend[-1] > quality_trend[0]:
                insights.append("Quality showing positive trend")
            elif quality_trend[-1] < quality_trend[0]:
                insights.append("Quality needs attention")
                
            # Analyze reliability trend
            if reliability_trend[-1] > reliability_trend[0]:
                insights.append("Reliability improving")
            elif reliability_trend[-1] < reliability_trend[0]:
                insights.append("Reliability degrading")
                
            # Analyze throughput trend
            if throughput_trend[-1] > throughput_trend[0]:
                insights.append("Throughput increasing")
            elif throughput_trend[-1] < throughput_trend[0]:
                insights.append("Throughput decreasing")
                
        return insights 