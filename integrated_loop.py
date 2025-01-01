"""
Example demonstrating integration of core, indexer, improver, and self-improving components.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any

from smol_loop.config import SmolLoopConfig
from smol_loop.core import smol_loop
from smol_loop.indexer import CodeIndexer
from smol_loop.improver import SmolImprover

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def output_callback(content: Dict[str, Any]) -> None:
    """Callback for general output."""
    if content.get("type") == "text":
        logger.info(f"Output: {content['text']}")


async def tool_callback(content: Dict[str, Any]) -> None:
    """Callback for tool-specific output."""
    if content.get("type") == "tool_use":
        logger.info(f"Tool used: {content['name']}")


async def api_callback(response: Dict[str, Any]) -> None:
    """Callback for API responses."""
    logger.info(f"API usage: {response.get('usage', {})}")


async def main():
    # Initialize components
    config = SmolLoopConfig(
        api_key="your-api-key",  # Replace with your API key
        endpoint_url="https://api.anthropic.com/v1",  # Optional: Override default endpoint
        output_dir=Path("./output"),
        timeout=30.0,
        cleanup=True,
        max_retries=3,
        base_chaos_level=0,
    )

    indexer = CodeIndexer(index_file=Path("./code_index.json"))
    improver = SmolImprover()

    # Example task
    task = """
    Create a function that calculates the Fibonacci sequence recursively,
    then analyze and improve its performance.
    """

    # Run initial code generation
    result = await smol_loop(
        task=task,
        config=config,
        chaos_level=0.3,
        output_callback=output_callback,
        tool_output_callback=tool_callback,
        api_response_callback=api_callback,
    )

    if not result.success:
        logger.error(f"Initial code generation failed: {result.error}")
        return

    # Index the generated code
    for execution_result in result.execution_results:
        index = indexer.index_file(
            file_path=execution_result.file,
            task=task,
            chaos_level=0.3,
            success=execution_result.success,
            execution_time=execution_result.execution_time,
            output=execution_result.output,
            error=execution_result.error,
        )
        logger.info(f"Indexed file: {index.path}")

    # Analyze code for improvements
    with open(result.execution_results[0].file, "r") as f:
        code = f.read()

    improvement_suggestions = improver.analyze_code(code)
    logger.info("Improvement suggestions:")
    for suggestion in improvement_suggestions:
        logger.info(
            f"Line {suggestion.line_number}: {suggestion.reason} "
            f"(confidence: {suggestion.confidence:.2f})"
        )

    # Get metrics from successful patterns
    patterns = indexer.get_successful_patterns(min_success_rate=0.8)
    logger.info("Successful patterns metrics:")
    for metric, value in patterns.items():
        logger.info(f"{metric}: {value}")

    # Find similar tasks
    similar_tasks = indexer.get_similar_tasks(
        task=task,
        limit=3,
        success_only=True,
    )
    logger.info("Similar successful tasks:")
    for task_index in similar_tasks:
        logger.info(
            f"Task: {task_index.task}, "
            f"Success: {task_index.success}, "
            f"Execution time: {task_index.execution_time:.2f}s"
        )


if __name__ == "__main__":
    asyncio.run(main())
