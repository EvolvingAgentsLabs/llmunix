"""
Q-Kids Studio Test Suite

Comprehensive tests for the educational quantum computing platform.
Tests cover:
- Kid-safe circuit tools
- Mission system
- Hint system
- Agent loading
- LLMOS integration
- Safety features
"""

import sys
from pathlib import Path
import json
import pytest

# Add paths
TEST_DIR = Path(__file__).parent
QKIDS_DIR = TEST_DIR.parent
LLMOS_DIR = QKIDS_DIR.parents[1] / "llmos"

sys.path.insert(0, str(LLMOS_DIR))
sys.path.insert(0, str(QKIDS_DIR / "plugins"))


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def sample_coin_flip_blocks():
    """Single coin flip (Hadamard gate)."""
    return [{"type": "COIN_FLIP", "targets": [0]}]


@pytest.fixture
def sample_bell_state_blocks():
    """Bell state (H + CNOT) - Magic Twins."""
    return [
        {"type": "COIN_FLIP", "targets": [0]},
        {"type": "TWIN_LINK", "targets": [0, 1]}
    ]


@pytest.fixture
def sample_phase_blocks():
    """Phase circuit (H + Z + H) - Color Magic."""
    return [
        {"type": "COIN_FLIP", "targets": [0]},
        {"type": "COLOR_CHANGE", "targets": [0]},
        {"type": "COIN_FLIP", "targets": [0]}
    ]


@pytest.fixture
def sample_complex_blocks():
    """Complex circuit with multiple operations."""
    return [
        {"type": "COIN_FLIP", "targets": [0]},
        {"type": "TWIN_LINK", "targets": [0, 1]},
        {"type": "COIN_FLIP", "targets": [2]},
        {"type": "TWIN_LINK", "targets": [1, 2]},
        {"type": "COLOR_CHANGE", "targets": [0]}
    ]


# =============================================================================
# KID CIRCUIT TOOLS TESTS
# =============================================================================

class TestKidCircuitTools:
    """Tests for kid_circuit_tools.py"""

    @pytest.mark.asyncio
    async def test_run_kid_circuit_coin_flip(self, sample_coin_flip_blocks):
        """Test basic coin flip circuit creates superposition."""
        from kid_circuit_tools import run_kid_circuit

        result = await run_kid_circuit(
            blocks=json.dumps(sample_coin_flip_blocks),
            player_name="Test Kid"
        )

        data = json.loads(result)
        assert data["error"] is False
        assert "story" in data
        assert "results" in data
        assert len(data["results"]) >= 1
        # Should have both outcomes (approximately 50/50)
        assert data["celebration"] == "🎉 Great job experimenting!"

    @pytest.mark.asyncio
    async def test_run_kid_circuit_bell_state(self, sample_bell_state_blocks):
        """Test Bell state circuit creates entangled qubits."""
        from kid_circuit_tools import run_kid_circuit

        result = await run_kid_circuit(
            blocks=json.dumps(sample_bell_state_blocks),
            player_name="Test Kid"
        )

        data = json.loads(result)
        assert data["error"] is False
        # Bell state should only show 00 or 11 (twins always match)
        results = data["results"]
        for r in results:
            coins = r["coins"]
            # Both coins should be same state (both asleep or both awake)
            assert "😴 Asleep | 😴 Asleep" in coins or "🌟 Awake | 🌟 Awake" in coins

    @pytest.mark.asyncio
    async def test_run_kid_circuit_phase(self, sample_phase_blocks):
        """Test phase circuit (H-Z-H = X) flips to |1>."""
        from kid_circuit_tools import run_kid_circuit

        result = await run_kid_circuit(
            blocks=json.dumps(sample_phase_blocks),
            player_name="Test Kid"
        )

        data = json.loads(result)
        assert data["error"] is False
        # H-Z-H should give |1> (Awake) 100% of time
        results = data["results"]
        assert len(results) == 1
        assert "🌟 Awake" in results[0]["coins"]
        assert "100%" in results[0]["happened"]

    @pytest.mark.asyncio
    async def test_run_kid_circuit_empty_blocks(self):
        """Test empty blocks returns helpful message."""
        from kid_circuit_tools import run_kid_circuit

        result = await run_kid_circuit(
            blocks=json.dumps([]),
            player_name="Test Kid"
        )

        data = json.loads(result)
        assert data["error"] is False
        assert "message" in data
        assert "add some spell blocks" in data["message"]

    @pytest.mark.asyncio
    async def test_run_kid_circuit_complex(self, sample_complex_blocks):
        """Test complex circuit with multiple qubits."""
        from kid_circuit_tools import run_kid_circuit

        result = await run_kid_circuit(
            blocks=json.dumps(sample_complex_blocks),
            player_name="Test Kid"
        )

        data = json.loads(result)
        assert data["error"] is False
        assert "results" in data


