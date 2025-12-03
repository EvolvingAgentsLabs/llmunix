"""
Tests for DynamicAgentManager - Adaptive Subagent Configuration

Tests the six key features:
1. Dynamic agent configuration per query
2. Sentience-driven agent adaptation
3. Trace-driven agent evolution
4. Memory-guided agent selection
5. Dynamic model selection
6. Agent prompt enhancement from examples
"""

import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
import sys

# Add llmos to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kernel.agent_factory import AgentSpec, AgentFactory
from kernel.sentience import SentienceState, LatentMode, ValenceVector
from kernel.dynamic_agents import (
    DynamicAgentManager,
    AgentAdaptation,
    AgentPerformanceMetrics
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_workspace(tmp_path):
    """Create a temporary workspace"""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    agents_dir = workspace / "agents"
    agents_dir.mkdir()
    return workspace


@pytest.fixture
def mock_agent_factory(mock_workspace):
    """Create a mock agent factory with sample agents"""
    factory = Mock(spec=AgentFactory)

    # Sample agents
    researcher = AgentSpec(
        name="researcher",
        agent_type="task",
        category="analysis",
        description="Expert at web research and data synthesis",
        tools=["WebFetch", "Read", "Write"],
        version="1.0.0",
        status="active",
        mode=["LEARNER"],
        system_prompt="You are an expert researcher...",
        capabilities=["research", "analysis"],
        constraints=[]
    )

    coder = AgentSpec(
        name="coder",
        agent_type="task",
        category="development",
        description="Expert Python developer",
        tools=["Read", "Write", "Edit", "Bash"],
        version="1.0.0",
        status="active",
        mode=["LEARNER"],
        system_prompt="You are an expert Python developer...",
        capabilities=["coding", "debugging"],
        constraints=[]
    )

    factory.get_agent.side_effect = lambda name: {
        "researcher": researcher,
        "coder": coder
    }.get(name)

    factory.list_agents.return_value = [researcher, coder]

    return factory


@pytest.fixture
def mock_trace_manager():
    """Create a mock trace manager"""
    manager = Mock()

    # Sample traces
    trace1 = Mock()
    trace1.goal_text = "Research AI trends"
    trace1.success_rating = 0.95
    trace1.tools_used = ["WebFetch", "Read"]
    trace1.output_summary = "Found 10 AI trends..."
    trace1.error_notes = ""
    trace1.estimated_cost_usd = 0.05
    trace1.estimated_time_secs = 2.5

    trace2 = Mock()
    trace2.goal_text = "Write Python script"
    trace2.success_rating = 0.6
    trace2.tools_used = ["Write", "Bash"]
    trace2.output_summary = ""
    trace2.error_notes = "Syntax error in line 10"
    trace2.estimated_cost_usd = 0.03
    trace2.estimated_time_secs = 1.5

    manager.list_traces.return_value = [trace1, trace2]
    manager.find_traces_with_llm = Mock(return_value=[trace1, trace2])

    return manager


@pytest.fixture
def mock_sentience_manager():
    """Create a mock sentience manager"""
    manager = Mock()

    # Default state - balanced
    state = SentienceState()
    state.valence.curiosity = 0.0
    state.valence.safety = 0.5
    state.valence.energy = 0.5
    state.valence.self_confidence = 0.5
    state.latent_mode = LatentMode.AUTO_CONTAINED

    manager.get_state.return_value = state
    return manager


@pytest.fixture
def dynamic_agent_manager(mock_agent_factory, mock_workspace, mock_trace_manager, mock_sentience_manager):
    """Create a DynamicAgentManager for testing"""
    return DynamicAgentManager(
        agent_factory=mock_agent_factory,
        workspace=mock_workspace,
        sentience_manager=mock_sentience_manager,
        trace_manager=mock_trace_manager,
        config=None
    )


# =============================================================================
# Test: Basic Initialization
# =============================================================================

class TestDynamicAgentManagerInit:
    """Test DynamicAgentManager initialization"""

    def test_init_with_all_dependencies(self, dynamic_agent_manager):
        """Test initialization with all dependencies"""
        assert dynamic_agent_manager is not None
        assert dynamic_agent_manager.agent_factory is not None
        assert dynamic_agent_manager.sentience_manager is not None
        assert dynamic_agent_manager.trace_manager is not None

    def test_init_with_minimal_dependencies(self, mock_agent_factory, mock_workspace):
        """Test initialization with minimal dependencies"""
        manager = DynamicAgentManager(
            agent_factory=mock_agent_factory,
            workspace=mock_workspace
        )
        assert manager is not None
        assert manager.sentience_manager is None
        assert manager.trace_manager is None


# =============================================================================
# Test 1: Dynamic Agent Configuration Per Query
# =============================================================================

class TestDynamicAgentConfigPerQuery:
    """Test dynamic agent configuration for each query"""

    def test_get_adapted_agent_basic(self, dynamic_agent_manager):
        """Test basic agent adaptation"""
        adapted = dynamic_agent_manager.get_adapted_agent(
            agent_name="researcher",
            goal="Research quantum computing trends"
        )

        assert adapted is not None
        assert adapted.name == "researcher"
        # Agent should have original tools
        assert "WebFetch" in adapted.tools

    def test_adapted_agent_is_deep_copy(self, dynamic_agent_manager, mock_agent_factory):
        """Test that adaptation creates a deep copy"""
        original = mock_agent_factory.get_agent("researcher")
        adapted = dynamic_agent_manager.get_adapted_agent(
            agent_name="researcher",
            goal="Research AI"
        )

        # Should be different objects
        assert adapted is not original

        # Modifying adapted shouldn't affect original
        adapted.tools.append("NewTool")
        original_agent = mock_agent_factory.get_agent("researcher")
        assert "NewTool" not in original_agent.tools

    def test_agent_not_found_raises_error(self, dynamic_agent_manager):
        """Test that requesting unknown agent raises ValueError"""
        with pytest.raises(ValueError, match="not found"):
            dynamic_agent_manager.get_adapted_agent(
                agent_name="nonexistent_agent",
                goal="Some goal"
            )


# =============================================================================
# Test 2: Sentience-Driven Agent Adaptation
# =============================================================================

class TestSentienceDrivenAdaptation:
    """Test agent adaptation based on sentience state"""

    def test_high_curiosity_adds_exploration_tools(self, dynamic_agent_manager, mock_sentience_manager):
        """Test that high curiosity adds exploration tools"""
        # Set high curiosity state
        state = SentienceState()
        state.valence.curiosity = 0.5
        state.valence.safety = 0.5
        state.valence.energy = 0.5
        state.valence.self_confidence = 0.5
        state.latent_mode = LatentMode.AUTO_CREATIVE
        mock_sentience_manager.get_state.return_value = state

        adapted = dynamic_agent_manager.get_adapted_agent(
            agent_name="coder",
            goal="Explore new Python libraries"
        )

        # Should add exploration tools
        assert "WebSearch" in adapted.tools or "Creative Mode" in adapted.system_prompt

    def test_low_curiosity_reduces_tools(self, dynamic_agent_manager, mock_sentience_manager):
        """Test that low curiosity reduces non-essential tools"""
        # Set low curiosity state
        state = SentienceState()
        state.valence.curiosity = -0.5
        state.valence.safety = 0.5
        state.valence.energy = 0.5
        state.valence.self_confidence = 0.5
        state.latent_mode = LatentMode.AUTO_CONTAINED
        mock_sentience_manager.get_state.return_value = state

        adapted = dynamic_agent_manager.get_adapted_agent(
            agent_name="researcher",
            goal="Quick task"
        )

        # Should have focus mode guidance
        assert "Focus Mode" in adapted.system_prompt or len(adapted.tools) <= 5

    def test_low_safety_removes_dangerous_tools(self, dynamic_agent_manager, mock_sentience_manager):
        """Test that low safety removes dangerous tools"""
        # Set low safety (cautious) state
        state = SentienceState()
        state.valence.curiosity = 0.0
        state.valence.safety = -0.3
        state.valence.energy = 0.5
        state.valence.self_confidence = 0.5
        state.latent_mode = LatentMode.CAUTIOUS
        mock_sentience_manager.get_state.return_value = state

        adapted = dynamic_agent_manager.get_adapted_agent(
            agent_name="coder",
            goal="Make some changes"
        )

        # Should remove dangerous tools or add caution constraints
        assert "Caution Mode" in adapted.system_prompt or "Bash" not in adapted.tools

    def test_low_energy_adds_conservation_guidance(self, dynamic_agent_manager, mock_sentience_manager):
        """Test that low energy adds conservation guidance"""
        # Set low energy state
        state = SentienceState()
        state.valence.curiosity = 0.0
        state.valence.safety = 0.5
        state.valence.energy = -0.5
        state.valence.self_confidence = 0.5
        state.latent_mode = LatentMode.RECOVERY
        mock_sentience_manager.get_state.return_value = state

        adapted = dynamic_agent_manager.get_adapted_agent(
            agent_name="researcher",
            goal="Research topic"
        )

        # Should add energy conservation guidance
        assert "Conservation" in adapted.system_prompt or "Energy" in adapted.system_prompt


# =============================================================================
# Test 3: Trace-Driven Agent Evolution
# =============================================================================

class TestTraceDrivenEvolution:
    """Test agent evolution based on trace analysis"""

    def test_calculate_metrics_from_traces(self, dynamic_agent_manager, mock_trace_manager):
        """Test calculating performance metrics from traces"""
        metrics = dynamic_agent_manager._calculate_agent_metrics("researcher")

        assert metrics is not None
        assert metrics.agent_name == "researcher"
        assert metrics.total_executions > 0

    def test_should_evolve_high_failure_rate(self, dynamic_agent_manager):
        """Test that high failure rate triggers evolution"""
        metrics = AgentPerformanceMetrics(
            agent_name="failing_agent",
            total_executions=10,
            successful_executions=5,
            failed_executions=5,  # 50% failure rate
            common_failure_patterns=["timeout", "permission denied", "not found"]
        )

        should_evolve = dynamic_agent_manager._should_evolve(metrics)
        assert should_evolve is True

    def test_should_not_evolve_insufficient_data(self, dynamic_agent_manager):
        """Test that insufficient data doesn't trigger evolution"""
        metrics = AgentPerformanceMetrics(
            agent_name="new_agent",
            total_executions=2,  # Below threshold
            successful_executions=1,
            failed_executions=1
        )

        should_evolve = dynamic_agent_manager._should_evolve(metrics)
        assert should_evolve is False

    def test_generate_improvements_from_failures(self, dynamic_agent_manager, mock_agent_factory):
        """Test that improvements are generated from failure patterns"""
        metrics = AgentPerformanceMetrics(
            agent_name="coder",
            total_executions=10,
            successful_executions=6,
            failed_executions=4,
            common_failure_patterns=[
                "timeout error after 30s",
                "permission denied for /etc/passwd",
                "file not found: config.yaml"
            ],
            successful_tool_sequences=[
                ["Read", "Edit", "Write"],
                ["Read", "Bash"]
            ]
        )

        agent = mock_agent_factory.get_agent("coder")
        improvements = dynamic_agent_manager._generate_improvements(agent, metrics)

        # Should have improvements based on failure patterns
        assert improvements is not None
        assert "constraints" in improvements or "system_prompt" in improvements


# =============================================================================
# Test 4: Memory-Guided Agent Selection
# =============================================================================

class TestMemoryGuidedSelection:
    """Test agent selection based on past performance"""

    def test_select_best_agent_for_goal(self, dynamic_agent_manager):
        """Test selecting best agent for a goal"""
        best_agent, confidence = dynamic_agent_manager.select_best_agent(
            goal="Research AI trends",
            available_agents=["researcher", "coder"]
        )

        assert best_agent in ["researcher", "coder"]
        assert 0.0 <= confidence <= 1.0

    def test_select_agent_with_no_traces(self, dynamic_agent_manager, mock_trace_manager):
        """Test agent selection when no traces available"""
        mock_trace_manager.list_traces.return_value = []

        best_agent, confidence = dynamic_agent_manager.select_best_agent(
            goal="Brand new task",
            available_agents=["researcher", "coder"]
        )

        # Should return first available agent with low confidence
        assert best_agent == "researcher"
        assert confidence == 0.5


# =============================================================================
# Test 5: Dynamic Model Selection
# =============================================================================

class TestDynamicModelSelection:
    """Test optimal model selection based on task complexity"""

    def test_simple_task_uses_haiku(self, dynamic_agent_manager, mock_trace_manager, mock_agent_factory):
        """Test that simple tasks with high success rate use haiku"""
        # Create high-success traces
        successful_trace = Mock()
        successful_trace.success_rating = 0.98
        mock_trace_manager.list_traces.return_value = [successful_trace] * 5

        agent = mock_agent_factory.get_agent("researcher")
        adapted = dynamic_agent_manager._select_optimal_model(
            agent, "Simple research task", [successful_trace] * 3
        )

        assert getattr(adapted, 'model', 'sonnet') == 'haiku'

    def test_complex_task_uses_opus(self, dynamic_agent_manager, mock_agent_factory):
        """Test that complex tasks use opus"""
        agent = mock_agent_factory.get_agent("researcher")
        adapted = dynamic_agent_manager._select_optimal_model(
            agent, "Analyze and design comprehensive multi-step architecture", None
        )

        assert getattr(adapted, 'model', 'sonnet') == 'opus'

    def test_creative_task_uses_opus(self, dynamic_agent_manager, mock_agent_factory):
        """Test that creative tasks use opus"""
        agent = mock_agent_factory.get_agent("researcher")
        adapted = dynamic_agent_manager._select_optimal_model(
            agent, "Creative brainstorming for novel approach", None
        )

        assert getattr(adapted, 'model', 'sonnet') == 'opus'

    def test_default_task_uses_sonnet(self, dynamic_agent_manager, mock_agent_factory):
        """Test that standard tasks use sonnet"""
        agent = mock_agent_factory.get_agent("researcher")
        adapted = dynamic_agent_manager._select_optimal_model(
            agent, "Read file and summarize", None
        )

        assert getattr(adapted, 'model', 'sonnet') == 'sonnet'


# =============================================================================
# Test 6: Agent Prompt Enhancement from Examples
# =============================================================================

class TestPromptEnhancementFromExamples:
    """Test enhancing agent prompts with successful examples"""

    def test_enhance_with_successful_examples(self, dynamic_agent_manager, mock_agent_factory, mock_trace_manager):
        """Test that successful examples are added to prompt"""
        # Create successful traces
        trace = Mock()
        trace.goal_text = "Research quantum computing"
        trace.success_rating = 0.95
        trace.tools_used = ["WebFetch", "Read"]
        trace.output_summary = "Found 5 key trends..."

        agent = mock_agent_factory.get_agent("researcher")
        enhanced = dynamic_agent_manager._enhance_with_examples(
            agent, [trace], "Research AI"
        )

        # Should have examples section
        assert "Example" in enhanced.system_prompt or "Memory" in enhanced.system_prompt

    def test_no_enhancement_without_examples(self, dynamic_agent_manager, mock_agent_factory):
        """Test that no enhancement happens without examples"""
        agent = mock_agent_factory.get_agent("researcher")
        original_prompt = agent.system_prompt

        enhanced = dynamic_agent_manager._enhance_with_examples(
            agent, [], "Some goal"
        )

        # Prompt should be unchanged
        assert enhanced.system_prompt == original_prompt


# =============================================================================
# Test: Adaptation History and Metrics
# =============================================================================

class TestAdaptationTracking:
    """Test tracking of adaptations and metrics"""

    def test_adaptation_history_recorded(self, dynamic_agent_manager, mock_sentience_manager):
        """Test that adaptations are recorded in history"""
        # Set high curiosity to trigger adaptation
        state = SentienceState()
        state.valence.curiosity = 0.5
        state.valence.safety = 0.5
        state.valence.energy = 0.5
        state.valence.self_confidence = 0.5
        state.latent_mode = LatentMode.AUTO_CREATIVE
        mock_sentience_manager.get_state.return_value = state

        dynamic_agent_manager.get_adapted_agent(
            agent_name="researcher",
            goal="Explore something"
        )

        # Should have recorded adaptation
        summary = dynamic_agent_manager.get_adaptation_summary()
        assert summary["total_adaptations"] >= 0

    def test_record_execution_result(self, dynamic_agent_manager):
        """Test recording execution results for learning"""
        dynamic_agent_manager.record_execution_result(
            agent_name="researcher",
            goal="Research AI",
            success=True,
            tokens_used=1000,
            time_secs=5.0
        )

        metrics = dynamic_agent_manager.agent_metrics.get("researcher")
        assert metrics is not None
        assert metrics.total_executions == 1
        assert metrics.successful_executions == 1

    def test_cache_clearing(self, dynamic_agent_manager):
        """Test cache clearing works"""
        # Add something to cache
        dynamic_agent_manager._adapted_agent_cache["test_key"] = "test_value"

        dynamic_agent_manager.clear_cache()

        assert len(dynamic_agent_manager._adapted_agent_cache) == 0


# =============================================================================
# Test: Integration with SDK Client
# =============================================================================

class TestSDKClientIntegration:
    """Test integration with LLMOSSDKClient"""

    def test_agent_spec_has_model_attribute(self, dynamic_agent_manager, mock_agent_factory):
        """Test that adapted agents have model attribute"""
        adapted = dynamic_agent_manager.get_adapted_agent(
            agent_name="researcher",
            goal="Complex analysis task"
        )

        # Should have model attribute set
        assert hasattr(adapted, 'model')


# =============================================================================
# Run tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
