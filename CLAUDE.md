# LLM-OS: Self-Evolving LLM Operating System

> A Self-Modifying LLM Operating System with Learning, Execution Optimization, and Sentience-Like Architecture

**Current Version**: 3.4.0 (Sentience Layer)

---

## Framework Philosophy

LLM-OS treats Large Language Models as the **CPU** of a new kind of operating system. The system implements a unique **Four-Layer Stack** that enables sentience-aware, self-evolving AI systems:

```
┌─────────────────────────────────────────────────────────────────┐
│                    SENTIENCE LAYER (Awareness)                  │
│  ValenceVector, CognitiveKernel, LatentModes                    │
│  Purpose: "What is my current internal state?"                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    LEARNING LAYER (Intelligence)                │
│  TraceManager, ModeStrategies, Semantic Matching                │
│  Purpose: "What's the BEST approach for this scenario?"         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   EXECUTION LAYER (Efficiency)                  │
│  PTC Executor, Tool Search, Tool Examples                       │
│  Purpose: "How to execute this pattern EFFICIENTLY?"            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│               SELF-MODIFICATION LAYER (Evolution)               │
│  Crystallization, Agent Creation, Capability Growth             │
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

LLM-OS automatically selects the optimal execution mode based on the Learning Layer's analysis:

| Mode | When Used | Tokens | Execution Layer |
|------|-----------|--------|-----------------|
| **CRYSTALLIZED** | Pattern used 5+ times, 95%+ success | 0 | Python execution |
| **FOLLOWER** | Very similar trace found (>92% confidence) | 0 | PTC (tool replay) |
| **MIXED** | Related trace found (75-92% confidence) | ~1,000 | Tool Examples + LLM |
| **LEARNER** | Novel scenario, no relevant traces | ~2,500 | Tool Search + Full LLM |
| **ORCHESTRATOR** | Complex task requiring multiple agents | Variable | Multi-agent coordination |

### Mode Flow Example

```
User: "Create a Python calculator"

1. LEARNER MODE (First time)
   - Learning Layer: "No matching trace found"
   - Execution Layer: Tool Search discovers needed tools
   - Tokens: ~2,500

2. FOLLOWER MODE (Second time)
   - Learning Layer: "Found trace with 98% confidence"
   - Execution Layer: PTC replays tool sequence (zero context!)
   - Tokens: 0

3. CRYSTALLIZED MODE (After 5+ successful runs)
   - Pattern crystallized into Python tool
   - Tokens: 0, <1s
```

---

## Quick Start

### Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your API key
export ANTHROPIC_API_KEY="your-key"
```

### Run Interactive Mode

```bash
python llmos/boot.py interactive
```

### Run Single Command

```bash
python llmos/boot.py "Create a Python calculator"
```

### Run Examples

```bash
# Demo app - interactive showcase
cd examples/demo-app
python demo_main.py

# Qiskit Studio - quantum computing
cd examples/qiskit-studio
python demo.py

# Q-Kids Studio - educational
cd examples/q-kids-studio
python demo.py

# RoboOS - robot control with safety hooks
cd examples/robo-os
python demo.py
```

---

## Project Structure

