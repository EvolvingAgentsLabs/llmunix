#!/usr/bin/env python3
"""
Hybrid Architecture Demo - Markdown Mind with Python Body

This example demonstrates the LLMOS Hybrid Architecture where:
- **Mind (Cognitive)**: Agents defined in Markdown files (workspace/agents/*.md)
- **Body (Somatic)**: Python Kernel with robust tooling (llmos)
- **Magic**: System can create new agents by writing text files

This combines:
- llmunix: Pure Markdown flexibility and self-modification
- llmos: Python stability, security, and performance

Key Concepts:
1. Markdown-defined agents are loaded automatically
2. System can create new agents using create_agent tool
3. Hot-reloading: New agents available immediately
4. Self-modification: System evolves its own capabilities
"""

import asyncio
import sys
from pathlib import Path

# Add llmos to path
sys.path.insert(0, str(Path(__file__).parent.parent / "llmos"))

from boot import LLMOS


async def demo_list_markdown_agents():
    """Demo 1: List Markdown-defined agents"""
    print("\n" + "="*70)
    print("DEMO 1: List Markdown-Defined Agents")
    print("="*70)

    os_instance = LLMOS(budget_usd=5.0)
    await os_instance.boot()

    print("\n📋 Requesting list of available agents...")

    result = await os_instance.execute(
        goal="Use the list_agents tool to show me all available agents",
        mode="AUTO"  # Let system choose optimal mode (LEARNER for simple tool calls)
    )

    print(f"\n{result.get('output', 'No output')}")

    await os_instance.shutdown()


async def demo_create_new_agent():
    """Demo 2: System creates a new agent"""
    print("\n" + "="*70)
    print("DEMO 2: Self-Modification - Create New Agent")
    print("="*70)

    os_instance = LLMOS(budget_usd=10.0)
    await os_instance.boot()

    print("\n🎯 Task: Create a specialized 'poet' agent that writes haikus...")
    print()

    goal = """
    Create a new agent with these specifications:
    - Name: "haiku-poet"
    - Description: "Writes beautiful haikus about any topic. Use when you need creative, poetic expression."
    - Tools: ["Write"]
    - System Prompt: "You are a master haiku poet. When given a topic, write a thoughtful 5-7-5 haiku. Format:

    Line 1 (5 syllables)
    Line 2 (7 syllables)
    Line 3 (5 syllables)

    Make each haiku evocative and meaningful. Save your haiku to workspace/haikus/ with a descriptive filename."

    Use the create_agent tool to make this agent.
    """

    result = await os_instance.execute(
        goal=goal,
        mode="AUTO"  # Let system choose (LEARNER for simple tool calls)
    )

    print(f"\n✅ Result:\n{result.get('output', 'No output')}")

    await os_instance.shutdown()


async def demo_use_newly_created_agent():
    """Demo 3: Use the newly created agent"""
    print("\n" + "="*70)
    print("DEMO 3: Use Newly Created Agent")
    print("="*70)

    # Check if agent was created
    agent_file = Path("workspace/agents/haiku-poet.md")

    if not agent_file.exists():
        print("\n⚠️  Haiku poet agent not found. Run Demo 2 first.")
        return

    os_instance = LLMOS(budget_usd=5.0)
    await os_instance.boot()

    print("\n🎯 Task: Use the haiku-poet agent to write a haiku about quantum computing...")
    print()

    goal = """
    Delegate this task to the haiku-poet agent:
    "Write a haiku about quantum computing and save it to a file"

    Use the Task tool to delegate to haiku-poet.
    """

    result = await os_instance.execute(
        goal=goal,
        mode="ORCHESTRATOR"  # Requires delegation - keep ORCHESTRATOR mode
    )

    print(f"\n✅ Result:\n{result.get('output', 'No output')}")

    # Check if haiku was created
    haikus_dir = Path("workspace/haikus")
    if haikus_dir.exists():
        haikus = list(haikus_dir.glob("*.txt"))
        if haikus:
            print(f"\n📝 Haiku saved: {haikus[0].name}")
            print(f"\nContent:\n{haikus[0].read_text()}")

    await os_instance.shutdown()


