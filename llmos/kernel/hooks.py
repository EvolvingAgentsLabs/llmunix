"""
SDK Hooks System for llmos
Provides event-based control flow for Claude Agent SDK integration

Hooks allow llmos to:
- Control budget and cost tracking
- Capture execution traces
- Enforce security policies
- Inject context and memory
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from pathlib import Path

try:
    from claude_agent_sdk.types import (
        HookEvent,
        HookMatcher,
        ToolUseBlock,
        HookPermissionDecision,
        Message
    )
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False
    HookEvent = None
    HookMatcher = None
    ToolUseBlock = None
    HookPermissionDecision = None
    Message = None


@dataclass
class HookContext:
    """Context passed to hook callbacks"""
    event: str  # "pre_tool_use", "post_tool_use", "user_prompt_submit"
    tool_name: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    tool_output: Optional[str] = None
    total_cost_usd: Optional[float] = None
    user_data: Optional[Dict[str, Any]] = None  # Custom data for hooks

    # Results from hook
    permission: str = "allow"  # "allow", "deny"
    continue_: bool = True
    stop_reason: Optional[str] = None
    injected_context: Optional[str] = None


class BudgetControlHook:
    """
    PreToolUse hook for budget control
    Denies expensive operations if budget is low
    """

    def __init__(self, token_economy, max_cost_per_operation: float = 1.0):
        """
        Args:
            token_economy: TokenEconomy instance
            max_cost_per_operation: Max cost allowed per operation
        """
        self.token_economy = token_economy
        self.max_cost_per_operation = max_cost_per_operation
        self.operations_count = 0

    async def __call__(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check budget before tool use

        Returns:
            Hook response with permission decision
        """
        tool_use = event.get("toolUse", {})
        tool_name = tool_use.get("name", "unknown")

        self.operations_count += 1

        # Estimate cost based on tool
        estimated_cost = self._estimate_tool_cost(tool_name)

        # Check budget
        try:
            self.token_economy.check_budget(estimated_cost)

            print(f"💰 Budget OK for {tool_name} (~${estimated_cost:.3f})")

            return {
                "permissionDecision": "allow",
                "continue": True
            }

        except Exception as e:
            print(f"❌ Budget exceeded for {tool_name}: {e}")

            return {
                "permissionDecision": "deny",
                "continue": False,
                "stopReason": f"Budget exceeded: {e}"
            }

    def _estimate_tool_cost(self, tool_name: str) -> float:
        """Estimate cost based on tool name"""
        # Simple heuristic - can be improved with actual tracking
        expensive_tools = {"WebSearch", "Task", "Bash"}

        if tool_name in expensive_tools:
            return 0.05  # Higher estimate
        return 0.01  # Lower estimate


