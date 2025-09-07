"""
Model client abstraction for agent evaluation framework.
代理评估框架的模型客户端抽象
"""

import asyncio
import hashlib
import json
import os
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from .config import get_config


class ModelClient(ABC):
    """Abstract base class for model clients.
    模型客户端的抽象基类
    """

    @abstractmethod
    async def call(self, prompt: str, **params) -> Dict[str, Any]:
        """Call the model with given prompt and parameters.
        使用给定的提示和参数调用模型

        Returns:
            Dictionary with keys: text, usage, latency_ms, raw
            返回包含文本、使用量、延迟和原始数据的字典
        """
        pass


class MockModelClient(ModelClient):
    """Mock model client for testing and development.
    用于测试和开发的模拟模型客户端
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.cache_enabled = self.config.get("cache_enabled", True)
        self.cache_path = self.config.get("cache_path", "data/cache")

        if self.cache_enabled:
            os.makedirs(self.cache_path, exist_ok=True)

    async def call(self, prompt: str, **params) -> Dict[str, Any]:
        """Mock model call that simulates API response.
        模拟API响应的模型调用
        """
        start_time = time.time()

        # Generate cache key
        cache_key = self._generate_cache_key(prompt, params)

        # Check cache first
        if self.cache_enabled:
            cached_response = self._get_from_cache(cache_key)
            if cached_response:
                cached_response["latency_ms"] = 1  # Fast cache retrieval
                return cached_response

        # Simulate API call delay
        await asyncio.sleep(0.1)  # 100ms delay

        # Generate mock response
        response_text = f"Mock response to: {prompt[:50]}..."

        response = {
            "text": response_text,
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(response_text.split()),
                "total_tokens": len(prompt.split()) + len(response_text.split()),
            },
            "latency_ms": (time.time() - start_time) * 1000,
            "raw": {"choices": [{"message": {"content": response_text}}]},
        }

        # Cache the response
        if self.cache_enabled:
            self._save_to_cache(cache_key, response)

        return response

    def _generate_cache_key(self, prompt: str, params: Dict[str, Any]) -> str:
        """Generate cache key from prompt and parameters.
        根据提示和参数生成缓存键
        """
        key_data = prompt + json.dumps(params, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()

    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get response from cache.
        从缓存中获取响应
        """
        cache_file = os.path.join(self.cache_path, f"{cache_key}.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return None
        return None

    def _save_to_cache(self, cache_key: str, response: Dict[str, Any]):
        """Save response to cache.
        保存响应到缓存
        """
        cache_file = os.path.join(self.cache_path, f"{cache_key}.json")
        try:
            with open(cache_file, "w") as f:
                json.dump(response, f)
        except IOError:
            pass  # Silently fail if cache write fails


def create_client(config: Optional[Dict[str, Any]] = None) -> ModelClient:
    """Factory function to create appropriate model client.
    创建适当模型客户端的工厂函数
    """
    config = config or get_config()
    model_config = config.get("model", {})
    model_name = model_config.get("name", "mock")

    if model_name == "mock":
        return MockModelClient(model_config)
    else:
        # For now, default to mock client
        return MockModelClient(model_config)


# Example usage for other client types (to be implemented later)
class OpenAIClient(ModelClient):
    """OpenAI API client implementation.
    OpenAI API客户端实现
    """

    async def call(self, prompt: str, **params) -> Dict[str, Any]:
        # TODO: Implement actual OpenAI API call
        raise NotImplementedError("OpenAIClient not implemented yet")


class ClaudeClient(ModelClient):
    """Claude API client implementation.
    Claude API客户端实现
    """

    async def call(self, prompt: str, **params) -> Dict[str, Any]:
        # TODO: Implement actual Claude API call
        raise NotImplementedError("ClaudeClient not implemented yet")
