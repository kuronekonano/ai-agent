import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .model import AIClient, create_client
from .planner import Planner
from .tools import ToolRegistry
from .trajectory import TrajectoryRecorder


@dataclass
class ReActStep:
    thought: str
    action: str
    action_input: Dict[str, Any]
    observation: str
    result: str


class ReActEngine:
    """ReAct (Reasoning + Acting) engine for autonomous AI agents."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = create_client(config["openai"])
        self.planner = Planner(self.client)
        self.tool_registry = ToolRegistry()
        self.trajectory_recorder = TrajectoryRecorder()

        self.max_iterations = config.get("agent", {}).get("max_iterations", 10)
        self.timeout_seconds = config.get("agent", {}).get("timeout_seconds", 300)

        self._setup_tools()

    def _setup_tools(self):
        """Initialize available tools based on configuration."""
        tool_config = self.config.get("tools", {})

        if tool_config.get("enable_file_operations", True):
            from .tools import FileTool

            self.tool_registry.register_tool("file", FileTool())

        if tool_config.get("enable_calculator", True):
            from .tools import CalculatorTool

            self.tool_registry.register_tool("calculator", CalculatorTool())

        if tool_config.get("enable_web_search", False):
            from .tools import WebSearchTool

            self.tool_registry.register_tool("web_search", WebSearchTool())

    def run(self, task: str) -> str:
        """Execute the ReAct loop for a given task."""
        start_time = time.time()
        iteration = 0
        current_state = {"task": task, "progress": ""}

        self.trajectory_recorder.start(task)

        while iteration < self.max_iterations:
            if time.time() - start_time > self.timeout_seconds:
                raise TimeoutError("Agent execution timed out")

            step = self._execute_step(iteration, current_state)

            if self._is_task_complete(step, current_state):
                self.trajectory_recorder.complete(step.result)
                return step.result

            current_state["progress"] = step.observation
            iteration += 1

        raise RuntimeError("Maximum iterations reached without completing task")

    def _execute_step(self, iteration: int, current_state: Dict[str, Any]) -> ReActStep:
        """Execute a single ReAct step."""
        thought_prompt = self.planner.generate_thought_prompt(
            current_state["task"],
            current_state["progress"],
            self.tool_registry.get_available_tools(),
        )

        thought = self.client.chat([{"role": "user", "content": thought_prompt}])

        action_decision = self.planner.decide_action(thought, self.tool_registry)

        if action_decision["action"] == "final_answer":
            observation = "Task completed"
            result = action_decision["action_input"]["answer"]
        else:
            observation = self._execute_action(action_decision)
            result = observation

        step = ReActStep(
            thought=thought,
            action=action_decision["action"],
            action_input=action_decision["action_input"],
            observation=observation,
            result=result,
        )

        self.trajectory_recorder.record_step(step)
        return step

    def _execute_action(self, action_decision: Dict[str, Any]) -> str:
        """Execute the chosen action using the appropriate tool."""
        action = action_decision["action"]
        action_input = action_decision["action_input"]

        try:
            tool = self.tool_registry.get_tool(action)
            result = tool.execute(**action_input)
            return str(result)
        except Exception as e:
            return f"Error executing action {action}: {str(e)}"

    def _is_task_complete(self, step: ReActStep, current_state: Dict[str, Any]) -> bool:
        """Determine if the task is complete based on the current step."""
        return step.action == "final_answer"

    def get_trajectory(self):
        """Get the complete execution trajectory."""
        return self.trajectory_recorder.get_trajectory()

    def reset(self):
        """Reset the agent's state."""
        self.trajectory_recorder.reset()
