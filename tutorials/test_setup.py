import os
from rich.console import Console
from anthropic import Anthropic
from dotenv import load_dotenv

def test_setup():
    console = Console()
    load_dotenv()
    
    # Check environment variables
    console.print("\n[bold]Checking environment variables...[/bold]")
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        console.print("[red]❌ ANTHROPIC_API_KEY not found in .env[/red]")
        return False
    console.print("[green]✓ ANTHROPIC_API_KEY found[/green]")
    
    # Test Anthropic API
    console.print("\n[bold]Testing Anthropic API connection...[/bold]")
    try:
        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=10,
            messages=[{
                "role": "user",
                "content": "Say hello!"
            }]
        )
        console.print("[green]✓ Successfully connected to Anthropic API[/green]")
    except Exception as e:
        console.print(f"[red]❌ Failed to connect to Anthropic API: {e}[/red]")
        return False
    
    # All tests passed
    console.print("\n[bold green]✓ All setup tests passed![/bold green]")
    return True

if __name__ == "__main__":
    test_setup() 