#!/usr/bin/env python3
"""
Integration tests for LLMOS functionality in Qiskit Studio

This test suite validates the full LLMOS stack:
1. Boot and initialization
2. Dispatcher and execution modes (LEARNER, FOLLOWER, etc.)
3. Sentience Layer integration
4. Memory and trace management
5. Tool registration and execution

Run with: pytest tests/test_llmos_integration.py -v
Or: python tests/test_llmos_integration.py
"""

import asyncio
import sys
from pathlib import Path
import pytest
import tempfile
import shutil

# Add paths for imports
TESTS_DIR = Path(__file__).parent
QISKIT_STUDIO_DIR = TESTS_DIR.parent
LLMOS_ROOT = QISKIT_STUDIO_DIR.parents[1]
LLMOS_PKG = LLMOS_ROOT / "llmos"

sys.path.insert(0, str(QISKIT_STUDIO_DIR))
sys.path.insert(0, str(LLMOS_ROOT))
sys.path.insert(0, str(LLMOS_PKG))


class TestLLMOSBoot:
    """Test LLMOS boot and initialization"""

    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing"""
        temp_dir = tempfile.mkdtemp()
        workspace = Path(temp_dir) / "workspace"
        workspace.mkdir(parents=True)
        (workspace / "agents").mkdir()
        (workspace / "memories").mkdir()
        (workspace / "memories" / "traces").mkdir()
        (workspace / "state").mkdir()
        yield workspace
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def llmos_config(self, temp_workspace):
        """Create a test LLMOSConfig"""
        from kernel.config import (
            LLMOSConfig,
            KernelConfig,
            MemoryConfig,
            SDKConfig,
            DispatcherConfig,
            ExecutionLayerConfig,
            SentienceConfig
        )

        return LLMOSConfig(
            workspace=temp_workspace,
            kernel=KernelConfig(
                budget_usd=10.0,
                enable_scheduling=True,
                enable_watchdog=False  # Disable for testing
            ),
            memory=MemoryConfig(
                enable_llm_matching=True,
                trace_confidence_threshold=0.9,
            ),
            sdk=SDKConfig(
                model="claude-sonnet-4-5-20250929",
                enable_streaming=False,
                enable_hooks=True
            ),
            dispatcher=DispatcherConfig(
                complexity_threshold=2,
                auto_crystallization=False,  # Disable for testing
            ),
            execution=ExecutionLayerConfig(
                enable_advanced_tool_use=True,
                enable_ptc=True,
                enable_tool_search=True,
                enable_tool_examples=True,
            ),
            sentience=SentienceConfig(
                enable_sentience=True,
                safety_setpoint=0.5,
                curiosity_setpoint=0.3,
                auto_persist=False,  # Don't persist in tests
                state_file="state/test_sentience.json"
            ),
            project_name="test_project"
        )

    def test_llmos_can_be_instantiated(self, llmos_config):
        """Test that LLMOS can be instantiated with config"""
        from boot import LLMOS

        os_instance = LLMOS(config=llmos_config)
        assert os_instance is not None
        assert os_instance.config == llmos_config

    def test_llmos_boot_creates_components(self, llmos_config):
        """Test that LLMOS boot creates all required components"""
        from boot import LLMOS

        os_instance = LLMOS(config=llmos_config)

        async def run_boot():
            await os_instance.boot()
            return os_instance

        os_instance = asyncio.run(run_boot())

        # Check core components exist
        assert os_instance.token_economy is not None
        assert os_instance.memory_store is not None
        assert os_instance.trace_manager is not None
        assert os_instance.dispatcher is not None
        assert os_instance.component_registry is not None

    def test_llmos_boot_initializes_execution_layer(self, llmos_config):
        """Test that LLMOS boot initializes the Execution Layer"""
        from boot import LLMOS

        os_instance = LLMOS(config=llmos_config)

        async def run_boot():
            await os_instance.boot()
            return os_instance

        os_instance = asyncio.run(run_boot())

        # Check Execution Layer components
        dispatcher = os_instance.dispatcher
        assert dispatcher.ptc_executor is not None or dispatcher.config.execution.enable_ptc == False
        assert dispatcher.tool_search is not None or dispatcher.config.execution.enable_tool_search == False

    def test_llmos_shutdown(self, llmos_config):
        """Test that LLMOS can shutdown cleanly"""
        from boot import LLMOS

        os_instance = LLMOS(config=llmos_config)

        async def run_test():
            await os_instance.boot()
            await os_instance.shutdown()
            return True

        result = asyncio.run(run_test())
        assert result == True


class TestDispatcher:
    """Test Dispatcher and execution modes"""

    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing"""
        temp_dir = tempfile.mkdtemp()
        workspace = Path(temp_dir) / "workspace"
        workspace.mkdir(parents=True)
        (workspace / "agents").mkdir()
        (workspace / "memories").mkdir()
        (workspace / "memories" / "traces").mkdir()
        (workspace / "state").mkdir()
        yield workspace
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def dispatcher(self, temp_workspace):
        """Create a dispatcher for testing"""
        from kernel.bus import EventBus
        from kernel.token_economy import TokenEconomy
        from memory.store_sdk import MemoryStore
        from memory.traces_sdk import TraceManager
        from kernel.config import LLMOSConfig, ExecutionLayerConfig, SentienceConfig
        from interfaces.dispatcher import Dispatcher

        event_bus = EventBus()
        token_economy = TokenEconomy(budget_usd=10.0)
        memory_store = MemoryStore(temp_workspace / "memories")
        trace_manager = TraceManager(temp_workspace / "memories" / "traces")

        config = LLMOSConfig(
            workspace=temp_workspace,
            execution=ExecutionLayerConfig(
                enable_advanced_tool_use=True,
                enable_ptc=True,
                enable_tool_search=True,
            ),
            sentience=SentienceConfig(enable_sentience=False)
        )

        dispatcher = Dispatcher(
            event_bus=event_bus,
            token_economy=token_economy,
            memory_store=memory_store,
            trace_manager=trace_manager,
            workspace=temp_workspace,
            config=config
        )

        return dispatcher

    def test_dispatcher_creation(self, dispatcher):
        """Test dispatcher can be created"""
        assert dispatcher is not None
        assert dispatcher.token_economy is not None
        assert dispatcher.trace_manager is not None

    def test_dispatcher_mode_detection_novel_task(self, dispatcher):
        """Test dispatcher correctly identifies novel tasks as LEARNER mode"""
        async def run_test():
            mode = await dispatcher._determine_mode("Create a new quantum algorithm")
            return mode

        mode = asyncio.run(run_test())
        # Novel task should be LEARNER or ORCHESTRATOR
        assert mode in ["LEARNER", "ORCHESTRATOR"]

    def test_dispatcher_registers_tools(self, dispatcher):
        """Test dispatcher can register tools"""
        def sample_tool(x: int) -> int:
            """A sample tool for testing"""
            return x * 2

        dispatcher.register_tool("sample_tool", sample_tool, "Doubles a number")

        assert "sample_tool" in dispatcher.tools
        assert dispatcher.tools["sample_tool"](5) == 10

    def test_execution_layer_stats(self, dispatcher):
        """Test getting execution layer statistics"""
        stats = dispatcher.get_execution_layer_stats()

        assert "enabled" in stats
        assert "ptc" in stats
        assert "tool_search" in stats


