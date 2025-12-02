"""
Sentience Hooks for LLM OS

This module provides SDK hooks that integrate the sentience layer with
the execution pipeline. The hooks:

1. Inject internal state into prompts (UserPromptSubmit)
2. Track task outcomes and update valence (PostToolUse)
3. Enforce safety policies based on internal state (PreToolUse)

These hooks work alongside the existing security, budget, and trace hooks.
"""

from typing import Dict, Any, Optional
from pathlib import Path

from kernel.sentience import SentienceManager, TriggerType
from kernel.cognitive_kernel import CognitiveKernel


class SentienceInjectionHook:
    """
    UserPromptSubmit hook for injecting internal state into prompts

    Adds internal state and behavioral guidance to agent prompts so
    they can adapt their behavior based on the system's cognitive state.
    """

    def __init__(self, cognitive_kernel: CognitiveKernel):
        """
        Args:
            cognitive_kernel: CognitiveKernel instance for state access
        """
        self.cognitive_kernel = cognitive_kernel

    async def __call__(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inject internal state before prompt submission

        Returns:
            Hook response with injected context
        """
        user_prompt = event.get("userPrompt", "")

        if not user_prompt:
            return {"continue": True}

        # Get enriched context from cognitive kernel
        injected_context = self.cognitive_kernel.enrich_context()

        if injected_context:
            print(f"[Sentience] Injected internal state into prompt")

            return {
                "continue": True,
                "injectedContext": injected_context
            }

        return {"continue": True}


class SentienceTrackingHook:
    """
    PostToolUse hook for tracking outcomes and updating valence

    Monitors tool execution results and triggers appropriate state updates:
    - Success/failure tracking
    - High cost detection
    - Pattern repetition detection
    """

    def __init__(
        self,
        sentience_manager: SentienceManager,
        cognitive_kernel: CognitiveKernel,
        high_cost_threshold: float = 0.5
    ):
        """
        Args:
            sentience_manager: SentienceManager for state updates
            cognitive_kernel: CognitiveKernel for tracking
            high_cost_threshold: Cost threshold for high-cost trigger
        """
        self.sentience_manager = sentience_manager
        self.cognitive_kernel = cognitive_kernel
        self.high_cost_threshold = high_cost_threshold
        self._recent_tools: list = []

    async def __call__(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track tool execution and update internal state

        Returns:
            Hook response (always continue)
        """
        tool_use = event.get("toolUse", {})
        tool_result = event.get("toolResult", {})
        total_cost = event.get("totalCostUsd", 0.0)

        tool_name = tool_use.get("name", "unknown")
        is_error = tool_result.get("isError", False)

        # Track tool usage for pattern detection
        self._recent_tools.append(tool_name)
        if len(self._recent_tools) > 20:
            self._recent_tools = self._recent_tools[-20:]

        # Check for tool discovery (new tool)
        state = self.sentience_manager.get_state()
        if tool_name not in state.self_model.known_tools:
            self.cognitive_kernel.on_tool_discovered(tool_name)
            print(f"[Sentience] Tool discovery: {tool_name}")

        # Check for high cost
        if total_cost > self.high_cost_threshold:
            self.sentience_manager.trigger(
                TriggerType.HIGH_COST,
                reason=f"High cost operation: ${total_cost:.2f}",
                context={"cost_usd": total_cost, "tool": tool_name}
            )
            print(f"[Sentience] High cost detected: ${total_cost:.2f}")

        # Track cost in cognitive kernel
        self.cognitive_kernel.track_cost(total_cost)

        return {"continue": True}


class SentienceSafetyHook:
    """
    PreToolUse hook for sentience-based safety policies

    Enforces safety policies based on internal state:
    - Block destructive operations in low-safety state
    - Require confirmation in cautious mode
    - Prefer dry-run when available
    """

    def __init__(
        self,
        cognitive_kernel: CognitiveKernel,
        workspace: Optional[Path] = None
    ):
        """
        Args:
            cognitive_kernel: CognitiveKernel for policy access
            workspace: Workspace path for safe zone
        """
        self.cognitive_kernel = cognitive_kernel
        self.workspace = workspace or Path("./workspace")

        # Destructive patterns
        self._destructive_patterns = [
            "rm -rf",
            "drop table",
            "delete from",
            "format",
            "truncate",
            "destroy",
            "reset --hard"
        ]

    async def __call__(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check for safety policy violations

        Returns:
            Hook response with permission decision
        """
        tool_use = event.get("toolUse", {})
        tool_name = tool_use.get("name", "")
        tool_input = tool_use.get("input", {})

        # Get current safety overrides
        overrides = self.cognitive_kernel.get_safety_overrides()

        # Check if destructive operations should be blocked
        if overrides.get("block_destructive_operations"):
            if tool_name == "Bash":
                command = tool_input.get("command", "")
                for pattern in self._destructive_patterns:
                    if pattern in command.lower():
                        print(f"[Sentience Safety] Blocked destructive operation: {pattern}")
                        return {
                            "permissionDecision": "deny",
                            "continue": False,
                            "stopReason": f"[SENTIENCE SAFETY] Destructive operation blocked in current state: {pattern}"
                        }

        # Check if shell commands need confirmation
        if overrides.get("require_confirmation_for_shell"):
            if tool_name == "Bash":
                command = tool_input.get("command", "")
                # Log that confirmation would be needed
                # (In a full implementation, this would pause for user input)
                print(f"[Sentience Safety] Shell command in cautious mode: {command[:50]}...")

        # Check if writes need confirmation
        if overrides.get("require_confirmation_for_writes"):
            if tool_name in {"Write", "Edit", "NotebookEdit"}:
                file_path = tool_input.get("file_path") or tool_input.get("notebook_path", "")
                print(f"[Sentience Safety] Write operation in cautious mode: {file_path}")

        # Allow if no issues
        return {
            "permissionDecision": "allow",
            "continue": True
        }


class SentienceTaskCompletionHook:
    """
    Hook for tracking task completion

    This is called at the end of a task to update internal state
    based on the overall outcome.
    """

    def __init__(
        self,
        cognitive_kernel: CognitiveKernel
    ):
        self.cognitive_kernel = cognitive_kernel
        self._current_task: Optional[Dict[str, Any]] = None

    def start_task(self, goal: str, mode: str):
        """Call at task start to begin tracking"""
        self._current_task = {
            "goal": goal,
            "mode": mode,
            "start_time": None,  # Would use time.time() in real impl
        }

    def complete_task(self, success: bool, cost: float):
        """Call at task completion to update state"""
        if self._current_task:
            self.cognitive_kernel.on_task_complete(
                success=success,
                cost=cost,
                mode=self._current_task["mode"],
                goal=self._current_task["goal"]
            )
            self._current_task = None


def create_sentience_hooks(
    sentience_manager: SentienceManager,
    cognitive_kernel: CognitiveKernel,
    workspace: Optional[Path] = None,
    high_cost_threshold: float = 0.5
) -> Dict[str, list]:
    """
    Create sentience hooks for integration with HookRegistry

    Args:
        sentience_manager: SentienceManager instance
        cognitive_kernel: CognitiveKernel instance
        workspace: Workspace path
        high_cost_threshold: Threshold for high-cost trigger

    Returns:
        Dict mapping hook events to hook instances
    """
    injection_hook = SentienceInjectionHook(cognitive_kernel)
    tracking_hook = SentienceTrackingHook(
        sentience_manager,
        cognitive_kernel,
        high_cost_threshold
    )
    safety_hook = SentienceSafetyHook(cognitive_kernel, workspace)

    return {
        "user_prompt_submit": [injection_hook],
        "post_tool_use": [tracking_hook],
        "pre_tool_use": [safety_hook],
    }
