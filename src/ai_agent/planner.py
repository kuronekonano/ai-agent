from typing import Any, Dict, List

from .model import AIClient
from .tools import ToolRegistry


class Planner:
    """Planning module for the ReAct agent."""

    def __init__(self, client: AIClient):
        self.client = client

    def generate_thought_prompt(
        self, task: str, progress: str, available_tools: List[str]
    ) -> str:
        """Generate the prompt for the thought phase."""
        tools_description = self._format_tools_description(available_tools)

        prompt = f"""You are an AI assistant using the ReAct framework. Your task is: {task}

Current progress: {progress or 'No progress yet'}

Available tools: {tools_description}

Think step by step about how to approach this task. Consider what information you need and which tools might be helpful.

Your response should be a clear, concise thought process that will help you decide the next action."""

        return prompt

    def decide_action(
        self, thought: str, tool_registry: ToolRegistry
    ) -> Dict[str, Any]:
        """Decide the next action based on the thought process."""
        action_prompt = f"""Based on your thought process:
{thought}

Decide what action to take next. You can choose to:
1. Use one of the available tools
2. Provide a final answer if you have enough information

Available tools: {', '.join(tool_registry.get_available_tools())}

Respond in JSON format with:
{{
  "action": "tool_name" or "final_answer",
  "action_input": {{...}}  // parameters for the tool or {{"answer": "final answer"}}
}}"""

        response = self.client.chat([{"role": "user", "content": action_prompt}])

        try:
            import json

            action_decision = json.loads(response)

            if action_decision["action"] not in tool_registry.get_available_tools() + [
                "final_answer"
            ]:
                raise ValueError(f"Invalid action: {action_decision['action']}")

            return action_decision
        except (json.JSONDecodeError, ValueError) as e:
            return {
                "action": "final_answer",
                "action_input": {
                    "answer": f"Error parsing action decision: {str(e)}. Original response: {response}"
                },
            }

    def _format_tools_description(self, tools: List[str]) -> str:
        """Format the tools description for the prompt."""
        tool_descriptions = {
            "file": "Read, write, and manipulate files",
            "calculator": "Perform mathematical calculations",
            "web_search": "Search the web for information",
        }

        descriptions = []
        for tool in tools:
            if tool in tool_descriptions:
                descriptions.append(f"{tool}: {tool_descriptions[tool]}")
            else:
                descriptions.append(tool)

        return "\n".join(descriptions)

    def reflect_on_progress(
        self, trajectory: List[Dict[str, Any]], current_task: str
    ) -> str:
        """Reflect on the progress made so far and suggest improvements."""
        reflection_prompt = f"""Review the execution trajectory for the task: {current_task}

Execution steps:
{self._format_trajectory_for_reflection(trajectory)}

Analyze what has been accomplished, what worked well, and what could be improved. 
Suggest any changes to the approach for the remaining part of the task."""

        return self.client.chat([{"role": "user", "content": reflection_prompt}])

    def _format_trajectory_for_reflection(
        self, trajectory: List[Dict[str, Any]]
    ) -> str:
        """Format the trajectory for reflection purposes."""
        formatted = []
        for i, step in enumerate(trajectory, 1):
            formatted.append(f"Step {i}:")
            formatted.append(f"  Thought: {step.get('thought', 'N/A')}")
            formatted.append(f"  Action: {step.get('action', 'N/A')}")
            formatted.append(f"  Result: {step.get('result', 'N/A')}")
            formatted.append("")

        return "\n".join(formatted)
