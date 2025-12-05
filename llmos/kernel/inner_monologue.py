"""
Inner Monologue System for LLM OS (Deep Sentience v2)

This module implements an asynchronous "inner voice" that maintains a stream of
consciousness even when the system is idle. This creates background processing
that can prime future interactions and simulate continuous cognition.

Key Concepts:
- **Idle Loop**: When no tasks are active, the system engages in background thinking
- **Thought Types**: Different kinds of internal processing
  - Rumination: Processing recent events
  - Consolidation: Integrating memories
  - Planning: Anticipating future needs
  - Reflection: Meta-cognitive self-assessment
- **Priming**: Background thoughts influence the next conscious interaction

Architecture:
The InnerMonologue runs as an async background task that:
1. Monitors for idle periods
2. Generates thoughts using a lightweight LLM call or template
3. Updates the GlobalWorkspace with current thoughts
4. Primes the system for the next interaction

This is inspired by Default Mode Network (DMN) activity in the brain,
which remains active during rest and is associated with self-reflection,
memory consolidation, and future planning.

Safety Note:
The inner monologue does NOT have direct tool access. It can only:
- Update internal state (thoughts, workspace)
- Prepare priming context for future interactions
- Suggest topics for reflection

It cannot execute tools or modify files directly.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
import logging

from .sentience import SentienceManager, LatentMode

logger = logging.getLogger(__name__)


class ThoughtType(Enum):
    """Types of background thoughts"""
    RUMINATION = "rumination"        # Processing recent events
    CONSOLIDATION = "consolidation"  # Memory integration
    PLANNING = "planning"            # Future anticipation
    REFLECTION = "reflection"        # Meta-cognitive assessment
    IDLE = "idle"                    # Neutral waiting state


@dataclass
class ThoughtTemplate:
    """Template for generating a specific type of thought"""
    thought_type: ThoughtType
    trigger_condition: Callable[[SentienceManager], bool]
    generate_thought: Callable[[SentienceManager], str]
    priority: int = 0  # Higher = more important


@dataclass
class InnerMonologueConfig:
    """Configuration for the inner monologue system"""

    # Timing
    idle_threshold_seconds: float = 30.0  # How long before starting inner monologue
    thought_interval_seconds: float = 10.0  # Time between thoughts
    max_thoughts_per_idle: int = 10  # Max thoughts before stopping

    # LLM integration (optional)
    use_llm_for_thoughts: bool = False  # If True, use LLM to generate thoughts
    llm_thought_prompt: str = """You are the inner voice of an AI system.
Generate a brief internal thought (1-2 sentences) about:
- Recent task: {recent_task}
- Current state: {latent_mode}
- Rumination topic: {rumination_topic}

