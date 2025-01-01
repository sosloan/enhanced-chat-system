import os
import sys
import platform
from typing import Dict, Any
from .base import BaseTool, ToolResult

class ComputerTool(BaseTool):
    """Tool for getting information about the computer environment."""
    
    async def run(self, tool_input: Dict[str, Any]) -> ToolResult:
        """Get information about the computer environment."""
        try:
            info = {
                "os": platform.system(),
                "os_version": platform.version(),
                "python_version": sys.version,
                "cpu_count": os.cpu_count(),
                "platform": platform.platform(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "hostname": platform.node(),
            }
            return ToolResult(output=str(info))
        except Exception as e:
            return ToolResult(error=f"Error getting computer info: {str(e)}")
            
    def to_param(self) -> Dict[str, Any]:
        """Convert tool to API parameter format."""
        return {
            "type": "function",
            "function": {
                "name": "computer",
                "description": "Get information about the computer environment",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        } 