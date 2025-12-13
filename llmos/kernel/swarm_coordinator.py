"""
Swarm Coordination for LLMOS

Implements parallel agent execution with mesh topology coordination.
Inspired by Claude-Flow's swarm architecture with 2.8-4.4x speed improvements.

Key Features:
- Mesh topology for agent coordination
- Parallel task distribution
- Contextual task routing
- Fault-tolerant agent interactions
- Result aggregation and synthesis

Inspired by Claude-Flow's swarm coordination (MIT License)
https://github.com/ruvnet/claude-flow
"""

from typing import Dict, Any, List, Optional, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from pathlib import Path
import time
from datetime import datetime


class SwarmTopology(Enum):
    """Swarm coordination topology"""
    MESH = "mesh"  # All agents can communicate
    STAR = "star"  # Central coordinator
    RING = "ring"  # Sequential processing
    PIPELINE = "pipeline"  # Staged processing


class AgentStatus(Enum):
    """Agent status in swarm"""
    IDLE = "idle"
    BUSY = "busy"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class SwarmAgent:
    """Agent in a swarm"""
    agent_id: str
    agent_type: str
    role: str
    tools: List[str]
    status: AgentStatus = AgentStatus.IDLE
    current_task: Optional[str] = None
    results: List[Any] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=lambda: time.time())

    @property
    def is_available(self) -> bool:
        """Check if agent is available for work"""
        return self.status == AgentStatus.IDLE


@dataclass
class SwarmTask:
    """Task in a swarm"""
    task_id: str
    description: str
    inputs: Dict[str, Any]
    assigned_agent: Optional[str] = None
    status: AgentStatus = AgentStatus.IDLE
    result: Optional[Any] = None
    error: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None

    @property
    def is_complete(self) -> bool:
        return self.status in [AgentStatus.COMPLETED, AgentStatus.FAILED]

    @property
    def execution_time(self) -> Optional[float]:
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None


@dataclass
class SwarmResult:
    """Result of swarm execution"""
    swarm_id: str
    success: bool
    tasks_completed: int
    tasks_failed: int
    total_time: float
    results: List[Any] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    agent_stats: Dict[str, Dict[str, Any]] = field(default_factory=dict)