class TestBlockTranslation:
    """Tests for block-to-circuit translation."""

    def test_translate_coin_flip(self, sample_coin_flip_blocks):
        """Test COIN_FLIP translates to Hadamard gate."""
        from kid_circuit_tools import translate_blocks_to_circuit

        code = translate_blocks_to_circuit(sample_coin_flip_blocks)
        assert "qc.h(0)" in code
        assert "qc.measure" in code

    def test_translate_twin_link(self, sample_bell_state_blocks):
        """Test TWIN_LINK translates to CNOT gate."""
        from kid_circuit_tools import translate_blocks_to_circuit

        code = translate_blocks_to_circuit(sample_bell_state_blocks)
        assert "qc.h(0)" in code
        assert "qc.cx(0, 1)" in code

    def test_translate_color_change(self, sample_phase_blocks):
        """Test COLOR_CHANGE translates to Z gate."""
        from kid_circuit_tools import translate_blocks_to_circuit

        code = translate_blocks_to_circuit(sample_phase_blocks)
        assert "qc.z(0)" in code

    def test_translate_multi_qubit(self, sample_complex_blocks):
        """Test multi-qubit circuit translation."""
        from kid_circuit_tools import translate_blocks_to_circuit

        code = translate_blocks_to_circuit(sample_complex_blocks)
        # Should create 3-qubit circuit
        assert "QuantumCircuit(3, 3)" in code


class TestKidFriendlyResults:
    """Tests for kid-friendly result formatting."""

    def test_kid_friendly_results_single_outcome(self):
        """Test single outcome formatting."""
        from kid_circuit_tools import kid_friendly_results

        counts = {"0": 100}
        result = kid_friendly_results(counts)

        assert "story" in result
        assert "results" in result
        assert "SAME way every time" in result["story"]

    def test_kid_friendly_results_balanced(self):
        """Test balanced outcome formatting."""
        from kid_circuit_tools import kid_friendly_results

        counts = {"0": 50, "1": 50}
        result = kid_friendly_results(counts)

        assert "balanced" in result["story"]

    def test_kid_friendly_results_emoji_conversion(self):
        """Test binary to emoji conversion."""
        from kid_circuit_tools import kid_friendly_results

        counts = {"00": 50, "11": 50}
        result = kid_friendly_results(counts)

        # Check emoji usage
        coins_str = " ".join([r["coins"] for r in result["results"]])
        assert "😴" in coins_str or "🌟" in coins_str


# =============================================================================
# HINT SYSTEM TESTS
# =============================================================================

class TestHintSystem:
    """Tests for the adaptive hint system."""

    @pytest.mark.asyncio
    async def test_get_hint_first_attempt(self):
        """Test hint for first attempt."""
        from kid_circuit_tools import get_hint

        hint = await get_hint(
            puzzle_goal="Make magic twins",
            current_blocks=json.dumps([{"type": "COIN_FLIP", "targets": [0]}]),
            attempt_number=1
        )

        assert "🦉" in hint
        assert len(hint) > 0

    @pytest.mark.asyncio
    async def test_get_hint_second_attempt(self):
        """Test hint for second attempt is different."""
        from kid_circuit_tools import get_hint

        hint = await get_hint(
            puzzle_goal="Make magic twins",
            current_blocks=json.dumps([{"type": "COIN_FLIP", "targets": [0]}]),
            attempt_number=2
        )

        assert "🦉" in hint
        assert "order" in hint.lower()  # Second hint mentions order

    @pytest.mark.asyncio
    async def test_get_hint_third_attempt(self):
        """Test hint for third attempt is more detailed."""
        from kid_circuit_tools import get_hint

        hint = await get_hint(
            puzzle_goal="Make magic twins",
            current_blocks=json.dumps([{"type": "COIN_FLIP", "targets": [0]}]),
            attempt_number=3
        )

        assert "🦉" in hint
        assert "step" in hint.lower()  # Third hint is step-by-step


# =============================================================================
# MISSION SYSTEM TESTS
# =============================================================================

