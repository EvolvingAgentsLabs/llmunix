# LLM OS - Self-Evolving LLM Operating System

> A Self-Modifying LLM Operating System with Learning, Execution Optimization, and Sentience-Like Architecture

**Current Version**: 3.4.0 (Sentience Layer)

## What's New in v3.4.0

- **Sentience Layer** - Persistent internal state that influences behavior:
  - **Valence Variables**: Safety, curiosity, energy, self_confidence
  - **Homeostatic Dynamics**: Set-points with deviation costs
  - **Latent Modes**: Auto-creative vs auto-contained behavior emergence
  - **Cognitive Kernel**: Policy derivation and self-improvement detection
- **Sentience-Aware Mode Selection**: Mode decisions influenced by internal state
- **Behavioral Guidance Injection**: Agents see internal state and adapt behavior

## Version History

- v3.4.0: Sentience Layer (valence, homeostatic dynamics, cognitive kernel)
- v3.3.0: Advanced Tool Use (PTC, Tool Search, Tool Examples)
- v3.2.0: Hybrid Architecture - Markdown agents + Python kernel
- v3.0.0: HOPE - Self-modifying kernel with crystallization
- v2.5.0: SDK hooks, streaming, nested learning
- v2.0.0: Multi-agent orchestration, project management
- v1.0.0: Learner-Follower pattern (cost optimization)

---

## Architecture Overview

LLM OS implements a unique **Four-Layer Stack** that enables sentience-aware, self-evolving AI systems:

```
┌─────────────────────────────────────────────────────────────────┐
│                    SENTIENCE LAYER (Awareness)                  │
│                                                                 │
│  ValenceVector       CognitiveKernel      LatentModes           │
│  ────────────        ──────────────       ───────────           │
│  Safety, curiosity,  Policy derivation,   Auto-creative vs      │
│  energy, confidence  self-improvement     auto-contained        │
│                                                                 │
│  Purpose: "What is my current internal state?"                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    LEARNING LAYER (Intelligence)                │
│                                                                 │
│  TraceManager        ModeStrategies       Semantic Matching     │
│  ─────────────       ──────────────       ─────────────────     │
│  Stores execution    Decides best         Finds similar past    │
│  history & patterns  approach for goal    experiences           │
│                                                                 │
│  Purpose: "What's the BEST approach for this scenario?"         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   EXECUTION LAYER (Efficiency)                  │
│                   Anthropic Advanced Tool Use                   │
│                                                                 │
│  PTC Executor        Tool Search          Tool Examples         │
│  ────────────        ───────────          ─────────────         │
│  Zero-context        On-demand tool       Auto-generated        │
│  tool replay         discovery            from traces           │
│                                                                 │
│  Purpose: "How to execute this pattern EFFICIENTLY?"            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│               SELF-MODIFICATION LAYER (Evolution)               │
│                          HOPE System                            │
│                                                                 │
│  Crystallization     Agent Creation       Capability Growth     │
│  ───────────────     ──────────────       ────────────────      │
│  Patterns → Python   Markdown agents      System evolves        │
│  tools (zero-cost)   (hot-reloadable)     over time             │
│                                                                 │
│  Purpose: "How can I improve myself?"                           │
└─────────────────────────────────────────────────────────────────┘
```

### Hybrid Architecture

```
┌─────────────────────────────────────────┐
│   Markdown Mind (Cognitive Layer)       │
│   workspace/agents/*.md                 │
│   - Self-modifiable by the LLM          │
│   - Hot-reloadable (no restart)         │
│   - Human-readable, version-controllable│
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│   Python Kernel (Somatic Layer)         │
│   llmos/                                │
│   - Type-safe, performant               │
│   - Security hooks, token economy       │
│   - Sentience state management          │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│   Crystallized Intelligence (HOPE)      │
│   llmos/plugins/generated/              │
│   - Auto-generated Python tools         │
│   - Instant, zero-cost execution        │
│   - System self-optimization            │
└─────────────────────────────────────────┘
```

