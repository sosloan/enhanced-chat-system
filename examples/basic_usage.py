"""Example usage of the GPU Analytics Platform."""

import asyncio
import numpy as np
import httpx
from typing import List, Dict
import time

# Sample data generation
def generate_data(n_points: int = 100) -> List[Dict]:
    """Generate sample data points."""
    return [
        {
            "id": i,
            "value": float(np.random.randn()),
            "metadata": {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "batch": i // 10
            }
        }
        for i in range(n_points)
    ]

async def run_analytics():
    """Run various analytics operations."""
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Check server health
        health = await client.get("/health")
        print(f"Server health: {health.json()}")
        
        # Get supported operations
        info = await client.get("/")
        print(f"\nSupported operations: {info.json()['supported_operations']}")
        
        # Generate test data
        data = generate_data(100)
        print(f"\nGenerated {len(data)} data points")
        
        # Run each operation
        operations = ["mean", "correlation", "matrix_multiply", "pca"]
        for op in operations:
            print(f"\nRunning {op}...")
            response = await client.post(
                "/analyze",
                json={
                    "data": data,
                    "operation": op,
                    "gpu_enabled": True
                }
            )
            result = response.json()
            print(f"Result: {result['result']:.4f}")
            print(f"Computation time: {result['computation_time']:.4f}s")
            print(f"GPU used: {result['used_gpu']}")

async def benchmark_gpu_vs_cpu():
    """Compare GPU vs CPU performance."""
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        data = generate_data(1000)  # Larger dataset for benchmarking
        operations = ["matrix_multiply", "pca"]  # Operations that benefit from GPU
        
        print("\nGPU vs CPU Benchmark:")
        print("-" * 40)
        
        for op in operations:
            print(f"\nOperation: {op}")
            
            # GPU run
            gpu_response = await client.post(
                "/analyze",
                json={
                    "data": data,
                    "operation": op,
                    "gpu_enabled": True
                }
            )
            gpu_result = gpu_response.json()
            
            # CPU run
            cpu_response = await client.post(
                "/analyze",
                json={
                    "data": data,
                    "operation": op,
                    "gpu_enabled": False
                }
            )
            cpu_result = cpu_response.json()
            
            # Compare results
            speedup = cpu_result["computation_time"] / gpu_result["computation_time"]
            print(f"GPU time: {gpu_result['computation_time']:.4f}s")
            print(f"CPU time: {cpu_result['computation_time']:.4f}s")
            print(f"Speedup: {speedup:.2f}x")

async def main():
    """Run example analytics operations."""
    print("GPU Analytics Platform Example\n")
    
    try:
        # Run basic analytics
        await run_analytics()
        
        # Run benchmark
        await benchmark_gpu_vs_cpu()
        
    except httpx.ConnectError:
        print("\nError: Could not connect to server. Make sure it's running at http://localhost:8000")
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 