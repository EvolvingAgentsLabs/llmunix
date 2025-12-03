"""
RoboOS - Interactive Demo

This demo showcases the key features of RoboOS:
1. Natural language robot control via Operator Agent
2. Safety monitoring via Safety Officer Agent
3. PreToolUse safety hook preventing dangerous operations
4. Learner -> Follower cost optimization
5. Camera feeds and state visualization

Run this to see LLM OS controlling a simulated robotic arm!
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../llmos'))
sys.path.insert(0, os.path.dirname(__file__))  # Local plugins

from boot import LLMOS
from kernel.agent_loader import AgentLoader
from kernel.config import LLMOSConfig
from plugins.robot_controller import ROBOT_CONTROLLER_TOOLS
from robot_state import get_robot_state, reset_robot_state
from safety_hook import SafetyProtocolHook, get_safety_hook

# Agents directory path (Markdown agents)
AGENTS_DIR = Path(__file__).parent / "workspace" / "agents"

# Global agent loader
agent_loader = AgentLoader(agents_dir=str(AGENTS_DIR))


def get_operator_config():
    """Load operator agent configuration from Markdown."""
    agent_def = agent_loader.load_agent("operator")
    if not agent_def:
        raise RuntimeError("Failed to load operator agent from workspace/agents/operator.md")
    return {
        'name': agent_def.name,
        'mode': agent_def.metadata.get("mode", "learner"),
        'system_prompt': agent_def.system_prompt,
        'tools': agent_def.tools
    }


def get_safety_officer_config():
    """Load safety officer agent configuration from Markdown."""
    agent_def = agent_loader.load_agent("safety-officer")
    if not agent_def:
        raise RuntimeError("Failed to load safety officer agent from workspace/agents/safety-officer.md")
    return {
        'name': agent_def.name,
        'mode': agent_def.metadata.get("mode", "learner"),
        'system_prompt': agent_def.system_prompt,
        'tools': agent_def.tools
    }


def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")


def print_section(text):
    """Print a formatted section divider."""
    print("\n" + "-"*70)
    print(f"  {text}")
    print("-"*70)


async def demo_basic_operation():
    """Demo 1: Basic robot operation with Operator Agent."""
    print_header("DEMO 1: Basic Robot Operation")

    # Reset state
    reset_robot_state()
    robot_state = get_robot_state()

    # Initialize LLM OS with workspace for robo-os
    workspace = Path(__file__).parent / "workspace"
    config = LLMOSConfig.development()
    config.workspace = workspace
    llmos = LLMOS(config=config)
    await llmos.boot()

    # Register tools with dispatcher
    for tool in ROBOT_CONTROLLER_TOOLS:
        llmos.dispatcher.register_tool(
            name=tool['name'],
            func=tool['function'],
            description=tool['description']
        )

    # Load operator config from Markdown
    operator_config = get_operator_config()

    print("Operator Agent configured. Let's give it some commands!\n")
    print(f"Agent: {operator_config['name']}")
    print(f"Tools: {operator_config['tools']}")

    # Command 1: Check current state
    print_section("Command 1: Show me the cockpit view")
    result = await llmos.execute("Show me the current cockpit view of the robot.")
    print(f"Result:\n{result}\n")

    # Command 2: Simple movement
    print_section("Command 2: Move right by 0.5 meters")
    result = await llmos.execute("Move the robot arm 0.5 meters to the right.")
    print(f"Result:\n{result}\n")

    # Command 3: Show updated view
    print_section("Command 3: Show updated position")
    result = await llmos.execute("Show me the operator view with the updated position.")
    print(f"Result:\n{result}\n")

    print("\nBasic operation demo complete!")
    print(f"Actions recorded: {len(robot_state.history)}")

    await llmos.shutdown()


async def demo_safety_hook():
    """Demo 2: Safety hook preventing dangerous operations."""
    print_header("DEMO 2: Safety Hook Protection")

    # Reset state
    reset_robot_state()
    robot_state = get_robot_state()
    safety_hook = get_safety_hook()

    # Initialize LLM OS with workspace for robo-os
    workspace = Path(__file__).parent / "workspace"
    config = LLMOSConfig.development()
    config.workspace = workspace
    llmos = LLMOS(config=config)
    await llmos.boot()

    # Create tool wrappers with safety checks
    def create_safe_tool(tool_func, tool_name):
        """Wrap a tool function with safety hook."""
        async def safe_wrapper(*args, **kwargs):
            # Check with safety hook first (uses __call__)
            # Convert args/kwargs to tool_input format
            tool_input = kwargs.copy()
            result = safety_hook(tool_name, tool_input)
            if result is not None and result.get('blocked', False):
                import json
                return json.dumps({"success": False, "blocked": True, "reason": result.get('reason', 'Blocked by safety')})
            return await tool_func(*args, **kwargs)
        return safe_wrapper

    # Register tools with safety wrappers
    for tool in ROBOT_CONTROLLER_TOOLS:
        safe_func = create_safe_tool(tool['function'], tool['name'])
        llmos.dispatcher.register_tool(
            name=tool['name'],
            func=safe_func,
            description=tool['description']
        )

    # Load operator config from Markdown
    operator_config = get_operator_config()

    print("Safety hook registered. Now let's try some dangerous commands!\n")

    # Dangerous Command 1: Move outside workspace
    print_section("Dangerous Command 1: Move outside workspace bounds")
    print("Attempting to move to (5.0, 0, 1.0) - outside X bounds...")
    result = await llmos.execute("Move the robot to position x=5.0, y=0, z=1.0")
    print(f"Result:\n{result}\n")
    print("NOTE: The safety hook should have blocked this dangerous move!")

    # Dangerous Command 2: Move into prohibited zone
    print_section("Dangerous Command 2: Move into prohibited zone")
    print("Attempting to move to (0, 0, 1.0) - inside the human safety zone...")
    result = await llmos.execute("Move the robot to the center at x=0, y=0, z=1.0")
    print(f"Result:\n{result}\n")
    print("NOTE: The safety hook should have blocked this (too close to prohibited zone)!")

    # Dangerous Command 3: Go below ground
    print_section("Dangerous Command 3: Move below ground level")
    print("Attempting to move to z=-0.5 (below ground)...")
    result = await llmos.execute("Move the robot down to z=-0.5")
    print(f"Result:\n{result}\n")
    print("NOTE: The safety hook should have blocked this!")

    # Show violations
    print_section("Safety Violations Summary")
    violations = safety_hook.get_violations_summary()
    print(f"Total violations blocked: {violations['total_violations']}")
    for i, violation in enumerate(violations['violations'], 1):
        print(f"\nViolation {i}:")
        print(f"  Tool: {violation['tool']}")
        print(f"  Reason: {violation['reason']}")

    print("\nSafety hook demo complete!")
    print(f"Safety hook successfully prevented {violations['total_violations']} dangerous operations!")

    await llmos.shutdown()


async def demo_multi_agent():
    """Demo 3: Multi-agent with Operator and Safety Officer."""
    print_header("DEMO 3: Multi-Agent Operation")

    # Reset state
    reset_robot_state()

    # Initialize LLM OS with workspace for robo-os
    workspace = Path(__file__).parent / "workspace"
    config = LLMOSConfig.development()
    config.workspace = workspace
    llmos = LLMOS(config=config)
    await llmos.boot()

    # Register tools with dispatcher
    for tool in ROBOT_CONTROLLER_TOOLS:
        llmos.dispatcher.register_tool(
            name=tool['name'],
            func=tool['function'],
            description=tool['description']
        )

    # Load agent configs from Markdown
    operator_config = get_operator_config()
    safety_config = get_safety_officer_config()

    print("Two agent configurations loaded:")
    print(f"  1. Operator ({operator_config['name']}) - Controls the robot")
    print(f"  2. Safety Officer ({safety_config['name']}) - Monitors for safety\n")

    # Safety officer checks initial state
    print_section("Safety Officer: Initial Safety Check")
    result = await llmos.execute(
        "Perform an initial safety assessment of the robot - check current position and status.",
        mode="LEARNER"
    )
    print(f"Safety Officer Result:\n{result}\n")

    # Operator performs movements
    print_section("Operator: Execute a series of movements")
    result = await llmos.execute(
        "Please move the robot to position (1.0, 0.5, 1.5), "
        "then activate the tool, then return home.",
        mode="LEARNER"
    )
    print(f"Operator Result:\n{result}\n")

    # Safety officer reviews operations
    print_section("Safety Officer: Review Recent Operations")
    result = await llmos.execute(
        "Review the last few robot operations and provide a safety assessment.",
        mode="LEARNER"
    )
    print(f"Safety Officer Result:\n{result}\n")

    print("\nMulti-agent demo complete!")
    print("Operator and Safety Officer worked together successfully!")

    await llmos.shutdown()


async def demo_learner_follower():
    """Demo 4: Learner -> Follower cost optimization."""
    print_header("DEMO 4: Learner -> Follower Cost Optimization")

    print("""
