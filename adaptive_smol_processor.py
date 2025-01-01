import logging
from collections import deque
from typing import Dict, List, Optional
import random
import time
import asyncio
from dataclasses import dataclass
from monitoring import MetricsVisualizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProcessingMetrics:
    quality: float = 0.0
    reliability: float = 0.0
    throughput: float = 0.0
    chaos_score: float = 0.0
    error_count: int = 0
    recovery_attempts: int = 0
    
class AdaptiveProcessor:
    def __init__(self, history_size: int = 10):
        self.metrics_history = deque(maxlen=history_size)
        self.improvement_history = deque(maxlen=history_size)
        self.chaos_level = 1
        self.error_threshold = 0.2
        self.recovery_timeout = 5.0
        self.backoff_multiplier = 1.5
        self.visualizer = MetricsVisualizer()
        self.processing_window = 0.1
        self.batch_size = 10
        self.concurrent_limit = 5
        
    async def process_message(self, message: str) -> bool:
        try:
            if random.random() < self.error_threshold:
                raise Exception("Simulated processing error")
                
            # Simulate processing with adaptive window
            await asyncio.sleep(self.processing_window)
            return True
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self.handle_error(message)
            return False
            
    async def handle_error(self, message: str) -> None:
        retry_count = 0
        current_timeout = self.recovery_timeout
        
        while retry_count < 3:
            try:
                logger.info(f"Recovery attempt {retry_count + 1} for message: {message}")
                await asyncio.sleep(current_timeout)
                
                if random.random() > self.error_threshold:
                    logger.info(f"Successfully recovered message: {message}")
                    return
                    
                current_timeout *= self.backoff_multiplier
                retry_count += 1
                
            except Exception as e:
                logger.error(f"Recovery failed: {e}")
                
        logger.error(f"Message recovery failed after {retry_count} attempts")
        
    def update_metrics(self, processed: int, failed: int) -> ProcessingMetrics:
        quality = random.uniform(0.6, 0.8)
        reliability = random.uniform(0.7, 0.9)
        throughput = random.uniform(0.15, 0.25)
        error_rate = failed / (processed + failed) if processed + failed > 0 else 0
        
        metrics = ProcessingMetrics(
            quality=quality,
            reliability=reliability,
            throughput=throughput,
            chaos_score=0.0,
            error_count=failed,
            recovery_attempts=failed
        )
        
        self.metrics_history.append(metrics)
        
        # Update visualizer
        self.visualizer.update_metrics({
            'quality': quality,
            'reliability': reliability,
            'throughput': throughput,
            'error_rate': error_rate
        })
        
        # Optimize processing parameters
        self._optimize_processing_params(metrics)
        
        return metrics
        
    def _optimize_processing_params(self, metrics: ProcessingMetrics):
        """Dynamically adjust processing parameters based on performance"""
        # Adjust processing window based on throughput
        if metrics.throughput < 0.2:
            self.processing_window = max(0.05, self.processing_window * 0.9)
        elif metrics.error_count > 2:
            self.processing_window = min(0.2, self.processing_window * 1.1)
            
        # Adjust batch size based on reliability
        if metrics.reliability > 0.85:
            self.batch_size = min(20, self.batch_size + 2)
        elif metrics.reliability < 0.7:
            self.batch_size = max(5, self.batch_size - 2)
            
        # Adjust concurrent limit based on quality
        if metrics.quality > 0.75:
            self.concurrent_limit = min(10, self.concurrent_limit + 1)
        elif metrics.quality < 0.65:
            self.concurrent_limit = max(3, self.concurrent_limit - 1)
        
    def generate_improvements(self, metrics: ProcessingMetrics) -> List[str]:
        improvements = [
            "Enhance processing quality",
            "Improve system reliability", 
            "Optimize processing speed"
        ]
        
        if metrics.error_count > 0:
            improvements.extend([
                "Implement advanced error recovery",
                "Add circuit breaker pattern",
                "Enhance monitoring and alerting"
            ])
            
        if len(self.metrics_history) >= 2:
            prev_metrics = self.metrics_history[-2]
            if metrics.throughput < prev_metrics.throughput:
                improvements.append("Scale processing capacity")
                
        return improvements

    async def process_batch(self, messages: List[str]) -> tuple[int, int]:
        processed = 0
        failed = 0
        
        # Process messages concurrently with limits
        tasks = []
        for i in range(0, len(messages), self.concurrent_limit):
            batch = messages[i:i + self.concurrent_limit]
            batch_tasks = [self.process_message(msg) for msg in batch]
            results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, bool) and result:
                    processed += 1
                else:
                    failed += 1
                
        return processed, failed
        
    def adjust_chaos_level(self, metrics: ProcessingMetrics):
        if metrics.error_count > 3:
            self.chaos_level = max(1, self.chaos_level - 1)
        elif metrics.reliability > 0.9:
            self.chaos_level = min(5, self.chaos_level + 1)
            
async def main():
    processor = AdaptiveProcessor()
    num_messages = 30
    batch_size = 10
    
    # Generate test messages
    messages = [f"message {i}" for i in range(num_messages)]
    
    # Process in batches
    for i in range(5):
        logger.info(f"\nIteration {i+1}")
        logger.info(f"Processing window: {processor.processing_window:.3f}s")
        logger.info(f"Batch size: {processor.batch_size}")
        logger.info(f"Concurrent limit: {processor.concurrent_limit}")
        
        start_idx = i * batch_size
        end_idx = min(start_idx + batch_size, num_messages)
        batch = messages[start_idx:end_idx]
        
        if not batch:
            processed, failed = 0, 0
        else:
            processed, failed = await processor.process_batch(batch)
            
        logger.info(f"Processed: {processed} messages")
        logger.info(f"Failed: {failed} messages")
        
        metrics = processor.update_metrics(processed, failed)
        logger.info(f"Metrics: {metrics.__dict__}")
        
        processor.adjust_chaos_level(metrics)
        logger.info(f"Chaos Level: {processor.chaos_level}")
        
        improvements = processor.generate_improvements(metrics)
        logger.info("New improvements:")
        for imp in improvements:
            logger.info(f"- {imp}")
            
    # Generate visualization and report
    processor.visualizer.plot_metrics()
    logger.info("\nPerformance Report:")
    logger.info(processor.visualizer.generate_report())
    
    logger.info("\nTrend Analysis:")
    for insight in processor.visualizer.analyze_trends():
        logger.info(f"- {insight}")
            
if __name__ == "__main__":
    asyncio.run(main()) 