async def demo_agent_evolution():
    """Demo 4: System improves an agent"""
    print("\n" + "="*70)
    print("DEMO 4: Self-Improvement - Modify Existing Agent")
    print("="*70)

    os_instance = LLMOS(budget_usd=5.0)
    await os_instance.boot()

    print("\n🎯 Task: Improve the haiku-poet agent to also create visual ASCII art...")
    print()

    goal = """
    Use the modify_agent tool to enhance the haiku-poet agent:
    - Field: "prompt"
    - Add this instruction to the system prompt:
    "After writing the haiku, also create simple ASCII art that represents the topic (5-7 lines).
    Include both the haiku and ASCII art in the saved file."

    This demonstrates system self-improvement.
    """

    result = await os_instance.execute(
        goal=goal,
        mode="AUTO"  # Let system choose (LEARNER for simple tool calls)
    )

    print(f"\n✅ Result:\n{result.get('output', 'No output')}")

    await os_instance.shutdown()


async def demo_markdown_inspection():
    """Demo 5: Inspect Markdown agent files"""
    print("\n" + "="*70)
    print("DEMO 5: Inspect Markdown Agent Definitions")
    print("="*70)

    print("\n📁 Markdown agent files in workspace/agents/:\n")

    agents_dir = Path("workspace/agents")
    if agents_dir.exists():
        for agent_file in sorted(agents_dir.glob("*.md")):
            print(f"   • {agent_file.name}")

            # Show first few lines
            content = agent_file.read_text(encoding='utf-8')
            lines = content.split('\n')[:15]
            print(f"\n   Preview:")
            for line in lines:
                print(f"     {line}")
            print()

    else:
        print("   No agents directory found.")


async def run_all_demos():
    """Run all demonstrations"""
    print("\n" + "="*70)
    print("LLMOS Hybrid Architecture - Complete Demonstration")
    print("Python Kernel + Markdown Mind")
    print("="*70)

    try:
        await demo_list_markdown_agents()
        input("\n▶️  Press Enter to continue to Demo 2...")

        await demo_create_new_agent()
        input("\n▶️  Press Enter to continue to Demo 3...")

        await demo_use_newly_created_agent()
        input("\n▶️  Press Enter to continue to Demo 4...")

        await demo_agent_evolution()
        input("\n▶️  Press Enter to see Markdown files...")

        await demo_markdown_inspection()

        print("\n" + "="*70)
        print("✅ All Demonstrations Complete!")
        print("="*70)

        print("\n🎓 Key Takeaways:")
        print("   1. Agents are defined in pure Markdown (workspace/agents/*.md)")
        print("   2. System can create new agents by writing files (create_agent tool)")
        print("   3. System can modify agents to improve capabilities (modify_agent tool)")
        print("   4. No restart required - agents loaded dynamically")
        print("   5. This is the 'HOPE' pattern: Higher-Order Programming Evolution")

        print("\n📚 Next Steps:")
        print("   • Explore workspace/agents/ directory")
        print("   • Read agent Markdown files")
        print("   • Modify agents and see changes take effect")
        print("   • Create your own agents using create_agent")

    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        demo_name = sys.argv[1]

        demo_map = {
            "1": demo_list_markdown_agents,
            "list": demo_list_markdown_agents,
            "2": demo_create_new_agent,
            "create": demo_create_new_agent,
            "3": demo_use_newly_created_agent,
            "use": demo_use_newly_created_agent,
            "4": demo_agent_evolution,
            "evolve": demo_agent_evolution,
            "5": demo_markdown_inspection,
            "inspect": demo_markdown_inspection,
        }

        if demo_name in demo_map:
            asyncio.run(demo_map[demo_name]())
        else:
            print(f"Unknown demo: {demo_name}")
            print("Available demos: 1, 2, 3, 4, 5, list, create, use, evolve, inspect")
    else:
        asyncio.run(run_all_demos())