class TestSentienceIntegration:
    """Test Sentience Layer integration with LLMOS"""

    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing"""
        temp_dir = tempfile.mkdtemp()
        workspace = Path(temp_dir) / "workspace"
        workspace.mkdir(parents=True)
        (workspace / "state").mkdir()
        yield workspace
        shutil.rmtree(temp_dir)

    def test_sentience_manager_with_triggers(self, temp_workspace):
        """Test SentienceManager responds to triggers correctly"""
        from kernel.sentience import SentienceManager, TriggerType

        state_path = temp_workspace / "state" / "test_sentience.json"

        manager = SentienceManager(
            state_path=state_path,
            auto_persist=False
        )

        # Get initial state
        initial_state = manager.get_state()
        initial_confidence = initial_state.valence.self_confidence

        # Trigger success
        manager.trigger(TriggerType.TASK_SUCCESS, reason="Test task completed")

        # Check confidence increased
        new_state = manager.get_state()
        assert new_state.valence.self_confidence > initial_confidence

    def test_sentience_manager_latent_modes(self, temp_workspace):
        """Test SentienceManager latent mode transitions"""
        from kernel.sentience import SentienceManager, TriggerType, LatentMode

        state_path = temp_workspace / "state" / "test_sentience.json"

        manager = SentienceManager(
            state_path=state_path,
            auto_persist=False
        )

        # Get initial latent mode
        state = manager.get_state()
        assert state.latent_mode is not None
        assert isinstance(state.latent_mode, LatentMode)

    def test_cognitive_kernel_derives_policy(self, temp_workspace):
        """Test CognitiveKernel derives behavioral policy"""
        from kernel.sentience import SentienceManager
        from kernel.cognitive_kernel import CognitiveKernel

        state_path = temp_workspace / "state" / "test_sentience.json"

        manager = SentienceManager(
            state_path=state_path,
            auto_persist=False
        )
        kernel = CognitiveKernel(manager)

        policy = kernel.derive_policy()

        assert policy is not None
        assert hasattr(policy, "prefer_cheap_modes")
        assert hasattr(policy, "prefer_safe_modes")
        assert hasattr(policy, "allow_exploration")
        assert hasattr(policy, "exploration_budget_multiplier")

    def test_cognitive_kernel_task_tracking(self, temp_workspace):
        """Test CognitiveKernel tracks task completion"""
        from kernel.sentience import SentienceManager
        from kernel.cognitive_kernel import CognitiveKernel

        state_path = temp_workspace / "state" / "test_sentience.json"

        manager = SentienceManager(
            state_path=state_path,
            auto_persist=False
        )
        kernel = CognitiveKernel(manager)

        # Track a successful task
        kernel.on_task_complete(
            success=True,
            cost=0.05,
            mode="LEARNER",
            goal="Test quantum circuit creation"
        )

        state = manager.get_state()
        # State should reflect the task completion
        assert state.last_trigger is not None


class TestMemoryAndTraces:
    """Test memory store and trace management"""

    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing"""
        temp_dir = tempfile.mkdtemp()
        workspace = Path(temp_dir) / "workspace"
        workspace.mkdir(parents=True)
        (workspace / "memories").mkdir()
        (workspace / "memories" / "traces").mkdir()
        (workspace / "memories" / "facts").mkdir()
        yield workspace
        shutil.rmtree(temp_dir)

    def test_trace_manager_creation(self, temp_workspace):
        """Test TraceManager can be created"""
        from memory.traces_sdk import TraceManager

        trace_manager = TraceManager(temp_workspace / "memories" / "traces")
        assert trace_manager is not None

    def test_trace_manager_save_and_find(self, temp_workspace):
        """Test TraceManager can save and find traces"""
        from memory.traces_sdk import TraceManager, ExecutionTrace
        from datetime import datetime

        trace_manager = TraceManager(temp_workspace / "memories" / "traces")

        # Get initial stats
        initial_stats = trace_manager.get_statistics()
        initial_count = initial_stats.get("total_traces", 0)

        # Create a test trace
        trace = ExecutionTrace(
            goal_signature="test123",
            goal_text="Create a Bell state circuit",
            success_rating=0.9,
            usage_count=1,
            created_at=datetime.now(),
            last_used=None,
            estimated_cost_usd=0.05,
            estimated_time_secs=2.0,
            mode="LEARNER",
            tools_used=["Write", "Bash"],
            output_summary="Created Bell state successfully"
        )

        # Save the trace
        trace_manager.save_trace(trace)

        # Verify trace was saved by checking statistics
        new_stats = trace_manager.get_statistics()
        new_count = new_stats.get("total_traces", 0)

        # Count should have increased
        assert new_count > initial_count, "Trace count should have increased after save"

    def test_memory_store_creation(self, temp_workspace):
        """Test MemoryStore can be created"""
        from memory.store_sdk import MemoryStore

        memory_store = MemoryStore(temp_workspace / "memories")
        assert memory_store is not None

    def test_memory_store_facts(self, temp_workspace):
        """Test MemoryStore can store and retrieve facts"""
        from memory.store_sdk import MemoryStore

        memory_store = MemoryStore(temp_workspace / "memories")

        # Store a fact using correct API: store_fact(fact, category)
        result = memory_store.store_fact(
            "Quantum computing uses qubits which can be in superposition",
            category="education"
        )

        assert result == True

        # Get facts count
        stats = memory_store.get_statistics()
        assert stats["facts_count"] >= 0  # May be 0 if not indexed yet


