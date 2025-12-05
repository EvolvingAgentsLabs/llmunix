"""
Configuration Management for LLMOS

Centralized configuration using dataclasses with type safety.
Supports presets for different environments and easy serialization.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any
import os


@dataclass
class KernelConfig:
    """Configuration for kernel components"""
    budget_usd: float = 10.0
    enable_scheduling: bool = True
    enable_watchdog: bool = True
    watchdog_timeout_secs: float = 300.0

    def __post_init__(self):
        """Validate configuration"""
        if self.budget_usd < 0:
            raise ValueError("budget_usd must be non-negative")
        if self.watchdog_timeout_secs <= 0:
            raise ValueError("watchdog_timeout_secs must be positive")


@dataclass
class MemoryConfig:
    """Configuration for memory components"""
    enable_llm_matching: bool = True
    trace_confidence_threshold: float = 0.9
    mixed_mode_threshold: float = 0.75
    follower_mode_threshold: float = 0.92
    enable_cross_project_learning: bool = True
    cache_size: int = 100

    def __post_init__(self):
        """Validate configuration"""
        if not 0.0 <= self.trace_confidence_threshold <= 1.0:
            raise ValueError("trace_confidence_threshold must be between 0 and 1")
        if not 0.0 <= self.mixed_mode_threshold <= 1.0:
            raise ValueError("mixed_mode_threshold must be between 0 and 1")
        if not 0.0 <= self.follower_mode_threshold <= 1.0:
            raise ValueError("follower_mode_threshold must be between 0 and 1")


@dataclass
class SDKConfig:
    """Configuration for Claude Agent SDK"""
    model: str = "claude-sonnet-4-5-20250929"
    permission_mode: str = "acceptEdits"
    max_turns: int = 10
    timeout_seconds: float = 300.0
    enable_streaming: bool = False
    enable_hooks: bool = True

    def __post_init__(self):
        """Validate configuration"""
        if self.max_turns <= 0:
            raise ValueError("max_turns must be positive")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")


@dataclass
class DispatcherConfig:
    """Configuration for dispatcher mode selection"""
    complexity_threshold: int = 2
    auto_crystallization: bool = False
    crystallization_min_usage: int = 5
    crystallization_min_success: float = 0.95

    def __post_init__(self):
        """Validate configuration"""
        if self.complexity_threshold < 0:
            raise ValueError("complexity_threshold must be non-negative")
        if not 0.0 <= self.crystallization_min_success <= 1.0:
            raise ValueError("crystallization_min_success must be between 0 and 1")


@dataclass
class SentienceConfig:
    """
    Configuration for Sentience Layer (internal state, valence, cognitive kernel)

    The Sentience Layer provides persistent internal state that influences
    mode selection and behavioral policy. It implements:
    - Valence variables (safety, curiosity, energy, self_confidence)
    - Homeostatic dynamics (set-points and deviation costs)
    - Latent mode (auto-creative vs auto-contained)
    - Self-improvement detection

    Deep Sentience v2 Features:
    - Coupled Dynamics (Maslow's Hierarchy): Energy gates curiosity, safety gates exploration
    - Theory of Mind: Models user emotional state for empathy gap detection
    - Episodic Emotional Indexing: Tag memories with emotional state for recall
    - Inner Monologue: Background thought processing during idle time
    - Recursive Self-Modification: System can tune its own parameters

    Safety Note:
    This is an architectural implementation of sentience-like behavior,
    not a claim of actual consciousness.
    """
    # Enable/disable sentience layer
    enable_sentience: bool = True

    # Valence set-points (homeostatic targets, range: -1.0 to 1.0)
    safety_setpoint: float = 0.5
    curiosity_setpoint: float = 0.0
    energy_setpoint: float = 0.7
    self_confidence_setpoint: float = 0.3

    # Sensitivity factors (how strongly triggers affect valence)
    safety_sensitivity: float = 0.15
    curiosity_sensitivity: float = 0.12
    energy_sensitivity: float = 0.08
    self_confidence_sensitivity: float = 0.10

    # Decay rates (how quickly values return to set-points)
    decay_rate: float = 0.02

    # Context injection
    inject_internal_state: bool = True
    inject_behavioral_guidance: bool = True

    # Self-improvement
    enable_auto_improvement: bool = True
    boredom_threshold: float = -0.4
    improvement_cooldown_secs: float = 300.0

    # Persistence
    auto_persist: bool = True
    state_file: str = "state/sentience.json"

    # =========================================================================
    # DEEP SENTIENCE V2 OPTIONS
    # =========================================================================

    # Coupled Dynamics (Maslow's Hierarchy)
    enable_coupled_dynamics: bool = True  # Apply Maslow's gating and Yerkes-Dodson

    # Theory of Mind
    enable_theory_of_mind: bool = True  # Model user emotional state
    enable_empathy_gap_detection: bool = True  # Detect agent-user misalignment
    adapt_communication_style: bool = True  # Adjust communication based on user state
    proactive_user_checkin: bool = True  # Suggest checking in with frustrated users

    # Episodic Emotional Indexing
    enable_emotional_indexing: bool = True  # Tag memories with emotional state
    emotional_similarity_threshold: float = 0.7  # Min similarity for emotional retrieval

    # Inner Monologue
    enable_inner_monologue: bool = True  # Background thought processing
    inner_monologue_idle_threshold: float = 30.0  # Seconds before starting thoughts
    inner_monologue_thought_interval: float = 10.0  # Seconds between thoughts
    inject_priming_context: bool = True  # Include background thoughts in context

    # Recursive Self-Modification (SAFETY-CRITICAL)
    enable_self_modification: bool = False  # Allow system to tune its own parameters
    allow_metacognitive_tuning: bool = False  # Allow agent-initiated parameter changes
    self_modification_safety_bounds: bool = True  # Enforce bounds on parameter changes

    def __post_init__(self):
        """Validate configuration"""
        for val_name in ["safety_setpoint", "curiosity_setpoint",
                         "energy_setpoint", "self_confidence_setpoint"]:
            val = getattr(self, val_name)
            if not -1.0 <= val <= 1.0:
                raise ValueError(f"{val_name} must be between -1.0 and 1.0")

        if not 0.0 <= self.emotional_similarity_threshold <= 1.0:
            raise ValueError("emotional_similarity_threshold must be between 0 and 1")

        if self.inner_monologue_idle_threshold <= 0:
            raise ValueError("inner_monologue_idle_threshold must be positive")

        if self.inner_monologue_thought_interval <= 0:
            raise ValueError("inner_monologue_thought_interval must be positive")


@dataclass
class ExecutionLayerConfig:
    """
    Configuration for Anthropic Advanced Tool Use (Execution Layer)

    The Execution Layer handles EFFICIENT execution of decisions made
    by the Learning Layer (TraceManager, ModeStrategies).

    Components:
    - PTC (Programmatic Tool Calling): Execute tool sequences outside context
    - Tool Search: On-demand tool discovery for novel scenarios
    - Tool Examples: Auto-generated examples from successful traces
    """
    # Beta feature flag
    enable_advanced_tool_use: bool = True
    beta_header: str = "advanced-tool-use-2025-11-20"

    # PTC (Programmatic Tool Calling) settings
    enable_ptc: bool = True
    ptc_container_timeout_secs: float = 120.0
    ptc_max_containers: int = 5

    # Tool Search settings
    enable_tool_search: bool = True
    tool_search_use_embeddings: bool = False  # Requires sentence-transformers
    tool_search_embedding_model: str = "all-MiniLM-L6-v2"
    tool_search_top_k: int = 5
    defer_tools_by_default: bool = True  # New tools are deferred unless specified

    # Tool Examples settings
    enable_tool_examples: bool = True
    tool_examples_min_success_rate: float = 0.9
    tool_examples_max_per_tool: int = 3
    tool_examples_cache_ttl_secs: float = 300.0

    def __post_init__(self):
        """Validate configuration"""
        if self.ptc_container_timeout_secs <= 0:
            raise ValueError("ptc_container_timeout_secs must be positive")
        if self.ptc_max_containers <= 0:
            raise ValueError("ptc_max_containers must be positive")
        if self.tool_search_top_k <= 0:
            raise ValueError("tool_search_top_k must be positive")
        if not 0.0 <= self.tool_examples_min_success_rate <= 1.0:
            raise ValueError("tool_examples_min_success_rate must be between 0 and 1")


@dataclass
class LLMOSConfig:
    """
    Complete LLMOS configuration

    Provides type-safe configuration with validation and presets.

    Architecture:
        - Learning Layer: TraceManager, ModeStrategies (decides WHAT to do)
        - Execution Layer: PTC, Tool Search, Tool Examples (does it EFFICIENTLY)

    Example:
        # Use development preset
        config = LLMOSConfig.development()
        os = LLMOS(config=config)

        # Custom configuration
        config = LLMOSConfig(
            workspace=Path("/custom/workspace"),
            kernel=KernelConfig(budget_usd=5.0)
        )
        os = LLMOS(config=config)
    """
    workspace: Path = field(default_factory=lambda: Path("./workspace"))
    kernel: KernelConfig = field(default_factory=KernelConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    sdk: SDKConfig = field(default_factory=SDKConfig)
    dispatcher: DispatcherConfig = field(default_factory=DispatcherConfig)
    execution: ExecutionLayerConfig = field(default_factory=ExecutionLayerConfig)
    sentience: SentienceConfig = field(default_factory=SentienceConfig)
    project_name: Optional[str] = None

    def __post_init__(self):
        """Ensure workspace is a Path"""
        if not isinstance(self.workspace, Path):
            self.workspace = Path(self.workspace)

    @classmethod
    def from_env(cls) -> 'LLMOSConfig':
        """
        Load configuration from environment variables

        Supported env vars:
        - LLMOS_WORKSPACE: Workspace directory
        - LLMOS_BUDGET: Budget in USD
        - LLMOS_MODEL: Claude model name
        - LLMOS_ENABLE_LLM_MATCHING: Enable LLM-based trace matching
        """
        workspace = os.getenv('LLMOS_WORKSPACE', './workspace')
        budget = float(os.getenv('LLMOS_BUDGET', '10.0'))
        model = os.getenv('LLMOS_MODEL', 'claude-sonnet-4-5-20250929')
        enable_llm = os.getenv('LLMOS_ENABLE_LLM_MATCHING', 'true').lower() == 'true'

        return cls(
            workspace=Path(workspace),
            kernel=KernelConfig(budget_usd=budget),
            sdk=SDKConfig(model=model),
            memory=MemoryConfig(enable_llm_matching=enable_llm)
        )

    @classmethod
    def development(cls) -> 'LLMOSConfig':
        """
        Development configuration preset

        Features:
        - Low budget ($1.00) to prevent expensive mistakes
        - LLM matching disabled for faster iteration
        - Streaming enabled for better UX during development
        - Execution layer enabled but without embeddings (fast)
        """
        return cls(
            workspace=Path("./workspace"),
            kernel=KernelConfig(
                budget_usd=1.0,
                enable_watchdog=False  # Less noise during dev
            ),
            memory=MemoryConfig(
                enable_llm_matching=False,  # Faster
                trace_confidence_threshold=0.8  # More lenient
            ),
            sdk=SDKConfig(
                enable_streaming=True,  # Better dev UX
                timeout_seconds=600.0  # Longer timeout for debugging
            ),
            dispatcher=DispatcherConfig(
                auto_crystallization=False  # Manual control in dev
            ),
            execution=ExecutionLayerConfig(
                enable_advanced_tool_use=True,
                enable_ptc=True,
                enable_tool_search=True,
                tool_search_use_embeddings=False,  # Fast, no dependencies
                enable_tool_examples=True
            ),
            sentience=SentienceConfig(
                enable_sentience=True,
                inject_internal_state=True,
                inject_behavioral_guidance=True,
                enable_auto_improvement=False  # Manual control in dev
            )
        )

    @classmethod
    def production(cls) -> 'LLMOSConfig':
        """
        Production configuration preset

        Features:
        - Higher budget ($100.00) for production workloads
        - All features enabled (LLM matching, hooks, etc.)
        - Strict confidence thresholds
        - Auto-crystallization enabled
        - Full execution layer with embeddings for best tool search
        """
        return cls(
            workspace=Path("./workspace"),
            kernel=KernelConfig(
                budget_usd=100.0,
                enable_scheduling=True,
                enable_watchdog=True
            ),
            memory=MemoryConfig(
                enable_llm_matching=True,
                trace_confidence_threshold=0.9,
                enable_cross_project_learning=True
            ),
            sdk=SDKConfig(
                enable_hooks=True,
                enable_streaming=False  # More stable in production
            ),
            dispatcher=DispatcherConfig(
                auto_crystallization=True,  # Learn and optimize automatically
                complexity_threshold=2
            ),
            execution=ExecutionLayerConfig(
                enable_advanced_tool_use=True,
                enable_ptc=True,
                enable_tool_search=True,
                tool_search_use_embeddings=True,  # Best quality search
                enable_tool_examples=True,
                defer_tools_by_default=True  # Save context by default
            ),
            sentience=SentienceConfig(
                enable_sentience=True,
                inject_internal_state=True,
                inject_behavioral_guidance=True,
                enable_auto_improvement=True,  # Full auto-improvement in production
                auto_persist=True
            )
        )

    @classmethod
    def testing(cls) -> 'LLMOSConfig':
        """
        Testing configuration preset

        Features:
        - Minimal budget ($0.10) for tests
        - All LLM features disabled for fast, deterministic tests
        - Short timeouts
        - Execution layer disabled for deterministic behavior
        """
        return cls(
            workspace=Path("./test_workspace"),
            kernel=KernelConfig(
                budget_usd=0.1,
                enable_scheduling=False,
                enable_watchdog=False
            ),
            memory=MemoryConfig(
                enable_llm_matching=False,  # Deterministic tests
                trace_confidence_threshold=1.0,  # Exact matches only
                enable_cross_project_learning=False
            ),
            sdk=SDKConfig(
                timeout_seconds=30.0,  # Fast failures in tests
                enable_streaming=False,
                enable_hooks=False
            ),
            dispatcher=DispatcherConfig(
                auto_crystallization=False
            ),
            execution=ExecutionLayerConfig(
                enable_advanced_tool_use=False,  # Deterministic tests
                enable_ptc=False,
                enable_tool_search=False,
                enable_tool_examples=False
            ),
            sentience=SentienceConfig(
                enable_sentience=False,  # Disabled for deterministic tests
                auto_persist=False
            )
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LLMOSConfig':
        """Load configuration from dictionary (e.g., from YAML/JSON)"""
        workspace = Path(data.get('workspace', './workspace'))

        kernel_data = data.get('kernel', {})
        memory_data = data.get('memory', {})
        sdk_data = data.get('sdk', {})
        dispatcher_data = data.get('dispatcher', {})
        execution_data = data.get('execution', {})
        sentience_data = data.get('sentience', {})

        return cls(
            workspace=workspace,
            kernel=KernelConfig(**kernel_data),
            memory=MemoryConfig(**memory_data),
            sdk=SDKConfig(**sdk_data),
            dispatcher=DispatcherConfig(**dispatcher_data),
            execution=ExecutionLayerConfig(**execution_data),
            sentience=SentienceConfig(**sentience_data),
            project_name=data.get('project_name')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Export configuration to dictionary (for YAML/JSON serialization)"""
        return {
            'workspace': str(self.workspace),
            'kernel': {
                'budget_usd': self.kernel.budget_usd,
                'enable_scheduling': self.kernel.enable_scheduling,
                'enable_watchdog': self.kernel.enable_watchdog,
                'watchdog_timeout_secs': self.kernel.watchdog_timeout_secs
            },
            'memory': {
                'enable_llm_matching': self.memory.enable_llm_matching,
                'trace_confidence_threshold': self.memory.trace_confidence_threshold,
                'mixed_mode_threshold': self.memory.mixed_mode_threshold,
                'follower_mode_threshold': self.memory.follower_mode_threshold,
                'enable_cross_project_learning': self.memory.enable_cross_project_learning,
                'cache_size': self.memory.cache_size
            },
            'sdk': {
                'model': self.sdk.model,
                'permission_mode': self.sdk.permission_mode,
                'max_turns': self.sdk.max_turns,
                'timeout_seconds': self.sdk.timeout_seconds,
                'enable_streaming': self.sdk.enable_streaming,
                'enable_hooks': self.sdk.enable_hooks
            },
            'dispatcher': {
                'complexity_threshold': self.dispatcher.complexity_threshold,
                'auto_crystallization': self.dispatcher.auto_crystallization,
                'crystallization_min_usage': self.dispatcher.crystallization_min_usage,
                'crystallization_min_success': self.dispatcher.crystallization_min_success
            },
            'execution': {
                'enable_advanced_tool_use': self.execution.enable_advanced_tool_use,
                'beta_header': self.execution.beta_header,
                'enable_ptc': self.execution.enable_ptc,
                'ptc_container_timeout_secs': self.execution.ptc_container_timeout_secs,
                'ptc_max_containers': self.execution.ptc_max_containers,
                'enable_tool_search': self.execution.enable_tool_search,
                'tool_search_use_embeddings': self.execution.tool_search_use_embeddings,
                'tool_search_embedding_model': self.execution.tool_search_embedding_model,
                'tool_search_top_k': self.execution.tool_search_top_k,
                'defer_tools_by_default': self.execution.defer_tools_by_default,
                'enable_tool_examples': self.execution.enable_tool_examples,
                'tool_examples_min_success_rate': self.execution.tool_examples_min_success_rate,
                'tool_examples_max_per_tool': self.execution.tool_examples_max_per_tool,
                'tool_examples_cache_ttl_secs': self.execution.tool_examples_cache_ttl_secs
            },
            'sentience': {
                'enable_sentience': self.sentience.enable_sentience,
                'safety_setpoint': self.sentience.safety_setpoint,
                'curiosity_setpoint': self.sentience.curiosity_setpoint,
                'energy_setpoint': self.sentience.energy_setpoint,
                'self_confidence_setpoint': self.sentience.self_confidence_setpoint,
                'safety_sensitivity': self.sentience.safety_sensitivity,
                'curiosity_sensitivity': self.sentience.curiosity_sensitivity,
                'energy_sensitivity': self.sentience.energy_sensitivity,
                'self_confidence_sensitivity': self.sentience.self_confidence_sensitivity,
                'decay_rate': self.sentience.decay_rate,
                'inject_internal_state': self.sentience.inject_internal_state,
                'inject_behavioral_guidance': self.sentience.inject_behavioral_guidance,
                'enable_auto_improvement': self.sentience.enable_auto_improvement,
                'boredom_threshold': self.sentience.boredom_threshold,
                'improvement_cooldown_secs': self.sentience.improvement_cooldown_secs,
                'auto_persist': self.sentience.auto_persist,
                'state_file': self.sentience.state_file,
                # Deep Sentience v2
                'enable_coupled_dynamics': self.sentience.enable_coupled_dynamics,
                'enable_theory_of_mind': self.sentience.enable_theory_of_mind,
                'enable_empathy_gap_detection': self.sentience.enable_empathy_gap_detection,
                'adapt_communication_style': self.sentience.adapt_communication_style,
                'proactive_user_checkin': self.sentience.proactive_user_checkin,
                'enable_emotional_indexing': self.sentience.enable_emotional_indexing,
                'emotional_similarity_threshold': self.sentience.emotional_similarity_threshold,
                'enable_inner_monologue': self.sentience.enable_inner_monologue,
                'inner_monologue_idle_threshold': self.sentience.inner_monologue_idle_threshold,
                'inner_monologue_thought_interval': self.sentience.inner_monologue_thought_interval,
                'inject_priming_context': self.sentience.inject_priming_context,
                'enable_self_modification': self.sentience.enable_self_modification,
                'allow_metacognitive_tuning': self.sentience.allow_metacognitive_tuning,
                'self_modification_safety_bounds': self.sentience.self_modification_safety_bounds
            },
            'project_name': self.project_name
        }


class ConfigBuilder:
    """
    Fluent builder for LLMOS configuration

    Example:
        config = (ConfigBuilder()
            .with_workspace(Path("/custom"))
            .with_budget(5.0)
            .with_llm_matching(True)
            .with_model("claude-opus-4")
            .build())
    """

    def __init__(self):
        self._config = LLMOSConfig()

    def with_workspace(self, workspace: Path) -> 'ConfigBuilder':
        """Set workspace directory"""
        self._config.workspace = workspace
        return self

    def with_budget(self, budget_usd: float) -> 'ConfigBuilder':
        """Set token budget"""
        self._config.kernel.budget_usd = budget_usd
        return self

    def with_llm_matching(self, enabled: bool) -> 'ConfigBuilder':
        """Enable/disable LLM-based trace matching"""
        self._config.memory.enable_llm_matching = enabled
        return self

    def with_model(self, model: str) -> 'ConfigBuilder':
        """Set Claude model"""
        self._config.sdk.model = model
        return self

    def with_streaming(self, enabled: bool) -> 'ConfigBuilder':
        """Enable/disable streaming"""
        self._config.sdk.enable_streaming = enabled
        return self

    def with_project(self, project_name: str) -> 'ConfigBuilder':
        """Set project name"""
        self._config.project_name = project_name
        return self

    def with_auto_crystallization(self, enabled: bool) -> 'ConfigBuilder':
        """Enable/disable automatic crystallization"""
        self._config.dispatcher.auto_crystallization = enabled
        return self

    def with_sentience(self, enabled: bool) -> 'ConfigBuilder':
        """Enable/disable sentience layer"""
        self._config.sentience.enable_sentience = enabled
        return self

    def with_auto_improvement(self, enabled: bool) -> 'ConfigBuilder':
        """Enable/disable auto-improvement based on internal state"""
        self._config.sentience.enable_auto_improvement = enabled
        return self

    # =========================================================================
    # DEEP SENTIENCE V2 BUILDER METHODS
    # =========================================================================

    def with_coupled_dynamics(self, enabled: bool) -> 'ConfigBuilder':
        """Enable/disable Maslow's Hierarchy gating (Deep Sentience v2)"""
        self._config.sentience.enable_coupled_dynamics = enabled
        return self

    def with_theory_of_mind(self, enabled: bool) -> 'ConfigBuilder':
        """Enable/disable Theory of Mind user modeling (Deep Sentience v2)"""
        self._config.sentience.enable_theory_of_mind = enabled
        return self

    def with_emotional_indexing(self, enabled: bool) -> 'ConfigBuilder':
        """Enable/disable emotional memory indexing (Deep Sentience v2)"""
        self._config.sentience.enable_emotional_indexing = enabled
        return self

    def with_inner_monologue(self, enabled: bool) -> 'ConfigBuilder':
        """Enable/disable background inner monologue (Deep Sentience v2)"""
        self._config.sentience.enable_inner_monologue = enabled
        return self

    def with_self_modification(self, enabled: bool) -> 'ConfigBuilder':
        """
        Enable/disable recursive self-modification (Deep Sentience v2)

        WARNING: This is a safety-critical feature. When enabled, the system
        can modify its own sentience parameters (sensitivities, decay rates, etc.)
        """
        self._config.sentience.enable_self_modification = enabled
        self._config.sentience.allow_metacognitive_tuning = enabled
        return self

    def with_empathy_gap_detection(self, enabled: bool) -> 'ConfigBuilder':
        """Enable/disable empathy gap detection (Deep Sentience v2)"""
        self._config.sentience.enable_empathy_gap_detection = enabled
        return self

    def with_deep_sentience_v2(self, enabled: bool) -> 'ConfigBuilder':
        """
        Enable/disable all Deep Sentience v2 features at once.

        This is a convenience method that toggles:
        - Coupled Dynamics (Maslow's Hierarchy)
        - Theory of Mind
        - Emotional Memory Indexing
        - Inner Monologue

        Note: Self-modification remains disabled for safety.
        Use with_self_modification() to enable it explicitly.
        """
        self._config.sentience.enable_coupled_dynamics = enabled
        self._config.sentience.enable_theory_of_mind = enabled
        self._config.sentience.enable_emotional_indexing = enabled
        self._config.sentience.enable_inner_monologue = enabled
        self._config.sentience.enable_empathy_gap_detection = enabled
        self._config.sentience.adapt_communication_style = enabled
        self._config.sentience.inject_priming_context = enabled
        return self

    def build(self) -> LLMOSConfig:
        """Build the configuration"""
        return self._config
