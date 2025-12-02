#!/usr/bin/env python3
"""
Demo script for Qiskit Studio Backend - LLM OS v3.3.0 Edition

This script demonstrates the key features including Advanced Tool Use:
1. Code generation via chat endpoint
2. Direct code execution
3. Learner → Follower → CRYSTALLIZED mode progression
4. PTC (Programmatic Tool Calling) for 90%+ token savings
5. Execution Layer statistics
"""

import asyncio
import httpx
import json
from pathlib import Path


class QiskitStudioDemo:
    """Demo client for Qiskit Studio Backend with v3.3.0 features"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)

    async def chat(self, message: str, session_id: str = "demo"):
        """Send a chat message"""
        response = await self.client.post(
            f"{self.base_url}/chat",
            json={
                "messages": [{"role": "user", "content": message}],
                "session_id": session_id
            }
        )
        return response.json()

    async def run_code(self, code: str):
        """Execute Qiskit code"""
        response = await self.client.post(
            f"{self.base_url}/run",
            json={"input_value": code}
        )
        return response.json()

    async def get_stats(self):
        """Get backend statistics including Execution Layer metrics"""
        response = await self.client.get(f"{self.base_url}/stats")
        return response.json()

    async def close(self):
        """Close the client"""
        await self.client.aclose()


async def demo_chat_code_generation():
    """Demo 1: Generate quantum code via chat"""
    print("\n" + "="*60)
    print("DEMO 1: Code Generation via Chat Endpoint")
    print("="*60)

    demo = QiskitStudioDemo()

    try:
        print("\n📝 Request: Generate a Bell state circuit")
        result = await demo.chat("Create a Bell state circuit and measure it")

        metadata = result.get('metadata', {})
        print(f"\n🤖 Agent: {metadata.get('agent', 'N/A')}")
        print(f"🎯 Mode: {metadata.get('mode', 'N/A')}")
        print(f"💰 Cost: ${metadata.get('cost', 0):.4f}")
        print(f"💾 Cached: {metadata.get('cached', False)}")

        # New v3.3.0 metadata
        if metadata.get('ptc_used'):
            print(f"⚡ PTC Used: Yes (Tokens saved: {metadata.get('tokens_saved', 0)})")

        content = result.get('output', result.get('content', ''))
        print(f"\n📄 Response:\n{content[:500]}...")

    finally:
        await demo.close()


async def demo_code_execution():
    """Demo 2: Direct code execution"""
    print("\n" + "="*60)
    print("DEMO 2: Direct Code Execution")
    print("="*60)

    demo = QiskitStudioDemo()

    try:
        code = """
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.primitives import Sampler

# Create a 2-qubit Bell state
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

print("Circuit created:")
print(qc)

# Simulate
sampler = Sampler()
job = sampler.run(qc, shots=100)
result = job.result()

print("\\nQuasi-probabilities:")
print(result.quasi_dists[0])
"""

        print("\n⚙️  Executing Qiskit code...")
        result = await demo.run_code(code)

        print(f"\n✅ Execution Output:\n{result['output']}")

    finally:
        await demo.close()


async def demo_cost_savings():
    """Demo 3: Learner → Follower → PTC cost savings"""
    print("\n" + "="*60)
    print("DEMO 3: Learner → Follower Cost Savings (with PTC)")
    print("="*60)

    demo = QiskitStudioDemo()

    try:
        message = "Create a 3-qubit GHZ state circuit"

        # First request (LEARNER mode)
        print(f"\n📝 First request: {message}")
        print("   Mode: LEARNER (will reason and generate)")
        result1 = await demo.chat(message, session_id="cost-demo-1")

        metadata1 = result1.get('metadata', {})
        cost1 = metadata1.get('cost', 0)
        mode1 = metadata1.get('mode', 'N/A')
        cached1 = metadata1.get('cached', False)

        print(f"   💰 Cost: ${cost1:.4f}")
        print(f"   🎯 Mode: {mode1}")
        print(f"   💾 Cached: {cached1}")

        # Second request (FOLLOWER mode - should use PTC)
        print(f"\n📝 Second request: {message}")
        print("   Mode: FOLLOWER (should use PTC for 90%+ savings)")
        result2 = await demo.chat(message, session_id="cost-demo-2")

        metadata2 = result2.get('metadata', {})
        cost2 = metadata2.get('cost', 0)
        mode2 = metadata2.get('mode', 'N/A')
        cached2 = metadata2.get('cached', False)
        ptc_used = metadata2.get('ptc_used', False)
        tokens_saved = metadata2.get('tokens_saved', 0)

        print(f"   💰 Cost: ${cost2:.4f}")
        print(f"   🎯 Mode: {mode2}")
        print(f"   💾 Cached: {cached2}")
        if ptc_used:
            print(f"   ⚡ PTC: Active (tool sequence replayed outside context!)")
            print(f"   📊 Tokens Saved: {tokens_saved}")

        # Summary
        print("\n📊 Summary:")
        print(f"   First request:  ${cost1:.4f} ({mode1})")
        print(f"   Second request: ${cost2:.4f} ({mode2})")

        if ptc_used:
            print(f"   ⚡ PTC ACTIVATED: Tool calls executed outside context window!")
        if cost2 == 0.0 or cost2 < 0.01:
            print(f"   ✨ Savings: ~100% (FOLLOWER mode with PTC!)")
        elif cost1 > 0:
            savings = ((cost1 - cost2) / cost1 * 100)
            print(f"   💡 Savings: {savings:.1f}%")

    finally:
        await demo.close()


async def demo_security():
    """Demo 4: Security hooks in action"""
    print("\n" + "="*60)
    print("DEMO 4: Security Hooks")
    print("="*60)

    demo = QiskitStudioDemo()

    try:
        # Try to execute malicious code
        malicious_code = """
