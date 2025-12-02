"""
Tool Examples Generator - Learning from Successful Traces

Implements Anthropic's Tool Use Examples feature by auto-generating
`input_examples` from successful execution traces.

Key Concept:
- Learning Layer (TraceManager) stores successful executions
- This module extracts tool call patterns from those traces
- Generated examples help Claude use tools correctly the first time
- Bridges the gap between Learning and Execution layers

The flow:
1. Trace succeeds with tool X (Learning Layer records this)
2. ToolExampleGenerator extracts the tool call data
3. Next time tool X is loaded, it includes real examples
4. Claude sees how the tool was successfully used before
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from datetime import datetime
import json

if TYPE_CHECKING:
    from memory.traces_sdk import TraceManager, ExecutionTrace


@dataclass
class ToolExample:
    """
    A single example of successful tool usage

    This maps to Anthropic's input_examples format.
    """
    description: str
    arguments: Dict[str, Any]
    source_goal: str  # Where this example came from
    success_rate: float  # How reliable this pattern is
    usage_count: int  # How often this pattern was used

    def to_api_format(self) -> Dict[str, Any]:
        """Convert to Anthropic API input_examples format"""
        return {
            "description": self.description,
            "arguments": self.arguments
        }


class ToolExampleGenerator:
    """
    Generates tool examples from execution traces

    This is the bridge between the Learning Layer (traces) and
    Execution Layer (tool definitions with examples).

    Usage:
        generator = ToolExampleGenerator(trace_manager)

        # Get examples for a specific tool
        examples = generator.get_examples_for_tool("write_file")

        # Enhance a tool definition with examples
        enhanced_def = generator.enhance_tool_definition(tool_def)
    """

    def __init__(
        self,
        trace_manager: 'TraceManager',
        min_success_rate: float = 0.9,
        max_examples_per_tool: int = 3
    ):
        """
        Initialize the generator

        Args:
            trace_manager: TraceManager for accessing execution history
            min_success_rate: Minimum trace success rate to extract examples from
            max_examples_per_tool: Maximum examples to include per tool
        """
        self.trace_manager = trace_manager
        self.min_success_rate = min_success_rate
        self.max_examples_per_tool = max_examples_per_tool

        # Cache of generated examples
        self._example_cache: Dict[str, List[ToolExample]] = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl_secs = 300  # 5 minute cache

    def _is_cache_valid(self) -> bool:
        """Check if the example cache is still valid"""
        if not self._cache_timestamp:
            return False
        age = (datetime.now() - self._cache_timestamp).total_seconds()
        return age < self._cache_ttl_secs

    def _extract_tool_calls_from_trace(
        self,
        trace: 'ExecutionTrace'
    ) -> List[Dict[str, Any]]:
        """
        Extract tool call data from a trace

        Args:
            trace: ExecutionTrace to extract from

        Returns:
            List of tool call dicts with name and arguments
        """
        # If trace has full tool_calls data, use it
        if hasattr(trace, 'tool_calls') and trace.tool_calls:
            return trace.tool_calls

        # Otherwise, we can only get tool names (no arguments)
        # This is a limitation - we need traces with full call data
        return []

    def get_examples_for_tool(
        self,
        tool_name: str,
        force_refresh: bool = False
    ) -> List[ToolExample]:
        """
        Get usage examples for a specific tool from traces

        Args:
            tool_name: Name of the tool
            force_refresh: Force cache refresh

        Returns:
            List of ToolExample instances
        """
        # Check cache
        if not force_refresh and self._is_cache_valid():
            if tool_name in self._example_cache:
                return self._example_cache[tool_name]

        # Get all traces
        traces = self.trace_manager.list_traces()

        # Filter for successful traces that used this tool
        relevant_traces = [
            t for t in traces
            if t.success_rating >= self.min_success_rate
            and t.tools_used
            and tool_name in t.tools_used
        ]

        if not relevant_traces:
            return []

        # Extract examples from traces
        examples = []
        seen_patterns = set()  # Avoid duplicate patterns

        for trace in relevant_traces:
            tool_calls = self._extract_tool_calls_from_trace(trace)

            for call in tool_calls:
                if call.get('name') != tool_name:
                    continue

                arguments = call.get('arguments', {})
                if not arguments:
                    continue

                # Create a pattern hash to detect duplicates
                pattern_hash = json.dumps(
                    sorted(arguments.keys())
                )

                if pattern_hash in seen_patterns:
                    continue
                seen_patterns.add(pattern_hash)

                # Create example
                example = ToolExample(
                    description=f"From: {trace.goal_text[:50]}...",
                    arguments=arguments,
                    source_goal=trace.goal_text,
                    success_rate=trace.success_rating,
                    usage_count=trace.usage_count
                )
                examples.append(example)

                if len(examples) >= self.max_examples_per_tool:
                    break

            if len(examples) >= self.max_examples_per_tool:
                break

        # Sort by usage count (most used patterns first)
        examples.sort(key=lambda e: e.usage_count, reverse=True)

        # Update cache
        self._example_cache[tool_name] = examples[:self.max_examples_per_tool]
        self._cache_timestamp = datetime.now()

        return self._example_cache[tool_name]

    def enhance_tool_definition(
        self,
        tool_definition: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enhance a tool definition with examples from traces

        Args:
            tool_definition: Original tool definition dict

        Returns:
            Enhanced definition with input_examples
        """
        tool_name = tool_definition.get('name')
        if not tool_name:
            return tool_definition

        examples = self.get_examples_for_tool(tool_name)

        if not examples:
            return tool_definition

        # Create enhanced copy
        enhanced = tool_definition.copy()
        enhanced['input_examples'] = [
            e.to_api_format() for e in examples
        ]

        return enhanced

    def enhance_tool_definitions(
        self,
        tool_definitions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Enhance multiple tool definitions with examples

        Args:
            tool_definitions: List of tool definition dicts

        Returns:
            List of enhanced definitions
        """
        return [
            self.enhance_tool_definition(t) for t in tool_definitions
        ]

    def get_all_examples(self) -> Dict[str, List[ToolExample]]:
        """
        Get examples for all tools found in traces

        Returns:
            Dict mapping tool_name -> List[ToolExample]
        """
        # Get all unique tools from traces
        traces = self.trace_manager.list_traces()
        all_tools = set()

        for trace in traces:
            if trace.tools_used:
                all_tools.update(trace.tools_used)

        # Get examples for each tool
        result = {}
        for tool_name in all_tools:
            examples = self.get_examples_for_tool(tool_name)
            if examples:
                result[tool_name] = examples

        return result

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about generated examples"""
        all_examples = self.get_all_examples()

        total_examples = sum(len(ex) for ex in all_examples.values())

        return {
            "tools_with_examples": len(all_examples),
            "total_examples": total_examples,
            "cache_valid": self._is_cache_valid(),
            "min_success_rate": self.min_success_rate,
            "max_examples_per_tool": self.max_examples_per_tool
        }

    def clear_cache(self) -> None:
        """Clear the example cache"""
        self._example_cache.clear()
        self._cache_timestamp = None


class TraceToolCallRecorder:
    """
    Helper to record tool calls during execution for later example generation

    Use this during LEARNER mode execution to capture full tool call data
    that can later be used to generate examples.
    """

    def __init__(self):
        self.tool_calls: List[Dict[str, Any]] = []

    def record_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        result: Any = None,
        success: bool = True
    ) -> None:
        """
        Record a tool call

        Args:
            tool_name: Name of the tool
            arguments: Arguments passed to the tool
            result: Optional result (for context)
            success: Whether the call succeeded
        """
        self.tool_calls.append({
            "name": tool_name,
            "arguments": arguments,
            "success": success,
            "timestamp": datetime.now().isoformat()
        })

    def get_calls(self) -> List[Dict[str, Any]]:
        """Get all recorded calls"""
        return self.tool_calls.copy()

    def clear(self) -> None:
        """Clear recorded calls"""
        self.tool_calls.clear()