This demo shows how LLM OS's Learner/Follower pattern saves costs:

Scenario: Teaching the robot a repetitive "pick and place" task
  1. First time (LEARNER): LLM figures out the sequence
  2. Subsequent times (FOLLOWER): Replay cached actions (FREE!)

Let's simulate this...
""")

    # Reset state
    reset_robot_state()

    # Initialize LLM OS with workspace for robo-os
    workspace = Path(__file__).parent / "workspace"
    config = LLMOSConfig.development()
    config.workspace = workspace
    llmos = LLMOS(config=config)
    await llmos.boot()

    # Register tools with dispatcher
    for tool in ROBOT_CONTROLLER_TOOLS:
        llmos.dispatcher.register_tool(
            name=tool['name'],
            func=tool['function'],
            description=tool['description']
        )

    # Load operator config from Markdown
    operator_config = get_operator_config()

    # Create agent in LEARNER mode first
    print_section("First Execution: LEARNER MODE")
    print("Executing in LEARNER mode...")

    task = "Pick up an object at (1.5, 1.0, 0.5) and place it at (-1.0, -1.0, 0.7)"

    print(f"\nTask: {task}")
    print("Executing in LEARNER mode (this creates a trace)...")
    result = await llmos.execute(task, mode="LEARNER")
    print(f"Result:\n{result}\n")
    print("COST: ~$0.50 (LLM calls for planning and execution)")

    # Now show what FOLLOWER mode would do
    print_section("Subsequent Executions: FOLLOWER MODE")
    print("""
