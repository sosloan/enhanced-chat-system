import logging
import asyncio
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import random
import numpy as np
from datetime import datetime
from pathlib import Path
import aiofiles
import aiohttp
import json
from contextlib import asynccontextmanager
import psutil
import time

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """System resource metrics"""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    disk_io_read: float = 0.0
    disk_io_write: float = 0.0
    start_time: float = field(default_factory=time.time)

@dataclass
class IOMetrics:
    """Tracks I/O performance metrics"""
    read_latency: float = 0.0
    write_latency: float = 0.0
    throughput: float = 0.0
    buffer_utilization: float = 0.0
    io_errors: int = 0
    total_bytes_read: int = 0
    total_bytes_written: int = 0

@dataclass
class ProcessingState:
    """Represents the current state of the processing system"""
    quality: float = 0.0
    reliability: float = 0.0
    throughput: float = 0.0
    complexity: float = 0.0
    creativity_score: float = 0.0
    adaptation_rate: float = 0.3
    chaos_level: int = 1
    io_metrics: IOMetrics = field(default_factory=IOMetrics)
    system_metrics: SystemMetrics = field(default_factory=SystemMetrics)

class MessageValidator:
    """Validates and transforms messages"""
    @staticmethod
    def validate_structure(message: str) -> bool:
        """Validate message structure"""
        try:
            parts = message.split('_')
            return len(parts) >= 3 and all(part.strip() for part in parts)
        except Exception:
            return False

    @staticmethod
    def validate_content(message: str) -> bool:
        """Validate message content"""
        try:
            return (
                len(message) > 0 and
                len(message) <= 1000 and
                not any(char in message for char in ['<', '>', '$', '#'])
            )
        except Exception:
            return False

    @staticmethod
    def transform_message(message: str, complexity: float) -> str:
        """Transform message based on complexity"""
        try:
            parts = message.split('_')
            if complexity > 0.7:
                # Complex transformation
                return '_'.join([
                    parts[0].upper(),
                    f"COMPLEX_{parts[1]}",
                    f"PRIORITY_{parts[2]}"
                ])
            elif complexity > 0.3:
                # Medium transformation
                return '_'.join([
                    parts[0].capitalize(),
                    f"Medium_{parts[1]}",
                    parts[2]
                ])
            else:
                # Simple transformation
                return '_'.join([
                    parts[0].lower(),
                    parts[1],
                    parts[2]
                ])
        except Exception as e:
            logger.error(f"Transform error: {e}")
            return message

class PerformanceMonitor:
    """Monitors system performance metrics"""
    def __init__(self):
        self.metrics_history = deque(maxlen=1000)
        self.start_time = time.time()

    def get_current_metrics(self) -> SystemMetrics:
        """Get current system metrics"""
        try:
            metrics = SystemMetrics(
                cpu_percent=psutil.cpu_percent(),
                memory_percent=psutil.virtual_memory().percent,
                disk_io_read=psutil.disk_io_counters().read_bytes,
                disk_io_write=psutil.disk_io_counters().write_bytes,
                start_time=self.start_time
            )
            self.metrics_history.append(metrics)
            return metrics
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return SystemMetrics()

    def get_performance_summary(self) -> Dict[str, float]:
        """Get performance summary"""
        if not self.metrics_history:
            return {}

        return {
            'avg_cpu': np.mean([m.cpu_percent for m in self.metrics_history]),
            'avg_memory': np.mean([m.memory_percent for m in self.metrics_history]),
            'total_io_read': self.metrics_history[-1].disk_io_read - self.metrics_history[0].disk_io_read,
            'total_io_write': self.metrics_history[-1].disk_io_write - self.metrics_history[0].disk_io_write,
            'uptime': time.time() - self.start_time
        }

