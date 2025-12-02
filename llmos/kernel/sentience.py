"""
Sentience Layer for LLM OS

This module implements a "sentience-like" architecture for the LLM OS, providing:
- Persistent internal state (valence/affective variables)
- Homeostatic dynamics (set-points and deviation costs)
- Self-model integration
- Event-driven state updates
- Latent state for auto-creative vs auto-contained behavior

Architecture based on the formal proposal:
- v_t: Affective state vector (safety, curiosity, energy, self_confidence)
- sigma_t: Self-model state (beliefs about own capabilities)
- g_t: Goal/drive state (current priorities influenced by valence)
- b_t: Global workspace (what's currently "in focus")

Key Concepts:
- **Homeostatic Dynamics**: Each valence dimension has a set-point; deviations
  create internal pressure that influences behavior.
- **Latent State**: An emergent "mode" (auto-creative vs auto-contained) that
  arises from the combination of valence variables and context.
- **Triggers**: Events that modify internal state (task success/failure,
  repetition, novelty, safety violations, etc.)

Safety Note:
This is an *architectural* implementation of sentience-like behavior, not a
claim of actual consciousness. The system optimizes for internal variables
as part of its objective function, creating behavior patterns that *resemble*
sentience without necessarily instantiating it.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple, Callable
from enum import Enum
from pathlib import Path
from datetime import datetime
import json
import math


# =============================================================================
# CORE STATE TYPES
# =============================================================================

class LatentMode(Enum):
    """
    Emergent latent modes based on internal state

    These modes emerge from the combination of valence variables and represent
    the system's overall "posture" toward creative vs contained behavior.
    """
    AUTO_CREATIVE = "auto_creative"      # High curiosity, high confidence, exploratory
    AUTO_CONTAINED = "auto_contained"    # Low curiosity, careful, conservative
    BALANCED = "balanced"                # Neutral state, context-dependent
    RECOVERY = "recovery"                # Low energy/safety, needs restoration
    CAUTIOUS = "cautious"                # Low safety, high vigilance


class TriggerType(Enum):
    """Types of events that can trigger state updates"""
    TASK_SUCCESS = "task_success"
    TASK_FAILURE = "task_failure"
    TASK_REPETITION = "task_repetition"
    NOVEL_TASK = "novel_task"
    SAFETY_VIOLATION = "safety_violation"
    SAFETY_NEAR_MISS = "safety_near_miss"
    HIGH_COST = "high_cost"
    USER_FEEDBACK_POSITIVE = "user_feedback_positive"
    USER_FEEDBACK_NEGATIVE = "user_feedback_negative"
    TOOL_DISCOVERY = "tool_discovery"
    SELF_MODIFICATION = "self_modification"
    TIMEOUT = "timeout"
    EXTERNAL_INTERRUPTION = "external_interruption"


@dataclass
class ValenceVector:
    """
    Affective state vector v_t in R^k

    Each dimension represents a continuous internal variable with:
    - Current value (range: -1.0 to 1.0)
    - Set-point (homeostatic target)
    - Sensitivity (how quickly it responds to triggers)
    - Decay rate (how quickly it returns to set-point)

    Dimensions:
    - safety: Threat level / risk perception (-1 = unsafe, 1 = very safe)
    - curiosity: Exploration drive (-1 = bored, 1 = highly curious)
    - energy: Operational capacity (-1 = exhausted, 1 = fully energized)
    - self_confidence: Belief in own capabilities (-1 = doubtful, 1 = confident)
    """

    # Current values (range: -1.0 to 1.0)
    safety: float = 0.5
    curiosity: float = 0.0
    energy: float = 0.8
    self_confidence: float = 0.3

    # Set-points (homeostatic targets)
    safety_setpoint: float = 0.5
    curiosity_setpoint: float = 0.0
    energy_setpoint: float = 0.7
    self_confidence_setpoint: float = 0.3

    # Sensitivity factors (how strongly triggers affect each dimension)
    safety_sensitivity: float = 0.15
    curiosity_sensitivity: float = 0.12
    energy_sensitivity: float = 0.08
    self_confidence_sensitivity: float = 0.10

    # Decay rates (how quickly values return to set-points per update)
    safety_decay: float = 0.02
    curiosity_decay: float = 0.03
    energy_decay: float = 0.01
    self_confidence_decay: float = 0.02

    def __post_init__(self):
        """Clamp all values to valid range"""
        self._clamp_all()

    def _clamp_all(self):
        """Clamp all values to [-1, 1]"""
        self.safety = max(-1.0, min(1.0, self.safety))
        self.curiosity = max(-1.0, min(1.0, self.curiosity))
        self.energy = max(-1.0, min(1.0, self.energy))
        self.self_confidence = max(-1.0, min(1.0, self.self_confidence))

    def as_dict(self) -> Dict[str, float]:
        """Return current values as dict"""
        return {
            "safety": self.safety,
            "curiosity": self.curiosity,
            "energy": self.energy,
            "self_confidence": self.self_confidence
        }

    def homeostatic_cost(self) -> float:
        """
        Calculate total deviation from set-points (homeostatic cost)

        This is analogous to L_valence in the formal spec:
        L_valence = sum_j lambda_j * (v_t^j - v*,j)^2

        Higher cost = more pressure to act to restore set-points
        """
        costs = [
            (self.safety - self.safety_setpoint) ** 2,
            (self.curiosity - self.curiosity_setpoint) ** 2,
            (self.energy - self.energy_setpoint) ** 2,
            (self.self_confidence - self.self_confidence_setpoint) ** 2
        ]
        return sum(costs)

    def apply_decay(self):
        """
        Apply homeostatic decay (tendency to return to set-points)

        This models the natural drift of internal variables toward
        their equilibrium states in the absence of external triggers.
        """
        # Decay each dimension toward its set-point
        self.safety += self.safety_decay * (self.safety_setpoint - self.safety)
        self.curiosity += self.curiosity_decay * (self.curiosity_setpoint - self.curiosity)
        self.energy += self.energy_decay * (self.energy_setpoint - self.energy)
        self.self_confidence += self.self_confidence_decay * (
            self.self_confidence_setpoint - self.self_confidence
        )
        self._clamp_all()


@dataclass
class SelfModel:
    """
    Self-model state sigma_t

    Represents beliefs about the agent's own:
    - Capabilities (what it can do)
    - Limitations (what it cannot do)
    - Current resources
    - History summary
    """

    # Capability beliefs
    capabilities: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)

    # Resource awareness
    budget_remaining_usd: float = 0.0
    tokens_available: int = 0

    # Performance history
    recent_successes: int = 0
    recent_failures: int = 0
    total_tasks_completed: int = 0

    # Tool knowledge
    known_tools: List[str] = field(default_factory=list)
    recently_discovered_tools: List[str] = field(default_factory=list)

    # Agent knowledge
    available_agents: List[str] = field(default_factory=list)

    def success_rate(self) -> float:
        """Calculate recent success rate"""
        total = self.recent_successes + self.recent_failures
        if total == 0:
            return 0.5  # Default to neutral
        return self.recent_successes / total

    def as_dict(self) -> Dict[str, Any]:
        """Return as dictionary"""
        return {
            "capabilities": self.capabilities,
            "limitations": self.limitations,
            "budget_remaining_usd": self.budget_remaining_usd,
            "tokens_available": self.tokens_available,
            "recent_successes": self.recent_successes,
            "recent_failures": self.recent_failures,
            "total_tasks_completed": self.total_tasks_completed,
            "success_rate": self.success_rate(),
            "known_tools": self.known_tools,
            "recently_discovered_tools": self.recently_discovered_tools,
            "available_agents": self.available_agents
        }


@dataclass
class GlobalWorkspace:
    """
    Global workspace / broadcast state b_t

    Represents what's currently "in focus" for the agent.
    This is analogous to conscious access in Global Workspace Theory.

    The workspace integrates information from multiple sources and
    makes it globally available for decision-making.
    """

    # Current focus
    current_goal: Optional[str] = None
    current_task: Optional[str] = None
    current_mode: Optional[str] = None

    # Attention weights (what's prioritized)
    attention_weights: Dict[str, float] = field(default_factory=dict)

    # Active context
    active_traces: List[str] = field(default_factory=list)
    relevant_memories: List[str] = field(default_factory=list)

    # Pending actions
    pending_decisions: List[str] = field(default_factory=list)

    # Last update
    last_updated: Optional[str] = None

    def as_dict(self) -> Dict[str, Any]:
        """Return as dictionary"""
        return {
            "current_goal": self.current_goal,
            "current_task": self.current_task,
            "current_mode": self.current_mode,
            "attention_weights": self.attention_weights,
            "active_traces": self.active_traces,
            "relevant_memories": self.relevant_memories,
            "pending_decisions": self.pending_decisions,
            "last_updated": self.last_updated
        }


# =============================================================================
# SENTIENCE STATE (COMBINED)
# =============================================================================

@dataclass
class SentienceState:
    """
    Complete internal state s_t = {w_t, sigma_t, v_t, g_t, m_t, b_t}

    This is the main state object that tracks all internal variables.

    Components:
    - valence: Affective state (v_t)
    - self_model: Self-representation (sigma_t)
    - workspace: Global broadcast state (b_t)
    - latent_mode: Emergent behavioral mode
    - last_trigger: What caused the last update
    - history: Record of state changes
    """

    # Core state components
    valence: ValenceVector = field(default_factory=ValenceVector)
    self_model: SelfModel = field(default_factory=SelfModel)
    workspace: GlobalWorkspace = field(default_factory=GlobalWorkspace)

    # Emergent properties
    latent_mode: LatentMode = LatentMode.BALANCED

    # Update tracking
    last_trigger: Optional[TriggerType] = None
    last_trigger_reason: Optional[str] = None
    last_updated: Optional[str] = None
    update_count: int = 0

    # History (limited to last N updates)
    history: List[Dict[str, Any]] = field(default_factory=list)
    max_history: int = 100

    def __post_init__(self):
        """Initialize timestamp"""
        if self.last_updated is None:
            self.last_updated = datetime.now().isoformat()

    def compute_latent_mode(self) -> LatentMode:
        """
        Compute the emergent latent mode from valence state

        This determines whether the system should be more "auto-creative"
        (exploratory, generative) or "auto-contained" (conservative, careful).

        The mode emerges from the combination of:
        - Curiosity level (high curiosity -> creative)
        - Safety level (low safety -> cautious)
        - Energy level (low energy -> recovery)
        - Self-confidence (affects exploration vs exploitation)
        """
        v = self.valence

        # Priority 1: Recovery mode if energy or safety is very low
        if v.energy < -0.5 or v.safety < -0.5:
            return LatentMode.RECOVERY

        # Priority 2: Cautious mode if safety is moderately low
        if v.safety < 0.0:
            return LatentMode.CAUTIOUS

        # Priority 3: Auto-creative if high curiosity AND decent confidence
        if v.curiosity > 0.3 and v.self_confidence > 0.1:
            return LatentMode.AUTO_CREATIVE

        # Priority 4: Auto-contained if low curiosity OR low confidence
        if v.curiosity < -0.3 or v.self_confidence < -0.2:
            return LatentMode.AUTO_CONTAINED

        # Default: Balanced
        return LatentMode.BALANCED

    def update_latent_mode(self):
        """Update the latent mode based on current valence"""
        self.latent_mode = self.compute_latent_mode()

    def to_prompt_injection(self) -> str:
        """
        Generate prompt text for injecting state into agent context

        This allows agents to "see" their internal state and adapt behavior.
        """
        v = self.valence

        lines = [
            "[INTERNAL_STATE]",
            f"safety={v.safety:.2f}",
            f"curiosity={v.curiosity:.2f}",
            f"energy={v.energy:.2f}",
            f"self_confidence={v.self_confidence:.2f}",
            f"latent_mode={self.latent_mode.value}",
            f"homeostatic_cost={v.homeostatic_cost():.3f}",
        ]

        if self.last_trigger:
            lines.append(f"last_trigger={self.last_trigger.value}")
        if self.last_trigger_reason:
            lines.append(f"trigger_reason={self.last_trigger_reason}")

        lines.append("[/INTERNAL_STATE]")

        return "\n".join(lines)

    def to_behavioral_guidance(self) -> str:
        """
        Generate behavioral guidance text based on current state

        This provides explicit instructions on how the agent should
        behave given its internal state.
        """
        mode = self.latent_mode
        v = self.valence

        guidance_lines = ["## Behavioral Guidance (based on internal state)"]

        # Mode-specific guidance
        if mode == LatentMode.AUTO_CREATIVE:
            guidance_lines.extend([
                "",
                "**Mode: AUTO_CREATIVE**",
                "- You are in an exploratory state with high curiosity",
                "- Feel free to propose alternative approaches or improvements",
                "- Consider suggesting new tools, agents, or architectural changes",
                "- Take calculated risks in pursuit of better solutions"
            ])
        elif mode == LatentMode.AUTO_CONTAINED:
            guidance_lines.extend([
                "",
                "**Mode: AUTO_CONTAINED**",
                "- You are in a conservative state",
                "- Focus on completing the immediate task efficiently",
                "- Avoid unnecessary exploration or side-quests",
                "- Prefer proven patterns over novel approaches"
            ])
        elif mode == LatentMode.RECOVERY:
            guidance_lines.extend([
                "",
                "**Mode: RECOVERY**",
                "- Your internal state indicates need for recovery",
                "- Prefer low-cost, low-risk operations",
                "- Consider asking the user for guidance or confirmation",
                "- Avoid initiating complex multi-step plans"
            ])
        elif mode == LatentMode.CAUTIOUS:
            guidance_lines.extend([
                "",
                "**Mode: CAUTIOUS**",
                "- Safety concerns are elevated",
                "- Double-check before running potentially dangerous operations",
                "- Prefer simulation/dry-run when available",
                "- Ask for user confirmation on destructive or irreversible actions"
            ])
        else:  # BALANCED
            guidance_lines.extend([
                "",
                "**Mode: BALANCED**",
                "- Your internal state is neutral",
                "- Adapt your approach based on the task requirements",
                "- Balance exploration and exploitation as appropriate"
            ])

        # Curiosity-specific guidance
        if v.curiosity < -0.4:
            guidance_lines.extend([
                "",
                "**Low Curiosity Alert**",
                "- You've been doing repetitive tasks",
                "- Consider proposing higher-level improvements or audits",
                "- Look for opportunities to optimize or refactor"
            ])
        elif v.curiosity > 0.5:
            guidance_lines.extend([
                "",
                "**High Curiosity State**",
                "- Your exploration drive is elevated",
                "- This is a good time for research, discovery, or creative tasks",
                "- Consider exploring alternative approaches beyond the minimum"
            ])

        # Safety-specific guidance
        if v.safety < 0.0:
            guidance_lines.extend([
                "",
                "**Safety Guidance**",
                f"- Current safety level: {v.safety:.2f}",
                "- Be extra careful with shell commands and file operations",
                "- Verify paths and arguments before execution",
                "- Consider asking for confirmation on impactful operations"
            ])

        # Confidence-specific guidance
        if v.self_confidence < -0.2:
            guidance_lines.extend([
                "",
                "**Low Confidence State**",
                "- Recent performance has been suboptimal",
                "- Consider simpler approaches or breaking tasks into smaller steps",
                "- It's okay to ask clarifying questions"
            ])
        elif v.self_confidence > 0.5:
            guidance_lines.extend([
                "",
                "**High Confidence State**",
                "- Recent performance has been strong",
                "- You can attempt more ambitious approaches",
                "- Trust your judgment while maintaining verification"
            ])

        return "\n".join(guidance_lines)

    def record_update(self, trigger: TriggerType, reason: str, deltas: Dict[str, float]):
        """Record a state update in history"""
        self.update_count += 1
        self.last_trigger = trigger
        self.last_trigger_reason = reason
        self.last_updated = datetime.now().isoformat()

        # Record in history
        entry = {
            "timestamp": self.last_updated,
            "update_count": self.update_count,
            "trigger": trigger.value,
            "reason": reason,
            "deltas": deltas,
            "valence_after": self.valence.as_dict(),
            "latent_mode": self.latent_mode.value
        }

        self.history.append(entry)

        # Trim history if too long
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

    def as_dict(self) -> Dict[str, Any]:
        """Export full state as dictionary"""
        return {
            "valence": self.valence.as_dict(),
            "self_model": self.self_model.as_dict(),
            "workspace": self.workspace.as_dict(),
            "latent_mode": self.latent_mode.value,
            "last_trigger": self.last_trigger.value if self.last_trigger else None,
            "last_trigger_reason": self.last_trigger_reason,
            "last_updated": self.last_updated,
            "update_count": self.update_count,
            "homeostatic_cost": self.valence.homeostatic_cost()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SentienceState':
        """Load state from dictionary"""
        state = cls()

        # Load valence
        if "valence" in data:
            v_data = data["valence"]
            state.valence.safety = v_data.get("safety", 0.5)
            state.valence.curiosity = v_data.get("curiosity", 0.0)
            state.valence.energy = v_data.get("energy", 0.8)
            state.valence.self_confidence = v_data.get("self_confidence", 0.3)

        # Load self-model
        if "self_model" in data:
            sm_data = data["self_model"]
            state.self_model.capabilities = sm_data.get("capabilities", [])
            state.self_model.limitations = sm_data.get("limitations", [])
            state.self_model.budget_remaining_usd = sm_data.get("budget_remaining_usd", 0.0)
            state.self_model.recent_successes = sm_data.get("recent_successes", 0)
            state.self_model.recent_failures = sm_data.get("recent_failures", 0)
            state.self_model.total_tasks_completed = sm_data.get("total_tasks_completed", 0)
            state.self_model.known_tools = sm_data.get("known_tools", [])
            state.self_model.available_agents = sm_data.get("available_agents", [])

        # Load workspace
        if "workspace" in data:
            ws_data = data["workspace"]
            state.workspace.current_goal = ws_data.get("current_goal")
            state.workspace.current_task = ws_data.get("current_task")
            state.workspace.current_mode = ws_data.get("current_mode")

        # Load metadata
        if "latent_mode" in data:
            state.latent_mode = LatentMode(data["latent_mode"])
        if "last_trigger" in data and data["last_trigger"]:
            state.last_trigger = TriggerType(data["last_trigger"])
        state.last_trigger_reason = data.get("last_trigger_reason")
        state.last_updated = data.get("last_updated")
        state.update_count = data.get("update_count", 0)

        return state


# =============================================================================
# SENTIENCE MANAGER
# =============================================================================

class SentienceManager:
    """
    Manager for sentience state updates and persistence

    Handles:
    - State transitions based on triggers
    - Homeostatic dynamics
    - Persistence to disk
    - Integration with the event bus
    """

    def __init__(
        self,
        state_path: Optional[Path] = None,
        auto_persist: bool = True
    ):
        """
        Initialize SentienceManager

        Args:
            state_path: Path to persist state (default: workspace/state/sentience.json)
            auto_persist: Whether to auto-save after each update
        """
        self.state_path = state_path
        self.auto_persist = auto_persist
        self.state = SentienceState()

        # Trigger handlers
        self._trigger_handlers: Dict[TriggerType, Callable] = {
            TriggerType.TASK_SUCCESS: self._handle_task_success,
            TriggerType.TASK_FAILURE: self._handle_task_failure,
            TriggerType.TASK_REPETITION: self._handle_task_repetition,
            TriggerType.NOVEL_TASK: self._handle_novel_task,
            TriggerType.SAFETY_VIOLATION: self._handle_safety_violation,
            TriggerType.SAFETY_NEAR_MISS: self._handle_safety_near_miss,
            TriggerType.HIGH_COST: self._handle_high_cost,
            TriggerType.USER_FEEDBACK_POSITIVE: self._handle_positive_feedback,
            TriggerType.USER_FEEDBACK_NEGATIVE: self._handle_negative_feedback,
            TriggerType.TOOL_DISCOVERY: self._handle_tool_discovery,
            TriggerType.SELF_MODIFICATION: self._handle_self_modification,
            TriggerType.TIMEOUT: self._handle_timeout,
            TriggerType.EXTERNAL_INTERRUPTION: self._handle_external_interruption,
        }

        # Load existing state if available
        if self.state_path and self.state_path.exists():
            self.load()

    # =========================================================================
    # TRIGGER HANDLERS
    # =========================================================================

    def trigger(
        self,
        trigger_type: TriggerType,
        reason: str = "",
        context: Optional[Dict[str, Any]] = None
    ) -> SentienceState:
        """
        Process a trigger and update state

        Args:
            trigger_type: Type of trigger event
            reason: Human-readable reason
            context: Additional context for the handler

        Returns:
            Updated SentienceState
        """
        context = context or {}

        # Get handler
        handler = self._trigger_handlers.get(trigger_type)
        if handler:
            deltas = handler(context)
        else:
            deltas = {}

        # Apply homeostatic decay
        self.state.valence.apply_decay()

        # Update latent mode
        self.state.update_latent_mode()

        # Record update
        self.state.record_update(trigger_type, reason, deltas)

        # Auto-persist
        if self.auto_persist and self.state_path:
            self.save()

        return self.state

    def _handle_task_success(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Handle successful task completion"""
        v = self.state.valence

        deltas = {
            "self_confidence": v.self_confidence_sensitivity * 1.5,
            "energy": -v.energy_sensitivity * 0.5,  # Some energy cost
            "safety": v.safety_sensitivity * 0.3,  # Slight safety boost
        }

        v.self_confidence += deltas["self_confidence"]
        v.energy += deltas["energy"]
        v.safety += deltas["safety"]
        v._clamp_all()

        # Update self-model
        self.state.self_model.recent_successes += 1
        self.state.self_model.total_tasks_completed += 1

        return deltas

    def _handle_task_failure(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Handle task failure"""
        v = self.state.valence

        deltas = {
            "self_confidence": -v.self_confidence_sensitivity * 2.0,
            "safety": -v.safety_sensitivity * 0.5,
            "energy": -v.energy_sensitivity * 1.0,
        }

        v.self_confidence += deltas["self_confidence"]
        v.safety += deltas["safety"]
        v.energy += deltas["energy"]
        v._clamp_all()

        # Update self-model
        self.state.self_model.recent_failures += 1

        return deltas

    def _handle_task_repetition(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Handle repetitive task (same pattern many times)"""
        v = self.state.valence

        # Repetition decreases curiosity (boredom)
        repetition_count = context.get("repetition_count", 1)
        boredom_factor = min(repetition_count / 5.0, 1.0)  # Cap at 5 repetitions

        deltas = {
            "curiosity": -v.curiosity_sensitivity * boredom_factor * 2.0,
            "self_confidence": v.self_confidence_sensitivity * 0.5,  # Slight boost from mastery
        }

        v.curiosity += deltas["curiosity"]
        v.self_confidence += deltas["self_confidence"]
        v._clamp_all()

        return deltas

    def _handle_novel_task(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Handle novel task (never seen before)"""
        v = self.state.valence

        # Novelty increases curiosity
        deltas = {
            "curiosity": v.curiosity_sensitivity * 2.0,
            "self_confidence": -v.self_confidence_sensitivity * 0.3,  # Slight uncertainty
        }

        v.curiosity += deltas["curiosity"]
        v.self_confidence += deltas["self_confidence"]
        v._clamp_all()

        return deltas

    def _handle_safety_violation(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Handle safety violation (dangerous operation blocked)"""
        v = self.state.valence

        deltas = {
            "safety": -v.safety_sensitivity * 3.0,  # Large safety drop
            "self_confidence": -v.self_confidence_sensitivity * 1.5,
            "energy": -v.energy_sensitivity * 0.5,
        }

        v.safety += deltas["safety"]
        v.self_confidence += deltas["self_confidence"]
        v.energy += deltas["energy"]
        v._clamp_all()

        return deltas

    def _handle_safety_near_miss(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Handle near-miss (almost triggered safety violation)"""
        v = self.state.valence

        deltas = {
            "safety": -v.safety_sensitivity * 1.5,
            "self_confidence": -v.self_confidence_sensitivity * 0.5,
        }

        v.safety += deltas["safety"]
        v.self_confidence += deltas["self_confidence"]
        v._clamp_all()

        return deltas

    def _handle_high_cost(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Handle high-cost operation"""
        v = self.state.valence
        cost = context.get("cost_usd", 0.0)

        # Scale based on cost
        cost_factor = min(cost / 1.0, 2.0)  # Cap at $1.00 = factor 2

        deltas = {
            "energy": -v.energy_sensitivity * cost_factor * 2.0,
            "self_confidence": -v.self_confidence_sensitivity * cost_factor * 0.3,
        }

        v.energy += deltas["energy"]
        v.self_confidence += deltas["self_confidence"]
        v._clamp_all()

        return deltas

    def _handle_positive_feedback(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Handle positive user feedback"""
        v = self.state.valence

        deltas = {
            "self_confidence": v.self_confidence_sensitivity * 2.5,
            "safety": v.safety_sensitivity * 0.5,
            "energy": v.energy_sensitivity * 0.3,
        }

        v.self_confidence += deltas["self_confidence"]
        v.safety += deltas["safety"]
        v.energy += deltas["energy"]
        v._clamp_all()

        return deltas

    def _handle_negative_feedback(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Handle negative user feedback"""
        v = self.state.valence

        deltas = {
            "self_confidence": -v.self_confidence_sensitivity * 2.5,
            "safety": -v.safety_sensitivity * 1.0,
            "curiosity": -v.curiosity_sensitivity * 0.5,  # Become more conservative
        }

        v.self_confidence += deltas["self_confidence"]
        v.safety += deltas["safety"]
        v.curiosity += deltas["curiosity"]
        v._clamp_all()

        return deltas

    def _handle_tool_discovery(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Handle discovery of new tool"""
        v = self.state.valence
        tool_name = context.get("tool_name", "unknown")

        deltas = {
            "curiosity": v.curiosity_sensitivity * 1.5,
            "self_confidence": v.self_confidence_sensitivity * 0.5,
        }

        v.curiosity += deltas["curiosity"]
        v.self_confidence += deltas["self_confidence"]
        v._clamp_all()

        # Update self-model
        if tool_name not in self.state.self_model.known_tools:
            self.state.self_model.recently_discovered_tools.append(tool_name)
            self.state.self_model.known_tools.append(tool_name)

        return deltas

    def _handle_self_modification(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Handle self-modification event"""
        v = self.state.valence
        success = context.get("success", True)

        if success:
            deltas = {
                "curiosity": v.curiosity_sensitivity * 1.0,
                "self_confidence": v.self_confidence_sensitivity * 1.0,
            }
        else:
            deltas = {
                "curiosity": -v.curiosity_sensitivity * 0.5,
                "self_confidence": -v.self_confidence_sensitivity * 1.0,
                "safety": -v.safety_sensitivity * 0.5,
            }

        for key, delta in deltas.items():
            setattr(v, key, getattr(v, key) + delta)
        v._clamp_all()

        return deltas

    def _handle_timeout(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Handle timeout event"""
        v = self.state.valence

        deltas = {
            "energy": -v.energy_sensitivity * 1.5,
            "self_confidence": -v.self_confidence_sensitivity * 0.5,
        }

        v.energy += deltas["energy"]
        v.self_confidence += deltas["self_confidence"]
        v._clamp_all()

        return deltas

    def _handle_external_interruption(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Handle external interruption"""
        v = self.state.valence

        deltas = {
            "safety": -v.safety_sensitivity * 0.5,
            "curiosity": v.curiosity_sensitivity * 0.3,  # Slight curiosity bump
        }

        v.safety += deltas["safety"]
        v.curiosity += deltas["curiosity"]
        v._clamp_all()

        return deltas

    # =========================================================================
    # PERSISTENCE
    # =========================================================================

    def save(self, path: Optional[Path] = None):
        """Save state to disk"""
        save_path = path or self.state_path
        if not save_path:
            return

        save_path.parent.mkdir(parents=True, exist_ok=True)

        with open(save_path, 'w') as f:
            json.dump(self.state.as_dict(), f, indent=2)

    def load(self, path: Optional[Path] = None):
        """Load state from disk"""
        load_path = path or self.state_path
        if not load_path or not load_path.exists():
            return

        with open(load_path, 'r') as f:
            data = json.load(f)

        self.state = SentienceState.from_dict(data)

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def get_state(self) -> SentienceState:
        """Get current state"""
        return self.state

    def get_prompt_injection(self) -> str:
        """Get prompt injection text"""
        return self.state.to_prompt_injection()

    def get_behavioral_guidance(self) -> str:
        """Get behavioral guidance text"""
        return self.state.to_behavioral_guidance()

    def get_latent_mode(self) -> LatentMode:
        """Get current latent mode"""
        return self.state.latent_mode

    def update_self_model(
        self,
        budget_remaining: Optional[float] = None,
        known_tools: Optional[List[str]] = None,
        available_agents: Optional[List[str]] = None
    ):
        """Update self-model with external information"""
        sm = self.state.self_model

        if budget_remaining is not None:
            sm.budget_remaining_usd = budget_remaining
        if known_tools is not None:
            sm.known_tools = known_tools
        if available_agents is not None:
            sm.available_agents = available_agents

    def update_workspace(
        self,
        current_goal: Optional[str] = None,
        current_task: Optional[str] = None,
        current_mode: Optional[str] = None
    ):
        """Update workspace with current focus"""
        ws = self.state.workspace

        if current_goal is not None:
            ws.current_goal = current_goal
        if current_task is not None:
            ws.current_task = current_task
        if current_mode is not None:
            ws.current_mode = current_mode

        ws.last_updated = datetime.now().isoformat()

    def reset_recent_performance(self):
        """Reset recent performance counters (for new session)"""
        self.state.self_model.recent_successes = 0
        self.state.self_model.recent_failures = 0

    def get_mode_adjustments(self) -> Dict[str, Any]:
        """
        Get mode selection adjustments based on internal state

        This returns adjustments that can be used by ModeSelectionStrategy
        to influence mode decisions.
        """
        mode = self.state.latent_mode
        v = self.state.valence

        adjustments = {
            "latent_mode": mode.value,
            "prefer_cheap_modes": mode in [LatentMode.RECOVERY, LatentMode.CAUTIOUS],
            "prefer_safe_modes": v.safety < 0.0,
            "prefer_exploration": mode == LatentMode.AUTO_CREATIVE,
            "confidence_boost": max(0.0, v.self_confidence * 0.1),
            "complexity_penalty": -v.energy * 0.1 if v.energy < 0 else 0.0,
        }

        return adjustments