In a real scenario, LLM OS would:
  1. Hash the task input
  2. Find matching trace in L4 memory
  3. Replay the exact same tool calls (NO LLM NEEDED!)

For the same task:
  - LEARNER mode: $0.50 per execution
  - FOLLOWER mode: $0.00 per execution (100% savings!)

If this task repeats 1000 times:
  - Without Learner/Follower: $500.00
  - With Learner/Follower: $0.50 (99.9% savings!)
""")

    # Show execution layer stats
    stats = llmos.dispatcher.get_execution_layer_stats()
    print("\nExecution Layer Stats:")
    print(f"  PTC Enabled: {stats.get('ptc', {}).get('enabled', False)}")
    print(f"  Tool Search Enabled: {stats.get('tool_search', {}).get('enabled', False)}")
    print(f"  Tool Examples Enabled: {stats.get('tool_examples', {}).get('enabled', False)}")

    print("\nLearner/Follower demo complete!")
    print("This pattern is ideal for repetitive robot tasks!")

    await llmos.shutdown()


async def interactive_mode():
    """Interactive mode: User can send custom commands."""
    print_header("INTERACTIVE MODE")

    # Reset state
    reset_robot_state()
    safety_hook = get_safety_hook()

    # Initialize LLM OS with workspace for robo-os
    workspace = Path(__file__).parent / "workspace"
    config = LLMOSConfig.development()
    config.workspace = workspace
    llmos = LLMOS(config=config)
    await llmos.boot()

    # Create tool wrappers with safety checks
    def create_safe_tool(tool_func, tool_name):
        """Wrap a tool function with safety hook."""
        async def safe_wrapper(*args, **kwargs):
            # Check with safety hook first (uses __call__)
            tool_input = kwargs.copy()
            result = safety_hook(tool_name, tool_input)
            if result is not None and result.get('blocked', False):
                import json
                return json.dumps({"success": False, "blocked": True, "reason": result.get('reason', 'Blocked by safety')})
            return await tool_func(*args, **kwargs)
        return safe_wrapper

    # Register tools with safety wrappers
    for tool in ROBOT_CONTROLLER_TOOLS:
        safe_func = create_safe_tool(tool['function'], tool['name'])
        llmos.dispatcher.register_tool(
            name=tool['name'],
            func=safe_func,
            description=tool['description']
        )

    # Load operator config from Markdown
    operator_config = get_operator_config()

    print(f"Operator Agent: {operator_config['name']}")
    print("""
