"""
SystemAgent Orchestrator - Multi-agent coordination using Claude Agent SDK
Implements llmunix-style orchestration in llmos
"""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

try:
    from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AgentDefinition
except ImportError:
    print("Warning: claude-agent-sdk not installed. Install with: pip install claude-agent-sdk")
    ClaudeSDKClient = None
    ClaudeAgentOptions = None
    AgentDefinition = None

from kernel.bus import EventBus, Event, EventType
from kernel.project_manager import Project, ProjectManager
from kernel.agent_factory import AgentFactory, AgentSpec
from kernel.component_registry import ComponentRegistry
from kernel.state_manager import StateManager, ExecutionStep
from kernel.token_economy import TokenEconomy
from memory.traces_sdk import TraceManager


@dataclass
class OrchestrationResult:
    """Result of orchestrated execution"""
    success: bool
    output: Any
    steps_completed: int
    total_steps: int
    cost_usd: float
    execution_time_secs: float
    state_summary: Dict[str, Any]


class SystemAgent:
    """
    SystemAgent Orchestrator - Master coordinator for multi-agent workflows

    Equivalent to llmunix SystemAgent, but using Claude Agent SDK.
    Coordinates multiple specialized agents to solve complex problems.
    """

    def __init__(
        self,
        event_bus: EventBus,
        project_manager: ProjectManager,
        agent_factory: AgentFactory,
        component_registry: ComponentRegistry,
        token_economy: TokenEconomy,
        trace_manager: TraceManager,
        workspace: Path,
        model: str = "claude-sonnet-4-5-20250929"
    ):
        """
        Initialize SystemAgent

        Args:
            event_bus: Event bus for system events
            project_manager: Project manager
            agent_factory: Agent factory for creating specialized agents
            component_registry: Component registry for discovery
            token_economy: Token economy for budget management
            trace_manager: Trace manager for memory
            workspace: Workspace directory
            model: Claude model to use
        """
        self.event_bus = event_bus
        self.project_manager = project_manager
        self.agent_factory = agent_factory
        self.component_registry = component_registry
        self.token_economy = token_economy
        self.trace_manager = trace_manager
        self.workspace = Path(workspace)
        self.model = model

        # Ensure system agent is registered
        self._ensure_system_agent_registered()

    def _ensure_system_agent_registered(self):
        """Ensure system agent is in registry"""
        from kernel.agent_factory import SYSTEM_AGENT_TEMPLATE

        if not self.component_registry.get_agent("system-agent"):
            self.component_registry.register_agent(SYSTEM_AGENT_TEMPLATE)

    async def orchestrate(
        self,
        goal: str,
        project: Optional[Project] = None,
        max_cost_usd: float = 5.0
    ) -> OrchestrationResult:
        """
        Orchestrate multi-agent execution to achieve goal

        This is the main entry point for complex, multi-step tasks.

        Workflow:
        1. Consult memory for similar tasks
        2. Decompose goal into sub-tasks
        3. Identify required specialized agents
        4. Create agents if needed (via AgentFactory)
        5. Delegate sub-tasks to agents
        6. Coordinate results
        7. Update memory with learnings

        Args:
            goal: Natural language goal to achieve
            project: Optional project context
            max_cost_usd: Maximum cost budget for this orchestration

        Returns:
            OrchestrationResult with execution details
        """
        import time
        start_time = time.time()

        # Create project if not provided
        if project is None:
            # Extract project name from goal (simple heuristic)
            project_name = goal.split()[0:3]
            project_name = "_".join(project_name).lower().replace(" ", "_")
            project = self.project_manager.create_project(
                name=project_name,
                description=f"Auto-created for goal: {goal}"
            )

        # Initialize state manager
        state = StateManager(project.root_path)
        state.initialize_execution(goal)

        # Set budget constraint
        state.update_constraint("max_token_cost", max_cost_usd)

        # Emit orchestration started event
        await self.event_bus.publish(Event(
            type=EventType.TASK_STARTED,
            data={"goal": goal, "project": project.name}
        ))

        # Log event
        state.log_event("ORCHESTRATION_STARTED", {
            "goal": goal,
            "project": project.name,
            "max_cost_usd": max_cost_usd
        })

        try:
            # Fast-path: Detect simple tool calls and handle directly
            # Pattern: "Use the X tool to Y" or "Call the X tool"
            import re
            tool_call_pattern = r"(?:use|call|execute)\s+(?:the\s+)?(\w+)(?:_tool|\s+tool)"
            match = re.search(tool_call_pattern, goal.lower())

            if match and len(goal.split()) < 20:  # Simple, short requests
                tool_name = match.group(1)
                state.log_event("FAST_PATH_DETECTED", {
                    "tool": tool_name,
                    "reason": "Simple tool call - skipping decomposition"
                })

                # Execute directly without decomposition
                options = ClaudeAgentOptions(
                    model=self.model,
                    cwd=str(project.root_path),
                    permission_mode="acceptEdits"
                )

                total_cost = 0.0
                output_text = ""

                async with ClaudeSDKClient(options=options) as client:
                    await client.query(goal)

                    async for msg in client.receive_response():
                        if hasattr(msg, "content"):
                            for block in msg.content:
                                if hasattr(block, "text"):
                                    output_text += block.text + "\n"

                        if hasattr(msg, "total_cost_usd"):
                            total_cost = msg.total_cost_usd or 0.0

                        if "Result" in msg.__class__.__name__:
                            break

                execution_time = time.time() - start_time
                state.mark_execution_complete(success=True)

                await self.event_bus.publish(Event(
                    type=EventType.TASK_COMPLETED,
                    data={"goal": goal, "fast_path": True}
                ))

                return OrchestrationResult(
                    success=True,
                    output=output_text.strip(),
                    steps_completed=1,
                    total_steps=1,
                    cost_usd=total_cost,
                    execution_time_secs=execution_time,
                    state_summary={"fast_path": True, "tool": tool_name}
                )

            # Step 1: Consult memory
            state.log_event("MEMORY_CONSULTATION", {"phase": "started"})
            memory_insights = await self._consult_memory(goal)
            state.set_variable("memory_insights", memory_insights)

            # Step 2: Register all agents as AgentDefinitions
            all_agents = self.component_registry.list_agents()
            agents_dict = {}
            if all_agents and AgentDefinition:
                for agent in all_agents:
                    try:
                        agents_dict[agent.name] = AgentDefinition(
                            description=agent.description,
                            prompt=agent.system_prompt,
                            tools=agent.tools,
                            model="claude-sonnet-4-5-20250929"  # Use proper model identifier
                        )
                        state.log_event("AGENT_REGISTERED", {
                            "agent": agent.name,
                            "tools": agent.tools
                        })
                    except Exception as e:
                        state.log_event("AGENT_REGISTRATION_FAILED", {
                            "agent": agent.name,
                            "error": str(e)
                        })
                        print(f"[WARNING] Failed to register agent {agent.name}: {e}")

            # Step 3: Create shared SDK client with all agents
            options = ClaudeAgentOptions(
                agents=agents_dict,  # All agents registered!
                cwd=str(project.root_path),
                permission_mode="acceptEdits"
            )

            # Step 4: Decompose goal using Claude Agent SDK
            state.log_event("GOAL_DECOMPOSITION", {"phase": "started"})
            plan = await self._decompose_goal(goal, project, memory_insights)
            state.set_plan(plan)

            # Step 4.5: Ensure all agents in plan exist (create on-demand if needed)
            plan, new_agents = await self._ensure_agents_for_plan(plan, project, state)

            # If new agents were created, re-register them with SDK
            if new_agents:
                for new_agent in new_agents:
                    try:
                        agents_dict[new_agent.name] = AgentDefinition(
                            description=new_agent.description,
                            prompt=new_agent.system_prompt,
                            tools=new_agent.tools,
                            model="claude-sonnet-4-5-20250929"
                        )
                        state.log_event("AGENT_CREATED_ON_DEMAND", {
                            "agent": new_agent.name,
                            "tools": new_agent.tools
                        })
                    except Exception as e:
                        print(f"[WARNING] Failed to register new agent {new_agent.name}: {e}")

                # Update options with new agents
                options = ClaudeAgentOptions(
                    agents=agents_dict,
                    cwd=str(project.root_path),
                    permission_mode="acceptEdits"
                )

            # Step 5: Execute plan with shared client
            total_cost = 0.0
            async with ClaudeSDKClient(options=options) as client:
                for step in plan:
                    state.update_step_status(step.step_number, "in_progress")

                    # Check budget
                    if total_cost >= max_cost_usd:
                        state.log_event("BUDGET_EXCEEDED", {
                            "total_cost": total_cost,
                            "max_cost": max_cost_usd
                        })
                        break

                    # Execute step with shared client
                    step_result = await self._execute_step_with_client(
                        client, step, project, state
                    )

                    if step_result["success"]:
                        state.update_step_status(
                            step.step_number,
                            "completed",
                            result=step_result.get("output")
                        )
                        total_cost += step_result.get("cost", 0.0)
                    else:
                        state.update_step_status(
                            step.step_number,
                            "failed",
                            error=step_result.get("error")
                        )
                        # Continue or halt based on criticality
                        # For now, continue

            # Step 6: Consolidate results
            execution_summary = state.get_execution_summary()
            state.mark_execution_complete(success=True)

            # Emit completion event
            await self.event_bus.publish(Event(
                type=EventType.TASK_COMPLETED,
                data={"goal": goal, "summary": execution_summary}
            ))

            # Calculate execution time
            execution_time = time.time() - start_time

            return OrchestrationResult(
                success=True,
                output=execution_summary,
                steps_completed=execution_summary["completed_steps"],
                total_steps=execution_summary["total_steps"],
                cost_usd=total_cost,
                execution_time_secs=execution_time,
                state_summary=execution_summary
            )

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"\n[ERROR] Orchestration failed:")
            print(error_details)

            state.log_event("ORCHESTRATION_FAILED", {
                "error": str(e),
                "traceback": error_details
            })
            state.mark_execution_complete(success=False)

            execution_time = time.time() - start_time

            return OrchestrationResult(
                success=False,
                output=str(e),
                steps_completed=0,
                total_steps=len(plan) if 'plan' in locals() else 0,
                cost_usd=0.0,
                execution_time_secs=execution_time,
                state_summary={}
            )

    async def _consult_memory(self, goal: str) -> Dict[str, Any]:
        """
        Consult memory for similar tasks

        Args:
            goal: Goal to search for

        Returns:
            Memory insights
        """
        # Find similar traces
        trace = self.trace_manager.find_trace(goal, min_confidence=0.7)

        insights = {
            "similar_trace_found": trace is not None,
            "trace": trace,
            "recommendations": []
        }

        if trace:
            insights["recommendations"].append(
                f"Similar task executed {trace.usage_count} times with "
                f"{trace.success_rating:.0%} success rate"
            )

        return insights

    async def _decompose_goal(
        self,
        goal: str,
        project: Project,
        memory_insights: Dict[str, Any]
    ) -> List[ExecutionStep]:
        """
        Decompose goal into execution steps using Claude Agent SDK

        Args:
            goal: Goal to decompose
            project: Project context
            memory_insights: Insights from memory consultation

        Returns:
            List of ExecutionStep instances
        """
        if ClaudeSDKClient is None:
            raise RuntimeError("Claude Agent SDK not installed")

        # Build planning prompt
        planning_prompt = f"""Decompose this goal into concrete execution steps:

Goal: {goal}

Memory Insights:
{json.dumps(memory_insights, indent=2)}

Available Agents:
{self._get_available_agents_summary()}

IMPORTANT - Agent Assignment:
You may (and SHOULD) suggest specialized agents even if they don't exist yet.
The system will automatically create them on-demand before execution.

Use descriptive kebab-case names that reflect the agent's purpose, such as:
- ansatz-designer (for quantum circuit design)
- vqe-executor (for running VQE simulations)
- optimizer-agent (for classical optimization)
- data-processor (for data transformation)
- code-generator (for writing code)
- test-runner (for running tests)

Only use "system-agent" for generic coordination tasks that don't need specialization.

Create a detailed execution plan with:
1. Clear, actionable steps
2. Agent assignment for each step (prefer specialized agents over system-agent)
3. Expected output for each step

Format your response as JSON:
{{
  "steps": [
    {{
      "number": 1,
      "description": "Step description",
      "agent": "specialized-agent-name",
      "expected_output": "What this step should produce"
    }}
  ]
}}
"""

        # Configure agent options
        options = ClaudeAgentOptions(
            model=self.model,
            cwd=str(project.root_path),
            allowed_tools=["Read", "Write", "Grep", "Glob"],
            permission_mode="acceptEdits",  # Auto-accept to avoid hanging
            system_prompt={
                "type": "preset",
                "preset": "claude_code",
                "append": """
You are the planning component of a multi-agent LLM operating system.
Your role is to decompose complex goals into concrete execution steps.

Think systematically:
1. What needs to be done?
2. What's the optimal order?
3. Which specialized agent should handle each step?
4. What are the dependencies between steps?

Be specific and actionable.
"""
            }
        )

        plan_json = None

        async with ClaudeSDKClient(options=options) as client:
            await client.query(planning_prompt)

            async for msg in client.receive_response():
                # Extract plan from response
                if hasattr(msg, "content"):
                    for block in msg.content:
                        if hasattr(block, "text"):
                            text = block.text
                            # Try to parse JSON from response
                            try:
                                # Find JSON in response
                                start = text.find("{")
                                end = text.rfind("}") + 1
                                if start != -1 and end != 0:
                                    plan_json = json.loads(text[start:end])
                            except json.JSONDecodeError:
                                continue

        # Convert to ExecutionStep instances
        steps = []
        if plan_json and "steps" in plan_json:
            for step_data in plan_json["steps"]:
                steps.append(ExecutionStep(
                    step_number=step_data["number"],
                    description=step_data["description"],
                    agent=step_data.get("agent", "system-agent"),
                    status="pending"
                ))

        # If no plan generated, create simple fallback
        if not steps:
            steps = [
                ExecutionStep(
                    step_number=1,
                    description=goal,
                    agent="system-agent",
                    status="pending"
                )
            ]

        return steps

    async def _execute_step_with_client(
        self,
        client: ClaudeSDKClient,
        step: ExecutionStep,
        project: Project,
        state: StateManager
    ) -> Dict[str, Any]:
        """
        Execute a single step using shared SDK client with agent delegation

        Uses natural language to delegate to registered agents:
        "Use the {agent_name} agent to {task_description}"

        Args:
            client: Shared ClaudeSDKClient with all agents registered
            step: ExecutionStep to execute
            project: Project context
            state: State manager

        Returns:
            Result dictionary with success, output, cost
        """
        state.log_event("STEP_EXECUTION_STARTED", {
            "step": step.step_number,
            "description": step.description,
            "agent": step.agent
        })

        # Check if agent exists
        agent_spec = self.component_registry.get_agent(step.agent)

        if agent_spec is None:
            state.log_event("AGENT_NOT_FOUND", {
                "agent": step.agent,
                "action": "using system-agent as fallback"
            })
            # Use system-agent as fallback
            step.agent = "system-agent"

        # Delegate using natural language (SDK handles routing to agent)
        delegation_prompt = f"Use the {step.agent} agent to {step.description}"

        result = await self._delegate_with_client(
            client,
            delegation_prompt,
            state
        )

        state.log_event("STEP_EXECUTION_COMPLETED", {
            "step": step.step_number,
            "success": result["success"],
            "cost": result.get("cost", 0.0)
        })

        return result

    async def _delegate_with_client(
        self,
        client: ClaudeSDKClient,
        delegation_prompt: str,
        state: StateManager,
        timeout_seconds: float = 300.0  # 5 minute timeout
    ) -> Dict[str, Any]:
        """
        Delegate task using shared SDK client

        The SDK routes to the appropriate agent based on natural language.
        Example: "Use the code-reviewer agent to review src/types.py"

        Args:
            client: Shared ClaudeSDKClient with agents registered
            delegation_prompt: Natural language delegation instruction
            state: State manager
            timeout_seconds: Timeout in seconds (default 300s/5min)

        Returns:
            Result dictionary
        """
        result_text_parts = []
        cost_estimate = 0.0

        print(f"\n[DEBUG] Starting delegation: {delegation_prompt[:100]}...")
        state.log_event("DELEGATION_STARTED", {
            "prompt": delegation_prompt[:200]
        })

        try:
            # Send delegation via SDK
            print(f"[DEBUG] Sending query to SDK...")
            await client.query(delegation_prompt)
            print(f"[DEBUG] Query sent, waiting for response...")

            # Collect response with timeout and inactivity detection
            async def collect_responses():
                nonlocal result_text_parts, cost_estimate
                message_count = 0
                last_message_time = asyncio.get_event_loop().time()
                inactivity_timeout = 60.0  # 60 seconds of no messages = likely stuck
                stop_iteration = False

                async def message_iterator():
                    """Wrapper to track last message time"""
                    nonlocal last_message_time, message_count, stop_iteration
                    try:
                        async for msg in client.receive_response():
                            if stop_iteration:
                                break
                            last_message_time = asyncio.get_event_loop().time()
                            message_count += 1
                            yield msg
                    except asyncio.CancelledError:
                        print(f"[DEBUG] Message iterator cancelled")
                        raise

                async def inactivity_checker():
                    """Check for inactivity and stop iteration if stuck"""
                    nonlocal stop_iteration
                    try:
                        while True:
                            await asyncio.sleep(5.0)  # Check every 5 seconds
                            time_since_last = asyncio.get_event_loop().time() - last_message_time
                            if time_since_last > inactivity_timeout:
                                print(f"[WARNING] No messages for {time_since_last:.1f}s - stopping delegation")
                                stop_iteration = True
                                raise asyncio.TimeoutError(f"Inactivity timeout: no messages for {time_since_last:.1f}s")
                    except asyncio.CancelledError:
                        # Expected when we're shutting down
                        pass

                # Run both the message iterator and inactivity checker concurrently
                inactivity_task = asyncio.create_task(inactivity_checker())
                iteration_error = None

                try:
                    async for msg in message_iterator():
                        print(f"[DEBUG] Received message {message_count}: {type(msg).__name__}")

                        # Log activity
                        activity = self._get_activity_text(msg)
                        if activity:
                            print(f"[DEBUG] Activity: {activity}")
                            state.log_event("AGENT_ACTIVITY", {
                                "activity": activity
                            })

                        # Extract text from AssistantMessage
                        if hasattr(msg, "content"):
                            for block in msg.content:
                                if hasattr(block, "text"):
                                    result_text_parts.append(block.text)
                                    print(f"[DEBUG] Extracted text: {block.text[:100]}...")

                        # Get cost from ResultMessage and break (delegation complete)
                        if hasattr(msg, "total_cost_usd"):
                            cost_estimate = msg.total_cost_usd or 0.0
                            print(f"[DEBUG] Cost: ${cost_estimate:.4f}")

                        # Break on ResultMessage (indicates completion)
                        if "Result" in msg.__class__.__name__:
                            print(f"[DEBUG] ResultMessage received - delegation complete")
                            break  # Exit loop when ResultMessage is received
                except asyncio.TimeoutError as e:
                    # Capture inactivity timeout for re-raising
                    iteration_error = e
                    print(f"[DEBUG] Caught inactivity timeout in message loop")
                finally:
                    # Cancel inactivity checker
                    inactivity_task.cancel()
                    try:
                        await inactivity_task
                    except asyncio.CancelledError:
                        pass
                    except asyncio.TimeoutError as e:
                        # Capture any timeout from the checker
                        if iteration_error is None:
                            iteration_error = e

                print(f"[DEBUG] Finished collecting responses. Total messages: {message_count}")

                # Re-raise inactivity timeout if it occurred
                if iteration_error:
                    raise iteration_error

            # Apply timeout
            await asyncio.wait_for(collect_responses(), timeout=timeout_seconds)

            print(f"[DEBUG] Delegation completed successfully")
            state.log_event("DELEGATION_COMPLETED", {
                "success": True,
                "cost": cost_estimate,
                "result_length": len("".join(result_text_parts))
            })

            return {
                "success": True,
                "output": "\n".join(result_text_parts) if result_text_parts else "",
                "cost": cost_estimate
            }

        except asyncio.TimeoutError:
            error_msg = f"Delegation timed out after {timeout_seconds}s"
            print(f"[ERROR] {error_msg}")

            # Drain any remaining messages to prevent bleeding into next delegation
            print(f"[DEBUG] Draining remaining messages from timed-out delegation...")
            try:
                # Try to collect remaining messages with a short timeout
                async def drain_messages():
                    drained = 0
                    async for msg in client.receive_response():
                        drained += 1
                        print(f"[DEBUG] Drained message {drained}: {type(msg).__name__}")
                        # Update cost if we find a ResultMessage
                        if hasattr(msg, "total_cost_usd"):
                            nonlocal cost_estimate
                            cost_estimate = msg.total_cost_usd or cost_estimate
                        # Stop if we hit a ResultMessage
                        if "Result" in msg.__class__.__name__:
                            print(f"[DEBUG] Found ResultMessage while draining")
                            break
                    print(f"[DEBUG] Drained {drained} messages")

                await asyncio.wait_for(drain_messages(), timeout=5.0)
            except asyncio.TimeoutError:
                print(f"[DEBUG] Drain timeout - some messages may remain buffered")
            except Exception as e:
                print(f"[DEBUG] Error while draining: {e}")

            state.log_event("DELEGATION_TIMEOUT", {
                "timeout": timeout_seconds,
                "prompt": delegation_prompt[:200]
            })
            return {
                "success": False,
                "error": error_msg,
                "cost": cost_estimate
            }

        except Exception as e:
            error_msg = f"Delegation failed: {str(e)}"
            print(f"[ERROR] {error_msg}")
            import traceback
            traceback.print_exc()
            state.log_event("DELEGATION_ERROR", {
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            return {
                "success": False,
                "error": str(e),
                "cost": cost_estimate
            }

    async def _delegate_to_agent(
        self,
        agent_spec: AgentSpec,
        task: str,
        project: Project,
        state: StateManager
    ) -> Dict[str, Any]:
        """
        DEPRECATED: Use _delegate_with_client instead

        Legacy method that creates a new SDK client per delegation.
        Kept for backward compatibility but not used in orchestrate().

        The new approach registers all agents upfront and uses
        natural language delegation with a shared client.

        Args:
            agent_spec: Agent specification
            task: Task description
            project: Project context
            state: State manager

        Returns:
            Result dictionary
        """
        if ClaudeSDKClient is None:
            raise RuntimeError("Claude Agent SDK not installed")

        # Configure agent options
        options = ClaudeAgentOptions(
            model=self.model,
            cwd=str(project.root_path),
            allowed_tools=agent_spec.tools,
            system_prompt={
                "type": "text",
                "text": agent_spec.system_prompt
            },
            permission_mode="acceptEdits"  # Auto-accept tool executions
        )

        result_text = None
        cost_estimate = 0.0

        try:
            async with ClaudeSDKClient(options=options) as client:
                await client.query(task)

                async for msg in client.receive_response():
                    # Emit activity event
                    activity = self._get_activity_text(msg)
                    if activity:
                        state.log_event("AGENT_ACTIVITY", {
                            "agent": agent_spec.name,
                            "activity": activity
                        })

                    # Extract result
                    if hasattr(msg, "result"):
                        result_text = msg.result

                    # Estimate cost (rough approximation)
                    # TODO: Get actual cost from SDK if available
                    cost_estimate += 0.001  # Small cost per message

            return {
                "success": True,
                "output": result_text,
                "cost": cost_estimate
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "cost": cost_estimate
            }

    async def _ensure_agents_for_plan(
        self,
        plan: List[ExecutionStep],
        project: Project,
        state: StateManager
    ) -> Tuple[List[ExecutionStep], List[AgentSpec]]:
        """
        Ensure all agents in the plan exist, creating them on-demand if needed.

        This solves the cold-start problem: when ORCHESTRATOR mode is selected
        but no specialized agents exist, we create them before execution.

        Args:
            plan: List of execution steps with agent assignments
            project: Project context for agent creation
            state: State manager for logging

        Returns:
            Tuple of (updated_plan, list_of_newly_created_agents)
        """
        new_agents = []
        agents_needed = set()

        # Collect unique agent names from plan (excluding system-agent)
        for step in plan:
            if step.agent and step.agent != "system-agent":
                agents_needed.add(step.agent)

        if not agents_needed:
            return plan, new_agents

        state.log_event("AGENT_GAP_DETECTION", {
            "agents_in_plan": list(agents_needed),
            "phase": "started"
        })

        # Check which agents don't exist
        missing_agents = []
        for agent_name in agents_needed:
            if not self.component_registry.get_agent(agent_name):
                missing_agents.append(agent_name)

        if not missing_agents:
            state.log_event("AGENT_GAP_DETECTION", {
                "result": "all_agents_exist",
                "phase": "completed"
            })
            return plan, new_agents

        print(f"\n[INFO] Detected {len(missing_agents)} missing agents: {missing_agents}")
        print("[INFO] Creating agents on-demand...")

        # Create missing agents
        for agent_name in missing_agents:
            # Find the step(s) that need this agent to understand the capability needed
            capability_hints = []
            for step in plan:
                if step.agent == agent_name:
                    capability_hints.append(step.description)

            capability = f"{agent_name}: {'; '.join(capability_hints)}"

            print(f"[INFO] Creating agent '{agent_name}'...")
            state.log_event("AGENT_CREATION_STARTED", {
                "agent": agent_name,
                "capability": capability[:200]
            })

            try:
                new_agent = await self.create_agent_on_demand(capability, project)

                if new_agent:
                    new_agents.append(new_agent)
                    print(f"[INFO] Successfully created agent: {new_agent.name}")
                    state.log_event("AGENT_CREATION_SUCCESS", {
                        "agent": new_agent.name,
                        "tools": new_agent.tools
                    })
                else:
                    # Fallback: update plan to use system-agent
                    print(f"[WARNING] Could not create '{agent_name}', falling back to system-agent")
                    state.log_event("AGENT_CREATION_FAILED", {
                        "agent": agent_name,
                        "fallback": "system-agent"
                    })
                    for step in plan:
                        if step.agent == agent_name:
                            step.agent = "system-agent"

            except Exception as e:
                print(f"[ERROR] Failed to create agent '{agent_name}': {e}")
                state.log_event("AGENT_CREATION_ERROR", {
                    "agent": agent_name,
                    "error": str(e)
                })
                # Fallback to system-agent
                for step in plan:
                    if step.agent == agent_name:
                        step.agent = "system-agent"

        state.log_event("AGENT_GAP_DETECTION", {
            "agents_created": [a.name for a in new_agents],
            "phase": "completed"
        })

        return plan, new_agents

    def _get_activity_text(self, msg) -> Optional[str]:
        """Extract activity text from a message (from chief_of_staff example)"""
        try:
            if "Assistant" in msg.__class__.__name__:
                if hasattr(msg, "content") and msg.content:
                    first_content = msg.content[0] if isinstance(msg.content, list) else msg.content
                    if hasattr(first_content, "name"):
                        return f"Using: {first_content.name}()"
                return "Thinking..."
            elif "User" in msg.__class__.__name__:
                return "Tool completed"
        except (AttributeError, IndexError):
            pass
        return None

    def _get_available_agents_summary(self) -> str:
        """Get summary of available agents for planning"""
        agents = self.component_registry.list_agents(status="production")

        summary_parts = []
        for agent in agents:
            summary_parts.append(
                f"- {agent.name}: {agent.description} (Tools: {', '.join(agent.tools)})"
            )

        return "\n".join(summary_parts) if summary_parts else "No specialized agents available"

    async def create_agent_on_demand(
        self,
        capability: str,
        project: Project
    ) -> Optional[AgentSpec]:
        """
        Create a specialized agent on-demand for a capability

        Args:
            capability: Capability description
            project: Project context

        Returns:
            Created AgentSpec or None
        """
        # Use Claude to design the agent
        if ClaudeSDKClient is None:
            return None

        design_prompt = f"""Design a specialized agent for this capability: {capability}

Create an agent specification in JSON format:
{{
  "name": "kebab-case-name",
  "type": "specialized",
  "category": "domain_category",
  "description": "When to use this agent",
  "tools": ["Read", "Write", "Bash"],
  "capabilities": ["capability 1", "capability 2"],
  "constraints": ["constraint 1", "constraint 2"],
  "system_prompt": "Detailed agent instructions..."
}}
"""

        options = ClaudeAgentOptions(
            model=self.model,
            cwd=str(project.root_path),
            allowed_tools=[],
            permission_mode="acceptEdits",  # Auto-accept to avoid hanging
            system_prompt={
                "type": "text",
                "text": "You are an agent designer. Create detailed agent specifications."
            }
        )

        agent_json = None

        async with ClaudeSDKClient(options=options) as client:
            await client.query(design_prompt)

            async for msg in client.receive_response():
                if hasattr(msg, "content"):
                    for block in msg.content:
                        if hasattr(block, "text"):
                            text = block.text
                            try:
                                start = text.find("{")
                                end = text.rfind("}") + 1
                                if start != -1 and end != 0:
                                    agent_json = json.loads(text[start:end])
                            except json.JSONDecodeError:
                                continue

        if agent_json:
            # Map JSON keys to factory parameter names
            # JSON uses "type" but factory expects "agent_type"
            factory_args = {
                "name": agent_json.get("name", "specialized-agent"),
                "agent_type": agent_json.get("type", "specialized"),
                "category": agent_json.get("category", "general"),
                "description": agent_json.get("description", "Auto-created specialized agent"),
                "system_prompt": agent_json.get("system_prompt", "You are a specialized agent."),
                "tools": agent_json.get("tools", ["Read", "Write", "Bash"]),
                "capabilities": agent_json.get("capabilities", []),
                "constraints": agent_json.get("constraints", [])
            }

            # Create agent using factory
            agent = self.agent_factory.create_agent(**factory_args)
            self.component_registry.register_agent(agent)
            return agent

        return None

    async def crystallize_pattern(
        self,
        trace_signature: str,
        plugin_loader = None
    ) -> Optional[str]:
        """
        Crystallize an execution trace into a Python tool (HOPE Protocol).

        This implements the Self-Modifying Kernel architecture from the Nested Learning paper.
        Converts fluid intelligence (LLM reasoning) into crystallized intelligence (Python code).

        Workflow:
        1. Retrieve trace details from memory
        2. Instantiate Toolsmith agent
        3. Generate Python plugin code
        4. Validate syntax
        5. Hot-load the new tool
        6. Mark trace as crystallized

        Args:
            trace_signature: Signature of the trace to crystallize
            plugin_loader: Optional PluginLoader instance for hot-loading

        Returns:
            Name of generated tool if successful, None otherwise
        """
        if ClaudeSDKClient is None:
            print("[ERROR] Claude Agent SDK required for crystallization")
            return None

        print(f"\n{'='*60}")
        print(f"💎 CRYSTALLIZATION: Converting trace to tool")
        print(f"{'='*60}")

        # 1. Get trace details
        traces = self.trace_manager.list_traces()
        trace = None
        for t in traces:
            if t.goal_signature == trace_signature:
                trace = t
                break

        if not trace:
            print(f"[ERROR] Trace not found: {trace_signature}")
            return None

        print(f"📝 Goal: {trace.goal_text}")
        print(f"📊 Usage: {trace.usage_count} times, {trace.success_rating:.0%} success")

        # 2. Ensure Toolsmith agent is registered
        from kernel.agent_factory import TOOLSMITH_AGENT_TEMPLATE

        if not self.component_registry.get_agent("toolsmith-agent"):
            self.component_registry.register_agent(TOOLSMITH_AGENT_TEMPLATE)

        # 3. Build crystallization prompt with trace details
        tools_used_str = ", ".join(trace.tools_used) if trace.tools_used else "N/A"

        crystallization_prompt = f"""
Convert this execution trace into a Python plugin tool.

## Trace Details

**Goal:** {trace.goal_text}
**Signature:** {trace.goal_signature}
**Success Rate:** {trace.success_rating:.0%}
**Usage Count:** {trace.usage_count}
**Tools Used:** {tools_used_str}
**Output Summary:**
{trace.output_summary or 'No summary available'}

## Your Task

1. Analyze the goal and determine the core functionality
2. Design a clean function signature with appropriate parameters
3. Implement the function using the @llm_tool decorator
4. Include error handling and type hints
5. Add comprehensive docstrings
6. Save to: `llmos/plugins/generated/tool_{trace.goal_signature}.py`

## Important

- The tool should generalize the pattern, not just replay the exact trace
- Use async def for the function
- Return a dict with {{"success": bool, "result": any}}
- Follow all safety constraints from your system prompt

Generate the complete Python file now.
"""

        # 4. Execute with Toolsmith agent using SDK delegation
        print(f"\n🔨 Invoking Toolsmith agent...")

        # Use the shared client approach
        toolsmith = self.component_registry.get_agent("toolsmith-agent")

        if not toolsmith:
            print("[ERROR] Toolsmith agent not found")
            return None

        # Create temporary project for this operation
        temp_project = Project(
            name="crystallization",
            description="Tool crystallization workspace",
            root_path=self.workspace
        )

        # Delegate to Toolsmith using Claude Agent SDK
        # Register Toolsmith as an AgentDefinition
        agents_dict = {}
        if AgentDefinition:
            agents_dict["toolsmith-agent"] = AgentDefinition(
                description=toolsmith.description,
                prompt=toolsmith.system_prompt,
                tools=toolsmith.tools,
                model="claude-sonnet-4-5-20250929"
            )

        options = ClaudeAgentOptions(
            agents=agents_dict,
            cwd=str(self.workspace),
            permission_mode="acceptEdits"
        )

        result = None

        async with ClaudeSDKClient(options=options) as client:
            # Delegate to Toolsmith
            delegation_msg = f"Use the toolsmith-agent to {crystallization_prompt}"

            result_parts = []
            await client.query(delegation_msg)

            async for msg in client.receive_response():
                # Extract result
                if hasattr(msg, "content"):
                    for block in msg.content:
                        if hasattr(block, "text"):
                            result_parts.append(block.text)

                # Break on ResultMessage
                if "Result" in msg.__class__.__name__:
                    break

            result = "\n".join(result_parts)

        # 5. Verify file was created
        generated_tool_path = self.workspace / "llmos" / "plugins" / "generated" / f"tool_{trace.goal_signature}.py"

        if not generated_tool_path.exists():
            print(f"[ERROR] Tool file not created at: {generated_tool_path}")
            return None

        # 6. Validate syntax using ast module
        print(f"\n✅ Validating generated code...")

        try:
            import ast
            with open(generated_tool_path, 'r') as f:
                code = f.read()
            ast.parse(code)
            print("   ✓ Syntax valid")
        except SyntaxError as e:
            print(f"[ERROR] Invalid syntax in generated tool: {e}")
            return None

        # 7. Hot-load the tool
        if plugin_loader:
            print(f"\n🔥 Hot-loading tool...")
            success = plugin_loader.load_plugin_dynamically(generated_tool_path)

            if not success:
                print(f"[ERROR] Failed to hot-load tool")
                return None
        else:
            print(f"   ⚠️  No plugin loader provided - tool will be loaded on next boot")

        # 8. Mark trace as crystallized
        tool_name = f"tool_{trace.goal_signature}"
        self.trace_manager.mark_trace_as_crystallized(trace.goal_signature, tool_name)

        print(f"\n{'='*60}")
        print(f"💎 SUCCESS: Tool crystallized as '{tool_name}'")
        print(f"{'='*60}\n")

        return tool_name
