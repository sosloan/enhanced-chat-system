import asyncio
import os
from typing import Dict, Any
from .base import BaseTool, ToolResult

class BashTool(BaseTool):
    """Tool for executing bash commands."""
    
    async def run(self, tool_input: Dict[str, Any]) -> ToolResult:
        """Execute a bash command."""
        command = tool_input.get("command")
        if not command:
            return ToolResult(error="No command provided")
            
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                shell=True
            )
            stdout, stderr = await process.communicate()
            
            output = stdout.decode() if stdout else ""
            error = stderr.decode() if stderr else ""
            
            return ToolResult(
                output=output,
                error=error if process.returncode != 0 else None,
                metadata={"return_code": process.returncode}
            )
        except Exception as e:
            return ToolResult(error=f"Error executing command: {str(e)}")
            
    def to_param(self) -> Dict[str, Any]:
        """Convert tool to API parameter format."""
        return {
            "type": "function",
            "function": {
                "name": "bash",
                "description": "Execute a bash command",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The command to execute"
                        }
                    },
                    "required": ["command"]
                }
            }
        } 