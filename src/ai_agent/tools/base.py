"""
Base classes for tools.
工具基类
"""

import time
from abc import ABC, abstractmethod
from typing import Any

from ..database import get_database
from ..logger import get_logger

logger = get_logger(__name__)


class Tool(ABC):
    """Abstract base class for all tools."""

    """所有工具的抽象基类"""

    def __init__(self):
        self.tool_name = self.__class__.__name__.replace("Tool", "").lower()

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

    def _record_tool_usage(
        self, operation: str, start_time: float, success: bool = True
    ):
        """Record tool usage to the database."""
        """将工具使用情况记录到数据库"""
        duration_ms = (time.time() - start_time) * 1000
        try:
            db = get_database()
            db.record_tool_usage(self.tool_name, operation, duration_ms, success)
            logger.debug(f"Tool usage recorded: {self.tool_name}.{operation}")
        except Exception as e:
            logger.error(f"Failed to record tool usage: {str(e)}")


class ToolRegistry:
    """Registry for managing available tools."""

    """管理可用工具的注册表"""

    def __init__(self):
        self.tools: dict[str, Tool] = {}  # 工具字典

    def register_tool(self, name: str, tool: Tool):
        """Register a new tool."""
        """注册新工具"""
        self.tools[name] = tool
        logger.debug(f"Tool registered: {name}")

    def get_tool(self, name: str) -> Tool:
        """Get a tool by name."""
        """按名称获取工具"""
        if name not in self.tools:
            logger.error(
                f"Tool not found: {name}, available tools: {list(self.tools.keys())}"
            )
            raise ValueError(f"Tool not found: {name}")
        logger.debug(f"Tool retrieved: {name}")
        return self.tools[name]

    def get_available_tools(self) -> list[str]:
        """Get list of available tool names."""
        """获取可用工具名称列表"""
        tools = list(self.tools.keys())
        logger.debug(f"Available tools: {tools}")
        return tools
