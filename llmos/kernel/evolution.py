"""
Evolution Analyzers for LLM OS

The evolution analyzers are the "intelligence" behind the sentience crons.
They analyze artifacts and propose evolutionary changes:

- **TraceEvolver**: Summarizes, consolidates, and extracts patterns from traces
- **ToolEvolver**: Proposes improvements, refactoring, and new tools
- **AgentEvolver**: Refines agent prompts and capabilities

Each evolver can work with or without an LLM:
- Without LLM: Uses heuristics and pattern matching
- With LLM: Uses LLM for deeper analysis and generation
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import re
import hashlib
import json

from .volumes import Volume, ArtifactType


@dataclass
class EvolutionProposal:
    """A proposed change to an artifact"""
    proposal_id: str
    artifact_type: ArtifactType
    artifact_id: str
    action: str  # summarize, merge, refactor, enhance, deprecate
    title: str
    description: str
    confidence: float
    estimated_impact: str
    original_content: Optional[str] = None
    proposed_content: Optional[str] = None
    related_artifacts: List[str] = field(default_factory=list)
    auto_apply: bool = False  # Can be applied without user approval

    def as_dict(self) -> Dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "artifact_type": self.artifact_type.value,
            "artifact_id": self.artifact_id,
            "action": self.action,
            "title": self.title,
            "description": self.description,
            "confidence": self.confidence,
            "estimated_impact": self.estimated_impact,
            "related_artifacts": self.related_artifacts,
            "auto_apply": self.auto_apply
        }


class TraceEvolver:
    """
    Analyzes and evolves execution traces.

    Capabilities:
    - Summarize old traces to save space
    - Detect repeated patterns across traces
    - Identify successful vs failed patterns
    - Propose trace consolidation
    - Extract reusable patterns for tools
    """

    def __init__(self, llm_callback: Optional[Callable[[str], str]] = None):
        self.llm_callback = llm_callback

    def analyze_traces(self, volume: Volume) -> Dict[str, Any]:
        """Analyze all traces in a volume"""
        trace_ids = volume.list_artifacts(ArtifactType.TRACE)

        analysis = {
            "total_traces": len(trace_ids),
            "patterns": [],
            "old_traces": [],
            "consolidation_candidates": [],
            "crystallization_candidates": []
        }

        # Group traces by goal signature
        goal_groups: Dict[str, List[Tuple[str, str]]] = {}

        for trace_id in trace_ids:
            content = volume.read_artifact(ArtifactType.TRACE, trace_id)
            if not content:
                continue

            # Extract goal from frontmatter
            goal = self._extract_goal(content)
            goal_sig = self._signature(goal) if goal else trace_id[:16]

            if goal_sig not in goal_groups:
                goal_groups[goal_sig] = []
            goal_groups[goal_sig].append((trace_id, content))

        # Find repeated patterns (crystallization candidates)
        for sig, traces in goal_groups.items():
            if len(traces) >= 3:
                success_rate = self._calculate_success_rate(traces)
                if success_rate > 0.8:
                    analysis["crystallization_candidates"].append({
                        "signature": sig,
                        "trace_count": len(traces),
                        "success_rate": success_rate,
                        "example_trace": traces[0][0]
                    })

        # Find old traces (consolidation candidates)
        for trace_id, content in [(t, c) for traces in goal_groups.values() for t, c in traces]:
            age_days = self._estimate_age_days(content)
            if age_days and age_days > 30:
                analysis["old_traces"].append({
                    "trace_id": trace_id,
                    "age_days": age_days
                })

        # Identify consolidation groups
        for sig, traces in goal_groups.items():
            if len(traces) >= 5:
                analysis["consolidation_candidates"].append({
                    "signature": sig,
                    "trace_ids": [t[0] for t in traces],
                    "count": len(traces)
                })

        return analysis

    def propose_summarization(
        self,
        volume: Volume,
        trace_ids: List[str],
        target_id: str
    ) -> Optional[EvolutionProposal]:
        """Propose summarizing multiple traces into one"""
        if len(trace_ids) < 2:
            return None

        # Read all traces
        traces = []
        for tid in trace_ids:
            content = volume.read_artifact(ArtifactType.TRACE, tid)
            if content:
                traces.append((tid, content))

        if not traces:
            return None

        # Generate summary (with or without LLM)
        if self.llm_callback:
            summary = self._llm_summarize(traces)
        else:
            summary = self._heuristic_summarize(traces)

        return EvolutionProposal(
            proposal_id=f"prop_summarize_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            artifact_type=ArtifactType.TRACE,
            artifact_id=target_id,
            action="summarize",
            title=f"Summarize {len(traces)} traces",
            description=f"Consolidate {len(traces)} similar traces into a single summary trace.",
            confidence=0.7,
            estimated_impact=f"Save ~{len(traces) - 1} trace files",
            proposed_content=summary,
            related_artifacts=trace_ids,
            auto_apply=len(traces) <= 5  # Auto-apply for small consolidations
        )

    def propose_crystallization(
        self,
        volume: Volume,
        trace_ids: List[str]
    ) -> Optional[EvolutionProposal]:
        """Propose crystallizing a repeated pattern into a tool"""
        if len(trace_ids) < 3:
            return None

        # Read traces and extract common pattern
        traces = []
        for tid in trace_ids:
            content = volume.read_artifact(ArtifactType.TRACE, tid)
            if content:
                traces.append((tid, content))

        if not traces:
            return None

        # Extract common tool sequence
        tool_pattern = self._extract_tool_pattern(traces)
        if not tool_pattern:
            return None

        # Generate tool code
        if self.llm_callback:
            tool_code = self._llm_generate_tool(traces, tool_pattern)
        else:
            tool_code = self._heuristic_generate_tool(traces, tool_pattern)

        tool_name = f"crystallized_{self._signature(tool_pattern)[:8]}"

        return EvolutionProposal(
            proposal_id=f"prop_crystallize_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            artifact_type=ArtifactType.TOOL,
            artifact_id=tool_name,
            action="crystallize",
            title=f"Create tool from {len(traces)} traces",
            description=f"Crystallize repeated pattern into reusable tool '{tool_name}'",
            confidence=0.8,
            estimated_impact="Zero-cost execution for this pattern",
            proposed_content=tool_code,
            related_artifacts=trace_ids,
            auto_apply=False  # Tools require review
        )

    def _extract_goal(self, content: str) -> Optional[str]:
        """Extract goal from trace content"""
        match = re.search(r'goal_text:\s*(.+?)(?:\n|$)', content)
        if match:
            return match.group(1).strip()
        return None

    def _signature(self, text: str) -> str:
        """Generate a signature for pattern matching"""
        normalized = re.sub(r'[^a-z0-9]', '', text.lower())
        return hashlib.md5(normalized.encode()).hexdigest()[:16]

    def _calculate_success_rate(self, traces: List[Tuple[str, str]]) -> float:
        """Calculate success rate across traces"""
        successes = 0
        for _, content in traces:
            if 'success_rating: 0.9' in content or 'success_rating: 1' in content:
                successes += 1
            elif 'success' in content.lower() and 'fail' not in content.lower():
                successes += 0.5
        return successes / len(traces) if traces else 0

    def _estimate_age_days(self, content: str) -> Optional[int]:
        """Estimate age of trace in days"""
        # Look for date patterns in content
        match = re.search(r'(\d{4}-\d{2}-\d{2})', content)
        if match:
            try:
                trace_date = datetime.strptime(match.group(1), '%Y-%m-%d')
                return (datetime.now() - trace_date).days
            except ValueError:
                pass
        return None

    def _extract_tool_pattern(self, traces: List[Tuple[str, str]]) -> Optional[str]:
        """Extract common tool call pattern from traces"""
        tool_sequences = []

        for _, content in traces:
            # Look for tool call sections
            match = re.search(r'## Tool Calls.*?```json\s*(\[.*?\])\s*```', content, re.DOTALL)
            if match:
                tool_sequences.append(match.group(1))

        if not tool_sequences:
            return None

        # Return the most common pattern (simplified)
        return tool_sequences[0] if tool_sequences else None

    def _heuristic_summarize(self, traces: List[Tuple[str, str]]) -> str:
        """Generate summary without LLM"""
        lines = [
            "---",
            f"summary_of: {len(traces)} traces",
            f"created_at: {datetime.now().isoformat()}",
            "---",
            "",
            "# Trace Summary",
            "",
            f"This is a summary of {len(traces)} similar traces.",
            "",
            "## Included Traces",
            ""
        ]
        for tid, _ in traces[:10]:
            lines.append(f"- {tid}")
        if len(traces) > 10:
            lines.append(f"- ... and {len(traces) - 10} more")

        return "\n".join(lines)

    def _heuristic_generate_tool(self, traces: List[Tuple[str, str]], pattern: str) -> str:
        """Generate tool code without LLM"""
        return f'''"""