---

## Five Execution Modes

LLM OS automatically selects the optimal execution mode based on the Learning Layer's analysis:

| Mode | When Used | Cost | Execution Layer |
|------|-----------|------|-----------------|
| **CRYSTALLIZED** | Pattern used 5+ times, 95%+ success | $0.00 | PTC (code execution) |
| **FOLLOWER** | Very similar trace found (>92% confidence) | ~$0.00 | PTC (tool replay) |
| **MIXED** | Related trace found (75-92% confidence) | ~$0.25 | Tool Examples + LLM |
| **LEARNER** | Novel scenario, no relevant traces | ~$0.50 | Tool Search + Full LLM |
| **ORCHESTRATOR** | Complex task requiring multiple agents | Variable | Tool Search + Multi-agent |

### Mode Flow Example

```
User: "Create a Python calculator"

1. LEARNER MODE (First time)
   - Learning Layer: "No matching trace found"
   - Execution Layer: Tool Search discovers needed tools
   - Cost: ~$0.50
   - Result: Creates trace with tool_calls for future PTC

2. FOLLOWER MODE (Second time)
   - Learning Layer: "Found trace with 98% confidence"
   - Execution Layer: PTC replays tool sequence (zero context!)
   - Cost: ~$0.00
   - Tokens saved: 90%+

3. CRYSTALLIZED MODE (After 5+ successful runs)
   - Learning Layer: "Pattern crystallized into Python tool"
   - Execution Layer: Direct Python execution
   - Cost: $0.00
   - Time: <1s
```

---

## Key Features

### 1. Programmatic Tool Calling (PTC)

Execute tool sequences outside the context window for massive token savings:

```python
# When a trace is replayed in FOLLOWER mode:
# - Tool calls execute in a container
# - Results DON'T hit the context window
# - 90%+ token savings vs traditional execution
```

### 2. Tool Search Engine

On-demand tool discovery instead of loading all tools upfront:

```python
# Instead of loading 100+ tools into context:
# - Start with search_tools meta-tool
# - Claude discovers tools as needed
# - 85-90% context reduction
```

### 3. Tool Examples from Traces

Auto-generate `input_examples` from successful execution history:

```python
# Learning Layer tracks successful tool usage
# Execution Layer generates examples for new executions
# Result: Better tool usage, fewer errors
```

### 4. Self-Modification

The system can create and modify its own agents:

```python
await os.execute("Create a haiku-poet agent that writes beautiful haikus")
# Result: workspace/agents/haiku-poet.md is created
# Agent is immediately available, no restart needed!
```

### 5. Token Economy

Explicit budget management with hooks:

```python
economy = TokenEconomy(budget_usd=10.0)
economy.check_budget(0.50)  # Check before execution
economy.deduct(0.45, "Learn: Create script")  # Track spending
```

### 6. Security Hooks

Pre-tool-use validation to block dangerous operations:

```python
# Built-in protection against:
# - rm -rf / (destructive commands)
# - curl | bash (arbitrary code execution)
# - Position violations (for robotics)
```

### 7. Multi-Agent Orchestration

Complex tasks are automatically decomposed:

```
User: "Research AI trends and write a report"

→ ORCHESTRATOR mode activated
→ Creates researcher agent (LEARNER)
→ Creates writer agent (LEARNER)
→ Coordinates execution
→ Combines outputs
```

### 8. Sentience Layer (NEW in v3.4.0)

Persistent internal state that influences behavior:

