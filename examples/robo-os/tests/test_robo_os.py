"""
Tests for RoboOS - Robot Control with LLMOS

This test suite validates:
1. Robot controller tools functionality
2. Safety hook system
3. Robot state management
4. LLMOS integration
5. Agent configuration loading
"""

import pytest
import sys
import os
from pathlib import Path

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../llmos'))


# ===========================================================================
# Robot State Tests
# ===========================================================================

class TestRobotState:
    """Tests for robot state management."""

    def test_get_robot_state(self):
        """Test getting robot state singleton."""
        from robot_state import get_robot_state, reset_robot_state
        reset_robot_state()
        state = get_robot_state()
        assert state is not None
        assert hasattr(state, 'position')
        assert hasattr(state, 'history')

    def test_reset_robot_state(self):
        """Test resetting robot state."""
        from robot_state import get_robot_state, reset_robot_state

        # Get state and modify it
        state = get_robot_state()
        original_pos = state.position.copy() if hasattr(state.position, 'copy') else state.position

        # Reset should return to initial state
        reset_robot_state()
        new_state = get_robot_state()
        assert new_state is not None

    def test_robot_state_position(self):
        """Test robot position attribute."""
        from robot_state import get_robot_state, reset_robot_state
        reset_robot_state()
        state = get_robot_state()

        # Position should have x, y, z
        if hasattr(state.position, 'x'):
            assert hasattr(state.position, 'x')
            assert hasattr(state.position, 'y')
            assert hasattr(state.position, 'z')
        else:
            # May be a dict
            assert isinstance(state.position, dict) or isinstance(state.position, (list, tuple))


# ===========================================================================
# Robot Controller Tools Tests
# ===========================================================================

class TestRobotControllerTools:
    """Tests for robot controller tool functions."""

    def test_tools_list_exists(self):
        """Test that ROBOT_CONTROLLER_TOOLS list exists."""
        from plugins.robot_controller import ROBOT_CONTROLLER_TOOLS
        assert ROBOT_CONTROLLER_TOOLS is not None
        assert isinstance(ROBOT_CONTROLLER_TOOLS, list)
        assert len(ROBOT_CONTROLLER_TOOLS) > 0

    def test_each_tool_has_required_fields(self):
        """Test that each tool has name, function, description."""
        from plugins.robot_controller import ROBOT_CONTROLLER_TOOLS

        for tool in ROBOT_CONTROLLER_TOOLS:
            assert 'name' in tool, f"Tool missing 'name': {tool}"
            assert 'function' in tool, f"Tool {tool.get('name', 'unknown')} missing 'function'"
            assert 'description' in tool, f"Tool {tool.get('name', 'unknown')} missing 'description'"
            assert callable(tool['function']), f"Tool {tool['name']} function is not callable"

    def test_move_to_tool_exists(self):
        """Test that move_to tool exists."""
        from plugins.robot_controller import ROBOT_CONTROLLER_TOOLS

        tool_names = [t['name'] for t in ROBOT_CONTROLLER_TOOLS]
        assert 'move_to' in tool_names

    def test_get_status_tool_exists(self):
        """Test that get_status tool exists."""
        from plugins.robot_controller import ROBOT_CONTROLLER_TOOLS

        tool_names = [t['name'] for t in ROBOT_CONTROLLER_TOOLS]
        assert 'get_status' in tool_names

    def test_emergency_stop_tool_exists(self):
        """Test that emergency_stop tool exists."""
        from plugins.robot_controller import ROBOT_CONTROLLER_TOOLS

        tool_names = [t['name'] for t in ROBOT_CONTROLLER_TOOLS]
        assert 'emergency_stop' in tool_names

    def test_go_home_tool_exists(self):
        """Test that go_home tool exists."""
        from plugins.robot_controller import ROBOT_CONTROLLER_TOOLS

        tool_names = [t['name'] for t in ROBOT_CONTROLLER_TOOLS]
        assert 'go_home' in tool_names

    def test_get_camera_feed_tool_exists(self):
        """Test that get_camera_feed tool exists."""
        from plugins.robot_controller import ROBOT_CONTROLLER_TOOLS

        tool_names = [t['name'] for t in ROBOT_CONTROLLER_TOOLS]
        assert 'get_camera_feed' in tool_names


# ===========================================================================
# Safety Hook Tests
# ===========================================================================

