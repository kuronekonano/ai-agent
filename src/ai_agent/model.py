from abc import ABC, abstractmethod
from typing import Any, Dict, List

import anthropic
import openai


class AIClient(ABC):
    """Abstract base class for AI model clients."""

    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> str:
        """Generate completion for the given prompt."""
        pass

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate chat completion for the given messages."""
        pass


class OpenAIClient(AIClient):
    """OpenAI API client implementation."""

    def __init__(self, api_key: str, model: str = "gpt-4", **kwargs):
        # Extract base_url from kwargs if provided
        base_url = kwargs.pop("base_url", None)
        
        # Create OpenAI client with optional base_url
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        
        self.client = openai.OpenAI(**client_kwargs)
        self.model = model
        self.default_params = {"temperature": 0.7, "max_tokens": 2000, **kwargs}

    def complete(self, prompt: str, **kwargs) -> str:
        params = {**self.default_params, **kwargs}
        response = self.client.completions.create(
            model=self.model, prompt=prompt, **params
        )
        return response.choices[0].text.strip()

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        params = {**self.default_params, **kwargs}
        response = self.client.chat.completions.create(
            model=self.model, messages=messages, **params
        )
        return response.choices[0].message.content.strip()


class AnthropicClient(AIClient):
    """Anthropic API client implementation."""

    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229", **kwargs):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.default_params = {"temperature": 0.7, "max_tokens": 2000, **kwargs}

    def complete(self, prompt: str, **kwargs) -> str:
        params = {**self.default_params, **kwargs}
        response = self.client.completions.create(
            model=self.model, prompt=prompt, **params
        )
        return response.completion.strip()

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        params = {**self.default_params, **kwargs}

        anthropic_messages = []
        for msg in messages:
            if msg["role"] == "system":
                anthropic_messages.append(
                    {"role": "assistant", "content": msg["content"]}
                )
            else:
                anthropic_messages.append(msg)

        response = self.client.messages.create(
            model=self.model, messages=anthropic_messages, **params
        )
        return response.content[0].text.strip()


def create_client(config: Dict[str, Any]) -> AIClient:
    """Factory function to create appropriate AI client based on config."""
    provider = config.get("provider", "openai")

    if provider == "openai":
        return OpenAIClient(
            api_key=config["api_key"],
            model=config.get("model", "gpt-4"),
            temperature=config.get("temperature", 0.7),
            max_tokens=config.get("max_tokens", 2000),
            base_url=config.get("base_url"),
        )
    elif provider == "anthropic":
        return AnthropicClient(
            api_key=config["api_key"],
            model=config.get("model", "claude-3-sonnet-20240229"),
            temperature=config.get("temperature", 0.7),
            max_tokens=config.get("max_tokens", 2000),
        )
    else:
        raise ValueError(f"Unsupported AI provider: {provider}")
