"""Command-line interface module."""

import click
import logging
import sys
import json
from typing import Optional
from pathlib import Path
import torch
import uvicorn
from src.config import Config
from src.lib.monitoring import AnalyticsMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """GPU Analytics Platform CLI."""
    pass

@cli.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", default=8000, help="Port to bind to")
@click.option("--workers", default=1, help="Number of worker processes")
@click.option("--reload", is_flag=True, help="Enable auto-reload")
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option("--config", type=click.Path(), help="Path to config file")
def serve(
    host: str,
    port: int,
    workers: int,
    reload: bool,
    debug: bool,
    config: Optional[str]
):
    """Start the analytics server."""
    try:
        # Load configuration
        if config:
            cfg = Config.from_env(config)
        else:
            cfg = Config()
        
        # Override with CLI arguments
        cfg.settings.HOST = host
        cfg.settings.PORT = port
        cfg.settings.WORKERS = workers
        cfg.settings.RELOAD = reload
        cfg.settings.DEBUG = debug
        
        # Configure logging
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Configure GPU
        if cfg.configure_gpu():
            logger.info("GPU configured successfully")
            logger.info(f"Using device: {torch.cuda.get_device_name()}")
        else:
            logger.warning("GPU not available or configuration failed")
        
        # Start server
        logger.info(f"Starting server on {host}:{port}")
        uvicorn.run(
            "src.main:app",
            host=host,
            port=port,
            reload=reload,
            workers=workers,
            log_level="debug" if debug else "info"
        )
        
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)

@cli.command()
@click.option("--config", type=click.Path(), help="Path to config file")
def check(config: Optional[str]):
    """Check system configuration."""
    try:
        # Load configuration
        if config:
            cfg = Config.from_env(config)
        else:
            cfg = Config()
        
        click.echo("System Configuration:")
        click.echo("-" * 50)
        
        # Check Python version
        import platform
        click.echo(f"Python version: {platform.python_version()}")
        
        # Check GPU
        click.echo("\nGPU Information:")
        if torch.cuda.is_available():
            click.echo(f"GPU available: {torch.cuda.get_device_name()}")
            click.echo(f"CUDA version: {torch.version.cuda}")
            click.echo(f"Device count: {torch.cuda.device_count()}")
            click.echo(f"Current device: {torch.cuda.current_device()}")
            memory = torch.cuda.get_device_properties(0).total_memory
            click.echo(f"Total memory: {memory / 1024**2:.2f} MB")
        else:
            click.echo("No GPU available")
        
        # Check configuration
        click.echo("\nConfiguration:")
        click.echo(json.dumps(cfg.to_dict(), indent=2))
        
    except Exception as e:
        logger.error(f"Error checking system: {e}")
        sys.exit(1)

@cli.command()
@click.argument("operation", type=click.Choice(["start", "stop", "status"]))
def monitor(operation: str):
    """Manage system monitoring."""
    try:
        monitor = AnalyticsMonitor()
        
        if operation == "start":
            click.echo("Starting system monitoring...")
            monitor.start_cleanup()
            click.echo("Monitoring started")
            
        elif operation == "stop":
            click.echo("Stopping system monitoring...")
            monitor.stop_cleanup()
            click.echo("Monitoring stopped")
            
        elif operation == "status":
            click.echo("Monitoring Status:")
            click.echo("-" * 50)
            stats = monitor.get_stats()
            click.echo(json.dumps(stats, indent=2))
        
    except Exception as e:
        logger.error(f"Error managing monitoring: {e}")
        sys.exit(1)

@cli.command()
@click.argument("path", type=click.Path())
def init(path: str):
    """Initialize a new configuration file."""
    try:
        path = Path(path)
        
        # Create default configuration
        config = Config()
        
        # Write configuration
        with path.open("w") as f:
            json.dump(config.to_dict(), f, indent=2)
        
        click.echo(f"Configuration file created at: {path}")
        
    except Exception as e:
        logger.error(f"Error creating configuration: {e}")
        sys.exit(1)

@cli.command()
def info():
    """Display system information."""
    try:
        import psutil
        import platform
        
        click.echo("System Information:")
        click.echo("-" * 50)
        
        # System info
        click.echo(f"OS: {platform.system()} {platform.release()}")
        click.echo(f"Python: {platform.python_version()}")
        click.echo(f"CPU cores: {psutil.cpu_count()}")
        
        # Memory info
        memory = psutil.virtual_memory()
        click.echo(f"\nMemory:")
        click.echo(f"Total: {memory.total / 1024**3:.2f} GB")
        click.echo(f"Available: {memory.available / 1024**3:.2f} GB")
        click.echo(f"Used: {memory.percent}%")
        
        # GPU info
        click.echo("\nGPU:")
        if torch.cuda.is_available():
            click.echo(f"Device: {torch.cuda.get_device_name()}")
            click.echo(f"CUDA: {torch.version.cuda}")
            props = torch.cuda.get_device_properties(0)
            click.echo(f"Memory: {props.total_memory / 1024**2:.2f} MB")
            click.echo(f"Compute capability: {props.major}.{props.minor}")
        else:
            click.echo("No GPU available")
        
        # Disk info
        disk = psutil.disk_usage("/")
        click.echo(f"\nDisk:")
        click.echo(f"Total: {disk.total / 1024**3:.2f} GB")
        click.echo(f"Free: {disk.free / 1024**3:.2f} GB")
        click.echo(f"Used: {disk.percent}%")
        
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        sys.exit(1)

if __name__ == "__main__":
    cli() 