"""
Cortex - Cognitive Interface using Claude Agent SDK
The "CPU" of the LLM OS
"""

import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock
except ImportError:
    # Fallback for development/testing
    print("Warning: claude-agent-sdk not installed. Install with: pip install claude-agent-sdk")
    ClaudeSDKClient = None
    ClaudeAgentOptions = None


from kernel.bus import EventBus, Event, EventType
from memory.traces import ExecutionTrace


class Cortex:
    """
    The Cortex - Cognitive processing using Claude Agent SDK
    Handles: Planning, Learning, Following
    """

    def __init__(
        self,
        event_bus: EventBus,
        workspace: Path,
        model: str = "claude-sonnet-4-5-20250929"
    ):
        self.event_bus = event_bus
        self.workspace = workspace
        self.model = model
        self.client: Optional[Any] = None

    async def initialize(self):
        """Initialize the Claude SDK client"""
        if ClaudeSDKClient is None:
            raise RuntimeError(
                "Claude Agent SDK not installed. "
                "Install with: pip install claude-agent-sdk"
            )

        # Configure Claude Agent options
        options = ClaudeAgentOptions(
            model=self.model,
            cwd=str(self.workspace),
            allowed_tools=[
                "Read", "Write", "Edit", "Bash",
                "Glob", "Grep"
            ],
            permission_mode="acceptEdits",
            system_prompt={
                "type": "preset",
                "preset": "claude_code",
                "append": """
You are the Cortex of an LLM Operating System.
Your role is to:
1. Decompose high-level goals into executable steps
2. Learn new patterns when encountering novel problems
3. Execute proven patterns efficiently

You have access to file operations, code execution, and search tools.
Work systematically and document your steps.
"""
            }
        )

        self.client = ClaudeSDKClient(options=options)

    async def plan(self, goal: str) -> List[Dict[str, Any]]:
        """
        Plan mode - Decompose a goal into steps

        Args:
            goal: Natural language goal

        Returns:
            List of planned steps
        """
        if not self.client:
            await self.initialize()

        async with self.client as client:
            await client.query(
                f"Plan how to achieve this goal, breaking it into clear steps: {goal}\n\n"
                "Output a numbered list of steps with tool names and parameters."
            )

            plan = []
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            # Parse the plan
                            # TODO: Implement proper plan parsing
                            plan.append({
                                "text": block.text
                            })

            return plan

    async def learn(self, goal: str) -> ExecutionTrace:
        """
        Learner mode - Execute a novel goal and create execution trace

        Args:
            goal: Natural language goal

        Returns:
            ExecutionTrace of the execution
        """
        if not self.client:
            await self.initialize()

        print("🧠 Learner Mode: Solving novel problem...")

        steps = []
        start_time = asyncio.get_event_loop().time()

        async with self.client as client:
            await client.query(goal)

            async for message in client.receive_response():
                # Emit event for each message
                event = Event(
                    type=EventType.LLM_OUTPUT,
                    data={"message": message}
                )
                await self.event_bus.publish(event)

                # Extract tool uses
                if hasattr(message, 'content'):
                    for block in message.content:
                        if hasattr(block, 'name'):  # Tool use
                            steps.append({
                                "tool": block.name,
                                "input": getattr(block, 'input', {})
                            })

        end_time = asyncio.get_event_loop().time()
        execution_time = end_time - start_time

        # Create execution trace
        trace = ExecutionTrace(
            goal_signature=self._hash_goal(goal),
            goal_text=goal,
            steps=steps,
            success_rating=0.75,  # Initial confidence
            estimated_time_secs=execution_time
        )

        print(f"✅ Learner Mode Complete: {len(steps)} steps, {execution_time:.2f}s")

        return trace

    async def follow(self, trace: ExecutionTrace) -> bool:
        """
        Follower mode - Execute a proven trace

        Args:
            trace: ExecutionTrace to execute

        Returns:
            True if successful
        """
        print(f"⚡ Follower Mode: Executing {len(trace.steps)} steps...")

        try:
            for step in trace.steps:
                # Execute each step deterministically
                # TODO: Implement actual tool execution
                print(f"  → {step['tool']}")
                await asyncio.sleep(0.1)  # Simulate execution

            print("✅ Follower Mode Complete")
            return True

        except Exception as e:
            print(f"❌ Follower Mode Failed: {e}")
            return False

    def _hash_goal(self, goal: str) -> str:
        """Hash a goal for signature"""
        import hashlib
        return hashlib.sha256(goal.lower().strip().encode()).hexdigest()[:16]