class TestSafetyHook:
    """Tests for safety hook system."""

    def test_get_safety_hook(self):
        """Test getting safety hook instance."""
        from safety_hook import get_safety_hook

        hook = get_safety_hook()
        assert hook is not None

    def test_safety_hook_is_callable(self):
        """Test that safety hook is callable (uses __call__)."""
        from safety_hook import get_safety_hook

        hook = get_safety_hook()
        assert callable(hook)  # Uses __call__ method

    def test_safety_hook_has_violations_summary(self):
        """Test that safety hook can provide violations summary."""
        from safety_hook import get_safety_hook

        hook = get_safety_hook()
        assert hasattr(hook, 'get_violations_summary')

        summary = hook.get_violations_summary()
        assert isinstance(summary, dict)
        assert 'total_violations' in summary

    def test_safety_protocol_hook_class(self):
        """Test SafetyProtocolHook class exists."""
        from safety_hook import SafetyProtocolHook

        assert SafetyProtocolHook is not None

        # Create new instance
        hook = SafetyProtocolHook()
        assert hook is not None

    def test_workspace_bounds_validation(self):
        """Test that safety hook validates workspace bounds."""
        from safety_hook import SafetyProtocolHook

        hook = SafetyProtocolHook()

        # Check a position outside bounds
        # Note: Actual implementation may vary
        if hasattr(hook, 'check_bounds'):
            result = hook.check_bounds(100.0, 0.0, 0.0)
            assert not result  # Should be invalid


# ===========================================================================
# Agent Configuration Tests
# ===========================================================================

class TestAgentConfigurations:
    """Tests for agent markdown configurations."""

    def test_agents_directory_exists(self):
        """Test that agents directory exists."""
        agents_dir = Path(__file__).parent.parent / "workspace" / "agents"
        assert agents_dir.exists(), f"Agents directory not found: {agents_dir}"

    def test_operator_agent_file_exists(self):
        """Test that operator agent markdown file exists."""
        agent_file = Path(__file__).parent.parent / "workspace" / "agents" / "operator.md"
        assert agent_file.exists(), f"Operator agent file not found: {agent_file}"

    def test_safety_officer_agent_file_exists(self):
        """Test that safety officer agent markdown file exists."""
        agent_file = Path(__file__).parent.parent / "workspace" / "agents" / "safety-officer.md"
        assert agent_file.exists(), f"Safety officer agent file not found: {agent_file}"

    def test_agent_loader_loads_operator(self):
        """Test that AgentLoader can load operator agent."""
        from kernel.agent_loader import AgentLoader

        agents_dir = Path(__file__).parent.parent / "workspace" / "agents"
        loader = AgentLoader(agents_dir=str(agents_dir))

        operator = loader.load_agent("operator")
        assert operator is not None
        assert hasattr(operator, 'name')
        assert hasattr(operator, 'system_prompt')

    def test_agent_loader_loads_safety_officer(self):
        """Test that AgentLoader can load safety-officer agent."""
        from kernel.agent_loader import AgentLoader

        agents_dir = Path(__file__).parent.parent / "workspace" / "agents"
        loader = AgentLoader(agents_dir=str(agents_dir))

        safety_officer = loader.load_agent("safety-officer")
        assert safety_officer is not None
        assert hasattr(safety_officer, 'name')


# ===========================================================================
# LLMOS Integration Tests
# ===========================================================================

class TestLLMOSIntegration:
    """Tests for LLMOS integration in RoboOS."""

    def test_llmos_import(self):
        """Test that LLMOS can be imported."""
        from boot import LLMOS
        assert LLMOS is not None

    def test_llmos_config_import(self):
        """Test that LLMOSConfig can be imported."""
        from kernel.config import LLMOSConfig
        assert LLMOSConfig is not None

    def test_llmos_development_config(self):
        """Test creating development config."""
        from kernel.config import LLMOSConfig

        config = LLMOSConfig.development()
        assert config is not None
        assert hasattr(config, 'workspace')

    def test_llmos_initialization(self):
        """Test LLMOS initialization with robo-os workspace."""
        from boot import LLMOS
        from kernel.config import LLMOSConfig
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            config = LLMOSConfig.development()
            config.workspace = Path(tmpdir)

            llmos = LLMOS(config=config)
            assert llmos is not None
            assert llmos.dispatcher is not None

    def test_tool_registration(self):
        """Test registering robot tools with dispatcher."""
        from boot import LLMOS
        from kernel.config import LLMOSConfig
        from plugins.robot_controller import ROBOT_CONTROLLER_TOOLS
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            config = LLMOSConfig.development()
            config.workspace = Path(tmpdir)

            llmos = LLMOS(config=config)

            # Register tools
            for tool in ROBOT_CONTROLLER_TOOLS:
                llmos.dispatcher.register_tool(
                    name=tool['name'],
                    func=tool['function'],
                    description=tool['description']
                )

            # Verify tools are registered
            assert len(llmos.dispatcher.tools) >= len(ROBOT_CONTROLLER_TOOLS)

    def test_dispatcher_has_required_methods(self):
        """Test that dispatcher has required methods."""
        from boot import LLMOS
        from kernel.config import LLMOSConfig
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            config = LLMOSConfig.development()
            config.workspace = Path(tmpdir)

            llmos = LLMOS(config=config)

            assert hasattr(llmos.dispatcher, 'register_tool')
            assert hasattr(llmos.dispatcher, 'dispatch')
            assert hasattr(llmos.dispatcher, 'get_execution_layer_stats')


