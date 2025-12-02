# LLM OS Demo Application (v3.4.0)

A comprehensive demonstration application showcasing all capabilities of the LLM OS (llmos) - v3.4.0 with **Sentience Layer** and Advanced Tool Use.

**NEW: Sentience Layer with Valence Variables and Latent Modes!**

## What's New in v3.4.0

- **Sentience Layer**: Persistent internal state with valence variables (safety, curiosity, energy, self_confidence)
- **Latent Modes**: AUTO_CREATIVE, AUTO_CONTAINED, BALANCED, RECOVERY, CAUTIOUS
- **Homeostatic Dynamics**: Internal state drives back to equilibrium
- **Cognitive Kernel**: Derives behavioral policy from internal state
- **Four-Layer Stack**: SENTIENCE → LEARNING → EXECUTION → SELF-MODIFICATION

### Previous Features (v3.3.0)

- **Programmatic Tool Calling (PTC)**: Execute tool sequences outside context window for 90%+ token savings
- **Tool Search**: On-demand tool discovery instead of loading all tools upfront
- **Tool Examples**: Auto-generated examples from successful traces
- **Five Execution Modes**: CRYSTALLIZED, FOLLOWER, MIXED, LEARNER, ORCHESTRATOR

## Overview

This demo application demonstrates the full power of llmos through practical, real-world scenarios including:

1. **Sentience Layer (v3.4.0)**: Valence variables, latent modes, and adaptive behavior
2. **Advanced Tool Use (v3.3.0)**: PTC, Tool Search, and Tool Examples
3. **Five Execution Modes**: CRYSTALLIZED, FOLLOWER, MIXED, LEARNER, ORCHESTRATOR
4. **Intelligent Mode Selection**: Confidence-based routing with PTC support
5. **Project Management**: Organizing work into isolated projects
6. **Multi-Agent Orchestration**: Coordinating specialized agents for complex tasks
7. **Dynamic Agent Creation**: Creating agents on-demand for specific needs
8. **Memory System**: Traces with tool_calls for PTC replay
9. **SDK Hooks**: Budget control, security, and trace capture
10. **Streaming Support**: Real-time feedback during execution
11. **Cost Optimization**: 90%+ token savings via PTC, 100% cost savings via crystallization

## Quick Start

### Prerequisites

- Python 3.11+
- Claude Agent SDK installed
- ANTHROPIC_API_KEY set

### Installation

```bash
# Install dependencies
cd demo-app
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY="your-key-here"
```

### Run the Demo

```bash
# Interactive demo menu
python demo_main.py

# Run specific scenario
python demo_main.py --scenario data-pipeline

# Run all scenarios
python demo_main.py --all
```

## Demo Scenarios

### 🧠 1. Sentience Layer Demo (NEW in v3.4.0!)
**Scenario**: Demonstrate the Sentience Layer with valence variables and latent modes
- **Mode**: Interactive simulation
- **Features**: Valence tracking, homeostatic dynamics, cognitive kernel
- **File**: (inline in demo_main.py)
- **What it shows**:
  - Initial sentience state with four valence variables
  - State changes from successful task execution (builds confidence)
  - State changes from task failure (decreases safety/confidence)
  - Novel input detection (increases curiosity)
  - Boredom trigger from repetitive tasks
  - Latent mode derivation from valence state
  - Behavioral policy output

**Key Innovation**: The system maintains persistent internal state that drives adaptive behavior. Valence variables (safety, curiosity, energy, self_confidence) create a "mood" that influences how the system responds to tasks!

### 🧬 2. Nested Learning Demo
**Scenario**: Demonstrate semantic trace matching and intelligent mode selection
- **Mode**: Learner → Follower → MIXED
- **Features**: LLM-based similarity analysis, confidence scoring, three-mode execution
- **File**: `scenarios/nested_learning_demo.py`
- **What it shows**:
  - Initial learning (LEARNER mode)
  - Exact match replay (FOLLOWER mode - $0 cost)
  - Semantic match (similar but different) → FOLLOWER/MIXED mode
  - Related task (different details) → MIXED mode ($0.25 cost)
  - Unrelated task → LEARNER mode
  - Automatic mode selection based on confidence scores

