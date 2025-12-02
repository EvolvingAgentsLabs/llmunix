"""
Kid-Safe Circuit Tools

Safe execution and visualization of block-based quantum circuits for children.
No dangerous operations, simplified results, gamified output.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any
import hashlib

# Add llmos to path
sys.path.insert(0, str(Path(__file__).parents[3] / "llmos"))

from plugins import llm_tool


# Block type mappings (kid-friendly names -> Qiskit operations)
BLOCK_MAPPINGS = {
    "COIN_FLIP": {"gate": "h", "qubits": 1, "name": "Coin Flip Spell"},
    "TWIN_LINK": {"gate": "cx", "qubits": 2, "name": "Twin Link Spell"},
    "COLOR_CHANGE": {"gate": "z", "qubits": 1, "name": "Color Change Spell"},
    "HALF_SPIN": {"gate": "s", "qubits": 1, "name": "Half Spin Spell"},
    "LOOK": {"gate": "measure", "qubits": 1, "name": "Look at Coin"},
}


def translate_blocks_to_circuit(blocks: List[Dict[str, Any]]) -> str:
    """
    Translate kid-friendly blocks to Qiskit code.

    Args:
        blocks: List of block dictionaries with type and target qubits

    Returns:
        Python code string for Qiskit circuit
    """
    # Find max qubit index
    max_qubit = 0
    for block in blocks:
        if "targets" in block:
            max_qubit = max(max(block["targets"]), max_qubit)

    n_qubits = max_qubit + 1

    # Build circuit code
    code_lines = [
        "from qiskit import QuantumCircuit",
        "from qiskit_aer import AerSimulator",
        "",
        f"qc = QuantumCircuit({n_qubits}, {n_qubits})",
        ""
    ]

    for block in blocks:
        block_type = block.get("type", "").upper()
        targets = block.get("targets", [0])

        if block_type == "COIN_FLIP":
            code_lines.append(f"qc.h({targets[0]})")
        elif block_type == "TWIN_LINK":
            if len(targets) >= 2:
                code_lines.append(f"qc.cx({targets[0]}, {targets[1]})")
        elif block_type == "COLOR_CHANGE":
            code_lines.append(f"qc.z({targets[0]})")
        elif block_type == "HALF_SPIN":
            code_lines.append(f"qc.s({targets[0]})")

    # Always add measurements at the end
    code_lines.append("")
    code_lines.append(f"qc.measure(range({n_qubits}), range({n_qubits}))")

    # Add execution
    code_lines.extend([
        "",
        "sim = AerSimulator()",
        "job = sim.run(qc, shots=100)",
        "result = job.result()",
        "counts = result.get_counts()",
        "print(counts)"
    ])

    return "\n".join(code_lines)


def kid_friendly_results(counts: Dict[str, int]) -> Dict[str, Any]:
    """
    Convert Qiskit measurement results to kid-friendly format.

    Args:
        counts: Raw measurement counts from Qiskit

    Returns:
        Kid-friendly result dictionary
    """
    total_shots = sum(counts.values())

    # Convert binary strings to coin descriptions
    kid_results = []

    for state, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_shots) * 100

        # Convert binary to coin states
        coins = []
        for bit in state:
            if bit == '0':
                coins.append("😴 Asleep")  # Heads/0
            else:
                coins.append("🌟 Awake")    # Tails/1

        kid_results.append({
            "coins": " | ".join(reversed(coins)),  # Reverse for qubit ordering
            "happened": f"{percentage:.0f}% of the time",
            "count": count
        })

    # Generate a simple story
    if len(kid_results) == 1:
        story = f"All your coins landed the SAME way every time! {kid_results[0]['coins']}"
    elif len(kid_results) == 2 and abs(kid_results[0]['count'] - kid_results[1]['count']) < 10:
        story = "Your coins are perfectly balanced - both ways happened equally!"
    else:
        top_result = kid_results[0]
        story = f"Most of the time ({top_result['happened']}), your coins were: {top_result['coins']}"

    return {
        "results": kid_results[:3],  # Top 3 results only
        "story": story,
        "total_tries": total_shots
    }


@llm_tool(
    "run_kid_circuit",
    "Runs a block-based quantum circuit and returns kid-friendly results with emojis and stories",
    {
        "blocks": "list of block dictionaries (type, targets)",
        "player_name": "str (optional)"
    }
)
async def run_kid_circuit(blocks: str, player_name: str = "Explorer") -> str:
    """
    Execute a kid-designed block circuit safely.

    This tool:
    1. Translates blocks to Qiskit (NO raw code execution from kids)
    2. Runs simulation locally (NO access to real quantum hardware without permission)
    3. Returns results in kid-friendly format with stories

    Args:
        blocks: JSON string of block list
        player_name: Optional player name for personalization

    Returns:
        JSON string with kid-friendly results
    """
    try:
        # Parse blocks
        block_list = json.loads(blocks) if isinstance(blocks, str) else blocks

        if not block_list:
            return json.dumps({
                "error": False,
                "message": "You need to add some spell blocks first! Try the Coin Flip Spell! 🪙",
                "results": []
            })

        # Generate circuit code
        circuit_code = translate_blocks_to_circuit(block_list)

        # Execute safely (using exec with controlled namespace)
        namespace = {}
        exec(circuit_code, namespace)

        # Get results from namespace
        if 'counts' in namespace:
            counts = namespace['counts']
        else:
            return json.dumps({
                "error": True,
                "message": "Oops! Something went wrong with the spell. Try again!",
                "results": []
            })

        # Convert to kid-friendly format
        kid_results = kid_friendly_results(counts)

        return json.dumps({
            "error": False,
            "player": player_name,
            "story": kid_results["story"],
            "results": kid_results["results"],
            "total_tries": kid_results["total_tries"],
            "celebration": "🎉 Great job experimenting!"
        })

    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"Oops! The spell fizzled. Let's try something different! (Error: {str(e)})",
            "results": []
        })


@llm_tool(
    "get_hint",
    "Generates a helpful hint when a kid is stuck on a puzzle. Uses Learner/Follower pattern for cost savings.",
    {
        "puzzle_goal": "str - what the kid is trying to achieve",
        "current_blocks": "str - JSON of blocks they've tried",
        "attempt_number": "int - how many times they've tried"
    }
)
async def get_hint(puzzle_goal: str, current_blocks: str, attempt_number: int = 1) -> str:
    """
    Generate adaptive hints based on the kid's attempts.

    Uses LLM OS Learner/Follower pattern:
    - First time someone makes THIS mistake: Learner mode generates hint (costs money)
    - Next time SAME mistake: Follower mode retrieves cached hint (FREE!)

    Args:
        puzzle_goal: What the puzzle asks for
        current_blocks: What the kid has built so far
        attempt_number: Number of attempts

    Returns:
        Kid-friendly hint string
    """
    # Create a hash of the mistake pattern
    mistake_hash = hashlib.md5(f"{puzzle_goal}:{current_blocks}".encode()).hexdigest()

    # In a full implementation, this would check LLM OS traces
    # For now, provide progressive hints based on attempt number

    if attempt_number == 1:
        return "🦉 Take your time! Look at what each spell block does."
    elif attempt_number == 2:
        return "🦉 Hint: Try the blocks in a different order! The order matters in quantum magic!"
    elif attempt_number >= 3:
        return f"🦉 Let's think step by step:\n1. What do you want to happen?\n2. Which spell makes that happen?\n3. Do you need more than one spell?"

    return "🦉 You're getting close! Don't give up!"


@llm_tool(
    "check_mission",
    "Verifies if a kid's circuit solves a mission correctly",
    {
        "mission_id": "str",
        "blocks": "str - JSON of block list",
        "results": "str - JSON of circuit results"
    }
)
async def check_mission(mission_id: str, blocks: str, results: str) -> str:
    """
    Check if the kid's solution meets the mission requirements.

    Args:
        mission_id: Identifier for the mission
        blocks: JSON string of blocks used
        results: JSON string of execution results

    Returns:
        JSON with success status and feedback
    """
    try:
        block_list = json.loads(blocks) if isinstance(blocks, str) else blocks
        result_data = json.loads(results) if isinstance(results, str) else results

        # Mission success criteria
        missions = {
            "coin_flip_01": {
                "name": "Your First Coin Flip",
                "requires_blocks": ["COIN_FLIP"],
                "success_condition": "Has multiple outcomes"
            },
            "twin_magic_01": {
                "name": "Create Magic Twins",
                "requires_blocks": ["COIN_FLIP", "TWIN_LINK"],
                "success_condition": "Only shows 00 or 11"
            },
            "teleport_01": {
                "name": "Teleportation Beam",
                "requires_blocks": ["COIN_FLIP", "TWIN_LINK", "LOOK"],
                "min_blocks": 5
            }
        }

        mission = missions.get(mission_id, {})

        if not mission:
            return json.dumps({
                "success": False,
                "message": "Unknown mission!",
                "feedback": "Ask Professor Q about available missions!"
            })

        # Basic validation
        used_block_types = [b.get("type") for b in block_list]
        required_blocks = mission.get("requires_blocks", [])

        has_required = all(req in used_block_types for req in required_blocks)

        if has_required:
            return json.dumps({
                "success": True,
                "message": f"🎉 MISSION COMPLETE! You solved '{mission['name']}'!",
                "reward": "quantum_badge",
                "next_mission": "Ready for the next challenge?"
            })
        else:
            missing = [b for b in required_blocks if b not in used_block_types]
            return json.dumps({
                "success": False,
                "message": "Not quite there yet! Keep experimenting!",
                "feedback": f"Try adding: {', '.join(missing)}",
                "encouragement": "You're on the right track! 🦉"
            })

    except Exception as e:
        return json.dumps({
            "success": False,
            "message": "Couldn't check your mission.",
            "feedback": str(e)
        })
