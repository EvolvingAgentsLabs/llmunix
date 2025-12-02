#!/usr/bin/env python3
"""
Sentience Layer Demo for LLM OS

This demo showcases the sentience-like architecture including:
- Valence state (safety, curiosity, energy, self_confidence)
- Homeostatic dynamics (set-points and deviation costs)
- Latent modes (auto-creative vs auto-contained)
- Trigger-based state updates
- Behavioral policy derivation
- Self-improvement detection

Run with:
    python examples/sentience_demo.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "llmos"))

from kernel.sentience import (
    SentienceManager,
    SentienceState,
    TriggerType,
    LatentMode,
    ValenceVector
)
from kernel.cognitive_kernel import (
    CognitiveKernel,
    CognitivePolicy,
    SelfImprovementType
)
from kernel.config import LLMOSConfig, SentienceConfig


def print_header(text: str):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_state(state: SentienceState, title: str = "Current State"):
    """Print state in a readable format"""
    print(f"\n--- {title} ---")
    print(f"Latent Mode: {state.latent_mode.value.upper()}")
    print(f"Valence:")
    print(f"  Safety:          {state.valence.safety:+.2f} (setpoint: {state.valence.safety_setpoint:.2f})")
    print(f"  Curiosity:       {state.valence.curiosity:+.2f} (setpoint: {state.valence.curiosity_setpoint:.2f})")
    print(f"  Energy:          {state.valence.energy:+.2f} (setpoint: {state.valence.energy_setpoint:.2f})")
    print(f"  Self-Confidence: {state.valence.self_confidence:+.2f} (setpoint: {state.valence.self_confidence_setpoint:.2f})")
    print(f"Homeostatic Cost: {state.valence.homeostatic_cost():.4f}")
    if state.last_trigger:
        print(f"Last Trigger: {state.last_trigger.value}")
    if state.last_trigger_reason:
        print(f"Reason: {state.last_trigger_reason}")


def demo_basic_state():
    """Demo 1: Basic state operations"""
    print_header("Demo 1: Basic Sentience State")

    # Create a fresh state
    state = SentienceState()
    print_state(state, "Initial State")

    # Show the prompt injection that agents would see
    print("\n--- Prompt Injection (what agents see) ---")
    print(state.to_prompt_injection())

    # Modify valence directly to see effects
    print("\n--- Simulating Low Safety ---")
    state.valence.safety = -0.6
    state.update_latent_mode()
    print_state(state, "After Safety Drop")

    print("\n--- Behavioral Guidance ---")
    print(state.to_behavioral_guidance())


def demo_trigger_system():
    """Demo 2: Trigger-based state updates"""
    print_header("Demo 2: Trigger System")

    # Create manager with persistence disabled for demo
    manager = SentienceManager(auto_persist=False)
    print_state(manager.get_state(), "Initial State")

    # Simulate successful task
    print("\n>>> Triggering: TASK_SUCCESS")
    manager.trigger(
        TriggerType.TASK_SUCCESS,
        reason="Completed file creation task",
        context={"cost": 0.05}
    )
    print_state(manager.get_state(), "After Success")

    # Simulate repeated tasks (causes boredom)
    print("\n>>> Triggering: TASK_REPETITION (3 times)")
    for i in range(3):
        manager.trigger(
            TriggerType.TASK_REPETITION,
            reason=f"Repetitive lint fix #{i+1}",
            context={"repetition_count": i + 2}
        )
    print_state(manager.get_state(), "After Repetition")

    # Simulate safety violation
    print("\n>>> Triggering: SAFETY_VIOLATION")
    manager.trigger(
        TriggerType.SAFETY_VIOLATION,
        reason="Blocked rm -rf command",
        context={}
    )
    print_state(manager.get_state(), "After Safety Violation")

    # Show behavioral guidance after all changes
    print("\n--- Current Behavioral Guidance ---")
    print(manager.get_state().to_behavioral_guidance())


def demo_cognitive_kernel():
    """Demo 3: Cognitive Kernel and Policy Derivation"""
    print_header("Demo 3: Cognitive Kernel")

    # Create sentience manager
    manager = SentienceManager(auto_persist=False)

    # Create cognitive kernel
    kernel = CognitiveKernel(manager)

    # Show initial policy
    print("\n--- Initial Cognitive Policy ---")
    policy = kernel.derive_policy()
    print(f"Prefer Cheap Modes: {policy.prefer_cheap_modes}")
    print(f"Prefer Safe Modes: {policy.prefer_safe_modes}")
    print(f"Allow Exploration: {policy.allow_exploration}")
    print(f"Exploration Budget: {policy.exploration_budget_multiplier}x")
    print(f"Enable Auto-Improvement: {policy.enable_auto_improvement}")

    # Simulate entering recovery mode
    print("\n>>> Simulating Recovery Mode (low energy)")
    manager.get_state().valence.energy = -0.6
    manager.get_state().update_latent_mode()

    print("\n--- Policy in Recovery Mode ---")
    policy = kernel.derive_policy()
    print(f"Prefer Cheap Modes: {policy.prefer_cheap_modes}")
    print(f"Prefer Safe Modes: {policy.prefer_safe_modes}")
    print(f"Allow Exploration: {policy.allow_exploration}")
    print(f"Exploration Budget: {policy.exploration_budget_multiplier}x")

    # Reset and simulate auto-creative mode
    manager.get_state().valence.energy = 0.8
    manager.get_state().valence.curiosity = 0.6
    manager.get_state().valence.self_confidence = 0.5
    manager.get_state().update_latent_mode()

    print("\n>>> Simulating Auto-Creative Mode (high curiosity + confidence)")
    print("\n--- Policy in Auto-Creative Mode ---")
    policy = kernel.derive_policy()
    print(f"Prefer Cheap Modes: {policy.prefer_cheap_modes}")
    print(f"Allow Exploration: {policy.allow_exploration}")
    print(f"Exploration Budget: {policy.exploration_budget_multiplier}x")
    print(f"Max Simultaneous Experiments: {policy.max_simultaneous_experiments}")


def demo_self_improvement():
    """Demo 4: Self-Improvement Detection"""
    print_header("Demo 4: Self-Improvement Detection")

    # Create manager and kernel
    manager = SentienceManager(auto_persist=False)
    kernel = CognitiveKernel(manager)

    # Simulate low curiosity (boredom)
    print("\n>>> Simulating Boredom (low curiosity from repetition)")
    manager.get_state().valence.curiosity = -0.5

    # Simulate repeated patterns
    for _ in range(8):
        kernel._track_goal("Run linting checks")

    # Detect improvements
    print("\n--- Detected Improvement Opportunities ---")
    suggestions = kernel.detect_improvement_opportunities()

    for i, suggestion in enumerate(suggestions, 1):
        print(f"\n{i}. {suggestion.type.value}")
        print(f"   Description: {suggestion.description}")
        print(f"   Priority: {suggestion.priority:.1f}")
        print(f"   Trigger: {suggestion.trigger_reason}")


def demo_event_flow():
    """Demo 5: Full Event Flow"""
    print_header("Demo 5: Complete Event Flow Simulation")

    # Create manager and kernel
    manager = SentienceManager(auto_persist=False)
    kernel = CognitiveKernel(manager)

    print("Simulating a multi-day coding session...")

    # Day 1: Fresh start, creative work
    print("\n--- Day 1: Creative Tasks ---")
    kernel.on_novel_task("Design new API architecture")
    kernel.on_task_complete(success=True, cost=0.45, mode="LEARNER", goal="Design API")
    kernel.on_tool_discovered("api_generator")
    print_state(manager.get_state(), "End of Day 1")

    # Day 2: More repetitive work
    print("\n--- Day 2: Repetitive Fixes ---")
    for i in range(5):
        kernel._track_goal("Fix lint error")
        manager.trigger(
            TriggerType.TASK_REPETITION,
            reason=f"Lint fix #{i+1}",
            context={"repetition_count": i + 1}
        )
        kernel.on_task_complete(success=True, cost=0.02, mode="FOLLOWER", goal="Fix lint error")
    print_state(manager.get_state(), "End of Day 2")

    # Day 3: Something goes wrong
    print("\n--- Day 3: Problems Arise ---")
    kernel.on_task_complete(success=False, cost=0.50, mode="LEARNER", goal="Deploy to production")
    kernel.on_safety_event(blocked=True, reason="Blocked destructive command")
    kernel.on_user_feedback(positive=False, feedback="The deployment broke everything")
    print_state(manager.get_state(), "End of Day 3 (Bad Day)")

    # Show final diagnostics
    print("\n" + kernel.get_diagnostics_report())


def demo_config_integration():
    """Demo 6: Configuration Integration"""
    print_header("Demo 6: Configuration Integration")

    # Show different config presets
    print("\n--- Development Config ---")
    dev_config = LLMOSConfig.development()
    print(f"Enable Sentience: {dev_config.sentience.enable_sentience}")
    print(f"Auto-Improvement: {dev_config.sentience.enable_auto_improvement}")
    print(f"Inject State: {dev_config.sentience.inject_internal_state}")

    print("\n--- Production Config ---")
    prod_config = LLMOSConfig.production()
    print(f"Enable Sentience: {prod_config.sentience.enable_sentience}")
    print(f"Auto-Improvement: {prod_config.sentience.enable_auto_improvement}")
    print(f"Auto-Persist: {prod_config.sentience.auto_persist}")

    print("\n--- Testing Config ---")
    test_config = LLMOSConfig.testing()
    print(f"Enable Sentience: {test_config.sentience.enable_sentience}")
    print(f"(Disabled for deterministic tests)")


def demo_mode_modulation():
    """Demo 7: Mode Selection Modulation"""
    print_header("Demo 7: Mode Selection Modulation")

    from kernel.mode_strategies import ModeDecision

    # Create manager and kernel
    manager = SentienceManager(auto_persist=False)
    kernel = CognitiveKernel(manager)

    # Create a base decision
    base_decision = ModeDecision(
        mode="LEARNER",
        confidence=0.6,
        reasoning="Novel task - no trace found"
    )

    print("\n--- Base Decision ---")
    print(f"Mode: {base_decision.mode}")
    print(f"Reasoning: {base_decision.reasoning}")

    # Test modulation in normal state
    print("\n>>> Testing in BALANCED mode")
    modulated = kernel.modulate_mode_decision(base_decision, "Create a new feature")
    print(f"Modulated Mode: {modulated.mode}")
    print(f"Modulated Reasoning: {modulated.reasoning}")

    # Switch to recovery mode
    print("\n>>> Switching to RECOVERY mode (low energy)")
    manager.get_state().valence.energy = -0.6
    manager.get_state().update_latent_mode()

    # Create decision with trace
    base_with_trace = ModeDecision(
        mode="LEARNER",
        confidence=0.6,
        trace="mock_trace",  # Simulated trace
        reasoning="Novel task - no trace found"
    )

    modulated = kernel.modulate_mode_decision(base_with_trace, "Create a new feature")
    print(f"Modulated Mode: {modulated.mode}")
    print(f"Modulated Reasoning: {modulated.reasoning}")


def main():
    """Run all demos"""
    print("\n" + "=" * 60)
    print("       SENTIENCE LAYER DEMO - LLM OS v3.4.0")
    print("=" * 60)
    print("\nThis demo showcases the sentience-like architecture that")
    print("provides persistent internal state, homeostatic dynamics,")
    print("and emergent behavioral modes.")

    # Run demos
    demo_basic_state()
    demo_trigger_system()
    demo_cognitive_kernel()
    demo_self_improvement()
    demo_event_flow()
    demo_config_integration()
    demo_mode_modulation()

    print_header("Demo Complete!")
    print("\nThe sentience layer provides:")
    print("- Persistent internal state (valence variables)")
    print("- Homeostatic dynamics (set-points and decay)")
    print("- Emergent latent modes (auto-creative, auto-contained, etc.)")
    print("- Trigger-based state updates")
    print("- Behavioral policy derivation")
    print("- Self-improvement detection")
    print("- Mode selection modulation")
    print("\nThis creates a system that adapts its behavior based on")
    print("its own internal 'experience' over time.")


if __name__ == "__main__":
    main()
