from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class ToolResult:
    """Result of a tool execution."""
    output: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

class BaseTool:
    """Base class for all tools."""
    
    async def run(self, tool_input: Dict[str, Any]) -> ToolResult:
        """Run the tool with the given input."""
        raise NotImplementedError("Tool must implement run method")
        
    def to_param(self) -> Dict[str, Any]:
        """Convert tool to API parameter format."""
        raise NotImplementedError("Tool must implement to_param method") 