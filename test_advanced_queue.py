import asyncio
import json
from datetime import datetime
import pytest
from redis_message_queue import Message, RedisMessageQueue
import os
from typing import Dict, Any, List
import aiohttp
import random

# Get Redis URL from environment or use default
REDIS_URL = os.getenv("KV_URL", "redis://localhost")

class MessageProcessor:
    def __init__(self):
        self.webhook_enabled = False
        self.webhook_url = "http://localhost:8000/webhook"
        
    async def analyze_sentiment(self, text: str) -> float:
        # Simulate sentiment analysis
        return random.random()
        
    async def calculate_priority(self, message: Dict[str, Any]) -> float:
        # Simulate priority calculation
        return random.random()
        
    async def categorize_message(self, text: str) -> str:
        categories = ["INQUIRY", "FEEDBACK", "SUPPORT", "GENERAL"]
        return random.choice(categories)
        
    async def process_message(self, message: Message) -> Dict[str, Any]:
        if isinstance(message.payload, dict) and 'text' in message.payload:
            text = message.payload['text']
            
            # Enrich message with analysis
            result = {
                'id': message.id,
                'text': text,
                'timestamp': message.timestamp.isoformat(),
                'sentiment': await self.analyze_sentiment(text),
                'priority': await self.calculate_priority(message.payload),
                'category': await self.categorize_message(text)
            }
            
            # Send to webhook if enabled
            if self.webhook_enabled:
                try:
                    async with aiohttp.ClientSession() as session:
                        await session.post(
                            self.webhook_url,
                            json=result
                        )
                except Exception as e:
                    print(f"Webhook delivery failed: {e}")
                    
            return result
        return message.payload

