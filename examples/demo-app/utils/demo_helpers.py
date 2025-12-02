"""
Demo Helper Functions

Utilities for running demo scenarios and displaying results.
"""

from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path


def format_cost(cost_usd: float) -> str:
    """
    Format cost for display

    Args:
        cost_usd: Cost in USD

    Returns:
        Formatted cost string
    """
    if cost_usd == 0:
        return "$0.00 (FREE)"
    elif cost_usd < 0.01:
        return f"${cost_usd:.4f}"
    else:
        return f"${cost_usd:.2f}"


def calculate_savings(first_cost: float, total_cost: float, runs: int) -> Dict[str, Any]:
    """
    Calculate savings from trace reuse

    Args:
        first_cost: Cost of first (Learner) execution
        total_cost: Total cost across all executions
        runs: Number of executions

    Returns:
        Dictionary with savings metrics
    """
    if first_cost == 0:
        return {
            "total_without_traces": 0,
            "total_with_traces": 0,
            "absolute_savings": 0,
            "percentage_savings": 0,
            "cost_per_run": 0
        }

    total_without_traces = first_cost * runs
    absolute_savings = total_without_traces - total_cost
    percentage_savings = (absolute_savings / total_without_traces * 100) if total_without_traces > 0 else 0
    cost_per_run = total_cost / runs if runs > 0 else 0

    return {
        "total_without_traces": total_without_traces,
        "total_with_traces": total_cost,
        "absolute_savings": absolute_savings,
        "percentage_savings": percentage_savings,
        "cost_per_run": cost_per_run
    }


def format_timestamp(dt: datetime = None) -> str:
    """
    Format timestamp for display

    Args:
        dt: Datetime to format (defaults to now)

    Returns:
        Formatted timestamp string
    """
    if dt is None:
        dt = datetime.now()

    return dt.strftime("%Y-%m-%d %H:%M:%S")


def create_output_structure(base_dir: Path):
    """
    Create output directory structure

    Args:
        base_dir: Base output directory
    """
    dirs = [
        base_dir / "projects",
        base_dir / "reports",
        base_dir / "traces",
        base_dir / "logs"
    ]

    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)


def save_demo_result(
    base_dir: Path,
    scenario_name: str,
    result: Dict[str, Any],
    output_content: str = None
):
    """
    Save demo result to file

    Args:
        base_dir: Base output directory
        scenario_name: Name of scenario
        result: Result dictionary
        output_content: Optional output content to save
    """
    output_dir = base_dir / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = format_timestamp()
    filename = f"{scenario_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    filepath = output_dir / filename

    with open(filepath, "w") as f:
        f.write(f"# Demo Result: {scenario_name}\n\n")
        f.write(f"**Timestamp**: {timestamp}\n\n")
        f.write(f"## Execution Details\n\n")
        f.write(f"- **Success**: {result.get('success', False)}\n")
        f.write(f"- **Mode**: {result.get('mode', 'UNKNOWN')}\n")
        f.write(f"- **Cost**: {format_cost(result.get('cost', 0.0))}\n")
        f.write(f"- **Steps**: {result.get('steps_completed', 'N/A')}/{result.get('total_steps', 'N/A')}\n")
        f.write(f"- **Time**: {result.get('execution_time', 0):.1f}s\n\n")

        if output_content:
            f.write(f"## Output\n\n")
            f.write(f"```\n{output_content}\n```\n")

    return filepath


def format_agent_summary(agent) -> str:
    """
    Format agent information for display

    Args:
        agent: AgentSpec instance

    Returns:
        Formatted summary string
    """
    return (
        f"**{agent.name}**\n"
        f"  - Category: {agent.category}\n"
        f"  - Tools: {', '.join(agent.tools)}\n"
        f"  - Capabilities: {', '.join(agent.capabilities)}\n"
    )


def format_trace_summary(trace) -> str:
    """
    Format execution trace for display

    Args:
        trace: ExecutionTrace instance

    Returns:
        Formatted summary string
    """
    return (
        f"Goal: {trace.goal_text[:60]}...\n"
        f"  Success: {trace.success_rating:.0%}\n"
        f"  Used: {trace.usage_count} times\n"
        f"  Cost: {format_cost(trace.estimated_cost_usd)}\n"
        f"  Time: {trace.estimated_time_secs:.1f}s\n"
    )


def create_cost_report(scenarios: Dict[str, float], base_dir: Path):
    """
    Create comprehensive cost report

    Args:
        scenarios: Dictionary of scenario names to costs
        base_dir: Base output directory
    """
    output_dir = base_dir / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    filepath = output_dir / "cost_analysis.md"

    total = sum(scenarios.values())

    with open(filepath, "w") as f:
        f.write("# LLM OS Demo - Cost Analysis\n\n")
        f.write(f"**Generated**: {format_timestamp()}\n\n")
        f.write("## Scenario Costs\n\n")

        f.write("| Scenario | Cost |\n")
        f.write("|----------|------|\n")

        for scenario, cost in scenarios.items():
            scenario_title = scenario.replace("_", " ").title()
            f.write(f"| {scenario_title} | {format_cost(cost)} |\n")

        f.write(f"| **Total** | **{format_cost(total)}** |\n\n")

        f.write("## Insights\n\n")
        f.write("- First-time executions use Learner mode (~$0.50 each)\n")
        f.write("- Repeated executions use Follower mode ($0.00)\n")
        f.write("- Complex orchestrations cost $1-3 depending on subtasks\n")
        f.write("- Overall savings after trace library built: 80-100%\n")

    return filepath