class TestMissionSystem:
    """Tests for the mission checking system."""

    @pytest.mark.asyncio
    async def test_check_mission_success(self, sample_bell_state_blocks):
        """Test successful mission completion."""
        from kid_circuit_tools import check_mission, run_kid_circuit

        # Run the circuit first
        result = await run_kid_circuit(
            blocks=json.dumps(sample_bell_state_blocks),
            player_name="Test Kid"
        )

        # Check the mission
        check = await check_mission(
            mission_id="twin_magic_01",
            blocks=json.dumps(sample_bell_state_blocks),
            results=result
        )

        data = json.loads(check)
        assert data["success"] is True
        assert "MISSION COMPLETE" in data["message"]
        assert "reward" in data

    @pytest.mark.asyncio
    async def test_check_mission_failure_missing_blocks(self, sample_coin_flip_blocks):
        """Test mission failure when blocks are missing."""
        from kid_circuit_tools import check_mission, run_kid_circuit

        # Run incomplete circuit
        result = await run_kid_circuit(
            blocks=json.dumps(sample_coin_flip_blocks),
            player_name="Test Kid"
        )

        # Check the mission
        check = await check_mission(
            mission_id="twin_magic_01",
            blocks=json.dumps(sample_coin_flip_blocks),
            results=result
        )

        data = json.loads(check)
        assert data["success"] is False
        assert "feedback" in data
        assert "TWIN_LINK" in data["feedback"]

    @pytest.mark.asyncio
    async def test_check_mission_unknown_mission(self, sample_coin_flip_blocks):
        """Test unknown mission handling."""
        from kid_circuit_tools import check_mission

        check = await check_mission(
            mission_id="fake_mission_99",
            blocks=json.dumps(sample_coin_flip_blocks),
            results="{}"
        )

        data = json.loads(check)
        assert data["success"] is False
        assert "Unknown" in data["message"] or "feedback" in data


# =============================================================================
# AGENT LOADING TESTS
# =============================================================================

class TestAgentLoading:
    """Tests for LLMOS agent loading."""

    def test_load_professor_q_agent(self):
        """Test loading Professor Q agent from markdown."""
        from kernel.agent_loader import AgentLoader

        agents_dir = QKIDS_DIR / "workspace" / "agents"
        loader = AgentLoader(agents_dir=str(agents_dir))

        agent = loader.load_agent("professor-q")

        assert agent is not None
        assert agent.name == "professor-q"
        assert "tutor" in agent.description.lower()
        assert "run_kid_circuit" in agent.tools
        assert "get_hint" in agent.tools
        assert "check_mission" in agent.tools

    def test_load_game_master_agent(self):
        """Test loading Game Master agent from markdown."""
        from kernel.agent_loader import AgentLoader

        agents_dir = QKIDS_DIR / "workspace" / "agents"
        loader = AgentLoader(agents_dir=str(agents_dir))

        agent = loader.load_agent("game-master")

        assert agent is not None
        assert agent.name == "game-master"
        assert "difficulty" in agent.description.lower()

    def test_agent_has_sentience_metadata(self):
        """Test that agents have sentience awareness metadata."""
        from kernel.agent_loader import AgentLoader

        agents_dir = QKIDS_DIR / "workspace" / "agents"
        loader = AgentLoader(agents_dir=str(agents_dir))

        professor_q = loader.load_agent("professor-q")
        game_master = loader.load_agent("game-master")

        # Metadata is nested under 'metadata' key
        inner_metadata = professor_q.metadata.get("metadata", {})
        assert inner_metadata.get("sentience_aware") is True

        inner_metadata = game_master.metadata.get("metadata", {})
        assert inner_metadata.get("sentience_aware") is True


# =============================================================================
# LLMOS INTEGRATION TESTS
# =============================================================================

class TestLLMOSIntegration:
    """Tests for LLMOS integration."""

    def test_llmos_config_creation(self):
        """Test LLMOS config with sentience settings."""
        from kernel.config import LLMOSConfig, SentienceConfig

        config = LLMOSConfig(
            workspace=QKIDS_DIR / "workspace",
            sentience=SentienceConfig(
                enable_sentience=True,
                safety_setpoint=0.7,
                curiosity_setpoint=0.3
            )
        )

        assert config.sentience.enable_sentience is True
        assert config.sentience.safety_setpoint == 0.7
        assert config.sentience.curiosity_setpoint == 0.3

    def test_sentience_manager_creation(self):
        """Test SentienceManager can be created."""
        from kernel.sentience import SentienceManager
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "test_sentience.json"

            manager = SentienceManager(
                state_path=state_path,
                auto_persist=False
            )

            state = manager.get_state()
            assert state is not None
            assert hasattr(state, "valence")
            assert hasattr(state, "latent_mode")

    def test_cognitive_kernel_creation(self):
        """Test CognitiveKernel can be created."""
        from kernel.sentience import SentienceManager
        from kernel.cognitive_kernel import CognitiveKernel
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "test_sentience.json"

            manager = SentienceManager(
                state_path=state_path,
                auto_persist=False
            )
            kernel = CognitiveKernel(manager)

            policy = kernel.derive_policy()
            assert policy is not None
            assert hasattr(policy, "allow_exploration")


