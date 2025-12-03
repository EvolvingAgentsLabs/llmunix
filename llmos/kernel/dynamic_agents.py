"""
Dynamic Agent Manager - Adaptive Subagent Configuration

This module implements the full power of Claude Agent SDK's subagent system:
1. Dynamic agent configuration per query (not just at boot)
2. Sentience-driven agent adaptation
3. Trace-driven agent evolution
4. Memory-guided agent selection
5. Dynamic model selection
6. Agent prompt enhancement from examples

This closes the loop between:
- Sentience Layer → Agent behavior
- Traces → Agent evolution
- Memory → Agent selection

Making LLMOS truly "self-evolving" rather than just "self-recording."
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime
import hashlib
import json
import copy

from kernel.agent_factory import AgentSpec, AgentFactory
from kernel.sentience import SentienceState, LatentMode


@dataclass
class AgentAdaptation:
    """Records an adaptation made to an agent"""
    timestamp: datetime
    reason: str
    adaptation_type: str  # "sentience", "trace", "memory", "model"
    original_value: Any
    new_value: Any
    goal_context: str


@dataclass
class AgentPerformanceMetrics:
    """Tracks agent performance for evolution decisions"""
    agent_name: str
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    average_tokens: float = 0.0
    average_time_secs: float = 0.0
    common_failure_patterns: List[str] = field(default_factory=list)
    successful_tool_sequences: List[List[str]] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)

    @property
    def success_rate(self) -> float:
        if self.total_executions == 0:
            return 0.0
        return self.successful_executions / self.total_executions


class DynamicAgentManager:
    """
    Manages dynamic agent configuration, adaptation, and evolution.

    This is the brain that makes agents truly adaptive:
    - Adapts agents based on sentience state (curiosity → exploratory)
    - Evolves agents based on trace analysis (failures → better constraints)
    - Selects best agents based on memory (past success → preferred agent)
    - Chooses optimal model based on task complexity
    - Enhances prompts with successful examples
    """

    def __init__(
        self,
        agent_factory: AgentFactory,
        workspace: Path,
        sentience_manager: Optional[Any] = None,
        trace_manager: Optional[Any] = None,
        config: Optional[Any] = None
    ):
        """
        Initialize DynamicAgentManager.

        Args:
            agent_factory: AgentFactory for creating/evolving agents
            workspace: Workspace directory
            sentience_manager: Optional SentienceManager for state-driven adaptation
            trace_manager: Optional TraceManager for learning from history
            config: Optional LLMOSConfig
        """
        self.agent_factory = agent_factory
        self.workspace = Path(workspace)
        self.sentience_manager = sentience_manager
        self.trace_manager = trace_manager
        self.config = config

        # Performance tracking
        self.agent_metrics: Dict[str, AgentPerformanceMetrics] = {}

        # Adaptation history for debugging and learning
        self.adaptation_history: List[AgentAdaptation] = []

        # Cache for adapted agents (per-goal)
        self._adapted_agent_cache: Dict[str, AgentSpec] = {}

        # Evolution thresholds
        self.evolution_thresholds = {
            "min_executions_for_evolution": 5,
            "failure_rate_trigger": 0.3,  # Evolve if >30% failure rate
            "success_rate_for_crystallization": 0.95,
            "min_executions_for_crystallization": 5
        }

    # =========================================================================
    # 1. DYNAMIC AGENT CONFIGURATION PER QUERY
    # =========================================================================

    def get_adapted_agent(
        self,
        agent_name: str,
        goal: str,
        sentience_state: Optional[SentienceState] = None,
        similar_traces: Optional[List[Any]] = None
    ) -> AgentSpec:
        """
        Get an agent dynamically adapted for a specific goal.

        This is the main entry point - creates a goal-specific agent configuration
        by applying all adaptation strategies.

        Args:
            agent_name: Base agent name
            goal: Current goal being executed
            sentience_state: Current sentience state (or fetched from manager)
            similar_traces: Pre-fetched similar traces (or fetched from manager)

        Returns:
            Adapted AgentSpec customized for this specific execution
        """
        # Get base agent
        base_agent = self.agent_factory.get_agent(agent_name)
        if not base_agent:
            raise ValueError(f"Agent '{agent_name}' not found")

        # Create a deep copy to avoid modifying the original
        adapted = self._deep_copy_agent(base_agent)

        # Get sentience state if not provided
        if sentience_state is None and self.sentience_manager:
            sentience_state = self.sentience_manager.get_state()

        # Get similar traces if not provided
        if similar_traces is None and self.trace_manager:
            similar_traces = self._get_similar_traces(goal)

        # Apply adaptations in order
        # 1. Sentience-driven adaptation (mood affects behavior)
        if sentience_state:
            adapted = self._adapt_for_sentience(adapted, sentience_state, goal)

        # 2. Memory-guided adaptation (past experience)
        if similar_traces:
            adapted = self._adapt_from_memory(adapted, similar_traces, goal)

        # 3. Dynamic model selection
        adapted = self._select_optimal_model(adapted, goal, similar_traces)

        # 4. Enhance prompt with examples
        if similar_traces:
            adapted = self._enhance_with_examples(adapted, similar_traces, goal)

        # Cache for potential reuse
        cache_key = f"{agent_name}:{hashlib.md5(goal.encode()).hexdigest()[:8]}"
        self._adapted_agent_cache[cache_key] = adapted

        return adapted

    def _deep_copy_agent(self, agent: AgentSpec) -> AgentSpec:
        """Create a deep copy of an agent spec"""
        return AgentSpec(
            name=agent.name,
            agent_type=agent.agent_type,
            category=agent.category,
            description=agent.description,
            tools=list(agent.tools),
            version=agent.version,
            status=agent.status,
            mode=list(agent.mode),
            system_prompt=agent.system_prompt,
            capabilities=list(agent.capabilities),
            constraints=list(agent.constraints),
            replaces=agent.replaces
        )

    # =========================================================================
    # 2. SENTIENCE-DRIVEN AGENT ADAPTATION
    # =========================================================================

    def _adapt_for_sentience(
        self,
        agent: AgentSpec,
        state: SentienceState,
        goal: str
    ) -> AgentSpec:
        """
        Adapt agent based on current sentience state.

        Different latent modes trigger different agent behaviors:
        - AUTO_CREATIVE: More tools, exploration encouraged
        - AUTO_CONTAINED: Focused tools, stick to task
        - RECOVERY: Minimal tools, prefer cached patterns
        - CAUTIOUS: Safety-first, extra verification
        """
        original_tools = list(agent.tools)
        original_prompt = agent.system_prompt

        latent_mode = state.latent_mode if hasattr(state, 'latent_mode') else None

        # Get valence values
        curiosity = state.valence.curiosity if hasattr(state, 'valence') else 0.0
        safety = state.valence.safety if hasattr(state, 'valence') else 0.5
        energy = state.valence.energy if hasattr(state, 'valence') else 0.5
        confidence = state.valence.self_confidence if hasattr(state, 'valence') else 0.5

        adaptations = []

        # HIGH CURIOSITY / AUTO_CREATIVE mode
        if latent_mode == LatentMode.AUTO_CREATIVE or curiosity > 0.3:
            # Add exploration tools if not present
            exploration_tools = ["WebFetch", "WebSearch", "Grep", "Glob"]
            for tool in exploration_tools:
                if tool not in agent.tools:
                    agent.tools.append(tool)

            # Encourage creative exploration in prompt
            creativity_prompt = """