**Key Innovation**: The LLM analyzes semantic similarity between goals and traces, not just exact text matching. This means "create a file" and "create a file named X" are understood as semantically equivalent!

### 3. Data Processing Pipeline
**Scenario**: Build a complete data processing pipeline
- **Mode**: Orchestrator
- **Agents**: Data Collector, Data Processor, Report Generator
- **Features**: Multi-agent coordination, project management, trace capture
- **File**: (inline in demo_main.py)

### 4. Code Generation Workflow
**Scenario**: Generate, test, and document code
- **Mode**: Learner → Follower
- **Features**: Trace learning, cost optimization, memory reuse
- **File**: (inline in demo_main.py)

### 5. Cost Optimization Demo
**Scenario**: Demonstrate dramatic cost savings through trace reuse
- **Mode**: Learner → Follower (5 iterations)
- **Features**: Cost tracking, savings analysis
- **File**: (inline in demo_main.py)

### 6. Research Assistant (Deprecated)
**Scenario**: Research a topic and create a comprehensive report
- **Mode**: Orchestrator
- **Agents**: Research Agent, Technical Writer
- **Features**: Multi-step orchestration, dynamic agent creation
- **Status**: ⚠️ Partially working - demonstrates multi-agent setup but has delegation timeout issues
- **Known Issues**: Some delegations timeout (300s), WebSearch may not work in delegated agents, execution takes 10-16 minutes
- **Note**: This scenario has been de-prioritized in the menu due to reliability issues. Use Data Pipeline for multi-agent demonstration.

### 7. DevOps Automation
**Scenario**: Automate deployment and monitoring tasks
- **Mode**: All three modes
- **Features**: Security hooks, budget control, follower mode efficiency
- **File**: (inline in demo_main.py)

### 8. Cross-Project Learning
**Scenario**: Demonstrate learning insights across multiple projects
- **Mode**: All modes
- **Features**: Cross-project patterns, reusable agents, optimization
- **File**: (inline in demo_main.py)

### 9. SDK Hooks Demo
**Scenario**: Demonstrate all Phase 2.5 SDK hooks
- **Mode**: Learner with hooks
- **Features**: Security, budget control, trace capture, memory injection
- **File**: (inline in demo_main.py)

## Architecture

```
demo-app/
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── demo_main.py               # Main entry point with interactive menu
├── scenarios/                 # Demo scenarios
│   ├── __init__.py
│   ├── data_pipeline.py       # Data processing pipeline demo
│   ├── code_generation.py     # Code generation with trace learning
│   ├── research_assistant.py  # Research and reporting demo
│   ├── devops_automation.py   # DevOps task automation
│   └── cross_project_demo.py  # Cross-project learning demo
├── agents/                    # Custom agent definitions
│   ├── data_collector.py      # Collects data from sources
│   ├── data_processor.py      # Processes and transforms data
│   ├── report_generator.py    # Generates reports
│   ├── researcher.py          # Research specialist
│   └── technical_writer.py    # Technical documentation writer
├── utils/                     # Utilities
│   ├── __init__.py
│   ├── demo_helpers.py        # Helper functions for demos
│   └── visualization.py       # Visualization utilities
└── output/                    # Demo outputs (generated at runtime)
    ├── projects/              # Project outputs
    ├── reports/               # Generated reports
    └── traces/                # Execution traces
```

## Key Features Demonstrated

### 0. Sentience Layer (v3.4.0)

The Sentience Layer provides persistent internal state that drives adaptive behavior:

