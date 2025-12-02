"""
Kernel Package - Somatic Layer
High-speed, deterministic, non-blocking execution

Includes:
- Sentience Layer: Internal state, valence, cognitive kernel
- Mode Strategies: Execution mode selection
- Configuration: Type-safe configuration management
"""

from kernel.sentience import (
    SentienceState,
    SentienceManager,
    ValenceVector,
    SelfModel,
    GlobalWorkspace,
    LatentMode,
    TriggerType
)

from kernel.cognitive_kernel import (
    CognitiveKernel,
    CognitivePolicy,
    SelfImprovementType,
    SelfImprovementSuggestion
)

from kernel.config import (
    LLMOSConfig,
    KernelConfig,
    MemoryConfig,
    SDKConfig,
    DispatcherConfig,
    ExecutionLayerConfig,
    SentienceConfig,
    ConfigBuilder
)

from kernel.mode_strategies import (
    ModeSelectionStrategy,
    ModeContext,
    ModeDecision,
    AutoModeStrategy,
    SentienceAwareStrategy,
    get_strategy,
    STRATEGIES
)

__all__ = [
    # Sentience
    "SentienceState",
    "SentienceManager",
    "ValenceVector",
    "SelfModel",
    "GlobalWorkspace",
    "LatentMode",
    "TriggerType",
    # Cognitive Kernel
    "CognitiveKernel",
    "CognitivePolicy",
    "SelfImprovementType",
    "SelfImprovementSuggestion",
    # Config
    "LLMOSConfig",
    "KernelConfig",
    "MemoryConfig",
    "SDKConfig",
    "DispatcherConfig",
    "ExecutionLayerConfig",
    "SentienceConfig",
    "ConfigBuilder",
    # Mode Strategies
    "ModeSelectionStrategy",
    "ModeContext",
    "ModeDecision",
    "AutoModeStrategy",
    "SentienceAwareStrategy",
    "get_strategy",
    "STRATEGIES",
]
