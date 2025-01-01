import os
from dataclasses import dataclass
from typing import List, Dict, Optional
import json
import time
from datetime import datetime

@dataclass
class CodeState:
    code: str
    metrics: dict
    generation: int

@dataclass 
class AdaptivePlan:
    improvements: List[str]
    expected_metrics: dict

class AdaptiveCodeAgent:
    def __init__(self, concept: str, max_generations: int = 3, quality_threshold: float = 0.8):
        self.concept = concept
        self.max_generations = max_generations
        self.quality_threshold = quality_threshold
        self.current_state = None
        
    def initialize_project(self) -> CodeState:
        initial_code = self._generate_initial_code()
        return CodeState(
            code=initial_code,
            metrics={"quality": 0.5, "coverage": 0.4},
            generation=0
        )

    def _generate_initial_code(self) -> str:
        return """
import asyncio
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Message:
    id: str
    payload: Dict[str, Any]
    timestamp: datetime
    retries: int = 0
    max_retries: int = 3
    
class MessageQueue:
    def __init__(self):
        self.queue: List[Message] = []
        self.processing: Dict[str, Message] = {}
        self.dead_letter: List[Message] = []
        
    async def enqueue(self, message: Message):
        logger.info(f"Enqueuing message {message.id}")
        self.queue.append(message)
        
    async def dequeue(self) -> Optional[Message]:
        if not self.queue:
            return None
        
        message = self.queue.pop(0)
        self.processing[message.id] = message
        return message
        
    async def ack(self, message_id: str):
        if message_id in self.processing:
            logger.info(f"Message {message_id} processed successfully")
            del self.processing[message_id]
            
    async def nack(self, message_id: str):
        if message_id in self.processing:
            message = self.processing[message_id]
            message.retries += 1
            
            if message.retries >= message.max_retries:
                logger.warning(f"Message {message_id} exceeded retry limit")
                self.dead_letter.append(message)
            else:
                logger.info(f"Requeueing message {message_id}")
                self.queue.append(message)
                
            del self.processing[message_id]
            
    async def process_messages(self, handler):
        while True:
            message = await self.dequeue()
            if not message:
                await asyncio.sleep(1)
                continue
                
            try:
                await handler(message)
                await self.ack(message.id)
            except Exception as e:
                logger.error(f"Error processing message {message.id}: {e}")
                await self.nack(message.id)

# Example usage
async def example_handler(message: Message):
    logger.info(f"Processing message: {message.payload}")
    await asyncio.sleep(1)  # Simulate work
    
async def main():
    queue = MessageQueue()
    
    # Producer
    for i in range(5):
        message = Message(
            id=str(i),
            payload={"data": f"test_{i}"},
            timestamp=datetime.now()
        )
        await queue.enqueue(message)
    
    # Consumer
    await queue.process_messages(example_handler)

if __name__ == "__main__":
    asyncio.run(main())
"""

    def generate_improvement_plan(self, current_state: CodeState) -> AdaptivePlan:
        improvements = [
            "Add persistent storage for messages",
            "Implement message prioritization",
            "Add monitoring and metrics",
            "Improve error handling and recovery",
            "Add message validation"
        ]
        return AdaptivePlan(
            improvements=improvements,
            expected_metrics={
                "quality": min(current_state.metrics["quality"] + 0.1, 1.0),
                "coverage": min(current_state.metrics["coverage"] + 0.1, 1.0)
            }
        )

    def evolve_code(self, current_state: CodeState, plan: AdaptivePlan) -> CodeState:
        improved_code = self._apply_improvements(current_state.code, plan.improvements)
        return CodeState(
            code=improved_code,
            metrics=plan.expected_metrics,
            generation=current_state.generation + 1
        )

    def _apply_improvements(self, code: str, improvements: List[str]) -> str:
        # Here we would apply each improvement to the code
        # For this example, we'll just add comments
        improved_code = code
        for improvement in improvements:
            improved_code = f"# TODO: {improvement}\n" + improved_code
        return improved_code

    def validate_code(self, state: CodeState) -> bool:
        try:
            # Basic syntax check
            compile(state.code, '<string>', 'exec')
            return True
        except Exception as e:
            print(f"Code validation failed: {e}")
            return False

    def run(self):
        print(f"Initializing project for concept: {self.concept}")
        self.current_state = self.initialize_project()
        
        while (
            self.current_state.generation < self.max_generations and
            self.current_state.metrics["quality"] < self.quality_threshold
        ):
            print(f"\nGeneration {self.current_state.generation + 1}")
            
            plan = self.generate_improvement_plan(self.current_state)
            print("Improvement plan generated:")
            for improvement in plan.improvements:
                print(f"- {improvement}")
            
            new_state = self.evolve_code(self.current_state, plan)
            print("Code evolved")
            
            if self.validate_code(new_state):
                self.current_state = new_state
                print(f"New metrics: {new_state.metrics}")
            else:
                print("Invalid code generated, keeping previous version")
                break
                
        print("\nFinal code quality:", self.current_state.metrics["quality"])
        print("\nFinal code:")
        print(self.current_state.code)
        return self.current_state

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--concept", required=True)
    parser.add_argument("--max_generations", type=int, default=3)
    args = parser.parse_args()
    
    agent = AdaptiveCodeAgent(args.concept, args.max_generations)
    agent.run() 