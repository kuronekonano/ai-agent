#!/usr/bin/env python3
"""
Test MockModelClient directly.
直接测试MockModelClient
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent_eval.client import MockModelClient
import asyncio

async def test_mock_client():
    """Test MockModelClient directly."""
    print("Testing MockModelClient directly...")
    
    client = MockModelClient()
    
    # Test a simple prompt
    prompt = "Hello, how are you?"
    print(f"Testing prompt: {prompt}")
    
    try:
        response = await client.call(prompt)
        print(f"Response: {response}")
        print(f"Response text: {response['text']}")
        print(f"Latency: {response['latency_ms']}ms")
        print(f"Token usage: {response['usage']}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mock_client())
    sys.exit(0 if success else 1)