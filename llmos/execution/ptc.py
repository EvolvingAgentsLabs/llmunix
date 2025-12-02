"""
Programmatic Tool Calling (PTC) - Execution Efficiency Layer

Implements Anthropic's PTC feature for executing tool sequences outside
the context window. This is the execution backend for CRYSTALLIZED and
FOLLOWER modes.

Key Concept:
- Learning Layer (TraceManager) decides we should replay a trace
- PTC executes that trace's tool sequence in a code container
- Tool results don't hit the context window = massive token savings

Reference: https://github.com/anthropics/anthropic-cookbook/tree/main/misc/programmatic_tool_calling
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import asyncio
import json


@dataclass
class ToolCall:
    """A single tool call to be executed"""
    tool_name: str
    arguments: Dict[str, Any]
    expected_output_type: str = "any"  # "json", "text", "binary", "any"


@dataclass
class ToolSequence:
    """A sequence of tool calls from a trace"""
    calls: List[ToolCall]
    source_trace_signature: str
    created_at: datetime = field(default_factory=datetime.now)

    def to_python_code(self, tool_registry: Dict[str, str]) -> str:
        """
        Convert tool sequence to Python code for PTC execution

        Args:
            tool_registry: Map of tool_name -> function path

        Returns:
            Python code string that executes the sequence
        """
        lines = [
            "# Auto-generated from trace: " + self.source_trace_signature,
            "# Generated at: " + self.created_at.isoformat(),
            "",
            "import json",
            "results = []",
            ""
        ]

        for i, call in enumerate(self.calls):
            args_json = json.dumps(call.arguments)
            lines.extend([
                f"# Step {i + 1}: {call.tool_name}",
                f"result_{i} = await tools.{call.tool_name}(**{args_json})",
                f"results.append({{'tool': '{call.tool_name}', 'result': result_{i}}})",
                ""
            ])

        lines.append("# Return all results")
        lines.append("return results")

        return "\n".join(lines)


@dataclass
class PTCResult:
    """Result of PTC execution"""
    success: bool
    results: List[Dict[str, Any]]
    execution_time_secs: float
    tokens_saved: int  # Estimated tokens saved vs context
    error: Optional[str] = None


class PTCContainer:
    """
    Container for PTC code execution

    Manages the lifecycle of a code execution environment where
    tool calls happen outside the LLM context window.

    In production, this could be:
    - A Docker container
    - A subprocess with sandboxing
    - A cloud function
    - Claude's built-in code execution (when available)

    For now, we implement a simple async Python execution model.
    """

    def __init__(
        self,
        container_id: str,
        tools: Dict[str, Callable],
        timeout_secs: float = 120.0
    ):
        """
        Initialize PTC container

        Args:
            container_id: Unique identifier for this container
            tools: Dict of tool_name -> callable function
            timeout_secs: Execution timeout
        """
        self.container_id = container_id
        self.tools = tools
        self.timeout_secs = timeout_secs
        self.created_at = datetime.now()
        self._is_active = True

    async def execute_sequence(self, sequence: ToolSequence) -> PTCResult:
        """
        Execute a tool sequence in the container

        This is where the magic happens - tool results stay in the container
        and don't consume context tokens.

        Args:
            sequence: ToolSequence to execute

        Returns:
            PTCResult with execution details
        """
        start_time = datetime.now()
        results = []
        tokens_saved = 0

        try:
            for call in sequence.calls:
                if call.tool_name not in self.tools:
                    return PTCResult(
                        success=False,
                        results=results,
                        execution_time_secs=(datetime.now() - start_time).total_seconds(),
                        tokens_saved=tokens_saved,
                        error=f"Tool not found: {call.tool_name}"
                    )

                # Execute the tool
                tool_func = self.tools[call.tool_name]

                try:
                    # Handle both sync and async tools
                    if asyncio.iscoroutinefunction(tool_func):
                        result = await asyncio.wait_for(
                            tool_func(**call.arguments),
                            timeout=self.timeout_secs
                        )
                    else:
                        result = tool_func(**call.arguments)

                    results.append({
                        "tool": call.tool_name,
                        "arguments": call.arguments,
                        "result": result,
                        "success": True
                    })

                    # Estimate tokens saved (result would have been in context)
                    result_str = str(result)
                    tokens_saved += len(result_str) // 4  # Rough estimate

                except asyncio.TimeoutError:
                    return PTCResult(
                        success=False,
                        results=results,
                        execution_time_secs=(datetime.now() - start_time).total_seconds(),
                        tokens_saved=tokens_saved,
                        error=f"Timeout executing {call.tool_name}"
                    )
                except Exception as e:
                    return PTCResult(
                        success=False,
                        results=results,
                        execution_time_secs=(datetime.now() - start_time).total_seconds(),
                        tokens_saved=tokens_saved,
                        error=f"Error in {call.tool_name}: {str(e)}"
                    )

            return PTCResult(
                success=True,
                results=results,
                execution_time_secs=(datetime.now() - start_time).total_seconds(),
                tokens_saved=tokens_saved
            )

        except Exception as e:
            return PTCResult(
                success=False,
                results=results,
                execution_time_secs=(datetime.now() - start_time).total_seconds(),
                tokens_saved=tokens_saved,
                error=str(e)
            )

    def shutdown(self):
        """Shutdown the container"""
        self._is_active = False

    @property
    def is_active(self) -> bool:
        return self._is_active


class PTCExecutor:
    """
    High-level executor for Programmatic Tool Calling

    This is the main interface used by the Dispatcher to execute
    CRYSTALLIZED and FOLLOWER mode traces efficiently.

    Usage:
        executor = PTCExecutor(tools=registered_tools)
        result = await executor.execute_trace(trace)
    """

    # Beta header for Advanced Tool Use (Nov 2025)
    BETA_HEADER = "advanced-tool-use-2025-11-20"

    def __init__(
        self,
        tools: Dict[str, Callable],
        container_timeout_secs: float = 120.0,
        max_containers: int = 5
    ):
        """
        Initialize PTC executor

        Args:
            tools: Dict of tool_name -> callable function
            container_timeout_secs: Timeout for container execution
            max_containers: Maximum concurrent containers
        """
        self.tools = tools
        self.container_timeout_secs = container_timeout_secs
        self.max_containers = max_containers
        self._containers: Dict[str, PTCContainer] = {}
        self._container_counter = 0

    def _get_or_create_container(self, container_id: Optional[str] = None) -> PTCContainer:
        """Get existing container or create new one"""
        if container_id and container_id in self._containers:
            container = self._containers[container_id]
            if container.is_active:
                return container

        # Create new container
        self._container_counter += 1
        new_id = container_id or f"ptc-container-{self._container_counter}"

        # Clean up old containers if at limit
        if len(self._containers) >= self.max_containers:
            oldest_id = min(
                self._containers.keys(),
                key=lambda k: self._containers[k].created_at
            )
            self._containers[oldest_id].shutdown()
            del self._containers[oldest_id]

        container = PTCContainer(
            container_id=new_id,
            tools=self.tools,
            timeout_secs=self.container_timeout_secs
        )
        self._containers[new_id] = container
        return container

    async def execute_sequence(
        self,
        sequence: ToolSequence,
        container_id: Optional[str] = None
    ) -> PTCResult:
        """
        Execute a tool sequence using PTC

        Args:
            sequence: ToolSequence to execute
            container_id: Optional container ID for reuse

        Returns:
            PTCResult with execution details
        """
        container = self._get_or_create_container(container_id)
        return await container.execute_sequence(sequence)

    async def execute_from_trace(
        self,
        trace: 'ExecutionTrace',  # Forward reference
        container_id: Optional[str] = None
    ) -> PTCResult:
        """
        Execute a trace's tool sequence using PTC

        This is the main entry point for FOLLOWER mode execution.

        Args:
            trace: ExecutionTrace with tool_calls data
            container_id: Optional container ID

        Returns:
            PTCResult with execution details
        """
        # Extract tool sequence from trace
        if not hasattr(trace, 'tool_calls') or not trace.tool_calls:
            # Fallback: try to reconstruct from tools_used
            if trace.tools_used:
                # Can't execute without full call data
                return PTCResult(
                    success=False,
                    results=[],
                    execution_time_secs=0.0,
                    tokens_saved=0,
                    error="Trace missing tool_calls data - cannot replay via PTC"
                )
            else:
                return PTCResult(
                    success=False,
                    results=[],
                    execution_time_secs=0.0,
                    tokens_saved=0,
                    error="Trace has no tool calls to execute"
                )

        sequence = ToolSequence(
            calls=[
                ToolCall(
                    tool_name=call['name'],
                    arguments=call.get('arguments', {})
                )
                for call in trace.tool_calls
            ],
            source_trace_signature=trace.goal_signature
        )

        return await self.execute_sequence(sequence, container_id)

    def get_tool_definitions_for_ptc(self) -> List[Dict[str, Any]]:
        """
        Get tool definitions with PTC `allowed_callers` field

        These tool definitions tell Claude that tools can be called
        from the code execution environment.

        Returns:
            List of tool definitions with allowed_callers
        """
        definitions = []

        for tool_name, tool_func in self.tools.items():
            # Get docstring for description
            description = tool_func.__doc__ or f"Execute {tool_name}"

            # Get type hints for schema (simplified)
            import inspect
            sig = inspect.signature(tool_func)
            properties = {}
            required = []

            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue

                param_type = "string"  # Default
                if param.annotation != inspect.Parameter.empty:
                    if param.annotation == int:
                        param_type = "integer"
                    elif param.annotation == float:
                        param_type = "number"
                    elif param.annotation == bool:
                        param_type = "boolean"

                properties[param_name] = {"type": param_type}

                if param.default == inspect.Parameter.empty:
                    required.append(param_name)

            definitions.append({
                "name": tool_name,
                "description": description.strip(),
                "input_schema": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                },
                # KEY: This enables PTC
                "allowed_callers": ["code_execution_20250825"]
            })

        return definitions

    def shutdown_all(self):
        """Shutdown all containers"""
        for container in self._containers.values():
            container.shutdown()
        self._containers.clear()