class BatchProcessor:
    def __init__(self, queue: RedisMessageQueue):
        self.queue = queue
        self.processed: List[Message] = []
        self.failed: List[Message] = []
        self.retried: Dict[str, int] = {}  # Track retry counts
        self.processing_complete = asyncio.Event()
        
    async def process_batch(self, handler, batch_size: int, timeout: int = 10):
        try:
            async def process_with_tracking(message: Message):
                try:
                    # Track retries
                    if message.id not in self.retried:
                        self.retried[message.id] = 0
                    
                    await handler(message)
                    self.processed.append(message)
                except Exception as e:
                    self.retried[message.id] += 1
                    if self.retried[message.id] >= message.max_retries:
                        self.failed.append(message)
                    raise
                
                # Check if batch is complete
                total_processed = len(self.processed) + len(self.failed)
                if total_processed >= batch_size:
                    # Verify all messages are either processed or failed max times
                    all_complete = True
                    for msg_id, retry_count in self.retried.items():
                        if retry_count < 3 and msg_id not in [m.id for m in self.processed]:
                            all_complete = False
                            break
                    
                    if all_complete:
                        self.processing_complete.set()
            
            # Start processing
            processor_task = asyncio.create_task(
                self.queue.process_messages(process_with_tracking)
            )
            
            # Wait for completion or timeout
            try:
                await asyncio.wait_for(
                    self.processing_complete.wait(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                print("Batch processing timed out")
            
            # Cancel processor if still running
            if not processor_task.done():
                processor_task.cancel()
                try:
                    await processor_task
                except asyncio.CancelledError:
                    pass
                    
        except Exception as e:
            print(f"Batch processing error: {e}")
            
        return {
            'processed': self.processed,
            'failed': self.failed,
            'retry_counts': self.retried
        }

async def test_message_enrichment():
    queue = RedisMessageQueue(redis_url=REDIS_URL)
    processor = MessageProcessor()
    await queue.cleanup()
    
    # Test messages with different characteristics
    test_messages = [
        {
            'id': '1',
            'text': 'I love this product!',
            'user_id': 'user1'
        },
        {
            'id': '2',
            'text': 'Having issues with login',
            'user_id': 'user2'
        },
        {
            'id': '3',
            'text': 'Can someone help me?',
            'user_id': 'user3'
        }
    ]
    
    # Enqueue messages
    for msg_data in test_messages:
        message = Message(
            id=msg_data['id'],
            payload=msg_data,
            timestamp=datetime.now()
        )
        await queue.enqueue(message)
    
    # Process messages
    processed_messages = []
    
    async def test_handler(message: Message):
        result = await processor.process_message(message)
        processed_messages.append(result)
        
    try:
        await asyncio.wait_for(
            queue.process_messages(test_handler),
            timeout=5
        )
    except asyncio.TimeoutError:
        pass
        
    # Verify processing results
    assert len(processed_messages) == len(test_messages)
    for msg in processed_messages:
        assert 'sentiment' in msg
        assert 'priority' in msg
        assert 'category' in msg
        assert isinstance(msg['sentiment'], float)
        assert isinstance(msg['priority'], float)
        assert msg['category'] in ["INQUIRY", "FEEDBACK", "SUPPORT", "GENERAL"]
    
    await queue.cleanup()

async def test_batch_processing():
    queue = RedisMessageQueue(redis_url=REDIS_URL)
    await queue.cleanup()
    
    # Generate batch of messages
    batch_size = 10
    messages = []
    
    for i in range(batch_size):
        priority = random.random()
        msg = Message(
            id=str(i),
            payload={
                'text': f'Test message {i}',
                'priority': priority
            },
            timestamp=datetime.now()
        )
        messages.append(msg)
        await queue.enqueue(msg)
    
    # Process batch
    batch_processor = BatchProcessor(queue)
    
    async def batch_handler(message: Message):
        if message.payload['priority'] < 0.5:
            raise Exception("Low priority message failure simulation")
        await asyncio.sleep(0.1)  # Simulate processing time
    
    results = await batch_processor.process_batch(
        batch_handler,
        batch_size=batch_size
    )
    
    # Wait for any remaining retries
    await asyncio.sleep(1)
    
    # Verify results
    stats = await queue.get_queue_stats()
    total_handled = len(results['processed']) + len(results['failed'])
    
    print(f"\nBatch Processing Results:")
    print(f"Successfully processed: {len(results['processed'])}")
    print(f"Failed messages: {len(results['failed'])}")
    print(f"Retry counts: {results['retry_counts']}")
    print(f"Queue stats: {stats}")
    
    assert total_handled == batch_size, f"Expected {batch_size} messages handled, got {total_handled}"
    assert stats['queue'] == 0, "Queue should be empty after processing"
    assert stats['processing'] == 0, "No messages should be in processing"
    assert stats['dead_letter'] == len(results['failed']), "Failed messages should be in dead letter queue"
    
    await queue.cleanup()

async def test_webhook_integration():
    queue = RedisMessageQueue(redis_url=REDIS_URL)
    processor = MessageProcessor()
    processor.webhook_enabled = True
    await queue.cleanup()
    
    # Test message
    message = Message(
        id='webhook_test',
        payload={
            'text': 'Test webhook integration',
            'user_id': 'test_user'
        },
        timestamp=datetime.now()
    )
    
    await queue.enqueue(message)
    
    # Process message
    webhook_called = False
    
    async def webhook_handler(message: Message):
        nonlocal webhook_called
        result = await processor.process_message(message)
        webhook_called = True
        return result
    
    try:
        await asyncio.wait_for(
            queue.process_messages(webhook_handler),
            timeout=5
        )
    except asyncio.TimeoutError:
        pass
    
    assert webhook_called
    await queue.cleanup()

if __name__ == "__main__":
    print("\nRunning Message Enrichment Test...")
    asyncio.run(test_message_enrichment())
    
    print("\nRunning Batch Processing Test...")
    asyncio.run(test_batch_processing())
    
    print("\nRunning Webhook Integration Test...")
    asyncio.run(test_webhook_integration())
    
    print("\nAll tests completed successfully!") 