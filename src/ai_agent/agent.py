import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .logger import get_logger
from .model import AIClient, create_client
from .planner import Planner
from .tools import ToolRegistry
from .trajectory import TrajectoryRecorder

logger = get_logger(__name__)


@dataclass
class ReActStep:
    """ReAct单步执行数据类"""

    thought: str  # 思考过程
    action: str  # 执行动作
    action_input: Dict[str, Any]  # 动作输入参数
    observation: str  # 观察结果
    result: str  # 执行结果


class ReActEngine:
    """ReAct (Reasoning + Acting) engine for autonomous AI agents."""

    """用于自主AI代理的ReAct（推理+行动）引擎"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config  # 配置信息
        logger.info("Initializing ReActEngine with configuration")

        self.client = create_client(config["openai"])  # AI客户端
        logger.debug("AI client created successfully")

        self.planner = Planner(self.client)  # 规划器
        logger.debug("Planner initialized")

        self.tool_registry = ToolRegistry()  # 工具注册表
        self.trajectory_recorder = TrajectoryRecorder()  # 轨迹记录器

        self.max_iterations = config.get("agent", {}).get(
            "max_iterations", 10
        )  # 最大迭代次数
        self.timeout_seconds = config.get("agent", {}).get(
            "timeout_seconds", 300
        )  # 超时时间（秒）
        logger.debug(
            f"Configuration: max_iterations={self.max_iterations}, timeout={self.timeout_seconds}s"
        )

        self._setup_tools()

    def _setup_tools(self):
        """Initialize available tools based on configuration."""
        """根据配置初始化可用工具"""
        tool_config = self.config.get("tools", {})
        logger.info("Setting up tools based on configuration")

        if tool_config.get("enable_file_operations", True):
            from .tools import FileTool

            self.tool_registry.register_tool("file", FileTool())
            logger.debug("File operations tool registered")

        if tool_config.get("enable_calculator", True):
            from .tools import CalculatorTool

            self.tool_registry.register_tool("calculator", CalculatorTool())
            logger.debug("Calculator tool registered")

        if tool_config.get("enable_web_search", False):
            from .tools import WebSearchTool

            self.tool_registry.register_tool("web_search", WebSearchTool())
            logger.debug("Web search tool registered")

        available_tools = self.tool_registry.get_available_tools()
        logger.info(f"Available tools: {available_tools}")

    def run(self, task: str) -> str:
        """Execute the ReAct loop for a given task."""
        """为给定任务执行ReAct循环"""
        logger.info(f"Starting ReAct execution for task: {task}")
        start_time = time.time()
        iteration = 0
        current_state = {"task": task, "progress": ""}

        self.trajectory_recorder.start(task)
        logger.debug("Trajectory recording started")

        while iteration < self.max_iterations:
            logger.debug(f"Starting iteration {iteration + 1}/{self.max_iterations}")

            if time.time() - start_time > self.timeout_seconds:
                logger.warning("Agent execution timed out")
                raise TimeoutError("Agent execution timed out")

            step = self._execute_step(iteration, current_state)

            if self._is_task_complete(step, current_state):
                logger.info(
                    f"Task completed successfully in {iteration + 1} iterations"
                )
                self.trajectory_recorder.complete(step.result)
                return step.result

            current_state["progress"] = step.observation
            iteration += 1

        logger.warning(
            f"Maximum iterations ({self.max_iterations}) reached without completing task"
        )
        raise RuntimeError("Maximum iterations reached without completing task")

    def _execute_step(self, iteration: int, current_state: Dict[str, Any]) -> ReActStep:
        """Execute a single ReAct step."""
        """执行单个ReAct步骤"""
        logger.debug(f"Executing step {iteration + 1}")

        thought_prompt = self.planner.generate_thought_prompt(
            current_state["task"],
            current_state["progress"],
            self.tool_registry.get_available_tools(),
        )
        logger.debug("Generated thought prompt")

        thought = self.client.chat([{"role": "user", "content": thought_prompt}])
        logger.debug(f"AI thought generated: {thought[:100]}...")

        action_decision = self.planner.decide_action(thought, self.tool_registry)
        logger.info(f"Action decided: {action_decision['action']}")

        if action_decision["action"] == "final_answer":
            observation = "Task completed"
            result = action_decision["action_input"]["answer"]
            logger.debug("Final answer action selected")
        else:
            observation = self._execute_action(action_decision)
            result = observation
            logger.debug(f"Action executed, observation: {observation[:100]}...")

        step = ReActStep(
            thought=thought,
            action=action_decision["action"],
            action_input=action_decision["action_input"],
            observation=observation,
            result=result,
        )

        self.trajectory_recorder.record_step(step)
        logger.debug("Step recorded in trajectory")
        return step

    def _execute_action(self, action_decision: Dict[str, Any]) -> str:
        """Execute the chosen action using the appropriate tool."""
        """使用适当的工具执行所选操作"""
        action = action_decision["action"]
        action_input = action_decision["action_input"]

        logger.info(f"Executing action: {action} with input: {action_input}")

        try:
            tool = self.tool_registry.get_tool(action)
            logger.debug(f"Tool found: {action}")
            result = tool.execute(**action_input)
            logger.info(f"Action {action} executed successfully")
            return str(result)
        except Exception as e:
            logger.error(f"Error executing action {action}: {str(e)}")
            return f"Error executing action {action}: {str(e)}"

    def _is_task_complete(self, step: ReActStep, current_state: Dict[str, Any]) -> bool:
        """Determine if the task is complete based on the current step."""
        """根据当前步骤确定任务是否完成"""
        return step.action == "final_answer"

    def get_trajectory(self):
        """Get the complete execution trajectory."""
        """获取完整的执行轨迹"""
        return self.trajectory_recorder.get_trajectory()

    def reset(self):
        """Reset the agent's state."""
        """重置代理的状态"""
        self.trajectory_recorder.reset()

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics including token usage and costs."""
        """获取性能统计信息，包括Token使用情况和成本"""
        return self.client.get_performance_stats()

    def reset_performance_stats(self):
        """Reset performance tracking statistics."""
        """重置性能跟踪统计信息"""
        self.client.reset_performance_stats()