Auto-generated tool from trace crystallization.
Generated from {len(traces)} similar traces.
"""

def execute(context):
    """
    Execute the crystallized pattern.

    This tool was automatically generated from successful trace patterns.
    Review and customize before production use.
    """
    # Tool pattern:
    # {pattern[:200]}...

    # TODO: Implement tool logic based on pattern
    raise NotImplementedError("Review and implement this crystallized tool")
'''

    def _llm_summarize(self, traces: List[Tuple[str, str]]) -> str:
        """Generate summary using LLM"""
        prompt = f"""Summarize these {len(traces)} execution traces into a single consolidated trace.
Preserve the key patterns, successful approaches, and lessons learned.

Traces:
{chr(10).join([f'--- {t[0]} ---{chr(10)}{t[1][:500]}...' for t in traces[:5]])}

Generate a markdown summary that captures the essence of these traces."""

        return self.llm_callback(prompt) if self.llm_callback else self._heuristic_summarize(traces)

    def _llm_generate_tool(self, traces: List[Tuple[str, str]], pattern: str) -> str:
        """Generate tool code using LLM"""
        prompt = f"""Generate a Python tool from this successful trace pattern.
The tool should encapsulate the common workflow seen in these traces.

Pattern:
{pattern[:500]}

Generate a Python function that implements this pattern as a reusable tool."""

        return self.llm_callback(prompt) if self.llm_callback else self._heuristic_generate_tool(traces, pattern)


class ToolEvolver:
    """
    Analyzes and evolves tools.

    Capabilities:
    - Identify unused or underused tools
    - Suggest tool refactoring
    - Propose new tools based on patterns
    - Detect tool dependencies and conflicts
    """

    def __init__(self, llm_callback: Optional[Callable[[str], str]] = None):
        self.llm_callback = llm_callback

    def analyze_tools(self, volume: Volume) -> Dict[str, Any]:
        """Analyze all tools in a volume"""
        tool_ids = volume.list_artifacts(ArtifactType.TOOL)

        analysis = {
            "total_tools": len(tool_ids),
            "tools": [],
            "improvement_candidates": [],
            "deprecation_candidates": []
        }

        for tool_id in tool_ids:
            content = volume.read_artifact(ArtifactType.TOOL, tool_id)
            if not content:
                continue

            tool_info = self._analyze_tool(tool_id, content)
            analysis["tools"].append(tool_info)

            # Check for improvement candidates
            if tool_info.get("complexity_score", 0) > 50:
                analysis["improvement_candidates"].append({
                    "tool_id": tool_id,
                    "reason": "High complexity",
                    "complexity": tool_info["complexity_score"]
                })

        return analysis

    def _analyze_tool(self, tool_id: str, content: str) -> Dict[str, Any]:
        """Analyze a single tool"""
        lines = content.split('\n')

        return {
            "tool_id": tool_id,
            "lines_of_code": len(lines),
            "has_docstring": '"""' in content or "'''" in content,
            "has_error_handling": 'try:' in content or 'except' in content,
            "complexity_score": self._estimate_complexity(content),
            "imports": self._extract_imports(content)
        }

    def _estimate_complexity(self, content: str) -> int:
        """Estimate cyclomatic complexity (simplified)"""
        complexity = 0
        complexity += content.count('if ')
        complexity += content.count('elif ')
        complexity += content.count('for ')
        complexity += content.count('while ')
        complexity += content.count('except')
        complexity += content.count(' and ')
        complexity += content.count(' or ')
        return complexity

    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements"""
        imports = []
        for line in content.split('\n'):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                imports.append(line.strip())
        return imports

    def propose_improvement(
        self,
        volume: Volume,
        tool_id: str
    ) -> Optional[EvolutionProposal]:
        """Propose improvement for a tool"""
        content = volume.read_artifact(ArtifactType.TOOL, tool_id)
        if not content:
            return None

        analysis = self._analyze_tool(tool_id, content)
        improvements = []

        if not analysis["has_docstring"]:
            improvements.append("Add documentation")

        if not analysis["has_error_handling"]:
            improvements.append("Add error handling")

        if analysis["complexity_score"] > 30:
            improvements.append("Reduce complexity by refactoring")

        if not improvements:
            return None

        return EvolutionProposal(
            proposal_id=f"prop_improve_{tool_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            artifact_type=ArtifactType.TOOL,
            artifact_id=tool_id,
            action="enhance",
            title=f"Improve tool: {tool_id}",
            description=f"Suggested improvements: {', '.join(improvements)}",
            confidence=0.6,
            estimated_impact="Better maintainability and reliability",
            original_content=content,
            auto_apply=False
        )


class AgentEvolver:
    """
    Analyzes and evolves agent definitions.

    Capabilities:
    - Analyze agent prompts for clarity
    - Suggest capability expansions
    - Identify overlapping agents
    - Propose agent consolidation
    """

    def __init__(self, llm_callback: Optional[Callable[[str], str]] = None):
        self.llm_callback = llm_callback

    def analyze_agents(self, volume: Volume) -> Dict[str, Any]:
        """Analyze all agents in a volume"""
        agent_ids = volume.list_artifacts(ArtifactType.AGENT)

        analysis = {
            "total_agents": len(agent_ids),
            "agents": [],
            "overlap_candidates": [],
            "enhancement_candidates": []
        }

        agent_capabilities: Dict[str, List[str]] = {}

        for agent_id in agent_ids:
            content = volume.read_artifact(ArtifactType.AGENT, agent_id)
            if not content:
                continue

            agent_info = self._analyze_agent(agent_id, content)
            analysis["agents"].append(agent_info)
            agent_capabilities[agent_id] = agent_info.get("tools", [])

        # Find overlapping agents
        for agent1, tools1 in agent_capabilities.items():
            for agent2, tools2 in agent_capabilities.items():
                if agent1 >= agent2:
                    continue
                overlap = set(tools1) & set(tools2)
                if len(overlap) > 2:
                    analysis["overlap_candidates"].append({
                        "agents": [agent1, agent2],
                        "overlapping_tools": list(overlap)
                    })

        return analysis

    def _analyze_agent(self, agent_id: str, content: str) -> Dict[str, Any]:
        """Analyze a single agent"""
        # Parse frontmatter
        tools = []
        model = "unknown"
        description = ""

        match = re.search(r'tools:\s*\[(.*?)\]', content)
        if match:
            tools = [t.strip().strip('"\'') for t in match.group(1).split(',')]

        match = re.search(r'model:\s*(.+?)(?:\n|$)', content)
        if match:
            model = match.group(1).strip()

        match = re.search(r'description:\s*(.+?)(?:\n|$)', content)
        if match:
            description = match.group(1).strip()

        return {
            "agent_id": agent_id,
            "tools": tools,
            "model": model,
            "description": description,
            "prompt_length": len(content)
        }

    def propose_enhancement(
        self,
        volume: Volume,
        agent_id: str
    ) -> Optional[EvolutionProposal]:
        """Propose enhancement for an agent"""
        content = volume.read_artifact(ArtifactType.AGENT, agent_id)
        if not content:
            return None

        analysis = self._analyze_agent(agent_id, content)
        enhancements = []

        if not analysis["description"]:
            enhancements.append("Add description")

        if len(analysis["tools"]) == 0:
            enhancements.append("Specify tools")

        if analysis["prompt_length"] < 200:
            enhancements.append("Expand system prompt for better guidance")

        if not enhancements:
            return None

        return EvolutionProposal(
            proposal_id=f"prop_enhance_{agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            artifact_type=ArtifactType.AGENT,
            artifact_id=agent_id,
            action="enhance",
            title=f"Enhance agent: {agent_id}",
            description=f"Suggested enhancements: {', '.join(enhancements)}",
            confidence=0.5,
            estimated_impact="More effective agent behavior",
            original_content=content,
            auto_apply=False
        )


class EvolutionEngine:
    """
    Orchestrates evolution across all artifact types.

    This is the main entry point for the sentience crons to trigger
    evolution analysis and proposals.
    """

    def __init__(self, llm_callback: Optional[Callable[[str], str]] = None):
        self.trace_evolver = TraceEvolver(llm_callback)
        self.tool_evolver = ToolEvolver(llm_callback)
        self.agent_evolver = AgentEvolver(llm_callback)
        self.llm_callback = llm_callback

    def full_analysis(self, volume: Volume) -> Dict[str, Any]:
        """Run full analysis on a volume"""
        return {
            "volume": volume.volume_type.value,
            "owner": volume.owner_id,
            "analyzed_at": datetime.now().isoformat(),
            "traces": self.trace_evolver.analyze_traces(volume),
            "tools": self.tool_evolver.analyze_tools(volume),
            "agents": self.agent_evolver.analyze_agents(volume)
        }

    def generate_proposals(self, volume: Volume) -> List[EvolutionProposal]:
        """Generate all evolution proposals for a volume"""
        proposals = []

        # Trace proposals
        trace_analysis = self.trace_evolver.analyze_traces(volume)

        for candidate in trace_analysis.get("consolidation_candidates", []):
            prop = self.trace_evolver.propose_summarization(
                volume,
                candidate["trace_ids"],
                f"summary_{candidate['signature']}"
            )
            if prop:
                proposals.append(prop)

        for candidate in trace_analysis.get("crystallization_candidates", []):
            trace_ids = [candidate["example_trace"]]  # Simplified
            prop = self.trace_evolver.propose_crystallization(volume, trace_ids)
            if prop:
                proposals.append(prop)

        # Tool proposals
        tool_analysis = self.tool_evolver.analyze_tools(volume)

        for candidate in tool_analysis.get("improvement_candidates", []):
            prop = self.tool_evolver.propose_improvement(volume, candidate["tool_id"])
            if prop:
                proposals.append(prop)

        # Agent proposals
        agent_analysis = self.agent_evolver.analyze_agents(volume)

        for agent in agent_analysis.get("agents", []):
            prop = self.agent_evolver.propose_enhancement(volume, agent["agent_id"])
            if prop:
                proposals.append(prop)

        return proposals

    def apply_proposal(
        self,
        volume: Volume,
        proposal: EvolutionProposal,
        cron_level: str
    ) -> bool:
        """Apply an evolution proposal"""
        if proposal.proposed_content is None:
            return False

        is_new = proposal.action in ["crystallize", "summarize"]

        return volume.write_artifact(
            artifact_type=proposal.artifact_type,
            artifact_id=proposal.artifact_id,
            content=proposal.proposed_content,
            reason=f"Applied proposal: {proposal.title}",
            cron_level=cron_level,
            is_new=is_new
        )
