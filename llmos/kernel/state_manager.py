"""
State Manager - Manages execution state machine
Brings llmunix's modular state file system to llmos
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class ExecutionStep:
    """A single step in the execution plan"""
    step_number: int
    description: str
    agent: Optional[str] = None
    status: str = "pending"  # pending, in_progress, completed, failed
    result: Optional[str] = None
    error: Optional[str] = None


class StateManager:
    """
    Manages execution state machine

    Creates and maintains modular state files:
    - plan.md: Execution plan
    - context.md: Current execution context
    - variables.json: Runtime variables
    - history.md: Complete execution log
    - constraints.json: Behavioral constraints
    """

    def __init__(self, project_path: Path):
        """
        Initialize StateManager

        Args:
            project_path: Path to project root
        """
        self.project_path = Path(project_path)
        self.state_path = self.project_path / "state"
        self.state_path.mkdir(parents=True, exist_ok=True)

        # State files
        self.plan_file = self.state_path / "plan.md"
        self.context_file = self.state_path / "context.md"
        self.variables_file = self.state_path / "variables.json"
        self.history_file = self.state_path / "history.md"
        self.constraints_file = self.state_path / "constraints.json"

        # In-memory state
        self.plan: List[ExecutionStep] = []
        self.context: Dict[str, Any] = {}
        self.variables: Dict[str, Any] = {}
        self.constraints: Dict[str, Any] = {}

        # Initialize state
        self._initialize_state()

    def _initialize_state(self):
        """Initialize state files if they don't exist"""
        if not self.history_file.exists():
            self._init_history()

        if self.variables_file.exists():
            with open(self.variables_file, 'r') as f:
                self.variables = json.load(f)

        if self.constraints_file.exists():
            with open(self.constraints_file, 'r') as f:
                self.constraints = json.load(f)
        else:
            # Default constraints
            self.constraints = {
                "max_token_cost": 10.0,
                "max_execution_time_secs": 600,
                "require_memory_consultation": True,
                "enable_learning": True
            }
            self._save_constraints()

    def _init_history(self):
        """Initialize history.md with header"""
        header = f"""# Execution History

**Project**: {self.project_path.name}
**Started**: {datetime.now().isoformat()}

---

## Events

"""
        with open(self.history_file, 'w') as f:
            f.write(header)

    def initialize_execution(self, goal: str):
        """
        Initialize a new execution

        Args:
            goal: Natural language goal
        """
        self.context = {
            "goal": goal,
            "started_at": datetime.now().isoformat(),
            "status": "initialized"
        }
        self._save_context()

        self.log_event("EXECUTION_INITIALIZED", {"goal": goal})

    def set_plan(self, steps: List[ExecutionStep]):
        """
        Set the execution plan

        Args:
            steps: List of ExecutionStep instances
        """
        self.plan = steps
        self._save_plan()
        self.log_event("PLAN_CREATED", {"step_count": len(steps)})

    def _save_plan(self):
        """Save execution plan to plan.md"""
        content_parts = [
            "# Execution Plan",
            "",
            f"**Total Steps**: {len(self.plan)}",
            f"**Created**: {datetime.now().isoformat()}",
            "",
            "---",
            ""
        ]

        for step in self.plan:
            status_emoji = {
                "pending": "⏸️",
                "in_progress": "▶️",
                "completed": "✅",
                "failed": "❌"
            }.get(step.status, "❓")

            content_parts.append(
                f"## Step {step.step_number}: {step.description} {status_emoji}"
            )

            if step.agent:
                content_parts.append(f"**Agent**: {step.agent}")

            content_parts.append(f"**Status**: {step.status}")

            if step.result:
                content_parts.append(f"**Result**: {step.result}")

            if step.error:
                content_parts.append(f"**Error**: {step.error}")

            content_parts.append("")

        with open(self.plan_file, 'w') as f:
            f.write('\n'.join(content_parts))

    def update_step_status(
        self,
        step_number: int,
        status: str,
        result: Optional[str] = None,
        error: Optional[str] = None
    ):
        """
        Update step status

        Args:
            step_number: Step number
            status: New status
            result: Optional result
            error: Optional error message
        """
        for step in self.plan:
            if step.step_number == step_number:
                step.status = status
                if result:
                    step.result = result
                if error:
                    step.error = error
                break

        self._save_plan()
        self.log_event("STEP_UPDATED", {
            "step": step_number,
            "status": status,
            "result": result,
            "error": error
        })

    def update_context(self, updates: Dict[str, Any]):
        """
        Update execution context

        Args:
            updates: Dictionary of context updates
        """
        self.context.update(updates)
        self._save_context()

    def _save_context(self):
        """Save context to context.md"""
        content_parts = [
            "# Execution Context",
            "",
            f"**Goal**: {self.context.get('goal', 'N/A')}",
            f"**Status**: {self.context.get('status', 'unknown')}",
            f"**Started**: {self.context.get('started_at', 'N/A')}",
            ""
        ]

        if "completed_at" in self.context:
            content_parts.append(f"**Completed**: {self.context['completed_at']}")

        content_parts.extend(["", "## Additional Context", ""])

        for key, value in self.context.items():
            if key not in ["goal", "status", "started_at", "completed_at"]:
                content_parts.append(f"**{key}**: {value}")

        with open(self.context_file, 'w') as f:
            f.write('\n'.join(content_parts))

    def set_variable(self, key: str, value: Any):
        """
        Set a runtime variable

        Args:
            key: Variable name
            value: Variable value
        """
        self.variables[key] = value
        self._save_variables()

    def get_variable(self, key: str, default: Any = None) -> Any:
        """
        Get a runtime variable

        Args:
            key: Variable name
            default: Default value if not found

        Returns:
            Variable value or default
        """
        return self.variables.get(key, default)

    def _save_variables(self):
        """Save variables to variables.json"""
        with open(self.variables_file, 'w') as f:
            json.dump(self.variables, f, indent=2)

    def update_constraint(self, key: str, value: Any):
        """
        Update a behavioral constraint

        Args:
            key: Constraint name
            value: Constraint value
        """
        self.constraints[key] = value
        self._save_constraints()

    def _save_constraints(self):
        """Save constraints to constraints.json"""
        with open(self.constraints_file, 'w') as f:
            json.dump(self.constraints, f, indent=2)

    def log_event(self, event_type: str, data: Dict[str, Any]):
        """
        Log an event to history.md

        Args:
            event_type: Event type
            data: Event data
        """
        timestamp = datetime.now().isoformat()

        log_entry = f"""
### {event_type}

**Timestamp**: {timestamp}

"""

        for key, value in data.items():
            log_entry += f"**{key}**: {value}\n"

        log_entry += "\n---\n"

        with open(self.history_file, 'a') as f:
            f.write(log_entry)

    def get_execution_summary(self) -> Dict[str, Any]:
        """
        Get execution summary

        Returns:
            Dictionary with execution summary
        """
        completed_steps = sum(1 for step in self.plan if step.status == "completed")
        failed_steps = sum(1 for step in self.plan if step.status == "failed")

        return {
            "goal": self.context.get("goal"),
            "status": self.context.get("status"),
            "started_at": self.context.get("started_at"),
            "completed_at": self.context.get("completed_at"),
            "total_steps": len(self.plan),
            "completed_steps": completed_steps,
            "failed_steps": failed_steps,
            "constraints": self.constraints,
            "variables": self.variables
        }

    def mark_execution_complete(self, success: bool = True):
        """
        Mark execution as complete

        Args:
            success: Whether execution was successful
        """
        self.context["status"] = "completed" if success else "failed"
        self.context["completed_at"] = datetime.now().isoformat()
        self._save_context()

        self.log_event("EXECUTION_COMPLETED", {
            "success": success,
            "summary": self.get_execution_summary()
        })
