"""
AI Agent Framework - A modular framework for building autonomous AI agents
with ReAct (Reasoning + Acting) pattern implementation.
"""

import os
from pathlib import Path

import yaml

from .agent import ReActEngine
from .analyzer import Analyzer
from .logger import get_logger, setup_logging
from .model import AIClient, OpenAIClient
from .performance import APICallRecord, CostCalculation, PerformanceTracker, TokenUsage
from .planner import Planner
from .tools import CalculatorTool, FileTool, ToolRegistry, WebSearchTool
from .trajectory import Trajectory, TrajectoryRecorder
from .visualizer import Visualizer

"""
AI代理框架 - 用于构建自主AI代理的模块化框架
实现ReAct（推理+行动）模式
"""


def load_config(config_path: str = "config/config.yaml") -> dict:
    """Load configuration from YAML file with environment variable overrides."""
    """从YAML文件加载配置，支持环境变量覆盖"""
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

    # Override API keys from environment variables if they exist
    # 如果存在环境变量，则覆盖API密钥
    api_key = os.environ.get("AIAGENT_AUTH_TOKEN", config["openai"].get("api_key"))
    config["openai"]["api_key"] = api_key

    # Override OpenAI base URL from environment variable if it exists
    # 如果存在环境变量，则覆盖OpenAI基础URL
    base_url = os.environ.get("AIAGENT_BASE_URL", config["openai"].get("base_url"))
    config["openai"]["base_url"] = base_url

    return config


__version__ = "0.1.0"
__all__ = [
    "AIClient",
    "OpenAIClient",
    "ReActEngine",
    "Planner",
    "ToolRegistry",
    "FileTool",
    "CalculatorTool",
    "WebSearchTool",
    "Trajectory",
    "TrajectoryRecorder",
    "Analyzer",
    "Visualizer",
    "PerformanceTracker",
    "TokenUsage",
    "APICallRecord",
    "CostCalculation",
    "load_config",
    "get_logger",
    "setup_logging",
]
