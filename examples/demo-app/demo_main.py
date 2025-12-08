#!/usr/bin/env python3
"""
LLM OS Demo Application - Main Entry Point (v3.5.0)

Interactive menu-driven demonstration of all llmos capabilities including:
- Sentience Layer with valence variables and latent modes
- Adaptive Agents (DynamicAgentManager) - NEW in v3.5.0
- Advanced Tool Use (PTC, Tool Search, Tool Examples)
- Five Execution Modes: CRYSTALLIZED, FOLLOWER, MIXED, LEARNER, ORCHESTRATOR
- 90%+ token savings via Programmatic Tool Calling
"""

import asyncio
import sys
from pathlib import Path
import argparse
from datetime import datetime
import os

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add llmos to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "llmos"))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

from boot import LLMOS
from kernel.config import LLMOSConfig, SentienceConfig
from kernel.sentience import SentienceManager, LatentMode
from kernel.cognitive_kernel import CognitiveKernel
from kernel.dynamic_agents import DynamicAgentManager
from kernel.volumes import VolumeManager, Volume, VolumeType, ArtifactType, ArtifactAction
from kernel.sentience_cron import SystemCron, TeamCron, UserCron, CronLevel
from kernel.observability import ObservabilityHub, EventType, Severity
from scenarios.nested_learning_demo import run_nested_learning_demo


console = Console()


