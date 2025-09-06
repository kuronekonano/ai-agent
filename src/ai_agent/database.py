"""
Database module for persistent storage of metrics and analytics using TinyDB.
Provides centralized data persistence for performance statistics, trajectories, and API calls.
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from tinydb import Query, TinyDB
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage

from .logger import get_logger

"""
AI代理框架的数据库模块。
使用TinyDB提供性能统计、轨迹和API调用的集中式数据持久化。
"""

logger = get_logger(__name__)


class DatabaseManager:
    """Manages persistent storage for metrics, trajectories, and API calls."""

    """管理指标、轨迹和API调用的持久化存储"""

    def __init__(self, db_path: str = "data/ai_agent_metrics.json"):
        """Initialize the database manager."""
        """初始化数据库管理器"""
        # Ensure data directory exists
        db_dir = os.path.dirname(db_path)
        if db_dir:  # Only create directory if path contains directories
            os.makedirs(db_dir, exist_ok=True)

        # Initialize TinyDB with caching for better performance
        self.db = TinyDB(db_path, storage=CachingMiddleware(JSONStorage))

        # Define tables
        self.trajectories_table = self.db.table("trajectories")
        self.performance_table = self.db.table("performance")
        self.api_calls_table = self.db.table("api_calls")
        self.tool_usage_table = self.db.table("tool_usage")

        logger.info(f"Database initialized at {db_path}")

    def save_trajectory(self, trajectory_data: Dict[str, Any]) -> int:
        """Save a complete execution trajectory to the database."""
        """将完整的执行轨迹保存到数据库"""
        trajectory_data["saved_at"] = datetime.now().isoformat()
        doc_id = self.trajectories_table.insert(trajectory_data)
        logger.debug(f"Trajectory saved with ID: {doc_id}")
        return doc_id

    def get_trajectory(self, doc_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a trajectory by its document ID."""
        """通过文档ID检索轨迹"""
        return self.trajectories_table.get(doc_id=doc_id)

    def get_all_trajectories(self) -> List[Dict[str, Any]]:
        """Retrieve all trajectories from the database."""
        """从数据库检索所有轨迹"""
        return self.trajectories_table.all()

    def get_trajectories_by_task(self, task_pattern: str) -> List[Dict[str, Any]]:
        """Retrieve trajectories matching a task pattern."""
        """检索匹配任务模式的轨迹"""
        Trajectory = Query()
        return self.trajectories_table.search(
            Trajectory.task.matches(f".*{task_pattern}.*")
        )

    def save_performance_stats(self, stats_data: Dict[str, Any]) -> int:
        """Save performance statistics to the database."""
        """将性能统计信息保存到数据库"""
        stats_data["timestamp"] = datetime.now().isoformat()
        doc_id = self.performance_table.insert(stats_data)
        logger.debug(f"Performance stats saved with ID: {doc_id}")
        return doc_id

    def get_latest_performance_stats(self) -> Optional[Dict[str, Any]]:
        """Retrieve the latest performance statistics."""
        """检索最新的性能统计信息"""
        all_stats = self.performance_table.all()
        if not all_stats:
            return None
        return max(all_stats, key=lambda x: x.get("timestamp", ""))

    def get_all_performance_stats(self) -> List[Dict[str, Any]]:
        """Retrieve all performance statistics."""
        """检索所有性能统计信息"""
        return self.performance_table.all()

    def save_api_call(self, api_call_data: Dict[str, Any]) -> int:
        """Save an individual API call record."""
        """保存单个API调用记录"""
        api_call_data["saved_at"] = datetime.now().isoformat()
        doc_id = self.api_calls_table.insert(api_call_data)
        logger.debug(f"API call saved with ID: {doc_id}")
        return doc_id

    def save_bulk_api_calls(self, api_calls: List[Dict[str, Any]]) -> List[int]:
        """Save multiple API call records in bulk."""
        """批量保存多个API调用记录"""
        for call in api_calls:
            call["saved_at"] = datetime.now().isoformat()
        doc_ids = self.api_calls_table.insert_multiple(api_calls)
        logger.debug(f"Bulk API calls saved: {len(doc_ids)} records")
        return doc_ids

    def get_api_calls_by_provider(self, provider: str) -> List[Dict[str, Any]]:
        """Retrieve API calls for a specific provider."""
        """检索特定提供商的API调用"""
        API_Call = Query()
        return self.api_calls_table.search(API_Call.provider == provider)

    def get_api_calls_by_model(self, model: str) -> List[Dict[str, Any]]:
        """Retrieve API calls for a specific model."""
        """检索特定模型的API调用"""
        API_Call = Query()
        return self.api_calls_table.search(API_Call.model == model)

    def record_tool_usage(
        self, tool_name: str, operation: str, duration_ms: float, success: bool = True
    ) -> int:
        """Record tool usage statistics."""
        """记录工具使用统计信息"""
        tool_data = {
            "tool_name": tool_name,
            "operation": operation,
            "duration_ms": duration_ms,
            "success": success,
            "timestamp": datetime.now().isoformat(),
        }
        doc_id = self.tool_usage_table.insert(tool_data)
        logger.debug(f"Tool usage recorded: {tool_name}.{operation}")
        return doc_id

    def get_tool_usage_stats(self, tool_name: str = None) -> Dict[str, Any]:
        """Get statistics for tool usage."""
        """获取工具使用统计信息"""
        all_usage = self.tool_usage_table.all()

        if tool_name:
            all_usage = [u for u in all_usage if u["tool_name"] == tool_name]

        if not all_usage:
            return {"total_uses": 0, "success_rate": 0, "avg_duration_ms": 0}

        total_uses = len(all_usage)
        successful_uses = sum(1 for u in all_usage if u["success"])
        total_duration = sum(u["duration_ms"] for u in all_usage)

        return {
            "total_uses": total_uses,
            "success_rate": successful_uses / total_uses if total_uses > 0 else 0,
            "avg_duration_ms": total_duration / total_uses if total_uses > 0 else 0,
            "total_duration_ms": total_duration,
        }

    def get_aggregate_statistics(self) -> Dict[str, Any]:
        """Get aggregate statistics across all data."""
        """获取所有数据的聚合统计信息"""
        trajectories = self.trajectories_table.all()
        performance_stats = self.performance_table.all()
        api_calls = self.api_calls_table.all()
        tool_usage = self.tool_usage_table.all()

        # Calculate trajectory statistics
        total_trajectories = len(trajectories)
        successful_trajectories = sum(
            1 for t in trajectories if t.get("success", False)
        )

        # Calculate API call statistics
        total_api_calls = len(api_calls)
        successful_api_calls = sum(
            1 for call in api_calls if call.get("success", False)
        )

        # Calculate total tokens and cost
        total_tokens = sum(
            call.get("token_usage", {}).get("total_tokens", 0) for call in api_calls
        )
        total_cost = sum(
            call.get("cost", {}).get("total_cost", 0) for call in api_calls
        )

        return {
            "trajectories": {
                "total": total_trajectories,
                "successful": successful_trajectories,
                "success_rate": (
                    successful_trajectories / total_trajectories
                    if total_trajectories > 0
                    else 0
                ),
            },
            "api_calls": {
                "total": total_api_calls,
                "successful": successful_api_calls,
                "success_rate": (
                    successful_api_calls / total_api_calls if total_api_calls > 0 else 0
                ),
                "total_tokens": total_tokens,
                "total_cost": total_cost,
            },
            "tool_usage": {
                "total_operations": len(tool_usage),
                "unique_tools": len(set(u["tool_name"] for u in tool_usage)),
            },
            "timestamp": datetime.now().isoformat(),
        }

    def clear_all_data(self):
        """Clear all data from the database (for testing/reset)."""
        """清除数据库中的所有数据（用于测试/重置）"""
        self.db.drop_tables()
        logger.warning("All database data cleared")

    def close(self):
        """Close the database connection."""
        """关闭数据库连接"""
        self.db.close()
        logger.debug("Database connection closed")

    def __enter__(self):
        """Context manager entry."""
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        """上下文管理器退出"""
        self.close()


# Global database instance for easy access
database_manager: Optional[DatabaseManager] = None


def init_database(db_path: str = "data/ai_agent_metrics.json") -> DatabaseManager:
    """Initialize the global database instance."""
    """初始化全局数据库实例"""
    global database_manager
    database_manager = DatabaseManager(db_path)
    return database_manager


def get_database() -> DatabaseManager:
    """Get the global database instance."""
    """获取全局数据库实例"""
    if database_manager is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return database_manager
