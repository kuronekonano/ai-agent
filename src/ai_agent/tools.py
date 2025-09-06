import json
import math
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class Tool(ABC):
    """Abstract base class for all tools."""

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Execute the tool with the given parameters."""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Get a description of what the tool does."""
        pass


class ToolRegistry:
    """Registry for managing available tools."""

    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register_tool(self, name: str, tool: Tool):
        """Register a new tool."""
        self.tools[name] = tool

    def get_tool(self, name: str) -> Tool:
        """Get a tool by name."""
        if name not in self.tools:
            raise ValueError(f"Tool not found: {name}")
        return self.tools[name]

    def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return list(self.tools.keys())


class FileTool(Tool):
    """Tool for file operations."""

    def execute(self, **kwargs) -> Any:
        operation = kwargs.get("operation")

        if operation == "read":
            return self._read_file(kwargs["path"])
        elif operation == "write":
            return self._write_file(kwargs["path"], kwargs["content"])
        elif operation == "list":
            return self._list_directory(kwargs.get("path", "."))
        elif operation == "exists":
            return self._file_exists(kwargs["path"])
        else:
            raise ValueError(f"Unknown file operation: {operation}")

    def get_description(self) -> str:
        return "Perform file operations: read, write, list, check existence"

    def _read_file(self, path: str) -> str:
        """Read content from a file."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def _write_file(self, path: str, content: str) -> str:
        """Write content to a file."""
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        return f"Successfully wrote to {path}"

    def _list_directory(self, path: str) -> List[str]:
        """List contents of a directory."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Directory not found: {path}")

        return os.listdir(path)

    def _file_exists(self, path: str) -> bool:
        """Check if a file or directory exists."""
        return os.path.exists(path)


class CalculatorTool(Tool):
    """Tool for mathematical calculations."""

    def execute(self, **kwargs) -> Any:
        operation = kwargs.get("operation")

        try:
            if operation == "add":
                return self._add(kwargs["a"], kwargs["b"])
            elif operation == "subtract":
                return self._subtract(kwargs["a"], kwargs["b"])
            elif operation == "multiply":
                return self._multiply(kwargs["a"], kwargs["b"])
            elif operation == "divide":
                return self._divide(kwargs["a"], kwargs["b"])
            elif operation == "power":
                return self._power(kwargs["base"], kwargs["exponent"])
            elif operation == "sqrt":
                return self._sqrt(kwargs["number"])
            elif operation == "evaluate":
                return self._evaluate_expression(kwargs["expression"])
            else:
                raise ValueError(f"Unknown calculation operation: {operation}")
        except Exception as e:
            return f"Calculation error: {str(e)}"

    def get_description(self) -> str:
        return "Perform mathematical calculations: add, subtract, multiply, divide, power, sqrt, evaluate expressions"

    def _add(self, a: float, b: float) -> float:
        return a + b

    def _subtract(self, a: float, b: float) -> float:
        return a - b

    def _multiply(self, a: float, b: float) -> float:
        return a * b

    def _divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Division by zero")
        return a / b

    def _power(self, base: float, exponent: float) -> float:
        return base**exponent

    def _sqrt(self, number: float) -> float:
        if number < 0:
            raise ValueError("Cannot calculate square root of negative number")
        return math.sqrt(number)

    def _evaluate_expression(self, expression: str) -> float:
        """Safely evaluate a mathematical expression."""
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in expression):
            raise ValueError("Expression contains invalid characters")

        try:
            return eval(expression, {"__builtins__": {}}, {})
        except Exception as e:
            raise ValueError(f"Error evaluating expression: {str(e)}")


class WebSearchTool(Tool):
    """Tool for web search operations (placeholder implementation)."""

    def execute(self, **kwargs) -> Any:
        query = kwargs.get("query")

        if not query:
            raise ValueError("Search query is required")

        return f"Web search for '{query}' would be performed here. This is a placeholder implementation."

    def get_description(self) -> str:
        return "Search the web for information (placeholder implementation)"
