"""
File operations tool.
文件操作工具
"""

import os
import time
from typing import List, Union

from ..logger import get_logger
from .base import Tool

logger = get_logger(__name__)


class FileTool(Tool):
    """Tool for file operations."""

    """文件操作工具"""

    def execute(self, **kwargs) -> Union[str, List[str], bool]:
        operation = kwargs.get("operation")
        logger.info(f"Executing file operation: {operation} with args: {kwargs}")

        start_time = time.time()
        success = True

        try:
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
        except Exception as e:
            success = False
            logger.error(f"File operation failed: {str(e)}")
            raise
        finally:
            self._record_tool_usage(operation, start_time, success)

    def get_description(self) -> str:
        return "file: Perform file operations - read(path), write(path, content), list(path), exists(path)"

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
