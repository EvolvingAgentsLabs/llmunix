"""
Mode Selection Strategies for Dispatcher

Implements the Strategy pattern for execution mode determination.
Enables A/B testing and experimentation with different mode selection algorithms.
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple
from dataclasses import dataclass


# Import types (will be resolved at runtime)
from memory.traces_sdk import ExecutionTrace, TraceManager


@dataclass
class ModeContext:
    """Context information for mode selection"""
    goal: str
    trace_manager: TraceManager
    config: any  # DispatcherConfig

    # Optional hints
    force_mode: Optional[str] = None
    prefer_cost_optimization: bool = False
    prefer_speed_optimization: bool = False


@dataclass
class ModeDecision:
    """Result of mode selection"""
    mode: str  # "CRYSTALLIZED", "FOLLOWER", "MIXED", "LEARNER", "ORCHESTRATOR"
    confidence: float  # 0.0 to 1.0
    trace: Optional[ExecutionTrace] = None
    reasoning: str = ""  # Why this mode was selected


class ModeSelectionStrategy(ABC):
    """
    Abstract strategy for execution mode selection

    Different strategies can implement different algorithms for
    choosing between CRYSTALLIZED, FOLLOWER, MIXED, LEARNER, and ORCHESTRATOR modes.
    """

    @abstractmethod
    async def determine_mode(self, context: ModeContext) -> ModeDecision:
        """
        Determine the execution mode for a given goal

        Args:
            context: ModeContext with goal and dependencies

        Returns:
            ModeDecision with mode, confidence, and optional trace
        """
        pass

    async def _find_trace(self, context: ModeContext) -> Tuple[Optional[ExecutionTrace], float]:
        """Helper: Find matching trace with confidence"""
        result = await context.trace_manager.find_trace_with_llm(
            context.goal,
            min_confidence=context.config.memory.mixed_mode_threshold
        )

        if result:
            return result  # (trace, confidence)
        return (None, 0.0)

    def _analyze_complexity(self, goal: str, threshold: int) -> Tuple[int, bool]:
        """
        Helper: Analyze goal complexity

        Returns: (complexity_score, is_complex)
        """
        complexity_indicators = [
            "and",  # Multiple tasks
            "then",  # Sequential steps
            "create a project",  # Project management
            "analyze and",  # Multi-step analysis
            "research",  # Complex investigation
            "multiple",  # Multiple items
            "coordinate",  # Coordination needed
            "delegate",  # Delegation needed
        ]

        goal_lower = goal.lower()
        score = sum(1 for indicator in complexity_indicators if indicator in goal_lower)
        return (score, score >= threshold)


class AutoModeStrategy(ModeSelectionStrategy):
    """
    Automatic mode selection (default llmos behavior)

    Algorithm:
    1. Check for crystallized tool (highest priority)
    2. Check trace confidence for FOLLOWER/MIXED
    3. Analyze complexity for ORCHESTRATOR
    4. Default to LEARNER for novel tasks
    """

    async def determine_mode(self, context: ModeContext) -> ModeDecision:
        """Determine mode using automatic selection"""

        # Forced mode override
        if context.force_mode:
            return ModeDecision(
                mode=context.force_mode,
                confidence=1.0,
                reasoning=f"Forced mode: {context.force_mode}"
            )

        # Try to find matching trace
        trace, confidence = await self._find_trace(context)

        if trace and confidence >= context.config.memory.mixed_mode_threshold:
            return self._select_from_trace(trace, confidence, context)

        # Analyze complexity for orchestrator mode
        complexity_score, is_complex = self._analyze_complexity(
            context.goal,
            context.config.dispatcher.complexity_threshold
        )

        if is_complex:
            return ModeDecision(
                mode="ORCHESTRATOR",
                confidence=0.7,  # Medium confidence for complexity-based decision
                reasoning=f"Complex task detected (score: {complexity_score})"
            )

        # Default to learner for novel tasks
        return ModeDecision(
            mode="LEARNER",
            confidence=0.5,  # Low confidence - novel task
            reasoning="Novel task - no trace found, not complex enough for orchestrator"
        )

    def _select_from_trace(
        self,
        trace: ExecutionTrace,
        confidence: float,
        context: ModeContext
    ) -> ModeDecision:
        """Select mode based on trace and confidence"""

        # Crystallized tool - instant execution
        if trace.crystallized_into_tool:
            return ModeDecision(
                mode="CRYSTALLIZED",
                confidence=1.0,
                trace=trace,
                reasoning=f"Crystallized tool available: {trace.crystallized_into_tool}"
            )

        # High confidence - follower mode
        if confidence >= context.config.memory.follower_mode_threshold:
            return ModeDecision(
                mode="FOLLOWER",
                confidence=confidence,
                trace=trace,
                reasoning=f"High-confidence trace match ({confidence:.0%})"
            )

        # Medium confidence - mixed mode (trace as guidance)
        return ModeDecision(
            mode="MIXED",
            confidence=confidence,
            trace=trace,
            reasoning=f"Medium-confidence trace match ({confidence:.0%}) - use as guidance"
        )


class CostOptimizedStrategy(ModeSelectionStrategy):
    """
    Cost-optimized mode selection

    Prioritizes cheaper modes with lower confidence thresholds.
    Useful for budget-constrained environments.

    Algorithm:
    1. Aggressively prefer CRYSTALLIZED/FOLLOWER (lower thresholds)
    2. Use MIXED mode more often
    3. Avoid ORCHESTRATOR unless absolutely necessary
    4. Use LEARNER only as last resort
    """

    async def determine_mode(self, context: ModeContext) -> ModeDecision:
        """Determine mode with cost optimization"""

        # Forced mode override
        if context.force_mode:
            return ModeDecision(
                mode=context.force_mode,
                confidence=1.0,
                reasoning=f"Forced mode: {context.force_mode}"
            )

        # Try to find trace with lower threshold (more aggressive)
        trace, confidence = await self._find_trace(context)

        if trace and confidence >= 0.5:  # Lower threshold than auto (0.75)
            return self._select_cost_optimized(trace, confidence, context)

        # Avoid ORCHESTRATOR - it's expensive
        # Go straight to LEARNER even for complex tasks
        complexity_score, is_complex = self._analyze_complexity(
            context.goal,
            context.config.dispatcher.complexity_threshold + 2  # Stricter
        )

        if is_complex:
            return ModeDecision(
                mode="ORCHESTRATOR",
                confidence=0.6,
                reasoning=f"Very complex task (score: {complexity_score}) - orchestrator required"
            )

        return ModeDecision(
            mode="LEARNER",
            confidence=0.5,
            reasoning="Cost-optimized: prefer single LLM call over orchestration"
        )

    def _select_cost_optimized(
        self,
        trace: ExecutionTrace,
        confidence: float,
        context: ModeContext
    ) -> ModeDecision:
        """Select mode with cost optimization"""

        if trace.crystallized_into_tool:
            return ModeDecision(
                mode="CRYSTALLIZED",
                confidence=1.0,
                trace=trace,
                reasoning="Cost-optimized: Free execution via crystallized tool"
            )

        # Lower threshold for FOLLOWER (0.75 instead of 0.92)
        if confidence >= 0.75:
            return ModeDecision(
                mode="FOLLOWER",
                confidence=confidence,
                trace=trace,
                reasoning=f"Cost-optimized: Acceptable trace ({confidence:.0%}) - free replay"
            )

        # Use MIXED more aggressively (0.5 instead of 0.75)
        if confidence >= 0.5:
            return ModeDecision(
                mode="MIXED",
                confidence=confidence,
                trace=trace,
                reasoning=f"Cost-optimized: Lower confidence ({confidence:.0%}) but cheaper than LEARNER"
            )

        # Should not reach here given the guard in determine_mode
        return ModeDecision(
            mode="LEARNER",
            confidence=confidence,
            reasoning="Cost-optimized: No suitable trace"
        )


class SpeedOptimizedStrategy(ModeSelectionStrategy):
    """
    Speed-optimized mode selection

    Prioritizes faster modes, tolerates slightly lower confidence.
    Useful for latency-sensitive applications.

    Algorithm:
    1. Strongly prefer CRYSTALLIZED (instant)
    2. Prefer FOLLOWER over MIXED (faster)
    3. Avoid ORCHESTRATOR (slow multi-agent coordination)
    4. Accept lower confidence for speed gains
    """

    async def determine_mode(self, context: ModeContext) -> ModeDecision:
        """Determine mode with speed optimization"""

        # Forced mode override
        if context.force_mode:
            return ModeDecision(
                mode=context.force_mode,
                confidence=1.0,
                reasoning=f"Forced mode: {context.force_mode}"
            )

        # Find trace with lower threshold
        trace, confidence = await self._find_trace(context)

        if trace and confidence >= 0.6:  # Lower than auto, higher than cost-optimized
            return self._select_speed_optimized(trace, confidence, context)

        # Avoid ORCHESTRATOR - too slow
        # Prefer LEARNER (single fast LLM call) over multi-agent coordination
        complexity_score, is_complex = self._analyze_complexity(
            context.goal,
            context.config.dispatcher.complexity_threshold + 3  # Very strict
        )

        if is_complex:
            return ModeDecision(
                mode="ORCHESTRATOR",
                confidence=0.5,
                reasoning=f"Extremely complex task (score: {complexity_score}) - must use orchestrator"
            )

        return ModeDecision(
            mode="LEARNER",
            confidence=0.6,
            reasoning="Speed-optimized: Fast single LLM call"
        )

    def _select_speed_optimized(
        self,
        trace: ExecutionTrace,
        confidence: float,
        context: ModeContext
    ) -> ModeDecision:
        """Select mode with speed optimization"""

        if trace.crystallized_into_tool:
            return ModeDecision(
                mode="CRYSTALLIZED",
                confidence=1.0,
                trace=trace,
                reasoning="Speed-optimized: Instant execution (<1s)"
            )

        # Lower threshold for FOLLOWER (0.7 instead of 0.92)
        if confidence >= 0.7:
            return ModeDecision(
                mode="FOLLOWER",
                confidence=confidence,
                trace=trace,
                reasoning=f"Speed-optimized: Fast replay ({confidence:.0%}) ~2-3s"
            )

        # Prefer FOLLOWER over MIXED even with slightly lower confidence
        # MIXED requires LLM call which is slower
        if confidence >= 0.6:
            return ModeDecision(
                mode="FOLLOWER",
                confidence=confidence,
                trace=trace,
                reasoning=f"Speed-optimized: Accept lower confidence ({confidence:.0%}) for speed"
            )

        return ModeDecision(
            mode="LEARNER",
            confidence=confidence,
            reasoning="Speed-optimized: No fast trace available"
        )


class ForcedLearnerStrategy(ModeSelectionStrategy):
    """
    Always use LEARNER mode

    Useful for:
    - Testing new implementations
    - Forcing fresh reasoning
    - Bypassing cached traces
    - Development/debugging
    """

    async def determine_mode(self, context: ModeContext) -> ModeDecision:
        """Always return LEARNER mode"""
        return ModeDecision(
            mode="LEARNER",
            confidence=1.0,
            reasoning="Forced LEARNER mode - always use fresh LLM reasoning"
        )


class ForcedFollowerStrategy(ModeSelectionStrategy):
    """
    Prefer FOLLOWER mode whenever possible

    Falls back to LEARNER only if no trace exists.
    Useful for testing trace replay system.
    """

    async def determine_mode(self, context: ModeContext) -> ModeDecision:
        """Prefer FOLLOWER mode"""

        # Find any trace, even with low confidence
        trace, confidence = await self._find_trace(context)

        if trace:
            return ModeDecision(
                mode="FOLLOWER",
                confidence=confidence,
                trace=trace,
                reasoning=f"Forced FOLLOWER mode with {confidence:.0%} confidence"
            )

        return ModeDecision(
            mode="LEARNER",
            confidence=0.0,
            reasoning="Forced FOLLOWER mode but no trace found - using LEARNER"
        )


class SentienceAwareStrategy(ModeSelectionStrategy):
    """
    Sentience-aware mode selection

    This strategy uses the CognitiveKernel to modulate mode decisions
    based on internal state (valence, latent mode, etc.).

    Key behaviors:
    - Recovery mode: Prefer cheap modes (FOLLOWER, CRYSTALLIZED)
    - Cautious mode: Stricter safety, prefer proven traces
    - Auto-creative mode: Allow more LEARNER for exploration
    - Auto-contained mode: Conservative, task-focused

    Requires a CognitiveKernel instance to be set via set_cognitive_kernel().
    """

    def __init__(self):
        self.cognitive_kernel = None
        self._base_strategy = AutoModeStrategy()

    def set_cognitive_kernel(self, kernel):
        """Set the cognitive kernel for state-aware decisions"""
        self.cognitive_kernel = kernel

    async def determine_mode(self, context: ModeContext) -> ModeDecision:
        """Determine mode with sentience awareness"""

        # First, get base decision from AutoModeStrategy
        base_decision = await self._base_strategy.determine_mode(context)

        # If no cognitive kernel, just return base decision
        if not self.cognitive_kernel:
            return base_decision

        # Modulate decision based on cognitive state
        return self.cognitive_kernel.modulate_mode_decision(base_decision, context.goal)


# Strategy registry for easy access
STRATEGIES = {
    "auto": AutoModeStrategy,
    "cost-optimized": CostOptimizedStrategy,
    "speed-optimized": SpeedOptimizedStrategy,
    "forced-learner": ForcedLearnerStrategy,
    "forced-follower": ForcedFollowerStrategy,
    "sentience-aware": SentienceAwareStrategy,
}


def get_strategy(name: str = "auto") -> ModeSelectionStrategy:
    """
    Get a mode selection strategy by name

    Args:
        name: Strategy name ("auto", "cost-optimized", "speed-optimized", etc.)

    Returns:
        ModeSelectionStrategy instance

    Raises:
        ValueError: If strategy name is unknown
    """
    if name not in STRATEGIES:
        available = ", ".join(STRATEGIES.keys())
        raise ValueError(f"Unknown strategy '{name}'. Available: {available}")

    return STRATEGIES[name]()
