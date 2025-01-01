import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from redis_message_queue import Message, RedisMessageQueue
from smol_loop_core import SmolLoop, SmolState, SmolConfig
from smol_loop_improver import SmolImprover
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueuedSmolLoop(SmolLoop):
    def __init__(self, queue: RedisMessageQueue, config: SmolConfig):
        super().__init__(config)
        self.queue = queue
        self.improver = SmolImprover()
        self.current_state = SmolState(
            iteration=0,
            metrics={
                "throughput": 0.5,
                "latency": 0.5,
                "reliability": 0.5,
                "quality": 0.5
            },
            improvements=[],
            code_version="1.0.0"
        )
    
    async def process_message(self, message: Message) -> Dict[str, Any]:
        """Process a single message with smol loop improvements"""
        try:
            # Apply current improvements to message processing
            improved_payload = await self.improver.enhance_processing(
                message.payload,
                self.current_state.improvements
            )
            
            # Simulate processing with metrics
            metrics = {
                "processing_time": random.uniform(0.1, 1.0),
                "success_rate": random.uniform(0.7, 1.0) if message.retries == 0 else random.uniform(0.3, 0.7),
                "quality_score": random.uniform(0.5, 1.0)
            }
            
            return {
                "message_id": message.id,
                "processed_payload": improved_payload,
                "metrics": metrics
            }
            
        except Exception as e:
            logger.error(f"Processing error for message {message.id}: {e}")
            return {
                "message_id": message.id,
                "error": str(e),
                "metrics": {
                    "processing_time": 1.0,
                    "success_rate": 0.0,
                    "quality_score": 0.0
                }
            }
    
    async def analyze_batch(self, results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze batch processing results"""
        if not results:
            return {}
            
        # Calculate aggregate metrics
        avg_processing_time = sum(r["metrics"]["processing_time"] for r in results) / len(results)
        avg_success_rate = sum(r["metrics"]["success_rate"] for r in results) / len(results)
        avg_quality = sum(r["metrics"]["quality_score"] for r in results) / len(results)
        
        return {
            "throughput": 1.0 - avg_processing_time,
            "reliability": avg_success_rate,
            "quality": avg_quality
        }
    
    async def improve(self, metrics: Dict[str, float]) -> List[str]:
        """Generate improvements based on metrics"""
        improvements = []
        
        # Analyze metrics and suggest improvements
        if metrics.get("throughput", 0) < 0.7:
            improvements.append("Optimize message processing pipeline")
        if metrics.get("reliability", 0) < 0.8:
            improvements.append("Enhance error handling and retry logic")
        if metrics.get("quality", 0) < 0.75:
            improvements.append("Improve message validation and enrichment")
            
        return improvements
    
    async def evolve_batch(self) -> Dict[str, Any]:
        """Process a batch of messages and evolve the system"""
        batch_results = []
        processed_count = 0
        failed_count = 0
        
        # Process batch of messages
        for _ in range(self.config.batch_size):
            message = await self.queue.dequeue()
            if not message:
                break
                
            result = await self.process_message(message)
            batch_results.append(result)
            
            if "error" not in result:
                await self.queue.ack(message.id)
                processed_count += 1
            else:
                await self.queue.nack(message.id)
                if message.retries >= message.max_retries:
                    failed_count += 1
        
        # Analyze results and improve
        metrics = await self.analyze_batch(batch_results)
        improvements = await self.improve(metrics)
        
        # Update state
        self.current_state.metrics.update(metrics)
        self.current_state.improvements.extend(improvements)
        self.current_state.iteration += 1
        
        return {
            "processed": processed_count,
            "failed": failed_count,
            "metrics": metrics,
            "improvements": improvements
        }
    
    async def run(self):
        """Run the smol loop evolution process"""
        while (
            self.current_state.iteration < self.config.max_iterations and
            self.current_state.metrics["quality"] < self.config.improvement_threshold
        ):
            logger.info(f"\nStarting iteration {self.current_state.iteration + 1}")
            
            # Process batch and evolve
            results = await self.evolve_batch()
            
            # Log progress
            logger.info(f"Processed: {results['processed']} messages")
            logger.info(f"Failed: {results['failed']} messages")
            logger.info(f"Current metrics: {results['metrics']}")
            if results['improvements']:
                logger.info("New improvements identified:")
                for imp in results['improvements']:
                    logger.info(f"- {imp}")
        
        return self.current_state

async def test_queued_smol_loop():
    # Initialize components
    queue = RedisMessageQueue()
    config = SmolConfig(
        max_iterations=5,
        batch_size=10,
        improvement_threshold=0.85,
        learning_rate=0.1
    )
    loop = QueuedSmolLoop(queue, config)
    
    await queue.cleanup()  # Start fresh
    
    # Generate test messages
    for i in range(20):
        msg = Message(
            id=str(i),
            payload={
                'content': f'Test message {i}',
                'complexity': random.random(),
                'priority': random.random(),
                'type': random.choice(['event', 'command', 'query'])
            },
            timestamp=datetime.now()
        )
        await queue.enqueue(msg)
    
    # Run evolution loop
    final_state = await loop.run()
    
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
    print("\nRunning Queued Smol Loop Test...")
    asyncio.run(test_queued_smol_loop()) 