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