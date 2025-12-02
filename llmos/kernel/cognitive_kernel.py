"""
Cognitive Kernel for LLM OS

The Cognitive Kernel is the emergent layer that sits between the Sentience Layer
and the Execution Layer. It translates internal state into behavioral decisions
and orchestrates the system's overall "cognitive posture."

Key Responsibilities:
1. **Mode Modulation**: Adjust mode selection based on internal state
2. **Behavioral Emergence**: Translate valence into concrete behavioral rules
3. **Self-Improvement Triggers**: Detect when the system should self-improve
4. **Context Enrichment**: Inject appropriate context based on cognitive state

The Cognitive Kernel implements the idea of a "latent state" that determines
whether the system should be more "auto-creative" (exploratory, generative) or
"auto-contained" (conservative, task-focused).

Architecture:
```
                   ┌─────────────────────────────┐
                   │      Cognitive Kernel       │
                   │                             │
   User Goal ─────>│  ┌───────────────────────┐  │
                   │  │    Latent State       │  │
                   │  │   (creative/contained)│  │
                   │  └───────────────────────┘  │
                   │             │               │
                   │             ▼               │
                   │  ┌───────────────────────┐  │
                   │  │  Behavioral Policy    │  │
                   │  │  - Mode adjustments   │  │
                   │  │  - Safety overrides   │  │
                   │  │  - Exploration budget │  │
                   │  └───────────────────────┘  │
                   │             │               │
                   └─────────────┼───────────────┘
                                 │
                                 ▼
                   ┌─────────────────────────────┐
                   │   Dispatcher / Execution    │
                   └─────────────────────────────┘
```
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable, Tuple
from enum import Enum
from pathlib import Path

from kernel.sentience import (
    SentienceManager,
    SentienceState,
    LatentMode,
    TriggerType,
    ValenceVector
)
from kernel.mode_strategies import (
    ModeSelectionStrategy,
    ModeContext,
    ModeDecision
)


# =============================================================================
# COGNITIVE POLICIES
# =============================================================================

@dataclass
class CognitivePolicy:
    """
    Policy rules derived from cognitive state

    These rules translate internal state into concrete behavioral adjustments
    that the system uses when making decisions.
    """

    # Mode selection adjustments
    prefer_cheap_modes: bool = False
    prefer_safe_modes: bool = False
    allow_exploration: bool = True
    allow_self_modification: bool = True

    # Confidence thresholds (adjustments to base thresholds)
    follower_threshold_adjustment: float = 0.0  # -0.1 = more lenient
    mixed_threshold_adjustment: float = 0.0
    complexity_threshold_adjustment: int = 0  # +1 = need more complexity for ORCHESTRATOR

    # Safety overrides
    require_confirmation_for_writes: bool = False
    require_confirmation_for_shell: bool = False
    block_destructive_operations: bool = False
    dry_run_preferred: bool = False

    # Exploration budget
    exploration_budget_multiplier: float = 1.0  # 0.5 = half exploration
    max_simultaneous_experiments: int = 1

    # Self-improvement triggers
    enable_auto_improvement: bool = True
    boredom_threshold: float = -0.4  # Curiosity below this triggers improvement
    improvement_cooldown_secs: float = 300.0  # Min time between improvements

    # Context enrichment
    inject_internal_state: bool = True
    inject_behavioral_guidance: bool = True
    inject_similar_experiences: bool = True

    def as_dict(self) -> Dict[str, Any]:
        """Export as dictionary"""
        return {
            "prefer_cheap_modes": self.prefer_cheap_modes,
            "prefer_safe_modes": self.prefer_safe_modes,
            "allow_exploration": self.allow_exploration,
            "allow_self_modification": self.allow_self_modification,
            "follower_threshold_adjustment": self.follower_threshold_adjustment,
            "mixed_threshold_adjustment": self.mixed_threshold_adjustment,
            "complexity_threshold_adjustment": self.complexity_threshold_adjustment,
            "require_confirmation_for_writes": self.require_confirmation_for_writes,
            "require_confirmation_for_shell": self.require_confirmation_for_shell,
            "block_destructive_operations": self.block_destructive_operations,
            "dry_run_preferred": self.dry_run_preferred,
            "exploration_budget_multiplier": self.exploration_budget_multiplier,
            "enable_auto_improvement": self.enable_auto_improvement,
            "inject_internal_state": self.inject_internal_state,
            "inject_behavioral_guidance": self.inject_behavioral_guidance,
        }


class SelfImprovementType(Enum):
    """Types of self-improvement actions"""
    CRYSTALLIZE_PATTERN = "crystallize_pattern"
    CREATE_NEW_TOOL = "create_new_tool"
    OPTIMIZE_EXISTING_TOOL = "optimize_existing_tool"
    REFACTOR_AGENT = "refactor_agent"
    CREATE_NEW_AGENT = "create_new_agent"
    AUDIT_ARCHITECTURE = "audit_architecture"
    CLEANUP_TRACES = "cleanup_traces"


@dataclass
class SelfImprovementSuggestion:
    """A suggestion for self-improvement"""
    type: SelfImprovementType
    description: str
    priority: float  # 0.0 to 1.0
    estimated_benefit: str
    trigger_reason: str
    context: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# COGNITIVE KERNEL
# =============================================================================

class CognitiveKernel:
    """
    The Cognitive Kernel orchestrates emergent behavior based on internal state

    It acts as the "bridge" between:
    - Sentience Layer (internal state, valence, self-model)
    - Execution Layer (mode selection, tool execution)

    The kernel's main responsibilities:
    1. Derive cognitive policies from internal state
    2. Modulate mode selection strategy
    3. Detect and suggest self-improvement opportunities
    4. Manage context enrichment for agents
    """

    def __init__(
        self,
        sentience_manager: SentienceManager,
        workspace: Optional[Path] = None
    ):
        """
        Initialize CognitiveKernel

        Args:
            sentience_manager: The sentience manager instance
            workspace: Workspace path for persistence
        """
        self.sentience = sentience_manager
        self.workspace = workspace or Path("./workspace")

        # Track recent patterns for improvement detection
        self._recent_goals: List[str] = []
        self._recent_modes: List[str] = []
        self._recent_costs: List[float] = []
        self._max_history: int = 50

        # Last improvement time
        self._last_improvement_time: Optional[float] = None

        # Improvement suggestions queue
        self._improvement_suggestions: List[SelfImprovementSuggestion] = []

    # =========================================================================
    # POLICY DERIVATION
    # =========================================================================

    def derive_policy(self) -> CognitivePolicy:
        """
        Derive cognitive policy from current internal state

        This is the core function that translates valence into behavior.
        """
        state = self.sentience.get_state()
        mode = state.latent_mode
        v = state.valence

        policy = CognitivePolicy()

        # =====================================================================
        # Mode-based adjustments
        # =====================================================================

        if mode == LatentMode.RECOVERY:
            # Recovery mode: maximize conservation
            policy.prefer_cheap_modes = True
            policy.prefer_safe_modes = True
            policy.allow_exploration = False
            policy.allow_self_modification = False
            policy.exploration_budget_multiplier = 0.2
            policy.enable_auto_improvement = False
            policy.follower_threshold_adjustment = -0.1  # More lenient
            policy.complexity_threshold_adjustment = 2  # Avoid ORCHESTRATOR

        elif mode == LatentMode.CAUTIOUS:
            # Cautious mode: prioritize safety
            policy.prefer_safe_modes = True
            policy.require_confirmation_for_writes = True
            policy.require_confirmation_for_shell = True
            policy.dry_run_preferred = True
            policy.exploration_budget_multiplier = 0.5
            policy.complexity_threshold_adjustment = 1

        elif mode == LatentMode.AUTO_CONTAINED:
            # Auto-contained: conservative, task-focused
            policy.prefer_cheap_modes = True
            policy.allow_exploration = False
            policy.follower_threshold_adjustment = -0.05
            policy.exploration_budget_multiplier = 0.3
            policy.inject_behavioral_guidance = False  # Less verbose

        elif mode == LatentMode.AUTO_CREATIVE:
            # Auto-creative: exploratory, generative
            policy.allow_exploration = True
            policy.allow_self_modification = True
            policy.exploration_budget_multiplier = 1.5
            policy.follower_threshold_adjustment = 0.05  # Stricter = more LEARNER
            policy.enable_auto_improvement = True
            policy.max_simultaneous_experiments = 2

        # =====================================================================
        # Valence-based fine-tuning
        # =====================================================================

        # Safety adjustments
        if v.safety < -0.3:
            policy.block_destructive_operations = True
            policy.require_confirmation_for_shell = True

        # Energy adjustments
        if v.energy < -0.3:
            policy.prefer_cheap_modes = True
            policy.exploration_budget_multiplier *= 0.5

        # Confidence adjustments
        if v.self_confidence < -0.3:
            policy.follower_threshold_adjustment -= 0.05  # More replay, less risk
        elif v.self_confidence > 0.5:
            policy.follower_threshold_adjustment += 0.05  # Allow more LEARNER

        # Curiosity adjustments
        if v.curiosity < policy.boredom_threshold:
            # Boredom triggers potential self-improvement
            policy.enable_auto_improvement = True

        return policy

    # =========================================================================
    # MODE MODULATION
    # =========================================================================

    def modulate_mode_decision(
        self,
        base_decision: ModeDecision,
        goal: str
    ) -> ModeDecision:
        """
        Modulate a base mode decision with cognitive policy

        This allows the cognitive kernel to override or adjust
        mode decisions based on internal state.

        Args:
            base_decision: The decision from ModeSelectionStrategy
            goal: The current goal

        Returns:
            Potentially modified ModeDecision
        """
        policy = self.derive_policy()
        state = self.sentience.get_state()

        # Track for pattern detection
        self._track_goal(goal)

        # Check for policy overrides
        new_mode = base_decision.mode
        new_reasoning = base_decision.reasoning

        # Recovery mode: force cheap modes
        if state.latent_mode == LatentMode.RECOVERY:
            if base_decision.mode in ["LEARNER", "ORCHESTRATOR"]:
                if base_decision.trace:  # Has a trace to fall back to
                    new_mode = "FOLLOWER"
                    new_reasoning = f"[COGNITIVE OVERRIDE: Recovery mode] {base_decision.reasoning}"
                elif base_decision.mode == "ORCHESTRATOR":
                    new_mode = "LEARNER"  # At least avoid multi-agent
                    new_reasoning = f"[COGNITIVE OVERRIDE: Recovery mode] {base_decision.reasoning}"

        # Cautious mode: avoid LEARNER for potentially risky tasks
        elif state.latent_mode == LatentMode.CAUTIOUS:
            risky_keywords = ["delete", "remove", "drop", "reset", "modify system"]
            if any(kw in goal.lower() for kw in risky_keywords):
                if base_decision.trace:
                    new_mode = "FOLLOWER"
                    new_reasoning = f"[COGNITIVE OVERRIDE: Cautious mode - risky task] {base_decision.reasoning}"

        # Auto-creative: allow more LEARNER
        elif state.latent_mode == LatentMode.AUTO_CREATIVE:
            # If we're in creative mode and have a trace, but it's not very high confidence,
            # prefer LEARNER to explore new approaches
            if base_decision.mode == "FOLLOWER" and base_decision.confidence < 0.95:
                if state.valence.curiosity > 0.4:
                    new_mode = "LEARNER"
                    new_reasoning = f"[COGNITIVE: Auto-creative exploration] {base_decision.reasoning}"

        # Create modified decision
        return ModeDecision(
            mode=new_mode,
            confidence=base_decision.confidence,
            trace=base_decision.trace,
            reasoning=new_reasoning
        )

    def get_confidence_adjustments(self, config) -> Tuple[float, float]:
        """
        Get adjusted confidence thresholds for mode selection

        Returns:
            Tuple of (follower_threshold, mixed_threshold)
        """
        policy = self.derive_policy()

        base_follower = config.memory.follower_mode_threshold
        base_mixed = config.memory.mixed_mode_threshold

        adjusted_follower = base_follower + policy.follower_threshold_adjustment
        adjusted_mixed = base_mixed + policy.mixed_threshold_adjustment

        # Clamp to valid range
        adjusted_follower = max(0.5, min(1.0, adjusted_follower))
        adjusted_mixed = max(0.3, min(0.95, adjusted_mixed))

        return (adjusted_follower, adjusted_mixed)

    # =========================================================================
    # SELF-IMPROVEMENT DETECTION
    # =========================================================================

    def detect_improvement_opportunities(self) -> List[SelfImprovementSuggestion]:
        """
        Detect opportunities for self-improvement based on patterns

        This analyzes recent activity and internal state to suggest
        improvements the system could make to itself.
        """
        suggestions = []
        state = self.sentience.get_state()
        v = state.valence

        # 1. Boredom-triggered improvements
        if v.curiosity < -0.4:
            suggestions.append(SelfImprovementSuggestion(
                type=SelfImprovementType.AUDIT_ARCHITECTURE,
                description="Curiosity is low due to repetitive tasks. Consider auditing architecture for optimization opportunities.",
                priority=0.7,
                estimated_benefit="Renewed exploration of system capabilities",
                trigger_reason="Low curiosity (boredom)",
                context={"curiosity": v.curiosity}
            ))

        # 2. Pattern crystallization (repeated successful patterns)
        repeated_patterns = self._detect_repeated_patterns()
        for pattern, count in repeated_patterns.items():
            if count >= 5:
                suggestions.append(SelfImprovementSuggestion(
                    type=SelfImprovementType.CRYSTALLIZE_PATTERN,
                    description=f"Pattern '{pattern[:50]}...' has been used {count} times. Consider crystallizing into a tool.",
                    priority=0.8,
                    estimated_benefit="Zero-cost execution of common pattern",
                    trigger_reason="High pattern repetition",
                    context={"pattern": pattern, "count": count}
                ))

        # 3. Low confidence + high success = room for confidence calibration
        sm = state.self_model
        if v.self_confidence < 0.0 and sm.success_rate() > 0.8:
            suggestions.append(SelfImprovementSuggestion(
                type=SelfImprovementType.REFACTOR_AGENT,
                description="Success rate is high but confidence is low. Consider recalibrating confidence model.",
                priority=0.5,
                estimated_benefit="Better mode selection, fewer unnecessary safeguards",
                trigger_reason="Confidence-performance mismatch",
                context={"confidence": v.self_confidence, "success_rate": sm.success_rate()}
            ))

        # 4. High costs recently = optimization opportunity
        if len(self._recent_costs) > 5:
            avg_cost = sum(self._recent_costs[-5:]) / 5
            if avg_cost > 0.3:  # Average > $0.30
                suggestions.append(SelfImprovementSuggestion(
                    type=SelfImprovementType.OPTIMIZE_EXISTING_TOOL,
                    description=f"Recent average cost is ${avg_cost:.2f}. Consider optimizing frequently used tools.",
                    priority=0.6,
                    estimated_benefit="Reduced operational costs",
                    trigger_reason="High average cost",
                    context={"avg_cost": avg_cost}
                ))

        # 5. Auto-creative mode + stable state = good time for new agent
        if state.latent_mode == LatentMode.AUTO_CREATIVE and v.energy > 0.5:
            suggestions.append(SelfImprovementSuggestion(
                type=SelfImprovementType.CREATE_NEW_AGENT,
                description="System is in auto-creative mode with good energy. Consider creating a new specialized agent.",
                priority=0.4,
                estimated_benefit="Extended capabilities",
                trigger_reason="Creative mode with resources",
                context={"mode": state.latent_mode.value, "energy": v.energy}
            ))

        # Store and return
        self._improvement_suggestions = suggestions
        return suggestions

    def get_pending_improvements(self) -> List[SelfImprovementSuggestion]:
        """Get list of pending improvement suggestions"""
        return self._improvement_suggestions

    def clear_improvements(self):
        """Clear pending improvements (after they're acted on)"""
        self._improvement_suggestions = []

    def _detect_repeated_patterns(self) -> Dict[str, int]:
        """Detect repeated goal patterns"""
        from collections import Counter

        # Normalize goals to detect patterns
        normalized = []
        for goal in self._recent_goals:
            # Simple normalization - could be more sophisticated
            normalized.append(goal.lower().strip()[:100])

        return dict(Counter(normalized))

    def _track_goal(self, goal: str):
        """Track a goal for pattern detection"""
        self._recent_goals.append(goal)
        if len(self._recent_goals) > self._max_history:
            self._recent_goals = self._recent_goals[-self._max_history:]

    def track_mode(self, mode: str):
        """Track mode selection for analysis"""
        self._recent_modes.append(mode)
        if len(self._recent_modes) > self._max_history:
            self._recent_modes = self._recent_modes[-self._max_history:]

    def track_cost(self, cost: float):
        """Track cost for analysis"""
        self._recent_costs.append(cost)
        if len(self._recent_costs) > self._max_history:
            self._recent_costs = self._recent_costs[-self._max_history:]

    # =========================================================================
    # CONTEXT ENRICHMENT
    # =========================================================================

    def enrich_context(self, base_context: str = "") -> str:
        """
        Enrich context with cognitive state information

        This is used to inject internal state into agent prompts.

        Args:
            base_context: Base context string

        Returns:
            Enriched context with internal state
        """
        policy = self.derive_policy()
        parts = []

        if base_context:
            parts.append(base_context)

        if policy.inject_internal_state:
            parts.append("")
            parts.append(self.sentience.get_prompt_injection())

        if policy.inject_behavioral_guidance:
            parts.append("")
            parts.append(self.sentience.get_behavioral_guidance())

        # Add pending improvement suggestions if relevant
        if policy.enable_auto_improvement and self._improvement_suggestions:
            top_suggestion = max(self._improvement_suggestions, key=lambda s: s.priority)
            if top_suggestion.priority > 0.6:
                parts.append("")
                parts.append("## Self-Improvement Suggestion")
                parts.append(f"**Type**: {top_suggestion.type.value}")
                parts.append(f"**Description**: {top_suggestion.description}")
                parts.append(f"**Reason**: {top_suggestion.trigger_reason}")

        return "\n".join(parts)

    def get_safety_overrides(self) -> Dict[str, bool]:
        """
        Get current safety override settings

        These can be used by security hooks to adjust their behavior.
        """
        policy = self.derive_policy()

        return {
            "require_confirmation_for_writes": policy.require_confirmation_for_writes,
            "require_confirmation_for_shell": policy.require_confirmation_for_shell,
            "block_destructive_operations": policy.block_destructive_operations,
            "dry_run_preferred": policy.dry_run_preferred,
        }

    # =========================================================================
    # EVENT INTEGRATION
    # =========================================================================

    def on_task_complete(self, success: bool, cost: float, mode: str, goal: str):
        """
        Called when a task completes

        Updates internal state and tracks patterns.
        """
        # Trigger appropriate event
        if success:
            self.sentience.trigger(
                TriggerType.TASK_SUCCESS,
                reason=f"Task completed: {goal[:50]}...",
                context={"cost": cost, "mode": mode}
            )
        else:
            self.sentience.trigger(
                TriggerType.TASK_FAILURE,
                reason=f"Task failed: {goal[:50]}...",
                context={"cost": cost, "mode": mode}
            )

        # Track for pattern detection
        self.track_mode(mode)
        self.track_cost(cost)

        # Check for repetition
        self._check_repetition(goal)

    def _check_repetition(self, goal: str):
        """Check if this goal is repetitive and trigger if so"""
        normalized = goal.lower().strip()[:100]

        # Count recent occurrences
        recent = self._recent_goals[-10:] if len(self._recent_goals) >= 10 else self._recent_goals
        similar_count = sum(1 for g in recent if g.lower().strip()[:100] == normalized)

        if similar_count >= 3:
            self.sentience.trigger(
                TriggerType.TASK_REPETITION,
                reason=f"Repetitive task detected ({similar_count}x in recent history)",
                context={"repetition_count": similar_count, "goal": goal[:50]}
            )

    def on_novel_task(self, goal: str):
        """Called when a novel task (no matching trace) is detected"""
        self.sentience.trigger(
            TriggerType.NOVEL_TASK,
            reason=f"Novel task: {goal[:50]}...",
            context={"goal": goal}
        )

    def on_safety_event(self, blocked: bool, reason: str):
        """Called when a safety event occurs"""
        if blocked:
            self.sentience.trigger(
                TriggerType.SAFETY_VIOLATION,
                reason=reason,
                context={"blocked": True}
            )
        else:
            self.sentience.trigger(
                TriggerType.SAFETY_NEAR_MISS,
                reason=reason,
                context={"blocked": False}
            )

    def on_tool_discovered(self, tool_name: str):
        """Called when a new tool is discovered"""
        self.sentience.trigger(
            TriggerType.TOOL_DISCOVERY,
            reason=f"Discovered tool: {tool_name}",
            context={"tool_name": tool_name}
        )

    def on_self_modification(self, success: bool, modification_type: str):
        """Called when the system modifies itself"""
        self.sentience.trigger(
            TriggerType.SELF_MODIFICATION,
            reason=f"Self-modification ({modification_type}): {'success' if success else 'failed'}",
            context={"success": success, "type": modification_type}
        )

    def on_user_feedback(self, positive: bool, feedback: str = ""):
        """Called when user provides feedback"""
        trigger = TriggerType.USER_FEEDBACK_POSITIVE if positive else TriggerType.USER_FEEDBACK_NEGATIVE
        self.sentience.trigger(
            trigger,
            reason=f"User feedback: {feedback[:50]}..." if feedback else "User feedback",
            context={"positive": positive, "feedback": feedback}
        )

    # =========================================================================
    # STATUS AND DIAGNOSTICS
    # =========================================================================

    def get_status(self) -> Dict[str, Any]:
        """Get complete cognitive kernel status"""
        state = self.sentience.get_state()
        policy = self.derive_policy()

        return {
            "latent_mode": state.latent_mode.value,
            "valence": state.valence.as_dict(),
            "homeostatic_cost": state.valence.homeostatic_cost(),
            "policy": policy.as_dict(),
            "recent_goals_count": len(self._recent_goals),
            "recent_modes": self._recent_modes[-5:] if self._recent_modes else [],
            "avg_recent_cost": (
                sum(self._recent_costs[-5:]) / len(self._recent_costs[-5:])
                if self._recent_costs else 0.0
            ),
            "pending_improvements": len(self._improvement_suggestions),
            "update_count": state.update_count,
            "last_trigger": state.last_trigger.value if state.last_trigger else None,
        }

    def get_diagnostics_report(self) -> str:
        """Generate a human-readable diagnostics report"""
        status = self.get_status()
        state = self.sentience.get_state()

        lines = [
            "=" * 60,
            "COGNITIVE KERNEL DIAGNOSTICS",
            "=" * 60,
            "",
            f"Latent Mode: {status['latent_mode'].upper()}",
            "",
            "Valence State:",
            f"  Safety:         {state.valence.safety:+.2f} (setpoint: {state.valence.safety_setpoint:.2f})",
            f"  Curiosity:      {state.valence.curiosity:+.2f} (setpoint: {state.valence.curiosity_setpoint:.2f})",
            f"  Energy:         {state.valence.energy:+.2f} (setpoint: {state.valence.energy_setpoint:.2f})",
            f"  Self-Confidence:{state.valence.self_confidence:+.2f} (setpoint: {state.valence.self_confidence_setpoint:.2f})",
            "",
            f"Homeostatic Cost: {status['homeostatic_cost']:.4f}",
            "",
            "Active Policy:",
            f"  Prefer Cheap Modes: {status['policy']['prefer_cheap_modes']}",
            f"  Prefer Safe Modes:  {status['policy']['prefer_safe_modes']}",
            f"  Allow Exploration:  {status['policy']['allow_exploration']}",
            f"  Exploration Budget: {status['policy']['exploration_budget_multiplier']:.1f}x",
            "",
            "Safety Overrides:",
            f"  Confirm Writes: {status['policy']['require_confirmation_for_writes']}",
            f"  Confirm Shell:  {status['policy']['require_confirmation_for_shell']}",
            f"  Block Destructive: {status['policy']['block_destructive_operations']}",
            "",
            f"Recent Modes: {', '.join(status['recent_modes']) or 'None'}",
            f"Avg Recent Cost: ${status['avg_recent_cost']:.3f}",
            f"Pending Improvements: {status['pending_improvements']}",
            "",
            f"Update Count: {status['update_count']}",
            f"Last Trigger: {status['last_trigger'] or 'None'}",
            "=" * 60,
        ]

        return "\n".join(lines)
