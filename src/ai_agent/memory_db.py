"""
Memory Database module for long-term memory and event recording using SQLite.
Provides persistent storage for notes, events, and memories with rich metadata.
"""

import json
import os
import sqlite3
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from .logger import get_logger

"""
AI代理框架的内存数据库模块。
使用SQLite提供笔记、事件和记忆的持久化存储，包含丰富的元数据。
"""

logger = get_logger(__name__)


class PriorityLevel(Enum):
    """Priority levels for memory records."""

    """记忆记录的优先级级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Status(Enum):
    """Status values for memory records."""

    """记忆记录的状态值"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class MemoryDBTool:
    """Tool for long-term memory storage and retrieval using SQLite."""

    """使用SQLite进行长期记忆存储和检索的工具"""

    def __init__(self, db_path: str = "data/memory.db"):
        """Initialize the memory database."""
        """初始化内存数据库"""
        # Ensure data directory exists
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

        self.db_path = db_path
        self._init_database()
        logger.info(f"Memory database initialized at {db_path}")

    def _init_database(self):
        """Initialize the database schema."""
        """初始化数据库模式"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create memories table with comprehensive schema
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    tags TEXT,  -- JSON array of tags
                    unique_tag TEXT UNIQUE,  -- Unique identifier for the record
                    priority TEXT CHECK(priority IN ('low', 'medium', 'high', 'critical')),
                    status TEXT CHECK(status IN ('pending', 'in_progress', 'completed', 'cancelled', 'expired')),
                    source TEXT,
                    metadata TEXT,  -- JSON object for additional metadata
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NULL
                )
            """
            )

            # Create indexes for better query performance
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_memories_tags ON memories(tags)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_memories_priority ON memories(priority)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_memories_status ON memories(status)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_memories_updated ON memories(updated_at)"
            )

            conn.commit()

    def execute(self, **kwargs) -> Any:
        """Execute memory database operations."""
        """执行内存数据库操作"""
        operation = kwargs.get("operation")
        logger.info(f"Executing memory DB operation: {operation} with args: {kwargs}")

        start_time = datetime.now()
        success = True

        try:
            if operation == "create":
                result = self.create_memory(**kwargs)
            elif operation == "read":
                result = self.read_memory(**kwargs)
            elif operation == "update":
                result = self.update_memory(**kwargs)
            elif operation == "delete":
                result = self.delete_memory(**kwargs)
            elif operation == "search":
                result = self.search_memories(**kwargs)
            elif operation == "get_by_tag":
                result = self.get_memories_by_tag(**kwargs)
            elif operation == "get_by_time_range":
                result = self.get_memories_by_time_range(**kwargs)
            elif operation == "get_by_status":
                result = self.get_memories_by_status(**kwargs)
            elif operation == "get_by_priority":
                result = self.get_memories_by_priority(**kwargs)
            elif operation == "stats":
                result = self.get_statistics()
            else:
                logger.error(f"Unknown memory DB operation: {operation}")
                raise ValueError(f"Unknown memory DB operation: {operation}")

            logger.debug(f"Memory DB operation successful: {result}")
            return result
        except Exception as e:
            success = False
            logger.error(f"Memory DB operation failed: {str(e)}")
            raise
        finally:
            # Record tool usage
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            self._record_tool_usage(operation, duration_ms, success)

    def get_description(self) -> str:
        """Get description of the memory database tool."""
        """获取内存数据库工具的描述"""
        return """memory_db: Long-term memory storage and retrieval using SQLite database.
Operations:
- create(content, tags, unique_tag, priority, status, source, metadata, expires_at): Create a new memory record
- read(id): Read a specific memory by ID
- update(id, content, tags, priority, status, metadata): Update an existing memory
- delete(id): Delete a memory by ID
- search(query): Search memories by content (full-text search)
- get_by_tag(tag): Get all memories with a specific tag
- get_by_time_range(start_time, end_time): Get memories within time range
- get_by_status(status): Get memories by status (pending, in_progress, completed, cancelled, expired)
- get_by_priority(priority): Get memories by priority (low, medium, high, critical)
- stats(): Get database statistics

Fields:
- id: Unique identifier (auto-generated)
- content: Main content/text of the memory
- tags: Array of tags for categorization (e.g., ["work", "meeting", "urgent"])
- unique_tag: Unique string identifier for the record
- priority: Priority level (low, medium, high, critical)
- status: Current status (pending, in_progress, completed, cancelled, expired)
- source: Source of the memory (e.g., "user_input", "system_generated")
- metadata: Additional metadata as JSON object
- created_at: Creation timestamp
- updated_at: Last update timestamp
- expires_at: Optional expiration timestamp

Example usage:
- Create a work-related task: create(content="Complete project report", tags=["work", "urgent"], priority="high", status="pending")
- Search for financial records: search(query="finance budget")
- Get all completed tasks: get_by_status(status="completed")
- Update task status: update(id=1, status="completed")
"""

    def _record_tool_usage(
        self, operation: str, duration_ms: float, success: bool = True
    ):
        """Record tool usage to the metrics database."""
        """将工具使用情况记录到指标数据库"""
        try:
            from .database import get_database

            db = get_database()
            db.record_tool_usage("memory_db", operation, duration_ms, success)
            logger.debug(f"Memory DB usage recorded: {operation}")
        except Exception as e:
            logger.error(f"Failed to record memory DB usage: {str(e)}")

    def create_memory(self, **kwargs) -> Dict[str, Any]:
        """Create a new memory record."""
        """创建新的记忆记录"""
        content = kwargs.get("content")
        if not content:
            raise ValueError("Content is required for creating a memory")

        # Prepare data for insertion
        tags = json.dumps(kwargs.get("tags", []))
        unique_tag = kwargs.get("unique_tag")
        priority = kwargs.get("priority")
        status = kwargs.get("status", "pending")
        source = kwargs.get("source", "user_input")
        metadata = json.dumps(kwargs.get("metadata", {}))

        # Handle expiration date
        expires_at = kwargs.get("expires_at")
        if expires_at and isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO memories (content, tags, unique_tag, priority, status, source, metadata, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    content,
                    tags,
                    unique_tag,
                    priority,
                    status,
                    source,
                    metadata,
                    expires_at,
                ),
            )

            memory_id = cursor.lastrowid
            conn.commit()

            # Return the created memory
            memory = self._get_memory_by_id(memory_id)
            if memory is None:
                raise ValueError(f"Failed to retrieve created memory with ID {memory_id}")
            return memory

    def read_memory(self, **kwargs) -> Optional[Dict[str, Any]]:
        """Read a specific memory by ID."""
        """通过ID读取特定的记忆"""
        memory_id = kwargs.get("id")
        if not memory_id:
            raise ValueError("Memory ID is required")

        return self._get_memory_by_id(memory_id)

    def _get_memory_by_id(self, memory_id: int) -> Optional[Dict[str, Any]]:
        """Internal method to get memory by ID."""
        """通过ID获取记忆的内部方法"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM memories WHERE id = ?", (memory_id,))
            row = cursor.fetchone()

            if row:
                return self._row_to_dict(row)
            return None

    def update_memory(self, **kwargs) -> Optional[Dict[str, Any]]:
        """Update an existing memory record."""
        """更新现有的记忆记录"""
        memory_id = kwargs.get("id")
        if not memory_id:
            raise ValueError("Memory ID is required for update")

        # Check if memory exists
        existing = self._get_memory_by_id(memory_id)
        if not existing:
            return None

        # Build update query dynamically based on provided fields
        update_fields = []
        update_values = []

        if "content" in kwargs:
            update_fields.append("content = ?")
            update_values.append(kwargs["content"])

        if "tags" in kwargs:
            update_fields.append("tags = ?")
            update_values.append(json.dumps(kwargs["tags"]))

        if "unique_tag" in kwargs:
            update_fields.append("unique_tag = ?")
            update_values.append(kwargs["unique_tag"])

        if "priority" in kwargs:
            update_fields.append("priority = ?")
            update_values.append(kwargs["priority"])

        if "status" in kwargs:
            update_fields.append("status = ?")
            update_values.append(kwargs["status"])

        if "source" in kwargs:
            update_fields.append("source = ?")
            update_values.append(kwargs["source"])

        if "metadata" in kwargs:
            update_fields.append("metadata = ?")
            update_values.append(json.dumps(kwargs["metadata"]))

        if "expires_at" in kwargs:
            expires_at = kwargs["expires_at"]
            if expires_at and isinstance(expires_at, str):
                expires_at = datetime.fromisoformat(expires_at)
            update_fields.append("expires_at = ?")
            update_values.append(expires_at)

        # Always update the updated_at timestamp
        update_fields.append("updated_at = CURRENT_TIMESTAMP")

        if not update_fields:
            return existing  # No changes to make

        update_values.append(memory_id)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = f"UPDATE memories SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, update_values)
            conn.commit()

            return self._get_memory_by_id(memory_id)

    def delete_memory(self, **kwargs) -> bool:
        """Delete a memory record by ID."""
        """通过ID删除记忆记录"""
        memory_id = kwargs.get("id")
        if not memory_id:
            raise ValueError("Memory ID is required for deletion")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            conn.commit()

            return cursor.rowcount > 0

    def search_memories(self, **kwargs) -> List[Dict[str, Any]]:
        """Search memories by content using full-text search."""
        """通过内容使用全文搜索搜索记忆"""
        query = kwargs.get("query")
        if not query:
            raise ValueError("Search query is required")

        limit = kwargs.get("limit", 50)
        offset = kwargs.get("offset", 0)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM memories 
                WHERE content LIKE ? 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            """,
                (f"%{query}%", limit, offset),
            )

            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def get_memories_by_tag(self, **kwargs) -> List[Dict[str, Any]]:
        """Get all memories with a specific tag."""
        """获取具有特定标签的所有记忆"""
        tag = kwargs.get("tag")
        if not tag:
            raise ValueError("Tag is required")

        limit = kwargs.get("limit", 50)
        offset = kwargs.get("offset", 0)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM memories 
                WHERE tags LIKE ? 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            """,
                (f"%{tag}%", limit, offset),
            )

            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def get_memories_by_time_range(self, **kwargs) -> List[Dict[str, Any]]:
        """Get memories within a specific time range."""
        """获取特定时间范围内的记忆"""
        start_time = kwargs.get("start_time")
        end_time = kwargs.get("end_time")

        if not start_time or not end_time:
            raise ValueError("Both start_time and end_time are required")

        # Convert string timestamps to datetime objects if needed
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time)
        if isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time)

        limit = kwargs.get("limit", 50)
        offset = kwargs.get("offset", 0)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM memories 
                WHERE created_at BETWEEN ? AND ? 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            """,
                (start_time, end_time, limit, offset),
            )

            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def get_memories_by_status(self, **kwargs) -> List[Dict[str, Any]]:
        """Get memories by status."""
        """按状态获取记忆"""
        status = kwargs.get("status")
        if not status:
            raise ValueError("Status is required")

        limit = kwargs.get("limit", 50)
        offset = kwargs.get("offset", 0)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM memories 
                WHERE status = ? 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            """,
                (status, limit, offset),
            )

            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def get_memories_by_priority(self, **kwargs) -> List[Dict[str, Any]]:
        """Get memories by priority level."""
        """按优先级级别获取记忆"""
        priority = kwargs.get("priority")
        if not priority:
            raise ValueError("Priority is required")

        limit = kwargs.get("limit", 50)
        offset = kwargs.get("offset", 0)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM memories 
                WHERE priority = ? 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            """,
                (priority, limit, offset),
            )

            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        """获取数据库统计信息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Total memories
            cursor.execute("SELECT COUNT(*) FROM memories")
            total_memories = cursor.fetchone()[0]

            # Memories by status
            cursor.execute("SELECT status, COUNT(*) FROM memories GROUP BY status")
            status_stats = {row[0]: row[1] for row in cursor.fetchall()}

            # Memories by priority
            cursor.execute("SELECT priority, COUNT(*) FROM memories GROUP BY priority")
            priority_stats = {row[0]: row[1] for row in cursor.fetchall() if row[0]}

            # Recent activity
            cursor.execute(
                "SELECT COUNT(*) FROM memories WHERE updated_at > datetime('now', '-7 days')"
            )
            recent_activity = cursor.fetchone()[0]

            return {
                "total_memories": total_memories,
                "status_distribution": status_stats,
                "priority_distribution": priority_stats,
                "recent_activity_7d": recent_activity,
                "timestamp": datetime.now().isoformat(),
            }

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert SQLite row to dictionary with proper type conversion."""
        """将SQLite行转换为具有适当类型转换的字典"""
        result = dict(row)

        # Parse JSON fields
        if result.get("tags"):
            result["tags"] = json.loads(result["tags"])
        else:
            result["tags"] = []

        if result.get("metadata"):
            result["metadata"] = json.loads(result["metadata"])
        else:
            result["metadata"] = {}

        # Convert timestamps to ISO format
        for time_field in ["created_at", "updated_at", "expires_at"]:
            if result.get(time_field) and isinstance(result[time_field], str):
                result[time_field] = datetime.fromisoformat(
                    result[time_field]
                ).isoformat()

        return result

    def close(self):
        """Close the database connection."""
        """关闭数据库连接"""
        # SQLite connections are closed automatically when using context manager
        pass

    def __enter__(self):
        """Context manager entry."""
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        """上下文管理器退出"""
        self.close()
