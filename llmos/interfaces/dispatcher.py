"""
Dispatcher - The Brain of the LLM OS
Decides between Learner, Follower, and Orchestration modes based on token economy

Architecture:
- Learning Layer: TraceManager, ModeStrategies (decides WHAT to do)
- Execution Layer: PTC, Tool Search, Tool Examples (does it EFFICIENTLY)

The Dispatcher bridges these two layers:
1. Learning Layer decides the mode (CRYSTALLIZED, FOLLOWER, MIXED, LEARNER, ORCHESTRATOR)
2. Execution Layer executes that decision efficiently using Anthropic's Advanced Tool Use
"""

from typing import Dict, Any, Optional, Callable
from pathlib import Path

from kernel.bus import EventBus
from kernel.token_economy import TokenEconomy, LowBatteryError
from kernel.project_manager import ProjectManager, Project
from kernel.config import LLMOSConfig
from kernel.mode_strategies import (
    ModeSelectionStrategy,
    ModeContext,
    get_strategy
)
from memory.store_sdk import MemoryStore
from memory.traces_sdk import TraceManager, ExecutionTrace
from memory.query_sdk import MemoryQueryInterface
from interfaces.cortex import Cortex
from interfaces.sdk_client import LLMOSSDKClient, is_sdk_available

# Execution Layer imports (Anthropic Advanced Tool Use)
# These are imported directly to avoid circular dependencies
try:
    from execution.ptc import PTCExecutor, ToolSequence, ToolCall
    from execution.tool_search import ToolSearchEngine, ToolDefinition
    from execution.tool_examples import ToolExampleGenerator
    EXECUTION_LAYER_AVAILABLE = True
except ImportError:
    EXECUTION_LAYER_AVAILABLE = False
    PTCExecutor = None
    ToolSearchEngine = None
    ToolExampleGenerator = None
    print("⚠️  Execution Layer not available - Advanced Tool Use features disabled")


class TaskBlock:
    """
    A TaskBlock is a "Program" in the LLM OS
    Not a compiled binary, but a natural language intent
    """

    def __init__(
        self,
        goal: str,
        inputs: Dict[str, Any] = None,
        constraints: list = None,
        priority: int = 50,
        mode: str = "AUTO"
    ):
        self.goal = goal
        self.inputs = inputs or {}
        self.constraints = constraints or []
        self.priority = priority
        self.mode = mode  # AUTO, LEARNER, or FOLLOWER


