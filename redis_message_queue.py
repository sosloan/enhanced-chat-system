import asyncio
import json
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
from redis import asyncio as aioredis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Message:
    id: str
    payload: Dict[str, Any]
    timestamp: datetime
    retries: int = 0
    max_retries: int = 3
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        data = json.loads(json_str)
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)
    
    def to_json(self) -> str:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return json.dumps(data)

class RedisMessageQueue:
    def __init__(self, redis_url: str = "redis://localhost"):
        self.redis = aioredis.from_url(redis_url, decode_responses=True)
        self.queue_key = "message_queue"
        self.processing_key = "processing_queue"
        self.dead_letter_key = "dead_letter_queue"
        
    async def enqueue(self, message: Message):
        logger.info(f"Enqueuing message {message.id}")
        await self.redis.rpush(self.queue_key, message.to_json())
        
    async def dequeue(self) -> Optional[Message]:
        message_json = await self.redis.lpop(self.queue_key)
        if not message_json:
            return None
            
        message = Message.from_json(message_json)
        await self.redis.hset(self.processing_key, message.id, message_json)
        return message
        
    async def ack(self, message_id: str):
        if await self.redis.hdel(self.processing_key, message_id) > 0:
            logger.info(f"Message {message_id} processed successfully")
            
    async def nack(self, message_id: str):
        message_json = await self.redis.hget(self.processing_key, message_id)
        if message_json:
            message = Message.from_json(message_json)
            message.retries += 1
            
            if message.retries >= message.max_retries:
                logger.warning(f"Message {message_id} exceeded retry limit")
                await self.redis.rpush(self.dead_letter_key, message.to_json())
            else:
                logger.info(f"Requeueing message {message_id}")
                await self.redis.rpush(self.queue_key, message.to_json())
                
            await self.redis.hdel(self.processing_key, message_id)
            
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
                
    async def get_queue_stats(self) -> Dict[str, int]:
        return {
            "queue": await self.redis.llen(self.queue_key),
            "processing": await self.redis.hlen(self.processing_key),
            "dead_letter": await self.redis.llen(self.dead_letter_key)
        }
        
    async def cleanup(self):
        await self.redis.delete(self.queue_key, self.processing_key, self.dead_letter_key)
        await self.redis.close()

# Example usage
async def example_handler(message: Message):
    logger.info(f"Processing message: {message.payload}")
    await asyncio.sleep(1)  # Simulate work
    
async def main():
    queue = RedisMessageQueue()
    await queue.cleanup()  # Start fresh
    
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