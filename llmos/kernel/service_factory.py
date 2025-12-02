"""
Service Factory Functions for LLMOS

Provides factory functions for creating LLMOS components.
Enables dependency injection for testing and customization.
"""

from pathlib import Path
from typing import Optional

from kernel.bus import EventBus
from kernel.scheduler import Scheduler
from kernel.watchdog import Watchdog
from kernel.project_manager import ProjectManager
from kernel.agent_factory import AgentFactory
from kernel.component_registry import ComponentRegistry
from kernel.token_economy import TokenEconomy
from memory.store_sdk import MemoryStore
from memory.traces_sdk import TraceManager
from memory.query_sdk import MemoryQueryInterface
from memory.cross_project_sdk import CrossProjectLearning
from interfaces.dispatcher import Dispatcher

from kernel.config import LLMOSConfig


def create_event_bus() -> EventBus:
    """Create an event bus instance"""
    return EventBus()


def create_token_economy(budget_usd: float) -> TokenEconomy:
    """
    Create a token economy instance

    Args:
        budget_usd: Token budget in USD

    Returns:
        TokenEconomy instance
    """
    return TokenEconomy(budget_usd)


def create_scheduler(event_bus: EventBus) -> Scheduler:
    """
    Create a scheduler instance

    Args:
        event_bus: Event bus for scheduling events

    Returns:
        Scheduler instance
    """
    return Scheduler(event_bus)


def create_watchdog(event_bus: EventBus) -> Watchdog:
    """
    Create a watchdog instance

    Args:
        event_bus: Event bus for watchdog events

    Returns:
        Watchdog instance
    """
    return Watchdog(event_bus)


def create_memory_store(workspace: Path) -> MemoryStore:
    """
    Create a memory store instance

    Args:
        workspace: Workspace directory

    Returns:
        MemoryStore instance
    """
    return MemoryStore(workspace)


def create_trace_manager(
    workspace: Path,
    enable_llm_matching: bool = True
) -> TraceManager:
    """
    Create a trace manager instance

    Args:
        workspace: Workspace directory
        enable_llm_matching: Enable LLM-based semantic matching

    Returns:
        TraceManager instance
    """
    return TraceManager(
        memories_dir=workspace / "memories",
        workspace=workspace,
        enable_llm_matching=enable_llm_matching
    )


def create_memory_query(
    trace_manager: TraceManager,
    memory_store: MemoryStore
) -> MemoryQueryInterface:
    """
    Create a memory query interface instance

    Args:
        trace_manager: Trace manager for queries
        memory_store: Memory store for queries

    Returns:
        MemoryQueryInterface instance
    """
    return MemoryQueryInterface(trace_manager, memory_store)


def create_project_manager(workspace: Path) -> ProjectManager:
    """
    Create a project manager instance

    Args:
        workspace: Workspace directory

    Returns:
        ProjectManager instance
    """
    return ProjectManager(workspace)


def create_agent_factory(workspace: Path) -> AgentFactory:
    """
    Create an agent factory instance

    Args:
        workspace: Workspace directory

    Returns:
        AgentFactory instance
    """
    return AgentFactory(workspace)


def create_component_registry() -> ComponentRegistry:
    """
    Create a component registry instance

    Returns:
        ComponentRegistry instance
    """
    return ComponentRegistry()


def create_cross_project_learning(
    project_manager: ProjectManager,
    workspace: Path
) -> CrossProjectLearning:
    """
    Create a cross-project learning instance

    Args:
        project_manager: Project manager for cross-project analysis
        workspace: Workspace directory

    Returns:
        CrossProjectLearning instance
    """
    return CrossProjectLearning(
        project_manager=project_manager,
        workspace=workspace
    )


def create_dispatcher(
    event_bus: EventBus,
    token_economy: TokenEconomy,
    memory_store: MemoryStore,
    trace_manager: TraceManager,
    project_manager: ProjectManager,
    workspace: Path,
    config: Optional[LLMOSConfig] = None
) -> Dispatcher:
    """
    Create a dispatcher instance

    Args:
        event_bus: Event bus for dispatcher events
        token_economy: Token economy for cost tracking
        memory_store: Memory store for trace storage
        trace_manager: Trace manager for memory operations
        project_manager: Project manager for project-based execution
        workspace: Workspace directory
        config: Optional LLMOS configuration

    Returns:
        Dispatcher instance
    """
    return Dispatcher(
        event_bus=event_bus,
        token_economy=token_economy,
        memory_store=memory_store,
        trace_manager=trace_manager,
        project_manager=project_manager,
        workspace=workspace,
        config=config
    )


def create_llmos_services(config: LLMOSConfig):
    """
    Create all LLMOS services using configuration

    This is a convenience factory that creates all services in the correct
    order with proper dependencies. Use this for production deployments.

    Args:
        config: LLMOS configuration

    Returns:
        Dictionary with all service instances
    """
    # Create kernel components
    event_bus = create_event_bus()
    token_economy = create_token_economy(config.kernel.budget_usd)
    scheduler = create_scheduler(event_bus)
    watchdog = create_watchdog(event_bus)

    # Create memory components
    memory_store = create_memory_store(config.workspace)
    trace_manager = create_trace_manager(
        config.workspace,
        enable_llm_matching=config.memory.enable_llm_matching
    )
    memory_query = create_memory_query(trace_manager, memory_store)

    # Create Phase 2 components
    project_manager = create_project_manager(config.workspace)
    agent_factory = create_agent_factory(config.workspace)
    component_registry = create_component_registry()
    cross_project_learning = create_cross_project_learning(
        project_manager,
        config.workspace
    )

    # Create dispatcher
    dispatcher = create_dispatcher(
        event_bus=event_bus,
        token_economy=token_economy,
        memory_store=memory_store,
        trace_manager=trace_manager,
        project_manager=project_manager,
        workspace=config.workspace,
        config=config
    )

    return {
        'event_bus': event_bus,
        'token_economy': token_economy,
        'scheduler': scheduler,
        'watchdog': watchdog,
        'memory_store': memory_store,
        'trace_manager': trace_manager,
        'memory_query': memory_query,
        'project_manager': project_manager,
        'agent_factory': agent_factory,
        'component_registry': component_registry,
        'cross_project_learning': cross_project_learning,
        'dispatcher': dispatcher,
    }