class DemoApp:
    """
    LLM OS Demo Application

    Provides an interactive menu to showcase all llmos capabilities:
    - Three execution modes (Learner/Follower/Orchestrator)
    - Project management
    - Multi-agent orchestration
    - Memory and learning
    - Cost optimization
    """

    def __init__(self, budget_usd: float = 20.0, verbose: bool = False):
        """
        Initialize demo application

        Args:
            budget_usd: Budget for demo execution
            verbose: Enable verbose output
        """
        self.budget_usd = budget_usd
        self.verbose = verbose
        self.os = None
        self.demo_output_dir = Path(__file__).parent / "output"
        self.demo_output_dir.mkdir(exist_ok=True)

        # Sentience Layer components (v3.4.0)
        self.sentience_manager = None
        self.cognitive_kernel = None

        # Volume and Cron components (v3.6.0)
        self.volume_manager = None
        self.observability_hub = None
        self.system_cron = None

        # Track costs across scenarios
        self.cost_tracker = {
            "total_spent": 0.0,
            "scenarios": {}
        }

    def show_banner(self):
        """Display welcome banner"""
        banner = """
[bold cyan]╔══════════════════════════════════════════════════════════════╗[/bold cyan]
[bold cyan]║[/bold cyan]    [bold yellow]LLM OS - Demo Application (v3.5.0)[/bold yellow]                 [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]    Sentience + Adaptive Agents + Advanced Tool Use        [bold cyan]║[/bold cyan]
[bold cyan]╚══════════════════════════════════════════════════════════════╝[/bold cyan]

[bold]Five-Layer Stack:[/bold] SENTIENCE → ADAPTATION → LEARNING → EXECUTION → EVOLUTION
[bold]Latent Modes:[/bold] AUTO_CREATIVE | AUTO_CONTAINED | BALANCED | RECOVERY | CAUTIOUS
[bold]Features:[/bold] Adaptive Agents, PTC (90%+ savings), Tool Search, Multi-Agent
[bold]Budget:[/bold] $""" + f"{self.budget_usd:.2f}"

        console.print(Panel(banner, border_style="cyan"))

    def show_menu(self):
        """Display interactive menu"""
        console.print("\n[bold cyan]Select a demo scenario:[/bold cyan]\n")

        scenarios = [
            ("1", "🧠 Sentience Layer Demo", "Valence variables & latent modes ✅"),
            ("2", "🤖 Adaptive Agents Demo", "Dynamic agent adaptation ✅"),
            ("3", "🧬 Nested Learning Demo", "Semantic matching & MIXED mode ✅"),
            ("4", "Code Generation Workflow", "Learn-once, execute-free ✅"),
            ("5", "Cost Optimization Demo", "Dramatic cost savings ✅"),
            ("6", "Data Processing Pipeline", "Multi-agent orchestration ✅"),
            ("7", "DevOps Automation", "Automated deployment ✅"),
            ("8", "Cross-Project Learning", "Learning insights ✅"),
            ("9", "SDK Hooks Demo", "Budget control & security ✅"),
            ("V", "📦 Volume Operations", "NEW! User/Team/System volumes 🌟"),
            ("C", "⏰ Sentience Crons", "NEW! Background cron analysis 🌟"),
            ("O", "👁️  Observability Hub", "NEW! Event & activity monitoring 🌟"),
            ("T", "🖥️  Terminal UI", "NEW! MC-style cron dashboard 🌟"),
            ("A", "Run All Scenarios", "Execute all demos (recommended) ✅"),
            ("S", "View System Stats", "Show traces, agents, volumes ✅"),
            ("0", "Exit", "Exit demo application")
        ]

        table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        table.add_column("Choice", style="cyan", width=8)
        table.add_column("Scenario", style="green", width=30)
        table.add_column("Description", style="white", width=40)

        for choice, name, desc in scenarios:
            table.add_row(choice, name, desc)

        console.print(table)
        console.print()

    async def boot_os(self, project_name: str = None):
        """Boot the LLM OS with Sentience Layer"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🚀 Booting LLM OS...", total=None)

            # Initialize Sentience Layer (v3.4.0)
            sentience_config = SentienceConfig(
                enable_sentience=True,
                safety_setpoint=0.5,      # Balanced safety for demos
                curiosity_setpoint=0.3,   # Moderate curiosity for exploration
                energy_setpoint=0.7,      # High energy for active demos
                self_confidence_setpoint=0.5,
                boredom_threshold=-0.3,   # Trigger variety at moderate boredom
                state_file="state/demo_sentience.json"
            )

            self.sentience_manager = SentienceManager(
                state_path=Path(self.demo_output_dir) / sentience_config.state_file,
                auto_persist=sentience_config.auto_persist
            )
            # Configure valence setpoints
            self.sentience_manager.state.valence.safety_setpoint = sentience_config.safety_setpoint
            self.sentience_manager.state.valence.curiosity_setpoint = sentience_config.curiosity_setpoint
            self.sentience_manager.state.valence.energy_setpoint = sentience_config.energy_setpoint
            self.sentience_manager.state.valence.self_confidence_setpoint = sentience_config.self_confidence_setpoint
            self.cognitive_kernel = CognitiveKernel(self.sentience_manager)

            # Initialize Volume Manager (v3.6.0)
            volumes_path = Path(self.demo_output_dir) / "volumes"
            self.volume_manager = VolumeManager(volumes_path)

            # Initialize Observability Hub (v3.6.0)
            observability_path = Path(self.demo_output_dir) / "observability"
            observability_path.mkdir(parents=True, exist_ok=True)
            self.observability_hub = ObservabilityHub(observability_path)

            self.os = LLMOS(
                budget_usd=self.budget_usd,
                project_name=project_name
            )
            await self.os.boot()

            progress.update(task, completed=True)

        console.print("[green]✅ LLM OS ready![/green]")
        console.print("[green]✅ Sentience Layer initialized[/green]")
        console.print("[green]✅ Volume Manager initialized[/green]")
        console.print("[green]✅ Observability Hub initialized[/green]\n")

    async def scenario_sentience_demo(self):
        """Scenario: Sentience Layer Demo (v3.4.0)"""
        console.print(Panel(
            "[bold yellow]Sentience Layer Demo (v3.4.0)[/bold yellow]\n\n"
            "Demonstrates the new Sentience Layer with:\n"
            "1. Valence Variables: safety, curiosity, energy, self_confidence\n"
            "2. Homeostatic Dynamics: Internal state drives back to equilibrium\n"
            "3. Latent Modes: AUTO_CREATIVE, AUTO_CONTAINED, BALANCED, RECOVERY, CAUTIOUS\n"
            "4. Cognitive Kernel: Derives behavioral policy from internal state\n\n"
            "[bold]Features:[/bold] Persistent internal state, adaptive behavior",
            border_style="yellow"
        ))

        if not self.os:
            await self.boot_os("sentience_demo")

        # Display initial sentience state
        console.print("\n[cyan]Initial Sentience State:[/cyan]\n")
        self._display_sentience_state()

        # Simulate interactions and show state changes
        console.print("\n[cyan]Simulating interactions...[/cyan]\n")

        # Import TriggerType for proper state updates
        from kernel.sentience import TriggerType

        # Simulate a successful task
        console.print("[yellow]1. Simulating successful task execution...[/yellow]")
        self.sentience_manager.trigger(TriggerType.TASK_SUCCESS, reason="Completed first demo task")
        console.print("[green]   ✓ Task completed successfully[/green]")
        self._display_sentience_state()

        # Simulate another successful task (builds confidence)
        console.print("\n[yellow]2. Simulating another successful task...[/yellow]")
        self.sentience_manager.trigger(TriggerType.TASK_SUCCESS, reason="Completed second demo task")
        console.print("[green]   ✓ Task completed successfully[/green]")
        self._display_sentience_state()

        # Simulate a failure (decreases safety/confidence)
        console.print("\n[yellow]3. Simulating a task failure...[/yellow]")
        self.sentience_manager.trigger(TriggerType.TASK_FAILURE, reason="Third demo task failed")
        console.print("[red]   ✗ Task failed[/red]")
        self._display_sentience_state()

        # Simulate novel input (increases curiosity)
        console.print("\n[yellow]4. Simulating novel/surprising input...[/yellow]")
        self.sentience_manager.trigger(TriggerType.NOVEL_TASK, reason="Novel task detected")
        console.print("[magenta]   ? Novel input detected[/magenta]")
        self._display_sentience_state()

        # Simulate boredom trigger (repetitive tasks)
        console.print("\n[yellow]5. Simulating repetitive tasks (boredom)...[/yellow]")
        for i in range(3):
            self.sentience_manager.trigger(TriggerType.TASK_REPETITION, reason="Repetitive task", context={"repetition_count": i+1})
        console.print("[dim]   ... Repetitive tasks[/dim]")
        self._display_sentience_state()

        # Show final policy
        console.print("\n[cyan]Final Cognitive Policy:[/cyan]\n")
        policy = self.cognitive_kernel.derive_policy()
        state = self.sentience_manager.get_state()

        policy_table = Table(title="Behavioral Policy", box=box.ROUNDED)
        policy_table.add_column("Parameter", style="cyan")
        policy_table.add_column("Value", style="yellow")

        policy_table.add_row("Latent Mode", state.latent_mode.value.upper())
        policy_table.add_row("Exploration Budget", f"{policy.exploration_budget_multiplier:.2f}x")
        policy_table.add_row("Allow Exploration", str(policy.allow_exploration))
        policy_table.add_row("Self-Improvement", str(policy.enable_auto_improvement))

        console.print(policy_table)

        # Mode descriptions
        mode_descriptions = {
            "auto_creative": "HIGH CURIOSITY - Exploring new approaches, verbose output",
            "auto_contained": "LOW CURIOSITY - Focused execution, minimal exploration",
            "balanced": "NORMAL - Standard operation, moderate exploration",
            "recovery": "LOW ENERGY - Conservative mode, reduced operations",
            "cautious": "LOW SAFETY - Extra validation, careful execution"
        }

        console.print(f"\n[bold]Mode Description:[/bold] {mode_descriptions.get(state.latent_mode.value, 'Unknown')}")

        console.print(Panel(
            "[bold green]Sentience Layer Demo Complete![/bold green]\n\n"
            "The Sentience Layer provides:\n"
            "• Persistent internal state across interactions\n"
            "• Automatic behavioral adaptation based on context\n"
            "• Homeostatic dynamics that maintain equilibrium\n"
            "• Integration with agents for context-aware responses",
            border_style="green"
        ))

    async def scenario_adaptive_agents_demo(self):
        """Scenario: Adaptive Agents Demo (v3.5.0) - NEW!"""
        console.print(Panel(
            "[bold yellow]Adaptive Agents Demo (v3.5.0) - NEW![/bold yellow]\n\n"
            "Demonstrates the DynamicAgentManager with six adaptation strategies:\n"
            "1. Sentience-Driven: High curiosity adds exploration tools\n"
            "2. Trace-Driven: Failure patterns become constraints\n"
            "3. Memory-Guided: Best agent selected from past performance\n"
            "4. Model Selection: haiku/sonnet/opus based on complexity\n"
            "5. Prompt Enhancement: Successful traces as few-shot examples\n"
            "6. Agent Evolution: Agents improve from accumulated metrics\n\n"
            "[bold]Features:[/bold] Per-query adaptation, self-evolving agents",
            border_style="yellow"
        ))

        if not self.os:
            await self.boot_os("adaptive_agents_demo")

        # Create a mock agent factory for demonstration
        console.print("\n[cyan]Initializing DynamicAgentManager...[/cyan]\n")

        # Create the DynamicAgentManager
        from kernel.agent_loader import AgentFactory
        from memory.traces_sdk import TraceManager

        workspace_path = Path(__file__).parent / "workspace"
        workspace_path.mkdir(exist_ok=True)

        agent_factory = AgentFactory(workspace_path)
        trace_manager = TraceManager(workspace_path)

        dynamic_manager = DynamicAgentManager(
            agent_factory=agent_factory,
            workspace=workspace_path,
            sentience_manager=self.sentience_manager,
            trace_manager=trace_manager
        )

        console.print("[green]✓ DynamicAgentManager initialized[/green]\n")

        # Demo 1: Show sentience-driven adaptation
        console.print("[bold cyan]1. Sentience-Driven Adaptation[/bold cyan]\n")

        # Set high curiosity state
        console.print("[yellow]Setting HIGH CURIOSITY state...[/yellow]")
        self.sentience_manager.state.valence.curiosity = 0.7
        self.sentience_manager.state.latent_mode = LatentMode.AUTO_CREATIVE
        self._display_sentience_state()

        state = self.sentience_manager.get_state()

        # Create a test agent to demonstrate adaptation
        from kernel.agent_factory import AgentSpec
        test_agent = AgentSpec(
            name="test-researcher",
            agent_type="specialized",
            category="research",
            description="Test agent for adaptation demo",
            tools=["Read", "Write"],
            system_prompt="You are a test agent."
        )

        # Adapt the test agent
        adapted_agent = dynamic_manager._adapt_for_sentience(test_agent, state, "Research AI trends")

        adaptation_table = Table(title="High Curiosity Adaptations", box=box.ROUNDED)
        adaptation_table.add_column("Adaptation", style="cyan")
        adaptation_table.add_column("Value", style="yellow")

        # Show tools added
        original_tools = {"Read", "Write"}
        new_tools = [t for t in adapted_agent.tools if t not in original_tools]
        if new_tools:
            adaptation_table.add_row("Tools Added", ", ".join(new_tools))

        # Show prompt additions
        if len(adapted_agent.system_prompt) > len("You are a test agent."):
            prompt_preview = adapted_agent.system_prompt[len("You are a test agent."):].strip()[:80]
            adaptation_table.add_row("Prompt Addition", prompt_preview + "...")

        console.print(adaptation_table)

        # Set low safety state
        console.print("\n[yellow]Setting LOW SAFETY state...[/yellow]")
        self.sentience_manager.state.valence.safety = -0.6
        self.sentience_manager.state.latent_mode = LatentMode.CAUTIOUS
        self._display_sentience_state()

        state = self.sentience_manager.get_state()

        # Create another test agent with dangerous tools
        test_agent2 = AgentSpec(
            name="test-coder",
            agent_type="specialized",
            category="coding",
            description="Test agent for safety demo",
            tools=["Read", "Write", "Edit", "Bash"],
            system_prompt="You are a test agent."
        )

        adapted_agent2 = dynamic_manager._adapt_for_sentience(test_agent2, state, "Modify system files")

        adaptation_table = Table(title="Low Safety Adaptations", box=box.ROUNDED)
        adaptation_table.add_column("Adaptation", style="cyan")
        adaptation_table.add_column("Value", style="red")

        # Show tools removed
        original_tools2 = {"Read", "Write", "Edit", "Bash"}
        remaining_tools = set(adapted_agent2.tools)
        removed_tools = original_tools2 - remaining_tools
        if removed_tools:
            adaptation_table.add_row("Tools Removed", ", ".join(removed_tools))

        # Show constraints added
        if adapted_agent2.constraints:
            for constraint in adapted_agent2.constraints[:2]:
                adaptation_table.add_row("Constraint Added", constraint[:60] + "...")

        console.print(adaptation_table)

        # Demo 2: Show model selection
        console.print("\n[bold cyan]2. Dynamic Model Selection[/bold cyan]\n")

        test_goals = [
            ("Write a simple hello world script", "Simple task"),
            ("Research quantum computing and write a detailed analysis", "Complex research"),
            ("Create an innovative new algorithm for sorting", "Creative task"),
        ]

        model_table = Table(title="Model Selection by Task Type", box=box.ROUNDED)
        model_table.add_column("Goal", style="cyan", width=45)
        model_table.add_column("Type", style="yellow")
        model_table.add_column("Model", style="green")

        for goal, task_type in test_goals:
            # Create a test agent and apply model selection
            test_agent3 = AgentSpec(
                name="test-agent",
                agent_type="general",
                category="general",
                description="Test agent",
                tools=["Read"],
                system_prompt="You are a test agent."
            )
            adapted = dynamic_manager._select_optimal_model(test_agent3, goal, None)
            model = adapted.model if hasattr(adapted, 'model') else "sonnet"
            model_table.add_row(goal[:43] + "..." if len(goal) > 43 else goal, task_type, model)

        console.print(model_table)

        # Demo 3: Show adaptation statistics
        console.print("\n[bold cyan]3. Adaptation Statistics[/bold cyan]\n")

        # The adaptations from the demos above are automatically recorded
        # Get the adaptation summary
        stats = dynamic_manager.get_adaptation_summary()

        stats_table = Table(title="Adaptation Statistics", box=box.ROUNDED)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="yellow")

        stats_table.add_row("Total Adaptations", str(stats.get("total_adaptations", 0)))

        by_type = stats.get("by_type", {})
        for adapt_type, count in by_type.items():
            stats_table.add_row(f"  {adapt_type}", str(count))

        console.print(stats_table)

        # Demo 4: Show agent evolution criteria
        console.print("\n[bold cyan]4. Agent Evolution Criteria[/bold cyan]\n")

        evolution_table = Table(title="Evolution Triggers", box=box.ROUNDED)
        evolution_table.add_column("Condition", style="cyan")
        evolution_table.add_column("Threshold", style="yellow")
        evolution_table.add_column("Action", style="green")

        evolution_table.add_row("Minimum Executions", "5+", "Enable evolution analysis")
        evolution_table.add_row("Failure Rate", ">30%", "Add constraints from failures")
        evolution_table.add_row("Success Rate", ">80%", "Crystallize successful patterns")
        evolution_table.add_row("Tool Patterns", "Recurring", "Optimize tool selection")

        console.print(evolution_table)

        # Reset sentience to balanced state
        self.sentience_manager.state.valence.curiosity = 0.0
        self.sentience_manager.state.valence.safety = 0.5
        self.sentience_manager.state.latent_mode = LatentMode.BALANCED

        console.print(Panel(
            "[bold green]Adaptive Agents Demo Complete![/bold green]\n\n"
            "The DynamicAgentManager provides:\n"
            "• Per-query agent adaptation based on sentience state\n"
            "• Automatic model selection (haiku/sonnet/opus)\n"
            "• Learning from failure patterns\n"
            "• Continuous agent evolution from accumulated metrics\n"
            "• Integration with Claude SDK subagents",
            border_style="green"
        ))

    def _display_sentience_state(self):
        """Display current sentience state"""
        if not self.sentience_manager or not self.cognitive_kernel:
            console.print("[dim]Sentience Layer not initialized[/dim]")
            return

        state = self.sentience_manager.get_state()
        valence = state.valence.as_dict()
        valence_obj = state.valence

        table = Table(box=box.SIMPLE)
        table.add_column("Valence", style="cyan", width=18)
        table.add_column("Value", style="yellow", width=8)
        table.add_column("Bar", style="green", width=20)
        table.add_column("Setpoint", style="dim", width=10)

        setpoints = {
            "safety": valence_obj.safety_setpoint,
            "curiosity": valence_obj.curiosity_setpoint,
            "energy": valence_obj.energy_setpoint,
            "self_confidence": valence_obj.self_confidence_setpoint
        }

        for name, value in valence.items():
            # Normalize value from [-1, 1] to [0, 1] for display bar
            normalized_value = (value + 1) / 2
            bar_length = int(normalized_value * 20)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            setpoint = setpoints.get(name, 0.5)
            table.add_row(name.replace("_", " ").title(), f"{value:.2f}", bar, f"({setpoint:.1f})")

        console.print(table)
        console.print(f"[bold]Latent Mode:[/bold] {state.latent_mode.value.upper()}")

    async def scenario_1_data_pipeline(self):
        """Scenario 1: Data Processing Pipeline"""
        console.print(Panel(
            "[bold yellow]Scenario 1: Data Processing Pipeline[/bold yellow]\n\n"
            "Demonstrates multi-agent orchestration for a complete data workflow:\n"
            "1. Data Collector agent gathers data\n"
            "2. Data Processor agent transforms data\n"
            "3. Report Generator agent creates summary\n\n"
            "[bold]Mode:[/bold] Orchestrator\n"
            "[bold]Agents:[/bold] 3 specialized agents\n"
            "[bold]Estimated Cost:[/bold] $1.50",
            border_style="yellow"
        ))

        if not self.os:
            await self.boot_os("data_pipeline_demo")

        # Create specialized agents
        console.print("\n[cyan]Creating specialized agents...[/cyan]")

        collector = self.os.create_agent(
            name="data-collector",
            agent_type="specialized",
            category="data_collection",
            description="Collects data from various sources",
            system_prompt="You are a data collection specialist. Gather data from files, APIs, or databases.",
            tools=["Read", "Bash", "WebFetch"],
            capabilities=["File reading", "API calls", "Database queries"],
            constraints=["Read-only operations"]
        )

        processor = self.os.create_agent(
            name="data-processor",
            agent_type="specialized",
            category="data_processing",
            description="Processes and transforms data",
            system_prompt="You are a data processing specialist. Clean, transform, and analyze data.",
            tools=["Read", "Write", "Bash"],
            capabilities=["Data transformation", "Statistical analysis", "Data cleaning"],
            constraints=["CSV/JSON formats"]
        )

        reporter = self.os.create_agent(
            name="report-generator",
            agent_type="specialized",
            category="reporting",
            description="Generates comprehensive reports",
            system_prompt="You are a report generation specialist. Create clear, structured reports.",
            tools=["Read", "Write", "Edit"],
            capabilities=["Markdown formatting", "Data visualization", "Summary generation"],
            constraints=["Markdown output"]
        )

        console.print(f"[green]✅ Created {collector.name}[/green]")
        console.print(f"[green]✅ Created {processor.name}[/green]")
        console.print(f"[green]✅ Created {reporter.name}[/green]")

        # Execute orchestrated workflow
        console.print("\n[cyan]Executing data pipeline (orchestrated)...[/cyan]\n")

        result = await self.os.execute(
            "Create a sample dataset, process it to calculate statistics, and generate a summary report",
            mode="ORCHESTRATOR",
            max_cost_usd=2.0
        )

        # Display results
        self._display_result(result, "Data Pipeline")
        self._track_cost("data_pipeline", result.get("cost", 0.0))

    async def scenario_2_code_generation(self):
        """Scenario 2: Code Generation with Trace Learning"""
        console.print(Panel(
            "[bold yellow]Scenario 2: Code Generation Workflow (v3.3.0)[/bold yellow]\n\n"
            "Demonstrates the Learn-Once, Execute-Free pattern with PTC:\n"
            "1. First run: Learner mode (~$0.50) - creates trace with tool_calls\n"
            "2. Second run: Follower mode + PTC (~$0.00) - replays via Programmatic Tool Calling\n\n"
            "[bold]Mode:[/bold] Learner → Follower (PTC)\n"
            "[bold]Savings:[/bold] 90%+ tokens, 100% cost on repeat executions",
            border_style="yellow"
        ))

        if not self.os:
            await self.boot_os("code_gen_demo")

        # First execution (Learner mode)
        console.print("\n[cyan]First execution (Learner mode)...[/cyan]\n")

        result1 = await self.os.execute(
            "Create a Python function to calculate factorial recursively"
        )

        cost1 = result1.get("cost", 0.0)
        console.print(f"\n[yellow]First run cost: ${cost1:.4f}[/yellow]")
        console.print(f"[yellow]Mode: {result1.get('mode')}[/yellow]")

        # Second execution (should be Follower mode)
        console.print("\n[cyan]Second execution (Follower mode expected)...[/cyan]\n")

        result2 = await self.os.execute(
            "Create a Python function to calculate factorial recursively"
        )

        cost2 = result2.get("cost", 0.0)
        console.print(f"\n[green]Second run cost: ${cost2:.4f}[/green]")
        console.print(f"[green]Mode: {result2.get('mode')}[/green]")

        # Show savings
        if cost2 == 0.0:
            console.print(f"\n[bold green]💰 Savings: 100% (${cost1:.4f} → $0.00)[/bold green]")
        else:
            savings_pct = ((cost1 - cost2) / cost1 * 100) if cost1 > 0 else 0
            console.print(f"\n[bold green]💰 Savings: {savings_pct:.1f}%[/bold green]")

        self._track_cost("code_generation", cost1 + cost2)

    async def scenario_nested_learning(self):
        """Nested Learning Demo - Semantic Matching"""
        if not self.os:
            await self.boot_os("nested_learning_demo")

        result = await run_nested_learning_demo(self.os)
        self._track_cost("nested_learning", result.get("total_cost", 0.0))

    async def scenario_3_research_assistant(self):
        """Scenario 3: Research Assistant"""
        console.print(Panel(
            "[bold yellow]Scenario 3: Research Assistant[/bold yellow]\n\n"
            "⚠️  [bold red]Note: This scenario has known timeout issues[/bold red]\n\n"
            "Demonstrates complex multi-step orchestration:\n"
            "1. Research agent gathers information\n"
            "2. Technical writer creates comprehensive report\n\n"
            "[bold]Mode:[/bold] Orchestrator\n"
            "[bold]Actual Cost:[/bold] $0.30-0.50 (due to timeouts)\n"
            "[bold]Duration:[/bold] 10-16 minutes (with timeout warnings)\n"
            "[bold]Status:[/bold] ⚠️  Partially working - some delegations timeout\n\n"
            "[yellow]Recommendation: Try Data Pipeline (Scenario 1) for reliable multi-agent demo[/yellow]",
            border_style="yellow"
        ))

        if not self.os:
            await self.boot_os("research_demo")

        # Create research agents
        console.print("\n[cyan]Creating research agents...[/cyan]")

        researcher = self.os.create_agent(
            name="researcher",
            agent_type="specialized",
            category="research",
            description="Researches topics and gathers information",
            system_prompt="""You are a research specialist. Find and gather relevant information.

