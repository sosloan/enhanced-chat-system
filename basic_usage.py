"""
Basic usage example of smol_loop.
"""

import os
import asyncio
from pathlib import Path
from datetime import datetime

from smol_loop import SmolLoopConfig, smol_loop


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
    """Run example tasks with increasing chaos levels."""
    if "ANTHROPIC_API_KEY" not in os.environ:
        raise ValueError("Please set ANTHROPIC_API_KEY environment variable")

    # Example tasks with increasing complexity and chaos
    tasks = [
        "Create a mystical greeting that echoes through the digital realm",
        "Forge a function that transforms mundane text into epic proclamations",
        "Summon a random constellation of ASCII art and poetic output",
        "Craft a time-aware enchantment that adapts its message to the cosmic hour",
    ]

    # Configuration
    config = SmolLoopConfig(
        api_key=os.environ["ANTHROPIC_API_KEY"],
        cleanup_files=True,
        debug=True,
        temp_dir=Path("temp") / datetime.now().strftime("%Y%m%d_%H%M%S"),
    )

    print("\n🎭 Initiating the Smol Loop Theater...")
    print("=" * 60)

    for i, task in enumerate(tasks):
        act_number = i + 1
        chaos_level = i

        print(f"\n🎬 Act {act_number}: {task}")
        print(f"{'~' * 40}")
        print(f"🌀 Chaos Level: {'✨' * (chaos_level + 1)}")

        try:
            result = await smol_loop(
                task=task,
                config=config,
                chaos_level=chaos_level,
                output_callback=output_callback,
                tool_output_callback=tool_callback,
                api_response_callback=api_callback,
            )

            if result.success:
                print("\n✅ Performance Successful!")
                if result.metrics:
                    print("\n📊 Performance Metrics:")
                    for key, value in result.metrics.items():
                        if key not in ("start_time", "end_time"):
                            print(f"- {key}: {value}")
            else:
                print(f"\n❌ Performance Error:")
                print(result.error)

        except Exception as e:
            print(f"🚫 Error in Act {act_number}: {e}")
            continue

        print(f"\n{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(main())
