#!/usr/bin/env python3
"""
LLM OS (llmos) - Boot Entry Point
Based on Claude Agent SDK

This is the main entry point for the LLM Operating System.
Treats the LLM as the CPU, Python as the motherboard, and tokens as energy.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

from kernel.bus import EventBus
from kernel.scheduler import Scheduler
from kernel.watchdog import Watchdog
from kernel.project_manager import ProjectManager, Project
from kernel.agent_factory import AgentFactory
from kernel.component_registry import ComponentRegistry
from memory.store_sdk import MemoryStore
from memory.traces_sdk import TraceManager
from memory.query_sdk import MemoryQueryInterface
from memory.cross_project_sdk import CrossProjectLearning
from interfaces.dispatcher import Dispatcher
from kernel.token_economy import TokenEconomy
from kernel.config import LLMOSConfig
from kernel.service_factory import (
    create_event_bus,
    create_token_economy,
    create_scheduler,
    create_watchdog,
    create_memory_store,
    create_trace_manager,
    create_memory_query,
    create_project_manager,
    create_agent_factory,
    create_component_registry,
    create_cross_project_learning,
    create_dispatcher,
)


class LLMOS:
    """
    The LLM Operating System

    Separates Cognitive Compute (LLM) from Somatic Compute (Python)
    Managed by a strict Token Economy.

    Now with Phase 2 capabilities:
    - Project management (llmunix-style)
    - Dynamic agent creation
    - Multi-agent orchestration
    - Component registry
    - Memory query interface
    """

    def __init__(
        self,
        budget_usd: float = 10.0,
        workspace: Optional[Path] = None,
        project_name: Optional[str] = None,
        config: Optional[LLMOSConfig] = None,
        # Optional dependency injection (for testing)
        event_bus: Optional[EventBus] = None,
        token_economy: Optional[TokenEconomy] = None,
        scheduler: Optional[Scheduler] = None,
        watchdog: Optional[Watchdog] = None,
        memory_store: Optional[MemoryStore] = None,
        trace_manager: Optional[TraceManager] = None,
        memory_query: Optional[MemoryQueryInterface] = None,
        project_manager: Optional[ProjectManager] = None,
        agent_factory: Optional[AgentFactory] = None,
        component_registry: Optional[ComponentRegistry] = None,
        cross_project_learning: Optional[CrossProjectLearning] = None,
        dispatcher: Optional[Dispatcher] = None,
    ):
        """
        Initialize the LLM OS

        Args:
            budget_usd: Token budget in USD (ignored if config provided)
            workspace: Workspace directory (defaults to ./workspace)
            project_name: Optional project name (creates/loads project)
            config: Optional LLMOSConfig instance (overrides other params)

            # Optional dependency injection (for testing):
            event_bus: Event bus instance
            token_economy: Token economy instance
            scheduler: Scheduler instance
            watchdog: Watchdog instance
            memory_store: Memory store instance
            trace_manager: Trace manager instance
            memory_query: Memory query interface instance
            project_manager: Project manager instance
            agent_factory: Agent factory instance
            component_registry: Component registry instance
            cross_project_learning: Cross-project learning instance
            dispatcher: Dispatcher instance

        Example:
            # Simple usage (backward compatible)
            os = LLMOS(budget_usd=10.0)

            # With configuration preset
            config = LLMOSConfig.production()
            os = LLMOS(config=config)

            # With dependency injection (testing)
            os = LLMOS(
                event_bus=mock_event_bus,
                token_economy=mock_token_economy
            )
        """
        # Use config or create from parameters
        if config is None:
            config = LLMOSConfig(
                workspace=workspace or Path("./workspace"),
                kernel=__import__('kernel.config', fromlist=['KernelConfig']).KernelConfig(
                    budget_usd=budget_usd
                )
            )

        self.config = config
        self.workspace = config.workspace
        self.workspace.mkdir(exist_ok=True)

        # Initialize kernel components (use injected or create defaults)
        self.event_bus = event_bus or create_event_bus()
        self.token_economy = token_economy or create_token_economy(config.kernel.budget_usd)
        self.scheduler = scheduler or create_scheduler(self.event_bus)
        self.watchdog = watchdog or create_watchdog(self.event_bus)

        # Initialize memory components (use injected or create defaults)
        self.memory_store = memory_store or create_memory_store(self.workspace)
        self.trace_manager = trace_manager or create_trace_manager(
            self.workspace,
            enable_llm_matching=config.memory.enable_llm_matching
        )
        self.memory_query = memory_query or create_memory_query(
            self.trace_manager,
            self.memory_store
        )

        # Initialize Phase 2 components (use injected or create defaults)
        self.project_manager = project_manager or create_project_manager(self.workspace)
        self.agent_factory = agent_factory or create_agent_factory(self.workspace)
        self.component_registry = component_registry or create_component_registry()
        self.cross_project_learning = cross_project_learning or create_cross_project_learning(
            self.project_manager,
            self.workspace
        )

        # Register built-in agents
        self._register_builtin_agents()

        # Create/load project if specified
        self.current_project: Optional[Project] = None
        if project_name:
            self.current_project = self.project_manager.create_project(project_name)

        # Initialize dispatcher (use injected or create default)
        self.dispatcher = dispatcher or create_dispatcher(
            event_bus=self.event_bus,
            token_economy=self.token_economy,
            memory_store=self.memory_store,
            trace_manager=self.trace_manager,
            project_manager=self.project_manager,
            workspace=self.workspace,
            config=self.config
        )

        self._running = False

    def _register_builtin_agents(self):
        """Register built-in system agents and tools"""
        from kernel.agent_factory import SYSTEM_AGENT_TEMPLATE

        # Register system agent
        self.component_registry.register_agent(SYSTEM_AGENT_TEMPLATE)

        # Register any custom agents from agents/ directory
        for agent_spec in self.agent_factory.list_agents():
            self.component_registry.register_agent(agent_spec)

        # Import system tools to make them available
        # (Hybrid Architecture: enables self-modification)
        try:
            import plugins.system_tools
            print("🔧 Loaded system tools (create_agent, list_agents, modify_agent)")
        except ImportError as e:
            print(f"⚠️  Could not load system tools: {e}")

    async def boot(self):
        """Boot the operating system"""
        print("🚀 Booting LLM OS (Phase 2 - Claude SDK Memory)...")
        print(f"💰 Token Budget: ${self.token_economy.balance:.2f}")
        print(f"📁 Workspace: {self.workspace.absolute()}")
        print(f"💾 Memory: /memories (Claude SDK file-based)")

        if self.current_project:
            print(f"📂 Current Project: {self.current_project.name}")

        # Show memory stats
        mem_stats = self.memory_query.get_memory_statistics()
        print(f"🧠 Traces: {mem_stats.get('total_traces', 0)} traces, "
              f"{mem_stats.get('high_confidence_count', 0)} high-confidence, "
              f"{mem_stats.get('facts_count', 0)} facts")

        # Show available agents
        agents = self.component_registry.list_agents()
        print(f"🤖 Agents: {len(agents)} registered")

        print()

        # Start kernel components
        await self.scheduler.start()
        await self.watchdog.start()

        self._running = True
        print("✅ LLM OS Ready (Learner | Follower | Orchestrator modes available)")
        print()

    async def execute(
        self,
        goal: str,
        mode: str = "AUTO",
        project_name: Optional[str] = None,
        max_cost_usd: float = 5.0
    ):
        """
        Execute a goal using Learner/Follower/Orchestrator pattern

        Args:
            goal: Natural language goal to execute
            mode: "AUTO" (auto-detect), "LEARNER", "FOLLOWER", or "ORCHESTRATOR"
            project_name: Optional project name (creates if doesn't exist)
            max_cost_usd: Maximum cost budget for execution

        Returns:
            Result dictionary
        """
        if not self._running:
            raise RuntimeError("OS not booted. Call boot() first.")

        print(f"🎯 Goal: {goal}")

        # Get/create project if specified
        project = None
        if project_name:
            project = self.project_manager.get_project(project_name)
            if not project:
                project = self.project_manager.create_project(project_name)
                print(f"📂 Created project: {project.name}")
        elif self.current_project:
            project = self.current_project

        # Get memory insights
        recommendations = await self.memory_query.get_recommendations(goal)
        if recommendations:
            print("\n💡 Memory Recommendations:")
            for rec in recommendations[:3]:  # Show top 3
                print(f"   - {rec}")

        # Get cross-project insights
        cross_project_recs = await self.cross_project_learning.get_cross_project_recommendations(
            current_project=project,
            goal=goal
        )
        if cross_project_recs:
            print("\n🌐 Cross-Project Insights:")
            for rec in cross_project_recs[:3]:  # Show top 3
                print(f"   - {rec}")

        print()

        # Dispatch to appropriate mode
        result = await self.dispatcher.dispatch(
            goal=goal,
            mode=mode,
            project=project,
            max_cost_usd=max_cost_usd
        )

        return result

    def create_project(self, name: str, description: str = "") -> Project:
        """
        Create a new project

        Args:
            name: Project name
            description: Project description

        Returns:
            Project instance
        """
        project = self.project_manager.create_project(name, description)
        self.current_project = project
        return project

    def set_project(self, name: str):
        """
        Set current project

        Args:
            name: Project name
        """
        project = self.project_manager.get_project(name)
        if project:
            self.current_project = project
        else:
            raise ValueError(f"Project {name} not found")

    def list_projects(self):
        """List all projects"""
        return self.project_manager.list_projects()

    def create_agent(self, **kwargs):
        """
        Create a new agent

        Args:
            **kwargs: Agent specification parameters

        Returns:
            AgentSpec instance
        """
        agent = self.agent_factory.create_agent(**kwargs)
        self.component_registry.register_agent(agent)
        return agent

    def list_agents(self, **kwargs):
        """
        List registered agents

        Args:
            **kwargs: Filter parameters

        Returns:
            List of AgentSpec instances
        """
        return self.component_registry.list_agents(**kwargs)

    async def get_cross_project_insights(self, **kwargs):
        """
        Get cross-project insights

        Args:
            **kwargs: Filter parameters for insights

        Returns:
            List of CrossProjectInsight instances
        """
        return await self.cross_project_learning.analyze_common_patterns(**kwargs)

    async def get_reusable_agents(self, **kwargs):
        """
        Get reusable agent patterns from cross-project analysis

        Args:
            **kwargs: Filter parameters

        Returns:
            List of ReusableAgent instances
        """
        return await self.cross_project_learning.identify_reusable_agents(**kwargs)

    async def get_project_summary(self, project_name: str):
        """
        Get learning summary for a project

        Args:
            project_name: Project name

        Returns:
            Dictionary with project insights
        """
        project = self.project_manager.get_project(project_name)
        if not project:
            raise ValueError(f"Project {project_name} not found")

        return await self.cross_project_learning.get_project_learning_summary(project)

    async def shutdown(self):
        """Shutdown the operating system"""
        print()
        print("🛑 Shutting down LLM OS...")

        self._running = False

        # Stop kernel components
        await self.scheduler.stop()
        await self.watchdog.stop()

        # Save state
        print(f"💾 Final Balance: ${self.token_economy.balance:.2f}")
        print(f"📊 Total Spent: ${sum(log.cost for log in self.token_economy.spend_log):.2f}")

        print("✅ Shutdown complete")


async def run_terminal(
    user_id: str,
    team_id: Optional[str] = None,
    use_real_data: bool = True,
    ui_mode: str = "textual"
):
    """
    Run the Cron Terminal UI with real LLMOS data.

    Args:
        user_id: User identifier
        team_id: Team identifier
        use_real_data: Connect to real LLMOS components (vs mock data)
        ui_mode: "textual" (MC-style TUI) or "legacy" (basic ANSI)
    """
    print("🖥️  Starting Cron Terminal...")
    print(f"👤 User: {user_id}")
    if team_id:
        print(f"👥 Team: {team_id}")
    print(f"🎨 UI Mode: {ui_mode}")

    # Initialize LLMOS components for real data
    data_provider = None
    status_callback = None
    events_callback = None
    suggestions_callback = None
    cron_callback = None

    if use_real_data:
        print("📊 Connecting to LLMOS data...")

        from kernel.terminal.llmos_data_provider import LLMOSDataProvider
        from memory.traces_sdk import TraceManager
        from memory.store_sdk import MemoryStore
        from kernel.token_economy import TokenEconomy

        workspace = Path("./workspace")
        workspace.mkdir(exist_ok=True)

        # Initialize components
        trace_manager = TraceManager(
            memories_dir=workspace / "memories",
            workspace=workspace,
            enable_llm_matching=False  # Disable for terminal (faster)
        )
        memory_store = MemoryStore(workspace)
        token_economy = TokenEconomy(budget_usd=10.0)

        # Create data provider
        data_provider = LLMOSDataProvider(
            trace_manager=trace_manager,
            memory_store=memory_store,
            token_economy=token_economy,
            workspace=workspace
        )

        # Set callbacks
        status_callback = data_provider.get_system_status
        events_callback = data_provider.get_events
        suggestions_callback = data_provider.get_suggestions
        cron_callback = data_provider.handle_user_message

        # Show initial stats
        trace_stats = trace_manager.get_statistics()
        memory_stats = memory_store.get_statistics()
        print(f"🧠 Traces: {trace_stats.get('total_traces', 0)} | Facts: {memory_stats.get('facts_count', 0)} | Insights: {memory_stats.get('insights_count', 0)}")

    print()

    # Run the appropriate UI
    if ui_mode == "textual":
        # Textual UI (Midnight Commander style)
        try:
            from kernel.terminal.app import CronTerminalApp
        except ImportError:
            print("❌ Textual UI requires the 'textual' package.")
            print("   Install with: pip install textual")
            print("   Or use --ui legacy for the basic terminal.")
            return

        print("🎨 Starting Midnight Commander-style UI...")
        print()
        print("FUNCTION KEYS:")
        print("  F1=Help  F5=Refresh  F10=Quit")
        print()
        print("NAVIGATION:")
        print("  Tab=Switch panels  j/k=Up/Down  Space=Expand")
        print()

        app = CronTerminalApp(
            user_id=user_id,
            team_id=team_id or "default",
            status_callback=status_callback,
            events_callback=events_callback,
            suggestions_callback=suggestions_callback,
            cron_callback=cron_callback,
        )
        await app.run_async()

    else:
        # Legacy UI (basic ANSI)
        from kernel.terminal import CronTerminal

        print("CONTROLS:")
        print("  ↑/↓     Navigate tree or scroll")
        print("  ←/→     Collapse/expand nodes")
        print("  Tab     Switch panels")
        print("  Enter   Select / send message")
        print("  r       Refresh data")
        print("  q       Quit")
        print()

        # Small delay to let user read the instructions
        import time
        time.sleep(2)

        # Create terminal with callbacks
        terminal = CronTerminal(
            user_id=user_id,
            team_id=team_id or "default",
            status_callback=status_callback,
            events_callback=events_callback,
            suggestions_callback=suggestions_callback,
            cron_callback=cron_callback
        )

        await terminal.run()


async def main():
    """Main entry point"""
    # Handle terminal mode separately (doesn't need full OS boot)
    if len(sys.argv) > 1 and sys.argv[1] == "terminal":
        # Parse terminal arguments
        user_id = "user"
        team_id = None
        ui_mode = "textual"  # Default to Textual (MC-style)

        # Simple argument parsing
        args = sys.argv[2:]
        i = 0
        while i < len(args):
            if args[i] == "--user" and i + 1 < len(args):
                user_id = args[i + 1]
                i += 2
            elif args[i] == "--team" and i + 1 < len(args):
                team_id = args[i + 1]
                i += 2
            elif args[i] == "--ui" and i + 1 < len(args):
                ui_mode = args[i + 1]
                i += 2
            else:
                i += 1

        await run_terminal(user_id, team_id, ui_mode=ui_mode)
        return

    # Create and boot the OS
    os = LLMOS(budget_usd=10.0)
    await os.boot()

    try:
        # Interactive mode
        if len(sys.argv) > 1 and sys.argv[1] == "interactive":
            print("📝 Interactive Mode (type 'exit' to quit)")
            print()

            while True:
                try:
                    goal = input("llmos> ")
                    if goal.lower() in ["exit", "quit"]:
                        break
                    if goal.strip():
                        await os.execute(goal)
                except KeyboardInterrupt:
                    break

        # Single command mode
        elif len(sys.argv) > 1:
            # Parse --mode flag if present
            args = sys.argv[1:]
            mode = "AUTO"
            goal_parts = []

            i = 0
            while i < len(args):
                if args[i] == "--mode" and i + 1 < len(args):
                    mode = args[i + 1].upper()
                    i += 2
                else:
                    goal_parts.append(args[i])
                    i += 1

            goal = " ".join(goal_parts)
            await os.execute(goal, mode=mode)

        else:
            print("Usage:")
            print("  python boot.py interactive                              # Interactive mode")
            print("  python boot.py terminal --user NAME [--team TEAM]       # Cron Terminal (Textual)")
            print("  python boot.py terminal --user NAME --ui legacy         # Cron Terminal (Legacy)")
            print("  python boot.py terminal --user NAME --ui textual        # Cron Terminal (MC-style)")
            print("  python boot.py <goal>                                   # Execute single goal")
            print("  python boot.py <goal> --mode ORCHESTRATOR               # Execute with specific mode")
            print()
            print("Modes: AUTO, LEARNER, FOLLOWER, MIXED, CRYSTALLIZED, ORCHESTRATOR")

    finally:
        await os.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
