import json
import math
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from .logger import get_logger

logger = get_logger(__name__)


class Tool(ABC):
    """Abstract base class for all tools."""

    """所有工具的抽象基类"""

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Execute the tool with the given parameters."""
        """使用给定参数执行工具"""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Get a description of what the tool does."""
        """获取工具功能的描述"""
        pass


class ToolRegistry:
    """Registry for managing available tools."""

    """管理可用工具的注册表"""

    def __init__(self):
        self.tools: Dict[str, Tool] = {}  # 工具字典

    def register_tool(self, name: str, tool: Tool):
        """Register a new tool."""
        """注册新工具"""
        self.tools[name] = tool
        logger.debug(f"Tool registered: {name}")

    def get_tool(self, name: str) -> Tool:
        """Get a tool by name."""
        """按名称获取工具"""
        if name not in self.tools:
            logger.error(f"Tool not found: {name}")
            raise ValueError(f"Tool not found: {name}")
        logger.debug(f"Tool retrieved: {name}")
        return self.tools[name]

    def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        """获取可用工具名称列表"""
        tools = list(self.tools.keys())
        logger.debug(f"Available tools: {tools}")
        return tools


class FileTool(Tool):
    """Tool for file operations."""

    """文件操作工具"""

    def execute(self, **kwargs) -> Any:
        operation = kwargs.get("operation")
        logger.info(f"Executing file operation: {operation} with args: {kwargs}")

        if operation == "read":
            result = self._read_file(kwargs["path"])
            logger.debug(f"File read successful, length: {len(result)}")
            return result
        elif operation == "write":
            result = self._write_file(kwargs["path"], kwargs["content"])
            logger.debug("File write successful")
            return result
        elif operation == "list":
            result = self._list_directory(kwargs.get("path", "."))
            logger.debug(f"Directory list successful, items: {len(result)}")
            return result
        elif operation == "exists":
            result = self._file_exists(kwargs["path"])
            logger.debug(f"File exists check: {result}")
            return result
        else:
            logger.error(f"Unknown file operation: {operation}")
            raise ValueError(f"Unknown file operation: {operation}")

    def get_description(self) -> str:
        return "Perform file operations: read, write, list, check existence"

    def _read_file(self, path: str) -> str:
        """Read content from a file."""
        """从文件读取内容"""
        logger.debug(f"Reading file: {path}")
        if not os.path.exists(path):
            logger.error(f"File not found: {path}")
            raise FileNotFoundError(f"File not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        logger.debug(f"File read completed, size: {len(content)} bytes")
        return content

    def _write_file(self, path: str, content: str) -> str:
        """Write content to a file."""
        """将内容写入文件"""
        logger.debug(f"Writing to file: {path}, content length: {len(content)}")
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"File written successfully: {path}")
        return f"Successfully wrote to {path}"

    def _list_directory(self, path: str) -> List[str]:
        """List contents of a directory."""
        """列出目录内容"""
        logger.debug(f"Listing directory: {path}")
        if not os.path.exists(path):
            logger.error(f"Directory not found: {path}")
            raise FileNotFoundError(f"Directory not found: {path}")

        items = os.listdir(path)
        logger.debug(f"Directory listed, found {len(items)} items")
        return items

    def _file_exists(self, path: str) -> bool:
        """Check if a file or directory exists."""
        """检查文件或目录是否存在"""
        exists = os.path.exists(path)
        logger.debug(f"File exists check for {path}: {exists}")
        return exists


class CalculatorTool(Tool):
    """Tool for mathematical calculations."""

    """数学计算工具"""

    def execute(self, **kwargs) -> Any:
        operation = kwargs.get("operation")
        logger.info(f"Executing calculator operation: {operation} with args: {kwargs}")

        try:
            if operation == "add":
                result = self._add(kwargs["a"], kwargs["b"])
            elif operation == "subtract":
                result = self._subtract(kwargs["a"], kwargs["b"])
            elif operation == "multiply":
                result = self._multiply(kwargs["a"], kwargs["b"])
            elif operation == "divide":
                result = self._divide(kwargs["a"], kwargs["b"])
            elif operation == "power":
                result = self._power(kwargs["base"], kwargs["exponent"])
            elif operation == "sqrt":
                result = self._sqrt(kwargs["number"])
            elif operation == "evaluate":
                result = self._evaluate_expression(kwargs["expression"])
            else:
                logger.error(f"Unknown calculation operation: {operation}")
                raise ValueError(f"Unknown calculation operation: {operation}")

            logger.debug(f"Calculation successful: {result}")
            return result
        except Exception as e:
            logger.error(f"Calculation error: {str(e)}")
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
        """安全评估数学表达式"""
        logger.debug(f"Evaluating expression: {expression}")
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in expression):
            logger.error("Expression contains invalid characters")
            raise ValueError("Expression contains invalid characters")

        try:
            result = eval(expression, {"__builtins__": {}}, {})
            logger.debug(f"Expression evaluated: {expression} = {result}")
            return result
        except Exception as e:
            logger.error(f"Error evaluating expression: {str(e)}")
            raise ValueError(f"Error evaluating expression: {str(e)}")


class WebSearchTool(Tool):
    """Tool for web search operations (placeholder implementation)."""

    """网络搜索操作工具（占位符实现）"""

    def execute(self, **kwargs) -> Any:
        query = kwargs.get("query")
        logger.info(f"Executing web search for query: {query}")

        if not query:
            logger.error("Search query is required")
            raise ValueError("Search query is required")

        result = f"Web search for '{query}' would be performed here. This is a placeholder implementation."
        logger.debug("Web search placeholder executed")
        return result

    def get_description(self) -> str:
        return "Search the web for information (placeholder implementation)"