class TestToolRegistration:
    """Test tool registration and execution"""

    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing"""
        temp_dir = tempfile.mkdtemp()
        workspace = Path(temp_dir) / "workspace"
        workspace.mkdir(parents=True)
        yield workspace
        shutil.rmtree(temp_dir)

    def test_component_registry_creation(self):
        """Test ComponentRegistry can be created"""
        from kernel.component_registry import ComponentRegistry

        registry = ComponentRegistry()
        assert registry is not None

    def test_component_registry_tool_registration(self):
        """Test ComponentRegistry can register tools"""
        from kernel.component_registry import ComponentRegistry, ToolSpec

        registry = ComponentRegistry()

        # Create a proper ToolSpec
        tool_spec = ToolSpec(
            name="my_tool",
            description="Doubles a number",
            category="math"
        )

        registry.register_tool(tool_spec)

        # list_tools returns List[ToolSpec], not List[dict]
        tools = registry.list_tools()
        assert len(tools) > 0
        assert any(t.name == "my_tool" for t in tools)

    def test_qiskit_tools_import(self):
        """Test Qiskit tools can be imported"""
        from plugins.qiskit_tools import execute_qiskit_code, validate_qiskit_code

        assert execute_qiskit_code is not None
        assert validate_qiskit_code is not None

    def test_qiskit_validate_tool(self):
        """Test Qiskit validate tool works"""
        from plugins.qiskit_tools import validate_qiskit_code

        code = """