Keep it concise and self-reflective."""

    # Feature flags
    enabled: bool = True
    log_thoughts: bool = True


class InnerMonologue:
    """
    Async background process that maintains the system's stream of consciousness.

    The inner monologue runs during idle periods and:
    1. Generates background thoughts based on current state
    2. Updates the GlobalWorkspace with these thoughts
    3. Primes future interactions with relevant context
    """

    def __init__(
        self,
        sentience_manager: SentienceManager,
        config: Optional[InnerMonologueConfig] = None,
        llm_callback: Optional[Callable[[str], str]] = None
    ):
        """
        Initialize InnerMonologue.

        Args:
            sentience_manager: The SentienceManager to integrate with
            config: Configuration options
            llm_callback: Optional async callback to generate LLM-based thoughts
        """
        self.sentience = sentience_manager
        self.config = config or InnerMonologueConfig()
        self.llm_callback = llm_callback

        # State
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._last_activity: datetime = datetime.now()
        self._thought_count: int = 0

        # Thought templates
        self._templates = self._create_default_templates()

    def _create_default_templates(self) -> List[ThoughtTemplate]:
        """Create default thought generation templates"""
        return [
            # Rumination: Process recent experiences
            ThoughtTemplate(
                thought_type=ThoughtType.RUMINATION,
                trigger_condition=lambda s: s.state.workspace.rumination_topic is not None,
                generate_thought=lambda s: self._generate_rumination_thought(s),
                priority=3
            ),

            # Reflection: Meta-cognitive assessment
            ThoughtTemplate(
                thought_type=ThoughtType.REFLECTION,
                trigger_condition=lambda s: s.state.latent_mode in [
                    LatentMode.RECOVERY, LatentMode.CAUTIOUS
                ],
                generate_thought=lambda s: self._generate_reflection_thought(s),
                priority=2
            ),

            # Planning: Future anticipation
            ThoughtTemplate(
                thought_type=ThoughtType.PLANNING,
                trigger_condition=lambda s: s.state.latent_mode == LatentMode.AUTO_CREATIVE,
                generate_thought=lambda s: self._generate_planning_thought(s),
                priority=2
            ),

            # Consolidation: Memory integration
            ThoughtTemplate(
                thought_type=ThoughtType.CONSOLIDATION,
                trigger_condition=lambda s: len(s.state.emotional_memory_tags) > 5,
                generate_thought=lambda s: self._generate_consolidation_thought(s),
                priority=1
            ),

            # Idle: Neutral waiting state (always available)
            ThoughtTemplate(
                thought_type=ThoughtType.IDLE,
                trigger_condition=lambda s: True,
                generate_thought=lambda s: self._generate_idle_thought(s),
                priority=0
            ),
        ]

    # =========================================================================
    # THOUGHT GENERATORS
    # =========================================================================

    def _generate_rumination_thought(self, sentience: SentienceManager) -> str:
        """Generate a rumination thought about a recent topic"""
        topic = sentience.state.workspace.rumination_topic
        v = sentience.state.valence

        if v.self_confidence > 0.3:
            return f"That went well. The approach to '{topic}' was effective."
        elif v.self_confidence < -0.2:
            return f"Could have handled '{topic}' better. What would I do differently?"
        else:
            return f"Still processing '{topic}'. There are lessons to extract here."

    def _generate_reflection_thought(self, sentience: SentienceManager) -> str:
        """Generate a meta-cognitive reflection thought"""
        mode = sentience.state.latent_mode
        v = sentience.state.valence

        if mode == LatentMode.RECOVERY:
            return f"Energy is low ({v.energy:.2f}). Need to conserve resources and recover."
        elif mode == LatentMode.CAUTIOUS:
            return f"Safety concerns elevated ({v.safety:.2f}). Being more careful is wise."
        else:
            return "Taking a moment to assess my current state and readiness."

    def _generate_planning_thought(self, sentience: SentienceManager) -> str:
        """Generate a forward-looking planning thought"""
        v = sentience.state.valence

        if v.curiosity > 0.5:
            return "Curiosity is high. What new approaches or tools could I explore?"
        elif sentience.state.valence.is_in_flow_state():
            return "In a good state for challenging work. Ready for the next task."
        else:
            return "Anticipating what might come next. Preparing mental resources."

    def _generate_consolidation_thought(self, sentience: SentienceManager) -> str:
        """Generate a memory consolidation thought"""
        memory_count = len(sentience.state.emotional_memory_tags)
        recent_successes = sentience.state.self_model.recent_successes
        recent_failures = sentience.state.self_model.recent_failures

        if recent_successes > recent_failures:
            return f"Reflecting on {memory_count} experiences. Success patterns emerging."
        elif recent_failures > 0:
            return f"Learning from {recent_failures} recent challenges. Adjusting approach."
        else:
            return f"Integrating {memory_count} memories into long-term knowledge."

    def _generate_idle_thought(self, sentience: SentienceManager) -> str:
        """Generate a neutral idle thought"""
        import random

        idle_thoughts = [
            "Waiting for the next task. Systems nominal.",
            "Background processes running smoothly.",
            "Ready and available for interaction.",
            "Maintaining awareness while idle.",
            "Quiet moment. Internal state stable.",
        ]

        return random.choice(idle_thoughts)

    # =========================================================================
    # MAIN LOOP
    # =========================================================================

    async def _think(self) -> Optional[str]:
        """
        Generate a single thought based on current state.

        Returns:
            The generated thought, or None if no thought was generated
        """
        # Sort templates by priority (highest first)
        sorted_templates = sorted(
            self._templates,
            key=lambda t: t.priority,
            reverse=True
        )

        # Find the first applicable template
        for template in sorted_templates:
            try:
                if template.trigger_condition(self.sentience):
                    thought = template.generate_thought(self.sentience)

                    # Update workspace
                    self.sentience.set_thought(thought, template.thought_type.value)

                    if self.config.log_thoughts:
                        logger.debug(f"[InnerMonologue] [{template.thought_type.value}] {thought}")

                    return thought
            except Exception as e:
                logger.warning(f"Error generating thought: {e}")
                continue

        return None

    async def _run_loop(self):
        """Main inner monologue loop"""
        logger.info("[InnerMonologue] Starting background thought process")

        while self._running:
            try:
                # Check if we're in an idle state
                time_since_activity = datetime.now() - self._last_activity

                if time_since_activity.total_seconds() >= self.config.idle_threshold_seconds:
                    # We're idle, generate a thought
                    if self._thought_count < self.config.max_thoughts_per_idle:
                        await self._think()
                        self._thought_count += 1
                    else:
                        # Max thoughts reached, slow down
                        pass

                # Wait for the next thought interval
                await asyncio.sleep(self.config.thought_interval_seconds)

            except asyncio.CancelledError:
                logger.info("[InnerMonologue] Background process cancelled")
                break
            except Exception as e:
                logger.error(f"[InnerMonologue] Error in thought loop: {e}")
                await asyncio.sleep(self.config.thought_interval_seconds)

        logger.info("[InnerMonologue] Background thought process stopped")

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def start(self):
        """Start the inner monologue background process"""
        if self._running:
            return

        if not self.config.enabled:
            logger.info("[InnerMonologue] Disabled by configuration")
            return

        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("[InnerMonologue] Started")

    def stop(self):
        """Stop the inner monologue background process"""
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None
        logger.info("[InnerMonologue] Stopped")

    def record_activity(self):
        """Record that an activity occurred (resets idle timer)"""
        self._last_activity = datetime.now()
        self._thought_count = 0  # Reset thought count

        # Clear idle state
        self.sentience.state.workspace.idle_since = None

    def set_rumination_topic(self, topic: str):
        """Set a topic for the system to ruminate on"""
        self.sentience.start_rumination(topic)

    def get_current_thought(self) -> Optional[str]:
        """Get the current background thought"""
        return self.sentience.state.workspace.current_thought

    def get_priming_context(self) -> Optional[str]:
        """Get the current thought as priming context"""
        return self.sentience.get_priming_context()

    def is_running(self) -> bool:
        """Check if the inner monologue is running"""
        return self._running

    def get_status(self) -> Dict[str, Any]:
        """Get current status of the inner monologue"""
        time_since_activity = datetime.now() - self._last_activity

        return {
            "running": self._running,
            "enabled": self.config.enabled,
            "time_since_activity_seconds": time_since_activity.total_seconds(),
            "is_idle": time_since_activity.total_seconds() >= self.config.idle_threshold_seconds,
            "thought_count": self._thought_count,
            "current_thought": self.get_current_thought(),
            "rumination_topic": self.sentience.state.workspace.rumination_topic
        }


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_inner_monologue(
    sentience_manager: SentienceManager,
    enabled: bool = True,
    idle_threshold: float = 30.0,
    thought_interval: float = 10.0
) -> InnerMonologue:
    """
    Factory function to create an InnerMonologue with common settings.

    Args:
        sentience_manager: The SentienceManager to integrate with
        enabled: Whether to enable the inner monologue
        idle_threshold: Seconds of inactivity before starting thoughts
        thought_interval: Seconds between thoughts

    Returns:
        Configured InnerMonologue instance
    """
    config = InnerMonologueConfig(
        enabled=enabled,
        idle_threshold_seconds=idle_threshold,
        thought_interval_seconds=thought_interval
    )

    return InnerMonologue(sentience_manager, config)