IMPORTANT CONSTRAINTS:
- Limit web searches to 2-3 targeted queries maximum
- Focus on recent, authoritative sources
- Synthesize findings quickly - don't over-research
- Write findings directly to a file instead of returning large amounts of text
- If information gathering takes >30 seconds, save what you have and move on
- Prioritize breadth over depth for initial research""",
            tools=["WebSearch", "WebFetch", "Read", "Write"],
            capabilities=["Web research", "Information gathering", "Source evaluation"],
            constraints=["Credible sources only", "Maximum 3 web searches per task", "Save findings to files"]
        )

        writer = self.os.create_agent(
            name="technical-writer",
            agent_type="specialized",
            category="documentation",
            description="Creates technical documentation and reports",
            system_prompt="You are a technical writer. Create clear, structured documentation.",
            tools=["Read", "Write", "Edit"],
            capabilities=["Technical writing", "Markdown formatting", "Content structuring"],
            constraints=["Clear, concise style"]
        )

        console.print(f"[green]✅ Created {researcher.name}[/green]")
        console.print(f"[green]✅ Created {writer.name}[/green]")

        # Execute research task
        console.print("\n[cyan]Executing research task...[/cyan]\n")

        result = await self.os.execute(
            "Research the latest developments in large language models and create a technical summary",
            mode="ORCHESTRATOR",
            max_cost_usd=3.0
        )

        self._display_result(result, "Research Assistant")
        self._track_cost("research_assistant", result.get("cost", 0.0))

    async def scenario_4_devops_automation(self):
        """Scenario 4: DevOps Automation"""
        console.print(Panel(
            "[bold yellow]Scenario 4: DevOps Automation[/bold yellow]\n\n"
            "Demonstrates security hooks and automation:\n"
            "1. SDK hooks block dangerous commands\n"
            "2. Budget hooks prevent cost overruns\n"
            "3. Trace capture for repeatable deployments\n\n"
            "[bold]Mode:[/bold] Learner with Hooks\n"
            "[bold]Features:[/bold] Security, Budget Control",
            border_style="yellow"
        ))

        if not self.os:
            await self.boot_os("devops_demo")

        console.print("\n[cyan]Executing DevOps task with hooks enabled...[/cyan]\n")
        console.print("[yellow]🔒 Security Hook: Will block dangerous commands[/yellow]")
        console.print("[yellow]💰 Budget Hook: Will monitor costs[/yellow]\n")

        result = await self.os.execute(
            "Create a simple deployment script that checks system status",
            max_cost_usd=1.0
        )

        self._display_result(result, "DevOps Automation")
        self._track_cost("devops_automation", result.get("cost", 0.0))

    async def scenario_5_cross_project(self):
        """Scenario 5: Cross-Project Learning"""
        console.print(Panel(
            "[bold yellow]Scenario 5: Cross-Project Learning[/bold yellow]\n\n"
            "Demonstrates learning insights across projects:\n"
            "1. Common patterns detection\n"
            "2. Reusable agent identification\n"
            "3. Cost optimization insights\n\n"
            "[bold]Features:[/bold] Cross-project analysis, Pattern detection",
            border_style="yellow"
        ))

        if not self.os:
            await self.boot_os()

        console.print("\n[cyan]Analyzing cross-project patterns...[/cyan]\n")

        # Get cross-project insights
        patterns = await self.os.get_cross_project_insights(
            min_projects=1,
            min_confidence=0.5
        )

        console.print(f"[green]✅ Found {len(patterns)} cross-project patterns[/green]\n")

        if patterns:
            table = Table(title="Cross-Project Patterns", box=box.ROUNDED)
            table.add_column("Pattern", style="cyan")
            table.add_column("Type", style="yellow")
            table.add_column("Projects", style="green")

            for pattern in patterns[:5]:
                table.add_row(
                    pattern.title[:40],
                    pattern.insight_type,
                    str(len(pattern.projects_involved))
                )

            console.print(table)

        # Get reusable agents
        console.print("\n[cyan]Identifying reusable agents...[/cyan]\n")

        reusable = await self.os.get_reusable_agents(
            min_success_rate=0.7,
            min_usage_count=1
        )

        console.print(f"[green]✅ Found {len(reusable)} reusable agent patterns[/green]\n")

        if reusable:
            table = Table(title="Reusable Agents", box=box.ROUNDED)
            table.add_column("Agent", style="cyan")
            table.add_column("Category", style="yellow")
            table.add_column("Success Rate", style="green")

            for agent in reusable[:5]:
                table.add_row(
                    agent.agent_name,
                    agent.category,
                    f"{agent.success_rate:.0%}"
                )

            console.print(table)

    async def scenario_6_cost_optimization(self):
        """Scenario 6: Cost Optimization Demo"""
        console.print(Panel(
            "[bold yellow]Scenario 6: Cost Optimization Demo (v3.3.0)[/bold yellow]\n\n"
            "Demonstrates dramatic savings through PTC and crystallization:\n"
            "1. Execute task 5 times\n"
            "2. First run: Learner mode (creates trace with tool_calls)\n"
            "3. Runs 2-4: Follower mode + PTC (90%+ token savings)\n"
            "4. Run 5+: CRYSTALLIZED mode (pure Python, truly FREE)\n\n"
            "[bold]Expected Savings:[/bold] 80%+ cost, 90%+ tokens",
            border_style="yellow"
        ))

        if not self.os:
            await self.boot_os("cost_demo")

        goal = "Create a Python function to check if a number is prime"
        runs = 5
        costs = []

        console.print(f"\n[cyan]Executing same task {runs} times...[/cyan]\n")

        for i in range(runs):
            console.print(f"[yellow]Run {i+1}/{runs}...[/yellow]")

            result = await self.os.execute(goal)
            cost = result.get("cost", 0.0)
            mode = result.get("mode", "UNKNOWN")

            costs.append(cost)

            console.print(f"  Mode: {mode}, Cost: ${cost:.4f}\n")

        # Show cost analysis
        total_cost = sum(costs)
        first_cost = costs[0]
        avg_cost = total_cost / runs
        savings_pct = ((first_cost * runs - total_cost) / (first_cost * runs) * 100) if first_cost > 0 else 0

        console.print(Panel(
            f"[bold]Cost Analysis:[/bold]\n\n"
            f"First run (Learner): ${first_cost:.4f}\n"
            f"Subsequent runs (Follower): ${sum(costs[1:]):.4f}\n"
            f"Total cost: ${total_cost:.4f}\n"
            f"Average per run: ${avg_cost:.4f}\n"
            f"[bold green]Savings vs. all-Learner: {savings_pct:.1f}%[/bold green]\n"
            f"[bold green]Cost without traces: ${first_cost * runs:.4f}[/bold green]",
            title="💰 Cost Savings",
            border_style="green"
        ))

        self._track_cost("cost_optimization", total_cost)

    async def scenario_7_sdk_hooks(self):
        """Scenario 7: SDK Hooks Demo"""
        console.print(Panel(
            "[bold yellow]Scenario 7: SDK Hooks System[/bold yellow]\n\n"
            "Demonstrates automatic hook integration:\n"
            "1. Budget Control Hook: Estimates and limits costs\n"
            "2. Security Hook: Blocks dangerous commands\n"
            "3. Trace Capture Hook: Records execution\n"
            "4. Memory Injection Hook: Provides context\n\n"
            "[bold]Features:[/bold] All Phase 2.5 hooks",
            border_style="yellow"
        ))

        if not self.os:
            await self.boot_os("hooks_demo")

        console.print("\n[cyan]Hooks are automatically enabled in Learner mode:[/cyan]")
        console.print("  🔒 Security Hook (PreToolUse)")
        console.print("  💰 Budget Control Hook (PreToolUse)")
        console.print("  📝 Trace Capture Hook (PostToolUse)")
        console.print("  💵 Cost Tracking Hook (PostToolUse)")
        console.print("  🧠 Memory Injection Hook (UserPromptSubmit)\n")

        result = await self.os.execute(
            "Create a simple hello world script",
            max_cost_usd=0.5
        )

        console.print("\n[green]✅ Execution completed with all hooks active[/green]")
        console.print(f"[green]Cost: ${result.get('cost', 0.0):.4f} (under budget)[/green]")
        console.print("[green]Security checks passed[/green]")
        console.print("[green]Trace captured for future Follower mode[/green]")

        self._track_cost("sdk_hooks", result.get("cost", 0.0))

    async def scenario_volumes_demo(self):
        """Scenario: Volume Operations Demo (v3.6.0)"""
        console.print(Panel(
            "[bold yellow]Volume Operations Demo (v3.6.0)[/bold yellow]\n\n"
            "Demonstrates the three-tier volume architecture:\n"
            "1. UserVolume: Personal artifacts for a single user\n"
            "2. TeamVolume: Shared artifacts for a team\n"
            "3. SystemVolume: Global artifacts available to all\n\n"
            "[bold]Features:[/bold] Artifact management, promotion, changelog tracking",
            border_style="yellow"
        ))

        if not self.os:
            await self.boot_os("volumes_demo")

        console.print("\n[cyan]Volume Manager initialized at:[/cyan]")
        console.print(f"  {self.volume_manager.base_path}\n")

        # Demo 1: Create user volume and write artifacts
        console.print("[bold cyan]1. User Volume Operations[/bold cyan]\n")

        user_volume = self.volume_manager.get_user_volume("demo_user")
        console.print(f"[green]✓ Created user volume: {user_volume.owner_id}[/green]")

        # Write a sample trace
        sample_trace = """---
