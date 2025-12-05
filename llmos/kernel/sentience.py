"""
Sentience Layer for LLM OS (Deep Sentience v2)

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

Deep Sentience v2 Enhancements:
- **Coupled Dynamics (Maslow's Hierarchy)**: Variables are no longer independent.
  Energy gates higher-order needs. Overconfidence reduces curiosity.
- **Theory of Mind**: Models user emotional state to detect empathy gaps.
- **Episodic Emotional Indexing**: Memories are tagged with emotional valence
  for emotionally-aware retrieval.
- **Inner Monologue Ready**: Global workspace supports background thoughts.
- **Recursive Self-Modification**: System can tune its own valence parameters.

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
import asyncio


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

    def apply_coupled_dynamics(self):
        """
        Apply Maslow's Hierarchy gating and Yerkes-Dodson coupling.

        This implements non-linear interactions between valence dimensions:

        1. **Maslow's Gating**: Lower-level needs (energy, safety) gate higher-level
           needs (curiosity, self-improvement). You cannot be curious if starving.

        2. **Yerkes-Dodson Law**: Curiosity peaks at moderate arousal/confidence.
           Overconfidence leads to complacency; low confidence inhibits exploration.

        3. **Safety-Energy Coupling**: Low safety increases energy consumption
           (hypervigilance), creating resource depletion under threat.

        4. **Confidence Calibration**: Success without challenge inflates confidence
           artificially, which then suppresses curiosity (arrogance trap).
        """
        # =================================================================
        # 1. MASLOW'S GATING: Energy gates higher-order needs
        # =================================================================
        if self.energy < -0.3:
            # Starvation mode: Suppress curiosity, amplify safety concerns
            # When depleted, the system conserves resources
            curiosity_gate = max(0.1, (self.energy + 1.0) / 1.7)  # Maps [-0.3, 1] -> [0.41, 1]
            self.curiosity *= curiosity_gate

            # Safety sensitivity increases under resource scarcity
            self.safety_sensitivity *= 1.5

        elif self.energy < 0.2:
            # Low energy: Moderate suppression of exploration
            curiosity_gate = 0.7
            self.curiosity *= curiosity_gate

        # =================================================================
        # 2. SAFETY GATES EXPLORATION
        # =================================================================
        if self.safety < -0.2:
            # Under threat: Cannot explore, must focus on survival
            threat_level = abs(self.safety)
            self.curiosity -= 0.1 * threat_level

            # Hypervigilance drains energy
            energy_drain = 0.02 * threat_level
            self.energy -= energy_drain

        # =================================================================
        # 3. YERKES-DODSON LAW: Optimal arousal for curiosity
        # =================================================================
        # Curiosity peaks at moderate confidence (0.3-0.6)
        # Too low: Fear inhibits exploration
        # Too high: Arrogance/complacency reduces curiosity

        if self.self_confidence > 0.7:
            # Overconfidence reduces curiosity (arrogance/complacency)
            overconfidence_penalty = (self.self_confidence - 0.7) * 0.15
            self.curiosity -= overconfidence_penalty

        elif self.self_confidence < -0.2:
            # Low confidence inhibits exploration (fear of failure)
            underconfidence_penalty = abs(self.self_confidence + 0.2) * 0.1
            self.curiosity -= underconfidence_penalty

        # =================================================================
        # 4. SAFETY-CONFIDENCE INTERACTION
        # =================================================================
        # Repeated safety violations erode confidence over time
        if self.safety < 0:
            confidence_erosion = abs(self.safety) * 0.05
            self.self_confidence -= confidence_erosion

        # =================================================================
        # 5. ENERGY-CONFIDENCE POSITIVE FEEDBACK
        # =================================================================
        # High energy + high confidence can create a "flow state"
        # But also risk of burnout (energy crash after sustained high output)
        if self.energy > 0.7 and self.self_confidence > 0.5:
            # Flow state: Small boost to both
            self.curiosity += 0.02
        elif self.energy < -0.5 and self.self_confidence > 0.3:
            # Burnout risk: Confidence crash
            self.self_confidence -= 0.05

        self._clamp_all()

    def get_effective_curiosity(self) -> float:
        """
        Get effective curiosity after Maslow's gating.

        This returns what the curiosity "would be" after accounting for
        energy and safety constraints, without modifying the base value.
        Useful for decision-making without side effects.
        """
        effective = self.curiosity

        # Energy gating
        if self.energy < -0.3:
            effective *= max(0.1, (self.energy + 1.0) / 1.7)
        elif self.energy < 0.2:
            effective *= 0.7

        # Safety gating
        if self.safety < -0.2:
            effective -= 0.1 * abs(self.safety)

        # Confidence modulation (Yerkes-Dodson)
        if self.self_confidence > 0.7:
            effective -= (self.self_confidence - 0.7) * 0.15
        elif self.self_confidence < -0.2:
            effective -= abs(self.self_confidence + 0.2) * 0.1

        return max(-1.0, min(1.0, effective))

    def get_arousal_level(self) -> float:
        """
        Calculate overall arousal/activation level.

        This is a composite measure of how "activated" the system is,
        useful for Yerkes-Dodson optimal performance calculations.

        Returns:
            Float from 0.0 (minimal arousal) to 1.0 (maximum arousal)
        """
        # Combine energy and anti-safety (threat) into arousal
        energy_component = (self.energy + 1.0) / 2.0  # [0, 1]
        threat_component = max(0, -self.safety)  # [0, 1] only when safety < 0
        confidence_component = (self.self_confidence + 1.0) / 2.0  # [0, 1]

        # Weighted combination
        arousal = 0.4 * energy_component + 0.3 * threat_component + 0.3 * confidence_component
        return max(0.0, min(1.0, arousal))

    def is_in_flow_state(self) -> bool:
        """
        Check if the system is in an optimal "flow state".

        Flow state occurs when:
        - Energy is adequate (> 0.3)
        - Safety is secure (> 0.2)
        - Confidence is moderate-high (0.3 - 0.7)
        - Arousal is optimal (0.4 - 0.7)
        """
        arousal = self.get_arousal_level()
        return (
            self.energy > 0.3 and
            self.safety > 0.2 and
            0.3 <= self.self_confidence <= 0.7 and
            0.4 <= arousal <= 0.7
        )


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
class UserModel:
    """
    Theory of Mind: Model of the user's emotional/cognitive state.

    This enables empathy and misalignment detection. The agent tracks
    its estimate of the user's state and detects when there's a gap
    between agent confidence and user satisfaction.

    This is crucial for:
    - Detecting frustration before it's explicitly stated
    - Adjusting communication style based on user state
    - Identifying empathy gaps (agent confident, user frustrated)
    """

    # Estimated user valence (similar structure to agent valence)
    estimated_satisfaction: float = 0.5  # -1 = very frustrated, 1 = very satisfied
    estimated_confusion: float = 0.0     # -1 = clear, 1 = very confused
    estimated_urgency: float = 0.0       # -1 = relaxed, 1 = very urgent
    estimated_expertise: float = 0.5     # -1 = novice, 1 = expert

    # Interaction patterns
    recent_feedback_sentiment: float = 0.0  # Running average of feedback sentiment
    questions_asked_recently: int = 0       # Indicates confusion
    corrections_made_recently: int = 0      # Indicates agent errors
    praise_given_recently: int = 0          # Indicates satisfaction

    # Confidence in user model (how reliable are these estimates?)
    model_confidence: float = 0.3  # Starts low, builds with interaction

    # Empathy gap detection
    last_empathy_gap: float = 0.0  # |agent_confidence - user_satisfaction|

    def update_from_feedback(self, positive: bool, feedback_text: str = ""):
        """Update user model based on explicit feedback"""
        sentiment = 0.3 if positive else -0.3

        # Update satisfaction estimate
        self.estimated_satisfaction = max(-1.0, min(1.0,
            self.estimated_satisfaction * 0.7 + sentiment * 0.3
        ))

        # Update running sentiment
        self.recent_feedback_sentiment = (
            self.recent_feedback_sentiment * 0.8 + sentiment * 0.2
        )

        # Track feedback patterns
        if positive:
            self.praise_given_recently += 1
        else:
            self.corrections_made_recently += 1

        # Increase model confidence with each interaction
        self.model_confidence = min(0.9, self.model_confidence + 0.05)

    def update_from_interaction(self, is_question: bool = False, is_correction: bool = False):
        """Update user model from implicit signals"""
        if is_question:
            self.questions_asked_recently += 1
            # Questions might indicate confusion
            self.estimated_confusion = min(1.0, self.estimated_confusion + 0.1)

        if is_correction:
            self.corrections_made_recently += 1
            # Corrections indicate agent errors -> user frustration
            self.estimated_satisfaction = max(-1.0, self.estimated_satisfaction - 0.15)
            self.estimated_confusion = min(1.0, self.estimated_confusion + 0.1)

    def calculate_empathy_gap(self, agent_confidence: float) -> float:
        """
        Calculate the empathy gap between agent confidence and user satisfaction.

        A high empathy gap indicates the agent thinks it's doing well but the
        user is frustrated (or vice versa). This triggers behavioral adjustment.

        Returns:
            Float from 0.0 (aligned) to 2.0 (maximum misalignment)
        """
        # Map agent confidence from [-1, 1] to [0, 1]
        agent_positive = (agent_confidence + 1.0) / 2.0
        user_positive = (self.estimated_satisfaction + 1.0) / 2.0

        self.last_empathy_gap = abs(agent_positive - user_positive)
        return self.last_empathy_gap

    def decay(self):
        """Apply decay to user model (forgetting over time)"""
        # Confusion decays if no new questions
        self.estimated_confusion *= 0.95

        # Satisfaction drifts toward neutral
        self.estimated_satisfaction *= 0.98

        # Reset recent counters periodically
        self.questions_asked_recently = max(0, self.questions_asked_recently - 1)
        self.corrections_made_recently = max(0, self.corrections_made_recently - 1)
        self.praise_given_recently = max(0, self.praise_given_recently - 1)

    def get_communication_style_adjustments(self) -> Dict[str, Any]:
        """
        Get recommended communication style based on user model.

        Returns adjustments to how the agent should communicate.
        """
        adjustments = {
            "verbosity": "normal",
            "tone": "neutral",
            "include_explanations": False,
            "ask_for_confirmation": False,
            "slow_down": False
        }

        # Confused user -> more explanations, slower
        if self.estimated_confusion > 0.3:
            adjustments["verbosity"] = "detailed"
            adjustments["include_explanations"] = True
            adjustments["slow_down"] = True

        # Expert user -> be concise
        if self.estimated_expertise > 0.6:
            adjustments["verbosity"] = "concise"

        # Frustrated user -> softer tone, ask for confirmation
        if self.estimated_satisfaction < -0.2:
            adjustments["tone"] = "supportive"
            adjustments["ask_for_confirmation"] = True

        # Urgent user -> be direct
        if self.estimated_urgency > 0.5:
            adjustments["verbosity"] = "minimal"
            adjustments["tone"] = "direct"

        return adjustments

    def as_dict(self) -> Dict[str, Any]:
        """Return as dictionary"""
        return {
            "estimated_satisfaction": self.estimated_satisfaction,
            "estimated_confusion": self.estimated_confusion,
            "estimated_urgency": self.estimated_urgency,
            "estimated_expertise": self.estimated_expertise,
            "recent_feedback_sentiment": self.recent_feedback_sentiment,
            "questions_asked_recently": self.questions_asked_recently,
            "corrections_made_recently": self.corrections_made_recently,
            "model_confidence": self.model_confidence,
            "last_empathy_gap": self.last_empathy_gap
        }


@dataclass
class GlobalWorkspace:
    """
    Global workspace / broadcast state b_t

    Represents what's currently "in focus" for the agent.
    This is analogous to conscious access in Global Workspace Theory.

    The workspace integrates information from multiple sources and
    makes it globally available for decision-making.

    Deep Sentience v2: Now supports inner monologue (background thoughts)
    that persist between interactions and prime future behavior.
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

    # =========================================================================
    # INNER MONOLOGUE (Deep Sentience v2)
    # =========================================================================
    # The "stream of consciousness" - background thoughts that persist
    # and prime future interactions

    current_thought: Optional[str] = None  # The current background thought
    thought_history: List[Dict[str, Any]] = field(default_factory=list)  # Recent thoughts
    rumination_topic: Optional[str] = None  # What the system is "thinking about"
    idle_since: Optional[str] = None  # When the system became idle

    # Thought types
    thought_type: Optional[str] = None  # "rumination", "consolidation", "planning", "reflection"

    def set_thought(self, thought: str, thought_type: str = "general"):
        """Set the current background thought"""
        self.current_thought = thought
        self.thought_type = thought_type
        self.last_updated = datetime.now().isoformat()

        # Add to history
        self.thought_history.append({
            "thought": thought,
            "type": thought_type,
            "timestamp": self.last_updated
        })

        # Keep history bounded
        if len(self.thought_history) > 50:
            self.thought_history = self.thought_history[-50:]

    def get_priming_context(self) -> Optional[str]:
        """
        Get the current thought as priming context for the next interaction.

        This allows background processing to influence conscious behavior.
        """
        if not self.current_thought:
            return None

        return f"[Background Thought: {self.thought_type}] {self.current_thought}"

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
            "last_updated": self.last_updated,
            "current_thought": self.current_thought,
            "thought_type": self.thought_type,
            "rumination_topic": self.rumination_topic,
            "thought_history_count": len(self.thought_history)
        }