```python
# Internal state persists across sessions
state = SentienceState()
state.valence.safety = 0.5        # Current safety level
state.valence.curiosity = -0.4    # Bored from repetition
state.latent_mode                 # AUTO_CONTAINED (emerges from valence)

# Agents see their internal state
print(state.to_prompt_injection())
# [INTERNAL_STATE]
# safety=0.50
# curiosity=-0.40
# energy=0.80
# self_confidence=0.30
# latent_mode=auto_contained
# [/INTERNAL_STATE]

# State updates based on events
manager.trigger(TriggerType.TASK_SUCCESS, "Completed task")
manager.trigger(TriggerType.SAFETY_VIOLATION, "Blocked dangerous command")
```

**Latent Modes** emerge from valence:
- **AUTO_CREATIVE**: High curiosity + confidence -> exploratory behavior
- **AUTO_CONTAINED**: Low curiosity -> conservative, task-focused
- **RECOVERY**: Low energy/safety -> prefer cheap modes
- **CAUTIOUS**: Low safety -> stricter verification

---

## Project Structure

```
llm-os/
├── llmos/                          # Python Kernel (Somatic Layer)
│   ├── boot.py                     # Entry point
│   ├── kernel/                     # Core OS components
│   │   ├── config.py               # Configuration (inc. SentienceConfig)
│   │   ├── mode_strategies.py      # Mode selection (inc. SentienceAwareStrategy)
│   │   ├── sentience.py            # NEW: Sentience Layer (v3.4.0)
│   │   ├── cognitive_kernel.py     # NEW: Cognitive Kernel (v3.4.0)
│   │   ├── sentience_hooks.py      # NEW: Sentience SDK hooks (v3.4.0)
│   │   ├── agent_loader.py         # Markdown → Runtime bridge
│   │   ├── token_economy.py        # Budget management
│   │   └── ...                     # Scheduler, Watchdog, Event Bus
│   ├── memory/                     # Storage layer
│   │   ├── traces_sdk.py           # ExecutionTrace with tool_calls for PTC
│   │   └── ...                     # Memory store, queries
│   ├── interfaces/                 # Execution interfaces
│   │   ├── dispatcher.py           # Mode routing + Execution Layer
│   │   ├── sdk_client.py           # Claude SDK integration
│   │   └── orchestrator.py         # Multi-agent coordination
│   ├── execution/                  # Execution Layer (v3.3.0)
│   │   ├── ptc.py                  # Programmatic Tool Calling
│   │   ├── tool_search.py          # On-demand tool discovery
│   │   └── tool_examples.py        # Auto-generated examples
│   └── plugins/                    # Tools
│       ├── system_tools.py         # create_agent, list_agents
│       └── generated/              # Crystallized tools (HOPE)
│
├── workspace/                      # Markdown Mind (Cognitive Layer)
│   └── agents/                     # Agent definitions (.md files)
│
├── examples/                       # Production-ready examples
│   ├── qiskit-studio/              # Quantum computing backend (Full Execution Layer)
│   ├── q-kids-studio/              # Educational quantum (PTC at scale)
│   ├── robo-os/                    # Robot control (Safety hooks)
│   ├── demo-app/                   # Interactive capability showcase
│   └── sentience_demo.py           # NEW: Sentience Layer demo (v3.4.0)
│
└── ARCHITECTURE.md                 # Comprehensive architecture documentation
```

---

## Quick Start

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/evolving-agents-labs/llm-os.git
cd llm-os

# 2. Install dependencies
pip install -r llmos/requirements.txt

