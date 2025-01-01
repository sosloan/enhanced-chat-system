"""Main application entry point."""

import asyncio
import logging
from typing import Optional
import uvicorn
from fastapi import FastAPI, HTTPException
from src.api.main import app as api_app
from src.lib.monitoring import AnalyticsMonitor
from src.lib.error_handling import ErrorHandler
from src.lib.caching import AnalyticsCache, CacheConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create main application
app = FastAPI(
    title="GPU Analytics Platform",
    description="High-performance analytics with GPU acceleration",
    version="1.0.0"
)

# Mount API router
app.mount("/api", api_app)

# Initialize components
monitor = AnalyticsMonitor(debug=True)
error_handler = ErrorHandler(logger=logger)
cache = AnalyticsCache(
    config=CacheConfig(
        max_size=10000,
        ttl=3600,
        cleanup_interval=300
    )
)

@app.on_event("startup")
async def startup():
    """Initialize application on startup."""
    logger.info("Starting GPU Analytics Platform")
    
    try:
        # Start cache cleanup task
        cache.start_cleanup()
        logger.info("Cache cleanup task started")
        
        # Initialize error recovery strategies
        from src.lib.error_handling import RecoveryStrategy
        
        # Strategy for computation errors
        compute_strategy = RecoveryStrategy(
            max_retries=3,
            retry_delay=1.0,
            exponential_backoff=True
        )
        error_handler.register_strategy("compute", compute_strategy)
        
        # Strategy for resource errors
        resource_strategy = RecoveryStrategy(
            max_retries=5,
            retry_delay=2.0,
            exponential_backoff=True
        )
        error_handler.register_strategy("resource", resource_strategy)
        
        logger.info("Error recovery strategies initialized")
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on application shutdown."""
    logger.info("Shutting down GPU Analytics Platform")
    
    try:
        # Stop cache cleanup task
        cache.stop_cleanup()
        logger.info("Cache cleanup task stopped")
        
        # Log final statistics
        cache_stats = cache.get_stats()
        logger.info(f"Final cache statistics: {cache_stats}")
        
        error_stats = error_handler.get_error_stats()
        logger.info(f"Final error statistics: {error_stats}")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint."""
    import torch
    return {
        "name": "GPU Analytics Platform",
        "version": "1.0.0",
        "gpu_available": torch.cuda.is_available(),
        "endpoints": [
            {"path": "/api", "description": "Analytics API"},
            {"path": "/docs", "description": "API documentation"},
            {"path": "/stats", "description": "System statistics"}
        ]
    }

@app.get("/stats")
async def get_stats():
    """Get system statistics."""
    try:
        return {
            "cache": cache.get_stats(),
            "errors": error_handler.get_error_stats(),
            "gpu": {
                "available": torch.cuda.is_available(),
                "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
                "memory_allocated": torch.cuda.memory_allocated() if torch.cuda.is_available() else 0,
                "memory_reserved": torch.cuda.memory_reserved() if torch.cuda.is_available() else 0
            }
        }
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving system statistics"
        )

def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    workers: Optional[int] = None
):
    """Run the server."""
    try:
        uvicorn.run(
            "src.main:app",
            host=host,
            port=port,
            reload=reload,
            workers=workers or (1 if reload else None)
        )
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="GPU Analytics Platform")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--workers", type=int, help="Number of worker processes")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    run_server(
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers
    )