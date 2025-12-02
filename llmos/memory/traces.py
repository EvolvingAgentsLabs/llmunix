"""
Execution Trace Manager - L3 Storage (Procedural Memory)
Stores and retrieves execution patterns for Follower Mode
"""

import json
import yaml
import hashlib
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ExecutionTrace:
    """
    An execution trace - the "compiled program" of the LLM OS
    This is what allows cheap repetition of expensive learning
    """
    goal_signature: str  # Hash of the goal
    goal_text: str  # Original goal
    steps: List[Dict]  # Tool call sequence
    success_rating: float  # 0.0 to 1.0
    usage_count: int = 0
    last_used: Optional[str] = None
    created_at: Optional[str] = None
    estimated_cost_usd: float = 0.0
    estimated_time_secs: float = 0.0
    crystallized_into_tool: Optional[str] = None  # Name of generated tool (HOPE architecture)

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class TraceManager:
    """
    Manages execution traces (L3 Storage)
    Think of this as the "compiled bytecode" storage
    """

    def __init__(self, storage_path: Path):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # In-memory index for fast lookup
        self.index: Dict[str, str] = {}  # goal_signature -> file_path
        self._load_index()

    def _load_index(self):
        """Load all traces into memory index"""
        for trace_file in self.storage_path.glob("*.yaml"):
            with open(trace_file, 'r') as f:
                data = yaml.safe_load(f)
                if data and 'goal_signature' in data:
                    self.index[data['goal_signature']] = str(trace_file)

    def _hash_goal(self, goal: str) -> str:
        """Create a hash signature for a goal"""
        return hashlib.sha256(goal.lower().strip().encode()).hexdigest()[:16]

    def save_trace(self, trace: ExecutionTrace) -> Path:
        """
        Save an execution trace

        Args:
            trace: ExecutionTrace to save

        Returns:
            Path to saved trace file
        """
        filename = f"trace_{trace.goal_signature}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
        filepath = self.storage_path / filename

        # Convert to dict and save as YAML
        data = asdict(trace)

        with open(filepath, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

        # Update index
        self.index[trace.goal_signature] = str(filepath)

        return filepath

    def find_trace(self, goal: str, confidence_threshold: float = 0.9) -> Optional[ExecutionTrace]:
        """
        Find a matching trace for a goal

        Args:
            goal: Natural language goal
            confidence_threshold: Minimum success rating required

        Returns:
            ExecutionTrace if found and confidence is high enough, None otherwise
        """
        goal_sig = self._hash_goal(goal)

        # Exact match
        if goal_sig in self.index:
            filepath = Path(self.index[goal_sig])
            if filepath.exists():
                with open(filepath, 'r') as f:
                    data = yaml.safe_load(f)

                trace = ExecutionTrace(**data)

                # Check confidence threshold
                if trace.success_rating >= confidence_threshold:
                    return trace

        # TODO: Implement semantic similarity search for partial matches
        # For now, only exact goal matches

        return None

    def update_trace_usage(self, goal_signature: str, success: bool):
        """
        Update trace usage statistics after execution

        Args:
            goal_signature: Trace signature
            success: Whether execution was successful
        """
        if goal_signature not in self.index:
            return

        filepath = Path(self.index[goal_signature])
        if not filepath.exists():
            return

        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)

        trace = ExecutionTrace(**data)

        # Update usage
        trace.usage_count += 1
        trace.last_used = datetime.now().isoformat()

        # Update success rating (exponential moving average)
        alpha = 0.1  # Learning rate
        new_rating = 1.0 if success else 0.0
        trace.success_rating = (1 - alpha) * trace.success_rating + alpha * new_rating

        # Save updated trace
        with open(filepath, 'w') as f:
            yaml.dump(asdict(trace), f, default_flow_style=False, sort_keys=False)

    def list_traces(self) -> List[ExecutionTrace]:
        """List all execution traces"""
        traces = []

        for filepath in Path(self.storage_path).glob("*.yaml"):
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
            traces.append(ExecutionTrace(**data))

        return sorted(traces, key=lambda t: t.usage_count, reverse=True)
