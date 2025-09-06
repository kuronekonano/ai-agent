"""
AI Agent Framework - A modular framework for building autonomous AI agents
with ReAct (Reasoning + Acting) pattern implementation.
"""

import os
from pathlib import Path

import yaml

from .agent import ReActEngine
from .analyzer import Analyzer
from .model import AIClient, AnthropicClient, OpenAIClient
from .planner import Planner
from .tools import CalculatorTool, FileTool, ToolRegistry, WebSearchTool
from .trajectory import Trajectory, TrajectoryRecorder
from .visualizer import Visualizer


def load_config(config_path: str = "config/config.yaml") -> dict:
    """Load configuration from YAML file with environment variable overrides."""
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    
    # Override API keys from environment variables if they exist
    anthropic_api_key = os.environ.get("ANTHROPIC_AUTH_TOKEN")
    if anthropic_api_key and "anthropic" in config:
        config["anthropic"]["api_key"] = anthropic_api_key
    
    # Override OpenAI base URL from environment variable if it exists
    anthropic_base_url = os.environ.get("ANTHROPIC_BASE_URL")
    if anthropic_base_url and "openai" in config:
        config["openai"]["base_url"] = anthropic_base_url
    
    return config


__version__ = "0.1.0"
__all__ = [
    "AIClient",
    "OpenAIClient",
    "AnthropicClient",
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
    "load_config",
]
