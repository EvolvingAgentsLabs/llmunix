"""
Cross-Project Learning - SDK Memory Implementation
Extract insights across project boundaries using file-based memory
"""

from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from collections import defaultdict

from memory.traces_sdk import TraceManager, ExecutionTrace
from memory.sdk_memory import SDKMemoryTool
from kernel.project_manager import ProjectManager, Project


@dataclass
class CrossProjectInsight:
    """Insight extracted from cross-project analysis"""
    insight_type: str  # "common_pattern", "reusable_agent", "successful_strategy", "anti_pattern"
    title: str
    description: str
    projects_involved: List[str]  # Project names
    evidence: List[str]  # Supporting evidence
    confidence: float  # 0.0 to 1.0
    impact: str  # "high", "medium", "low"
    recommendation: str  # What to do with this insight


@dataclass
class ReusableAgent:
    """Agent pattern that could be reused across projects"""
    agent_name: str
    category: str
    description: str
    success_rate: float
    usage_count: int
    projects_used: List[str]
    capabilities: List[str]
    recommended_for: List[str]  # Types of tasks


@dataclass
class SuccessfulStrategy:
    """Successful execution strategy observed across projects"""
    strategy_type: str
    description: str
    success_rate: float
    projects: List[str]
    applicable_to: List[str]  # Types of goals/tasks
    key_factors: List[str]


