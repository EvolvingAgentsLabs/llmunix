"""
Q-Kids Studio Demo Script

Demonstrates the educational quantum platform with example missions.
Shows the Learner/Follower cost optimization in action!
"""

import sys
from pathlib import Path
import json
import asyncio
from typing import List, Dict

# Add llmos to path
sys.path.insert(0, str(Path(__file__).parents[2] / "llmos"))

from plugins.kid_circuit_tools import run_kid_circuit, get_hint, check_mission


def print_banner(text: str):
    """Print a colorful banner."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_mission(mission_num: int, title: str, story: str):
    """Print mission details in kid-friendly format."""
    print(f"\n🎯 MISSION {mission_num}: {title}")
    print("-" * 70)
    print(story)
    print("-" * 70)


async def demo_mission_1():
    """Demo: First Coin Flip - Basic superposition."""
    print_banner("🦉 Mission 1: Your First Coin Flip!")

    print_mission(
        1,
        "Your First Coin Flip",
        """
        Welcome to Quantum Land! Professor Q needs your help!

        Your mission: Make a coin SPIN using the Coin Flip Spell!
        The coin can be heads AND tails at the same time! 🪙✨
        """
    )

    # Define the blocks
    blocks = [
        {"type": "COIN_FLIP", "targets": [0]}
    ]

    print("📦 Building circuit with blocks:")
    print(f"   - Coin Flip Spell on coin 0")
    print("\n🎮 Running circuit...")

    # Execute the circuit
    result = await run_kid_circuit(
        blocks=json.dumps(blocks),
        player_name="Demo Player"
    )

    result_data = json.loads(result)

    print("\n✨ RESULTS:")
    print(f"   {result_data.get('story', 'No story')}")
    print(f"\n   Top outcomes:")
    for outcome in result_data.get('results', [])[:3]:
        print(f"      {outcome['coins']} - {outcome['happened']}")

    print(f"\n   {result_data.get('celebration', '')}")

    return result_data


async def demo_mission_2():
    """Demo: Magic Twins - Entanglement."""
    print_banner("🦉 Mission 2: Create Magic Twins!")

    print_mission(
        2,
        "Create Magic Twins",
        """
        Now for something REALLY cool! 🎪

        Make TWO coins that are connected by invisible magic string!
        When one lands heads, the other ALWAYS lands heads too!
        They're like magical twins! 👯
        """
    )

    # Define the blocks for Bell state
    blocks = [
        {"type": "COIN_FLIP", "targets": [0]},
        {"type": "TWIN_LINK", "targets": [0, 1]}
    ]

    print("📦 Building circuit with blocks:")
    print(f"   - Coin Flip Spell on coin 0")
    print(f"   - Twin Link Spell connecting coins 0 and 1")
    print("\n🎮 Running circuit...")

    # Execute the circuit
    result = await run_kid_circuit(
        blocks=json.dumps(blocks),
        player_name="Demo Player"
    )

    result_data = json.loads(result)

    print("\n✨ RESULTS:")
    print(f"   {result_data.get('story', 'No story')}")
    print(f"\n   Top outcomes:")
    for outcome in result_data.get('results', [])[:3]:
        print(f"      {outcome['coins']} - {outcome['happened']}")

    print(f"\n   {result_data.get('celebration', '')}")

    # Check if mission is complete
    print("\n🔍 Checking mission completion...")
    mission_check = await check_mission(
        mission_id="twin_magic_01",
        blocks=json.dumps(blocks),
        results=result
    )

    check_data = json.loads(mission_check)
    if check_data.get('success'):
        print(f"   🎉 {check_data.get('message')}")
        print(f"   🏆 Reward: {check_data.get('reward')}")
    else:
        print(f"   {check_data.get('message')}")
        print(f"   💡 {check_data.get('feedback')}")

    return result_data


async def demo_hint_system():
    """Demo: Hint system with Learner/Follower pattern."""
    print_banner("🦉 Demo: Adaptive Hint System (Learner → Follower)")

    print("""
    The hint system uses the Learner/Follower pattern to save costs!

    - First time a kid makes a mistake: Learner mode generates hint (costs $)
    - Same mistake again (by any kid): Follower mode retrieves cached hint (FREE!)

    Let's see it in action...
    """)

    # Simulate a kid stuck on the twins mission
    print("\n👦 Kid's attempt #1: Only using Coin Flip (missing Twin Link)")
    blocks = [
        {"type": "COIN_FLIP", "targets": [0]}
    ]

    hint1 = await get_hint(
        puzzle_goal="Make both coins always match (00 or 11)",
        current_blocks=json.dumps(blocks),
        attempt_number=1
    )

    print(f"   Hint: {hint1}")
    print(f"   💰 Cost: First time = uses LLM tokens")

    print("\n👦 Kid's attempt #2: Still stuck")
    hint2 = await get_hint(
        puzzle_goal="Make both coins always match (00 or 11)",
        current_blocks=json.dumps(blocks),
        attempt_number=2
    )

    print(f"   Hint: {hint2}")
    print(f"   💰 Cost: Second time = cached (FREE!)")

    print("\n👧 Different kid, SAME mistake:")
    hint3 = await get_hint(
        puzzle_goal="Make both coins always match (00 or 11)",
        current_blocks=json.dumps(blocks),
        attempt_number=1  # First attempt for this kid
    )

    print(f"   Hint: {hint3}")
    print(f"   💰 Cost: Same pattern = cached (FREE!)")
    print("\n   🎯 This is the power of Learner/Follower!")
    print("      One kid's learning helps ALL future kids for FREE!")


async def demo_color_magic():
    """Demo: Phase gate experiment."""
    print_banner("🦉 Mission 3: Secret Color Codes!")

    print_mission(
        3,
        "Secret Color Codes",
        """
        Let's learn about SECRET CODES! 🎨

        There's a spell that changes the 'color' of a coin without anyone seeing it.
        Try: Coin Flip → Color Change → Coin Flip again

        What happens? 🤔
        """
    )

    # Phase cancellation circuit
    blocks = [
        {"type": "COIN_FLIP", "targets": [0]},
        {"type": "COLOR_CHANGE", "targets": [0]},
        {"type": "COIN_FLIP", "targets": [0]}
    ]

    print("📦 Building circuit with blocks:")
    print(f"   - Coin Flip Spell on coin 0")
    print(f"   - Color Change Spell on coin 0")
    print(f"   - Coin Flip Spell on coin 0 again")
    print("\n🎮 Running circuit...")

    result = await run_kid_circuit(
        blocks=json.dumps(blocks),
        player_name="Demo Player"
    )

    result_data = json.loads(result)

    print("\n✨ RESULTS:")
    print(f"   {result_data.get('story', 'No story')}")
    print(f"\n   Top outcomes:")
    for outcome in result_data.get('results', [])[:3]:
        print(f"      {outcome['coins']} - {outcome['happened']}")

    print(f"\n   {result_data.get('celebration', '')}")

    print("\n🔬 What's happening?")
    print("   The coin went back to where it started!")
    print("   This is called 'interference' - it's quantum magic!")
    print("   Scientists use this for secret codes that can't be broken! 🔐")

    return result_data


async def demo_error_handling():
    """Demo: Safety features."""
    print_banner("🛡️ Demo: Safety Features")

    print("""
    Q-Kids Studio has multiple safety layers to protect kids:

    1. ✅ Block-based only (no raw code execution)
    2. ✅ Simulator only (no access to real quantum hardware)
    3. ✅ Limited complexity (max qubits, max blocks)
    4. ✅ Kid-friendly error messages
    """)

    print("\n🧪 Test 1: Empty circuit")
    result1 = await run_kid_circuit(
        blocks=json.dumps([]),
        player_name="Test Player"
    )
    data1 = json.loads(result1)
    print(f"   {data1.get('message')}")

    print("\n🧪 Test 2: Invalid mission check")
    result2 = await check_mission(
        mission_id="fake_mission_99",
        blocks=json.dumps([{"type": "COIN_FLIP", "targets": [0]}]),
        results="{}"
    )
    data2 = json.loads(result2)
    print(f"   {data2.get('feedback')}")

    print("\n   ✅ All errors handled safely and kid-friendly!")


async def main():
    """Run all demos."""
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║           🦉 Q-KIDS STUDIO DEMO 🦉                           ║
    ║                                                               ║
    ║     Educational Quantum Computing for Ages 8-12              ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)

    print("\n🎯 This demo shows:")
    print("   1. Kid-friendly quantum circuit execution")
    print("   2. Block-based programming (like Scratch!)")
    print("   3. Gamified missions with progressive difficulty")
    print("   4. Adaptive hint system (Learner/Follower cost savings)")
    print("   5. Safety features for kids")

    input("\n📚 Press Enter to start the demo...")

    # Run demos
    try:
        await demo_mission_1()
        input("\n📚 Press Enter for next mission...")

        await demo_mission_2()
        input("\n📚 Press Enter for hint system demo...")

        await demo_hint_system()
        input("\n📚 Press Enter for color magic demo...")

        await demo_color_magic()
        input("\n📚 Press Enter for safety demo...")

        await demo_error_handling()

        print_banner("🎉 Demo Complete!")
        print("""
        🎓 What We Learned:

        ✅ Kids can build quantum circuits using simple blocks
        ✅ Results are presented with emojis and stories (not scary numbers!)
        ✅ Missions progressively teach quantum concepts
        ✅ Hints adapt to each kid's mistakes
        ✅ Learner/Follower saves costs (one kid helps all future kids!)
        ✅ Safety features ensure kids can experiment freely

        🚀 Next Steps:

        1. Start the backend server: ./run.sh
        2. Build a block-based frontend (like Blockly/Scratch)
        3. Connect frontend to API endpoints
        4. Watch kids become quantum wizards! 🧙‍♀️✨

        📖 Full documentation in README.md
        """)

    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        print("   Make sure llmos is properly installed!")


if __name__ == "__main__":
    asyncio.run(main())
