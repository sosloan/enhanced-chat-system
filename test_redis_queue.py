import asyncio
from redis_message_queue import Message, RedisMessageQueue
from datetime import datetime
import os

# Get Redis URL from environment or use default
REDIS_URL = os.getenv("KV_URL", "redis://localhost")

async def test_handler(message):
    print(f'Processing message: {message.payload}')
    if message.id == '2':  # Simulate failure for message 2
        raise Exception('Simulated failure')
    await asyncio.sleep(0.5)

async def main():
    queue = RedisMessageQueue(redis_url=REDIS_URL)
    await queue.cleanup()  # Start fresh
    
    # Enqueue test messages
    for i in range(5):
        msg = Message(
            id=str(i),
            payload={'data': f'test_{i}'},
            timestamp=datetime.now()
        )
        await queue.enqueue(msg)
    
    # Process messages with timeout
    try:
        await asyncio.wait_for(queue.process_messages(test_handler), timeout=5)
    except asyncio.TimeoutError:
        print('\nQueue processing stats:')
        stats = await queue.get_queue_stats()
        print(f'Messages in queue: {stats["queue"]}')
        print(f'Messages being processed: {stats["processing"]}')
        print(f'Messages in dead letter queue: {stats["dead_letter"]}')
    
    await queue.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 