class CrossProjectLearning:
    """
    Cross-Project Learning using SDK Memory

    Analyzes execution history across all projects to extract
    insights without requiring embeddings - uses file-based search.
    """

    def __init__(
        self,
        project_manager: ProjectManager,
        workspace: Path
    ):
        """
        Initialize cross-project learning

        Args:
            project_manager: Project manager instance
            workspace: Workspace directory
        """
        self.project_manager = project_manager
        self.workspace = Path(workspace)
        self.memories_dir = self.workspace / "memories"

        # Initialize SDK Memory Tool
        self.memory_tool = SDKMemoryTool(self.memories_dir)

        # Cache for project traces
        self._project_traces_cache: Dict[str, List[ExecutionTrace]] = {}

    def _get_project_traces(self, project: Project) -> List[ExecutionTrace]:
        """Get all traces for a project"""
        if project.name in self._project_traces_cache:
            return self._project_traces_cache[project.name]

        # Load traces from project memory (stored in /memories/projects/{name}/traces/)
        project_memories = self.memories_dir / "projects" / project.name
        if not project_memories.exists():
            return []

        trace_manager = TraceManager(
            memories_dir=self.memories_dir,
            workspace=self.workspace,
            enable_llm_matching=False  # Disable for cross-project (optional optimization)
        )

        # List traces specific to this project
        traces = []
        project_trace_files = self.memory_tool.list_files(
            f"projects/{project.name}/traces",
            pattern="*.md"
        )

        for file in project_trace_files:
            try:
                trace = ExecutionTrace.from_markdown(file.content)
                traces.append(trace)
            except Exception as e:
                print(f"Warning: Could not parse trace {file.name}: {e}")

        self._project_traces_cache[project.name] = traces
        return traces

    def _get_all_traces(self) -> Dict[str, List[ExecutionTrace]]:
        """Get traces from all projects"""
        all_traces = {}

        for project in self.project_manager.list_projects():
            traces = self._get_project_traces(project)
            if traces:
                all_traces[project.name] = traces

        return all_traces

    async def analyze_common_patterns(
        self,
        min_projects: int = 2,
        min_confidence: float = 0.7
    ) -> List[CrossProjectInsight]:
        """
        Analyze patterns that appear across multiple projects

        Args:
            min_projects: Minimum number of projects for a pattern
            min_confidence: Minimum confidence threshold

        Returns:
            List of cross-project insights
        """
        insights = []
        all_traces = self._get_all_traces()

        if len(all_traces) < min_projects:
            return []

        # Pattern 1: Common goal types across projects
        goal_patterns = defaultdict(lambda: {"projects": set(), "traces": []})

        for project_name, traces in all_traces.items():
            for trace in traces:
                # Extract first word as goal type
                goal_type = trace.goal_text.split()[0] if trace.goal_text else "Unknown"
                goal_patterns[goal_type]["projects"].add(project_name)
                goal_patterns[goal_type]["traces"].append(trace)

        # Find patterns that appear in multiple projects
        for goal_type, data in goal_patterns.items():
            if len(data["projects"]) >= min_projects:
                traces = data["traces"]
                avg_success = sum(t.success_rating for t in traces) / len(traces)

                if avg_success >= min_confidence:
                    insights.append(CrossProjectInsight(
                        insight_type="common_pattern",
                        title=f"Common Task Type: {goal_type}",
                        description=f"'{goal_type}' tasks appear across {len(data['projects'])} projects",
                        projects_involved=list(data["projects"]),
                        evidence=[
                            f"{len(traces)} executions",
                            f"Average success rate: {avg_success:.0%}",
                            f"Projects: {', '.join(data['projects'])}"
                        ],
                        confidence=avg_success,
                        impact="high" if len(data["projects"]) >= 3 else "medium",
                        recommendation=f"Consider creating specialized '{goal_type}' agent for reuse"
                    ))

        # Pattern 2: Cost-intensive patterns
        for project_name, traces in all_traces.items():
            high_cost_traces = [t for t in traces if t.estimated_cost_usd > 1.0]
            if len(high_cost_traces) >= 3:
                avg_cost = sum(t.estimated_cost_usd for t in high_cost_traces) / len(high_cost_traces)

                insights.append(CrossProjectInsight(
                    insight_type="anti_pattern",
                    title=f"High-cost operations in {project_name}",
                    description=f"Multiple expensive operations detected (avg ${avg_cost:.2f})",
                    projects_involved=[project_name],
                    evidence=[
                        f"{len(high_cost_traces)} high-cost executions",
                        f"Average cost: ${avg_cost:.2f}",
                        f"Total cost: ${sum(t.estimated_cost_usd for t in high_cost_traces):.2f}"
                    ],
                    confidence=0.9,
                    impact="high",
                    recommendation="Consider breaking down tasks or using cheaper models"
                ))

        return insights

    async def identify_reusable_agents(
        self,
        min_success_rate: float = 0.8,
        min_usage_count: int = 3
    ) -> List[ReusableAgent]:
        """
        Identify agent patterns that could be reused

        Args:
            min_success_rate: Minimum success rate
            min_usage_count: Minimum usage count

        Returns:
            List of reusable agent patterns
        """
        reusable_agents = []
        all_traces = self._get_all_traces()

        # Group traces by goal signature pattern
        agent_patterns = defaultdict(lambda: {
            "traces": [],
            "projects": set(),
            "goal_types": set()
        })

        for project_name, traces in all_traces.items():
            for trace in traces:
                # Extract goal pattern (first 2-3 words)
                words = trace.goal_text.split()[:3]
                pattern = " ".join(words) if words else "Unknown"

                agent_patterns[pattern]["traces"].append(trace)
                agent_patterns[pattern]["projects"].add(project_name)

                # Extract goal type
                if words:
                    agent_patterns[pattern]["goal_types"].add(words[0])

        # Identify high-performing patterns
        for pattern, data in agent_patterns.items():
            traces = data["traces"]

            if len(traces) >= min_usage_count:
                success_rate = sum(t.success_rating for t in traces) / len(traces)

                if success_rate >= min_success_rate:
                    # Infer agent category from goal types
                    goal_types = list(data["goal_types"])
                    category = self._infer_category(pattern, goal_types)

                    reusable_agents.append(ReusableAgent(
                        agent_name=f"{pattern.lower().replace(' ', '-')}-agent",
                        category=category,
                        description=f"Handles tasks like '{pattern}'",
                        success_rate=success_rate,
                        usage_count=len(traces),
                        projects_used=list(data["projects"]),
                        capabilities=[f"{goal_type} operations" for goal_type in goal_types],
                        recommended_for=[
                            f"Tasks starting with '{pattern}'",
                            f"{category} operations"
                        ]
                    ))

        # Sort by success rate and usage count
        reusable_agents.sort(key=lambda a: (a.success_rate, a.usage_count), reverse=True)

        return reusable_agents

    async def extract_successful_strategies(
        self,
        min_success_rate: float = 0.9,
        min_projects: int = 2
    ) -> List[SuccessfulStrategy]:
        """
        Extract successful execution strategies across projects

        Args:
            min_success_rate: Minimum success rate
            min_projects: Minimum number of projects

        Returns:
            List of successful strategies
        """
        strategies = []
        all_traces = self._get_all_traces()

        # Strategy 1: Quick execution (< 30 seconds) with high success
        quick_traces = defaultdict(list)
        for project_name, traces in all_traces.items():
            for trace in traces:
                if trace.estimated_time_secs < 30 and trace.success_rating >= min_success_rate:
                    quick_traces[project_name].append(trace)

        if len(quick_traces) >= min_projects:
            all_quick = [t for traces in quick_traces.values() for t in traces]
            avg_success = sum(t.success_rating for t in all_quick) / len(all_quick)

            strategies.append(SuccessfulStrategy(
                strategy_type="quick_execution",
                description="Fast execution with high success rate",
                success_rate=avg_success,
                projects=list(quick_traces.keys()),
                applicable_to=["Simple tasks", "Well-defined operations"],
                key_factors=[
                    "Clear goal definition",
                    "Existing trace available (Follower mode)",
                    "Simple single-step operations"
                ]
            ))

        # Strategy 2: Follower mode success
        follower_traces = defaultdict(list)
        for project_name, traces in all_traces.items():
            for trace in traces:
                # High success with usage suggests Follower mode
                if (trace.success_rating >= 0.95 and
                    trace.usage_count > 1):
                    follower_traces[project_name].append(trace)

        if len(follower_traces) >= min_projects:
            all_follower = [t for traces in follower_traces.values() for t in traces]
            avg_success = sum(t.success_rating for t in all_follower) / len(all_follower)

            strategies.append(SuccessfulStrategy(
                strategy_type="follower_mode",
                description="Zero-cost Follower mode execution",
                success_rate=avg_success,
                projects=list(follower_traces.keys()),
                applicable_to=["Repeated tasks", "Proven workflows"],
                key_factors=[
                    "High-quality trace available",
                    "Similar goal to past execution",
                    "Stable environment/requirements"
                ]
            ))

        return strategies

    async def get_cross_project_recommendations(
        self,
        current_project: Optional[Project] = None,
        goal: Optional[str] = None
    ) -> List[str]:
        """
        Get recommendations based on cross-project learning

        Args:
            current_project: Current project context
            goal: Optional goal to get recommendations for

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Get insights
        patterns = await self.analyze_common_patterns()
        reusable_agents = await self.identify_reusable_agents()
        strategies = await self.extract_successful_strategies()

        # Recommendation 1: Suggest reusable agents
        if reusable_agents and goal:
            top_agent = reusable_agents[0]
            if any(pattern in goal.lower() for pattern in top_agent.agent_name.split('-')):
                recommendations.append(
                    f"💡 Consider using '{top_agent.agent_name}' pattern - "
                    f"{top_agent.success_rate:.0%} success rate across {len(top_agent.projects_used)} projects"
                )

        # Recommendation 2: Common patterns
        if patterns:
            for pattern in patterns[:2]:  # Top 2
                if pattern.insight_type == "common_pattern":
                    recommendations.append(
                        f"🔄 {pattern.title} - {pattern.recommendation}"
                    )
                elif pattern.insight_type == "anti_pattern":
                    recommendations.append(
                        f"⚠️  {pattern.title} - {pattern.recommendation}"
                    )

        # Recommendation 3: Learning from other projects
        all_traces = self._get_all_traces()
        if len(all_traces) > 1:
            recommendations.append(
                f"📚 Learning from {len(all_traces)} projects - "
                f"{sum(len(traces) for traces in all_traces.values())} total executions"
            )

        return recommendations

    def _infer_category(self, pattern: str, goal_types: List[str]) -> str:
        """Infer agent category from pattern and goal types"""
        pattern_lower = pattern.lower()

        # Category mapping
        if any(word in pattern_lower for word in ["analyze", "data", "statistics"]):
            return "data_analysis"
        elif any(word in pattern_lower for word in ["create", "build", "generate"]):
            return "creation"
        elif any(word in pattern_lower for word in ["research", "search", "find"]):
            return "research"
        elif any(word in pattern_lower for word in ["write", "document", "report"]):
            return "documentation"
        elif any(word in pattern_lower for word in ["test", "verify", "check"]):
            return "testing"
        elif any(word in pattern_lower for word in ["fix", "debug", "resolve"]):
            return "debugging"
        else:
            return "general"

    async def get_project_learning_summary(self, project: Project) -> Dict[str, Any]:
        """
        Get learning summary for a specific project

        Args:
            project: Project to summarize

        Returns:
            Dictionary with learning insights
        """
        traces = self._get_project_traces(project)

        if not traces:
            return {
                "project": project.name,
                "total_executions": 0,
                "insights": []
            }

        # Calculate statistics
        total_cost = sum(t.estimated_cost_usd for t in traces)
        total_time = sum(t.estimated_time_secs for t in traces)
        avg_success = sum(t.success_rating for t in traces) / len(traces)
        high_success_count = len([t for t in traces if t.success_rating >= 0.9])

        # Identify top patterns
        goal_types = defaultdict(int)
        for trace in traces:
            goal_type = trace.goal_text.split()[0] if trace.goal_text else "Unknown"
            goal_types[goal_type] += 1

        top_patterns = sorted(goal_types.items(), key=lambda x: x[1], reverse=True)[:3]

        return {
            "project": project.name,
            "total_executions": len(traces),
            "total_cost": total_cost,
            "total_time": total_time,
            "avg_success_rate": avg_success,
            "high_confidence_traces": high_success_count,
            "top_patterns": [
                {"type": goal_type, "count": count}
                for goal_type, count in top_patterns
            ],
            "follower_mode_available": high_success_count > 0,
            "insights": [
                f"Most common task: {top_patterns[0][0]} ({top_patterns[0][1]} times)" if top_patterns else "No patterns yet",
                f"Average success rate: {avg_success:.0%}",
                f"Total cost: ${total_cost:.2f}",
                f"{high_success_count} high-confidence traces available for Follower mode"
            ]
        }

    def clear_cache(self):
        """Clear the project traces cache"""
        self._project_traces_cache.clear()

    async def identify_crystallization_candidates(
        self,
        min_usage: int = 5,
        min_success: float = 0.95
    ) -> List[Dict[str, Any]]:
        """
        Identify traces that are stable enough to be crystallized into Python tools.

        This implements the HOPE (Self-Modifying Kernel) protocol from the Nested Learning paper.
        Traces meeting the criteria are candidates for conversion from fluid intelligence (LLM)
        to crystallized intelligence (Python code).

        Criteria for crystallization:
        1. High usage count (≥ min_usage) - Pattern is frequently needed
        2. High success rating (≥ min_success) - Pattern is stable and proven
        3. Mode is FOLLOWER - Already proven to work reliably

        Args:
            min_usage: Minimum usage count (default: 5)
            min_success: Minimum success rating (default: 0.95)

        Returns:
            List of crystallization candidate dictionaries
        """
        candidates = []
        all_traces = self._get_all_traces()

        for project_name, traces in all_traces.items():
            for trace in traces:
                # Check crystallization criteria
                if (trace.usage_count >= min_usage and
                    trace.success_rating >= min_success and
                    not trace.crystallized_into_tool):  # Not already crystallized

                    candidates.append({
                        "goal": trace.goal_text,
                        "signature": trace.goal_signature,
                        "project": project_name,
                        "usage_count": trace.usage_count,
                        "success_rating": trace.success_rating,
                        "estimated_cost_usd": trace.estimated_cost_usd,
                        "estimated_time_secs": trace.estimated_time_secs,
                        "tools_used": trace.tools_used or [],
                        "output_summary": trace.output_summary or "",
                        "crystallization_priority": self._calculate_crystallization_priority(trace)
                    })

        # Sort by priority (highest first)
        candidates.sort(key=lambda c: c["crystallization_priority"], reverse=True)

        return candidates

    def _calculate_crystallization_priority(self, trace: ExecutionTrace) -> float:
        """
        Calculate crystallization priority score for a trace.

        Higher scores indicate higher value in crystallizing this pattern.

        Factors:
        - Usage frequency (more uses = higher priority)
        - Cost savings potential (expensive traces save more when crystallized)
        - Success rate (more reliable = higher priority)

        Returns:
            Priority score (0.0-100.0+)
        """
        # Usage weight: 10 points per use
        usage_score = trace.usage_count * 10

        # Cost weight: $0.50 = 50 points (potential savings from crystallization)
        cost_score = trace.estimated_cost_usd * 100

        # Success weight: 95% = 95 points
        success_score = trace.success_rating * 100

        # Combined score with weights
        priority = (
            usage_score * 0.5 +      # 50% weight on usage
            cost_score * 0.3 +        # 30% weight on cost savings
            success_score * 0.2       # 20% weight on reliability
        )

        return priority