class MessageBuffer:
    """Efficient message buffer with automatic batching"""
    def __init__(self, max_size: int = 1000):
        self.buffer = asyncio.Queue(maxsize=max_size)
        self.batch_sizes = deque(maxlen=100)
        self.processing_times = deque(maxlen=100)
        
    async def put(self, message: str):
        """Add message to buffer with backpressure"""
        if self.buffer.full():
            await asyncio.sleep(0.1)  # Backpressure
        await self.buffer.put(message)
        
    async def get_batch(self, size: int) -> List[str]:
        """Get batch of messages with adaptive sizing"""
        batch = []
        start_time = datetime.now()
        
        try:
            for _ in range(size):
                if not self.buffer.empty():
                    batch.append(await self.buffer.get())
                else:
                    break
                    
            processing_time = (datetime.now() - start_time).total_seconds()
            self.processing_times.append(processing_time)
            self.batch_sizes.append(len(batch))
            
            return batch
            
        except Exception as e:
            logger.error(f"Error getting batch: {e}")
            return batch
            
    def get_metrics(self) -> Dict[str, float]:
        """Calculate buffer metrics"""
        if not self.batch_sizes or not self.processing_times:
            return {
                'avg_batch_size': 0,
                'avg_processing_time': 0,
                'buffer_utilization': 0
            }
            
        return {
            'avg_batch_size': sum(self.batch_sizes) / len(self.batch_sizes),
            'avg_processing_time': sum(self.processing_times) / len(self.processing_times),
            'buffer_utilization': self.buffer.qsize() / self.buffer.maxsize
        }

class IOManager:
    """Manages I/O operations with caching and batching"""
    def __init__(self, cache_size: int = 1000):
        self.cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self.write_buffer = []
        self.buffer_size = 0
        self.max_buffer_size = 1024 * 1024  # 1MB
        self.metrics = IOMetrics()
        
    @asynccontextmanager
    async def batch_writer(self, file_path: str):
        """Context manager for batch writing"""
        try:
            self.write_buffer = []
            self.buffer_size = 0
            yield self
        finally:
            if self.write_buffer:
                async with aiofiles.open(file_path, mode='a') as f:
                    await f.write(''.join(self.write_buffer))
            self.write_buffer = []
            self.buffer_size = 0
            
    async def read_with_cache(self, file_path: str) -> List[str]:
        """Read file with caching"""
        if file_path in self.cache:
            self.cache_hits += 1
            return self.cache[file_path]
            
        self.cache_misses += 1
        start_time = datetime.now()
        
        try:
            async with aiofiles.open(file_path, mode='r') as f:
                content = await f.readlines()
                
            self.metrics.read_latency = (datetime.now() - start_time).total_seconds()
            
            if len(self.cache) < 1000:  # Simple LRU
                self.cache[file_path] = content
                
            return content
            
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            self.metrics.io_errors += 1
            return []
            
    async def write_with_buffer(self, content: str):
        """Write with buffering"""
        self.write_buffer.append(content)
        self.buffer_size += len(content)
        
        if self.buffer_size >= self.max_buffer_size:
            return True
        return False