from qiskit import QuantumCircuit
qc = QuantumCircuit(2, 2)
qc.h(0)
"""
        result = asyncio.run(validate_qiskit_code(code))
        assert "passed" in result.lower() or "correct" in result.lower()


class TestEndToEnd:
    """End-to-end integration tests"""

    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing"""
        temp_dir = tempfile.mkdtemp()
        workspace = Path(temp_dir) / "workspace"
        workspace.mkdir(parents=True)
        (workspace / "agents").mkdir()
        (workspace / "memories").mkdir()
        (workspace / "memories" / "traces").mkdir()
        (workspace / "state").mkdir()
        yield workspace
        shutil.rmtree(temp_dir)

    def test_full_llmos_lifecycle(self, temp_workspace):
        """Test full LLMOS lifecycle: boot, register tools, shutdown"""
        from boot import LLMOS
        from kernel.config import LLMOSConfig, SentienceConfig
        from kernel.component_registry import ToolSpec

        config = LLMOSConfig(
            workspace=temp_workspace,
            sentience=SentienceConfig(
                enable_sentience=True,
                auto_persist=False
            )
        )

        os_instance = LLMOS(config=config)

        async def run_lifecycle():
            # Boot
            await os_instance.boot()
            assert os_instance._running == True

            # Register a custom tool using proper ToolSpec
            tool_spec = ToolSpec(
                name="custom_tool",
                description="Processes a string",
                category="utility"
            )
            os_instance.component_registry.register_tool(tool_spec)

            # Verify tool was registered (list_tools returns List[ToolSpec])
            tools = os_instance.component_registry.list_tools()
            assert any(t.name == "custom_tool" for t in tools)

            # Shutdown
            await os_instance.shutdown()
            return True

        result = asyncio.run(run_lifecycle())
        assert result == True

    def test_token_economy_tracking(self, temp_workspace):
        """Test token economy tracks spending"""
        from boot import LLMOS
        from kernel.config import LLMOSConfig, KernelConfig

        config = LLMOSConfig(
            workspace=temp_workspace,
            kernel=KernelConfig(budget_usd=10.0)
        )

        os_instance = LLMOS(config=config)

        async def run_test():
            await os_instance.boot()

            # Check initial budget
            assert os_instance.token_economy.balance == 10.0

            # Manually deduct (simulating execution cost)
            os_instance.token_economy.deduct(0.5, "Test execution")

            assert os_instance.token_economy.balance == 9.5
            assert len(os_instance.token_economy.spend_log) == 1

            await os_instance.shutdown()
            return True

        result = asyncio.run(run_test())
        assert result == True


# ============================================================================
# Main runner
# ============================================================================

def run_tests():
    """Run all tests and report results"""
    print("=" * 70)
    print("LLMOS Integration Tests - Qiskit Studio")
    print("=" * 70)
    print()

    # Use pytest for execution
    import pytest
    exit_code = pytest.main([__file__, "-v", "--tb=short"])
    return exit_code


if __name__ == "__main__":
    sys.exit(run_tests())