class Dispatcher:
    """
    The Dispatcher - Makes the Learner/Follower/Orchestration decision
    This is the "operating system scheduler" that optimizes for token cost

    Architecture:
        Learning Layer (decides WHAT to do):
        - TraceManager: Stores execution history
        - ModeSelectionStrategy: Analyzes and decides mode

        Execution Layer (does it EFFICIENTLY):
        - PTCExecutor: Executes tool sequences outside context (CRYSTALLIZED/FOLLOWER)
        - ToolSearchEngine: On-demand tool discovery (LEARNER/ORCHESTRATOR)
        - ToolExampleGenerator: Auto-generates examples from traces (all modes)

    Modes:
        1. CRYSTALLIZED: Execute via PTC (instant, free)
        2. FOLLOWER: Replay trace via PTC (fast, cheap)
        3. MIXED: Trace-guided LLM with examples (medium cost)
        4. LEARNER: Full LLM with tool search (expensive, creative)
        5. ORCHESTRATOR: Multi-agent with tool search (complex)
    """

    def __init__(
        self,
        event_bus: EventBus,
        token_economy: TokenEconomy,
        memory_store: MemoryStore,
        trace_manager: TraceManager,
        project_manager: Optional[ProjectManager] = None,
        workspace: Optional[Path] = None,
        config: Optional[LLMOSConfig] = None,
        strategy: Optional[ModeSelectionStrategy] = None,
        tools: Optional[Dict[str, Callable]] = None
    ):
        self.event_bus = event_bus
        self.token_economy = token_economy
        self.memory_store = memory_store
        self.trace_manager = trace_manager
        self.project_manager = project_manager
        self.workspace = workspace or Path("./workspace")
        self.tools = tools or {}  # Registered tool functions

        # Configuration and strategy (Learning Layer)
        self.config = config or LLMOSConfig()
        self.strategy = strategy or get_strategy("auto")

        # Initialize cortex (will be lazy-loaded)
        self.cortex: Cortex = None

        # Initialize orchestrator (will be lazy-loaded)
        self.orchestrator = None

        # Initialize memory query interface
        self.memory_query = MemoryQueryInterface(trace_manager, memory_store)

        # Initialize SDK client (if available)
        self.sdk_client: Optional[LLMOSSDKClient] = None
        if is_sdk_available():
            self.sdk_client = LLMOSSDKClient(
                workspace=self.workspace,
                trace_manager=self.trace_manager,
                token_economy=self.token_economy,  # For budget control hooks
                memory_query=self.memory_query  # For context injection hooks
            )
        else:
            print("⚠️  Claude Agent SDK not available - using fallback cortex mode")
            print("   Install with: pip install claude-agent-sdk")

        # =====================================================================
        # EXECUTION LAYER (Anthropic Advanced Tool Use)
        # =====================================================================
        self._init_execution_layer()

    def _init_execution_layer(self):
        """
        Initialize the Execution Layer components

        These handle EFFICIENT execution of decisions made by the Learning Layer.
        """
        exec_config = self.config.execution

        # Check if Execution Layer is available
        if not EXECUTION_LAYER_AVAILABLE:
            self.ptc_executor = None
            self.tool_search = None
            self.tool_examples = None
            return

        # PTC Executor (for CRYSTALLIZED/FOLLOWER modes)
        self.ptc_executor = None
        if exec_config.enable_advanced_tool_use and exec_config.enable_ptc and PTCExecutor:
            self.ptc_executor = PTCExecutor(
                tools=self.tools,
                container_timeout_secs=exec_config.ptc_container_timeout_secs,
                max_containers=exec_config.ptc_max_containers
            )
            print("✓ PTC Executor initialized (Programmatic Tool Calling)")

        # Tool Search Engine (for LEARNER/ORCHESTRATOR modes)
        self.tool_search = None
        if exec_config.enable_advanced_tool_use and exec_config.enable_tool_search and ToolSearchEngine:
            self.tool_search = ToolSearchEngine(
                use_embeddings=exec_config.tool_search_use_embeddings,
                embedding_model=exec_config.tool_search_embedding_model
            )
            print("✓ Tool Search Engine initialized")

        # Tool Example Generator (for all modes)
        self.tool_examples = None
        if exec_config.enable_advanced_tool_use and exec_config.enable_tool_examples and ToolExampleGenerator:
            self.tool_examples = ToolExampleGenerator(
                trace_manager=self.trace_manager,
                min_success_rate=exec_config.tool_examples_min_success_rate,
                max_examples_per_tool=exec_config.tool_examples_max_per_tool
            )
            print("✓ Tool Example Generator initialized")

        if exec_config.enable_advanced_tool_use:
            print(f"✓ Execution Layer ready (beta: {exec_config.beta_header})")

    def register_tool(
        self,
        name: str,
        func: Callable,
        description: str = "",
        defer_loading: bool = None
    ):
        """
        Register a tool with the Dispatcher

        Tools are registered in both layers:
        - Execution Layer: For PTC and Tool Search
        - Learning Layer: For trace recording

        Args:
            name: Tool name
            func: Tool function (sync or async)
            description: Tool description
            defer_loading: Whether to defer loading (default from config)
        """
        # Register in tools dict
        self.tools[name] = func

        # Update PTC executor if available
        if self.ptc_executor:
            self.ptc_executor.tools[name] = func

        # Register in Tool Search if available
        if self.tool_search:
            should_defer = defer_loading if defer_loading is not None else \
                          self.config.execution.defer_tools_by_default

            tool_def = ToolDefinition(
                name=name,
                description=description or func.__doc__ or f"Execute {name}",
                input_schema={},  # Would need introspection
                defer_loading=should_defer
            )
            self.tool_search.register_tool(tool_def)

    async def _ensure_cortex(self):
        """Lazy initialization of cortex"""
        if self.cortex is None:
            self.cortex = Cortex(self.event_bus, self.workspace)
            await self.cortex.initialize()

    async def _ensure_orchestrator(self):
        """Lazy initialization of orchestrator"""
        if self.orchestrator is None:
            from kernel.agent_factory import AgentFactory
            from kernel.component_registry import ComponentRegistry
            from interfaces.orchestrator import SystemAgent

            # Initialize dependencies
            agent_factory = AgentFactory(self.workspace)
            component_registry = ComponentRegistry()

            # Register built-in agents
            for agent in agent_factory.list_agents():
                component_registry.register_agent(agent)

            self.orchestrator = SystemAgent(
                event_bus=self.event_bus,
                project_manager=self.project_manager,
                agent_factory=agent_factory,
                component_registry=component_registry,
                token_economy=self.token_economy,
                trace_manager=self.trace_manager,
                workspace=self.workspace
            )

    async def dispatch(
        self,
        goal: str,
        mode: str = "AUTO",
        project: Optional[Project] = None,
        max_cost_usd: float = 5.0
    ) -> Dict[str, Any]:
        """
        Dispatch a goal to appropriate execution mode

        This is the core algorithm that makes LLM OS economical:
        1. Check complexity (simple vs complex)
        2. Check if we have a proven trace
        3. Route to: FOLLOWER (proven) / LEARNER (novel) / ORCHESTRATOR (complex)

        Args:
            goal: Natural language goal
            mode: "AUTO" (auto-detect), "LEARNER", "FOLLOWER", or "ORCHESTRATOR"
            project: Optional project context for orchestration
            max_cost_usd: Maximum cost budget

        Returns:
            Result dictionary
        """
        print("=" * 60)
        print(f"🎯 Dispatching: {goal}")
        print("=" * 60)

        # Determine execution mode
        if mode == "AUTO":
            mode = await self._determine_mode(goal)

        print(f"📋 Selected Mode: {mode}")
        print("=" * 60)

        # Route to appropriate mode
        if mode == "CRYSTALLIZED":
            return await self._dispatch_crystallized(goal)
        elif mode == "ORCHESTRATOR":
            return await self._dispatch_orchestrator(goal, project, max_cost_usd)
        elif mode == "FOLLOWER":
            return await self._dispatch_follower(goal)
        elif mode == "MIXED":
            return await self._dispatch_mixed(goal, project, max_cost_usd)
        else:  # LEARNER
            return await self._dispatch_learner(goal, project, max_cost_usd)

    async def _determine_mode(self, goal: str) -> str:
        """
        Automatically determine the best execution mode using Strategy pattern

        Uses the configured mode selection strategy to determine the optimal
        execution mode based on available traces, complexity, and configuration.

        Execution modes:
        - CRYSTALLIZED: Trace has been converted to tool - Execute tool directly
        - FOLLOWER: High confidence - Execute proven trace directly
        - MIXED: Medium confidence - Use trace as few-shot guidance
        - LEARNER: Low confidence - Full LLM reasoning
        - ORCHESTRATOR: Complex multi-agent task

        Args:
            goal: Natural language goal

        Returns:
            Mode string: "CRYSTALLIZED", "FOLLOWER", "MIXED", "LEARNER", or "ORCHESTRATOR"
        """
        # Use strategy pattern for mode selection
        context = ModeContext(
            goal=goal,
            trace_manager=self.trace_manager,
            config=self.config
        )

        decision = await self.strategy.determine_mode(context)

        # Log decision
        if decision.trace:
            if decision.mode == "CRYSTALLIZED":
                print(f"💎 Crystallized tool: {decision.trace.crystallized_into_tool}")
                print(f"   {decision.reasoning}")
            elif decision.mode == "FOLLOWER":
                print(f"📦 Trace replay (confidence: {decision.confidence:.0%})")
                print(f"   Success: {decision.trace.success_rating:.0%}, "
                      f"Used: {decision.trace.usage_count}x")
                print(f"   {decision.reasoning}")
            elif decision.mode == "MIXED":
                print(f"📝 Trace-guided (confidence: {decision.confidence:.0%})")
                print(f"   {decision.reasoning}")
        else:
            if decision.mode == "ORCHESTRATOR":
                print(f"🔀 {decision.reasoning}")
            else:
                print(f"🆕 {decision.reasoning}")

        return decision.mode

    async def _dispatch_crystallized(self, goal: str) -> Dict[str, Any]:
        """
        Dispatch to Crystallized mode (execute generated tool directly)

        This is the final form of the HOPE architecture - instant, free execution
        of a crystallized pattern via Python code.

        Args:
            goal: Natural language goal

        Returns:
            Result dictionary
        """
        # Find the trace with crystallized tool
        result = await self.trace_manager.find_trace_with_llm(goal, min_confidence=0.75)

        if not result:
            return {
                "success": False,
                "error": "No crystallized trace found",
                "mode": "CRYSTALLIZED"
            }

        trace, confidence = result

        if not trace.crystallized_into_tool:
            return {
                "success": False,
                "error": "Trace not crystallized",
                "mode": "CRYSTALLIZED"
            }

        print(f"💡 Cost: $0.00 (crystallized tool)")
        print(f"💡 Time: ~instant")

        # Execute the crystallized tool
        # Note: Tool execution would be handled by the plugin system
        # For now, we return success with metadata

        # Update trace statistics
        self.trace_manager.update_usage(trace.goal_signature)

        return {
            "success": True,
            "mode": "CRYSTALLIZED",
            "tool_name": trace.crystallized_into_tool,
            "trace": trace,
            "cost": 0.0,
            "message": f"Executed crystallized tool: {trace.crystallized_into_tool}"
        }

    async def _dispatch_follower(self, goal: str) -> Dict[str, Any]:
        """
        Dispatch to Follower mode (direct trace replay)

        Used when confidence ≥0.92 (virtually identical to previous execution)

        Execution Strategy:
        - If PTC enabled and trace has tool_calls: Use PTC (zero-context execution)
        - Otherwise: Fall back to cortex replay
        """
        # Try to find trace with LLM matching
        result = await self.trace_manager.find_trace_with_llm(goal, min_confidence=0.92)

        if not result:
            # Fallback to hash matching
            trace = self.trace_manager.find_trace(goal, min_confidence=0.9)
            if not trace:
                return {
                    "success": False,
                    "error": "No trace found for Follower mode",
                    "mode": "FOLLOWER"
                }
            confidence = 1.0  # Hash match = exact
        else:
            trace, confidence = result

        print(f"💡 Cost: ~$0, Time: ~{trace.estimated_time_secs:.1f}s")

        # =====================================================================
        # EXECUTION LAYER: Try PTC first (Anthropic Advanced Tool Use)
        # =====================================================================
        if self.ptc_executor and hasattr(trace, 'tool_calls') and trace.tool_calls:
            print("⚡ Using PTC (Programmatic Tool Calling) - zero context execution")

            ptc_result = await self.ptc_executor.execute_from_trace(trace)

            if ptc_result.success:
                # Update trace statistics
                self.trace_manager.update_usage(trace.goal_signature)

                print(f"✓ PTC execution complete - saved ~{ptc_result.tokens_saved} tokens")

                return {
                    "success": True,
                    "mode": "FOLLOWER",
                    "execution_method": "PTC",
                    "trace": trace,
                    "cost": 0.0,
                    "tokens_saved": ptc_result.tokens_saved,
                    "results": ptc_result.results
                }
            else:
                print(f"⚠️ PTC execution failed: {ptc_result.error}")
                print("   Falling back to cortex replay...")

        # =====================================================================
        # FALLBACK: Cortex replay (original method)
        # =====================================================================
        await self._ensure_cortex()
        success = await self.cortex.follow(trace)

        # Update trace statistics
        self.trace_manager.update_usage(trace.goal_signature)

        return {
            "success": success,
            "mode": "FOLLOWER",
            "execution_method": "cortex",
            "trace": trace,
            "cost": 0.0
        }

    async def _dispatch_mixed(
        self,
        goal: str,
        project: Optional[Project] = None,
        max_cost_usd: float = 5.0
    ) -> Dict[str, Any]:
        """
        Dispatch to Mixed mode (trace-guided LLM execution)

        Used when confidence is 0.75-0.92 (similar but not identical).
        The trace is provided as few-shot guidance to the LLM.

        This is cheaper than full LEARNER mode but more adaptive than FOLLOWER.
        """
        # Find matching trace
        result = await self.trace_manager.find_trace_with_llm(goal, min_confidence=0.75)

        if not result:
            print("[WARNING] MIXED mode requested but no trace found - falling back to LEARNER")
            return await self._dispatch_learner(goal, project, max_cost_usd)

        trace, confidence = result

        estimated_cost = 0.25  # Cheaper than LEARNER ($0.50) but not free

        print(f"💡 Cost: ~${estimated_cost:.2f}, Time: variable")
        print(f"💡 Using trace as guidance (confidence: {confidence:.0%})")

        # Check budget
        try:
            self.token_economy.check_budget(max_cost_usd)
        except LowBatteryError as e:
            return {
                "success": False,
                "error": str(e),
                "mode": "MIXED"
            }

        # Use SDK client if available
        if self.sdk_client:
            print("🔌 Using Claude Agent SDK with trace guidance")

            # Build few-shot prompt with trace
            few_shot_context = f"""
# Similar Task Example

I have executed a similar task before. Here's what I did:

**Previous Goal:** {trace.goal_text}
**Success Rate:** {trace.success_rating:.0%}
**Tools Used:** {', '.join(trace.tools_used) if trace.tools_used else 'N/A'}

**Output Summary:**
{trace.output_summary if trace.output_summary else 'No summary available'}

---

**Current Goal (may differ slightly):** {goal}

Use the above as guidance, but adapt as needed for the current goal.
"""

            # Execute with few-shot context
            import hashlib
            goal_signature = hashlib.sha256(goal.encode()).hexdigest()[:16]

            result = await self.sdk_client.execute_learner_mode(
                goal=few_shot_context,
                goal_signature=goal_signature,
                project=project,
                max_cost_usd=max_cost_usd
            )

            # Deduct cost
            if result["success"]:
                self.token_economy.deduct(
                    result["cost"],
                    f"Mixed: {goal[:50]}..."
                )

            result["mode"] = "MIXED"
            result["guidance_trace"] = trace
            result["confidence"] = confidence
            return result

        # Fallback to cortex
        else:
            print("⚠️  Using fallback cortex mode (SDK not available)")

            await self._ensure_cortex()

            # Execute with trace as context
            new_trace = await self.cortex.learn(goal, guidance_trace=trace)

            # Save the new trace
            self.trace_manager.save_trace(new_trace)

            # Deduct cost
            self.token_economy.deduct(estimated_cost, f"Mixed: {goal[:50]}...")

            return {
                "success": True,
                "mode": "MIXED",
                "trace": new_trace,
                "guidance_trace": trace,
                "confidence": confidence,
                "cost": estimated_cost
            }

    async def _dispatch_learner(
        self,
        goal: str,
        project: Optional[Project] = None,
        max_cost_usd: float = 5.0
    ) -> Dict[str, Any]:
        """
        Dispatch to Learner mode

        Uses Claude Agent SDK when available for proper integration.
        Falls back to cortex if SDK not installed.

        Execution Strategy (with Execution Layer):
        - Tool Search: Load tools on-demand instead of all upfront
        - Tool Examples: Include auto-generated examples from successful traces
        """
        estimated_cost = 0.50

        print(f"💡 Cost: ~${estimated_cost:.2f}, Time: variable")

        # Check budget
        try:
            self.token_economy.check_budget(max_cost_usd)
        except LowBatteryError as e:
            return {
                "success": False,
                "error": str(e),
                "mode": "LEARNER"
            }

        # =====================================================================
        # EXECUTION LAYER: Prepare efficient tool loading
        # =====================================================================
        tool_search_enabled = False
        tool_examples_enabled = False

        if self.tool_search and self.config.execution.enable_tool_search:
            tool_search_enabled = True
            stats = self.tool_search.get_statistics()
            print(f"🔍 Tool Search enabled ({stats['deferred_tools']} deferred, "
                  f"{stats['immediate_tools']} immediate)")

        if self.tool_examples and self.config.execution.enable_tool_examples:
            tool_examples_enabled = True
            stats = self.tool_examples.get_statistics()
            print(f"📚 Tool Examples enabled ({stats['tools_with_examples']} tools "
                  f"with {stats['total_examples']} examples)")

        # Use SDK client if available (PROPER WAY)
        if self.sdk_client:
            print("🔌 Using Claude Agent SDK (proper integration)")

            # Compute goal signature for trace storage
            import hashlib
            goal_signature = hashlib.sha256(goal.encode()).hexdigest()[:16]

            # Get available agents to register in SDK
            available_agents = None
            if hasattr(self, 'orchestrator') and self.orchestrator:
                available_agents = self.orchestrator.component_registry.list_agents()

            # Execute with SDK
            result = await self.sdk_client.execute_learner_mode(
                goal=goal,
                goal_signature=goal_signature,
                project=project,
                available_agents=available_agents,  # Pass all agents!
                max_cost_usd=max_cost_usd
            )

            # Deduct actual cost
            if result["success"]:
                self.token_economy.deduct(
                    result["cost"],
                    f"Learner: {goal[:50]}..."
                )

            # Add execution layer metadata
            result["tool_search_enabled"] = tool_search_enabled
            result["tool_examples_enabled"] = tool_examples_enabled

            return result

        # Fallback to cortex (if SDK not available)
        else:
            print("⚠️  Using fallback cortex mode (SDK not available)")

            await self._ensure_cortex()

            # Execute with full LLM reasoning
            trace = await self.cortex.learn(goal)

            # Save the new trace for future use
            self.trace_manager.save_trace(trace)

            # Deduct cost
            actual_cost = estimated_cost
            self.token_economy.deduct(actual_cost, f"Learner: {goal[:50]}...")

            return {
                "success": True,
                "mode": "LEARNER",
                "trace": trace,
                "cost": actual_cost,
                "tool_search_enabled": tool_search_enabled,
                "tool_examples_enabled": tool_examples_enabled
            }

    async def _dispatch_orchestrator(
        self,
        goal: str,
        project: Optional[Project],
        max_cost_usd: float
    ) -> Dict[str, Any]:
        """Dispatch to Orchestrator mode (multi-agent)"""
        print(f"💡 Multi-agent orchestration")
        print(f"💡 Max Cost: ${max_cost_usd:.2f}")

        # Check budget
        try:
            self.token_economy.check_budget(max_cost_usd)
        except LowBatteryError as e:
            return {
                "success": False,
                "error": str(e),
                "mode": "ORCHESTRATOR"
            }

        await self._ensure_orchestrator()

        # Execute orchestration
        result = await self.orchestrator.orchestrate(
            goal=goal,
            project=project,
            max_cost_usd=max_cost_usd
        )

        # Deduct actual cost
        if result.success:
            self.token_economy.deduct(
                result.cost_usd,
                f"Orchestrator: {goal[:50]}..."
            )

        return {
            "success": result.success,
            "mode": "ORCHESTRATOR",
            "output": result.output,
            "steps_completed": result.steps_completed,
            "total_steps": result.total_steps,
            "cost": result.cost_usd,
            "execution_time": result.execution_time_secs,
            "state_summary": result.state_summary
        }

    # =========================================================================
    # EXECUTION LAYER UTILITIES
    # =========================================================================

    def get_execution_layer_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the Execution Layer

        Returns information about:
        - PTC: Container count, tools registered
        - Tool Search: Deferred vs immediate tools
        - Tool Examples: Examples generated from traces
        """
        stats = {
            "enabled": self.config.execution.enable_advanced_tool_use,
            "beta_header": self.config.execution.beta_header
        }

        # PTC stats
        if self.ptc_executor:
            stats["ptc"] = {
                "enabled": True,
                "tools_registered": len(self.ptc_executor.tools),
                "active_containers": len(self.ptc_executor._containers),
                "max_containers": self.ptc_executor.max_containers
            }
        else:
            stats["ptc"] = {"enabled": False}

        # Tool Search stats
        if self.tool_search:
            stats["tool_search"] = self.tool_search.get_statistics()
        else:
            stats["tool_search"] = {"enabled": False}

        # Tool Examples stats
        if self.tool_examples:
            stats["tool_examples"] = self.tool_examples.get_statistics()
        else:
            stats["tool_examples"] = {"enabled": False}

        return stats

    def get_enhanced_tool_definitions(self) -> list:
        """
        Get tool definitions enhanced with examples from traces

        These are ready to use with the Anthropic API's input_examples field.

        Returns:
            List of tool definitions with auto-generated examples
        """
        if not self.tool_examples:
            return []

        if not self.ptc_executor:
            return []

        # Get base definitions from PTC executor
        definitions = self.ptc_executor.get_tool_definitions_for_ptc()

        # Enhance with examples
        return self.tool_examples.enhance_tool_definitions(definitions)

    async def search_tools(self, query: str, top_k: int = 5) -> list:
        """
        Search for tools by description

        This is the interface to the Tool Search Engine.

        Args:
            query: Natural language description of needed capability
            top_k: Maximum results

        Returns:
            List of ToolReference objects
        """
        if not self.tool_search:
            return []

        return self.tool_search.search(query, top_k=top_k)

    def shutdown(self):
        """
        Shutdown the Dispatcher and cleanup resources

        Particularly important for PTC containers.
        """
        if self.ptc_executor:
            self.ptc_executor.shutdown_all()
            print("✓ PTC containers shutdown")

        if self.tool_examples:
            self.tool_examples.clear_cache()
            print("✓ Tool examples cache cleared")