class SwarmCoordinator:
    """
    Swarm Coordinator

    Manages parallel execution of tasks across multiple agents.
    Implements mesh topology for flexible coordination.

    Features:
    - Dynamic task allocation
    - Dependency resolution
    - Parallel execution where possible
    - Result aggregation
    - Fault tolerance
    """

    def __init__(
        self,
        swarm_id: str,
        topology: SwarmTopology = SwarmTopology.MESH,
        max_parallel: int = 5,
        timeout_secs: float = 300.0
    ):
        self.swarm_id = swarm_id
        self.topology = topology
        self.max_parallel = max_parallel
        self.timeout_secs = timeout_secs

        # Swarm state
        self.agents: Dict[str, SwarmAgent] = {}
        self.tasks: Dict[str, SwarmTask] = {}
        self.active_tasks: Set[str] = set()

        # Execution context
        self.shared_context: Dict[str, Any] = {}
        self.task_queue = asyncio.Queue()

        # Statistics
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    def add_agent(
        self,
        agent_id: str,
        agent_type: str,
        role: str,
        tools: List[str]
    ) -> SwarmAgent:
        """
        Add an agent to the swarm

        Args:
            agent_id: Unique agent identifier
            agent_type: Type of agent (planner, coder, etc.)
            role: Specific role description
            tools: List of tools this agent can use

        Returns:
            SwarmAgent instance
        """
        agent = SwarmAgent(
            agent_id=agent_id,
            agent_type=agent_type,
            role=role,
            tools=tools
        )

        self.agents[agent_id] = agent
        return agent

    def add_task(
        self,
        task_id: str,
        description: str,
        inputs: Dict[str, Any],
        dependencies: List[str] = None
    ) -> SwarmTask:
        """
        Add a task to the swarm

        Args:
            task_id: Unique task identifier
            description: Task description
            inputs: Task inputs
            dependencies: List of task IDs this task depends on

        Returns:
            SwarmTask instance
        """
        task = SwarmTask(
            task_id=task_id,
            description=description,
            inputs=inputs,
            dependencies=dependencies or []
        )

        self.tasks[task_id] = task
        return task

    async def execute(
        self,
        executor: Callable,
        progress_callback: Optional[Callable] = None
    ) -> SwarmResult:
        """
        Execute all tasks in the swarm

        Args:
            executor: Async function to execute tasks (agent_id, task) -> result
            progress_callback: Optional callback for progress updates

        Returns:
            SwarmResult with execution summary
        """
        self.start_time = time.time()

        try:
            # Execute based on topology
            if self.topology == SwarmTopology.MESH:
                await self._execute_mesh(executor, progress_callback)
            elif self.topology == SwarmTopology.STAR:
                await self._execute_star(executor, progress_callback)
            elif self.topology == SwarmTopology.PIPELINE:
                await self._execute_pipeline(executor, progress_callback)
            else:
                await self._execute_mesh(executor, progress_callback)

        except asyncio.TimeoutError:
            # Timeout - mark remaining tasks as failed
            for task_id, task in self.tasks.items():
                if not task.is_complete:
                    task.status = AgentStatus.FAILED
                    task.error = "Execution timeout"

        self.end_time = time.time()

        return self._generate_result()

    async def _execute_mesh(
        self,
        executor: Callable,
        progress_callback: Optional[Callable]
    ):
        """
        Execute tasks using mesh topology (fully parallel)

        All tasks that don't have dependencies are executed in parallel.
        """
        # Build dependency graph
        ready_tasks = self._get_ready_tasks()

        # Execute until all tasks complete
        while ready_tasks or self.active_tasks:
            # Start new tasks up to max_parallel
            while ready_tasks and len(self.active_tasks) < self.max_parallel:
                task_id = ready_tasks.pop(0)
                task = self.tasks[task_id]

                # Assign to available agent
                agent = self._find_available_agent(task)
                if not agent:
                    # No agent available, wait
                    break

                # Start task execution
                self.active_tasks.add(task_id)
                task.assigned_agent = agent.agent_id
                task.status = AgentStatus.BUSY
                task.started_at = time.time()

                agent.status = AgentStatus.BUSY
                agent.current_task = task_id

                # Execute in background
                asyncio.create_task(
                    self._execute_task(
                        task_id,
                        executor,
                        progress_callback
                    )
                )

            # Wait for at least one task to complete
            if self.active_tasks:
                await asyncio.sleep(0.1)

            # Check for newly ready tasks
            ready_tasks.extend(self._get_ready_tasks())

    async def _execute_star(
        self,
        executor: Callable,
        progress_callback: Optional[Callable]
    ):
        """
        Execute tasks using star topology (central coordinator)

        One agent coordinates, others execute in parallel.
        """
        # Find coordinator agent
        coordinator = next(
            (a for a in self.agents.values() if "orchestrator" in a.agent_type.lower()),
            None
        )

        if not coordinator:
            # Fallback to mesh if no coordinator
            await self._execute_mesh(executor, progress_callback)
            return

        # Coordinator creates execution plan
        # Then delegate to mesh execution
        await self._execute_mesh(executor, progress_callback)

    async def _execute_pipeline(
        self,
        executor: Callable,
        progress_callback: Optional[Callable]
    ):
        """
        Execute tasks using pipeline topology (staged)

        Tasks execute in stages based on dependencies.
        """
        # Group tasks by dependency depth
        stages = self._create_pipeline_stages()

        # Execute each stage
        for stage_num, stage_tasks in enumerate(stages):
            # Execute all tasks in this stage in parallel
            tasks = [
                self._execute_task(task_id, executor, progress_callback)
                for task_id in stage_tasks
            ]

            await asyncio.gather(*tasks, return_exceptions=True)

            if progress_callback:
                await progress_callback(f"Completed stage {stage_num + 1}/{len(stages)}")

    async def _execute_task(
        self,
        task_id: str,
        executor: Callable,
        progress_callback: Optional[Callable]
    ):
        """Execute a single task"""
        task = self.tasks[task_id]
        agent = self.agents.get(task.assigned_agent)

        try:
            # Execute task
            result = await executor(agent.agent_id, task)

            # Update task
            task.result = result
            task.status = AgentStatus.COMPLETED
            task.completed_at = time.time()

            # Update agent
            agent.status = AgentStatus.IDLE
            agent.current_task = None
            agent.results.append(result)

            # Update shared context
            self.shared_context[task_id] = result

            if progress_callback:
                await progress_callback(f"Completed: {task.description}")

        except Exception as e:
            # Task failed
            task.error = str(e)
            task.status = AgentStatus.FAILED
            task.completed_at = time.time()

            agent.status = AgentStatus.IDLE
            agent.current_task = None
            agent.errors.append(str(e))

            if progress_callback:
                await progress_callback(f"Failed: {task.description} - {str(e)}")

        finally:
            self.active_tasks.discard(task_id)

    def _get_ready_tasks(self) -> List[str]:
        """Get tasks that are ready to execute (dependencies met)"""
        ready = []

        for task_id, task in self.tasks.items():
            # Skip if already started
            if task.status != AgentStatus.IDLE:
                continue

            # Skip if already in active set
            if task_id in self.active_tasks:
                continue

            # Check if dependencies are met
            deps_met = all(
                self.tasks[dep_id].status == AgentStatus.COMPLETED
                for dep_id in task.dependencies
                if dep_id in self.tasks
            )

            if deps_met:
                ready.append(task_id)

        return ready

    def _find_available_agent(self, task: SwarmTask) -> Optional[SwarmAgent]:
        """Find an available agent suitable for the task"""
        # Simple strategy: return first available agent
        # Could be enhanced with skill matching
        for agent in self.agents.values():
            if agent.is_available:
                return agent
        return None

    def _create_pipeline_stages(self) -> List[List[str]]:
        """Create pipeline stages based on dependencies"""
        stages = []
        remaining_tasks = set(self.tasks.keys())

        while remaining_tasks:
            # Find tasks with no dependencies in remaining set
            stage = [
                task_id for task_id in remaining_tasks
                if all(
                    dep_id not in remaining_tasks
                    for dep_id in self.tasks[task_id].dependencies
                )
            ]

            if not stage:
                # Circular dependency - break it
                stage = [remaining_tasks.pop()]

            stages.append(stage)

            for task_id in stage:
                remaining_tasks.discard(task_id)

        return stages

    def _generate_result(self) -> SwarmResult:
        """Generate swarm execution result"""
        completed = sum(
            1 for t in self.tasks.values()
            if t.status == AgentStatus.COMPLETED
        )

        failed = sum(
            1 for t in self.tasks.values()
            if t.status == AgentStatus.FAILED
        )

        total_time = (self.end_time or time.time()) - (self.start_time or time.time())

        # Collect results and errors
        results = [
            t.result for t in self.tasks.values()
            if t.result is not None
        ]

        errors = [
            t.error for t in self.tasks.values()
            if t.error is not None
        ]

        # Agent statistics
        agent_stats = {}
        for agent_id, agent in self.agents.items():
            agent_stats[agent_id] = {
                "type": agent.agent_type,
                "role": agent.role,
                "tasks_completed": len(agent.results),
                "errors": len(agent.errors),
                "final_status": agent.status.value
            }

        return SwarmResult(
            swarm_id=self.swarm_id,
            success=(failed == 0 and completed > 0),
            tasks_completed=completed,
            tasks_failed=failed,
            total_time=total_time,
            results=results,
            errors=errors,
            agent_stats=agent_stats
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get swarm execution statistics"""
        return {
            "swarm_id": self.swarm_id,
            "topology": self.topology.value,
            "agents": len(self.agents),
            "tasks": len(self.tasks),
            "completed": sum(1 for t in self.tasks.values() if t.status == AgentStatus.COMPLETED),
            "failed": sum(1 for t in self.tasks.values() if t.status == AgentStatus.FAILED),
            "active": len(self.active_tasks),
            "agent_utilization": {
                agent_id: {
                    "status": agent.status.value,
                    "tasks_completed": len(agent.results),
                    "errors": len(agent.errors)
                }
                for agent_id, agent in self.agents.items()
            }
        }


class SwarmManager:
    """
    Swarm Manager

    Manages multiple swarms and provides high-level coordination.
    """

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.swarms: Dict[str, SwarmCoordinator] = {}

    async def create_swarm(
        self,
        swarm_name: str,
        goal: str,
        topology: SwarmTopology = SwarmTopology.MESH,
        max_parallel: int = 5
    ) -> SwarmCoordinator:
        """
        Create a new swarm

        Args:
            swarm_name: Name of the swarm
            goal: High-level goal
            topology: Coordination topology
            max_parallel: Maximum parallel agents

        Returns:
            SwarmCoordinator instance
        """
        swarm_id = f"swarm_{swarm_name}_{int(time.time())}"

        coordinator = SwarmCoordinator(
            swarm_id=swarm_id,
            topology=topology,
            max_parallel=max_parallel
        )

        self.swarms[swarm_id] = coordinator

        return coordinator

    def get_swarm(self, swarm_id: str) -> Optional[SwarmCoordinator]:
        """Get swarm by ID"""
        return self.swarms.get(swarm_id)

    def list_swarms(self) -> List[str]:
        """List all swarm IDs"""
        return list(self.swarms.keys())

    def get_all_statistics(self) -> Dict[str, Any]:
        """Get statistics for all swarms"""
        return {
            swarm_id: coordinator.get_statistics()
            for swarm_id, coordinator in self.swarms.items()
        }

    async def shutdown_swarm(self, swarm_id: str):
        """Shutdown a swarm"""
        if swarm_id in self.swarms:
            # Cancel any active tasks
            coordinator = self.swarms[swarm_id]
            coordinator.active_tasks.clear()

            del self.swarms[swarm_id]


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def calculate_speedup(
    sequential_time: float,
    parallel_time: float
) -> float:
    """
    Calculate speedup from parallelization

    Args:
        sequential_time: Time for sequential execution
        parallel_time: Time for parallel execution

    Returns:
        Speedup factor (e.g., 2.8 means 2.8x faster)
    """
    if parallel_time == 0:
        return 0.0
    return sequential_time / parallel_time


def estimate_parallel_efficiency(
    speedup: float,
    num_agents: int
) -> float:
    """
    Calculate parallel efficiency

    Perfect efficiency = 1.0 (linear speedup)
    Typical efficiency for real workloads: 0.6-0.8

    Args:
        speedup: Actual speedup achieved
        num_agents: Number of parallel agents

    Returns:
        Efficiency ratio (0.0 to 1.0)
    """
    if num_agents == 0:
        return 0.0
    return speedup / num_agents