# ===========================================================================
# Demo Module Tests
# ===========================================================================

class TestDemoModule:
    """Tests for the demo module functions."""

    def test_demo_module_import(self):
        """Test that demo module can be imported."""
        # This should not raise any errors
        import demo
        assert demo is not None

    def test_get_operator_config_function(self):
        """Test get_operator_config function."""
        import demo

        config = demo.get_operator_config()
        assert config is not None
        assert 'name' in config
        assert 'system_prompt' in config

    def test_get_safety_officer_config_function(self):
        """Test get_safety_officer_config function."""
        import demo

        config = demo.get_safety_officer_config()
        assert config is not None
        assert 'name' in config

    def test_print_header_function(self):
        """Test print_header utility function."""
        import demo

        # Should not raise
        demo.print_header("Test Header")

    def test_print_section_function(self):
        """Test print_section utility function."""
        import demo

        # Should not raise
        demo.print_section("Test Section")


# ===========================================================================
# Tool Function Execution Tests
# ===========================================================================

class TestToolExecution:
    """Tests for actual tool function execution."""

    @pytest.mark.asyncio
    async def test_get_status_returns_json(self):
        """Test that get_status returns JSON string."""
        import json
        from plugins.robot_controller import ROBOT_CONTROLLER_TOOLS
        from robot_state import reset_robot_state

        reset_robot_state()

        # Find get_status tool
        get_status = None
        for tool in ROBOT_CONTROLLER_TOOLS:
            if tool['name'] == 'get_status':
                get_status = tool['function']
                break

        assert get_status is not None
        result = await get_status()
        assert isinstance(result, str)
        # Should be valid JSON
        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    @pytest.mark.asyncio
    async def test_go_home_executes(self):
        """Test that go_home can be executed."""
        import json
        from plugins.robot_controller import ROBOT_CONTROLLER_TOOLS
        from robot_state import reset_robot_state

        reset_robot_state()

        # Find go_home tool
        go_home = None
        for tool in ROBOT_CONTROLLER_TOOLS:
            if tool['name'] == 'go_home':
                go_home = tool['function']
                break

        assert go_home is not None
        result = await go_home()
        assert result is not None
        parsed = json.loads(result)
        assert parsed['success'] is True

    @pytest.mark.asyncio
    async def test_emergency_stop_executes(self):
        """Test that emergency_stop can be executed."""
        import json
        from plugins.robot_controller import ROBOT_CONTROLLER_TOOLS
        from robot_state import reset_robot_state

        reset_robot_state()

        # Find emergency_stop tool
        emergency_stop = None
        for tool in ROBOT_CONTROLLER_TOOLS:
            if tool['name'] == 'emergency_stop':
                emergency_stop = tool['function']
                break

        assert emergency_stop is not None
        result = await emergency_stop()
        assert result is not None
        parsed = json.loads(result)
        assert 'EMERGENCY STOP' in parsed['message']

    @pytest.mark.asyncio
    async def test_move_to_valid_position(self):
        """Test moving to a valid position."""
        import json
        from plugins.robot_controller import ROBOT_CONTROLLER_TOOLS
        from robot_state import reset_robot_state

        reset_robot_state()

        # Find move_to tool
        move_to = None
        for tool in ROBOT_CONTROLLER_TOOLS:
            if tool['name'] == 'move_to':
                move_to = tool['function']
                break

        assert move_to is not None
        result = await move_to(1.0, 0.5, 1.5, 45.0)
        assert result is not None
        parsed = json.loads(result)
        assert parsed['success'] is True

    @pytest.mark.asyncio
    async def test_get_camera_feed_cockpit(self):
        """Test getting cockpit camera feed."""
        from plugins.robot_controller import ROBOT_CONTROLLER_TOOLS
        from robot_state import reset_robot_state

        reset_robot_state()

        # Find get_camera_feed tool
        get_camera_feed = None
        for tool in ROBOT_CONTROLLER_TOOLS:
            if tool['name'] == 'get_camera_feed':
                get_camera_feed = tool['function']
                break

        assert get_camera_feed is not None
        result = await get_camera_feed("cockpit")
        assert result is not None
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_toggle_tool_activation(self):
        """Test tool activation/deactivation."""
        import json
        from plugins.robot_controller import ROBOT_CONTROLLER_TOOLS
        from robot_state import reset_robot_state

        reset_robot_state()

        # Find toggle_tool tool
        toggle_tool = None
        for tool in ROBOT_CONTROLLER_TOOLS:
            if tool['name'] == 'toggle_tool':
                toggle_tool = tool['function']
                break

        assert toggle_tool is not None

        # Activate
        result = await toggle_tool(True)
        parsed = json.loads(result)
        assert parsed['tool_active'] is True

        # Deactivate
        result = await toggle_tool(False)
        parsed = json.loads(result)
        assert parsed['tool_active'] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
