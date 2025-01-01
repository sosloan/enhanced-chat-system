from typing import Dict, List, Any
from .base import BaseTool, ToolResult

class ToolCollection:
    """Collection of tools that can be used by the AI."""
    
    def __init__(self, *tools: BaseTool):
        self.tools = {tool.__class__.__name__.lower(): tool for tool in tools}
        
    async def run(self, name: str, tool_input: Dict[str, Any]) -> ToolResult:
        """Run a tool by name with the given input."""
        if name not in self.tools:
            return ToolResult(error=f"Tool {name} not found")
            
        try:
            return await self.tools[name].run(tool_input)
        except Exception as e:
            return ToolResult(error=f"Error running tool {name}: {str(e)}")
            
    def to_params(self) -> List[Dict[str, Any]]:
        """Convert all tools to API parameter format."""
        return [tool.to_param() for tool in self.tools.values()] 