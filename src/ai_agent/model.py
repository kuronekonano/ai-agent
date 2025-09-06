import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List

import anthropic
import openai

from .logger import get_logger
from .performance import PerformanceTracker


def estimate_tokens(text: str) -> int:
    """Estimate token count for text (approx 4 chars per token)."""
    """估算文本的Token数量（大约4个字符1个Token）"""
    return max(1, len(text) // 4)


logger = get_logger(__name__)


class AIClient(ABC):
    """Abstract base class for AI model clients."""

    """AI模型客户端的抽象基类"""

    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> str:
        """Generate completion for the given prompt."""
        """为给定的提示生成补全内容"""
        pass

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate chat completion for the given messages."""
        """为给定的消息生成聊天补全内容"""
        pass

    @abstractmethod
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics including token usage and costs."""
        """获取性能统计信息，包括Token使用情况和成本"""
        pass

    @abstractmethod
    def reset_performance_stats(self):
        """Reset performance tracking statistics."""
        """重置性能跟踪统计信息"""
        pass


class OpenAIClient(AIClient):
    """OpenAI API client implementation."""

    """OpenAI API客户端实现"""

    def __init__(self, api_key: str, model: str = "gpt-4", **kwargs):
        # Extract base_url from kwargs if provided
        # 从kwargs中提取base_url（如果提供）
        base_url = kwargs.pop("base_url", None)

        logger.info(f"Initializing OpenAI client with model: {model}")

        # Create OpenAI client with optional base_url
        # 创建OpenAI客户端，支持可选的base_url
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
            logger.debug(f"Using custom base URL: {base_url}")

        self.client = openai.OpenAI(**client_kwargs)
        self.model = model
        self.default_params = {"temperature": 0.7, "max_tokens": 2000, **kwargs}
        self.performance_tracker = PerformanceTracker()
        logger.debug(f"Default parameters: {self.default_params}")

    def complete(self, prompt: str, **kwargs) -> str:
        params = {**self.default_params, **kwargs}
        logger.debug(
            f"Sending completion request to {self.model}, prompt length: {len(prompt)}"
        )

        start_time = time.time()

        try:
            response = self.client.completions.create(
                model=self.model, prompt=prompt, **params
            )

            duration_ms = (time.time() - start_time) * 1000

            # Record API call with token usage
            self.performance_tracker.record_api_call(
                provider="openai",
                model=self.model,
                endpoint="completions",
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                duration_ms=duration_ms,
            )

            logger.debug(
                f"Completion response received, tokens: {response.usage.total_tokens}, "
                f"duration: {duration_ms:.2f}ms"
            )
            return response.choices[0].text.strip()

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            # Record failed API call
            self.performance_tracker.record_api_call(
                provider="openai",
                model=self.model,
                endpoint="completions",
                prompt_tokens=0,
                completion_tokens=0,
                duration_ms=duration_ms,
                success=False,
                error_message=str(e),
            )

            logger.error(f"Completion request failed: {str(e)}")
            raise

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        params = {**self.default_params, **kwargs}
        logger.debug(f"Sending chat request to {self.model}, messages: {len(messages)}")

        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.model, messages=messages, **params
            )

            duration_ms = (time.time() - start_time) * 1000

            # Record API call with token usage
            self.performance_tracker.record_api_call(
                provider="openai",
                model=self.model,
                endpoint="chat/completions",
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                duration_ms=duration_ms,
            )

            logger.debug(
                f"Chat response received, tokens: {response.usage.total_tokens}, "
                f"duration: {duration_ms:.2f}ms"
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            # Record failed API call
            self.performance_tracker.record_api_call(
                provider="openai",
                model=self.model,
                endpoint="chat/completions",
                prompt_tokens=0,
                completion_tokens=0,
                duration_ms=duration_ms,
                success=False,
                error_message=str(e),
            )

            logger.error(f"Chat request failed: {str(e)}")
            raise

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics including token usage and costs."""
        """获取性能统计信息，包括Token使用情况和成本"""
        return self.performance_tracker.get_statistics()

    def reset_performance_stats(self):
        """Reset performance tracking statistics."""
        """重置性能跟踪统计信息"""
        self.performance_tracker.reset()


def create_client(config: Dict[str, Any]) -> AIClient:
    """Factory function to create appropriate AI client based on config."""
    """根据配置创建适当的AI客户端的工厂函数"""
    provider = config.get("provider", "openai")
    logger.info(f"Creating AI client for provider: {provider}")

    if provider == "openai":
        logger.debug("Creating OpenAI client")
        return OpenAIClient(
            api_key=config["api_key"],
            model=config.get("model", "deepseek-chat"),
            temperature=config.get("temperature", 0.7),
            max_tokens=config.get("max_tokens", 2000),
            base_url=config.get("base_url"),
        )
    else:
        logger.error(f"Unsupported AI provider: {provider}")
        raise ValueError(f"Unsupported AI provider: {provider}")
