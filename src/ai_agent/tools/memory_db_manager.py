"""
SQLite-based memory database for long-term memory storage.
使用SQLite的长时记忆数据库
"""

import json
import sqlite3
from pathlib import Path
from typing import Any, List, Optional

from ..logger import get_logger

logger = get_logger(__name__)


class MemoryDB:
    """SQLite-based memory database for persistent storage."""

    """基于SQLite的长时记忆数据库"""

    def __init__(self, db_path: str = "data/memory.db"):
        """Initialize the memory database."""
        """初始化内存数据库"""
        # Ensure data directory exists
        db_dir = Path(db_path).parent
        if db_dir:
            db_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self._init_tables()
        logger.info(f"Memory database initialized at {db_path}")

    def _init_tables(self):
        """Initialize database tables."""
        """初始化数据库表"""
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    UNIQUE(key)
                )
            """
            )

    def store(self, key: str, value: Any) -> bool:
        """Store data in the memory database."""
        """在内存数据库中存储数据"""
        try:
            # Convert value to JSON string for storage
            value_json = json.dumps(value, ensure_ascii=False)
            timestamp = self._get_current_timestamp()

            with self.connection:
                self.connection.execute(
                    "INSERT OR REPLACE INTO memory_data (key, value, timestamp) VALUES (?, ?, ?)",
                    (key, value_json, timestamp),
                )
            logger.debug(f"Data stored in memory database: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to store data in memory database: {str(e)}")
            return False

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data from the memory database."""
        """从内存数据库中检索数据"""
        try:
            cursor = self.connection.execute(
                "SELECT value FROM memory_data WHERE key = ?", (key,)
            )
            result = cursor.fetchone()
            if result:
                # Parse JSON string back to original object
                return json.loads(result[0])
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve data from memory database: {str(e)}")
            return None

    def delete(self, key: str) -> bool:
        """Delete data from the memory database."""
        """从内存数据库中删除数据"""
        try:
            with self.connection:
                self.connection.execute("DELETE FROM memory_data WHERE key = ?", (key,))
            logger.debug(f"Data deleted from memory database: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete data from memory database: {str(e)}")
            return False

    def list_keys(self) -> List[str]:
        """List all keys in the memory database."""
        """列出内存数据库中的所有键"""
        try:
            cursor = self.connection.execute("SELECT key FROM memory_data")
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to list keys from memory database: {str(e)}")
            return []

    def clear(self) -> bool:
        """Clear all data from the memory database."""
        """清除内存数据库中的所有数据"""
        try:
            with self.connection:
                self.connection.execute("DELETE FROM memory_data")
            logger.debug("Memory database cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear memory database: {str(e)}")
            return False

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        """获取当前时间戳（ISO格式）"""
        from datetime import datetime

        return datetime.now().isoformat()

    def close(self):
        """Close the database connection."""
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            logger.debug("Memory database connection closed")

    def __enter__(self):
        """Context manager entry."""
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        """上下文管理器退出"""
        self.close()


# Global memory database instance
memory_db_instance: Optional[MemoryDB] = None


def init_memory_db(db_path: str = "data/memory.db") -> MemoryDB:
    """Initialize the global memory database instance."""
    """初始化全局内存数据库实例"""
    global memory_db_instance
    memory_db_instance = MemoryDB(db_path)
    return memory_db_instance


def get_memory_db() -> MemoryDB:
    """Get the global memory database instance."""
    """获取全局内存数据库实例"""
    if memory_db_instance is None:
        raise RuntimeError(
            "Memory database not initialized. Call init_memory_db() first."
        )
    return memory_db_instance
