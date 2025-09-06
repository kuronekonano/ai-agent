import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from .logger import get_logger

logger = get_logger(__name__)


@dataclass
class TrajectoryStep:
    """单步执行轨迹数据类"""

    timestamp: str  # 时间戳
    thought: str  # 思考过程
    action: str  # 执行的动作
    action_input: Dict[str, Any]  # 动作输入参数
    observation: str  # 观察结果
    result: str  # 执行结果
    step_number: int  # 步骤编号


@dataclass
class Trajectory:
    """完整执行轨迹数据类"""

    task: str  # 任务描述
    start_time: str  # 开始时间
    end_time: Optional[str]  # 结束时间
    steps: List[TrajectoryStep]  # 步骤列表
    success: bool  # 是否成功
    final_result: Optional[str]  # 最终结果
    total_steps: int  # 总步骤数
    duration_seconds: Optional[float]  # 持续时间（秒）


class TrajectoryRecorder:
    """Records and manages the execution trajectory of an AI agent."""

    """记录和管理AI代理的执行轨迹"""

    def __init__(self):
        self.current_trajectory: Optional[Trajectory] = None  # 当前轨迹
        self.steps: List[TrajectoryStep] = []  # 步骤列表
        self.start_time: Optional[datetime] = None  # 开始时间
        logger.debug("TrajectoryRecorder initialized")

    def start(self, task: str):
        """Start recording a new trajectory."""
        """开始记录新的轨迹"""
        logger.info(f"Starting trajectory recording for task: {task}")
        self.current_trajectory = None
        self.steps = []
        self.start_time = datetime.now()

        self.current_trajectory = Trajectory(
            task=task,
            start_time=self.start_time.isoformat(),
            end_time=None,
            steps=[],
            success=False,
            final_result=None,
            total_steps=0,
            duration_seconds=None,
        )
        logger.debug("New trajectory created")

    def record_step(self, step_data: Any):
        """Record a single execution step."""
        """记录单个执行步骤"""
        if not self.current_trajectory:
            logger.error("No active trajectory. Call start() first.")
            raise RuntimeError("No active trajectory. Call start() first.")

        step = TrajectoryStep(
            timestamp=datetime.now().isoformat(),
            thought=step_data.thought,
            action=step_data.action,
            action_input=step_data.action_input,
            observation=step_data.observation,
            result=step_data.result,
            step_number=len(self.steps) + 1,
        )

        self.steps.append(step)
        self.current_trajectory.steps = self.steps
        self.current_trajectory.total_steps = len(self.steps)
        logger.debug(f"Step {step.step_number} recorded: {step.action}")

    def complete(self, final_result: str, success: bool = True):
        """Mark the trajectory as completed."""
        """标记轨迹为已完成"""
        if not self.current_trajectory:
            logger.error("No active trajectory. Call start() first.")
            raise RuntimeError("No active trajectory. Call start() first.")

        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds() if self.start_time else 0.0

        self.current_trajectory.end_time = end_time.isoformat()
        self.current_trajectory.success = success
        self.current_trajectory.final_result = final_result
        self.current_trajectory.duration_seconds = duration

        logger.info(
            f"Trajectory completed: success={success}, steps={self.current_trajectory.total_steps}, duration={duration:.2f}s"
        )

    def get_trajectory(self) -> Optional[Trajectory]:
        """Get the current trajectory."""
        """获取当前轨迹"""
        return self.current_trajectory

    def to_dict(self) -> Optional[Dict[str, Any]]:
        """Convert the trajectory to a dictionary."""
        """将轨迹转换为字典"""
        if not self.current_trajectory:
            return None

        return {
            "task": self.current_trajectory.task,
            "start_time": self.current_trajectory.start_time,
            "end_time": self.current_trajectory.end_time,
            "success": self.current_trajectory.success,
            "final_result": self.current_trajectory.final_result,
            "total_steps": self.current_trajectory.total_steps,
            "duration_seconds": self.current_trajectory.duration_seconds,
            "steps": [asdict(step) for step in self.current_trajectory.steps],
        }

    def to_json(self, indent: int = 2) -> Optional[str]:
        """Convert the trajectory to JSON format."""
        """将轨迹转换为JSON格式"""
        trajectory_dict = self.to_dict()
        if not trajectory_dict:
            return None

        return json.dumps(trajectory_dict, indent=indent, ensure_ascii=False)

    def save_to_file(self, filepath: str):
        """Save the trajectory to a JSON file."""
        """将轨迹保存到JSON文件"""
        trajectory_json = self.to_json()
        if not trajectory_json:
            logger.error("No trajectory to save")
            raise RuntimeError("No trajectory to save")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(trajectory_json)

        logger.info(f"Trajectory saved to file: {filepath}")

    def load_from_file(self, filepath: str):
        """Load a trajectory from a JSON file."""
        """从JSON文件加载轨迹"""
        logger.info(f"Loading trajectory from file: {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        steps = []
        for step_data in data["steps"]:
            steps.append(TrajectoryStep(**step_data))

        self.current_trajectory = Trajectory(
            task=data["task"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            steps=steps,
            success=data["success"],
            final_result=data["final_result"],
            total_steps=data["total_steps"],
            duration_seconds=data["duration_seconds"],
        )
        self.steps = steps

        if data["start_time"]:
            self.start_time = datetime.fromisoformat(data["start_time"])

        logger.debug(f"Trajectory loaded: {data['task']}, steps: {len(steps)}")

    def reset(self):
        """Reset the trajectory recorder."""
        """重置轨迹记录器"""
        logger.debug("Resetting trajectory recorder")
        self.current_trajectory = None
        self.steps = []
        self.start_time = None

    def get_statistics(self) -> Optional[Dict[str, Any]]:
        """Get statistics about the trajectory."""
        """获取轨迹统计信息"""
        if not self.current_trajectory:
            return None

        return {
            "total_steps": self.current_trajectory.total_steps,
            "duration_seconds": self.current_trajectory.duration_seconds,
            "success": self.current_trajectory.success,
            "average_step_time": (
                self.current_trajectory.duration_seconds
                / self.current_trajectory.total_steps
                if self.current_trajectory.duration_seconds
                and self.current_trajectory.total_steps > 0
                else None
            ),
        }
