"""
Configuration management for agent evaluation framework.
代理评估框架的配置管理
"""

import os
from typing import Any, Dict


class Config:
    """Configuration class with defaults and environment variable support.
    配置类，支持默认值和环境变量覆盖
    """

    def __init__(self):
        # Default configuration
        self.defaults = {
            "concurrency": 8,
            "timeout_seconds": 30,
            "max_retries": 3,
            "storage_path": "data/eval_runs",
            "cache_enabled": True,
            "cache_path": "data/cache",
            "model": {
                "name": "mock",
                "temperature": 0.0,
                "max_tokens": 1000,
            },
        }

        # Environment variable mappings
        self.env_mappings = {
            "AGENT_EVAL_CONCURRENCY": "concurrency",
            "AGENT_EVAL_TIMEOUT": "timeout_seconds",
            "AGENT_EVAL_MAX_RETRIES": "max_retries",
            "AGENT_EVAL_STORAGE_PATH": "storage_path",
            "AGENT_EVAL_CACHE_ENABLED": "cache_enabled",
            "AGENT_EVAL_CACHE_PATH": "cache_path",
            "AGENT_EVAL_MODEL_NAME": "model.name",
            "AGENT_EVAL_MODEL_TEMPERATURE": "model.temperature",
            "AGENT_EVAL_MODEL_MAX_TOKENS": "model.max_tokens",
        }

    def get_config(self) -> Dict[str, Any]:
        """Get configuration with environment variable overrides.
        获取配置，支持环境变量覆盖
        """
        config = self.defaults.copy()

        # Apply environment variable overrides
        for env_var, config_key in self.env_mappings.items():
            if env_var in os.environ:
                value = os.environ[env_var]
                self._set_nested_config(config, config_key, value)

        return config

    def _set_nested_config(self, config: Dict[str, Any], key_path: str, value: Any):
        """Set nested configuration value.
        设置嵌套配置值
        """
        keys = key_path.split(".")
        current = config

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        final_key = keys[-1]
        # Convert value types based on default
        if final_key in current:
            default_value = current[final_key]
            if isinstance(default_value, bool):
                value = value.lower() in ("true", "1", "yes")
            elif isinstance(default_value, int):
                value = int(value)
            elif isinstance(default_value, float):
                value = float(value)

        current[final_key] = value


def get_config() -> Dict[str, Any]:
    """Get the current configuration.
    获取当前配置
    """
    return Config().get_config()