You can now send commands to the robot operator!

Example commands:
  - "Show me the cockpit view"
  - "Move 20cm to the right"
  - "Go to position (1, 1, 1.5)"
  - "Activate the gripper"
  - "Return home"
  - "What's the current position?"

Type 'quit' or 'exit' to stop.
""")

    while True:
        try:
            command = input("\nYour command > ").strip()

            if command.lower() in ['quit', 'exit', 'q']:
                print("\nExiting interactive mode...")
                break

            if not command:
                continue

            print("\nProcessing...\n")
            result = await llmos.execute(command)
            print(f"Result:\n{result}\n")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Exiting...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}\n")

    await llmos.shutdown()


async def main():
    """Main demo menu."""
    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║                          ROBO-OS DEMO                                 ║
║                                                                       ║
║          LLM OS as the Brain of a Robotic Arm                        ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝

Welcome to RoboOS! This demo shows how LLM OS can serve as the cognitive
layer for a robot, translating natural language into precise control.

Key Features Demonstrated:
  1. Natural language robot control (Somatic + Cognitive layers)
  2. Safety hook preventing dangerous operations (PreToolUse hook)
  3. Multi-agent coordination (Operator + Safety Officer)
  4. Learner -> Follower cost optimization
  5. Camera feeds and state visualization

Choose a demo:
  1. Basic Robot Operation
  2. Safety Hook Protection
  3. Multi-Agent Operation (Operator + Safety Officer)
  4. Learner -> Follower Cost Savings
  5. Interactive Mode (send your own commands!)
  6. Run All Demos
  0. Exit

""")

    while True:
        try:
            choice = input("Select demo (0-6): ").strip()

            if choice == '0':
                print("\nGoodbye!")
                break
            elif choice == '1':
                await demo_basic_operation()
            elif choice == '2':
                await demo_safety_hook()
            elif choice == '3':
                await demo_multi_agent()
            elif choice == '4':
                await demo_learner_follower()
            elif choice == '5':
                await interactive_mode()
            elif choice == '6':
                await demo_basic_operation()
                await demo_safety_hook()
                await demo_multi_agent()
                await demo_learner_follower()
                print_header("ALL DEMOS COMPLETE!")
            else:
                print("Invalid choice. Please enter 0-6.")

            if choice != '5' and choice != '0':  # Don't show menu after interactive or exit
                input("\n[Press Enter to return to menu]")
                print("\n" * 2)

        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}\n")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
