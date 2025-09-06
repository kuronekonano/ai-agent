"""
Performance tracking module for AI Agent Framework.
Provides token counting, API call statistics, and cost calculation.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from .database import get_database
from .logger import get_logger

"""
AI代理框架的性能跟踪模块。
提供Token计数、API调用统计和成本计算功能。
"""

logger = get_logger(__name__)


@dataclass
class TokenUsage:
    """Token使用统计数据类"""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class APICallRecord:
    """API调用记录数据类"""

    timestamp: str
    provider: str
    model: str
    endpoint: str
    token_usage: TokenUsage
    duration_ms: float
    success: bool
    error_message: Optional[str] = None


@dataclass
class CostCalculation:
    """成本计算结果数据类"""

    input_cost: float
    output_cost: float
    total_cost: float
    currency: str = "USD"


class PerformanceTracker:
    """Performance tracking and cost calculation system."""

    """性能跟踪和成本计算系统"""

    # Model pricing (per 1K tokens) - update as needed
    MODEL_PRICING = {
        "openai": {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
            "deepseek-chat": {"input": 0.00014, "output": 0.00028},
        },
    }

    def __init__(self):
        self.api_calls: List[APICallRecord] = []
        self.total_token_usage = TokenUsage()
        logger.debug("PerformanceTracker initialized")

    def record_api_call(
        self,
        provider: str,
        model: str,
        endpoint: str,
        prompt_tokens: int,
        completion_tokens: int,
        duration_ms: float,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> APICallRecord:
        """Record an API call with token usage and timing."""
        """记录API调用，包括Token使用情况和时间"""
        timestamp = datetime.now().isoformat()
        total_tokens = prompt_tokens + completion_tokens

        token_usage = TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )

        # Update total usage
        self.total_token_usage.prompt_tokens += prompt_tokens
        self.total_token_usage.completion_tokens += completion_tokens
        self.total_token_usage.total_tokens += total_tokens

        record = APICallRecord(
            timestamp=timestamp,
            provider=provider,
            model=model,
            endpoint=endpoint,
            token_usage=token_usage,
            duration_ms=duration_ms,
            success=success,
            error_message=error_message,
        )

        self.api_calls.append(record)

        # Save to database
        try:
            db = get_database()
            api_call_data = {
                "timestamp": timestamp,
                "provider": provider,
                "model": model,
                "endpoint": endpoint,
                "token_usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                },
                "duration_ms": duration_ms,
                "success": success,
                "error_message": error_message,
                "cost": asdict(self.calculate_cost(provider, model, token_usage)),
            }
            db.save_api_call(api_call_data)
            logger.debug("API call saved to database")
        except Exception as e:
            logger.error(f"Failed to save API call to database: {str(e)}")

        logger.debug(
            f"API call recorded: {provider}/{model} - "
            f"{prompt_tokens} prompt + {completion_tokens} completion tokens, "
            f"{duration_ms:.2f}ms"
        )

        return record

    def calculate_cost(
        self, provider: str, model: str, token_usage: TokenUsage
    ) -> CostCalculation:
        """Calculate cost for token usage."""
        """计算Token使用成本"""
        pricing = self.MODEL_PRICING.get(provider, {}).get(model)

        if not pricing:
            logger.warning(f"No pricing found for {provider}/{model}")
            return CostCalculation(0, 0, 0)

        input_cost = (token_usage.prompt_tokens / 1000) * pricing["input"]
        output_cost = (token_usage.completion_tokens / 1000) * pricing["output"]
        total_cost = input_cost + output_cost

        return CostCalculation(
            input_cost=input_cost, output_cost=output_cost, total_cost=total_cost
        )

    def get_total_cost(self) -> CostCalculation:
        """Calculate total cost across all API calls."""
        """计算所有API调用的总成本"""
        total_input_cost = 0
        total_output_cost = 0

        for call in self.api_calls:
            cost = self.calculate_cost(call.provider, call.model, call.token_usage)
            total_input_cost += cost.input_cost
            total_output_cost += cost.output_cost

        return CostCalculation(
            input_cost=total_input_cost,
            output_cost=total_output_cost,
            total_cost=total_input_cost + total_output_cost,
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        """获取全面的性能统计信息"""
        total_calls = len(self.api_calls)
        successful_calls = sum(1 for call in self.api_calls if call.success)
        failed_calls = total_calls - successful_calls

        total_duration = sum(call.duration_ms for call in self.api_calls)
        avg_duration = total_duration / total_calls if total_calls > 0 else 0

        # Group by provider and model
        provider_stats = {}
        for call in self.api_calls:
            key = f"{call.provider}/{call.model}"
            if key not in provider_stats:
                provider_stats[key] = {
                    "calls": 0,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                    "duration_ms": 0,
                }

            provider_stats[key]["calls"] += 1
            provider_stats[key]["prompt_tokens"] += call.token_usage.prompt_tokens
            provider_stats[key][
                "completion_tokens"
            ] += call.token_usage.completion_tokens
            provider_stats[key]["total_tokens"] += call.token_usage.total_tokens
            provider_stats[key]["duration_ms"] += call.duration_ms

        total_cost = self.get_total_cost()

        return {
            "total_api_calls": total_calls,
            "successful_calls": successful_calls,
            "failed_calls": failed_calls,
            "success_rate": successful_calls / total_calls if total_calls > 0 else 0,
            "total_token_usage": {
                "prompt_tokens": self.total_token_usage.prompt_tokens,
                "completion_tokens": self.total_token_usage.completion_tokens,
                "total_tokens": self.total_token_usage.total_tokens,
            },
            "total_duration_ms": total_duration,
            "average_duration_ms": avg_duration,
            "provider_statistics": provider_stats,
            "cost_summary": {
                "total_cost": total_cost.total_cost,
                "input_cost": total_cost.input_cost,
                "output_cost": total_cost.output_cost,
                "currency": total_cost.currency,
            },
        }

    def reset(self):
        """Reset all performance tracking data."""
        """重置所有性能跟踪数据"""
        logger.debug("Resetting performance tracker")
        self.api_calls.clear()
        self.total_token_usage = TokenUsage()

    def save_statistics_to_db(self):
        """Save current performance statistics to the database."""
        """将当前性能统计信息保存到数据库"""
        try:
            stats = self.get_statistics()
            db = get_database()
            db.save_performance_stats(stats)
            logger.debug("Performance statistics saved to database")
        except Exception as e:
            logger.error(f"Failed to save performance statistics to database: {str(e)}")

    def export_to_json(self) -> str:
        """Export performance data to JSON format."""
        """将性能数据导出为JSON格式"""
        import json

        data = {
            "timestamp": datetime.now().isoformat(),
            "statistics": self.get_statistics(),
            "api_calls": [
                {
                    "timestamp": call.timestamp,
                    "provider": call.provider,
                    "model": call.model,
                    "endpoint": call.endpoint,
                    "token_usage": {
                        "prompt_tokens": call.token_usage.prompt_tokens,
                        "completion_tokens": call.token_usage.completion_tokens,
                        "total_tokens": call.token_usage.total_tokens,
                    },
                    "duration_ms": call.duration_ms,
                    "success": call.success,
                    "error_message": call.error_message,
                }
                for call in self.api_calls
            ],
        }

        return json.dumps(data, indent=2, ensure_ascii=False)

    def save_to_file(self, filepath: str):
        """Save performance data to a JSON file."""
        """将性能数据保存到JSON文件"""
        json_data = self.export_to_json()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(json_data)
        logger.info(f"Performance data saved to {filepath}")