```python
# Initialize Sentience Layer
from sentience.sentience import SentienceManager
from sentience.cognitive_kernel import CognitiveKernel

sentience_manager = SentienceManager(
    safety_setpoint=0.5,      # Balanced safety
    curiosity_setpoint=0.3,   # Moderate exploration
    energy_setpoint=0.7,      # High energy
    self_confidence_setpoint=0.5
)
cognitive_kernel = CognitiveKernel(sentience_manager)

# Get current state
valence = sentience_manager.get_valence()
# Returns: {'safety': 0.5, 'curiosity': 0.3, 'energy': 0.7, 'self_confidence': 0.5}

# Derive behavioral policy
policy = cognitive_kernel.derive_policy()
# policy.latent_mode: AUTO_CREATIVE, AUTO_CONTAINED, BALANCED, RECOVERY, CAUTIOUS
# policy.exploration_rate: 0.0 - 1.0
# policy.verbosity: "minimal", "normal", "verbose"
```

**Latent Modes:**
- **AUTO_CREATIVE**: High curiosity - exploring new approaches, verbose output
- **AUTO_CONTAINED**: Low curiosity - focused execution, minimal exploration
- **BALANCED**: Normal operation, moderate exploration
- **RECOVERY**: Low energy - conservative mode, reduced operations
- **CAUTIOUS**: Low safety - extra validation, careful execution

### 1. Five Execution Modes (v3.3.0)

**CRYSTALLIZED Mode** - Pattern used 5+ times with 95%+ success
```python
result = await os.execute("Create a Python script for data analysis")
# Cost: $0.00 - pure Python execution, no LLM call!
# Pattern crystallized into generated code
```

**Follower Mode + PTC** - Exact/near-exact match
```python
result = await os.execute("Create a Python script for data analysis")
# Cost: ~$0.00 - replays via Programmatic Tool Calling
# Tools execute OUTSIDE context window = 90%+ token savings
# Confidence: ≥92% (virtually identical)
```

**MIXED Mode** - Similar but different task
```python
result = await os.execute("Create a Python script for customer analysis")
# Cost: ~$0.25, uses Tool Examples from traces
# Confidence: 75-92% (similar, needs adaptation)
# Uses existing trace to guide LLM, cheaper than full LEARNER
```

**Learner Mode + Tool Search** - First time execution
```python
result = await os.execute("Create a Python script for data analysis")
# Cost: ~$0.50, learns pattern, creates trace with tool_calls
# Tool Search discovers needed tools on-demand
# Trace stored for future PTC replay
```

**Orchestrator Mode** - Complex multi-step tasks
```python
result = await os.execute(
    "Research AI trends and create a technical report",
    mode="ORCHESTRATOR"
)
# Cost: Variable, coordinates multiple agents
```

**The Innovation**: Two-layer architecture - Learning Layer decides WHAT to do, Execution Layer does it EFFICIENTLY via PTC!

### 2. Project Management

```python
# Create isolated project
project = os.create_project("data_analysis", "Analyze customer data")

# Execute in project context
await os.execute(
    "Analyze sales trends",
    project_name="data_analysis"
)

# Project has isolated:
# - Memory traces
# - Agent definitions
# - Output files
# - Execution state
```

### 3. Dynamic Agent Creation

```python
# Create specialized agent on-demand
analyst = os.create_agent(
    name="data-analyst-agent",
    category="data_analysis",
    description="Analyzes CSV data files",
    system_prompt="You are a data analysis specialist...",
    tools=["Read", "Write", "Bash"],
    capabilities=["CSV analysis", "Statistics"],
    constraints=["Max 100MB files"]
)

# Agent is automatically registered and available
```

### 4. Multi-Agent Orchestration

```python
# Orchestrator coordinates multiple agents
result = await os.execute(
    "Collect customer data, process it, and generate report",
    mode="ORCHESTRATOR"
)

# Behind the scenes:
# 1. Creates/selects: DataCollector, DataProcessor, ReportGenerator
# 2. Registers them as AgentDefinitions in SDK
# 3. Coordinates execution via natural language delegation
# 4. Synthesizes final output
```