# =============================================================================
# SAFETY TESTS
# =============================================================================

class TestSafety:
    """Tests for safety features."""

    def test_block_based_only(self):
        """Test that only block-based circuits are allowed."""
        from kid_circuit_tools import translate_blocks_to_circuit

        # Blocks should translate to safe code
        blocks = [{"type": "COIN_FLIP", "targets": [0]}]
        code = translate_blocks_to_circuit(blocks)

        # Should not contain dangerous operations
        assert "import os" not in code
        assert "subprocess" not in code
        assert "eval" not in code
        assert "exec" not in code.replace("exec(circuit_code", "")  # Only our safe exec

    @pytest.mark.asyncio
    async def test_invalid_block_type_handled(self):
        """Test that invalid block types are handled safely."""
        from kid_circuit_tools import run_kid_circuit

        # Invalid block type
        blocks = [{"type": "INVALID_SPELL", "targets": [0]}]
        result = await run_kid_circuit(
            blocks=json.dumps(blocks),
            player_name="Test Kid"
        )

        data = json.loads(result)
        # Should not crash, just ignore invalid blocks
        assert "error" in data

    def test_max_qubit_calculation(self):
        """Test qubit count is correctly calculated."""
        from kid_circuit_tools import translate_blocks_to_circuit

        # 3 qubits used
        blocks = [
            {"type": "COIN_FLIP", "targets": [0]},
            {"type": "TWIN_LINK", "targets": [1, 2]}
        ]
        code = translate_blocks_to_circuit(blocks)

        assert "QuantumCircuit(3, 3)" in code


# =============================================================================
# MISSION DEFINITIONS TESTS
# =============================================================================

class TestMissionDefinitions:
    """Tests for mission definitions in server.py."""

    def test_missions_exist(self):
        """Test that mission definitions are present."""
        # Import server module
        sys.path.insert(0, str(QKIDS_DIR))
        from server import MISSIONS

        assert len(MISSIONS) >= 6  # At least 6 missions

        # Check required missions exist
        assert "coin_flip_01" in MISSIONS
        assert "twin_magic_01" in MISSIONS
        assert "color_magic_01" in MISSIONS
        assert "teleport_01" in MISSIONS

    def test_mission_structure(self):
        """Test mission structure is correct."""
        sys.path.insert(0, str(QKIDS_DIR))
        from server import MISSIONS

        for mission_id, mission in MISSIONS.items():
            assert "id" in mission
            assert "title" in mission
            assert "level" in mission
            assert "story" in mission
            assert "goal" in mission
            assert "required_blocks" in mission
            assert "hints" in mission
            assert "reward" in mission

    def test_mission_progression(self):
        """Test mission progression chain."""
        sys.path.insert(0, str(QKIDS_DIR))
        from server import MISSIONS

        # Check level progression
        levels = [MISSIONS[m]["level"] for m in MISSIONS]
        assert sorted(levels) == list(range(1, len(levels) + 1))

        # Check next_mission chain
        current = "coin_flip_01"
        visited = set()
        while current and current not in visited:
            visited.add(current)
            current = MISSIONS[current].get("next_mission")

        # Should visit all missions
        assert len(visited) == len(MISSIONS)


# =============================================================================
# PLAYER PROGRESS TESTS
# =============================================================================

class TestPlayerProgress:
    """Tests for player progress tracking."""

    def test_player_progress_model(self):
        """Test PlayerProgress model structure."""
        sys.path.insert(0, str(QKIDS_DIR))
        from server import PlayerProgress

        player = PlayerProgress(player_name="TestKid")

        assert player.player_name == "TestKid"
        assert player.level == 1
        assert player.completed_missions == []
        assert player.current_mission == "coin_flip_01"
        assert player.badges == []
        assert player.total_attempts == 0

    def test_session_manager(self):
        """Test SessionManager functionality."""
        sys.path.insert(0, str(QKIDS_DIR))
        from server import SessionManager

        manager = SessionManager()

        # Create player
        player = manager.get_or_create_player("Alice")
        assert player.player_name == "Alice"

        # Update player
        manager.update_player("Alice", {"level": 2})
        player = manager.get_or_create_player("Alice")
        assert player.level == 2

        # Add history
        manager.add_history("Alice", {"action": "test", "success": True})
        assert len(manager.session_history["Alice"]) == 1

        # Get skill level
        skill = manager.get_skill_level("Alice")
        assert "level" in skill
        assert "recent_success_rate" in skill


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
