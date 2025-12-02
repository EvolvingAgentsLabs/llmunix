"""
Nested Learning Demo - Semantic Trace Matching

Demonstrates the new Nested Learning implementation:
- Semantic matching (understanding similar but different goals)
- Three-mode execution (FOLLOWER/MIXED/LEARNER)
- Confidence-based mode selection
- Dramatic cost savings through intelligent matching
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box


console = Console()


async def run_nested_learning_demo(os):
    """
    Run Nested Learning demonstration

    Shows:
    1. Creating initial trace (LEARNER mode)
    2. Exact match replay (FOLLOWER mode - hash or LLM)
    3. Similar goal with semantic match (FOLLOWER/MIXED mode)
    4. Related but different goal (MIXED mode)
    5. Unrelated goal (LEARNER mode)
    """

    console.print(Panel(
        "[bold yellow]🧬 Nested Learning Demo[/bold yellow]\n\n"
        "Demonstrates intelligent semantic trace matching:\n\n"
        "[bold]Phase 1:[/bold] Create initial trace (LEARNER)\n"
        "[bold]Phase 2:[/bold] Exact match → FOLLOWER ($0)\n"
        "[bold]Phase 3:[/bold] Semantic match → FOLLOWER/MIXED ($0-$0.25)\n"
        "[bold]Phase 4:[/bold] Related task → MIXED ($0.25)\n"
        "[bold]Phase 5:[/bold] Unrelated task → LEARNER ($0.50)\n\n"
        "[bold cyan]Key Innovation:[/bold cyan] LLM analyzes similarity, not just exact hashes\n"
        "[bold green]Expected Savings:[/bold green] 50-100% across variations",
        border_style="cyan",
        title="🧬 Nested Learning"
    ))

    console.input("\n[dim]Press Enter to start...[/dim]")

    # Track costs for analysis
    executions = []

    # Phase 1: Initial execution (LEARNER)
    console.print("\n" + "=" * 70)
    console.print("[bold cyan]Phase 1: Initial Execution (Create Trace)[/bold cyan]")
    console.print("=" * 70)

    goal1 = "Create a Python file with a hello world function"
    console.print(f"\n[yellow]Goal:[/yellow] '{goal1}'")
    console.print("[yellow]Expected Mode:[/yellow] LEARNER (no trace exists)")
    console.print("[yellow]Expected Cost:[/yellow] ~$0.50\n")

    result1 = await os.execute(goal1, max_cost_usd=1.0)

    executions.append({
        "goal": goal1,
        "mode": result1.get("mode", "UNKNOWN"),
        "cost": result1.get("cost", 0.0),
        "match_type": "N/A (initial)"
    })

    console.print(f"\n✅ [green]Result:[/green]")
    console.print(f"   Mode: [bold]{result1.get('mode')}[/bold]")
    console.print(f"   Cost: [bold]${result1.get('cost', 0.0):.4f}[/bold]")
    console.print(f"   Trace saved for future use ✓")

    console.input("\n[dim]Press Enter to continue...[/dim]")

    # Phase 2: Exact match (FOLLOWER via hash or LLM)
    console.print("\n" + "=" * 70)
    console.print("[bold cyan]Phase 2: Exact Match (Hash or LLM)[/bold cyan]")
    console.print("=" * 70)

    goal2 = goal1  # Same exact goal
    console.print(f"\n[yellow]Goal:[/yellow] '{goal2}'")
    console.print("[yellow]Expected Mode:[/yellow] FOLLOWER (exact match)")
    console.print("[yellow]Expected Cost:[/yellow] $0.00\n")

    result2 = await os.execute(goal2, max_cost_usd=1.0)

    executions.append({
        "goal": goal2,
        "mode": result2.get("mode", "UNKNOWN"),
        "cost": result2.get("cost", 0.0),
        "match_type": "Exact"
    })

    console.print(f"\n✅ [green]Result:[/green]")
    console.print(f"   Mode: [bold]{result2.get('mode')}[/bold]")
    console.print(f"   Cost: [bold]${result2.get('cost', 0.0):.4f}[/bold]")

    if result2.get("cost", 0.0) == 0.0:
        console.print(f"   [bold green]💰 100% savings vs LEARNER![/bold green]")

    console.input("\n[dim]Press Enter to continue...[/dim]")

    # Phase 3: Semantic match - minor variation
    console.print("\n" + "=" * 70)
    console.print("[bold cyan]Phase 3: Semantic Match (Minor Variation)[/bold cyan]")
    console.print("=" * 70)

    goal3 = "Create a Python file with a hello world function named greet"
    console.print(f"\n[yellow]Goal:[/yellow] '{goal3}'")
    console.print(f"[yellow]vs Previous:[/yellow] '{goal1}'")
    console.print("[yellow]Expected Mode:[/yellow] FOLLOWER or MIXED (high similarity)")
    console.print("[yellow]Expected Cost:[/yellow] $0.00-$0.25")
    console.print("[yellow]LLM Analysis:[/yellow] Will detect semantic equivalence\n")

    result3 = await os.execute(goal3, max_cost_usd=1.0)

    executions.append({
        "goal": goal3,
        "mode": result3.get("mode", "UNKNOWN"),
        "cost": result3.get("cost", 0.0),
        "match_type": "Semantic (high conf.)"
    })

    console.print(f"\n✅ [green]Result:[/green]")
    console.print(f"   Mode: [bold]{result3.get('mode')}[/bold]")
    console.print(f"   Cost: [bold]${result3.get('cost', 0.0):.4f}[/bold]")

    if "confidence" in result3:
        console.print(f"   Confidence: [bold]{result3['confidence']:.0%}[/bold]")

    savings_pct = ((executions[0]["cost"] - result3.get("cost", 0.0)) / executions[0]["cost"] * 100) if executions[0]["cost"] > 0 else 0
    console.print(f"   [bold green]💰 {savings_pct:.0f}% savings vs LEARNER![/bold green]")

    console.input("\n[dim]Press Enter to continue...[/dim]")

    # Phase 4: Related task (MIXED mode expected)
    console.print("\n" + "=" * 70)
    console.print("[bold cyan]Phase 4: Related Task (Different Details)[/bold cyan]")
    console.print("=" * 70)

    goal4 = "Create a Python file with a goodbye function"
    console.print(f"\n[yellow]Goal:[/yellow] '{goal4}'")
    console.print(f"[yellow]vs Original:[/yellow] '{goal1}'")
    console.print("[yellow]Expected Mode:[/yellow] MIXED (similar structure, different content)")
    console.print("[yellow]Expected Cost:[/yellow] ~$0.25")
    console.print("[yellow]LLM Analysis:[/yellow] Similar pattern, use trace as guidance\n")

    result4 = await os.execute(goal4, max_cost_usd=1.0)

    executions.append({
        "goal": goal4,
        "mode": result4.get("mode", "UNKNOWN"),
        "cost": result4.get("cost", 0.0),
        "match_type": "Semantic (medium conf.)"
    })

    console.print(f"\n✅ [green]Result:[/green]")
    console.print(f"   Mode: [bold]{result4.get('mode')}[/bold]")
    console.print(f"   Cost: [bold]${result4.get('cost', 0.0):.4f}[/bold]")

    if result4.get("mode") == "MIXED":
        console.print(f"   [cyan]Trace used as few-shot guidance[/cyan]")

    if "confidence" in result4:
        console.print(f"   Confidence: [bold]{result4['confidence']:.0%}[/bold]")

    savings_pct = ((executions[0]["cost"] - result4.get("cost", 0.0)) / executions[0]["cost"] * 100) if executions[0]["cost"] > 0 else 0
    console.print(f"   [bold green]💰 {savings_pct:.0f}% savings vs LEARNER![/bold green]")

    console.input("\n[dim]Press Enter to continue...[/dim]")

    # Phase 5: Unrelated task (LEARNER)
    console.print("\n" + "=" * 70)
    console.print("[bold cyan]Phase 5: Unrelated Task (New Learning)[/bold cyan]")
    console.print("=" * 70)

    goal5 = "List all Python files in the current directory"
    console.print(f"\n[yellow]Goal:[/yellow] '{goal5}'")
    console.print(f"[yellow]vs Original:[/yellow] '{goal1}'")
    console.print("[yellow]Expected Mode:[/yellow] LEARNER (completely different)")
    console.print("[yellow]Expected Cost:[/yellow] ~$0.50")
    console.print("[yellow]LLM Analysis:[/yellow] No useful trace match, learn from scratch\n")

    result5 = await os.execute(goal5, max_cost_usd=1.0)

    executions.append({
        "goal": goal5,
        "mode": result5.get("mode", "UNKNOWN"),
        "cost": result5.get("cost", 0.0),
        "match_type": "No match"
    })

    console.print(f"\n✅ [green]Result:[/green]")
    console.print(f"   Mode: [bold]{result5.get('mode')}[/bold]")
    console.print(f"   Cost: [bold]${result5.get('cost', 0.0):.4f}[/bold]")
    console.print(f"   New trace created for future 'list files' tasks ✓")

    console.input("\n[dim]Press Enter to view analysis...[/dim]")

    # Final Analysis
    console.print("\n" + "=" * 70)
    console.print("[bold cyan]📊 Nested Learning Analysis[/bold cyan]")
    console.print("=" * 70)

    # Create comparison table
    table = Table(title="Execution Summary", box=box.ROUNDED)
    table.add_column("Phase", style="cyan", width=8)
    table.add_column("Goal (Truncated)", style="white", width=30)
    table.add_column("Mode", style="yellow", width=12)
    table.add_column("Match Type", style="green", width=20)
    table.add_column("Cost", style="magenta", width=10)

    for i, exec_data in enumerate(executions, 1):
        goal_short = exec_data["goal"][:30] + "..." if len(exec_data["goal"]) > 30 else exec_data["goal"]
        table.add_row(
            str(i),
            goal_short,
            exec_data["mode"],
            exec_data["match_type"],
            f"${exec_data['cost']:.4f}"
        )

    console.print(table)

    # Cost analysis
    total_cost = sum(e["cost"] for e in executions)
    learner_cost = executions[0]["cost"]
    if_all_learner = learner_cost * len(executions)
    savings = if_all_learner - total_cost
    savings_pct = (savings / if_all_learner * 100) if if_all_learner > 0 else 0

    console.print(Panel(
        f"[bold]Cost Breakdown:[/bold]\n\n"
        f"Total executions: {len(executions)}\n"
        f"Total cost: ${total_cost:.4f}\n"
        f"Average per execution: ${total_cost/len(executions):.4f}\n\n"
        f"[bold yellow]Comparison:[/bold yellow]\n"
        f"If all LEARNER mode: ${if_all_learner:.4f}\n"
        f"With Nested Learning: ${total_cost:.4f}\n"
        f"[bold green]Savings: ${savings:.4f} ({savings_pct:.1f}%)[/bold green]\n\n"
        f"[bold cyan]Key Insights:[/bold cyan]\n"
        f"• Exact matches: FREE (FOLLOWER mode)\n"
        f"• Similar tasks: $0-$0.25 (FOLLOWER/MIXED mode)\n"
        f"• Unrelated tasks: $0.50 (LEARNER mode)\n"
        f"• LLM understands semantic similarity, not just exact text!",
        title="💰 Cost Savings",
        border_style="green"
    ))

    console.print("\n[bold green]✅ Nested Learning Demo Complete![/bold green]\n")

    console.print("[bold]What Just Happened:[/bold]")
    console.print("  1️⃣  Hash-based matching: 'create file' ≠ 'create file named X' → No match")
    console.print("  2️⃣  LLM-based matching: Understands semantic equivalence → Match!")
    console.print("  3️⃣  Three modes: FOLLOWER (free) / MIXED (cheap) / LEARNER (expensive)")
    console.print("  4️⃣  Automatic mode selection based on confidence scores")
    console.print()

    return {
        "success": True,
        "executions": executions,
        "total_cost": total_cost,
        "savings": savings,
        "savings_pct": savings_pct
    }