```
llm-os/
├── llmos/                              # Python Kernel (Somatic Layer)
│   ├── boot.py                         # Entry point
│   ├── kernel/                         # Core OS components
│   │   ├── config.py                   # Configuration
│   │   ├── sentience.py                # Sentience Layer
│   │   ├── cognitive_kernel.py         # Cognitive Kernel
│   │   ├── mode_strategies.py          # Mode selection
│   │   ├── agent_loader.py             # Markdown → Runtime bridge
│   │   ├── token_economy.py            # Budget management
│   │   └── hooks.py                    # SDK hooks system
│   ├── memory/                         # Storage layer
│   │   ├── traces_sdk.py               # Execution traces
│   │   └── store_sdk.py                # File-based memory
│   ├── interfaces/                     # Execution interfaces
│   │   ├── dispatcher.py               # Five-mode router
│   │   ├── sdk_client.py               # Claude SDK integration
│   │   └── orchestrator.py             # Multi-agent coordination
│   ├── execution/                      # Execution Layer
│   │   ├── ptc.py                      # Programmatic Tool Calling
│   │   ├── tool_search.py              # On-demand tool discovery
│   │   └── tool_examples.py            # Auto-generated examples
│   └── plugins/                        # Tools
│       ├── system_tools.py             # create_agent, list_agents
│       └── generated/                  # Crystallized tools (HOPE)
│
├── workspace/                          # Markdown Mind (Cognitive Layer)
│   ├── agents/                         # Agent definitions (.md files)
│   ├── memories/                       # Memory storage
│   │   ├── traces/                     # Execution traces
│   │   ├── sessions/                   # Session context
│   │   └── facts/                      # Long-term facts
│   ├── projects/                       # Project workspaces
│   └── state/                          # System state
│       └── sentience.json              # Persisted sentience state
│
├── edge_runtime/                       # Edge/Offline Execution
│   ├── run_follower.py                 # Deterministic execution
│   ├── run_agentic_follower.py         # LLM-powered execution (Granite/Qwen)
│   └── requirements.txt                # Edge dependencies
│
├── examples/                           # Production-ready examples
│   ├── qiskit-studio/                  # Quantum computing backend
│   ├── q-kids-studio/                  # Educational quantum
│   ├── robo-os/                        # Robot control
│   ├── demo-app/                       # Interactive showcase
│   └── EXAMPLES.md                     # Examples guide
│
├── ARCHITECTURE.md                     # Comprehensive architecture docs
├── README.md                           # Quick start guide
├── CLAUDE.md                           # This configuration file
├── requirements.txt                    # Python dependencies
└── .gitignore
```

---

## Key Features

### 1. Sentience Layer (v3.4.0)

Persistent internal state that influences behavior:

```python
# Internal state persists across sessions
state = SentienceState()
state.valence.safety = 0.5        # Current safety level
state.valence.curiosity = -0.4    # Bored from repetition
state.latent_mode                 # AUTO_CONTAINED (emerges from valence)

# Agents see their internal state
# [INTERNAL_STATE]
# safety=0.50
# curiosity=-0.40
# energy=0.80
# latent_mode=auto_contained
# [/INTERNAL_STATE]
```

**Latent Modes** emerge from valence:
- **AUTO_CREATIVE**: High curiosity + confidence -> exploratory behavior
- **AUTO_CONTAINED**: Low curiosity -> conservative, task-focused
- **RECOVERY**: Low energy/safety -> prefer cheap modes
- **CAUTIOUS**: Low safety -> stricter verification

### 2. Programmatic Tool Calling (PTC)

Execute tool sequences outside the context window for massive token savings:

```python
# When a trace is replayed in FOLLOWER mode:
# - Tool calls execute in a container
# - Results DON'T hit the context window
# - 90%+ token savings vs traditional execution
```

### 3. Tool Search Engine

On-demand tool discovery instead of loading all tools upfront:

```python
# Instead of loading 100+ tools into context:
# - Start with search_tools meta-tool
# - Claude discovers tools as needed
# - 85-90% context reduction
```

### 4. Self-Modification (HOPE)

The system can create and modify its own agents:

```python
await os.execute("Create a haiku-poet agent that writes beautiful haikus")
# Result: workspace/agents/haiku-poet.md is created
# Agent is immediately available, no restart needed!
```

### 5. Token Economy

Explicit token tracking with hooks:

```python
economy = TokenEconomy()
economy.track_tokens(2500, "Learn: Create script")  # Track consumption
economy.get_total_tokens()  # Total tokens used
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

---

## Edge Runtime

LLM-OS includes an edge runtime for offline/edge deployment in `edge_runtime/`:

### Deterministic Follower (No LLM)

```bash
python edge_runtime/run_follower.py
```

Executes pre-learned traces deterministically:
- Tokens: 0
- Speed: 0.01-0.1s
- Requires: PyYAML only

### Agentic Follower (Local LLM)

```bash
python edge_runtime/run_agentic_follower.py
```

Executes with local LLM reasoning (Granite/Qwen via Ollama):
- Tokens: 0 (local model)
- Speed: 0.5-3s
- Adapts to variations

---

## Configuration

### Presets

```python
from kernel.config import LLMOSConfig

