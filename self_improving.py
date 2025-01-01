"""
Example of self-improving smol loop.
"""

import asyncio
import os
from datetime import datetime
from pathlib import Path

from smol_loop import SmolLoopConfig
from smol_loop.improver import SmolImprover, ImprovementStrategy


async def output_callback(content):
    """Callback for model outputs."""
    if content.get("type") == "text":
        print(f"\n📝 Model Output:")
        print(f"{'~' * 40}")
        print(content["text"])
        print(f"{'~' * 40}")


async def tool_callback(result, tool_id):
    """Callback for tool outputs."""
    if result.output:
        print(f"\n🛠️ Tool Output ({tool_id}):")
        print(f"{'~' * 40}")
        print(result.output)
        print(f"{'~' * 40}")


async def api_callback(request, response, error):
    """Callback for API responses."""
    if error:
        print(f"\n❌ API Error: {error}")
    elif response:
        print(f"\n✅ API Success: {response.status_code}")


async def main():
    """Run example of self-improving loop."""
    if "ANTHROPIC_API_KEY" not in os.environ:
        raise ValueError("Please set ANTHROPIC_API_KEY environment variable")

    # Create output directory
    output_dir = Path("output") / datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Configuration
    config = SmolLoopConfig(
        api_key=os.environ["ANTHROPIC_API_KEY"],
        cleanup_files=False,  # Keep files for analysis
        debug=True,
        temp_dir=output_dir / "temp",
    )

    # Create improver with custom strategy
    strategy = ImprovementStrategy(
        base_chaos=2,
        complexity_target=0.7,
        creativity_target=0.8,
        max_retries=3,
        adaptation_rate=0.3,
    )

    improver = SmolImprover(
        config=config,
        index_path=output_dir / "index.json",
        strategy=strategy,
    )

    # Example tasks with increasing complexity
    tasks = [
        "Create a function that generates a random password",
        "Create a class for managing a todo list with priorities",
        "Create an async function that simulates a space battle",
        "Create a text-based adventure game engine",
    ]

    print("\n🔄 Starting Self-Improving Loop")
    print("=" * 60)

    for i, task in enumerate(tasks, 1):
        print(f"\n🎯 Task {i}: {task}")
        print(f"{'~' * 40}")

        try:
            result, history = await improver.improve_task(
                task=task,
                max_iterations=5,
                min_success_rate=0.8,
            )

            # Print improvement history
            print("\n📈 Improvement History:")
            for entry in history:
                status = "✅" if entry["success"] else "❌"
                print(
                    f"Iteration {entry['iteration']}: "
                    f"Chaos {entry['chaos_level']} "
                    f"Time {entry['execution_time']:.2f}s "
                    f"{status}"
                )

            if result.success:
                print("\n✨ Final Result:")
                if result.metrics:
                    print("\n📊 Metrics:")
                    for key, value in result.metrics.items():
                        if key not in ("start_time", "end_time"):
                            print(f"- {key}: {value}")

                print("\n📁 Generated Files:")
                for exec_result in result.execution_results:
                    print(f"- {exec_result.file}")
                    if exec_result.output:
                        print(f"  Output: {exec_result.output}")
            else:
                print(f"\n❌ Task Failed:")
                print(result.error)

        except Exception as e:
            print(f"🚫 Error: {e}")
            continue

        print(f"\n{'=' * 60}")

    # Get successful patterns
    patterns = improver.indexer.get_successful_patterns()
    if patterns:
        print("\n🏆 Most Successful Patterns:")
        for pattern, success_rate, metrics in patterns:
            print(f"\n- Pattern: {pattern}")
            print(f"  Success Rate: {success_rate:.1%}")
            print(f"  Creativity Score: {metrics.creativity_score:.2f}")
            print(f"  Complexity: {metrics.complexity}")


if __name__ == "__main__":
    asyncio.run(main())