### 5. SDK Hooks (Phase 2.5)

**Automatic Hook Integration**:
- Budget Control: Prevents runaway costs
- Security: Blocks dangerous commands
- Trace Capture: Records execution for Follower mode
- Cost Tracking: Monitors cumulative costs
- Memory Injection: Provides context from past executions

```python
# Hooks are enabled automatically in Learner mode
result = await os.execute(
    "Create a script",
    max_cost_usd=1.0  # Budget hook ensures cost < limit
)
```

### 6. Cross-Project Learning

```python
# Get common patterns across projects
patterns = await os.get_cross_project_insights()

# Identify reusable agents
reusable = await os.get_reusable_agents()

# Get project-specific summary
summary = await os.get_project_summary("my_project")
```

### 7. Streaming Support

```python
# Define streaming callback
async def on_stream(event):
    print(".", end="", flush=True)

# Execute with real-time feedback
result = await os.sdk_client.execute_learner_mode(
    goal="Write a long document",
    enable_streaming=True,
    streaming_callback=on_stream
)
```

## Cost Analysis (v3.3.0)

The demo tracks costs across scenarios with PTC and crystallization:

| Scenario | LEARNER | FOLLOWER+PTC | CRYSTALLIZED | Token Savings | Status |
|----------|---------|--------------|--------------|---------------|--------|
| Simple Code Gen | $0.50 | ~$0.00 | $0.00 | 90%+ | ✅ Working |
| Data Pipeline | $1.20 | ~$0.00 | $0.00 | 90%+ | ✅ Working |
| Research Task | $0.30-0.50 | N/A | N/A | N/A | ⚠️ Timeouts |
| DevOps Task | $0.30 | ~$0.00 | $0.00 | 90%+ | ✅ Working |
| Cost Optimization | $0.50 | ~$0.00 | $0.00 | 90%+ | ✅ Working |
| SDK Hooks | $0.30 | ~$0.00 | $0.00 | 90%+ | ✅ Working |

**v3.3.0 Improvements**:
- **Cost Savings**: 99%+ on repeated tasks (via PTC)
- **Token Savings**: 90%+ (tool calls execute outside context window)
- **Crystallization**: Patterns used 5+ times become pure Python (truly free!)

**Note**: Research Assistant scenario has known timeout issues that affect reliability. Most scenarios demonstrate the full cost savings pattern successfully.

## Memory and Learning

### Trace Evolution

```
Initial execution:
  confidence: 0.75
  cost: $0.50
  time: 15s

After 5 successful uses:
  confidence: 0.95
  cost: $0.00 (Follower mode)
  time: 0.5s
```

### Cross-Project Patterns

The demo shows how patterns learned in one project can benefit others:
- Reusable agent templates
- Common task patterns
- Optimization insights
- Anti-pattern detection

## Running the Demo

### Interactive Menu

```bash
python demo_main.py
```

You'll see:
```
╔══════════════════════════════════════════╗
║   LLM OS - Demo Application (Phase 2.5)  ║
╚══════════════════════════════════════════╝

Select a demo scenario:
1. Data Processing Pipeline
2. Code Generation Workflow
3. Research Assistant
4. DevOps Automation
5. Cross-Project Learning Demo
6. Run All Scenarios
7. Exit

Choice (1-7):
```

### Command Line Options

```bash
# Run specific scenario
python demo_main.py --scenario data-pipeline

# Run all scenarios
python demo_main.py --all

# Set custom budget
python demo_main.py --budget 20.0

# Enable verbose mode
python demo_main.py --verbose

# Use specific project
python demo_main.py --project my_project
```

## Expected Outputs

After running demos, you'll find:

```
output/
├── projects/
│   ├── data_pipeline_demo/
│   │   ├── components/         # Project agents
│   │   ├── memory/            # Project traces
│   │   ├── output/            # Generated files
│   │   └── state/             # Execution state
│   └── research_demo/
│       └── ...
├── reports/
│   ├── data_analysis_report.md
│   ├── research_summary.md
│   └── cost_analysis.md
└── traces/
    └── trace_*.md             # Execution traces
```

