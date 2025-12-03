"""
Claude SDK Client Integration for llmos
Proper integration with Claude Agent SDK for Learner and Orchestrator modes
"""

from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from datetime import datetime

try:
    from claude_agent_sdk import ClaudeSDKClient, query as sdk_query, AgentDefinition
    from claude_agent_sdk.types import ClaudeAgentOptions, HookEvent, HookMatcher, Message
    from claude_agent_sdk.types import AssistantMessage, ResultMessage, TextBlock, ToolUseBlock, StreamEvent
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False
    AgentDefinition = None
    StreamEvent = None
    ClaudeSDKClient = None
    ClaudeAgentOptions = None
    HookEvent = None
    HookMatcher = None
    Message = None
    AssistantMessage = None
    ResultMessage = None
    TextBlock = None
    ToolUseBlock = None
    print("Warning: claude-agent-sdk not installed. Install with: pip install claude-agent-sdk")

from memory.traces_sdk import ExecutionTrace
from kernel.project_manager import Project
from kernel.agent_factory import AgentSpec, AgentFactory
from kernel.hooks import HookRegistry, create_default_hooks
from kernel.agent_loader import AgentLoader

# Import DynamicAgentManager for adaptive subagents
try:
    from kernel.dynamic_agents import DynamicAgentManager
    DYNAMIC_AGENTS_AVAILABLE = True
except ImportError:
    DynamicAgentManager = None
    DYNAMIC_AGENTS_AVAILABLE = False


def agent_spec_to_definition(spec: AgentSpec, model_override: str = None) -> 'AgentDefinition':
    """
    Convert AgentSpec to Claude SDK AgentDefinition

    Args:
        spec: AgentSpec instance
        model_override: Optional model override (from dynamic selection)

    Returns:
        AgentDefinition for SDK
    """
    if not SDK_AVAILABLE or AgentDefinition is None:
        raise RuntimeError("Claude Agent SDK not available")

    # Use model from spec if available, otherwise default to sonnet
    model = model_override or getattr(spec, 'model', 'sonnet') or 'sonnet'

    return AgentDefinition(
        description=spec.description,
        prompt=spec.system_prompt,
        tools=spec.tools,
        model=model
    )


class TraceBuilder:
    """
    Builds execution traces from SDK messages

    Captures tool usage, outputs, and metadata during execution
    to create replayable traces for Follower mode.

    Now also captures full tool_calls for PTC (Programmatic Tool Calling):
    - Stores tool name AND arguments for each call
    - Enables zero-context replay via Anthropic's Advanced Tool Use
    """

    def __init__(self, goal: str):
        self.goal = goal
        self.tools_used: List[str] = []
        self.tool_calls: List[Dict[str, Any]] = []  # NEW: Full tool call data for PTC
        self.output_parts: List[str] = []
        self.error_notes: List[str] = []
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.cost_usd: float = 0.0
        self.success: bool = True

    def add_message(self, message: 'Message'):
        """Process message and extract trace information"""
        if not SDK_AVAILABLE:
            return

        # Extract from AssistantMessage
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    self.output_parts.append(block.text)
                elif isinstance(block, ToolUseBlock):
                    # Track tool name (for quick filtering)
                    if block.name not in self.tools_used:
                        self.tools_used.append(block.name)

                    # NEW: Store full tool call data for PTC replay
                    self.tool_calls.append({
                        "name": block.name,
                        "arguments": block.input if hasattr(block, 'input') else {},
                        "id": block.id if hasattr(block, 'id') else None
                    })

        # Extract from ResultMessage
        elif isinstance(message, ResultMessage):
            self.end_time = datetime.now()
            self.cost_usd = message.total_cost_usd
            # Consider it successful if no error in result
            self.success = not hasattr(message, 'error') or message.error is None

    def add_tool_call(self, name: str, arguments: Dict[str, Any], tool_id: str = None):
        """
        Manually add a tool call (for non-SDK execution paths)

        Args:
            name: Tool name
            arguments: Tool arguments
            tool_id: Optional tool call ID
        """
        if name not in self.tools_used:
            self.tools_used.append(name)

        self.tool_calls.append({
            "name": name,
            "arguments": arguments,
            "id": tool_id
        })

    def add_error(self, error: str):
        """Add error note"""
        self.error_notes.append(error)
        self.success = False

    def to_trace(self, goal_signature: str) -> ExecutionTrace:
        """Convert to ExecutionTrace"""
        execution_time = (
            (self.end_time - self.start_time).total_seconds()
            if self.end_time else 0.0
        )

        return ExecutionTrace(
            goal_signature=goal_signature,
            goal_text=self.goal,
            success_rating=1.0 if self.success else 0.5,
            usage_count=1,
            created_at=self.start_time,
            last_used=None,
            estimated_cost_usd=self.cost_usd,
            estimated_time_secs=execution_time,
            mode="LEARNER",
            tools_used=self.tools_used if self.tools_used else None,
            output_summary="\n".join(self.output_parts[:5]) if self.output_parts else "",
            error_notes="\n".join(self.error_notes) if self.error_notes else "",
            tool_calls=self.tool_calls if self.tool_calls else None  # NEW: For PTC
        )