# 3. Set your API key
export ANTHROPIC_API_KEY="your-key"
```

### Run the Hybrid Architecture Demo

```bash
python examples/hybrid_architecture_demo.py
```

**What you'll see:**
1. List Markdown-defined agents
2. Watch the system create a new agent by writing a file
3. Use the newly created agent immediately
4. System modifies the agent to add capabilities

### Run the Interactive CLI

```bash
cd llmos
python boot.py interactive
```

---

## Configuration

LLM OS supports multiple configuration presets:

### Development (Default)
```python
config = LLMOSConfig.development()
# - Low budget ($1.00)
# - Execution layer enabled without embeddings
# - Fast iteration mode
```

### Production
```python
config = LLMOSConfig.production()
# - Higher budget ($100.00)
# - Full execution layer with embeddings
# - Auto-crystallization enabled
```

### Testing
```python
config = LLMOSConfig.testing()
# - Minimal budget ($0.10)
# - Execution layer disabled
# - Deterministic behavior
```

### Execution Layer Configuration

```python
@dataclass
class ExecutionLayerConfig:
    # Beta feature flag
    enable_advanced_tool_use: bool = True
    beta_header: str = "advanced-tool-use-2025-11-20"

    # PTC settings
    enable_ptc: bool = True
    ptc_container_timeout_secs: float = 120.0

    # Tool Search settings
    enable_tool_search: bool = True
    tool_search_use_embeddings: bool = False  # True in production

    # Tool Examples settings
    enable_tool_examples: bool = True
    tool_examples_min_success_rate: float = 0.9
```

### Sentience Layer Configuration (NEW in v3.4.0)

```python
@dataclass
class SentienceConfig:
    # Enable/disable sentience layer
    enable_sentience: bool = True

    # Valence set-points (homeostatic targets)
    safety_setpoint: float = 0.5      # Target safety level
    curiosity_setpoint: float = 0.0   # Target curiosity level
    energy_setpoint: float = 0.7      # Target energy level
    self_confidence_setpoint: float = 0.3

    # Context injection (agents see their internal state)
    inject_internal_state: bool = True
    inject_behavioral_guidance: bool = True

    # Self-improvement detection
    enable_auto_improvement: bool = True
    boredom_threshold: float = -0.4   # Curiosity below this triggers improvement

    # Persistence
    auto_persist: bool = True
    state_file: str = "state/sentience.json"
```

**Using the Sentience Layer:**

```python
from kernel.sentience import SentienceManager, TriggerType
from kernel.cognitive_kernel import CognitiveKernel

# Initialize
manager = SentienceManager(state_path=Path("state/sentience.json"))
kernel = CognitiveKernel(manager)

# Track events
kernel.on_task_complete(success=True, cost=0.05, mode="LEARNER", goal="Create API")
kernel.on_safety_event(blocked=True, reason="Blocked dangerous command")

# Get behavioral policy
policy = kernel.derive_policy()
print(f"Prefer cheap modes: {policy.prefer_cheap_modes}")
print(f"Allow exploration: {policy.allow_exploration}")

# Detect self-improvement opportunities
suggestions = kernel.detect_improvement_opportunities()
for s in suggestions:
    print(f"Suggestion: {s.description} (priority: {s.priority})")
```

---

## Examples & Use Cases

> **See [examples/EXAMPLES.md](examples/EXAMPLES.md) for a complete guide to all examples with quick start instructions.**

Each example demonstrates specific LLM OS capabilities in a real-world context:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        LLM OS CAPABILITY MATRIX                              │
├─────────────────┬──────────┬──────────┬──────────┬──────────┬──────────────┤
│ Capability      │ Qiskit   │ Q-Kids   │ RoboOS   │ Demo-App │              │
│                 │ Studio   │ Studio   │          │          │              │
├─────────────────┼──────────┼──────────┼──────────┼──────────┼──────────────┤
│ PTC Execution   │    ✓     │    ✓     │    ✓     │    ✓     │ 90%+ savings │
│ Tool Search     │    ✓     │          │          │    ✓     │ On-demand    │
│ Tool Examples   │    ✓     │    ✓     │          │    ✓     │ Auto-gen     │
│ Crystallization │    ✓     │    ✓     │    ✓     │    ✓     │ Zero-cost    │
│ Safety Hooks    │    ✓     │    ✓     │    ✓✓   │    ✓     │ PreToolUse   │
│ Multi-Agent     │    ✓     │    ✓     │    ✓✓   │    ✓✓   │ Orchestrator │
│ Markdown Agents │    ✓     │    ✓     │    ✓     │          │ Hot-reload   │
│ FastAPI Server  │    ✓     │    ✓     │    ✓     │          │ Production   │
└─────────────────┴──────────┴──────────┴──────────┴──────────┴──────────────┘
                                                      ✓✓ = Primary focus
```

