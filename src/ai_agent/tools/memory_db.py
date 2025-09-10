"""
Memory database tool for storing and retrieving data using SQLite.
使用SQLite的内存数据库工具，用于存储和检索数据
"""

import time
from typing import Any, List

from ..logger import get_logger
from .base import Tool
from .memory_db_manager import get_memory_db

logger = get_logger(__name__)


class MemoryDBTool(Tool):
    """Tool for memory database operations using SQLite."""

    """使用SQLite的内存数据库操作工具"""

    def execute(self, **kwargs) -> Any:
        operation = kwargs.get("operation")
        logger.info(f"Executing memory_db operation: {operation} with args: {kwargs}")

        start_time = time.time()
        success = True

        try:
            if operation == "store":
                result = self._store_data(kwargs["key"], kwargs["value"])
            elif operation == "retrieve":
                result = self._retrieve_data(kwargs["key"])
            elif operation == "delete":
                result = self._delete_data(kwargs["key"])
            elif operation == "list_keys":
                result = self._list_keys()
            elif operation == "clear":
                result = self._clear_data()
            else:
                logger.error(f"Unknown memory_db operation: {operation}")
                raise ValueError(f"Unknown memory_db operation: {operation}")

            logger.debug(f"Memory_db operation successful: {result}")
            return result
        except Exception as e:
            success = False
            logger.error(f"Memory_db operation error: {str(e)}")
            return f"Memory_db operation error: {str(e)}"
        finally:
            self._record_tool_usage(operation, start_time, success)

    def get_description(self) -> str:
        return "memory_db: Memory database operations - store(key, value), retrieve(key), delete(key), list_keys(), clear()"

    def _store_data(self, key: str, value: Any) -> str:
        """Store data in the memory database."""
        """在内存数据库中存储数据"""
        logger.debug(f"Storing data with key: {key}")
        db = get_memory_db()
        success = db.store(key, value)
        if success:
            logger.info(f"Data stored successfully: {key}")
            return f"Data stored successfully: {key}"
        else:
            logger.error(f"Failed to store data: {key}")
            return f"Failed to store data: {key}"

    def _retrieve_data(self, key: str) -> Any:
        """Retrieve data from the memory database."""
        """从内存数据库中检索数据"""
        logger.debug(f"Retrieving data with key: {key}")
        db = get_memory_db()
        result = db.retrieve(key)
        if result is None:
            logger.warning(f"Key not found: {key}")
            return f"Key not found: {key}"
        logger.debug(f"Data retrieved: {key}")
        return result

    def _delete_data(self, key: str) -> str:
        """Delete data from the memory database."""
        """从内存数据库中删除数据"""
        logger.debug(f"Deleting data with key: {key}")
        db = get_memory_db()
        success = db.delete(key)
        if success:
            logger.info(f"Data deleted: {key}")
            return f"Data deleted: {key}"
        else:
            logger.error(f"Failed to delete data: {key}")
            return f"Failed to delete data: {key}"

    def _list_keys(self) -> List[str]:
        """List all keys in the memory database."""
        """列出内存数据库中的所有键"""
        logger.debug("Listing all keys in memory database")
        db = get_memory_db()
        keys = db.list_keys()
        logger.debug(f"Found {len(keys)} keys")
        return keys

    def _clear_data(self) -> str:
        """Clear all data from the memory database."""
        """清除内存数据库中的所有数据"""
        logger.debug("Clearing all data from memory database")
        db = get_memory_db()
        success = db.clear()
        if success:
            logger.info("All data cleared from memory database")
            return "All data cleared from memory database"
        else:
            logger.error("Failed to clear memory database")
            return "Failed to clear memory database"

    def _record_tool_usage(
        self, operation: str, start_time: float, success: bool = True
    ):
        """Record tool usage statistics."""
        """记录工具使用统计信息"""
        duration_ms = (time.time() - start_time) * 1000
        try:
            from ..database import get_database

            db = get_database()
            db.record_tool_usage(
                tool_name="memory_db",
                operation=operation,
                duration_ms=duration_ms,
                success=success,
            )
        except Exception as e:
            logger.debug(f"Failed to record tool usage: {str(e)}")