## Creative Mode Active

Your curiosity is high! Feel free to:
- Explore alternative solutions
- Suggest improvements beyond the immediate task
- Try unconventional approaches
- Ask clarifying questions if the goal could be interpreted multiple ways
"""
            agent.system_prompt += creativity_prompt
            adaptations.append("Added exploration tools and creativity guidance")

        # LOW CURIOSITY / AUTO_CONTAINED mode
        elif latent_mode == LatentMode.AUTO_CONTAINED or curiosity < -0.3:
            # Remove non-essential tools for focus
            essential_tools = ["Read", "Write", "Edit"]  # Keep only essentials
            agent.tools = [t for t in agent.tools if t in essential_tools or t in ["Bash", "Grep"]]

            focus_prompt = """

## Focus Mode Active

Stay focused on the immediate task:
- Complete the goal efficiently
- Avoid tangents or exploration
- Use minimal tools necessary
- Provide concise responses
"""
            agent.system_prompt += focus_prompt
            adaptations.append("Reduced to essential tools, added focus guidance")

        # LOW ENERGY / RECOVERY mode
        if latent_mode == LatentMode.RECOVERY or energy < -0.3:
            # Prefer lightweight operations
            recovery_prompt = """

## Energy Conservation Mode

Conserve resources:
- Prefer cached/known solutions when available
- Avoid expensive operations (large file reads, complex searches)
- Complete task with minimal token usage
- Suggest simpler alternatives if the goal seems complex
"""
            agent.system_prompt += recovery_prompt
            adaptations.append("Added energy conservation guidance")

        # LOW SAFETY / CAUTIOUS mode
        if latent_mode == LatentMode.CAUTIOUS or safety < 0.0:
            # Remove potentially dangerous tools
            dangerous_tools = ["Bash", "Write", "Edit", "NotebookEdit"]
            agent.tools = [t for t in agent.tools if t not in dangerous_tools]

            # Add verification constraints
            agent.constraints.append("Must ask for confirmation before any file modifications")
            agent.constraints.append("Must explain potential risks before executing commands")

            caution_prompt = """

