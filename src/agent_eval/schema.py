"""
Data models for agent evaluation framework.
代理评估框架的数据模型
"""

import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class TestCase:
    """A single test case with prompt and expected output.
    单个测试用例，包含提示和期望输出
    """

    id: str
    prompt: str
    expected: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization.
        转换为字典用于序列化
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestCase":
        """Create from dictionary.
        从字典创建测试用例
        """
        return cls(**data)


@dataclass
class RunMeta:
    """Metadata about a test run.
    测试运行的元数据
    """

    run_id: str
    test_suite_id: str
    model: Dict[str, Any]
    started_at: str
    commit: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization.
        转换为字典用于序列化
        """
        return asdict(self)


@dataclass
class ExecutionRecord:
    """Record of a single test case execution.
    单个测试用例执行的记录
    """

    run_id: str
    test_case_id: str
    prompt: Dict[str, Any]
    response: Dict[str, Any]
    scoring: Dict[str, Any]
    status: str
    created_at: str
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization.
        转换为字典用于序列化
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionRecord":
        """Create from dictionary."""
        return cls(**data)


def generate_run_id() -> str:
    """Generate a unique run ID."""
    return f"run-{uuid.uuid4().hex[:8]}"


def now_iso() -> str:
    """Get current time in ISO format."""
    return datetime.now().isoformat()