class LLMOSSDKClient:
    """
    Wrapper around Claude Agent SDK for llmos integration

    Provides proper integration between llmos architecture and
    Claude Agent SDK, handling:
    - Learner mode execution with trace capture
    - Orchestrator mode with multi-agent coordination
    - Hook-based trace building and control flow
    - Project-aware execution
    - System prompt presets
    - Streaming support
    """

    def __init__(
        self,
        workspace: Path,
        trace_manager: Optional[Any] = None,
        token_economy: Optional[Any] = None,
        memory_query: Optional[Any] = None,
        sentience_manager: Optional[Any] = None,
        agent_factory: Optional[AgentFactory] = None,
        config: Optional[Any] = None
    ):
        """
        Initialize SDK client wrapper

        Args:
            workspace: Workspace directory
            trace_manager: Optional trace manager for saving traces
            token_economy: Optional TokenEconomy for budget control hooks
            memory_query: Optional MemoryQueryInterface for context injection hooks
            sentience_manager: Optional SentienceManager for adaptive agents
            agent_factory: Optional AgentFactory for creating agents
            config: Optional LLMOSConfig
        """
        if not SDK_AVAILABLE:
            raise RuntimeError(
                "Claude Agent SDK not installed. "
                "Install with: pip install claude-agent-sdk"
            )

        self.workspace = Path(workspace)
        self.trace_manager = trace_manager
        self.token_economy = token_economy
        self.memory_query = memory_query
        self.sentience_manager = sentience_manager
        self.config = config

        # Initialize AgentLoader for Markdown-defined agents (Hybrid Architecture)
        self.agent_loader = AgentLoader(str(workspace / "agents"))

        # Initialize DynamicAgentManager for adaptive subagents
        self.dynamic_agent_manager: Optional[DynamicAgentManager] = None
        if DYNAMIC_AGENTS_AVAILABLE and agent_factory:
            self.dynamic_agent_manager = DynamicAgentManager(
                agent_factory=agent_factory,
                workspace=workspace,
                sentience_manager=sentience_manager,
                trace_manager=trace_manager,
                config=config
            )
            print("✓ DynamicAgentManager initialized (adaptive subagents enabled)")

    def _build_agent_options(
        self,
        agent_spec: Optional[AgentSpec] = None,
        project: Optional[Project] = None,
        available_agents: Optional[List[AgentSpec]] = None,
        permission_mode: str = "default",
        hooks: Optional[Dict[HookEvent, List[HookMatcher]]] = None,
        use_preset: bool = False,
        preset_name: str = "claude_code",
        model: str = "sonnet",
        max_turns: Optional[int] = None,
        env: Optional[Dict[str, str]] = None,
        include_partial_messages: bool = False,
        goal: Optional[str] = None
    ) -> ClaudeAgentOptions:
        """
        Build ClaudeAgentOptions from agent spec and project

        Args:
            agent_spec: Primary agent specification (for system_prompt)
            project: Project context
            available_agents: List of all available agents to register
            permission_mode: Permission mode for tools
            hooks: Optional hooks for events
            use_preset: Use system prompt preset instead of custom prompt
            preset_name: Preset name if using preset (e.g., "claude_code")
            model: Model to use ("sonnet", "opus", "haiku")
            max_turns: Maximum conversation turns
            env: Environment variables
            include_partial_messages: Enable streaming with partial messages
            goal: Current goal (for dynamic agent adaptation)

        Returns:
            ClaudeAgentOptions configured for llmos
        """
        # Determine working directory
        cwd = str(project.path) if project else str(self.workspace)

        # =====================================================================
        # DYNAMIC AGENT ADAPTATION (New!)
        # Adapts agents per-query based on sentience, memory, and traces
        # =====================================================================

        # Get sentience state if available (for adaptation)
        sentience_state = None
        if self.sentience_manager:
            try:
                sentience_state = self.sentience_manager.get_state()
            except Exception:
                pass

        # Get similar traces for context (if goal provided)
        similar_traces = None
        if goal and self.trace_manager:
            try:
                if hasattr(self.trace_manager, 'find_traces_with_llm'):
                    similar_traces = self.trace_manager.find_traces_with_llm(goal, limit=5)
                else:
                    similar_traces = self.trace_manager.list_traces()[:5]
            except Exception:
                pass

        # Build system prompt (support presets)
        system_prompt: Optional[Union[str, Dict[str, Any]]] = None

        if use_preset and agent_spec:
            # Use preset with appended custom prompt
            system_prompt = {
                "type": "preset",
                "preset": preset_name,
                "append": agent_spec.system_prompt
            }
        elif agent_spec:
            # Use custom prompt directly
            system_prompt = agent_spec.system_prompt

        # Register all available agents as AgentDefinitions
        # HYBRID ARCHITECTURE: Load Markdown agents first, then merge programmatic agents

        # 1. Load dynamic Markdown-defined agents from workspace/agents/*.md
        agents_dict = self.agent_loader.load_all_agents()

        # 2. Merge programmatic agents (Python-defined AgentSpec)
        # NOW WITH DYNAMIC ADAPTATION: Adapt each agent based on goal/sentience/traces
        if available_agents:
            for spec in available_agents:
                try:
                    # Apply dynamic adaptation if available
                    adapted_spec = spec
                    model_override = None

                    if self.dynamic_agent_manager and goal:
                        try:
                            adapted_spec = self.dynamic_agent_manager.get_adapted_agent(
                                agent_name=spec.name,
                                goal=goal,
                                sentience_state=sentience_state,
                                similar_traces=similar_traces
                            )
                            # Get model from adapted spec
                            model_override = getattr(adapted_spec, 'model', None)

                            # Log adaptation (if changed)
                            if adapted_spec.system_prompt != spec.system_prompt:
                                print(f"   🔄 Adapted agent '{spec.name}' for goal")
                            if model_override and model_override != getattr(spec, 'model', 'sonnet'):
                                print(f"   🎯 Selected model '{model_override}' for '{spec.name}'")

                        except ValueError:
                            # Agent not found in factory, use original spec
                            adapted_spec = spec
                        except Exception as e:
                            # Log but continue with original spec
                            print(f"   ⚠️ Agent adaptation failed for {spec.name}: {e}")
                            adapted_spec = spec

                    agents_dict[spec.name] = agent_spec_to_definition(adapted_spec, model_override)
                except Exception as e:
                    print(f"Warning: Could not register agent {spec.name}: {e}")

        # =====================================================================
        # DYNAMIC MODEL SELECTION FOR PRIMARY AGENT
        # Select optimal model based on task complexity
        # =====================================================================
        selected_model = model
        if self.dynamic_agent_manager and goal:
            try:
                # Create a temporary spec for model selection analysis
                from kernel.agent_factory import AgentSpec
                temp_spec = AgentSpec(
                    name="temp",
                    agent_type="system",
                    category="core",
                    description="Temporary for model selection",
                    tools=[],
                    version="1.0.0",
                    status="active",
                    mode=["LEARNER"],
                    system_prompt="",
                    capabilities=[],
                    constraints=[]
                )
                adapted_temp = self.dynamic_agent_manager._select_optimal_model(
                    temp_spec, goal, similar_traces
                )
                if hasattr(adapted_temp, 'model') and adapted_temp.model:
                    selected_model = adapted_temp.model
                    if selected_model != model:
                        print(f"   🎯 Dynamic model selection: {model} → {selected_model}")
            except Exception:
                pass

        # Build ClaudeAgentOptions with all fields
        options_dict = {
            "system_prompt": system_prompt,
            "cwd": cwd,
            "agents": agents_dict,
            "permission_mode": permission_mode,
            "hooks": hooks or {},
            "model": selected_model,
            "include_partial_messages": include_partial_messages
        }

        # Add optional fields
        if max_turns is not None:
            options_dict["max_turns"] = max_turns

        if env is not None:
            options_dict["env"] = env

        return ClaudeAgentOptions(**options_dict)

    async def execute_learner_mode(
        self,
        goal: str,
        goal_signature: str,
        agent_spec: Optional[AgentSpec] = None,
        project: Optional[Project] = None,
        available_agents: Optional[List[AgentSpec]] = None,
        max_cost_usd: float = 5.0,
        enable_hooks: bool = True,
        enable_streaming: bool = False,
        streaming_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Execute goal in Learner mode using Claude SDK

        This is the proper way to use the SDK - it handles all
        communication with Claude and returns structured messages.

        Args:
            goal: Goal to execute
            goal_signature: Signature for trace storage
            agent_spec: Optional agent specification
            project: Optional project context
            available_agents: List of all available agents to register
            max_cost_usd: Maximum cost budget
            enable_hooks: Enable default hooks (budget, security, trace capture)
            enable_streaming: Enable streaming with partial messages
            streaming_callback: Optional callback for streaming events

        Returns:
            Result dictionary with trace and execution details
        """
        trace_builder = TraceBuilder(goal)

        # Create hooks if enabled
        sdk_hooks = {}
        if enable_hooks:
            hook_registry = create_default_hooks(
                token_economy=self.token_economy,
                workspace=self.workspace,
                trace_builder=trace_builder,
                memory_query=self.memory_query,
                max_cost_usd=max_cost_usd
            )
            sdk_hooks = hook_registry.to_sdk_hooks()

            print(f"🔌 Enabled {len(sdk_hooks)} hook types")

        # Build SDK options with all available agents and hooks
        # NEW: Pass goal for dynamic agent adaptation
        options = self._build_agent_options(
            agent_spec=agent_spec,
            project=project,
            available_agents=available_agents,  # Register all agents!
            permission_mode="acceptEdits",  # Auto-accept edits in Learner mode
            hooks=sdk_hooks,
            include_partial_messages=enable_streaming,
            goal=goal  # Enable dynamic agent adaptation!
        )

        result = {
            "success": False,
            "mode": "LEARNER",
            "trace": None,
            "cost": 0.0,
            "output": ""
        }

        try:
            # Use SDK client
            async with ClaudeSDKClient(options=options) as client:
                # Connect and send goal
                await client.connect(prompt=goal)

                # Receive all messages
                async for message in client.receive_response():
                    # Handle streaming events
                    if enable_streaming and isinstance(message, StreamEvent):
                        if streaming_callback:
                            await streaming_callback(message)
                        # StreamEvent doesn't contribute to trace
                        continue

                    # Build trace from regular messages
                    trace_builder.add_message(message)

                    # Check cost budget
                    if isinstance(message, ResultMessage):
                        if message.total_cost_usd > max_cost_usd:
                            print(f"⚠️  Cost ${message.total_cost_usd:.2f} exceeded budget ${max_cost_usd:.2f}")

                        result["cost"] = message.total_cost_usd
                        result["success"] = True

            # Build trace
            trace = trace_builder.to_trace(goal_signature)
            result["trace"] = trace
            result["output"] = trace.output_summary

            # Save trace to memory
            if self.trace_manager:
                self.trace_manager.save_trace(trace)

        except Exception as e:
            trace_builder.add_error(str(e))
            result["error"] = str(e)

            # Still save failed trace for learning
            trace = trace_builder.to_trace(goal_signature)
            result["trace"] = trace

            if self.trace_manager:
                self.trace_manager.save_trace(trace)

        return result

    async def execute_one_shot_query(
        self,
        goal: str,
        agent_spec: Optional[AgentSpec] = None,
        project: Optional[Project] = None
    ) -> Dict[str, Any]:
        """
        Execute simple one-shot query using SDK query function

        Use this for simple, stateless queries where you don't need
        trace capture or complex interaction.

        Args:
            goal: Goal to execute
            agent_spec: Optional agent specification
            project: Optional project context

        Returns:
            Result dictionary
        """
        # NEW: Pass goal for dynamic agent adaptation
        options = self._build_agent_options(
            agent_spec=agent_spec,
            project=project,
            goal=goal  # Enable dynamic agent adaptation!
        )

        result = {
            "success": False,
            "output": "",
            "cost": 0.0
        }

        output_parts = []

        try:
            async for message in sdk_query(prompt=goal, options=options):
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            output_parts.append(block.text)

                if isinstance(message, ResultMessage):
                    result["cost"] = message.total_cost_usd
                    result["success"] = True

            result["output"] = "\n".join(output_parts)

        except Exception as e:
            result["error"] = str(e)

        return result

    async def execute_with_streaming(
        self,
        goal: str,
        on_message_callback,
        agent_spec: Optional[AgentSpec] = None,
        project: Optional[Project] = None
    ) -> Dict[str, Any]:
        """
        Execute with streaming callback for real-time updates

        Args:
            goal: Goal to execute
            on_message_callback: Async callback called for each message
            agent_spec: Optional agent specification
            project: Optional project context

        Returns:
            Result dictionary
        """
        # NEW: Pass goal for dynamic agent adaptation
        options = self._build_agent_options(
            agent_spec=agent_spec,
            project=project,
            goal=goal  # Enable dynamic agent adaptation!
        )

        result = {
            "success": False,
            "cost": 0.0
        }

        try:
            async with ClaudeSDKClient(options=options) as client:
                await client.connect(prompt=goal)

                async for message in client.receive_response():
                    # Call user callback
                    await on_message_callback(message)

                    if isinstance(message, ResultMessage):
                        result["cost"] = message.total_cost_usd
                        result["success"] = True

        except Exception as e:
            result["error"] = str(e)

        return result


def is_sdk_available() -> bool:
    """Check if Claude Agent SDK is available"""
    return SDK_AVAILABLE


def get_sdk_version() -> Optional[str]:
    """Get installed SDK version"""
    if not SDK_AVAILABLE:
        return None

    try:
        import claude_agent_sdk
        return getattr(claude_agent_sdk, '__version__', 'unknown')
    except:
        return None