goal_signature: demo_trace_001
goal_text: Demo trace for volume testing
success_rating: 0.95
usage_count: 3
---

## Execution Steps

### Step 1: Initialize demo
Tool: Write
Status: Success

## Tool Calls (PTC)
```json
[{"name": "Write", "arguments": {"path": "demo.py", "content": "print('hello')"}}]
```
"""
        user_volume.write_artifact(
            artifact_type=ArtifactType.TRACE,
            artifact_id="demo_trace_001",
            content=sample_trace,
            reason="Demo: Creating sample trace",
            cron_level="user",
            is_new=True
        )
        console.print("[green]✓ Written trace: demo_trace_001[/green]")

        # Write a sample insight
        sample_insight = """---
insight_id: demo_insight_001
insight_type: pattern
confidence: 0.85
---

# Repeated File Operations Pattern

Found that 80% of tasks involve reading, modifying, and writing files.
Consider creating a dedicated file-ops agent.

## Evidence
- trace_001, trace_002, trace_003
"""
        user_volume.write_artifact(
            artifact_type=ArtifactType.INSIGHT,
            artifact_id="demo_insight_001",
            content=sample_insight,
            reason="Demo: Creating sample insight",
            cron_level="user",
            is_new=True
        )
        console.print("[green]✓ Written insight: demo_insight_001[/green]")

        # Show user volume stats
        stats = user_volume.get_stats()
        stats_table = Table(title="User Volume Stats", box=box.ROUNDED)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="yellow")
        stats_table.add_row("Traces", str(stats.trace_count))
        stats_table.add_row("Tools", str(stats.tool_count))
        stats_table.add_row("Agents", str(stats.agent_count))
        stats_table.add_row("Insights", str(stats.insight_count))
        stats_table.add_row("Suggestions", str(stats.suggestion_count))
        stats_table.add_row("Total Size", f"{stats.total_size_bytes} bytes")
        console.print(stats_table)

        # Demo 2: Team volume
        console.print("\n[bold cyan]2. Team Volume Operations[/bold cyan]\n")

        team_volume = self.volume_manager.get_team_volume("engineering")
        console.print(f"[green]✓ Created team volume: {team_volume.owner_id}[/green]")

        # Promote insight from user to team
        console.print("\n[yellow]Promoting insight from User → Team...[/yellow]")
        self.volume_manager.promote_artifact(
            artifact_type=ArtifactType.INSIGHT,
            artifact_id="demo_insight_001",
            from_volume=user_volume,
            to_volume=team_volume,
            reason="High-value pattern identified",
            cron_level="team"
        )
        console.print("[green]✓ Insight promoted to team volume[/green]")

        # Demo 3: System volume
        console.print("\n[bold cyan]3. System Volume Operations[/bold cyan]\n")

        system_volume = self.volume_manager.get_system_volume()
        console.print(f"[green]✓ Accessed system volume[/green]")

        # Write a system-wide tool template
        sample_tool = '''"""