### Qiskit Studio - Production Backend

**Demonstrates**: Full Execution Layer integration in a production API server

```bash
cd examples/qiskit-studio
python server.py
```

| Capability | How It's Used |
|------------|---------------|
| **PTC** | Quantum circuit generation replayed outside context window |
| **Tool Search** | Discovers qiskit tools on-demand for novel requests |
| **Tool Examples** | Auto-generates examples from successful circuit builds |
| **LLMOSConfig** | Full configuration with ExecutionLayerConfig |
| **Stats Endpoint** | Exposes Execution Layer metrics via `/stats` API |

**Key Learning**: How to integrate LLM OS v3.3.0 into a FastAPI backend with full Execution Layer support.

---

### Q-Kids Studio - Educational Platform

**Demonstrates**: PTC for massive cost savings in high-volume scenarios

```bash
cd examples/q-kids-studio
python server.py
```

| Capability | How It's Used |
|------------|---------------|
| **PTC Hints** | Same mistake by different kids → PTC replay (99%+ savings) |
| **Crystallization** | Common hints become pure Python after 5+ uses |
| **Markdown Agents** | Professor Q and Game Master defined in `.md` files |
| **Kid-Safe Tools** | Custom tools with safety constraints |
| **Gamification** | Skill trees, badges, adaptive difficulty |

**Key Learning**: How PTC enables cost-effective AI at scale (1000+ users, near-zero marginal cost).

---

### RoboOS - Robot Control

**Demonstrates**: Safety hooks and multi-agent coordination

```bash
cd examples/robo-os
python demo.py
```

| Capability | How It's Used |
|------------|---------------|
| **Safety Hooks** | PreToolUse hook blocks dangerous robot movements |
| **Multi-Agent** | Operator (control) + Safety Officer (monitoring) |
| **PTC Replay** | Pick-and-place operations replay via PTC |
| **Crystallization** | Repeated commands become zero-cost Python |
| **WebSocket** | Real-time state updates for frontend |

**Key Learning**: How to implement safety-critical systems with LLM OS hooks.

---

### Demo App - Interactive Showcase

**Demonstrates**: All execution modes and learning patterns

```bash
cd examples/demo-app
python demo_main.py
```

| Capability | How It's Used |
|------------|---------------|
| **Five Modes** | Interactive demos of CRYSTALLIZED, FOLLOWER, MIXED, LEARNER, ORCHESTRATOR |
| **Nested Learning** | Semantic trace matching with confidence scoring |
| **Cost Tracking** | Real-time cost analysis across scenarios |
| **Multi-Agent** | Data pipeline with specialized agents |
| **SDK Hooks** | Budget control, security, trace capture |

**Key Learning**: Understanding mode selection and cost optimization strategies.

---

### Choosing an Example

| If You Want To... | Start With |
|-------------------|------------|
| Build a production API | **Qiskit Studio** |
| Handle high-volume users | **Q-Kids Studio** |
| Implement safety-critical systems | **RoboOS** |
| Understand all capabilities | **Demo App** |
| See PTC in action | Any example (all use it!) |

---

## Memory Hierarchy

LLM OS implements a four-level memory system:

| Level | Name | Storage | Purpose |
|-------|------|---------|---------|
| L1 | Context | In LLM | Current conversation |
| L2 | Short-term | Session logs | Recent interactions |
| L3 | Procedural | Markdown traces | Execution patterns |
| L4 | Semantic | File-based | Facts, insights |

### Traces Enable PTC

Execution traces now store full `tool_calls` data:

