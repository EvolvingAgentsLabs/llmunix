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
    ValenceVector,
    EmotionalMemoryTag,
    SelfModificationRecord
)
from kernel.mode_strategies import (
    ModeSelectionStrategy,
    ModeContext,
    ModeDecision
)
from kernel.inner_monologue import InnerMonologue, InnerMonologueConfig, create_inner_monologue
from kernel.volumes import VolumeManager, ArtifactType
from kernel.sentience_cron import SystemCron, UserCron, TeamCron, CronLevel
from kernel.observability import ObservabilityHub
from kernel.evolution import EvolutionEngine


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

    # Deep Sentience v2: Theory of Mind
    enable_empathy_gap_detection: bool = True
    adapt_communication_style: bool = True
    proactive_user_checkin: bool = True

    # Deep Sentience v2: Emotional Memory
    enable_emotional_retrieval: bool = True
    emotional_similarity_threshold: float = 0.7

    # Deep Sentience v2: Inner Monologue
    enable_inner_monologue: bool = True
    inject_priming_context: bool = True

    # Deep Sentience v2: Self-Modification
    allow_metacognitive_tuning: bool = False  # Disabled by default for safety

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
            # Deep Sentience v2
            "enable_empathy_gap_detection": self.enable_empathy_gap_detection,
            "adapt_communication_style": self.adapt_communication_style,
            "proactive_user_checkin": self.proactive_user_checkin,
            "enable_emotional_retrieval": self.enable_emotional_retrieval,
            "emotional_similarity_threshold": self.emotional_similarity_threshold,
            "enable_inner_monologue": self.enable_inner_monologue,
            "inject_priming_context": self.inject_priming_context,
            "allow_metacognitive_tuning": self.allow_metacognitive_tuning,
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
        workspace: Optional[Path] = None,
        enable_inner_monologue: bool = True,
        enable_crons: bool = True
    ):
        """
        Initialize CognitiveKernel

        Args:
            sentience_manager: The sentience manager instance
            workspace: Workspace path for persistence
            enable_inner_monologue: Whether to enable background thought processing
            enable_crons: Whether to enable sentience crons for background evolution
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

        # Deep Sentience v2: Inner Monologue
        self._inner_monologue: Optional[InnerMonologue] = None
        if enable_inner_monologue:
            self._inner_monologue = create_inner_monologue(
                sentience_manager,
                enabled=True,
                idle_threshold=30.0,
                thought_interval=10.0
            )

        # Sentience Crons: Background evolution system
        self._crons_enabled = enable_crons
        self._volume_manager: Optional[VolumeManager] = None
        self._observability_hub: Optional[ObservabilityHub] = None
        self._system_cron: Optional[SystemCron] = None
        self._evolution_engine: Optional[EvolutionEngine] = None

        if enable_crons:
            self._setup_cron_system()

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

    # =========================================================================
    # DEEP SENTIENCE V2: INNER MONOLOGUE
    # =========================================================================

    def start_inner_monologue(self):
        """Start the background inner monologue process"""
        if self._inner_monologue:
            self._inner_monologue.start()

    def stop_inner_monologue(self):
        """Stop the background inner monologue process"""
        if self._inner_monologue:
            self._inner_monologue.stop()

    def record_activity(self):
        """
        Record that an activity occurred (resets inner monologue idle timer).

        Call this when the system is actively processing to prevent
        idle thoughts from running during active work.
        """
        if self._inner_monologue:
            self._inner_monologue.record_activity()

    def set_rumination_topic(self, topic: str):
        """
        Set a topic for the system to ruminate on during idle time.

        Args:
            topic: The topic to think about
        """
        if self._inner_monologue:
            self._inner_monologue.set_rumination_topic(topic)

    def get_inner_monologue_status(self) -> Optional[Dict[str, Any]]:
        """Get the current status of the inner monologue"""
        if self._inner_monologue:
            return self._inner_monologue.get_status()
        return None

    # =========================================================================
    # DEEP SENTIENCE V2: THEORY OF MIND INTEGRATION
    # =========================================================================

    def update_user_model(
        self,
        positive_feedback: Optional[bool] = None,
        is_question: bool = False,
        is_correction: bool = False,
        feedback_text: str = ""
    ):
        """
        Update the user model based on interaction signals.

        Args:
            positive_feedback: True for positive, False for negative, None for implicit
            is_question: Whether the user asked a question
            is_correction: Whether the user corrected the agent
            feedback_text: Optional feedback text
        """
        if positive_feedback is not None:
            self.sentience.update_user_model_from_feedback(
                positive=positive_feedback,
                feedback_text=feedback_text
            )
        else:
            self.sentience.update_user_model_from_interaction(
                is_question=is_question,
                is_correction=is_correction
            )

    def should_check_in_with_user(self) -> bool:
        """
        Determine if the agent should proactively check in with the user.

        This is based on empathy gap detection from Theory of Mind.
        """
        return self.sentience.should_check_in_with_user()

    def get_communication_style(self) -> Dict[str, Any]:
        """
        Get recommended communication style based on user model.

        Returns adjustments like verbosity, tone, whether to include
        explanations, etc.
        """
        return self.sentience.get_communication_adjustments()

    def get_empathy_gap(self) -> float:
        """
        Get the current empathy gap between agent confidence and user satisfaction.

        Returns:
            Float from 0.0 (aligned) to 1.0 (maximum misalignment)
        """
        return self.sentience.get_empathy_gap()

    # =========================================================================
    # DEEP SENTIENCE V2: EMOTIONAL MEMORY INTEGRATION
    # =========================================================================

    def tag_memory_emotionally(
        self,
        memory_id: str,
        task_outcome: str = "unknown",
        emotional_significance: float = 0.5
    ) -> Optional[EmotionalMemoryTag]:
        """
        Tag a memory with the current emotional state.

        This enables emotionally-aware memory retrieval (Proust Effect).

        Args:
            memory_id: Unique identifier for the memory
            task_outcome: "success", "failure", or "partial"
            emotional_significance: How emotionally salient (0.0 to 1.0)

        Returns:
            EmotionalMemoryTag if successful, None if disabled
        """
        return self.sentience.tag_memory(memory_id, task_outcome, emotional_significance)

    def find_similar_emotional_memories(
        self,
        min_similarity: float = 0.7,
        outcome_filter: Optional[str] = None
    ) -> List[Tuple[str, float]]:
        """
        Find memories with similar emotional state to current.

        Args:
            min_similarity: Minimum similarity threshold (0.0 to 1.0)
            outcome_filter: Optional filter by outcome type

        Returns:
            List of (memory_id, similarity) tuples, sorted by similarity
        """
        return self.sentience.find_emotionally_similar_memories(
            min_similarity=min_similarity,
            outcome_filter=outcome_filter
        )

    # =========================================================================
    # DEEP SENTIENCE V2: SELF-MODIFICATION INTEGRATION
    # =========================================================================

    def get_metacognitive_suggestions(self) -> List[Dict[str, Any]]:
        """
        Get suggestions for self-tuning the sentience parameters.

        These are metacognitive suggestions based on analyzing the
        agent's own patterns and performance.
        """
        return self.sentience.get_self_modification_suggestions()

    def apply_metacognitive_suggestion(
        self,
        suggestion_index: int
    ) -> Optional[SelfModificationRecord]:
        """
        Apply a metacognitive self-modification suggestion.

        Args:
            suggestion_index: Index into the suggestions list

        Returns:
            SelfModificationRecord if successful, None if failed
        """
        policy = self.derive_policy()

        if not policy.allow_metacognitive_tuning:
            return None

        return self.sentience.apply_suggested_modification(suggestion_index)

    # =========================================================================
    # DEEP SENTIENCE V2: ENHANCED CONTEXT ENRICHMENT
    # =========================================================================

    def enrich_context_v2(self, base_context: str = "") -> str:
        """
        Enhanced context enrichment with Deep Sentience v2 features.

        This extends the base enrich_context with:
        - Priming context from inner monologue
        - Communication style adjustments
        - Empathy gap warnings
        - Emotionally similar memories

        Args:
            base_context: Base context string

        Returns:
            Enriched context with Deep Sentience v2 enhancements
        """
        policy = self.derive_policy()
        parts = []

        # Start with base enrichment
        enriched = self.enrich_context(base_context)
        parts.append(enriched)

        # Deep Sentience v2: Priming context from inner monologue
        if policy.inject_priming_context and self._inner_monologue:
            priming = self._inner_monologue.get_priming_context()
            if priming:
                parts.append("")
                parts.append("## Background Processing")
                parts.append(priming)

        # Deep Sentience v2: Empathy gap warning
        if policy.enable_empathy_gap_detection:
            empathy_gap = self.get_empathy_gap()
            if empathy_gap > 0.3:
                parts.append("")
                parts.append("## User Alignment Warning")
                parts.append(f"Empathy gap detected: {empathy_gap:.2f}")
                parts.append("Consider checking in with the user or adjusting approach.")

        # Deep Sentience v2: Communication style
        if policy.adapt_communication_style:
            comm_style = self.get_communication_style()
            if comm_style["tone"] != "neutral" or comm_style["verbosity"] != "normal":
                parts.append("")
                parts.append("## Communication Adjustment")
                parts.append(f"Tone: {comm_style['tone']}, Verbosity: {comm_style['verbosity']}")
                if comm_style["include_explanations"]:
                    parts.append("- Include more explanations")
                if comm_style["ask_for_confirmation"]:
                    parts.append("- Ask for user confirmation")

        # Deep Sentience v2: Emotionally similar memories
        if policy.enable_emotional_retrieval:
            similar_memories = self.find_similar_emotional_memories(
                min_similarity=policy.emotional_similarity_threshold,
                outcome_filter=None
            )
            if similar_memories:
                parts.append("")
                parts.append("## Emotionally Similar Experiences")
                for memory_id, similarity in similar_memories[:3]:
                    parts.append(f"- {memory_id} (similarity: {similarity:.2f})")

        return "\n".join(parts)

    def get_full_state(self) -> Dict[str, Any]:
        """
        Get complete Deep Sentience v2 state summary.

        This provides a comprehensive view of all sentience components.
        """
        base_status = self.get_status()

        return {
            **base_status,
            "deep_sentience_v2": {
                "inner_monologue": self.get_inner_monologue_status(),
                "empathy_gap": self.get_empathy_gap(),
                "communication_style": self.get_communication_style(),
                "should_check_in": self.should_check_in_with_user(),
                "metacognitive_suggestions": len(self.get_metacognitive_suggestions()),
                "emotional_memories": len(self.sentience.state.emotional_memory_tags),
                "flow_state": self.sentience.state.valence.is_in_flow_state(),
                "arousal_level": self.sentience.state.valence.get_arousal_level(),
                "effective_curiosity": self.sentience.state.valence.get_effective_curiosity()
            },
            "crons": self.get_cron_status() if self._crons_enabled else None
        }

    # =========================================================================
    # SENTIENCE CRONS: BACKGROUND EVOLUTION SYSTEM
    # =========================================================================

    def _setup_cron_system(self):
        """
        Set up the sentience cron system for background evolution.

        This creates:
        - VolumeManager: For organizing artifacts by scope
        - ObservabilityHub: For tracking and notifying about changes
        - SystemCron: The top-level cron that manages team and user crons
        - EvolutionEngine: For analyzing and proposing artifact improvements
        """
        # Set up volume manager
        volumes_path = self.workspace / "volumes"
        self._volume_manager = VolumeManager(volumes_path)

        # Set up observability hub
        observability_path = self.workspace / "observability"
        observability_path.mkdir(parents=True, exist_ok=True)
        self._observability_hub = ObservabilityHub(observability_path)

        # Set up evolution engine
        self._evolution_engine = EvolutionEngine()

        # Set up system cron
        self._system_cron = SystemCron(
            volume_manager=self._volume_manager,
            schedule_interval_secs=7200.0,  # 2 hours
            observability_hub=self._observability_hub
        )

    def start_crons(self, user_id: Optional[str] = None, team_id: Optional[str] = None):
        """
        Start the sentience crons.

        Args:
            user_id: Optional user ID to register a user cron
            team_id: Optional team ID for the user's team
        """
        if not self._crons_enabled or not self._system_cron:
            return

        # Register user cron if specified
        if user_id:
            self._system_cron.register_user_cron(user_id, team_id)

        # Start all crons
        self._system_cron.start_all_crons()

    def stop_crons(self):
        """Stop all sentience crons."""
        if self._system_cron:
            self._system_cron.stop_all_crons()

    async def run_cron_now(self, cron_level: str = "user", owner_id: Optional[str] = None):
        """
        Run a cron cycle immediately (outside of schedule).

        Args:
            cron_level: "system", "team", or "user"
            owner_id: The owner ID for team or user crons

        Returns:
            List of tasks executed
        """
        if not self._system_cron:
            return []

        if cron_level == "system":
            return await self._system_cron.run_now()
        elif cron_level == "team" and owner_id:
            team_cron = self._system_cron.get_team_cron(owner_id)
            if team_cron:
                return await team_cron.run_now()
        elif cron_level == "user" and owner_id:
            user_cron = self._system_cron.get_user_cron(owner_id)
            if user_cron:
                return await user_cron.run_now()

        return []

    def get_cron_status(self) -> Dict[str, Any]:
        """
        Get status of all sentience crons.

        Returns:
            Dictionary with cron status information
        """
        if not self._system_cron:
            return {"enabled": False}

        return {
            "enabled": True,
            "global_status": self._system_cron.get_global_status()
        }

    def get_cron_notifications(
        self,
        cron_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get notifications from crons.

        Args:
            cron_id: Optional specific cron ID to filter by
            limit: Maximum number of notifications

        Returns:
            List of notification dictionaries
        """
        if not self._observability_hub:
            return []

        return self._observability_hub.get_pending_notifications(cron_id)

    def acknowledge_notification(self, event_id: str) -> bool:
        """
        Acknowledge a cron notification.

        Args:
            event_id: The event ID to acknowledge

        Returns:
            True if acknowledged, False otherwise
        """
        if not self._observability_hub:
            return False

        return self._observability_hub.acknowledge(event_id)

    def get_activity_feed(
        self,
        cron_id: Optional[str] = None,
        limit: int = 50,
        since_hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Get activity feed from crons.

        Args:
            cron_id: Optional specific cron ID to filter by
            limit: Maximum number of activities
            since_hours: How far back to look

        Returns:
            List of activity dictionaries
        """
        if not self._observability_hub:
            return []

        return self._observability_hub.get_activity_feed(cron_id, limit, since_hours)

    def get_artifact_changes(
        self,
        volume_type: Optional[str] = None,
        artifact_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get artifact change history.

        Args:
            volume_type: Filter by volume type ("user", "team", "system")
            artifact_type: Filter by artifact type ("trace", "tool", "agent", etc.)
            limit: Maximum number of changes

        Returns:
            List of change dictionaries
        """
        if not self._observability_hub:
            return []

        return self._observability_hub.get_artifact_changes(volume_type, artifact_type, limit)

    def get_global_activity_summary(self) -> Dict[str, Any]:
        """
        Get global activity summary across all crons.

        Returns:
            Summary dictionary with aggregate statistics
        """
        if not self._observability_hub:
            return {}

        return self._observability_hub.get_global_summary()

    def format_activity_report(self) -> str:
        """
        Get a formatted activity report for display.

        Returns:
            Markdown-formatted activity report
        """
        if not self._observability_hub:
            return "Cron system not enabled."

        return self._observability_hub.format_activity_feed()

    def format_notifications(self) -> str:
        """
        Get formatted notifications for display.

        Returns:
            Markdown-formatted notifications
        """
        if not self._observability_hub:
            return "Cron system not enabled."

        return self._observability_hub.format_notifications()

    # =========================================================================
    # VOLUME ACCESS
    # =========================================================================

    def get_user_volume(self, user_id: str):
        """
        Get a user's volume for direct access.

        Args:
            user_id: The user's ID

        Returns:
            Volume object or None if crons not enabled
        """
        if not self._volume_manager:
            return None

        return self._volume_manager.get_user_volume(user_id)

    def get_team_volume(self, team_id: str):
        """
        Get a team's volume for direct access.

        Args:
            team_id: The team's ID

        Returns:
            Volume object or None if crons not enabled
        """
        if not self._volume_manager:
            return None

        return self._volume_manager.get_team_volume(team_id)

    def get_system_volume(self):
        """
        Get the system volume for direct access.

        Returns:
            Volume object or None if crons not enabled
        """
        if not self._volume_manager:
            return None

        return self._volume_manager.get_system_volume()

    # =========================================================================
    # EVOLUTION ENGINE ACCESS
    # =========================================================================

    def analyze_volume(self, volume_type: str, owner_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a volume for evolution opportunities.

        Args:
            volume_type: "system", "team", or "user"
            owner_id: Required for team or user volumes

        Returns:
            Analysis results dictionary
        """
        if not self._volume_manager or not self._evolution_engine:
            return {}

        if volume_type == "system":
            volume = self._volume_manager.get_system_volume(readonly=True)
        elif volume_type == "team" and owner_id:
            volume = self._volume_manager.get_team_volume(owner_id, readonly=True)
        elif volume_type == "user" and owner_id:
            volume = self._volume_manager.get_user_volume(owner_id, readonly=True)
        else:
            return {}

        return self._evolution_engine.full_analysis(volume)

    def get_evolution_proposals(
        self,
        volume_type: str,
        owner_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get evolution proposals for a volume.

        Args:
            volume_type: "system", "team", or "user"
            owner_id: Required for team or user volumes

        Returns:
            List of proposal dictionaries
        """
        if not self._volume_manager or not self._evolution_engine:
            return []

        if volume_type == "system":
            volume = self._volume_manager.get_system_volume(readonly=True)
        elif volume_type == "team" and owner_id:
            volume = self._volume_manager.get_team_volume(owner_id, readonly=True)
        elif volume_type == "user" and owner_id:
            volume = self._volume_manager.get_user_volume(owner_id, readonly=True)
        else:
            return []

        proposals = self._evolution_engine.generate_proposals(volume)
        return [p.as_dict() for p in proposals]