class AdvancedIOProcessor:
    """Advanced processor with optimized I/O handling and monitoring"""
    def __init__(self, history_size: int = 100):
        self.state = ProcessingState()
        self.buffer = MessageBuffer()
        self.io_manager = IOManager()
        self.validator = MessageValidator()
        self.monitor = PerformanceMonitor()
        self.processing_window = 0.1
        self.batch_size = 10
        self.concurrent_limit = 5
        self.error_threshold = 0.2
        
    async def process_file(self, input_path: str, output_path: str):
        """Process entire file with optimized I/O"""
        start_time = time.time()
        try:
            messages = await self.io_manager.read_with_cache(input_path)
            
            async with self.io_manager.batch_writer(output_path) as writer:
                for message in messages:
                    await self.buffer.put(message.strip())
                    
                total_processed = 0
                total_failed = 0
                
                while not self.buffer.buffer.empty():
                    batch = await self.buffer.get_batch(self.batch_size)
                    if not batch:
                        break
                        
                    results = await self._process_batch(batch)
                    
                    # Update metrics
                    for result in results:
                        if result.get('status') == 'success':
                            total_processed += 1
                        else:
                            total_failed += 1
                        
                        # Write results with buffering
                        should_flush = await writer.write_with_buffer(
                            json.dumps(result) + '\n'
                        )
                        if should_flush:
                            logger.info("Buffer full, flushing to disk...")
                    
                    # Update system metrics
                    self.state.system_metrics = self.monitor.get_current_metrics()
                    
                    # Log progress
                    progress = (total_processed + total_failed) / len(messages) * 100
                    logger.info(f"Progress: {progress:.1f}% - Processed: {total_processed}, Failed: {total_failed}")
                    
            processing_time = time.time() - start_time
            metrics = self._get_metrics()
            metrics['processing_summary'] = {
                'total_time': processing_time,
                'messages_per_second': len(messages) / processing_time,
                'total_processed': total_processed,
                'total_failed': total_failed,
                'success_rate': total_processed / (total_processed + total_failed) if total_processed + total_failed > 0 else 0
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            return None
            
    async def _process_batch(self, messages: List[str]) -> List[Dict[str, Any]]:
        """Process a batch of messages with advanced error handling"""
        tasks = []
        for msg in messages:
            task = asyncio.create_task(self._process_single(msg))
            tasks.append(task)
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if isinstance(r, dict)]
        
    async def _process_single(self, message: str) -> Optional[Dict[str, Any]]:
        """Process single message with sophisticated logic and metrics"""
        start_time = time.time()
        try:
            # Validate message
            if not (self.validator.validate_structure(message) and 
                   self.validator.validate_content(message)):
                raise ValueError("Invalid message format or content")
            
            # Analyze complexity
            complexity = self._analyze_complexity(message)
            
            # Transform message
            transformed = self.validator.transform_message(message, complexity)
            
            # Simulate processing
            await asyncio.sleep(self.processing_window * (1 + complexity))
            
            processing_time = time.time() - start_time
            
            return {
                'message': message,
                'transformed': transformed,
                'status': 'success',
                'processing_time': processing_time,
                'complexity': complexity,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                'message': message,
                'transformed': None,
                'status': 'error',
                'error': str(e),
                'processing_time': time.time() - start_time,
                'timestamp': datetime.now().isoformat()
            }
            
    def _analyze_complexity(self, message: str) -> float:
        """Advanced complexity analysis"""
        try:
            # Consider message length
            length_factor = len(message) / 1000
            
            # Consider character diversity
            unique_chars = len(set(message))
            diversity_factor = unique_chars / len(message)
            
            # Consider special patterns
            special_patterns = sum(1 for char in message if not char.isalnum())
            pattern_factor = special_patterns / len(message)
            
            # Combine factors with weights
            complexity = (
                0.4 * length_factor +
                0.3 * diversity_factor +
                0.3 * pattern_factor
            )
            
            return min(1.0, complexity)
            
        except Exception as e:
            logger.error(f"Error analyzing complexity: {e}")
            return 0.5
            
    def _get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics"""
        buffer_metrics = self.buffer.get_metrics()
        performance_metrics = self.monitor.get_performance_summary()
        
        return {
            'io_metrics': {
                'read_latency': self.io_manager.metrics.read_latency,
                'write_latency': self.io_manager.metrics.write_latency,
                'io_errors': self.io_manager.metrics.io_errors,
                'cache_hits': self.io_manager.cache_hits,
                'cache_misses': self.io_manager.cache_misses,
                'total_bytes_read': self.io_manager.metrics.total_bytes_read,
                'total_bytes_written': self.io_manager.metrics.total_bytes_written
            },
            'buffer_metrics': buffer_metrics,
            'system_metrics': performance_metrics,
            'processing_metrics': {
                'batch_size': self.batch_size,
                'concurrent_limit': self.concurrent_limit,
                'processing_window': self.processing_window,
                'error_threshold': self.error_threshold
            }
        }

async def main():
    # Initialize processor
    processor = AdvancedIOProcessor()
    
    # Generate larger test dataset
    num_messages = 10000  # Increased message count
    test_data = [
        f"message_{i}_{random.choice(['simple', 'medium', 'complex'])}_{random.randint(1, 1000)}\n"
        for i in range(num_messages)
    ]
    
    # Write test data
    async with aiofiles.open('input.txt', mode='w') as f:
        await f.writelines(test_data)
        
    logger.info(f"Starting advanced I/O processing test with {num_messages} messages...")
    
    # Process file and get metrics
    metrics = await processor.process_file('input.txt', 'output.txt')
    
    logger.info("\nProcessing complete!")
    logger.info("\nPerformance Metrics:")
    logger.info(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    asyncio.run(main()) 