# Development - fast iteration
config = LLMOSConfig.development()
# - Sentience enabled, auto-improvement disabled

# Production - full features
config = LLMOSConfig.production()
# - Full sentience with auto-improvement
# - Auto-crystallization enabled

# Testing - deterministic
config = LLMOSConfig.testing()
# - Sentience disabled
```

### Environment Variables

```bash
ANTHROPIC_API_KEY=your-key
LLMOS_WORKSPACE=/path/to/workspace
```

---

## Memory Hierarchy

LLM-OS implements a four-level memory system:

| Level | Name | Storage | Purpose |
|-------|------|---------|---------|
| L1 | Context | In LLM | Current conversation |
| L2 | Short-term | Session logs | Recent interactions |
| L3 | Procedural | Markdown traces | Execution patterns |
| L4 | Semantic | File-based | Facts, insights |

### Execution Traces

Traces are stored as Markdown files with YAML frontmatter:

```markdown
---
goal_signature: a3f7c9e1b2d4f8a6
goal_text: Create a Python script to calculate primes
success_rating: 0.92
usage_count: 15
---

## Execution Steps

### Step 1: Write primes.py
Tool: Write
...

## Tool Calls (PTC)
```json
[
  {"name": "Write", "arguments": {"path": "primes.py", "content": "..."}},
  {"name": "Bash", "arguments": {"command": "python primes.py"}}
]
```
```

---

## Agent Definitions

Agents are defined as Markdown files in `workspace/agents/`:

```markdown
---
name: researcher
description: Expert at web research and data synthesis
tools: ["WebFetch", "Read", "Write"]
model: sonnet
---

# Researcher Agent

You are an expert researcher...
[System prompt instructions]
```

The system can:
- Load agents at runtime (hot-reload)
- Create new agents dynamically
- Modify existing agents
- All changes are version-controllable

---

## SDK Hooks System

Automatic hooks for safety and efficiency:

| Hook | Purpose |
|------|---------|
| **Security** | Blocks dangerous commands |
| **Trace** | Captures tool_calls for PTC |
| **Tokens** | Real-time token monitoring |
| **Memory** | Injects relevant context |
| **Sentience** | Injects internal state |

---

## API Reference

### LLMOS Core

```python
from llmos.boot import LLMOS

# Initialize
os = LLMOS()

# Boot
await os.boot()

# Execute
result = await os.execute(
    goal="Create a Python calculator",
    mode="AUTO"  # or "LEARNER", "FOLLOWER", "ORCHESTRATOR"
)

# Shutdown
await os.shutdown()
```

### Dispatcher

```python
from interfaces.dispatcher import Dispatcher

# Get stats
stats = dispatcher.get_execution_layer_stats()

# Search tools
tools = await dispatcher.search_tools("file operations")

# Dispatch
result = await dispatcher.dispatch(goal="Analyze data", mode="AUTO")
```

---

## Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Comprehensive architecture documentation
- **[README.md](README.md)** - Quick start guide with diagrams
- **[examples/EXAMPLES.md](examples/EXAMPLES.md)** - Examples guide

---

## Version History

| Version | Highlights |
|---------|------------|
| **3.4.0** | Sentience Layer, CognitiveKernel, auto-creative/auto-contained modes |
| 3.3.0 | Advanced Tool Use (PTC, Tool Search, Tool Examples) |
| 3.2.0 | Hybrid Architecture (Markdown agents + Python kernel) |
| 3.0.0 | HOPE - Self-modifying kernel with crystallization |
| 2.5.0 | SDK hooks, streaming, nested learning |
| 2.0.0 | Multi-agent orchestration, project management |
| 1.0.0 | Learner-Follower pattern (cost optimization) |

---

## License

Apache 2.0

---

*Part of the Evolving Agents Labs ecosystem*
