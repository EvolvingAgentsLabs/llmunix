"""
Q-Kids Studio - FastAPI Backend Server (v3.4.0)

Educational quantum computing platform for children ages 8-12.
Provides safe, fun, gamified quantum learning with adaptive difficulty.

LLM OS v3.4.0 Features:
- Sentience Layer: Adaptive behavior based on internal state
- Execution Layer: PTC, Tool Search, Tool Examples
- Five Execution Modes: CRYSTALLIZED, FOLLOWER, MIXED, LEARNER, ORCHESTRATOR
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add llmos to path
sys.path.insert(0, str(Path(__file__).parents[2] / "llmos"))

from kernel.llm_os import LLMOS
from kernel.agent_factory import AgentSpec
from kernel.agent_loader import AgentLoader

# Agents directory path (Markdown agents)
AGENTS_DIR = Path(__file__).parent / "workspace" / "agents"


# ============================================================================
# MISSION DEFINITIONS
# ============================================================================

MISSIONS = {
    "coin_flip_01": {
        "id": "coin_flip_01",
        "title": "🪙 Your First Coin Flip",
        "level": 1,
        "story": """
        Welcome to Quantum Land! 🦉✨

        Professor Q needs your help! There's a magical coin that can do something
        AMAZING - it can be heads AND tails at the same time while it's spinning!

        Your mission: Make the coin SPIN using the Coin Flip Spell!
        """,
        "goal": "Add a Coin Flip Spell block and see what happens!",
        "required_skills": ["hadamard"],
        "required_blocks": ["COIN_FLIP"],
        "hints": [
            "🦉 Try dragging the Coin Flip Spell block to your workspace!",
            "🦉 Click the RUN button to see the magic happen!",
            "🦉 The coin should land on heads (😴) and tails (🌟) different times!"
        ],
        "reward": "quantum_explorer_badge",
        "next_mission": "twin_magic_01"
    },

    "twin_magic_01": {
        "id": "twin_magic_01",
        "title": "👯 Create Magic Twins",
        "level": 2,
        "story": """
        Awesome work on the coin flip! Now for something REALLY cool! 🎪

        What if we could make TWO coins that are connected by invisible magic string?
        When one coin lands on heads, the other ALWAYS lands on heads too!
        When one is tails, the other is ALSO tails! They're like magical twins!

        Your mission: Create two coins that always match!
        """,
        "goal": "Make both coins always land the same way (both 😴 or both 🌟)",
        "required_skills": ["hadamard", "cnot"],
        "required_blocks": ["COIN_FLIP", "TWIN_LINK"],
        "hints": [
            "🦉 First, make one coin spin with Coin Flip Spell",
            "🦉 Then use Twin Link Spell to connect two coins together",
            "🦉 Remember: The first coin gets the Coin Flip, then you link them!"
        ],
        "reward": "entanglement_master_badge",
        "next_mission": "color_magic_01"
    },

    "color_magic_01": {
        "id": "color_magic_01",
        "title": "🎨 Secret Color Codes",
        "level": 3,
        "story": """
        You're becoming a real Quantum Wizard! 🧙‍♀️

        Now let's learn about SECRET CODES! There's a spell that changes the
        'color' of a coin without anyone seeing it. It's like writing invisible ink!

        When you flip the coin twice and add a Color Change in between,
        something magical happens...

        Your mission: Discover what the Color Change Spell does!
        """,
        "goal": "Experiment with Color Change Spell between two Coin Flips",
        "required_skills": ["hadamard", "phase"],
        "required_blocks": ["COIN_FLIP", "COLOR_CHANGE"],
        "hints": [
            "🦉 Try: Coin Flip → Color Change → Coin Flip",
            "🦉 What happens to the coin at the end?",
            "🦉 This is how quantum computers make secret codes!"
        ],
        "reward": "phase_explorer_badge",
        "next_mission": "teleport_01"
    },

    "teleport_01": {
        "id": "teleport_01",
        "title": "🚀 The Teleportation Beam",
        "level": 4,
        "story": """
        This is THE COOLEST quantum trick ever! 🤯

        What if you could teleport information from one coin to another
        WITHOUT touching the second coin? Scientists actually do this in real life!

        It uses Magic Twins and some tricks with measurements.
        This is a HARD puzzle - but you can do it!

        Your mission: Build a teleportation circuit!
        """,
        "goal": "Teleport the state of one coin to another using entanglement",
        "required_skills": ["hadamard", "cnot", "measurement"],
        "required_blocks": ["COIN_FLIP", "TWIN_LINK", "LOOK"],
        "hints": [
            "🦉 You'll need at least 3 coins for this!",
            "🦉 Start by making Magic Twins (coins 1 and 2)",
            "🦉 Then use another Twin Link with coin 0 and coin 1",
            "🦉 Scientists use this for quantum internet!"
        ],
        "reward": "teleportation_wizard_badge",
        "next_mission": "noise_monsters_01"
    },

    "noise_monsters_01": {
        "id": "noise_monsters_01",
        "title": "👾 The Noise Monsters Attack",
        "level": 5,
        "story": """
        Oh no! There are NOISE MONSTERS trying to mess up your quantum coins! 👾

        Real quantum computers have this problem too. Things like vibrations
        and heat can make quantum coins stop working. But scientists have
        special SHIELDS to protect them!

        You'll learn how to use extra coins as 'bodyguards' to protect your data!

        Your mission: Build an error-correcting shield!
        """,
        "goal": "Protect one coin using two extra 'bodyguard' coins",
        "required_skills": ["hadamard", "cnot", "error_correction_basic"],
        "required_blocks": ["COIN_FLIP", "TWIN_LINK"],
        "hints": [
            "🦉 Use 3 coins total: 1 data coin, 2 bodyguard coins",
            "🦉 Link the data coin to BOTH bodyguards",
            "🦉 This is called the 'bit flip code' - it's real quantum science!"
        ],
        "reward": "error_correction_hero_badge",
        "next_mission": "valley_hunter_01"
    },

    "valley_hunter_01": {
        "id": "valley_hunter_01",
        "title": "🏔️ The Valley Hunter",
        "level": 6,
        "story": """
        Final challenge! This is what real quantum computers do! 🎯

        Imagine a bumpy landscape with hills and valleys. You want to find
        the LOWEST valley. Regular computers try every spot (takes forever!).
        Quantum computers can find it SUPER fast using a trick called VQE!

        You'll design a circuit that 'rolls downhill' to find the answer!

        Your mission: Find the lowest energy state!
        """,
        "goal": "Use quantum tricks to find the minimum of a simple function",
        "required_skills": ["hadamard", "cnot", "rotation", "measurement"],
        "required_blocks": ["COIN_FLIP", "TWIN_LINK", "HALF_SPIN", "LOOK"],
        "hints": [
            "🦉 This is advanced! Scientists use this to design new medicines!",
            "🦉 The pattern: Prepare → Measure → Adjust → Repeat",
            "🦉 You're doing real quantum chemistry - how cool is that?!"
        ],
        "reward": "quantum_scientist_badge",
        "next_mission": None  # Final mission!
    }
}


# ============================================================================
# DATA MODELS
# ============================================================================

class BlockData(BaseModel):
    type: str
    targets: List[int]


class PlayRequest(BaseModel):
    player_name: str
    blocks: List[BlockData]
    mission_id: Optional[str] = None


class HintRequest(BaseModel):
    player_name: str
    mission_id: str
    current_blocks: List[BlockData]
    attempt_number: int = 1


class CheckMissionRequest(BaseModel):
    player_name: str
    mission_id: str
    blocks: List[BlockData]


class PlayerProgress(BaseModel):
    player_name: str
    level: int = 1
    completed_missions: List[str] = []
    current_mission: str = "coin_flip_01"
    badges: List[str] = []
    total_attempts: int = 0


# ============================================================================
# IN-MEMORY SESSION STORAGE
# ============================================================================

class SessionManager:
    """Manages player sessions and progress."""

    def __init__(self):
        self.players: Dict[str, PlayerProgress] = {}
        self.session_history: Dict[str, List[Dict[str, Any]]] = {}

    def get_or_create_player(self, player_name: str) -> PlayerProgress:
        """Get existing player or create new one."""
        if player_name not in self.players:
            self.players[player_name] = PlayerProgress(player_name=player_name)
            self.session_history[player_name] = []
        return self.players[player_name]

    def update_player(self, player_name: str, updates: Dict[str, Any]) -> PlayerProgress:
        """Update player progress."""
        player = self.get_or_create_player(player_name)
        for key, value in updates.items():
            if hasattr(player, key):
                setattr(player, key, value)
        return player

    def add_history(self, player_name: str, event: Dict[str, Any]):
        """Add event to player history."""
        if player_name not in self.session_history:
            self.session_history[player_name] = []

        event["timestamp"] = datetime.now().isoformat()
        self.session_history[player_name].append(event)

    def get_skill_level(self, player_name: str) -> Dict[str, Any]:
        """Calculate player's current skill level."""
        player = self.get_or_create_player(player_name)
        history = self.session_history.get(player_name, [])

        # Calculate statistics
        recent_attempts = history[-10:] if len(history) >= 10 else history
        recent_successes = sum(1 for event in recent_attempts if event.get("success", False))

        return {
            "level": player.level,
            "completed_missions": len(player.completed_missions),
            "recent_success_rate": recent_successes / len(recent_attempts) if recent_attempts else 0,
            "badges": player.badges,
            "total_attempts": player.total_attempts
        }


# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Q-Kids Studio API",
    description="Educational quantum computing for kids ages 8-12, powered by LLM OS v3.4.0 with Sentience Layer",
    version="3.4.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize session manager
session_manager = SessionManager()

# Initialize LLM OS
llmos = None
professor_q = None
game_master = None

# Sentience components (v3.4.0)
sentience_manager = None
cognitive_kernel = None


def init_llmos():
    """Initialize LLM OS with Q-Kids Studio agents and Sentience Layer."""
    global llmos, professor_q, game_master, sentience_manager, cognitive_kernel

    print("🦉 Initializing Q-Kids Studio Backend (LLM OS v3.4.0)...")
    print("=" * 60)

    # Initialize LLM OS with configuration
    from kernel.config import LLMOSConfig, SentienceConfig

    # Configure for kids - higher safety, moderate curiosity for exploration
    config = LLMOSConfig(
        workspace=Path(__file__).parent / "workspace",
        sentience=SentienceConfig(
            enable_sentience=True,
            # Kid-focused valence setpoints
            safety_setpoint=0.7,  # Higher safety for children
            curiosity_setpoint=0.3,  # Encourage exploration/learning
            energy_setpoint=0.8,  # Keep energy high for engagement
            self_confidence_setpoint=0.5,  # Build confidence gradually
            # Context injection for adaptive responses
            inject_internal_state=True,
            inject_behavioral_guidance=True,
            # Self-improvement for detecting repetitive patterns
            enable_auto_improvement=True,
            boredom_threshold=-0.2,  # Lower threshold - kids benefit from variety
            # Persistence
            auto_persist=True,
            state_file="state/qkids_sentience.json"
        )
    )

    llmos = LLMOS(config=config)

    # Initialize Sentience Layer
    try:
        from kernel.sentience import SentienceManager
        from kernel.cognitive_kernel import CognitiveKernel

        state_path = Path(__file__).parent / "state" / "qkids_sentience.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)

        sentience_manager = SentienceManager(
            state_path=state_path,
            auto_persist=True
        )
        cognitive_kernel = CognitiveKernel(sentience_manager)

        print(f"✨ Sentience Layer initialized")
        print(f"   - Latent mode: {sentience_manager.get_state().latent_mode.value}")
        print(f"   - Safety: {sentience_manager.get_state().valence.safety:.2f}")
        print(f"   - Curiosity: {sentience_manager.get_state().valence.curiosity:.2f}")
    except ImportError as e:
        print(f"⚠️ Sentience Layer not available: {e}")
        sentience_manager = None
        cognitive_kernel = None

    # Load agents from Markdown files (Hybrid Architecture approach)
    print("📚 Loading agents from Markdown files...")
    agent_loader = AgentLoader(agents_dir=str(AGENTS_DIR))

    # Load Professor Q
    professor_q_def = agent_loader.load_agent("professor-q")
    if professor_q_def:
        professor_q = AgentSpec(
            name=professor_q_def.name,
            agent_type=professor_q_def.metadata.get("agent_type", "specialized"),
            category=professor_q_def.metadata.get("category", "education"),
            description=professor_q_def.description,
            tools=professor_q_def.tools,
            system_prompt=professor_q_def.system_prompt,
            version=professor_q_def.metadata.get("version", "1.0")
        )
        print(f"  - Loaded: {professor_q_def.name}")
    else:
        print("  - Warning: professor-q.md not found")

    # Load Game Master
    game_master_def = agent_loader.load_agent("game-master")
    if game_master_def:
        game_master = AgentSpec(
            name=game_master_def.name,
            agent_type=game_master_def.metadata.get("agent_type", "orchestration"),
            category=game_master_def.metadata.get("category", "education"),
            description=game_master_def.description,
            tools=game_master_def.tools,
            system_prompt=game_master_def.system_prompt,
            version=game_master_def.metadata.get("version", "1.0")
        )
        print(f"  - Loaded: {game_master_def.name}")
    else:
        print("  - Warning: game-master.md not found")

    # Register kid-safe circuit tools
    print("🔧 Registering kid-safe quantum tools...")
    plugins_path = Path(__file__).parent / "plugins"
    sys.path.insert(0, str(plugins_path))

    # Import plugin to register tools
    import kid_circuit_tools

    print("✅ Q-Kids Studio Backend ready!")
    print("🎨 Kids can now build quantum circuits safely!")
    print("=" * 60)