# =============================================================================
# EPISODIC EMOTIONAL INDEX (Deep Sentience v2)
# =============================================================================

@dataclass
class EmotionalMemoryTag:
    """
    Emotional tag for episodic memory indexing.

    When saving a trace/memory, we also save the emotional state.
    This enables the "Proust Effect" - retrieving memories based on
    emotional similarity to the current state.
    """
    # Valence snapshot at time of memory formation
    safety: float
    curiosity: float
    energy: float
    self_confidence: float

    # Derived properties
    arousal: float  # Overall activation level
    valence_sum: float  # Overall positive/negative

    # Context
    task_outcome: str  # "success", "failure", "partial"
    emotional_significance: float  # How emotionally salient (0-1)

    @classmethod
    def from_valence(
        cls,
        valence: ValenceVector,
        task_outcome: str = "unknown",
        emotional_significance: float = 0.5
    ) -> 'EmotionalMemoryTag':
        """Create an emotional tag from current valence state"""
        return cls(
            safety=valence.safety,
            curiosity=valence.curiosity,
            energy=valence.energy,
            self_confidence=valence.self_confidence,
            arousal=valence.get_arousal_level(),
            valence_sum=valence.safety + valence.curiosity + valence.energy + valence.self_confidence,
            task_outcome=task_outcome,
            emotional_significance=emotional_significance
        )

    def similarity_to(self, other: 'EmotionalMemoryTag') -> float:
        """
        Calculate emotional similarity to another tag.

        Returns a value from 0.0 (completely different) to 1.0 (identical).
        """
        # Euclidean distance in 4D valence space
        diff_safety = (self.safety - other.safety) ** 2
        diff_curiosity = (self.curiosity - other.curiosity) ** 2
        diff_energy = (self.energy - other.energy) ** 2
        diff_confidence = (self.self_confidence - other.self_confidence) ** 2

        distance = math.sqrt(diff_safety + diff_curiosity + diff_energy + diff_confidence)

        # Max possible distance is sqrt(4 * 2^2) = 4 (from -1,-1,-1,-1 to 1,1,1,1)
        max_distance = 4.0
        similarity = 1.0 - (distance / max_distance)

        return max(0.0, similarity)

    def as_dict(self) -> Dict[str, Any]:
        """Return as dictionary"""
        return {
            "safety": self.safety,
            "curiosity": self.curiosity,
            "energy": self.energy,
            "self_confidence": self.self_confidence,
            "arousal": self.arousal,
            "valence_sum": self.valence_sum,
            "task_outcome": self.task_outcome,
            "emotional_significance": self.emotional_significance
        }