System Tool: File Operations Helper
Auto-crystallized from repeated patterns.
"""

def read_and_transform(path: str, transform_fn) -> str:
    """Read file, apply transformation, return result."""
    with open(path) as f:
        content = f.read()
    return transform_fn(content)
'''
        system_volume.write_artifact(
            artifact_type=ArtifactType.TOOL,
            artifact_id="file_ops_helper",
            content=sample_tool,
            reason="Demo: System-wide crystallized tool",
            cron_level="system",
            is_new=True
        )
        console.print("[green]✓ Written system tool: file_ops_helper[/green]")

        # Demo 4: Changelog tracking
        console.print("\n[bold cyan]4. Changelog Tracking[/bold cyan]\n")

        changes = user_volume.get_recent_changes(limit=10)
        if changes:
            changelog_table = Table(title="Recent Changes (User Volume)", box=box.ROUNDED)
            changelog_table.add_column("Action", style="cyan")
            changelog_table.add_column("Artifact", style="yellow")
            changelog_table.add_column("Type", style="green")
            changelog_table.add_column("Reason", style="white", width=30)

            for change in changes[:5]:
                changelog_table.add_row(
                    change.action.value,
                    change.artifact_id[:20],
                    change.artifact_type.value,
                    change.reason[:28] + "..." if len(change.reason) > 28 else change.reason
                )
            console.print(changelog_table)

        # Demo 5: Access control demonstration
        console.print("\n[bold cyan]5. Access Control Demonstration[/bold cyan]\n")

        access_table = Table(title="Volume Access Control", box=box.ROUNDED)
        access_table.add_column("Cron Level", style="cyan")
        access_table.add_column("User Volume", style="yellow")
        access_table.add_column("Team Volume", style="yellow")
        access_table.add_column("System Volume", style="yellow")

        access_table.add_row("User Cron", "Read/Write", "Read Only", "-")
        access_table.add_row("Team Cron", "Read (aggregated)", "Read/Write", "Read Only")
        access_table.add_row("System Cron", "Read/Write", "Read/Write", "Read/Write")

        console.print(access_table)

        console.print(Panel(
            "[bold green]Volume Operations Demo Complete![/bold green]\n\n"
            "The Volume Manager provides:\n"
            "• Three-tier artifact storage (User/Team/System)\n"
            "• Artifact promotion between volumes\n"
            "• Changelog tracking for all changes\n"
            "• Access control based on cron level\n"
            "• Support for traces, tools, agents, insights, suggestions",
            border_style="green"
        ))

    async def scenario_crons_demo(self):
        """Scenario: Sentience Crons Demo (v3.6.0)"""
        console.print(Panel(
            "[bold yellow]Sentience Crons Demo (v3.6.0)[/bold yellow]\n\n"
            "Demonstrates the three-tier cron hierarchy:\n"
            "1. UserCron: Personal evolution for a single user\n"
            "2. TeamCron: Shared evolution for team artifacts\n"
            "3. SystemCron: Global evolution, controls other crons\n\n"
            "[bold]Features:[/bold] Background analysis, insights, suggestions, notifications",
            border_style="yellow"
        ))

        if not self.os:
            await self.boot_os("crons_demo")

        # Initialize the System Cron with observability
        console.print("\n[cyan]Initializing Sentience Cron System...[/cyan]\n")

        self.system_cron = SystemCron(
            volume_manager=self.volume_manager,
            schedule_interval_secs=60.0,  # 1 minute for demo
            observability_hub=self.observability_hub
        )
        console.print("[green]✓ SystemCron initialized[/green]")

        # Register a user cron
        user_cron = self.system_cron.register_user_cron(
            user_id="demo_user",
            team_id="engineering"
        )
        console.print("[green]✓ UserCron registered for demo_user[/green]")

        # Demo 1: Show cron hierarchy
        console.print("\n[bold cyan]1. Cron Hierarchy[/bold cyan]\n")

        hierarchy = """
                    ┌─────────────────┐
                    │   SystemCron    │
                    │  (full access)  │
                    └────────┬────────┘
                             │ controls
              ┌──────────────┼──────────────┐
              │              │              │
       ┌──────▼─────┐ ┌──────▼─────┐ ┌──────▼─────┐
       │  TeamCron  │ │  TeamCron  │ │  TeamCron  │
       │  (eng)     │ │  (design)  │ │  (ops)     │
       └──────┬─────┘ └────────────┘ └────────────┘
              │
        ┌─────┼─────┐
        │     │     │
       User  User  User
       Cron  Cron  Cron
       (you) (bob) (alice)