class SecurityHook:
    """
    PreToolUse hook for security checks
    Denies dangerous operations
    """

    def __init__(self, workspace: Path, dangerous_patterns: Optional[List[str]] = None):
        """
        Args:
            workspace: Workspace directory (safe zone)
            dangerous_patterns: List of dangerous command patterns
        """
        self.workspace = Path(workspace)
        self.dangerous_patterns = dangerous_patterns or [
            "rm -rf /",
            "sudo rm",
            "dd if=",
            ":(){ :|:& };:",  # Fork bomb
            "chmod 777",
            "curl | bash",
            "wget | bash"
        ]

    async def __call__(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check for dangerous operations

        Returns:
            Hook response with permission decision
        """
        tool_use = event.get("toolUse", {})
        tool_name = tool_use.get("name", "")
        tool_input = tool_use.get("input", {})

        # Check Bash commands
        if tool_name == "Bash":
            command = tool_input.get("command", "")

            for pattern in self.dangerous_patterns:
                if pattern in command:
                    print(f"🚨 SECURITY: Blocked dangerous command: {pattern}")

                    return {
                        "permissionDecision": "deny",
                        "continue": False,
                        "stopReason": f"Security: Dangerous pattern detected: {pattern}"
                    }

        # Check file operations outside workspace
        if tool_name in {"Write", "Edit", "NotebookEdit"}:
            file_path = (
                tool_input.get("file_path") or
                tool_input.get("notebook_path") or
                ""
            )

            if file_path:
                abs_path = Path(file_path).resolve()

                # Check if path is within workspace
                try:
                    abs_path.relative_to(self.workspace)
                except ValueError:
                    print(f"🚨 SECURITY: Blocked write outside workspace: {file_path}")

                    return {
                        "permissionDecision": "deny",
                        "continue": False,
                        "stopReason": f"Security: File operation outside workspace: {file_path}"
                    }

        # Allow if no issues
        return {
            "permissionDecision": "allow",
            "continue": True
        }


class TraceCaptureHook:
    """
    PostToolUse hook for trace capture
    Records tool usage for building execution traces
    """

    def __init__(self, trace_builder=None):
        """
        Args:
            trace_builder: TraceBuilder instance to update
        """
        self.trace_builder = trace_builder
        self.tools_used = []
        self.outputs = []

    async def __call__(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Capture tool usage after execution

        Returns:
            Hook response (always allow)
        """
        tool_use = event.get("toolUse", {})
        tool_result = event.get("toolResult", {})

        tool_name = tool_use.get("name", "unknown")
        output = tool_result.get("output", "")

        # Record tool usage
        if tool_name not in self.tools_used:
            self.tools_used.append(tool_name)

        # Record output (truncate if too long)
        if output:
            output_summary = output[:200] + "..." if len(output) > 200 else output
            self.outputs.append(f"{tool_name}: {output_summary}")

        # Update trace builder if provided
        if self.trace_builder:
            # TraceBuilder will handle this in add_message()
            pass

        print(f"📝 Captured: {tool_name}")

        return {
            "continue": True
        }


class CostTrackingHook:
    """
    PostToolUse hook for cost tracking
    Monitors cumulative cost during execution
    """

    def __init__(self, max_cost_usd: float = 5.0):
        """
        Args:
            max_cost_usd: Maximum allowed cost
        """
        self.max_cost_usd = max_cost_usd
        self.cumulative_cost = 0.0
        self.tool_costs = []

    async def __call__(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track cost after tool execution

        Returns:
            Hook response (stop if over budget)
        """
        # SDK provides total_cost_usd in ResultMessage, not per-tool
        # This is a placeholder for future per-tool cost tracking
        total_cost = event.get("totalCostUsd", 0.0)

        if total_cost > 0:
            self.cumulative_cost = total_cost

            print(f"💵 Cost: ${total_cost:.4f}")

            # Check if over budget
            if self.cumulative_cost > self.max_cost_usd:
                print(f"⚠️  Cost ${self.cumulative_cost:.2f} exceeded budget ${self.max_cost_usd:.2f}")

                return {
                    "continue": False,
                    "stopReason": f"Budget exceeded: ${self.cumulative_cost:.2f} > ${self.max_cost_usd:.2f}"
                }

        return {
            "continue": True
        }


class MemoryInjectionHook:
    """
    UserPromptSubmit hook for memory/context injection
    Injects relevant past experiences before prompt submission
    """

    def __init__(self, memory_query_interface=None):
        """
        Args:
            memory_query_interface: MemoryQueryInterface instance
        """
        self.memory_query = memory_query_interface

    async def __call__(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inject relevant memory before prompt submission

        Returns:
            Hook response with injected context
        """
        user_prompt = event.get("userPrompt", "")

        if not self.memory_query or not user_prompt:
            return {
                "continue": True
            }

        # Find similar past tasks
        try:
            similar_tasks = await self.memory_query.find_similar_tasks(
                goal=user_prompt,
                limit=3,
                min_confidence=0.7
            )

            if similar_tasks:
                # Build context injection
                context_lines = ["## Relevant Past Experiences"]

                for i, task in enumerate(similar_tasks, 1):
                    context_lines.append(f"\n### Similar Task {i}")
                    context_lines.append(f"**Goal**: {task.goal_text}")
                    context_lines.append(f"**Success Rate**: {task.success_rating:.0%}")
                    context_lines.append(f"**Used**: {task.usage_count} times")

                    if task.tools_used:
                        context_lines.append(f"**Tools**: {', '.join(task.tools_used)}")

                    if task.output_summary:
                        context_lines.append(f"**Output**: {task.output_summary[:100]}...")

                injected_context = "\n".join(context_lines)

                print(f"🧠 Injected {len(similar_tasks)} similar experiences")

                return {
                    "continue": True,
                    "injectedContext": injected_context
                }

        except Exception as e:
            print(f"⚠️  Memory injection failed: {e}")

        return {
            "continue": True
        }


class HookRegistry:
    """
    Registry for managing SDK hooks
    Converts llmos hooks to SDK hook format
    """

    def __init__(self):
        self.hooks: Dict[str, List[Callable]] = {
            "pre_tool_use": [],
            "post_tool_use": [],
            "user_prompt_submit": []
        }

    def register(self, event: str, callback: Callable, matcher: Optional[Dict] = None):
        """
        Register a hook callback

        Args:
            event: "pre_tool_use", "post_tool_use", or "user_prompt_submit"
            callback: Async callable that takes event dict and returns response dict
            matcher: Optional HookMatcher dict (e.g., {"tool_name": "Bash"})
        """
        if event not in self.hooks:
            raise ValueError(f"Invalid hook event: {event}")

        self.hooks[event].append({
            "callback": callback,
            "matcher": matcher
        })

    def to_sdk_hooks(self) -> Dict:
        """
        Convert to SDK hooks format

        Returns:
            Dict mapping HookEvent to List[HookMatcher]
        """
        if not SDK_AVAILABLE:
            return {}

        sdk_hooks = {}

        # PreToolUse
        if self.hooks["pre_tool_use"]:
            sdk_hooks[HookEvent.PRE_TOOL_USE] = [
                HookMatcher(
                    matcher=hook.get("matcher", {}),
                    callback=hook["callback"]
                )
                for hook in self.hooks["pre_tool_use"]
            ]

        # PostToolUse
        if self.hooks["post_tool_use"]:
            sdk_hooks[HookEvent.POST_TOOL_USE] = [
                HookMatcher(
                    matcher=hook.get("matcher", {}),
                    callback=hook["callback"]
                )
                for hook in self.hooks["post_tool_use"]
            ]

        # UserPromptSubmit
        if self.hooks["user_prompt_submit"]:
            sdk_hooks[HookEvent.USER_PROMPT_SUBMIT] = [
                HookMatcher(
                    matcher=hook.get("matcher", {}),
                    callback=hook["callback"]
                )
                for hook in self.hooks["user_prompt_submit"]
            ]

        return sdk_hooks

    def clear(self):
        """Clear all registered hooks"""
        for event in self.hooks:
            self.hooks[event] = []


def create_default_hooks(
    token_economy=None,
    workspace: Optional[Path] = None,
    trace_builder=None,
    memory_query=None,
    max_cost_usd: float = 5.0
) -> HookRegistry:
    """
    Create default hook registry for llmos

    Args:
        token_economy: TokenEconomy instance for budget control
        workspace: Workspace path for security checks
        trace_builder: TraceBuilder for trace capture
        memory_query: MemoryQueryInterface for context injection
        max_cost_usd: Maximum cost budget

    Returns:
        HookRegistry with default hooks
    """
    registry = HookRegistry()

    # Budget control (PreToolUse)
    if token_economy:
        budget_hook = BudgetControlHook(token_economy, max_cost_per_operation=1.0)
        registry.register("pre_tool_use", budget_hook)

    # Security checks (PreToolUse)
    if workspace:
        security_hook = SecurityHook(workspace)
        registry.register("pre_tool_use", security_hook)

    # Trace capture (PostToolUse)
    if trace_builder:
        trace_hook = TraceCaptureHook(trace_builder)
        registry.register("post_tool_use", trace_hook)

    # Cost tracking (PostToolUse)
    cost_hook = CostTrackingHook(max_cost_usd)
    registry.register("post_tool_use", cost_hook)

    # Memory injection (UserPromptSubmit)
    if memory_query:
        memory_hook = MemoryInjectionHook(memory_query)
        registry.register("user_prompt_submit", memory_hook)

    return registry
