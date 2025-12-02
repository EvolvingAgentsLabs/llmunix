"""
Memory Query Interface - SDK-based Implementation
Keyword-based search without embeddings, using SDK memory

Provides intelligent memory consultation using file-based search.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from memory.traces_sdk import TraceManager, ExecutionTrace
from memory.store_sdk import MemoryStore


@dataclass
class MemoryInsight:
    """Insight extracted from memory"""
    insight_type: str  # "pattern", "recommendation", "warning", "success_factor"
    description: str
    evidence: List[str]  # Supporting evidence from past executions
    confidence: float  # 0.0 to 1.0
    relevance: float  # 0.0 to 1.0 (to current goal)


@dataclass
class FailurePattern:
    """Pattern of failures"""
    pattern_type: str  # "tool_error", "timeout", "constraint_violation"
    description: str
    occurrences: int
    affected_traces: List[str]  # Trace signatures
    mitigation: str  # How to avoid


class MemoryQueryInterface:
    """
    SDK-based Memory Query Interface

    Provides keyword-based search over past executions,
    pattern recognition, and recommendations.

    No embeddings - uses fast file-based keyword matching.
    """

    def __init__(
        self,
        trace_manager: TraceManager,
        memory_store: MemoryStore
    ):
        """
        Initialize Memory Query Interface

        Args:
            trace_manager: Trace manager (SDK-based)
            memory_store: Memory store (SDK-based)
        """
        self.trace_manager = trace_manager
        self.memory_store = memory_store

    async def find_similar_tasks(
        self,
        goal: str,
        limit: int = 5,
        min_confidence: float = 0.7
    ) -> List[ExecutionTrace]:
        """
        Find similar past executions using keyword matching

        Args:
            goal: Goal to search for
            limit: Maximum number of results
            min_confidence: Minimum success rating

        Returns:
            List of similar ExecutionTrace instances
        """
        # Use trace manager's keyword search
        traces = self.trace_manager.search_traces(
            query=goal,
            limit=limit * 2,  # Get more for filtering
            min_confidence=min_confidence
        )

        # Return top results
        return traces[:limit]

    async def get_recommendations(
        self,
        goal: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Get recommendations based on historical performance

        Args:
            goal: Goal to get recommendations for
            context: Optional context information

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Find similar tasks
        similar = await self.find_similar_tasks(goal, limit=3)

        if similar:
            # Extract recommendations from similar tasks
            for trace in similar:
                if trace.success_rating > 0.9:
                    recommendations.append(
                        f"High success rate ({trace.success_rating:.0%}) "
                        f"for similar task: '{trace.goal_text[:50]}...'"
                    )

                if trace.usage_count > 5:
                    recommendations.append(
                        f"Task similar to '{trace.goal_text[:50]}...' "
                        f"has been executed {trace.usage_count} times successfully"
                    )

        # Generic recommendations based on patterns
        if not similar:
            recommendations.append(
                "Novel task - no similar executions found. "
                "Will use Learner mode and create new trace."
            )

        return recommendations

    async def analyze_failures(
        self,
        pattern: Optional[str] = None
    ) -> List[FailurePattern]:
        """
        Analyze failure patterns across executions

        Args:
            pattern: Optional pattern to filter

        Returns:
            List of FailurePattern instances
        """
        failure_patterns = []

        # Get all traces
        all_traces = self.trace_manager.list_traces()

        # Filter low-success traces
        failed_traces = [
            t for t in all_traces
            if t.success_rating < 0.5
        ]

        if not failed_traces:
            return []

        # Group by common patterns
        goal_failures: Dict[str, List[ExecutionTrace]] = {}
        for trace in failed_traces:
            key = trace.goal_text[:50]  # First 50 chars as key
            if key not in goal_failures:
                goal_failures[key] = []
            goal_failures[key].append(trace)

        for goal_prefix, traces in goal_failures.items():
            if len(traces) >= 2:
                failure_patterns.append(FailurePattern(
                    pattern_type="repeated_failure",
                    description=f"Multiple failures for goals starting with '{goal_prefix}'",
                    occurrences=len(traces),
                    affected_traces=[t.goal_signature for t in traces],
                    mitigation="Consider breaking down the task or creating specialized agent"
                ))

        return failure_patterns

    async def extract_patterns(
        self,
        category: Optional[str] = None
    ) -> List[MemoryInsight]:
        """
        Extract patterns from memory

        Args:
            category: Optional category filter

        Returns:
            List of MemoryInsight instances
        """
        insights = []

        # Get all traces
        all_traces = self.trace_manager.list_traces()

        # Pattern 1: Frequently executed tasks
        frequent_traces = [
            t for t in all_traces
            if t.usage_count >= 5
        ]

        for trace in frequent_traces:
            insights.append(MemoryInsight(
                insight_type="pattern",
                description=f"Frequent task: {trace.goal_text[:50]}",
                evidence=[
                    f"Executed {trace.usage_count} times",
                    f"Success rate: {trace.success_rating:.0%}"
                ],
                confidence=0.9,
                relevance=0.5
            ))

        # Pattern 2: High-success patterns
        high_success = [
            t for t in all_traces
            if t.success_rating > 0.95 and t.usage_count >= 3
        ]

        for trace in high_success[:3]:  # Top 3
            insights.append(MemoryInsight(
                insight_type="success_factor",
                description=f"Proven approach: {trace.goal_text[:50]}",
                evidence=[
                    f"Success rate: {trace.success_rating:.0%}",
                    f"Used {trace.usage_count} times"
                ],
                confidence=0.95,
                relevance=0.7
            ))

        # Pattern 3: Recent trends
        recent_traces = sorted(
            all_traces,
            key=lambda t: t.last_used or t.created_at,
            reverse=True
        )[:10]

        if recent_traces:
            insights.append(MemoryInsight(
                insight_type="pattern",
                description="Recent activity focused on: " +
                           ", ".join(set(t.goal_text.split()[0] for t in recent_traces[:5] if t.goal_text)),
                evidence=[f"Last 10 executions analyzed"],
                confidence=0.7,
                relevance=0.8
            ))

        return insights

    async def get_optimization_suggestions(
        self,
        goal: str
    ) -> List[str]:
        """
        Get optimization suggestions based on past performance

        Args:
            goal: Goal to optimize

        Returns:
            List of suggestion strings
        """
        suggestions = []

        # Find similar tasks
        similar = await self.find_similar_tasks(goal, limit=5, min_confidence=0.7)

        if similar:
            # Check if Follower mode is available
            high_confidence = [t for t in similar if t.success_rating >= 0.9]
            if high_confidence:
                suggestions.append(
                    "✅ Follower mode available - can execute at $0 cost using proven trace"
                )

            # Check for frequent patterns
            frequent = [t for t in similar if t.usage_count >= 5]
            if frequent:
                suggestions.append(
                    "📊 This type of task is executed frequently - "
                    "consider creating dedicated specialized agent"
                )

            # Cost optimization
            avg_cost = sum(t.estimated_cost_usd for t in similar) / len(similar)
            if avg_cost > 0.5:
                suggestions.append(
                    f"💰 Average cost for similar tasks: ${avg_cost:.2f} - "
                    "consider optimizing or using cheaper model"
                )

            # Time optimization
            avg_time = sum(t.estimated_time_secs for t in similar) / len(similar)
            if avg_time > 60:
                suggestions.append(
                    f"⏱️ Average time for similar tasks: {avg_time:.0f}s - "
                    "consider breaking into smaller steps"
                )

        else:
            suggestions.append(
                "🆕 Novel task - will use Learner mode. "
                "Future executions can use Follower mode at $0 cost."
            )

        return suggestions

    async def should_use_follower_mode(
        self,
        goal: str,
        confidence_threshold: float = 0.9
    ) -> tuple[bool, Optional[ExecutionTrace]]:
        """
        Determine if Follower mode should be used

        Args:
            goal: Goal to check
            confidence_threshold: Minimum confidence required

        Returns:
            Tuple of (should_use_follower, trace)
        """
        trace = self.trace_manager.find_trace(goal, confidence_threshold)

        if trace and trace.success_rating >= confidence_threshold:
            return True, trace

        return False, None

    def get_memory_statistics(self) -> Dict[str, Any]:
        """
        Get memory statistics

        Returns:
            Dictionary with memory stats
        """
        # Get trace statistics
        trace_stats = self.trace_manager.get_statistics()

        # Get store statistics
        store_stats = self.memory_store.get_statistics()

        return {
            **trace_stats,
            **store_stats,
            "follower_mode_available": trace_stats["high_confidence_count"] > 0
        }