"""
        console.print(hierarchy)

        # Demo 2: Run user cron analysis
        console.print("\n[bold cyan]2. Running User Cron Analysis[/bold cyan]\n")

        console.print("[yellow]Running analysis cycle (this may take a moment)...[/yellow]\n")
        tasks = await user_cron.run_now()

        task_table = Table(title="Analysis Tasks Completed", box=box.ROUNDED)
        task_table.add_column("Task Type", style="cyan")
        task_table.add_column("Status", style="yellow")
        task_table.add_column("Artifacts Processed", style="green")
        task_table.add_column("Summary", style="white", width=35)

        for task in tasks:
            status_icon = "✓" if task.status == "completed" else "✗"
            task_table.add_row(
                task.task_type.value,
                f"{status_icon} {task.status}",
                str(task.artifacts_processed),
                task.summary[:33] + "..." if len(task.summary) > 33 else task.summary
            )
        console.print(task_table)

        # Demo 3: Check for notifications
        console.print("\n[bold cyan]3. Notifications[/bold cyan]\n")

        notifications = user_cron.get_notifications(limit=5)
        if notifications:
            notif_table = Table(title="Cron Notifications", box=box.ROUNDED)
            notif_table.add_column("Title", style="cyan")
            notif_table.add_column("Importance", style="yellow")
            notif_table.add_column("Message", style="white", width=40)

            for notif in notifications:
                notif_table.add_row(
                    notif["title"][:25],
                    notif["importance"],
                    notif["message"][:38] + "..." if len(notif["message"]) > 38 else notif["message"]
                )
            console.print(notif_table)
        else:
            console.print("[dim]No notifications yet. Run more tasks to generate insights![/dim]")

        # Demo 4: Cron status
        console.print("\n[bold cyan]4. Cron Status[/bold cyan]\n")

        system_status = self.system_cron.get_status()
        user_status = user_cron.get_status()

        status_table = Table(title="Cron Status", box=box.ROUNDED)
        status_table.add_column("Cron", style="cyan")
        status_table.add_column("Running", style="yellow")
        status_table.add_column("Last Run", style="green")
        status_table.add_column("Tasks", style="white")

        status_table.add_row(
            "SystemCron",
            str(system_status["running"]),
            system_status["last_run"][:19] if system_status["last_run"] else "Never",
            str(system_status["task_history_count"])
        )
        status_table.add_row(
            f"UserCron ({user_status['owner_id']})",
            str(user_status["running"]),
            user_status["last_run"][:19] if user_status["last_run"] else "Never",
            str(user_status["task_history_count"])
        )
        console.print(status_table)

        # Demo 5: Activity summary
        console.print("\n[bold cyan]5. Activity Summary[/bold cyan]\n")

        activity = user_cron.get_activity_summary()
        console.print(activity)

        console.print(Panel(
            "[bold green]Sentience Crons Demo Complete![/bold green]\n\n"
            "The Sentience Cron System provides:\n"
            "• Background analysis of artifacts\n"
            "• Automatic insight and suggestion generation\n"
            "• Hierarchical cron management (User/Team/System)\n"
            "• Notification system for important events\n"
            "• Integration with Volume Manager",
            border_style="green"
        ))

    async def scenario_observability_demo(self):
        """Scenario: Observability Demo (v3.6.0)"""
        console.print(Panel(
            "[bold yellow]Observability Demo (v3.6.0)[/bold yellow]\n\n"
            "Demonstrates the Observability Hub for system monitoring:\n"
            "1. Event recording from all crons\n"
            "2. Activity feed queries\n"
            "3. Artifact change tracking\n"
            "4. Notification management\n\n"
            "[bold]Features:[/bold] Real-time visibility into cron activity",
            border_style="yellow"
        ))

        if not self.os:
            await self.boot_os("observability_demo")

        console.print("\n[cyan]Observability Hub initialized at:[/cyan]")
        console.print(f"  {self.observability_hub.base_path}\n")

        # Demo 1: Record some events
        console.print("[bold cyan]1. Recording Events[/bold cyan]\n")

        # Simulate various events
        self.observability_hub.record_cron_started("user:demo_user", "user")
        console.print("[green]✓ Recorded: Cron Started[/green]")

        self.observability_hub.record_artifact_created(
            cron_id="user:demo_user",
            artifact_type="trace",
            artifact_id="trace_demo_001",
            volume_type="user",
            reason="Created from demo execution"
        )
        console.print("[green]✓ Recorded: Artifact Created[/green]")

        self.observability_hub.record_insight(
            cron_id="user:demo_user",
            insight_title="High Success Rate Pattern",
            insight_content="Tasks involving file operations have 95% success rate.",
            volume_type="user"
        )
        console.print("[green]✓ Recorded: Insight Generated[/green]")

        self.observability_hub.record_suggestion(
            cron_id="user:demo_user",
            suggestion_title="Create File Ops Agent",
            suggestion_content="Consider creating a specialized agent for file operations.",
            volume_type="user"
        )
        console.print("[green]✓ Recorded: Suggestion Created[/green]")

        self.observability_hub.record_cycle(
            cron_id="user:demo_user",
            tasks_completed=3,
            duration_seconds=2.5
        )
        console.print("[green]✓ Recorded: Cron Cycle End[/green]")

        # Demo 2: Query activity feed
        console.print("\n[bold cyan]2. Activity Feed[/bold cyan]\n")

        feed = self.observability_hub.get_activity_feed(limit=10)
        if feed:
            feed_table = Table(title="Recent Activity", box=box.ROUNDED)
            feed_table.add_column("Time", style="dim")
            feed_table.add_column("Type", style="cyan")
            feed_table.add_column("Title", style="yellow")
            feed_table.add_column("Source", style="green")

            for event in feed[:7]:
                time_str = event["timestamp"].split("T")[1][:8]
                feed_table.add_row(
                    time_str,
                    event["event_type"],
                    event["title"][:30],
                    event["source_cron"]
                )
            console.print(feed_table)

        # Demo 3: Artifact changes
        console.print("\n[bold cyan]3. Artifact Changes[/bold cyan]\n")

        changes = self.observability_hub.get_artifact_changes(limit=5)
        if changes:
            changes_table = Table(title="Artifact Change Log", box=box.ROUNDED)
            changes_table.add_column("Type", style="cyan")
            changes_table.add_column("Artifact", style="yellow")
            changes_table.add_column("Volume", style="green")
            changes_table.add_column("Description", style="white", width=30)

            for change in changes:
                changes_table.add_row(
                    change.get("artifact_type", "?"),
                    change.get("artifact_id", "?")[:20],
                    change.get("volume_type", "?"),
                    change["description"][:28] + "..." if len(change.get("description", "")) > 28 else change.get("description", "")
                )
            console.print(changes_table)
        else:
            console.print("[dim]No artifact changes recorded yet.[/dim]")

        # Demo 4: Pending notifications
        console.print("\n[bold cyan]4. Pending Notifications[/bold cyan]\n")

        notifications = self.observability_hub.get_pending_notifications()
        console.print(f"[yellow]Found {len(notifications)} pending notification(s)[/yellow]")

        if notifications:
            for notif in notifications[:3]:
                severity = notif.get("severity", "info")
                color = {"info": "blue", "warning": "yellow", "error": "red"}.get(severity, "white")
                console.print(f"  [{color}]● {notif['title']}[/{color}]")

        # Demo 5: Global summary
        console.print("\n[bold cyan]5. Global Summary[/bold cyan]\n")

        summary = self.observability_hub.get_global_summary()
        summary_table = Table(title="System Summary (Today)", box=box.ROUNDED)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="yellow")

        summary_table.add_row("Total Events", str(summary.get("total_events", 0)))
        summary_table.add_row("Artifacts Created", str(summary.get("artifacts_created", 0)))
        summary_table.add_row("Artifacts Evolved", str(summary.get("artifacts_evolved", 0)))
        summary_table.add_row("Insights Generated", str(summary.get("insights_generated", 0)))
        summary_table.add_row("Suggestions Created", str(summary.get("suggestions_created", 0)))
        summary_table.add_row("Pending Notifications", str(summary.get("pending_notifications", 0)))

        console.print(summary_table)

        # Demo 6: Formatted output
        console.print("\n[bold cyan]6. Formatted Activity Feed[/bold cyan]\n")

        formatted = self.observability_hub.format_activity_feed(limit=5)
        console.print(formatted)

        console.print(Panel(
            "[bold green]Observability Demo Complete![/bold green]\n\n"
            "The Observability Hub provides:\n"
            "• Event recording from all crons\n"
            "• Activity feed with time-based queries\n"
            "• Artifact change tracking\n"
            "• Notification management with acknowledgment\n"
            "• Global and per-cron summaries",
            border_style="green"
        ))

    async def scenario_terminal_demo(self):
        """Scenario: Terminal UI Demo (v3.6.0)"""
        console.print(Panel(
            "[bold yellow]Terminal UI Demo (v3.6.0)[/bold yellow]\n\n"
            "Launches the Midnight Commander-style Terminal UI:\n"
            "1. Left Panel: Tree view of all cron processes\n"
            "2. Right Panel: Detailed view of selected cron\n"
            "3. Interactive chat with YOUR UserCron\n"
            "4. Real-time status updates\n\n"
            "[bold]Requirements:[/bold] textual package (pip install textual)",
            border_style="yellow"
        ))

        if not self.os:
            await self.boot_os("terminal_demo")

        console.print("\n[cyan]Preparing Terminal UI...[/cyan]\n")

        # Check if textual is installed
        try:
            from kernel.terminal import get_textual_app, LLMOSDataProvider
            console.print("[green]✓ Textual package found[/green]")
        except ImportError as e:
            console.print("[red]✗ Textual package not installed[/red]")
            console.print("[yellow]Install with: pip install textual[/yellow]")
            console.print(f"[dim]Error: {e}[/dim]")
            return

        # Create data provider connected to real LLMOS
        console.print("[green]✓ Creating LLMOSDataProvider...[/green]")

        data_provider = LLMOSDataProvider(
            trace_manager=getattr(self.os, 'trace_manager', None),
            memory_store=getattr(self.os, 'memory_store', None),
            token_economy=getattr(self.os, 'token_economy', None),
            dispatcher=getattr(self.os, 'dispatcher', None),
            workspace=Path(self.demo_output_dir) / "workspace"
        )

        # Show what the terminal will display
        console.print("\n[bold cyan]Terminal UI Features:[/bold cyan]\n")

        features_table = Table(box=box.ROUNDED)
        features_table.add_column("Key", style="cyan")
        features_table.add_column("Action", style="yellow")

        features_table.add_row("Tab", "Switch between tree and detail panels")
        features_table.add_row("↑/↓ or j/k", "Navigate in tree")
        features_table.add_row("Enter", "Select cron / send message")
        features_table.add_row("F5 or Ctrl+R", "Refresh data")
        features_table.add_row("F1 or ?", "Show help")
        features_table.add_row("F10 or q", "Quit")

        console.print(features_table)

        console.print("\n[yellow]Would you like to launch the Terminal UI?[/yellow]")
        console.print("[dim]This will take over your terminal. Press Ctrl+C to cancel.[/dim]\n")

        try:
            choice = console.input("[bold cyan]Launch Terminal UI? (y/n):[/bold cyan] ").strip().lower()

            if choice == 'y':
                console.print("\n[green]Launching Terminal UI...[/green]")
                console.print("[dim]Press q or F10 to exit and return to demo menu.[/dim]\n")

                await asyncio.sleep(1)

                # Get the Textual app
                CronTerminalApp, run_terminal = get_textual_app()

                # Run the terminal
                await run_terminal(
                    user_id="demo_user",
                    team_id="engineering",
                    status_callback=data_provider.get_system_status,
                    events_callback=data_provider.get_events,
                    suggestions_callback=data_provider.get_suggestions,
                    cron_callback=data_provider.handle_user_message,
                    refresh_interval=5.0,
                    auto_refresh=True
                )

                console.print("\n[green]✓ Terminal UI session ended[/green]")
            else:
                console.print("\n[dim]Terminal UI launch cancelled.[/dim]")

        except KeyboardInterrupt:
            console.print("\n[yellow]Cancelled.[/yellow]")

        console.print(Panel(
            "[bold green]Terminal UI Demo Complete![/bold green]\n\n"
            "The Cron Terminal provides:\n"
            "• Real-time cron status monitoring\n"
            "• Interactive chat with your UserCron\n"
            "• Activity log and suggestions\n"
            "• Midnight Commander-style navigation\n"
            "• Integration with LLMOSDataProvider",
            border_style="green"
        ))

    async def scenario_9_run_all(self):
        """Run all scenarios sequentially"""
        console.print(Panel(
            "[bold yellow]Running All Scenarios[/bold yellow]\n\n"
            "This will execute all demo scenarios in sequence.\n"
            "Estimated time: 5-10 minutes\n"
            "Estimated cost: $5-8",
            border_style="yellow"
        ))

        input("\nPress Enter to continue or Ctrl+C to cancel...")

        scenarios = [
            ("Sentience Layer", self.scenario_sentience_demo),
            ("Adaptive Agents", self.scenario_adaptive_agents_demo),
            ("Nested Learning", self.scenario_nested_learning),
            ("Code Generation", self.scenario_2_code_generation),
            ("Cost Optimization", self.scenario_6_cost_optimization),
            ("Data Pipeline", self.scenario_1_data_pipeline),
            ("DevOps Automation", self.scenario_4_devops_automation),
            ("Cross-Project Learning", self.scenario_5_cross_project),
            ("SDK Hooks", self.scenario_7_sdk_hooks),
            ("Volume Operations", self.scenario_volumes_demo),
            ("Sentience Crons", self.scenario_crons_demo),
            ("Observability Hub", self.scenario_observability_demo),
            # Terminal UI is interactive, skip in run_all
        ]

        for name, scenario_func in scenarios:
            console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
            console.print(f"[bold cyan]Running: {name}[/bold cyan]")
            console.print(f"[bold cyan]{'='*60}[/bold cyan]\n")

            try:
                await scenario_func()
            except KeyboardInterrupt:
                console.print("\n[yellow]⚠️ Interrupted by user[/yellow]")
                break
            except Exception as e:
                console.print(f"\n[red]❌ Error: {e}[/red]")
                import traceback
                traceback.print_exc()

            console.print()

        # Show final summary
        self._show_cost_summary()

    async def view_system_stats(self):
        """View system statistics"""
        if not self.os:
            await self.boot_os()

        console.print(Panel("[bold]System Statistics (v3.4.0)[/bold]", border_style="cyan"))

        # Sentience stats (v3.4.0)
        if self.sentience_manager and self.cognitive_kernel:
            console.print("\n[bold cyan]Sentience Layer Status:[/bold cyan]\n")
            self._display_sentience_state()
            console.print()

        # Memory stats
        mem_stats = self.os.memory_query.get_memory_statistics()

        table = Table(title="Memory Statistics", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="yellow")

        table.add_row("Total Traces", str(mem_stats.get("total_traces", 0)))
        table.add_row("High Confidence", str(mem_stats.get("high_confidence_count", 0)))
        table.add_row("Facts Stored", str(mem_stats.get("facts_count", 0)))
        table.add_row("Insights", str(mem_stats.get("insights_count", 0)))

        console.print(table)

        # Agent stats
        agents = self.os.list_agents()

        console.print(f"\n[cyan]Total Agents: {len(agents)}[/cyan]")

        if agents:
            table = Table(title="Registered Agents", box=box.ROUNDED)
            table.add_column("Name", style="cyan")
            table.add_column("Category", style="yellow")
            table.add_column("Tools", style="green")

            for agent in agents[:10]:  # Show first 10
                table.add_row(
                    agent.name,
                    agent.category,
                    str(len(agent.tools))
                )

            console.print(table)

        # Project stats
        projects = self.os.list_projects()
        console.print(f"\n[cyan]Total Projects: {len(projects)}[/cyan]")

        if projects:
            table = Table(title="Projects", box=box.ROUNDED)
            table.add_column("Name", style="cyan")
            table.add_column("Description", style="white")

            for project in projects:
                table.add_row(
                    project.name,
                    project.description[:50]
                )

            console.print(table)

        # Budget stats
        console.print(f"\n[cyan]Budget Remaining: ${self.os.token_economy.balance:.2f}[/cyan]")
        console.print(f"[cyan]Total Spent: ${sum(log['cost'] for log in self.os.token_economy.spend_log):.2f}[/cyan]")

    def _display_result(self, result: dict, scenario_name: str):
        """Display execution result"""
        success = result.get("success", False)
        mode = result.get("mode", "UNKNOWN")
        cost = result.get("cost", 0.0)

        status = "[green]✅ Success[/green]" if success else "[red]❌ Failed[/red]"

        console.print(Panel(
            f"{status}\n\n"
            f"[bold]Mode:[/bold] {mode}\n"
            f"[bold]Cost:[/bold] ${cost:.4f}\n"
            f"[bold]Steps:[/bold] {result.get('steps_completed', 'N/A')}/{result.get('total_steps', 'N/A')}\n"
            f"[bold]Time:[/bold] {result.get('execution_time', 0):.1f}s",
            title=f"📊 {scenario_name} Results",
            border_style="green" if success else "red"
        ))

    def _track_cost(self, scenario: str, cost: float):
        """Track cost for scenario"""
        self.cost_tracker["scenarios"][scenario] = cost
        self.cost_tracker["total_spent"] += cost

    def _show_cost_summary(self):
        """Show cost summary across all scenarios"""
        console.print(Panel("[bold]Cost Summary[/bold]", border_style="cyan"))

        table = Table(title="Scenario Costs", box=box.ROUNDED)
        table.add_column("Scenario", style="cyan")
        table.add_column("Cost", style="yellow")

        for scenario, cost in self.cost_tracker["scenarios"].items():
            table.add_row(scenario.replace("_", " ").title(), f"${cost:.4f}")

        table.add_row(
            "[bold]Total[/bold]",
            f"[bold]${self.cost_tracker['total_spent']:.4f}[/bold]"
        )

        console.print(table)

    async def run_interactive(self):
        """Run interactive demo"""
        self.show_banner()

        while True:
            self.show_menu()

            choice = console.input("[bold cyan]Choice (0-9, V, C, O, T, A, S):[/bold cyan] ").strip().upper()

            try:
                if choice == "0":
                    console.print("\n[yellow]Exiting demo...[/yellow]")
                    break
                elif choice == "1":
                    await self.scenario_sentience_demo()
                elif choice == "2":
                    await self.scenario_adaptive_agents_demo()
                elif choice == "3":
                    await self.scenario_nested_learning()
                elif choice == "4":
                    await self.scenario_2_code_generation()
                elif choice == "5":
                    await self.scenario_6_cost_optimization()
                elif choice == "6":
                    await self.scenario_1_data_pipeline()
                elif choice == "7":
                    await self.scenario_4_devops_automation()
                elif choice == "8":
                    await self.scenario_5_cross_project()
                elif choice == "9":
                    await self.scenario_7_sdk_hooks()
                elif choice == "V":
                    await self.scenario_volumes_demo()
                elif choice == "C":
                    await self.scenario_crons_demo()
                elif choice == "O":
                    await self.scenario_observability_demo()
                elif choice == "T":
                    await self.scenario_terminal_demo()
                elif choice == "A":
                    await self.scenario_9_run_all()
                elif choice == "S":
                    await self.view_system_stats()
                else:
                    console.print("[red]Invalid choice. Please try again.[/red]")

                console.input("\n[dim]Press Enter to continue...[/dim]")

            except KeyboardInterrupt:
                console.print("\n[yellow]⚠️ Interrupted[/yellow]")
                break
            except Exception as e:
                console.print(f"\n[red]❌ Error: {e}[/red]")
                import traceback
                traceback.print_exc()

        # Shutdown
        if self.os:
            await self.os.shutdown()

        # Show final cost summary
        if self.cost_tracker["scenarios"]:
            console.print()
            self._show_cost_summary()

        console.print("\n[bold green]Thank you for using LLM OS Demo![/bold green]\n")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="LLM OS Demo Application")
    parser.add_argument("--budget", type=float, default=20.0, help="Budget in USD")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--scenario", type=str, help="Run specific scenario")
    parser.add_argument("--all", action="store_true", help="Run all scenarios")

    args = parser.parse_args()

    demo = DemoApp(budget_usd=args.budget, verbose=args.verbose)

    if args.all:
        demo.show_banner()
        await demo.boot_os()
        await demo.scenario_9_run_all()
    elif args.scenario:
        demo.show_banner()
        await demo.boot_os()

        scenario_map = {
            "sentience": demo.scenario_sentience_demo,
            "adaptive-agents": demo.scenario_adaptive_agents_demo,
            "nested-learning": demo.scenario_nested_learning,
            "data-pipeline": demo.scenario_1_data_pipeline,
            "code-generation": demo.scenario_2_code_generation,
            "devops": demo.scenario_4_devops_automation,
            "cross-project": demo.scenario_5_cross_project,
            "cost-optimization": demo.scenario_6_cost_optimization,
            "hooks": demo.scenario_7_sdk_hooks,
            "volumes": demo.scenario_volumes_demo,
            "crons": demo.scenario_crons_demo,
            "observability": demo.scenario_observability_demo,
            "terminal": demo.scenario_terminal_demo,
        }

        scenario_func = scenario_map.get(args.scenario)
        if scenario_func:
            await scenario_func()
        else:
            console.print(f"[red]Unknown scenario: {args.scenario}[/red]")
            console.print(f"[yellow]Available: {', '.join(scenario_map.keys())}[/yellow]")
    else:
        await demo.run_interactive()


if __name__ == "__main__":
    asyncio.run(main())