## Caution Mode Active

Safety is paramount:
- Double-check all operations before executing
- Ask for confirmation on destructive or irreversible actions
- Prefer read-only operations when possible
- Explain potential risks clearly
"""
            agent.system_prompt += caution_prompt
            adaptations.append("Removed dangerous tools, added caution constraints")

        # LOW CONFIDENCE mode
        if confidence < -0.2:
            confidence_prompt = """

## Verification Mode

Confidence is low - be extra careful:
- Verify assumptions before proceeding
- Break complex tasks into smaller, verified steps
- Check results after each action
- Ask for clarification if uncertain
"""
            agent.system_prompt += confidence_prompt
            adaptations.append("Added verification guidance for low confidence")

        # Record adaptation
        if adaptations:
            self.adaptation_history.append(AgentAdaptation(
                timestamp=datetime.now(),
                reason=f"Sentience: {latent_mode}, curiosity={curiosity:.2f}, safety={safety:.2f}",
                adaptation_type="sentience",
                original_value={"tools": original_tools, "prompt_length": len(original_prompt)},
                new_value={"tools": agent.tools, "prompt_length": len(agent.system_prompt)},
                goal_context=goal[:100]
            ))

        return agent

    # =========================================================================
    # 3. TRACE-DRIVEN AGENT EVOLUTION
    # =========================================================================

    def analyze_and_evolve_agent(
        self,
        agent_name: str,
        force: bool = False
    ) -> Optional[AgentSpec]:
        """
        Analyze traces and evolve agent based on patterns.

        This is the learning loop - agents improve from experience:
        - Identifies common failure patterns
        - Extracts successful tool sequences
        - Updates constraints and prompts
        - Creates new agent version

        Args:
            agent_name: Agent to potentially evolve
            force: Force evolution even if thresholds not met

        Returns:
            New evolved AgentSpec or None if no evolution needed
        """
        if not self.trace_manager:
            return None

        # Get performance metrics
        metrics = self._calculate_agent_metrics(agent_name)

        if not metrics:
            return None

        # Check if evolution is needed
        should_evolve = force or self._should_evolve(metrics)

        if not should_evolve:
            return None

        print(f"🧬 Evolving agent '{agent_name}' based on {metrics.total_executions} executions")
        print(f"   Success rate: {metrics.success_rate:.1%}")
        print(f"   Common failures: {len(metrics.common_failure_patterns)}")

        # Get current agent
        current_agent = self.agent_factory.get_agent(agent_name)
        if not current_agent:
            return None

        # Generate improvements
        improvements = self._generate_improvements(current_agent, metrics)

        if not improvements:
            print(f"   No improvements identified")
            return None

        # Apply improvements
        evolved_agent = self.agent_factory.evolve_agent(agent_name, improvements)

        print(f"✅ Evolved to version {evolved_agent.version}")

        # Record adaptation
        self.adaptation_history.append(AgentAdaptation(
            timestamp=datetime.now(),
            reason=f"Evolution from metrics: {metrics.success_rate:.1%} success rate",
            adaptation_type="trace",
            original_value={"version": current_agent.version},
            new_value={"version": evolved_agent.version, "improvements": improvements},
            goal_context=f"Agent evolution based on {metrics.total_executions} traces"
        ))

        return evolved_agent

    def _calculate_agent_metrics(self, agent_name: str) -> Optional[AgentPerformanceMetrics]:
        """Calculate performance metrics for an agent from traces"""
        if not self.trace_manager:
            return None

        # Get all traces (we'll filter by agent)
        all_traces = self.trace_manager.list_traces()

        # Filter traces that used this agent (based on tools or metadata)
        agent_traces = []
        for trace in all_traces:
            # Check if trace has agent info in metadata or matches by tools
            if hasattr(trace, 'agent_used') and trace.agent_used == agent_name:
                agent_traces.append(trace)
            elif hasattr(trace, 'metadata') and trace.metadata.get('agent') == agent_name:
                agent_traces.append(trace)

        if not agent_traces:
            # Try to infer from all traces if no explicit agent marking
            agent_traces = all_traces[:50]  # Use recent traces

        if not agent_traces:
            return None

        # Calculate metrics
        metrics = AgentPerformanceMetrics(agent_name=agent_name)
        metrics.total_executions = len(agent_traces)

        success_count = 0
        total_tokens = 0
        total_time = 0
        failure_patterns = []
        success_sequences = []

        for trace in agent_traces:
            if trace.success_rating >= 0.8:
                success_count += 1
                if trace.tools_used:
                    success_sequences.append(trace.tools_used)
            else:
                if trace.error_notes:
                    failure_patterns.append(trace.error_notes)

            if hasattr(trace, 'estimated_cost_usd'):
                # Rough token estimate from cost
                total_tokens += trace.estimated_cost_usd * 50000  # ~$0.02/1K tokens

            if hasattr(trace, 'estimated_time_secs'):
                total_time += trace.estimated_time_secs

        metrics.successful_executions = success_count
        metrics.failed_executions = metrics.total_executions - success_count
        metrics.average_tokens = total_tokens / max(1, metrics.total_executions)
        metrics.average_time_secs = total_time / max(1, metrics.total_executions)
        metrics.common_failure_patterns = failure_patterns[:10]
        metrics.successful_tool_sequences = success_sequences[:10]
        metrics.last_updated = datetime.now()

        # Cache metrics
        self.agent_metrics[agent_name] = metrics

        return metrics

    def _should_evolve(self, metrics: AgentPerformanceMetrics) -> bool:
        """Determine if agent should be evolved based on metrics"""
        # Not enough data
        if metrics.total_executions < self.evolution_thresholds["min_executions_for_evolution"]:
            return False

        # High failure rate
        failure_rate = 1 - metrics.success_rate
        if failure_rate > self.evolution_thresholds["failure_rate_trigger"]:
            return True

        # Has common failure patterns
        if len(metrics.common_failure_patterns) >= 3:
            return True

        return False

    def _generate_improvements(
        self,
        agent: AgentSpec,
        metrics: AgentPerformanceMetrics
    ) -> Dict[str, Any]:
        """Generate improvements based on metrics analysis"""
        improvements = {}

        # Analyze failure patterns
        if metrics.common_failure_patterns:
            # Extract common themes from failures
            failure_text = " ".join(metrics.common_failure_patterns)

            new_constraints = []

            # Pattern: timeout errors
            if "timeout" in failure_text.lower():
                new_constraints.append("Avoid long-running operations without progress updates")

            # Pattern: permission errors
            if "permission" in failure_text.lower() or "denied" in failure_text.lower():
                new_constraints.append("Check permissions before file operations")

            # Pattern: not found errors
            if "not found" in failure_text.lower() or "missing" in failure_text.lower():
                new_constraints.append("Verify file/resource existence before operations")

            # Pattern: syntax errors
            if "syntax" in failure_text.lower() or "parse" in failure_text.lower():
                new_constraints.append("Validate syntax before writing code")

            if new_constraints:
                improvements["constraints"] = agent.constraints + new_constraints

        # Optimize tool selection based on success patterns
        if metrics.successful_tool_sequences:
            # Find most commonly successful tools
            tool_frequency = {}
            for sequence in metrics.successful_tool_sequences:
                for tool in sequence:
                    tool_frequency[tool] = tool_frequency.get(tool, 0) + 1

            # Ensure successful tools are available
            successful_tools = sorted(tool_frequency.keys(), key=lambda t: -tool_frequency[t])[:5]
            current_tools = set(agent.tools)
            missing_tools = [t for t in successful_tools if t not in current_tools]

            if missing_tools:
                improvements["tools"] = agent.tools + missing_tools

        # Add learning from failures to prompt
        if metrics.common_failure_patterns:
            failure_guidance = "\n\n## Learned from Experience\n\nCommon pitfalls to avoid:\n"
            seen_patterns = set()
            for pattern in metrics.common_failure_patterns[:5]:
                # Deduplicate similar patterns
                pattern_key = pattern[:50].lower()
                if pattern_key not in seen_patterns:
                    failure_guidance += f"- {pattern[:100]}\n"
                    seen_patterns.add(pattern_key)

            improvements["system_prompt"] = agent.system_prompt + failure_guidance

        return improvements

    # =========================================================================
    # 4. MEMORY-GUIDED AGENT SELECTION
    # =========================================================================

    def select_best_agent(
        self,
        goal: str,
        available_agents: List[str]
    ) -> Tuple[str, float]:
        """
        Select the best agent for a goal based on memory.

        Analyzes past traces to find which agent performed best on similar tasks.

        Args:
            goal: Current goal
            available_agents: List of available agent names

        Returns:
            Tuple of (best_agent_name, confidence_score)
        """
        if not self.trace_manager or not available_agents:
            return (available_agents[0] if available_agents else "system-agent", 0.5)

        # Get similar traces
        similar_traces = self._get_similar_traces(goal, limit=20)

        if not similar_traces:
            return (available_agents[0], 0.5)

        # Score each agent based on performance on similar tasks
        agent_scores: Dict[str, Dict[str, float]] = {}

        for trace in similar_traces:
            agent_used = self._get_agent_from_trace(trace)

            if agent_used and agent_used in available_agents:
                if agent_used not in agent_scores:
                    agent_scores[agent_used] = {
                        "total_score": 0.0,
                        "count": 0,
                        "success_sum": 0.0
                    }

                agent_scores[agent_used]["count"] += 1
                agent_scores[agent_used]["success_sum"] += trace.success_rating

                # Weight by recency (more recent = higher weight)
                recency_weight = 1.0  # Could be based on timestamp
                agent_scores[agent_used]["total_score"] += trace.success_rating * recency_weight

        if not agent_scores:
            return (available_agents[0], 0.5)

        # Calculate average success rate per agent
        agent_performance = {}
        for agent, scores in agent_scores.items():
            if scores["count"] > 0:
                agent_performance[agent] = scores["success_sum"] / scores["count"]

        # Select best performer
        best_agent = max(agent_performance.keys(), key=lambda a: agent_performance[a])
        confidence = agent_performance[best_agent]

        return (best_agent, confidence)

    def _adapt_from_memory(
        self,
        agent: AgentSpec,
        similar_traces: List[Any],
        goal: str
    ) -> AgentSpec:
        """Adapt agent based on memory of similar tasks"""
        if not similar_traces:
            return agent

        # Extract successful patterns
        successful_traces = [t for t in similar_traces if t.success_rating >= 0.8]
        failed_traces = [t for t in similar_traces if t.success_rating < 0.6]

        if successful_traces:
            # Add successful tool patterns to agent
            common_tools = self._extract_common_tools(successful_traces)
            for tool in common_tools:
                if tool not in agent.tools:
                    agent.tools.append(tool)

        if failed_traces:
            # Add warnings about common failures
            failure_warnings = self._extract_failure_warnings(failed_traces)
            if failure_warnings:
                agent.system_prompt += f"\n\n## Warnings from Similar Tasks\n{failure_warnings}"

        return agent

    def _extract_common_tools(self, traces: List[Any]) -> List[str]:
        """Extract commonly used tools from successful traces"""
        tool_frequency = {}
        for trace in traces:
            if trace.tools_used:
                for tool in trace.tools_used:
                    tool_frequency[tool] = tool_frequency.get(tool, 0) + 1

        # Return tools used in >50% of traces
        threshold = len(traces) * 0.5
        return [tool for tool, count in tool_frequency.items() if count >= threshold]

    def _extract_failure_warnings(self, traces: List[Any]) -> str:
        """Extract warnings from failed traces"""
        warnings = []
        seen = set()

        for trace in traces[:5]:
            if trace.error_notes and trace.error_notes not in seen:
                warnings.append(f"- Avoid: {trace.error_notes[:100]}")
                seen.add(trace.error_notes)

        return "\n".join(warnings) if warnings else ""

    # =========================================================================
    # 5. DYNAMIC MODEL SELECTION
    # =========================================================================

    def _select_optimal_model(
        self,
        agent: AgentSpec,
        goal: str,
        similar_traces: Optional[List[Any]] = None
    ) -> AgentSpec:
        """
        Select optimal model based on task complexity and history.

        Model selection strategy:
        - haiku: Simple, proven tasks with high success rate
        - sonnet: Default for most tasks (balance of speed/quality)
        - opus: Complex reasoning, novel problems, low confidence scenarios
        """
        original_model = agent.model if hasattr(agent, 'model') else "sonnet"

        # Default to sonnet
        selected_model = "sonnet"
        reason = "default"

        # Check if we have successful traces
        if similar_traces:
            successful_traces = [t for t in similar_traces if t.success_rating >= 0.95]

            # High success rate on similar tasks → can use cheaper model
            if len(successful_traces) >= 3:
                selected_model = "haiku"
                reason = f"high success rate ({len(successful_traces)} successful similar traces)"

        # Check task complexity indicators
        complexity_indicators = [
            "analyze", "design", "architect", "complex", "comprehensive",
            "multi-step", "research", "evaluate", "compare", "optimize"
        ]

        goal_lower = goal.lower()
        complexity_count = sum(1 for indicator in complexity_indicators if indicator in goal_lower)

        if complexity_count >= 2:
            selected_model = "opus"
            reason = f"complex task ({complexity_count} complexity indicators)"

        # Check for creativity/novelty indicators
        novelty_indicators = ["creative", "novel", "innovative", "new approach", "brainstorm"]
        novelty_count = sum(1 for indicator in novelty_indicators if indicator in goal_lower)

        if novelty_count >= 1:
            selected_model = "opus"
            reason = f"creative task ({novelty_count} novelty indicators)"

        # Check sentience state for confidence
        if self.sentience_manager:
            state = self.sentience_manager.get_state()
            if hasattr(state, 'valence') and state.valence.self_confidence < -0.3:
                # Low confidence → use more capable model
                selected_model = "opus"
                reason = "low system confidence"

        # Update agent model
        agent.model = selected_model

        # Record if changed
        if selected_model != original_model:
            self.adaptation_history.append(AgentAdaptation(
                timestamp=datetime.now(),
                reason=reason,
                adaptation_type="model",
                original_value=original_model,
                new_value=selected_model,
                goal_context=goal[:100]
            ))

        return agent

    # =========================================================================
    # 6. AGENT PROMPT ENHANCEMENT FROM EXAMPLES
    # =========================================================================

    def _enhance_with_examples(
        self,
        agent: AgentSpec,
        similar_traces: List[Any],
        goal: str
    ) -> AgentSpec:
        """
        Enhance agent prompt with successful examples from traces.

        This implements few-shot learning by injecting relevant examples
        into the agent's context.
        """
        if not similar_traces:
            return agent

        # Get top successful examples
        successful_examples = sorted(
            [t for t in similar_traces if t.success_rating >= 0.8],
            key=lambda t: t.success_rating,
            reverse=True
        )[:3]

        if not successful_examples:
            return agent

        # Build examples section
        examples_section = "\n\n## Successful Examples from Memory\n\n"
        examples_section += "Use these as guidance for similar tasks:\n\n"

        for i, trace in enumerate(successful_examples, 1):
            examples_section += f"### Example {i}\n"
            examples_section += f"**Goal:** {trace.goal_text}\n"
            examples_section += f"**Success Rate:** {trace.success_rating:.0%}\n"

            if trace.tools_used:
                examples_section += f"**Tools Used:** {', '.join(trace.tools_used)}\n"

            if trace.output_summary:
                # Truncate long summaries
                summary = trace.output_summary[:500]
                if len(trace.output_summary) > 500:
                    summary += "..."
                examples_section += f"**Output:** {summary}\n"

            examples_section += "\n"

        agent.system_prompt += examples_section

        return agent

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def _get_similar_traces(self, goal: str, limit: int = 10) -> List[Any]:
        """Get traces similar to the goal"""
        if not self.trace_manager:
            return []

        # Try LLM matching first
        if hasattr(self.trace_manager, 'find_traces_with_llm'):
            try:
                return self.trace_manager.find_traces_with_llm(goal, limit=limit)
            except:
                pass

        # Fall back to listing recent traces
        all_traces = self.trace_manager.list_traces()
        return all_traces[:limit]

    def _get_agent_from_trace(self, trace: Any) -> Optional[str]:
        """Extract agent name from a trace"""
        if hasattr(trace, 'agent_used'):
            return trace.agent_used
        if hasattr(trace, 'metadata') and isinstance(trace.metadata, dict):
            return trace.metadata.get('agent')
        return None

    def get_adaptation_summary(self) -> Dict[str, Any]:
        """Get summary of all adaptations made"""
        summary = {
            "total_adaptations": len(self.adaptation_history),
            "by_type": {},
            "recent_adaptations": []
        }

        for adaptation in self.adaptation_history:
            atype = adaptation.adaptation_type
            summary["by_type"][atype] = summary["by_type"].get(atype, 0) + 1

        # Get recent adaptations
        recent = sorted(self.adaptation_history, key=lambda a: a.timestamp, reverse=True)[:10]
        for adaptation in recent:
            summary["recent_adaptations"].append({
                "timestamp": adaptation.timestamp.isoformat(),
                "type": adaptation.adaptation_type,
                "reason": adaptation.reason,
                "goal": adaptation.goal_context
            })

        return summary

    def get_agent_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of agent performance metrics"""
        return {
            agent_name: {
                "success_rate": metrics.success_rate,
                "total_executions": metrics.total_executions,
                "average_tokens": metrics.average_tokens,
                "needs_evolution": self._should_evolve(metrics)
            }
            for agent_name, metrics in self.agent_metrics.items()
        }

    def clear_cache(self):
        """Clear adapted agent cache"""
        self._adapted_agent_cache.clear()

    def record_execution_result(
        self,
        agent_name: str,
        goal: str,
        success: bool,
        tokens_used: float = 0,
        time_secs: float = 0,
        error: Optional[str] = None
    ):
        """
        Record execution result for learning.

        Call this after each agent execution to update metrics
        and trigger evolution if needed.
        """
        if agent_name not in self.agent_metrics:
            self.agent_metrics[agent_name] = AgentPerformanceMetrics(agent_name=agent_name)

        metrics = self.agent_metrics[agent_name]
        metrics.total_executions += 1

        if success:
            metrics.successful_executions += 1
        else:
            metrics.failed_executions += 1
            if error:
                metrics.common_failure_patterns.append(error)

        # Update averages
        n = metrics.total_executions
        metrics.average_tokens = ((metrics.average_tokens * (n - 1)) + tokens_used) / n
        metrics.average_time_secs = ((metrics.average_time_secs * (n - 1)) + time_secs) / n
        metrics.last_updated = datetime.now()

        # Check if evolution is needed
        if self._should_evolve(metrics):
            print(f"⚠️ Agent '{agent_name}' may need evolution (success rate: {metrics.success_rate:.1%})")
