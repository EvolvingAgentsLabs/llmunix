"""
Execution Traces - SDK Memory-based Implementation
Stores execution traces as markdown files in /memories/traces/

Aligned with Claude Agent SDK's file-based memory approach.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
import re

from memory.sdk_memory import SDKMemoryTool
from memory.trace_analyzer import TraceAnalyzer, TraceMatch


@dataclass
class ExecutionTrace:
    """
    Execution trace stored as markdown

    Represents a learned execution pattern that can be reused
    in Follower mode.

    Architecture:
        - Learning Layer uses traces to decide mode (FOLLOWER vs LEARNER)
        - Execution Layer uses tool_calls for PTC replay (if available)

    The tool_calls field enables Programmatic Tool Calling (PTC):
        - Stores full tool call details (name + arguments)
        - Allows zero-context replay via code execution
        - Critical for Anthropic's Advanced Tool Use integration
    """
    goal_signature: str  # Hash of normalized goal
    goal_text: str  # Original goal text
    success_rating: float  # 0.0 to 1.0
    usage_count: int  # How many times this trace was used
    created_at: datetime
    last_used: Optional[datetime]
    estimated_cost_usd: float
    estimated_time_secs: float
    mode: str  # "LEARNER", "FOLLOWER", "ORCHESTRATOR", "CRYSTALLIZED"

    # Optional metadata
    tools_used: List[str] = None  # List of tool names (for quick filtering)
    output_summary: str = ""
    error_notes: str = ""
    crystallized_into_tool: Optional[str] = None  # Name of generated tool (HOPE architecture)

    # PTC (Programmatic Tool Calling) support
    # This enables zero-context replay via Anthropic's Advanced Tool Use
    tool_calls: Optional[List[Dict[str, Any]]] = None  # Full tool call data: [{name, arguments}, ...]

    def to_markdown(self) -> str:
        """Convert trace to markdown format"""
        import json

        lines = [
            f"# Execution Trace: {self.goal_text}",
            "",
            "## Metadata",
            f"- **Goal Signature**: `{self.goal_signature}`",
            f"- **Success Rating**: {self.success_rating:.0%}",
            f"- **Usage Count**: {self.usage_count}",
            f"- **Mode**: {self.mode}",
            f"- **Created**: {self.created_at.isoformat()}",
            f"- **Last Used**: {self.last_used.isoformat() if self.last_used else 'Never'}",
            f"- **Estimated Cost**: ${self.estimated_cost_usd:.4f}",
            f"- **Estimated Time**: {self.estimated_time_secs:.1f}s",
        ]

        if self.crystallized_into_tool:
            lines.append(f"- **Crystallized Tool**: `{self.crystallized_into_tool}` 💎")

        # Indicate PTC capability
        if self.tool_calls:
            lines.append(f"- **PTC Enabled**: Yes ({len(self.tool_calls)} calls)")

        lines.append("")

        if self.tools_used:
            lines.extend([
                "## Tools Used",
                "",
                "```",
                ", ".join(self.tools_used),
                "```",
                ""
            ])

        # Store full tool calls for PTC replay
        if self.tool_calls:
            lines.extend([
                "## Tool Calls (PTC)",
                "",
                "```json",
                json.dumps(self.tool_calls, indent=2),
                "```",
                ""
            ])

        if self.output_summary:
            lines.extend([
                "## Output Summary",
                "",
                self.output_summary,
                ""
            ])

        if self.error_notes:
            lines.extend([
                "## Error Notes",
                "",
                self.error_notes,
                ""
            ])

        return "\n".join(lines)

    @classmethod
    def from_markdown(cls, content: str) -> 'ExecutionTrace':
        """Parse trace from markdown"""
        import json

        lines = content.splitlines()

        # Extract metadata
        metadata = {}
        tools_used = []
        tool_calls = None
        output_summary = ""
        error_notes = ""

        current_section = None
        section_lines = []
        in_json_block = False
        json_lines = []

        for line in lines:
            # Section headers
            if line.startswith("## "):
                # Process previous section
                if current_section and section_lines:
                    if current_section == "Output Summary":
                        output_summary = "\n".join(section_lines).strip()
                    elif current_section == "Error Notes":
                        error_notes = "\n".join(section_lines).strip()

                # Handle JSON block end for Tool Calls
                if current_section == "Tool Calls (PTC)" and json_lines:
                    try:
                        tool_calls = json.loads("\n".join(json_lines))
                    except json.JSONDecodeError:
                        pass
                    json_lines = []

                current_section = line[3:].strip()
                section_lines = []
                in_json_block = False
                continue

            # Metadata parsing
            if current_section == "Metadata" and line.startswith("- **"):
                match = re.match(r"- \*\*(.+?)\*\*: (.+)", line)
                if match:
                    key, value = match.groups()
                    metadata[key] = value.strip('`')

            # Tools Used parsing
            elif current_section == "Tools Used" and line.strip() and line.strip() != "```":
                tools_used = [t.strip() for t in line.split(",")]

            # Tool Calls (PTC) JSON parsing
            elif current_section == "Tool Calls (PTC)":
                if line.strip() == "```json":
                    in_json_block = True
                    continue
                elif line.strip() == "```":
                    in_json_block = False
                    if json_lines:
                        try:
                            tool_calls = json.loads("\n".join(json_lines))
                        except json.JSONDecodeError:
                            pass
                        json_lines = []
                elif in_json_block:
                    json_lines.append(line)

            # Content accumulation for other sections
            elif current_section in ["Output Summary", "Error Notes"]:
                section_lines.append(line)

        # Handle last section
        if current_section == "Output Summary" and section_lines:
            output_summary = "\n".join(section_lines).strip()
        elif current_section == "Error Notes" and section_lines:
            error_notes = "\n".join(section_lines).strip()
        elif current_section == "Tool Calls (PTC)" and json_lines:
            try:
                tool_calls = json.loads("\n".join(json_lines))
            except json.JSONDecodeError:
                pass

        # Extract goal from title
        goal_text = lines[0].replace("# Execution Trace: ", "").strip() if lines else "Unknown"

        # Extract crystallized tool name (remove emoji if present)
        crystallized_tool = metadata.get("Crystallized Tool", "").rstrip(" 💎").strip() or None

        return cls(
            goal_signature=metadata.get("Goal Signature", ""),
            goal_text=goal_text,
            success_rating=float(metadata.get("Success Rating", "0%").rstrip('%')) / 100.0,
            usage_count=int(metadata.get("Usage Count", "0")),
            created_at=datetime.fromisoformat(metadata.get("Created", datetime.now().isoformat())),
            last_used=datetime.fromisoformat(metadata["Last Used"]) if metadata.get("Last Used") != "Never" else None,
            estimated_cost_usd=float(metadata.get("Estimated Cost", "$0").lstrip('$')),
            estimated_time_secs=float(metadata.get("Estimated Time", "0s").rstrip('s')),
            mode=metadata.get("Mode", "LEARNER"),
            tools_used=tools_used if tools_used else None,
            output_summary=output_summary,
            error_notes=error_notes,
            crystallized_into_tool=crystallized_tool,
            tool_calls=tool_calls
        )


class TraceManager:
    """
    Manages execution traces using SDK memory

    Stores traces as markdown files in /memories/traces/
    """

    def __init__(
        self,
        memories_dir: Path,
        workspace: Optional[Path] = None,
        enable_llm_matching: bool = True
    ):
        """
        Initialize trace manager

        Args:
            memories_dir: Root /memories directory
            workspace: Workspace directory (for LLM analysis)
            enable_llm_matching: Enable LLM-based semantic matching
        """
        self.memories_dir = Path(memories_dir)
        self.traces_dir = "traces"  # Relative to /memories
        self.enable_llm_matching = enable_llm_matching

        # Initialize SDK Memory Tool
        self.memory_tool = SDKMemoryTool(self.memories_dir)

        # Initialize LLM-based trace analyzer
        self.trace_analyzer: Optional[TraceAnalyzer] = None
        if enable_llm_matching:
            try:
                workspace = workspace or Path.cwd()
                self.trace_analyzer = TraceAnalyzer(workspace)
            except RuntimeError as e:
                print(f"[WARNING] Could not initialize TraceAnalyzer: {e}")
                print("          Falling back to hash-based matching only")
                self.enable_llm_matching = False

        # Ensure traces directory exists
        (self.memories_dir / self.traces_dir).mkdir(parents=True, exist_ok=True)

    def _normalize_goal(self, goal: str) -> str:
        """Normalize goal text for signature"""
        # Lowercase, remove punctuation, collapse whitespace
        normalized = goal.lower()
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized

    def _compute_signature(self, goal: str) -> str:
        """Compute signature for goal"""
        normalized = self._normalize_goal(goal)
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]

    def _get_trace_filename(self, goal_signature: str, goal_text: str) -> str:
        """
        Generate filename for trace

        Format: {signature}_{sanitized_goal}.md
        """
        # Sanitize goal text for filename
        sanitized = re.sub(r'[^\w\s-]', '', goal_text.lower())
        sanitized = re.sub(r'[\s]+', '_', sanitized)[:50]  # Max 50 chars

        return f"{goal_signature}_{sanitized}.md"

    def save_trace(self, trace: ExecutionTrace) -> bool:
        """
        Save execution trace

        Args:
            trace: ExecutionTrace to save

        Returns:
            True if saved successfully
        """
        filename = self._get_trace_filename(trace.goal_signature, trace.goal_text)
        file_path = f"{self.traces_dir}/{filename}"

        content = trace.to_markdown()

        if self.memory_tool.exists(file_path):
            # Update existing trace
            self.memory_tool.str_replace(
                file_path,
                self.memory_tool.view(file_path),
                content
            )
        else:
            # Create new trace
            self.memory_tool.create(file_path, content)

        return True

    def find_trace(
        self,
        goal: str,
        min_confidence: float = 0.9
    ) -> Optional[ExecutionTrace]:
        """
        Find trace for goal using hash-based exact matching

        This is the legacy method. For semantic matching, use find_trace_with_llm().

        Args:
            goal: Goal to search for
            min_confidence: Minimum success rating threshold

        Returns:
            ExecutionTrace if found, None otherwise
        """
        signature = self._compute_signature(goal)

        # Look for exact signature match first
        traces = self.list_traces()

        for trace in traces:
            if trace.goal_signature == signature and trace.success_rating >= min_confidence:
                return trace

        return None

    async def find_trace_with_llm(
        self,
        goal: str,
        min_confidence: float = 0.75,
        fallback_to_hash: bool = True
    ) -> Optional[Tuple[ExecutionTrace, float]]:
        """
        Find trace using LLM-based semantic matching

        This implements "soft" associative memory:
        - Understands semantic equivalence ("create file" ≈ "create a file")
        - Returns confidence score for intelligent mode selection
        - Falls back to hash matching if LLM analysis unavailable

        Args:
            goal: Goal to search for
            min_confidence: Minimum confidence threshold (0.0-1.0)
            fallback_to_hash: Fall back to hash matching if LLM unavailable

        Returns:
            Tuple of (ExecutionTrace, confidence_score) if found, None otherwise
        """
        # Try LLM-based matching first
        if self.enable_llm_matching and self.trace_analyzer:
            traces = self.list_traces()

            if not traces:
                return None

            try:
                match = await self.trace_analyzer.find_best_matching_trace(
                    goal=goal,
                    traces=traces,
                    min_confidence=min_confidence
                )

                if match:
                    # Find the matching trace
                    for trace in traces:
                        if trace.goal_signature == match.trace_signature:
                            print(f"[LLM Match] Confidence: {match.confidence:.0%}, Mode: {match.recommended_mode}")
                            print(f"[LLM Match] Reasoning: {match.reasoning}")
                            return (trace, match.confidence)

            except Exception as e:
                print(f"[WARNING] LLM trace matching failed: {e}")
                if not fallback_to_hash:
                    return None

        # Fallback to hash-based matching
        if fallback_to_hash:
            trace = self.find_trace(goal, min_confidence=0.9)
            if trace:
                print("[Hash Match] Exact signature match found")
                return (trace, 1.0)  # Hash match = 100% confidence

        return None

    async def find_trace_smart(
        self,
        goal: str
    ) -> Tuple[Optional[ExecutionTrace], float, str]:
        """
        Smart trace finding with automatic mode detection

        Combines LLM and hash matching with intelligent mode recommendation.

        Returns:
            Tuple of (trace, confidence, recommended_mode)
            - trace: ExecutionTrace if found, None otherwise
            - confidence: 0.0-1.0 confidence score
            - recommended_mode: "FOLLOWER", "MIXED", or "LEARNER"
        """
        result = await self.find_trace_with_llm(goal, min_confidence=0.75)

        if result:
            trace, confidence = result

            # Determine mode based on confidence
            if confidence >= 0.92:
                mode = "FOLLOWER"
            elif confidence >= 0.75:
                mode = "MIXED"
            else:
                mode = "LEARNER"

            return (trace, confidence, mode)

        return (None, 0.0, "LEARNER")

    def list_traces(self) -> List[ExecutionTrace]:
        """
        List all traces

        Returns:
            List of ExecutionTrace instances
        """
        traces = []

        files = self.memory_tool.list_files(self.traces_dir, pattern="*.md")

        for file in files:
            try:
                trace = ExecutionTrace.from_markdown(file.content)
                traces.append(trace)
            except Exception as e:
                print(f"Warning: Could not parse trace {file.name}: {e}")

        return traces

    def update_usage(self, goal_signature: str):
        """
        Update usage count for a trace

        Args:
            goal_signature: Trace signature to update
        """
        traces = self.list_traces()

        for trace in traces:
            if trace.goal_signature == goal_signature:
                trace.usage_count += 1
                trace.last_used = datetime.now()
                self.save_trace(trace)
                break

    def search_traces(
        self,
        query: str,
        limit: int = 5,
        min_confidence: float = 0.7
    ) -> List[ExecutionTrace]:
        """
        Search traces by keyword

        Args:
            query: Search query
            limit: Maximum results
            min_confidence: Minimum confidence

        Returns:
            List of matching traces
        """
        # Use SDK memory search
        files = self.memory_tool.search(query, directory=self.traces_dir)

        traces = []
        for file in files[:limit]:
            try:
                trace = ExecutionTrace.from_markdown(file.content)
                if trace.success_rating >= min_confidence:
                    traces.append(trace)
            except Exception as e:
                print(f"Warning: Could not parse trace {file.name}: {e}")

        return traces

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get trace statistics

        Returns:
            Dictionary with statistics
        """
        traces = self.list_traces()

        if not traces:
            return {
                "total_traces": 0,
                "avg_success_rate": 0.0,
                "total_usage": 0,
                "high_confidence_count": 0
            }

        total_usage = sum(t.usage_count for t in traces)
        avg_success = sum(t.success_rating for t in traces) / len(traces)
        high_confidence = len([t for t in traces if t.success_rating >= 0.9])

        return {
            "total_traces": len(traces),
            "avg_success_rate": avg_success,
            "total_usage": total_usage,
            "high_confidence_count": high_confidence,
            "total_cost": sum(t.estimated_cost_usd for t in traces),
            "total_time": sum(t.estimated_time_secs for t in traces)
        }

    def delete_trace(self, goal_signature: str) -> bool:
        """
        Delete a trace

        Args:
            goal_signature: Signature of trace to delete

        Returns:
            True if deleted
        """
        traces = self.list_traces()

        for trace in traces:
            if trace.goal_signature == goal_signature:
                filename = self._get_trace_filename(trace.goal_signature, trace.goal_text)
                file_path = f"{self.traces_dir}/{filename}"
                self.memory_tool.delete(file_path)
                return True

        return False

    def mark_trace_as_crystallized(self, goal_signature: str, tool_name: str) -> bool:
        """
        Mark a trace as crystallized into a tool (HOPE architecture)

        This updates the trace to indicate it has been converted into a permanent Python tool.
        When a crystallized trace is found, the Dispatcher will execute the tool directly
        instead of replaying the trace or using LLM reasoning.

        Args:
            goal_signature: Signature of trace to mark
            tool_name: Name of the generated tool

        Returns:
            True if marked successfully
        """
        traces = self.list_traces()

        for trace in traces:
            if trace.goal_signature == goal_signature:
                trace.crystallized_into_tool = tool_name
                trace.mode = "CRYSTALLIZED"  # New mode for crystallized traces
                self.save_trace(trace)
                print(f"💎 Trace crystallized into tool: {tool_name}")
                return True

        return False

    def get_crystallized_traces(self) -> List[Tuple[ExecutionTrace, str]]:
        """
        Get all traces that have been crystallized into tools

        Returns:
            List of (trace, tool_name) tuples
        """
        traces = self.list_traces()
        crystallized = []

        for trace in traces:
            if trace.crystallized_into_tool:
                crystallized.append((trace, trace.crystallized_into_tool))

        return crystallized
