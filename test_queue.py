import asyncio
from message_queue import Message, MessageQueue
from datetime import datetime

async def test_handler(message):
    print(f'Processing message: {message.payload}')
    if message.id == '2':  # Simulate failure for message 2
        raise Exception('Simulated failure')
    await asyncio.sleep(0.5)

async def main():
    queue = MessageQueue()
    
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
        print(f'Messages in queue: {len(queue.queue)}')
        print(f'Messages being processed: {len(queue.processing)}')
        print(f'Messages in dead letter queue: {len(queue.dead_letter)}')

if __name__ == "__main__":
    asyncio.run(main()) 