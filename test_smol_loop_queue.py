import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from redis_message_queue import Message, RedisMessageQueue
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LoopState:
    iteration: int
    metrics: Dict[str, float]
    improvements: List[str]
    code_version: str

@dataclass
class LoopConfig:
    max_iterations: int = 5
    improvement_threshold: float = 0.8
    learning_rate: float = 0.1
    batch_size: int = 10

class AdaptiveMessageProcessor:
    def __init__(self, queue: RedisMessageQueue, config: LoopConfig):
        self.queue = queue
        self.config = config
        self.current_state = LoopState(
            iteration=0,
            metrics={"quality": 0.5, "efficiency": 0.5, "reliability": 0.5},
            improvements=[],
            code_version="1.0.0"
        )
        
    async def analyze_message(self, message: Message) -> Dict[str, Any]:
        """Analyze message and extract insights for improvement"""
        if isinstance(message.payload, dict):
            # Simulate analysis metrics
            analysis = {
                "processing_time": random.uniform(0.1, 1.0),
                "complexity": random.uniform(0.2, 0.8),
                "success_rate": random.uniform(0.7, 1.0) if message.retries == 0 else random.uniform(0.3, 0.7)
            }
            
            # Extract patterns and insights
            patterns = {
                "has_error": message.retries > 0,
                "is_complex": analysis["complexity"] > 0.6,
                "is_slow": analysis["processing_time"] > 0.8
            }
            
            return {
                "analysis": analysis,
                "patterns": patterns,
                "message_id": message.id
            }
        return {}

    async def generate_improvements(self, insights: List[Dict[str, Any]]) -> List[str]:
        """Generate improvement suggestions based on analysis insights"""
        improvements = []
        
        # Analyze patterns
        error_rate = sum(1 for i in insights if i["patterns"]["has_error"]) / len(insights)
        complexity_rate = sum(1 for i in insights if i["patterns"]["is_complex"]) / len(insights)
        slowness_rate = sum(1 for i in insights if i["patterns"]["is_slow"]) / len(insights)
        
        # Generate targeted improvements
        if error_rate > 0.3:
            improvements.append(f"Enhance error handling (current error rate: {error_rate:.2%})")
        if complexity_rate > 0.4:
            improvements.append(f"Optimize complex message processing (complexity rate: {complexity_rate:.2%})")
        if slowness_rate > 0.3:
            improvements.append(f"Improve processing speed (slow message rate: {slowness_rate:.2%})")
            
        return improvements

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
        
        # Adjust learning rate based on system performance
        if avg_success_rate > 0.8:
            self.config.learning_rate = min(0.5, self.config.learning_rate * 1.1)
        else:
            self.config.learning_rate = max(0.01, self.config.learning_rate * 0.9)

    async def process_batch(self) -> Dict[str, Any]:
        """Process a batch of messages and evolve the system"""
        insights = []
        processed = []
        failed = []
        
        # Process batch of messages
        for _ in range(self.config.batch_size):
            message = await self.queue.dequeue()
            if not message:
                break
                
            try:
                # Analyze before processing
                insight = await self.analyze_message(message)
                insights.append(insight)
                
                # Simulate processing with adaptive behavior
                if insight["analysis"]["success_rate"] > 0.5:
                    await self.queue.ack(message.id)
                    processed.append(message)
                else:
                    await self.queue.nack(message.id)
                    if message.retries >= message.max_retries:
                        failed.append(message)
                        
            except Exception as e:
                logger.error(f"Processing error: {e}")
                await self.queue.nack(message.id)
                
        # Generate improvements and update metrics
        improvements = await self.generate_improvements(insights)
        await self.update_metrics(insights)
        
        # Update state
        self.current_state.iteration += 1
        self.current_state.improvements.extend(improvements)
        
        return {
            "processed": processed,
            "failed": failed,
            "insights": insights,
            "improvements": improvements,
            "metrics": self.current_state.metrics
        }

    async def evolve(self):
        """Run the evolution loop"""
        best_metrics = self.current_state.metrics.copy()
        iterations_without_improvement = 0
        
        while (
            self.current_state.iteration < self.config.max_iterations and
            (self.current_state.metrics["quality"] < self.config.improvement_threshold or
             iterations_without_improvement < 2)  # Continue if still improving
        ):
            logger.info(f"\nStarting iteration {self.current_state.iteration + 1}")
            
            # Process batch and evolve
            results = await self.process_batch()
            
            # Check for improvements
            current_avg = sum(self.current_state.metrics.values()) / len(self.current_state.metrics)
            best_avg = sum(best_metrics.values()) / len(best_metrics)
            
            if current_avg > best_avg:
                best_metrics = self.current_state.metrics.copy()
                iterations_without_improvement = 0
            else:
                iterations_without_improvement += 1
            
            # Log progress
            logger.info(f"Processed: {len(results['processed'])} messages")
            logger.info(f"Failed: {len(results['failed'])} messages")
            logger.info(f"Current metrics: {self.current_state.metrics}")
            if results['improvements']:
                logger.info("Improvements identified:")
                for imp in results['improvements']:
                    logger.info(f"- {imp}")
                    
        return self.current_state

async def test_adaptive_processing():
    # Initialize queue and processor
    queue = RedisMessageQueue()
    config = LoopConfig(max_iterations=5, batch_size=10)
    processor = AdaptiveMessageProcessor(queue, config)
    
    await queue.cleanup()  # Start fresh
    
    # Generate test messages with varying characteristics
    for i in range(20):
        complexity = random.random()
        msg = Message(
            id=str(i),
            payload={
                'text': f'Test message {i}',
                'complexity': complexity,
                'priority': random.random(),
                'type': random.choice(['event', 'command', 'query'])
            },
            timestamp=datetime.now()
        )
        await queue.enqueue(msg)
    
    # Run evolution loop
    final_state = await processor.evolve()
    
    # Verify results
    stats = await queue.get_queue_stats()
    print(f"\nFinal Results:")
    print(f"Iterations completed: {final_state.iteration}")
    print(f"Final metrics: {final_state.metrics}")
    print(f"Queue stats: {stats}")
    print(f"\nSystem improvements identified:")
    for imp in final_state.improvements:
        print(f"- {imp}")
    
    await queue.cleanup()

if __name__ == "__main__":
    print("\nRunning Adaptive Message Processing Test...")
    asyncio.run(test_adaptive_processing()) 