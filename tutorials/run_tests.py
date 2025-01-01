import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn

from src.lib.test_framework import TestFramework
from src.lib.smol_loop import SmolLoopConfig
from src.lib.improver import SmolImprover, ImprovementStrategy

# Configure console
console = Console()

async def main():
    load_dotenv()
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    together_key = os.getenv("TOGETHER_AI_API_KEY")
    
    if not anthropic_key:
        console.print("[red]Error: ANTHROPIC_API_KEY not found in .env file[/red]")
        return
        
    if not together_key:
        console.print("[red]Error: TOGETHER_AI_API_KEY not found in .env file[/red]")
        return
    
    # Create output directory
    output_dir = Path("output") / "latest"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure framework
    config = SmolLoopConfig(
        api_key=anthropic_key,
        cleanup_files=False,
        debug=True,
        temp_dir=output_dir / "temp"
    )
    
    # Configure improvement strategy
    strategy = ImprovementStrategy(
        base_chaos=2,
        complexity_target=0.7,
        creativity_target=0.8,
        max_retries=3,
        adaptation_rate=0.3
    )
    
    # Create improver
    improver = SmolImprover(
        config=config,
        index_path=output_dir / "index.json",
        strategy=strategy
    )
    
    # Create test framework
    framework = TestFramework(
        api_key=anthropic_key,
        improver=improver
    )
    
    console.print("\n🎭 Starting Enhanced Test Framework")
    console.print("=" * 60)
    
    with Progress(
        SpinnerColumn(),
        *Progress.get_default_columns(),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Running tests...", total=100)
        
        try:
            await framework.run_tests(num_iterations=100)
            progress.update(task, completed=100)
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            return
    
    # Show successful patterns
    patterns = improver.indexer.get_successful_patterns()
    if patterns:
        console.print("\n🏆 Most Successful Patterns:")
        for pattern, success_rate, metrics in patterns:
            console.print(
                Panel(
                    f"Pattern: {pattern}\n"
                    f"Success Rate: {success_rate:.1%}\n"
                    f"Creativity Score: {metrics.creativity_score:.2f}\n"
                    f"Complexity: {metrics.complexity}",
                    title=f"[green]{pattern}[/green]",
                    border_style="green"
                )
            )

if __name__ == "__main__":
    asyncio.run(main()) 