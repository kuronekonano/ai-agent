import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class TrajectoryStep:
    timestamp: str
    thought: str
    action: str
    action_input: Dict[str, Any]
    observation: str
    result: str
    step_number: int


@dataclass
class Trajectory:
    task: str
    start_time: str
    end_time: Optional[str]
    steps: List[TrajectoryStep]
    success: bool
    final_result: Optional[str]
    total_steps: int
    duration_seconds: Optional[float]


class TrajectoryRecorder:
    """Records and manages the execution trajectory of an AI agent."""

    def __init__(self):
        self.current_trajectory: Optional[Trajectory] = None
        self.steps: List[TrajectoryStep] = []
        self.start_time: Optional[datetime] = None

    def start(self, task: str):
        """Start recording a new trajectory."""
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

    def record_step(self, step_data: Any):
        """Record a single execution step."""
        if not self.current_trajectory:
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

    def complete(self, final_result: str, success: bool = True):
        """Mark the trajectory as completed."""
        if not self.current_trajectory:
            raise RuntimeError("No active trajectory. Call start() first.")

        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        self.current_trajectory.end_time = end_time.isoformat()
        self.current_trajectory.success = success
        self.current_trajectory.final_result = final_result
        self.current_trajectory.duration_seconds = duration

    def get_trajectory(self) -> Optional[Trajectory]:
        """Get the current trajectory."""
        return self.current_trajectory

    def to_dict(self) -> Optional[Dict[str, Any]]:
        """Convert the trajectory to a dictionary."""
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
        trajectory_dict = self.to_dict()
        if not trajectory_dict:
            return None

        return json.dumps(trajectory_dict, indent=indent, ensure_ascii=False)

    def save_to_file(self, filepath: str):
        """Save the trajectory to a JSON file."""
        trajectory_json = self.to_json()
        if not trajectory_json:
            raise RuntimeError("No trajectory to save")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(trajectory_json)

    def load_from_file(self, filepath: str):
        """Load a trajectory from a JSON file."""
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

    def reset(self):
        """Reset the trajectory recorder."""
        self.current_trajectory = None
        self.steps = []
        self.start_time = None

    def get_statistics(self) -> Optional[Dict[str, Any]]:
        """Get statistics about the trajectory."""
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
