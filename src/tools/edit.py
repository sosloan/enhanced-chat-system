import os
from pathlib import Path
from typing import Dict, Any
from .base import BaseTool, ToolResult

class EditTool(BaseTool):
    """Tool for editing files."""
    
    async def run(self, tool_input: Dict[str, Any]) -> ToolResult:
        """Edit a file."""
        path = tool_input.get("path")
        content = tool_input.get("content")
        mode = tool_input.get("mode", "w")  # Default to write mode
        
        if not path or content is None:
            return ToolResult(error="Path and content are required")
            
        try:
            # Ensure directory exists
            file_path = Path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content to file
            with open(file_path, mode) as f:
                f.write(content)
                
            return ToolResult(
                output=f"File edited successfully at: {path}",
                metadata={"path": path, "mode": mode}
            )
        except Exception as e:
            return ToolResult(error=f"Error editing file: {str(e)}")
            
    def to_param(self) -> Dict[str, Any]:
        """Convert tool to API parameter format."""
        return {
            "type": "function",
            "function": {
                "name": "edit",
                "description": "Edit a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the file to edit"
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to write to the file"
                        },
                        "mode": {
                            "type": "string",
                            "description": "File open mode (w for write, a for append)",
                            "enum": ["w", "a"]
                        }
                    },
                    "required": ["path", "content"]
                }
            }
        } 