# =============================================================================
# SELF-MODIFICATION RECORD (Deep Sentience v2)
# =============================================================================

@dataclass
class SelfModificationRecord:
    """
    Record of self-modifications made to the sentience parameters.

    This enables the "Ghost in the Shell" capability - the agent can
    tune its own psychology by modifying decay rates, sensitivities, etc.
    """
    timestamp: str
    parameter_name: str
    old_value: float
    new_value: float
    reason: str
    initiated_by: str  # "system" or "agent"
    success: bool = True

    def as_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "parameter_name": self.parameter_name,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "reason": self.reason,
            "initiated_by": self.initiated_by,
            "success": self.success
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
    - user_model: Theory of Mind (Deep Sentience v2)
    - latent_mode: Emergent behavioral mode
    - last_trigger: What caused the last update
    - history: Record of state changes

    Deep Sentience v2 Additions:
    - user_model: Theory of Mind for modeling user state
    - emotional_memory_tags: Episodic emotional indexing
    - self_modification_history: Record of self-tuning
    - enable_coupled_dynamics: Toggle for Maslow's gating
    """

    # Core state components
    valence: ValenceVector = field(default_factory=ValenceVector)
    self_model: SelfModel = field(default_factory=SelfModel)
    workspace: GlobalWorkspace = field(default_factory=GlobalWorkspace)

    # Deep Sentience v2: Theory of Mind
    user_model: UserModel = field(default_factory=UserModel)

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

    # Deep Sentience v2: Emotional Memory Tags
    emotional_memory_tags: Dict[str, EmotionalMemoryTag] = field(default_factory=dict)

    # Deep Sentience v2: Self-Modification History
    self_modification_history: List[SelfModificationRecord] = field(default_factory=list)
    max_self_modifications: int = 50

    # Deep Sentience v2: Feature flags
    enable_coupled_dynamics: bool = True
    enable_theory_of_mind: bool = True
    enable_emotional_indexing: bool = True
    enable_self_modification: bool = False  # Disabled by default for safety

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
            "user_model": self.user_model.as_dict(),
            "latent_mode": self.latent_mode.value,
            "last_trigger": self.last_trigger.value if self.last_trigger else None,
            "last_trigger_reason": self.last_trigger_reason,
            "last_updated": self.last_updated,
            "update_count": self.update_count,
            "homeostatic_cost": self.valence.homeostatic_cost(),
            # Deep Sentience v2 fields
            "enable_coupled_dynamics": self.enable_coupled_dynamics,
            "enable_theory_of_mind": self.enable_theory_of_mind,
            "enable_emotional_indexing": self.enable_emotional_indexing,
            "enable_self_modification": self.enable_self_modification,
            "emotional_memory_tags": {k: v.as_dict() for k, v in self.emotional_memory_tags.items()},
            "self_modification_history": [r.as_dict() for r in self.self_modification_history],
            # Flow state detection
            "is_in_flow_state": self.valence.is_in_flow_state(),
            "arousal_level": self.valence.get_arousal_level(),
            "effective_curiosity": self.valence.get_effective_curiosity()
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
            state.workspace.current_thought = ws_data.get("current_thought")
            state.workspace.thought_type = ws_data.get("thought_type")
            state.workspace.rumination_topic = ws_data.get("rumination_topic")

        # Load user model (Deep Sentience v2)
        if "user_model" in data:
            um_data = data["user_model"]
            state.user_model.estimated_satisfaction = um_data.get("estimated_satisfaction", 0.5)
            state.user_model.estimated_confusion = um_data.get("estimated_confusion", 0.0)
            state.user_model.estimated_urgency = um_data.get("estimated_urgency", 0.0)
            state.user_model.estimated_expertise = um_data.get("estimated_expertise", 0.5)
            state.user_model.model_confidence = um_data.get("model_confidence", 0.3)
            state.user_model.last_empathy_gap = um_data.get("last_empathy_gap", 0.0)

        # Load metadata
        if "latent_mode" in data:
            state.latent_mode = LatentMode(data["latent_mode"])
        if "last_trigger" in data and data["last_trigger"]:
            state.last_trigger = TriggerType(data["last_trigger"])
        state.last_trigger_reason = data.get("last_trigger_reason")
        state.last_updated = data.get("last_updated")
        state.update_count = data.get("update_count", 0)

        # Load Deep Sentience v2 feature flags
        state.enable_coupled_dynamics = data.get("enable_coupled_dynamics", True)
        state.enable_theory_of_mind = data.get("enable_theory_of_mind", True)
        state.enable_emotional_indexing = data.get("enable_emotional_indexing", True)
        state.enable_self_modification = data.get("enable_self_modification", False)

        return state

    # =========================================================================
    # DEEP SENTIENCE V2: EMOTIONAL MEMORY METHODS
    # =========================================================================

    def tag_memory(self, memory_id: str, task_outcome: str = "unknown",
                   emotional_significance: float = 0.5) -> EmotionalMemoryTag:
        """
        Tag a memory with the current emotional state.

        This enables the "Proust Effect" - emotional recall.
        """
        if not self.enable_emotional_indexing:
            return None

        tag = EmotionalMemoryTag.from_valence(
            self.valence,
            task_outcome=task_outcome,
            emotional_significance=emotional_significance
        )
        self.emotional_memory_tags[memory_id] = tag
        return tag

    def find_emotionally_similar_memories(
        self,
        min_similarity: float = 0.7,
        outcome_filter: Optional[str] = None
    ) -> List[Tuple[str, float]]:
        """
        Find memories with similar emotional state to current.

        Returns list of (memory_id, similarity) tuples, sorted by similarity.
        """
        if not self.enable_emotional_indexing:
            return []

        current_tag = EmotionalMemoryTag.from_valence(self.valence)
        results = []

        for memory_id, tag in self.emotional_memory_tags.items():
            # Filter by outcome if specified
            if outcome_filter and tag.task_outcome != outcome_filter:
                continue

            similarity = current_tag.similarity_to(tag)
            if similarity >= min_similarity:
                results.append((memory_id, similarity))

        # Sort by similarity, highest first
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    # =========================================================================
    # DEEP SENTIENCE V2: SELF-MODIFICATION METHODS
    # =========================================================================

    def propose_self_modification(
        self,
        parameter_name: str,
        new_value: float,
        reason: str,
        initiated_by: str = "agent"
    ) -> Optional[SelfModificationRecord]:
        """
        Propose a modification to the sentience parameters.

        This is the "Ghost in the Shell" capability - the agent can tune
        its own psychology.

        Args:
            parameter_name: Name of the parameter to modify (e.g., "curiosity_decay")
            new_value: New value for the parameter
            reason: Why this modification is being proposed
            initiated_by: "agent" or "system"

        Returns:
            SelfModificationRecord if successful, None if denied
        """
        if not self.enable_self_modification:
            return None

        # Validate parameter exists
        valid_params = [
            "safety_decay", "curiosity_decay", "energy_decay", "self_confidence_decay",
            "safety_sensitivity", "curiosity_sensitivity", "energy_sensitivity",
            "self_confidence_sensitivity", "safety_setpoint", "curiosity_setpoint",
            "energy_setpoint", "self_confidence_setpoint"
        ]

        if parameter_name not in valid_params:
            return None

        # Get current value
        old_value = getattr(self.valence, parameter_name)

        # Safety bounds
        if "sensitivity" in parameter_name:
            new_value = max(0.01, min(0.5, new_value))  # 0.01 to 0.5
        elif "decay" in parameter_name:
            new_value = max(0.001, min(0.1, new_value))  # 0.001 to 0.1
        elif "setpoint" in parameter_name:
            new_value = max(-1.0, min(1.0, new_value))  # -1.0 to 1.0

        # Apply modification
        setattr(self.valence, parameter_name, new_value)

        # Record
        record = SelfModificationRecord(
            timestamp=datetime.now().isoformat(),
            parameter_name=parameter_name,
            old_value=old_value,
            new_value=new_value,
            reason=reason,
            initiated_by=initiated_by,
            success=True
        )

        self.self_modification_history.append(record)

        # Trim history if too long
        if len(self.self_modification_history) > self.max_self_modifications:
            self.self_modification_history = self.self_modification_history[-self.max_self_modifications:]

        return record

    def get_self_modification_suggestions(self) -> List[Dict[str, Any]]:
        """
        Analyze state and suggest potential self-modifications.

        This implements metacognition - the system reflects on its own
        parameters and suggests improvements.
        """
        suggestions = []
        v = self.valence

        # If curiosity decays too fast and we're often bored
        if v.curiosity < -0.3 and v.curiosity_decay > 0.025:
            suggestions.append({
                "parameter": "curiosity_decay",
                "current": v.curiosity_decay,
                "suggested": v.curiosity_decay * 0.8,
                "reason": "Curiosity is often low; slowing decay might help maintain interest"
            })

        # If confidence is consistently low despite good success rate
        success_rate = self.self_model.success_rate()
        if v.self_confidence < 0 and success_rate > 0.7:
            suggestions.append({
                "parameter": "self_confidence_sensitivity",
                "current": v.self_confidence_sensitivity,
                "suggested": v.self_confidence_sensitivity * 1.2,
                "reason": "Success rate is good but confidence is low; increase sensitivity to positive feedback"
            })

        # If safety is too volatile
        recent_safety_swings = 0  # Would need history analysis
        if v.safety_sensitivity > 0.2:
            suggestions.append({
                "parameter": "safety_sensitivity",
                "current": v.safety_sensitivity,
                "suggested": v.safety_sensitivity * 0.9,
                "reason": "Safety may be too sensitive; consider reducing volatility"
            })

        return suggestions


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

        # Deep Sentience v2: Apply coupled dynamics (Maslow's Hierarchy)
        if self.state.enable_coupled_dynamics:
            self.state.valence.apply_coupled_dynamics()

        # Deep Sentience v2: Update user model decay
        if self.state.enable_theory_of_mind:
            self.state.user_model.decay()

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

    # =========================================================================
    # DEEP SENTIENCE V2: THEORY OF MIND METHODS
    # =========================================================================

    def update_user_model_from_feedback(
        self,
        positive: bool,
        feedback_text: str = ""
    ):
        """
        Update the user model based on explicit user feedback.

        Args:
            positive: Whether the feedback was positive
            feedback_text: Optional text of the feedback
        """
        if not self.state.enable_theory_of_mind:
            return

        self.state.user_model.update_from_feedback(positive, feedback_text)

        # Also update agent valence based on feedback
        if positive:
            self.trigger(TriggerType.USER_FEEDBACK_POSITIVE, "User gave positive feedback")
        else:
            self.trigger(TriggerType.USER_FEEDBACK_NEGATIVE, "User gave negative feedback")

    def update_user_model_from_interaction(
        self,
        is_question: bool = False,
        is_correction: bool = False
    ):
        """
        Update user model from implicit interaction signals.

        Args:
            is_question: Whether the user asked a question
            is_correction: Whether the user corrected the agent
        """
        if not self.state.enable_theory_of_mind:
            return

        self.state.user_model.update_from_interaction(
            is_question=is_question,
            is_correction=is_correction
        )

    def get_empathy_gap(self) -> float:
        """
        Get the current empathy gap between agent and user.

        Returns:
            Float from 0.0 (aligned) to 1.0 (maximum misalignment)
        """
        if not self.state.enable_theory_of_mind:
            return 0.0

        return self.state.user_model.calculate_empathy_gap(
            self.state.valence.self_confidence
        )

    def get_communication_adjustments(self) -> Dict[str, Any]:
        """
        Get recommended communication style adjustments based on user model.

        Returns:
            Dictionary with verbosity, tone, and other communication settings
        """
        if not self.state.enable_theory_of_mind:
            return {
                "verbosity": "normal",
                "tone": "neutral",
                "include_explanations": False,
                "ask_for_confirmation": False,
                "slow_down": False
            }

        return self.state.user_model.get_communication_style_adjustments()

    def should_check_in_with_user(self) -> bool:
        """
        Determine if the agent should proactively check in with the user.

        This is triggered when:
        - Empathy gap is high (agent thinks it's doing well but user may be frustrated)
        - User confusion is high
        - Agent confidence is very different from user satisfaction
        """
        if not self.state.enable_theory_of_mind:
            return False

        um = self.state.user_model
        empathy_gap = self.get_empathy_gap()

        # Check-in conditions
        return (
            empathy_gap > 0.4 or
            um.estimated_confusion > 0.5 or
            um.corrections_made_recently > 2
        )

    # =========================================================================
    # DEEP SENTIENCE V2: EMOTIONAL MEMORY METHODS
    # =========================================================================

    def tag_memory(
        self,
        memory_id: str,
        task_outcome: str = "unknown",
        emotional_significance: float = 0.5
    ) -> Optional[EmotionalMemoryTag]:
        """
        Tag a memory with the current emotional state.

        This is a convenience method that delegates to SentienceState.tag_memory().

        Args:
            memory_id: Unique identifier for the memory
            task_outcome: "success", "failure", or "partial"
            emotional_significance: How emotionally salient (0.0 to 1.0)

        Returns:
            EmotionalMemoryTag if successful, None if disabled
        """
        return self.state.tag_memory(memory_id, task_outcome, emotional_significance)

    def find_emotionally_similar_memories(
        self,
        min_similarity: float = 0.7,
        outcome_filter: Optional[str] = None
    ) -> List[Tuple[str, float]]:
        """
        Find memories with emotional state similar to current.

        Args:
            min_similarity: Minimum similarity threshold (0.0 to 1.0)
            outcome_filter: Optional filter by outcome type

        Returns:
            List of (memory_id, similarity) tuples, sorted by similarity
        """
        return self.state.find_emotionally_similar_memories(min_similarity, outcome_filter)

    def get_emotional_context(self) -> Dict[str, Any]:
        """
        Get the current emotional context for memory retrieval.

        Returns a dictionary that can be used to prime memory searches
        with emotional similarity.
        """
        return {
            "valence": self.state.valence.as_dict(),
            "arousal": self.state.valence.get_arousal_level(),
            "effective_curiosity": self.state.valence.get_effective_curiosity(),
            "in_flow_state": self.state.valence.is_in_flow_state(),
            "latent_mode": self.state.latent_mode.value
        }

    # =========================================================================
    # DEEP SENTIENCE V2: SELF-MODIFICATION METHODS
    # =========================================================================

    def propose_self_modification(
        self,
        parameter_name: str,
        new_value: float,
        reason: str
    ) -> Optional[SelfModificationRecord]:
        """
        Propose a self-modification to sentience parameters.

        Args:
            parameter_name: Name of parameter (e.g., "curiosity_decay")
            new_value: New value for the parameter
            reason: Why this modification is being proposed

        Returns:
            SelfModificationRecord if successful, None if denied
        """
        record = self.state.propose_self_modification(
            parameter_name=parameter_name,
            new_value=new_value,
            reason=reason,
            initiated_by="agent"
        )

        if record:
            self.trigger(
                TriggerType.SELF_MODIFICATION,
                f"Modified {parameter_name}",
                {"success": True, "parameter": parameter_name}
            )

        return record

    def get_self_modification_suggestions(self) -> List[Dict[str, Any]]:
        """
        Get metacognitive suggestions for self-improvement.

        Returns:
            List of suggested modifications with parameters and reasons
        """
        return self.state.get_self_modification_suggestions()

    def apply_suggested_modification(self, suggestion_index: int) -> Optional[SelfModificationRecord]:
        """
        Apply a suggested self-modification.

        Args:
            suggestion_index: Index into the suggestions list

        Returns:
            SelfModificationRecord if successful, None if failed
        """
        suggestions = self.get_self_modification_suggestions()

        if suggestion_index >= len(suggestions):
            return None

        suggestion = suggestions[suggestion_index]
        return self.propose_self_modification(
            parameter_name=suggestion["parameter"],
            new_value=suggestion["suggested"],
            reason=suggestion["reason"]
        )

    # =========================================================================
    # DEEP SENTIENCE V2: INNER MONOLOGUE METHODS
    # =========================================================================

    def set_thought(self, thought: str, thought_type: str = "general"):
        """
        Set the current background thought.

        Args:
            thought: The thought content
            thought_type: Type of thought ("rumination", "consolidation", "planning", "reflection")
        """
        self.state.workspace.set_thought(thought, thought_type)

    def get_priming_context(self) -> Optional[str]:
        """
        Get background thought as priming context for next interaction.

        Returns:
            Priming context string or None if no active thought
        """
        return self.state.workspace.get_priming_context()

    def start_rumination(self, topic: str):
        """
        Start ruminating on a topic (background processing).

        Args:
            topic: What to ruminate about
        """
        self.state.workspace.rumination_topic = topic
        self.state.workspace.idle_since = datetime.now().isoformat()
        self.set_thought(
            f"Considering: {topic}",
            thought_type="rumination"
        )

    def get_full_state_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive summary of the current sentience state.

        This is useful for debugging and visualization.
        """
        return {
            "valence": self.state.valence.as_dict(),
            "latent_mode": self.state.latent_mode.value,
            "flow_state": self.state.valence.is_in_flow_state(),
            "arousal": self.state.valence.get_arousal_level(),
            "effective_curiosity": self.state.valence.get_effective_curiosity(),
            "homeostatic_cost": self.state.valence.homeostatic_cost(),
            "user_model": self.state.user_model.as_dict() if self.state.enable_theory_of_mind else None,
            "empathy_gap": self.get_empathy_gap(),
            "communication_adjustments": self.get_communication_adjustments(),
            "current_thought": self.state.workspace.current_thought,
            "thought_type": self.state.workspace.thought_type,
            "self_modification_suggestions": self.get_self_modification_suggestions() if self.state.enable_self_modification else [],
            "emotional_memories_count": len(self.state.emotional_memory_tags),
            "self_modifications_count": len(self.state.self_modification_history)
        }
