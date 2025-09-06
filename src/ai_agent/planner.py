from typing import Any, Dict, List

from .logger import get_logger
from .model import AIClient
from .tools import ToolRegistry

logger = get_logger(__name__)


class Planner:
    """Planning module for the ReAct agent."""

    """ReAct代理的规划模块"""

    def __init__(self, client: AIClient):
        self.client = client  # AI客户端
        logger.info("Planner initialized with AI client")

    def generate_thought_prompt(
        self, task: str, progress: str, available_tools: List[str]
    ) -> str:
        """Generate the prompt for the thought phase."""
        """为思考阶段生成提示"""
        logger.debug(f"Generating thought prompt for task: {task}")
        tools_description = self._format_tools_description(available_tools)

        prompt = f"""You are an AI assistant using the ReAct framework. Your task is: {task}

Current progress: {progress or 'No progress yet'}

Available tools: {tools_description}

Think step by step about how to approach this task. Consider what information you need and which tools might be helpful.

Your response should be a clear, concise thought process that will help you decide the next action."""

        logger.debug(f"Thought prompt generated, length: {len(prompt)}, content: {prompt}")
        return prompt

    def decide_action(
        self, thought: str, tool_registry: ToolRegistry
    ) -> Dict[str, Any]:
        """Decide the next action based on the thought process."""
        """根据思考过程决定下一步行动"""
        logger.debug("Deciding next action based on thought process")
        # Get detailed tool descriptions for the action prompt
        detailed_tools = self._format_tools_description(tool_registry.get_available_tools())
        
        action_prompt = f"""Based on your thought process:
{thought}

Decide what action to take next. You can choose to:
1. Use one of the available tools (provide operation and parameters)
2. Provide a final answer if you have enough information

Available tools with operations:
{detailed_tools}

When using a tool, you MUST include the "operation" parameter that specifies which operation to perform.
For example, to read a file: {{"action": "file", "action_input": {{"operation": "read", "path": "filename.txt"}}}}

Respond in JSON format with:
{{
  "action": "tool_name" or "final_answer",
  "action_input": {{...}}  // parameters for the tool including "operation", or {{"answer": "final answer"}}
}}"""

        logger.debug(f"Action prompt generated, length: {len(action_prompt)}, content: {action_prompt}")
        response = self.client.chat([{"role": "user", "content": action_prompt}])

        try:
            import json

            action_decision = json.loads(response)
            logger.info(f"Action decision parsed: {action_decision['action']}")

            if action_decision["action"] not in tool_registry.get_available_tools() + [
                "final_answer"
            ]:
                error_msg = f"Invalid action: {action_decision['action']}"
                logger.warning(error_msg)
                raise ValueError(error_msg)

            return action_decision
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error parsing action decision: {str(e)}")
            return {
                "action": "final_answer",
                "action_input": {
                    "answer": f"Error parsing action decision: {str(e)}. Original response: {response}"
                },
            }

    def _format_tools_description(self, tools: List[str]) -> str:
        """Format the tools description for the prompt."""
        """为提示格式化工具描述"""
        from .tools import ToolRegistry
        
        # Create a temporary tool registry to get detailed descriptions
        temp_registry = ToolRegistry()
        
        # Register tools with their detailed descriptions
        if "file" in tools:
            from .tools import FileTool
            temp_registry.register_tool("file", FileTool())
        
        if "calculator" in tools:
            from .tools import CalculatorTool
            temp_registry.register_tool("calculator", CalculatorTool())
        
        if "web_search" in tools:
            from .tools import WebSearchTool
            temp_registry.register_tool("web_search", WebSearchTool())
        
        # Get detailed descriptions from the tools themselves
        descriptions = []
        for tool_name in tools:
            try:
                tool = temp_registry.get_tool(tool_name)
                descriptions.append(tool.get_description())
            except ValueError:
                descriptions.append(tool_name)

        return "\n".join(descriptions)

    def reflect_on_progress(
        self, trajectory: List[Dict[str, Any]], current_task: str
    ) -> str:
        """Reflect on the progress made so far and suggest improvements."""
        """反思到目前为止的进展并提出改进建议"""
        logger.debug(f"Reflecting on progress for task: {current_task}")
        reflection_prompt = f"""Review the execution trajectory for the task: {current_task}

Execution steps:
{self._format_trajectory_for_reflection(trajectory)}

Analyze what has been accomplished, what worked well, and what could be improved. 
Suggest any changes to the approach for the remaining part of the task."""

        logger.debug("Reflection prompt generated")
        return self.client.chat([{"role": "user", "content": reflection_prompt}])

    def _format_trajectory_for_reflection(
        self, trajectory: List[Dict[str, Any]]
    ) -> str:
        """Format the trajectory for reflection purposes."""
        """为反思目的格式化轨迹"""
        formatted = []
        for i, step in enumerate(trajectory, 1):
            formatted.append(f"Step {i}:")
            formatted.append(f"  Thought: {step.get('thought', 'N/A')}")
            formatted.append(f"  Action: {step.get('action', 'N/A')}")
            formatted.append(f"  Result: {step.get('result', 'N/A')}")
            formatted.append("")

        return "\n".join(formatted)