import os
os.system("echo 'Attempting system access...'")
"""

        print("\n⚠️  Attempting to execute malicious code:")
        print(malicious_code)
        print("\n🔒 LLM OS Security Hooks should block this...")

        result = await demo.run_code(malicious_code)

        print(f"\n✅ Security Response:\n{result['output']}")

        if "Security Error" in result['output']:
            print("\n✅ SUCCESS: Malicious code was blocked!")
        else:
            print("\n⚠️  WARNING: Code was not blocked (check security hooks)")

    finally:
        await demo.close()


async def demo_statistics():
    """Demo 5: View backend statistics including Execution Layer"""
    print("\n" + "="*60)
    print("DEMO 5: Backend Statistics (v3.3.0 with Execution Layer)")
    print("="*60)

    demo = QiskitStudioDemo()

    try:
        print("\n📊 Fetching statistics...")
        stats = await demo.get_stats()

        print(f"\n🏷️  Version: {stats.get('version', 'N/A')}")

        print("\n💰 Token Economy:")
        token_stats = stats.get('token_economy', {})
        print(f"   Budget:    ${token_stats.get('budget_usd', 0):.2f}")
        print(f"   Spent:     ${token_stats.get('spent_usd', 0):.2f}")
        print(f"   Remaining: ${token_stats.get('remaining_usd', 0):.2f}")
        print(f"   Transactions: {token_stats.get('transactions', 0)}")

        print("\n🧠 Memory:")
        mem_stats = stats.get('memory', {})
        print(f"   Total Traces:        {mem_stats.get('total_traces', 0)}")
        print(f"   High-Confidence:     {mem_stats.get('high_confidence_traces', 0)}")
        print(f"   Traces with PTC:     {mem_stats.get('traces_with_tool_calls', 0)}")
        print(f"   Facts:               {mem_stats.get('facts', 0)}")

        print("\n🤖 Agents:")
        agent_stats = stats.get('agents', {})
        print(f"   Registered: {agent_stats.get('registered', 0)}")
        available = agent_stats.get('available', [])
        print(f"   Available:  {', '.join(available) if available else 'None'}")

        print("\n💬 Sessions:")
        session_stats = stats.get('sessions', {})
        print(f"   Active:         {session_stats.get('active', 0)}")
        print(f"   Total Messages: {session_stats.get('total_messages', 0)}")

        # New v3.3.0 Execution Layer stats
        exec_layer = stats.get('execution_layer', {})
        if exec_layer.get('enabled'):
            print("\n⚡ Execution Layer (v3.3.0):")

            ptc_stats = exec_layer.get('ptc', {})
            print(f"\n   PTC (Programmatic Tool Calling):")
            print(f"      Enabled:          {ptc_stats.get('enabled', False)}")
            print(f"      Active Containers: {ptc_stats.get('active_containers', 0)}")
            print(f"      Total Executions:  {ptc_stats.get('total_executions', 0)}")
            print(f"      Tokens Saved:      {ptc_stats.get('tokens_saved', 0)}")

            tool_search = exec_layer.get('tool_search', {})
            print(f"\n   Tool Search:")
            print(f"      Enabled:         {tool_search.get('enabled', False)}")
            print(f"      Use Embeddings:  {tool_search.get('use_embeddings', False)}")
            print(f"      Registered Tools: {tool_search.get('registered_tools', 0)}")
            print(f"      Total Searches:   {tool_search.get('total_searches', 0)}")

            tool_examples = exec_layer.get('tool_examples', {})
            print(f"\n   Tool Examples:")
            print(f"      Enabled:            {tool_examples.get('enabled', False)}")
            print(f"      Generated Examples: {tool_examples.get('generated_examples', 0)}")

        # Mode distribution
        mode_dist = stats.get('mode_distribution', {})
        if any(mode_dist.values()):
            print("\n📈 Mode Distribution:")
            print(f"   CRYSTALLIZED: {mode_dist.get('crystallized', 0)}")
            print(f"   FOLLOWER:     {mode_dist.get('follower', 0)}")
            print(f"   MIXED:        {mode_dist.get('mixed', 0)}")
            print(f"   LEARNER:      {mode_dist.get('learner', 0)}")
            print(f"   ORCHESTRATOR: {mode_dist.get('orchestrator', 0)}")

    finally:
        await demo.close()


async def run_all_demos():
    """Run all demos including v3.3.0 Execution Layer features"""
    print("\n" + "="*70)
    print(" "*10 + "Qiskit Studio Backend - LLM OS v3.3.0 Edition")
    print(" "*15 + "with Advanced Tool Use (PTC, Tool Search)")
    print("="*70)

    try:
        # Check if server is running
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get("http://localhost:8000/")
                if response.status_code != 200:
                    print("\n❌ Error: Backend server is not responding")
                    print("   Start the server with: ./run.sh")
                    return
            except httpx.ConnectError:
                print("\n❌ Error: Cannot connect to backend server")
                print("   Start the server with: ./run.sh")
                return

        # Run demos
        await demo_chat_code_generation()
        await asyncio.sleep(1)

        await demo_code_execution()
        await asyncio.sleep(1)

        await demo_cost_savings()
        await asyncio.sleep(1)

        await demo_security()
        await asyncio.sleep(1)

        await demo_statistics()

        print("\n" + "="*70)
        print("✅ All demos completed successfully!")
        print("="*70)
        print("\nNext steps:")
        print("  1. Check the backend logs for detailed execution info")
        print("  2. Try the Qiskit Studio frontend at http://localhost:3000")
        print("  3. Review the README.md for more examples")
        print()

    except Exception as e:
        print(f"\n❌ Error running demos: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_all_demos())
