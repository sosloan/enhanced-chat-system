import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from redis_message_queue import Message, RedisMessageQueue
from smol_loop_core import SmolLoop, SmolState, SmolConfig
from smol_loop_improver import SmolImprover
import random
import logging
import numpy as np
from collections import deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AdvancedMetrics:
    throughput_history: deque
    quality_history: deque
    reliability_history: deque
    improvement_effectiveness: Dict[str, float]
    processing_patterns: Dict[str, List[float]]
    
    @classmethod
    def create(cls, window_size: int = 50):
        return cls(
            throughput_history=deque(maxlen=window_size),
            quality_history=deque(maxlen=window_size),
            reliability_history=deque(maxlen=window_size),
            improvement_effectiveness={},
            processing_patterns={"latency": [], "error_rates": [], "complexity": []}
        )

class AdaptiveOptimizer:
    """Advanced optimization strategies for message processing"""
    
    def __init__(self):
        self.processing_strategies = {
            "parallel": self._parallel_processing_simulation,
            "batched": self._batched_processing_simulation,
            "prioritized": self._priority_based_simulation
        }
        self.current_strategy = "parallel"
        self.strategy_effectiveness = {k: 0.5 for k in self.processing_strategies}
        
    async def _parallel_processing_simulation(self, message: Dict[str, Any]) -> Tuple[float, float, float]:
        """Simulate parallel processing with improved throughput"""
        base_time = random.uniform(0.05, 0.3)  # Faster base processing
        success_rate = random.uniform(0.8, 1.0)  # Higher reliability
        quality = random.uniform(0.7, 1.0)
        return base_time, success_rate, quality
        
    async def _batched_processing_simulation(self, message: Dict[str, Any]) -> Tuple[float, float, float]:
        """Simulate batch processing optimization"""
        base_time = random.uniform(0.1, 0.4)
        success_rate = random.uniform(0.85, 0.95)
        quality = random.uniform(0.75, 0.95)
        return base_time, success_rate, quality
        
    async def _priority_based_simulation(self, message: Dict[str, Any]) -> Tuple[float, float, float]:
        """Simulate priority-based processing"""
        priority = message.get("priority", 0.5)
        base_time = random.uniform(0.1, 0.5) * (1 - priority * 0.3)
        success_rate = random.uniform(0.75, 1.0) * (1 + priority * 0.2)
        quality = random.uniform(0.7, 0.9) * (1 + priority * 0.1)
        return base_time, success_rate, quality
        
    async def optimize_processing(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Apply current best processing strategy"""
        strategy_fn = self.processing_strategies[self.current_strategy]
        processing_time, success_rate, quality = await strategy_fn(message)
        
        return {
            "processing_time": processing_time,
            "success_rate": success_rate,
            "quality_score": quality,
            "strategy_used": self.current_strategy
        }
        
    def update_strategy_effectiveness(self, metrics: Dict[str, float]):
        """Update strategy effectiveness based on results"""
        current_effectiveness = (
            metrics.get("throughput", 0) * 0.4 +
            metrics.get("reliability", 0) * 0.3 +
            metrics.get("quality", 0) * 0.3
        )
        self.strategy_effectiveness[self.current_strategy] = (
            0.8 * self.strategy_effectiveness[self.current_strategy] +
            0.2 * current_effectiveness
        )
        
    def select_best_strategy(self):
        """Select the most effective processing strategy"""
        self.current_strategy = max(
            self.strategy_effectiveness.items(),
            key=lambda x: x[1]
        )[0]

class AdvancedSmolLoop(SmolLoop):
    def __init__(self, queue: RedisMessageQueue, config: SmolConfig):
        super().__init__(config)
        self.queue = queue
        self.improver = SmolImprover()
        self.optimizer = AdaptiveOptimizer()
        self.advanced_metrics = AdvancedMetrics.create()
        self.current_state = SmolState(
            iteration=0,
            metrics={
                "throughput": 0.5,
                "reliability": 0.5,
                "quality": 0.5,
                "optimization_score": 0.5
            },
            improvements=[],
            code_version="2.0.0"
        )
        
    async def process_message_batch(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """Process a batch of messages with advanced optimization"""
        results = []
        
        for message in messages:
            try:
                # Apply current improvements
                enhanced_payload = await self.improver.enhance_processing(
                    message.payload,
                    self.current_state.improvements
                )
                
                # Apply optimization strategy
                optimization_result = await self.optimizer.optimize_processing(enhanced_payload)
                
                # Process message
                result = {
                    "message_id": message.id,
                    "processed_payload": enhanced_payload,
                    "metrics": optimization_result
                }
                
                # Track success/failure
                if optimization_result["success_rate"] > 0.7:
                    await self.queue.ack(message.id)
                else:
                    await self.queue.nack(message.id)
                    
                results.append(result)
                
            except Exception as e:
                logger.error(f"Processing error for message {message.id}: {e}")
                await self.queue.nack(message.id)
                results.append({
                    "message_id": message.id,
                    "error": str(e),
                    "metrics": {
                        "processing_time": 1.0,
                        "success_rate": 0.0,
                        "quality_score": 0.0
                    }
                })
                
        return results
        
    async def analyze_batch_results(self, results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze batch results with advanced metrics"""
        if not results:
            return {}
            
        # Calculate base metrics
        processing_times = [r["metrics"]["processing_time"] for r in results]
        success_rates = [r["metrics"]["success_rate"] for r in results]
        quality_scores = [r["metrics"]["quality_score"] for r in results]
        error_rate = 1.0 - np.mean(success_rates)  # Calculate error rate from success rates
        
        # Calculate advanced metrics
        throughput = 1.0 - np.mean(processing_times)
        reliability = 1.0 - error_rate  # Use error rate for reliability
        quality = np.mean(quality_scores)
        
        # Update historical metrics
        self.advanced_metrics.throughput_history.append(throughput)
        self.advanced_metrics.reliability_history.append(reliability)
        self.advanced_metrics.quality_history.append(quality)
        
        # Calculate trends
        throughput_trend = self._calculate_trend(self.advanced_metrics.throughput_history)
        reliability_trend = self._calculate_trend(self.advanced_metrics.reliability_history)
        quality_trend = self._calculate_trend(self.advanced_metrics.quality_history)
        
        # Calculate optimization score
        optimization_score = (
            throughput * 0.4 +
            reliability * 0.3 +
            quality * 0.3 +
            (throughput_trend + reliability_trend + quality_trend) * 0.1
        )
        
        return {
            "throughput": throughput,
            "reliability": reliability,
            "quality": quality,
            "optimization_score": optimization_score,
            "throughput_trend": throughput_trend,
            "reliability_trend": reliability_trend,
            "quality_trend": quality_trend
        }
        
    def _calculate_trend(self, history: deque) -> float:
        """Calculate trend from metric history"""
        if len(history) < 2:
            return 0.0
        return (sum(1 for i in range(1, len(history)) if history[i] > history[i-1]) / (len(history) - 1)) - 0.5
        
    async def generate_advanced_improvements(self, metrics: Dict[str, float]) -> List[str]:
        """Generate improvements based on advanced metrics analysis"""
        improvements = []
        
        # Analyze metric trends
        if metrics.get("throughput_trend", 0) < 0:
            improvements.append("Implement adaptive load balancing")
        if metrics.get("reliability_trend", 0) < 0:
            improvements.append("Enhance fault tolerance mechanisms")
        if metrics.get("quality_trend", 0) < 0:
            improvements.append("Implement advanced validation patterns")
            
        # Analyze current values
        if metrics.get("throughput", 0) < 0.7:
            improvements.append("Optimize resource utilization")
        if metrics.get("reliability", 0) < 0.8:
            improvements.append("Implement circuit breaker pattern")
        if metrics.get("quality", 0) < 0.75:
            improvements.append("Enhance data consistency checks")
            
        return improvements
        
    async def evolve_batch(self) -> Dict[str, Any]:
        """Process a batch of messages and evolve the system"""
        # Dequeue batch of messages
        messages = []
        for _ in range(self.config.batch_size):
            message = await self.queue.dequeue()
            if not message:
                break
            messages.append(message)
            
        if not messages:
            return {
                "processed": 0,
                "failed": 0,
                "metrics": self.current_state.metrics,  # Return current metrics instead of empty dict
                "improvements": []
            }
            
        # Process batch
        results = await self.process_message_batch(messages)
        
        # Analyze results
        metrics = await self.analyze_batch_results(results)
        
        # Update optimization strategy
        self.optimizer.update_strategy_effectiveness(metrics)
        self.optimizer.select_best_strategy()
        
        # Generate improvements
        improvements = await self.generate_advanced_improvements(metrics)
        
        # Update state with weighted average of new and current metrics
        lr = self.config.learning_rate
        for key in self.current_state.metrics:
            if key in metrics:
                self.current_state.metrics[key] = (
                    (1 - lr) * self.current_state.metrics[key] +
                    lr * metrics[key]
                )
        
        self.current_state.improvements.extend(improvements)
        self.current_state.iteration += 1
        
        processed_count = len([r for r in results if "error" not in r])
        failed_count = len([r for r in results if "error" in r])
        
        return {
            "processed": processed_count,
            "failed": failed_count,
            "metrics": self.current_state.metrics,
            "improvements": improvements
        }

    async def run(self):
        """Run the smol loop evolution process"""
        while (
            self.current_state.iteration < self.config.max_iterations and
            (self.current_state.metrics.get("quality", 0) < self.config.improvement_threshold or
             self.current_state.metrics.get("reliability", 0) < self.config.improvement_threshold)
        ):
            logger.info(f"\nStarting iteration {self.current_state.iteration + 1}")
            
            # Process batch and evolve
            results = await self.evolve_batch()
            
            # Log progress
            logger.info(f"Processed: {results['processed']} messages")
            logger.info(f"Failed: {results['failed']} messages")
            logger.info(f"Current metrics: {results['metrics']}")
            logger.info(f"Current strategy: {self.optimizer.current_strategy}")
            
            if results['improvements']:
                logger.info("New improvements identified:")
                for imp in results['improvements']:
                    logger.info(f"- {imp}")
            
            # Early stopping if we've achieved target metrics
            if (self.current_state.metrics.get("quality", 0) >= self.config.improvement_threshold and
                self.current_state.metrics.get("reliability", 0) >= self.config.improvement_threshold and
                results['processed'] > 0):
                logger.info("Target metrics achieved - stopping early")
                break
        
        return self.current_state

    async def update_metrics(self, insights: List[Dict[str, Any]]):
        """Update system metrics based on processing insights"""
        if not insights:
            return
            
        avg_success_rate = sum(i["analysis"]["success_rate"] for i in insights) / len(insights)
        avg_processing_time = sum(i["analysis"]["processing_time"] for i in insights) / len(insights)
        error_rate = 1.0 - avg_success_rate  # Calculate error rate from success rate
        
        # Update metrics with learning rate
        lr = self.config.learning_rate
        self.current_state.metrics["quality"] = min(1.0, self.current_state.metrics["quality"] + lr * (avg_success_rate - 0.5))
        self.current_state.metrics["efficiency"] = min(1.0, self.current_state.metrics["efficiency"] + lr * (1 - avg_processing_time))
        self.current_state.metrics["reliability"] = min(1.0, self.current_state.metrics["reliability"] + lr * (1 - error_rate))

async def test_advanced_processing():
    # Initialize components
    queue = RedisMessageQueue()
    config = SmolConfig(
        max_iterations=10,  # More iterations for better adaptation
        batch_size=10,
        improvement_threshold=0.9,  # Higher threshold
        learning_rate=0.15  # Faster learning
    )
    loop = AdvancedSmolLoop(queue, config)
    
    await queue.cleanup()  # Start fresh
    
    # Generate diverse test messages
    for i in range(50):  # More messages for better analysis
        complexity = random.uniform(0.2, 0.8)
        priority = random.uniform(0.3, 1.0)
        msg = Message(
            id=str(i),
            payload={
                'content': f'Test message {i}',
                'complexity': complexity,
                'priority': priority,
                'type': random.choice(['event', 'command', 'query', 'notification']),
                'size': random.randint(100, 10000)
            },
            timestamp=datetime.now()
        )
        await queue.enqueue(msg)
    
    # Run evolution loop
    final_state = await loop.run()
    
    # Analyze results
    stats = await queue.get_queue_stats()
    print(f"\nAdvanced Processing Results:")
    print(f"Iterations completed: {final_state.iteration}")
    print(f"Final metrics: {final_state.metrics}")
    print(f"Queue stats: {stats}")
    print(f"\nFinal optimization strategy: {loop.optimizer.current_strategy}")
    print(f"Strategy effectiveness: {loop.optimizer.strategy_effectiveness}")
    print(f"\nSystem improvements identified:")
    for imp in final_state.improvements:
        print(f"- {imp}")
    
    # Calculate improvement effectiveness
    if len(loop.advanced_metrics.throughput_history) >= 3:
        initial_metrics = list(loop.advanced_metrics.throughput_history)[:3]
        final_metrics = list(loop.advanced_metrics.throughput_history)[-3:]
        improvement_percentage = (
            (sum(final_metrics) / len(final_metrics)) /
            (sum(initial_metrics) / len(initial_metrics)) - 1
        ) * 100
        print(f"\nOverall throughput improvement: {improvement_percentage:.1f}%")
    
    # Print trend analysis
    print("\nMetric Trends:")
    for metric_name, history in {
        "Throughput": loop.advanced_metrics.throughput_history,
        "Quality": loop.advanced_metrics.quality_history,
        "Reliability": loop.advanced_metrics.reliability_history
    }.items():
        if len(history) >= 2:
            trend = loop._calculate_trend(history)
            trend_direction = "improving" if trend > 0 else "declining" if trend < 0 else "stable"
            print(f"{metric_name}: {trend_direction} (trend score: {trend:.3f})")
    
    await queue.cleanup()

if __name__ == "__main__":
    print("\nRunning Advanced Smol Loop Test...")
    asyncio.run(test_advanced_processing()) 