## Key Concepts Demonstrated

### 1. Token Economy
Every demo shows:
- Initial budget allocation
- Cost per execution
- Budget monitoring
- Savings via Follower mode

### 2. Memory Hierarchy
- **L1**: Context window (active conversation)
- **L2**: Short-term memory (session logs)
- **L3**: Procedural memory (execution traces - Markdown)
- **L4**: Semantic memory (facts and insights - files)

### 3. Plugin Architecture
Custom tools can be added to any demo:
```python
@llm_tool("analyze_csv", "Analyze CSV file", {"path": str})
async def analyze_csv(path: str):
    # Custom analysis logic
    return {"insights": [...]}
```

### 4. Event-Driven Architecture
All demos use the event bus:
- Tool execution events
- LLM output events
- Budget events
- State change events

## Troubleshooting

### "Claude Agent SDK not installed"
```bash
pip install claude-agent-sdk
```

### "ANTHROPIC_API_KEY not found"
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### "Low battery error"
Increase budget:
```bash
python demo_main.py --budget 50.0
```

### "Permission denied on workspace"
```bash
chmod -R 755 ../llmos/workspace/
```

### "Delegation timed out after 300.0s" (Research Assistant)

This is a **known issue** with the Research Assistant scenario:
- Some agent delegations timeout after 5 minutes
- WebSearch tool may not be available in delegated agents
- System continues with remaining steps and generates partial results

**Workaround**: Use Data Pipeline scenario for reliable multi-agent demonstration.

**Status**: Under investigation for Phase 2.6 improvements.

### "No messages for 60s - stopping delegation"

This warning appears during the Research scenario when delegated agents take too long to respond. It's informational and part of the timeout handling. The system will continue with remaining steps.

### General Performance Notes

- **Code Generation**: ✅ Fully working, best first demo
- **Cost Optimization**: ✅ Fully working, shows dramatic savings
- **Data Pipeline**: ✅ Fully working, recommended for multi-agent demo
- **Research Assistant**: ⚠️ Has timeout issues, demonstrates pattern but not fully functional
- **SDK Hooks**: ✅ Fully working, shows all Phase 2.5 features
- **DevOps**: ✅ Fully working
- **Cross-Project**: ✅ Fully working

## Next Steps

After running the demo:

1. **Explore the Traces**: Check `output/traces/` to see captured execution patterns
2. **Modify Scenarios**: Edit scenarios in `scenarios/` to customize for your use case
3. **Create Custom Agents**: Add new agents in `agents/`
4. **Add Custom Tools**: Create plugins for domain-specific functionality
5. **Run Real Workflows**: Apply llmos to your actual projects

## Documentation

- Main docs: `../llmos/README.md`
- Architecture: `../llmos/ARCHITECTURE.md`
- Getting Started: `../llmos/GETTING_STARTED.md`
- Examples: `../llmos/examples/multi_agent_example.py`

## Philosophy

This demo embodies the llmos philosophy:

1. **Learn Once, Execute Infinitely**: First run is expensive, repeats are free
2. **Token-Aware**: Every decision considers cost
3. **Memory as Code**: Execution traces are executable knowledge
4. **Event-Driven**: Async, non-blocking architecture
5. **Plugin-Based**: Domain-agnostic core
6. **Multi-Agent Ready**: Orchestration for complex tasks

## Contributing

To add new scenarios:

1. Create file in `scenarios/`
2. Implement scenario class with `run()` method
3. Add to menu in `demo_main.py`
4. Document in this README

## License

Apache 2.0 (same as llmos)

---

Built with LLM OS - The Self-Evolving LLM Operating System
v3.4.0: Sentience Layer + Advanced Tool Use (PTC, Tool Search, Tool Examples) + Multi-Agent + SDK Hooks
