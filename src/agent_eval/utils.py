"""
Utility functions for agent evaluation framework.
"""

import hashlib
import json
import time
from datetime import datetime
from typing import Any


def now_iso() -> str:
    """Get current time in ISO format."""
    return datetime.now().isoformat()


def time_ms() -> float:
    """Get current time in milliseconds."""
    return time.time() * 1000


def generate_id(prefix: str = "id") -> str:
    """Generate a unique ID with prefix."""
    timestamp = int(time.time() * 1000)
    random_suffix = hashlib.md5(str(timestamp).encode()).hexdigest()[:6]
    return f"{prefix}-{timestamp}-{random_suffix}"


def hash_data(data: Any) -> str:
    """Generate hash for any data structure."""
    if isinstance(data, (dict, list)):
        data_str = json.dumps(data, sort_keys=True)
    else:
        data_str = str(data)

    return hashlib.md5(data_str.encode()).hexdigest()


def mask_pii(text: str) -> str:
    """Mask personally identifiable information in text."""
    import re

    # Mask email addresses
    text = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL]", text
    )

    # Mask phone numbers (simple pattern)
    text = re.sub(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "[PHONE]", text)

    # Mask credit card numbers (simple pattern)
    text = re.sub(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b", "[CARD]", text)

    return text


def retry_with_backoff(func, max_retries: int = 3, base_delay: float = 1.0):
    """Retry function with exponential backoff."""
    import asyncio

    async def async_wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise

                delay = base_delay * (2**attempt)
                print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s...")
                await asyncio.sleep(delay)

    def sync_wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise

                delay = base_delay * (2**attempt)
                print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s...")
                time.sleep(delay)

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def get_git_commit() -> str:
    """Get current git commit hash."""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"