@app.on_event("startup")
async def startup_event():
    """Initialize on server startup."""
    init_llmos()


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint."""
    sentience_mode = None
    if sentience_manager:
        sentience_mode = sentience_manager.get_state().latent_mode.value

    return {
        "service": "Q-Kids Studio Backend",
        "status": "ready",
        "message": "🦉 Professor Q is ready to teach!",
        "version": "3.4.0",
        "llm_os_features": {
            "sentience_layer": sentience_manager is not None,
            "current_mode": sentience_mode
        }
    }


@app.get("/missions")
async def get_missions(player_name: Optional[str] = None):
    """Get all available missions, optionally filtered by player progress."""
    if player_name:
        player = session_manager.get_or_create_player(player_name)
        unlocked_missions = []

        for mission_id, mission in MISSIONS.items():
            if (mission["level"] <= player.level or
                mission_id in player.completed_missions):
                unlocked_missions.append({
                    **mission,
                    "completed": mission_id in player.completed_missions
                })

        return {
            "player": player_name,
            "level": player.level,
            "missions": unlocked_missions
        }

    return {"missions": list(MISSIONS.values())}


@app.get("/mission/{mission_id}")
async def get_mission(mission_id: str):
    """Get details for a specific mission."""
    if mission_id not in MISSIONS:
        raise HTTPException(status_code=404, detail="Mission not found")

    return MISSIONS[mission_id]


@app.get("/player/{player_name}")
async def get_player_progress(player_name: str):
    """Get player progress and statistics."""
    player = session_manager.get_or_create_player(player_name)
    skill_level = session_manager.get_skill_level(player_name)

    return {
        "player": player.dict(),
        "skill_level": skill_level,
        "current_mission": MISSIONS.get(player.current_mission),
        "history": session_manager.session_history.get(player_name, [])[-5:]  # Last 5 events
    }


@app.post("/play")
async def play_circuit(request: PlayRequest):
    """
    Execute a kid's block-based circuit.

    This endpoint:
    1. Translates blocks to safe Qiskit code
    2. Executes on simulator
    3. Returns kid-friendly results with emojis and stories
    4. Updates player progress
    """
    try:
        player = session_manager.get_or_create_player(request.player_name)
        player.total_attempts += 1

        # Convert blocks to JSON for tool
        blocks_json = json.dumps([block.dict() for block in request.blocks])

        # Use Professor Q to run the circuit and explain results
        result = await llmos.run_tool(
            "run_kid_circuit",
            blocks=blocks_json,
            player_name=request.player_name
        )

        # Parse result
        result_data = json.loads(result) if isinstance(result, str) else result

        # Add to history
        session_manager.add_history(request.player_name, {
            "action": "run_circuit",
            "blocks": [block.dict() for block in request.blocks],
            "mission_id": request.mission_id,
            "success": not result_data.get("error", False)
        })

        # Update sentience state based on kid's task outcome (v3.4.0)
        if cognitive_kernel:
            try:
                success = not result_data.get("error", False)
                cognitive_kernel.on_task_complete(
                    success=success,
                    cost=0.001,  # Minimal cost tracking for kids
                    mode="LEARNER",
                    goal=f"Circuit from {request.player_name}"
                )

                # Novel circuits boost curiosity
                if len(request.blocks) > 2:
                    cognitive_kernel.on_novel_task(f"Complex circuit: {len(request.blocks)} blocks")

            except Exception as e:
                print(f"⚠️ Sentience tracking: {e}")

        # Get Professor Q's explanation
        explanation_prompt = f"""
        A kid named {request.player_name} just ran this circuit:
        Blocks: {blocks_json}
        Results: {json.dumps(result_data)}

        Explain what happened in 1-2 simple sentences! Keep it fun and exciting!
        """

        explanation = await llmos.cortex.process(
            prompt=explanation_prompt,
            agent_spec=professor_q,
            context={"mode": "explanation"}
        )

        return {
            "player": request.player_name,
            "execution_results": result_data,
            "professor_says": explanation.response if hasattr(explanation, 'response') else str(explanation),
            "player_level": player.level,
            "badges": player.badges
        }

    except Exception as e:
        print(f"❌ Error in play_circuit: {e}")
        return {
            "error": True,
            "message": "Oops! Something went wrong. Let's try again! 🦉",
            "details": str(e)
        }


@app.post("/hint")
async def get_hint(request: HintRequest):
    """
    Get adaptive hint based on player's attempts.

    Uses Learner/Follower pattern:
    - First time this mistake is made: Learner generates hint (costs tokens)
    - Same mistake again: Follower retrieves cached hint (FREE!)
    """
    try:
        player = session_manager.get_or_create_player(request.player_name)

        # Get mission details
        mission = MISSIONS.get(request.mission_id)
        if not mission:
            raise HTTPException(status_code=404, detail="Mission not found")

        # Convert blocks to JSON
        blocks_json = json.dumps([block.dict() for block in request.current_blocks])

        # Call hint tool (uses Learner/Follower internally)
        hint = await llmos.run_tool(
            "get_hint",
            puzzle_goal=mission["goal"],
            current_blocks=blocks_json,
            attempt_number=request.attempt_number
        )

        # Add to history
        session_manager.add_history(request.player_name, {
            "action": "requested_hint",
            "mission_id": request.mission_id,
            "attempt_number": request.attempt_number
        })

        return {
            "player": request.player_name,
            "mission": mission["title"],
            "hint": hint,
            "attempt_number": request.attempt_number,
            "encouragement": "You're getting closer! Keep experimenting! 🌟"
        }

    except Exception as e:
        print(f"❌ Error in get_hint: {e}")
        return {
            "error": True,
            "message": "🦉 Professor Q is thinking... try asking again!",
            "details": str(e)
        }


@app.post("/check-mission")
async def check_mission(request: CheckMissionRequest):
    """
    Check if player's solution completes the mission.

    Awards badges and unlocks next missions on success!
    """
    try:
        player = session_manager.get_or_create_player(request.player_name)

        # Get mission details
        mission = MISSIONS.get(request.mission_id)
        if not mission:
            raise HTTPException(status_code=404, detail="Mission not found")

        # Convert blocks to JSON
        blocks_json = json.dumps([block.dict() for block in request.blocks])

        # Run the circuit to get results
        circuit_result = await llmos.run_tool(
            "run_kid_circuit",
            blocks=blocks_json,
            player_name=request.player_name
        )

        # Check mission completion
        mission_result = await llmos.run_tool(
            "check_mission",
            mission_id=request.mission_id,
            blocks=blocks_json,
            results=circuit_result
        )

        # Parse result
        mission_data = json.loads(mission_result) if isinstance(mission_result, str) else mission_result

        # Update player progress if successful
        if mission_data.get("success", False):
            if request.mission_id not in player.completed_missions:
                player.completed_missions.append(request.mission_id)

            # Award badge
            if mission["reward"] not in player.badges:
                player.badges.append(mission["reward"])

            # Level up if appropriate
            if mission["level"] >= player.level:
                player.level = mission["level"] + 1

            # Set next mission
            if mission["next_mission"]:
                player.current_mission = mission["next_mission"]

        # Add to history
        session_manager.add_history(request.player_name, {
            "action": "mission_check",
            "mission_id": request.mission_id,
            "success": mission_data.get("success", False),
            "blocks": [block.dict() for block in request.blocks]
        })

        return {
            "player": request.player_name,
            "mission_result": mission_data,
            "player_level": player.level,
            "badges": player.badges,
            "next_mission": MISSIONS.get(mission["next_mission"]) if mission.get("next_mission") else None
        }

    except Exception as e:
        print(f"❌ Error in check_mission: {e}")
        return {
            "error": True,
            "message": "Couldn't check your mission. Let's try again! 🦉",
            "details": str(e)
        }


@app.post("/ask-professor")
async def ask_professor(question: str, player_name: str):
    """
    Ask Professor Q a question about quantum computing.

    Kids can ask anything and get kid-friendly explanations!
    """
    try:
        player = session_manager.get_or_create_player(player_name)

        # Build context-aware prompt
        prompt = f"""
        {player_name} (Level {player.level}) asks: "{question}"

        Answer in your fun, kid-friendly style! Remember to:
        - Use simple words and analogies
        - Keep it to 2-3 sentences
        - Use emojis!
        - Be encouraging!
        """

        # Get Professor Q's answer
        answer = await llmos.cortex.process(
            prompt=prompt,
            agent_spec=professor_q,
            context={
                "player_level": player.level,
                "completed_missions": player.completed_missions
            }
        )

        # Add to history
        session_manager.add_history(player_name, {
            "action": "asked_question",
            "question": question
        })

        return {
            "player": player_name,
            "question": question,
            "professor_says": answer.response if hasattr(answer, 'response') else str(answer),
            "encouragement": "Great question! Keep learning! 🦉✨"
        }

    except Exception as e:
        print(f"❌ Error in ask_professor: {e}")
        return {
            "error": True,
            "message": "Professor Q is busy right now. Try again soon! 🦉",
            "details": str(e)
        }


@app.get("/leaderboard")
async def get_leaderboard(limit: int = 10):
    """Get top players by level and badges."""
    players = sorted(
        session_manager.players.values(),
        key=lambda p: (p.level, len(p.badges), len(p.completed_missions)),
        reverse=True
    )[:limit]

    return {
        "leaderboard": [
            {
                "player_name": p.player_name,
                "level": p.level,
                "badges": len(p.badges),
                "missions_completed": len(p.completed_missions)
            }
            for p in players
        ]
    }


@app.get("/stats")
async def get_stats():
    """Get overall platform statistics including Sentience Layer state."""
    total_players = len(session_manager.players)
    total_attempts = sum(p.total_attempts for p in session_manager.players.values())
    total_completions = sum(len(p.completed_missions) for p in session_manager.players.values())

    # Get sentience stats (v3.4.0)
    sentience_stats = {"enabled": False}
    if sentience_manager:
        state = sentience_manager.get_state()
        policy = cognitive_kernel.derive_policy() if cognitive_kernel else None

        sentience_stats = {
            "enabled": True,
            "latent_mode": state.latent_mode.value,
            "valence": {
                "safety": round(state.valence.safety, 3),
                "curiosity": round(state.valence.curiosity, 3),
                "energy": round(state.valence.energy, 3),
                "self_confidence": round(state.valence.self_confidence, 3)
            },
            "homeostatic_cost": round(state.valence.homeostatic_cost(), 4),
            "policy": {
                "allow_exploration": policy.allow_exploration if policy else True,
                "exploration_budget_multiplier": policy.exploration_budget_multiplier if policy else 1.0
            } if policy else {}
        }

    return {
        "version": "3.4.0",
        "total_players": total_players,
        "total_circuit_runs": total_attempts,
        "total_missions_completed": total_completions,
        "available_missions": len(MISSIONS),
        "active_sessions": len(session_manager.session_history),
        "sentience": sentience_stats
    }


@app.get("/sentience")
async def get_sentience():
    """
    Get detailed Sentience Layer state (v3.4.0).

    Shows how the system's internal state adapts based on interactions.
    """
    if not sentience_manager:
        return {
            "enabled": False,
            "message": "Sentience Layer not enabled"
        }

    state = sentience_manager.get_state()
    policy = cognitive_kernel.derive_policy() if cognitive_kernel else None

    # Kid-friendly descriptions of latent modes
    mode_descriptions = {
        "auto_creative": "Professor Q is in EXPLORATION mode! 🚀 Ready to try new things!",
        "auto_contained": "Professor Q is in FOCUS mode! 🎯 Let's solve this puzzle!",
        "balanced": "Professor Q is in NORMAL mode! 🦉 Ready to teach!",
        "recovery": "Professor Q is taking a breather! 😌 Let's do something simple!",
        "cautious": "Professor Q is being extra careful! 🛡️ Safety first!"
    }

    return {
        "enabled": True,
        "latent_mode": {
            "current": state.latent_mode.value,
            "description": mode_descriptions.get(state.latent_mode.value, "Unknown mode")
        },
        "valence": {
            "safety": {
                "value": round(state.valence.safety, 3),
                "setpoint": round(state.valence.safety_setpoint, 3),
                "kid_description": "How careful Professor Q is being"
            },
            "curiosity": {
                "value": round(state.valence.curiosity, 3),
                "setpoint": round(state.valence.curiosity_setpoint, 3),
                "kid_description": "How excited Professor Q is to explore"
            },
            "energy": {
                "value": round(state.valence.energy, 3),
                "setpoint": round(state.valence.energy_setpoint, 3),
                "kid_description": "How energetic Professor Q feels"
            },
            "self_confidence": {
                "value": round(state.valence.self_confidence, 3),
                "setpoint": round(state.valence.self_confidence_setpoint, 3),
                "kid_description": "How confident Professor Q is"
            }
        },
        "homeostatic_cost": round(state.valence.homeostatic_cost(), 4),
        "last_trigger": {
            "type": state.last_trigger.value if state.last_trigger else None,
            "reason": state.last_trigger_reason
        },
        "behavioral_guidance": state.to_behavioral_guidance(),
        "policy": {
            "allow_exploration": policy.allow_exploration if policy else True,
            "exploration_budget_multiplier": policy.exploration_budget_multiplier if policy else 1.0,
            "prefer_safe_modes": policy.prefer_safe_modes if policy else False
        } if policy else {}
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("🦉 Starting Q-Kids Studio Backend Server (LLM OS v3.4.0)...")
    print("📚 Educational Quantum Computing for Ages 8-12")
    print("✨ Sentience Layer: Adaptive teaching based on internal state")
    print("=" * 60)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