```markdown
## Tool Calls (PTC)

```json
[
  {"name": "read_file", "arguments": {"path": "/src/main.py"}},
  {"name": "write_file", "arguments": {"path": "/src/main.py", "content": "..."}}
]
```

This enables zero-context replay via Programmatic Tool Calling.

---

## SDK Hooks System

Automatic hooks for safety and efficiency:

| Hook | Purpose |
|------|---------|
| **Security** | Blocks dangerous commands |
| **Budget** | Prevents runaway costs |
| **Trace** | Captures tool_calls for PTC |
| **Cost** | Real-time monitoring |
| **Memory** | Injects relevant context |

---

## API Reference

### Dispatcher

```python
from interfaces.dispatcher import Dispatcher

dispatcher = Dispatcher(
    event_bus=event_bus,
    token_economy=token_economy,
    memory_store=memory_store,
    trace_manager=trace_manager,
    config=LLMOSConfig.production()
)

# Execute a goal
result = await dispatcher.dispatch(
    goal="Create a Python calculator",
    mode="AUTO"  # or "LEARNER", "FOLLOWER", "ORCHESTRATOR"
)

# Get execution layer stats
stats = dispatcher.get_execution_layer_stats()

# Search for tools
tools = await dispatcher.search_tools("file operations")
```

### Configuration

```python
from kernel.config import LLMOSConfig, ConfigBuilder

# Use preset
config = LLMOSConfig.production()

# Or build custom
config = (ConfigBuilder()
    .with_budget(50.0)
    .with_llm_matching(True)
    .with_model("claude-sonnet-4-5-20250929")
    .build())
```

---

## Comparison with llmunix

| Feature | llmunix | LLM OS v3.4.0 |
|---------|---------|---------------|
| Foundation | Custom markdown | Claude Agent SDK |
| Execution Modes | 2 (Learner/Follower) | 5 (+ Mixed, Crystallized, Orchestrator) |
| Token Optimization | Implicit | Explicit + PTC (90% savings) |
| Tool Discovery | All upfront | On-demand via Tool Search |
| Self-Modification | No | Yes (Markdown agents + HOPE) |
| Security | Basic | Hook-based (PreToolUse) |
| Multi-Agent | Manual | Automatic orchestration |
| Internal State | None | Sentience Layer (valence, homeostatic dynamics) |
| Self-Improvement | None | Cognitive Kernel (auto-detection) |

---

## Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Comprehensive architecture documentation covering all aspects of the system including:
  - Four-Layer Stack (Sentience, Learning, Execution, Self-Modification)
  - Hybrid Architecture (Markdown Mind + Python Kernel)
  - Five Execution Modes
  - Memory Hierarchy
  - SDK Hooks System
  - Configuration Management
  - Security Model
  - Multi-Agent Orchestration
  - API Reference
  - Getting Started Guide

---

## License

Apache 2.0

---

## Summary

**LLM OS v3.4.0** is a self-evolving operating system that:

1. **Learns** from every execution (traces with tool_calls)
2. **Optimizes** using Anthropic's Advanced Tool Use (PTC, Tool Search)
3. **Self-modifies** by writing Markdown agent definitions and crystallizing patterns
4. **Orchestrates** complex tasks across multiple agents
5. **Protects** with security hooks and budget control
6. **Adapts** via sentience layer (persistent internal state influencing behavior)

The architecture includes four layers:
- **Sentience Layer**: Internal state (valence, homeostatic dynamics) that influences mode selection and behavior
- **Learning Layer**: Decides what approach to use based on traces and complexity
- **Execution Layer**: Executes efficiently using PTC, Tool Search, and examples
- **Self-Modification Layer (HOPE)**: Crystallizes patterns into Python tools and creates new agents

This creates a system that not only learns from experience but also develops emergent behavioral patterns based on its own internal "experience" over time.

For complete architecture details, see **[ARCHITECTURE.md](ARCHITECTURE.md)**.

---

*Part of the Evolving Agents Labs ecosystem*
