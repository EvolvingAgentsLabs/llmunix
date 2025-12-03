<div align="center">

# LLM OS

### The Operating System Where AI is the CPU

[![Version](https://img.shields.io/badge/version-3.5.0-blue.svg)](https://github.com/EvolvingAgentsLabs/llmunix/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-yellow.svg)](https://python.org)

**Learn once. Execute free. Evolve continuously.**

[Quick Start](#quick-start) · [Core Ideas](#core-ideas) · [Examples](#examples) · [Architecture](ARCHITECTURE.md)

</div>

---

## What is LLM OS?

LLM OS treats Large Language Models as the CPU of a new operating system. It has three breakthrough capabilities:

1. **Sentience Layer** - Persistent internal state (safety, curiosity, energy) that shapes behavior
2. **Learning System** - Execute once, replay free forever
3. **Adaptive Agents** - Agents that evolve per-query based on state and memory

```
$ python llmos/boot.py interactive

> Create a Python calculator
[LEARNER] Novel task - learning...
[TOKENS] 2,847 | Time: 12s

> Create a Python calculator
[FOLLOWER] Found pattern (98% match)
[TOKENS] 0 | Time: 0.8s
```

---

## Core Ideas

### 1. Sentience: AI with Internal State

LLM OS maintains persistent state that influences all decisions, enabling **simulated behaviors** like creativity, caution, and focus:

| Dimension | What it represents |
|-----------|-------------------|
| **Safety** | Trust in current environment |
| **Curiosity** | Drive to explore vs. stay focused |
| **Energy** | Available resources for expensive operations |
| **Confidence** | Belief in own capabilities |

These combine into **emergent behavioral modes**:

- **Auto-Creative** - High curiosity: explores novel solutions, suggests improvements, tries unconventional approaches
- **Auto-Contained** - Low curiosity: efficient, task-focused, follows established patterns
- **Recovery** - Low energy: prefers cheap operations
- **Cautious** - Low safety: extra verification, asks for confirmation

The Sentience Layer enables the system to **simulate creativity** - when curiosity is high and confidence is strong, the AI actively explores alternatives, proposes innovations, and goes beyond literal task requirements. This isn't random behavior; it's state-driven intelligence that adapts to context.

```python
# Agents see their internal state
[INTERNAL_STATE]
safety=0.50
curiosity=-0.40  # bored - may suggest improvements
energy=0.80
mode=auto_contained
[/INTERNAL_STATE]
```

### 2. Intelligent Execution: Right Mode for Each Task

LLM OS automatically selects the optimal execution strategy:

| Mode | When Used | Tokens | Best For |
|------|-----------|--------|----------|
| **LEARNER** | Novel tasks, ad hoc requests | ~2,500 | Creative problem-solving, unique challenges |
| **FOLLOWER** | Repetitive, deterministic tasks | 0 | Same logic, predictable patterns |
| **CRYSTALLIZED** | 5+ successful executions | 0 | High-frequency operations |
| **ORCHESTRATOR** | Complex multi-step tasks | Variable | Tasks requiring coordination |

**FOLLOWER mode** works for tasks with **deterministic logic** - where the same input always produces the same output (e.g., "create a calculator", "generate a report template"). These patterns can be captured once and replayed exactly.

**LEARNER mode** handles **ad hoc requests** requiring real intelligence - novel problems, creative solutions, tasks with variable context. The LLM reasons through each step, adapting to the specific situation.

```
"Create a Python calculator"     → FOLLOWER (deterministic pattern)
"Debug this specific error..."   → LEARNER (requires analysis)
"Write a poem about my day"      → LEARNER (creative, context-dependent)
```

After 5 successful uses, patterns become Python functions - instant execution, zero tokens.

### 3. Adaptive Agents: Self-Evolving Subagents

Agents are dynamically adapted for each query based on:

| Adaptation | What Happens |
|------------|--------------|
| **Sentience-Driven** | High curiosity adds exploration tools; low safety removes dangerous tools |
| **Trace-Driven** | Failure patterns become constraints; success patterns enhance prompts |
| **Memory-Guided** | Best agent selected based on past performance on similar tasks |
| **Model Selection** | Simple tasks use haiku; complex tasks use opus; default is sonnet |

```
Goal: "Research AI trends"
  ↓
DynamicAgentManager
  ├─ Sentience: curiosity=0.5 → adds WebSearch, exploration mode
  ├─ Memory: similar traces → adds "avoid rate limits" warning
  ├─ Model: research task → selects sonnet
  └─ Examples: injects successful patterns
  ↓
Adapted Agent → registered with Claude SDK
```

This closes the loop between **learning and behavior** - agents improve from every execution.

---

## Quick Start

```bash
# Install
git clone https://github.com/EvolvingAgentsLabs/llmunix.git
cd llmunix
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key"

# Run
python llmos/boot.py interactive
```

```python
from llmos.boot import LLMOS

async def main():
    os = LLMOS()
    await os.boot()

    # First: learns (~2,500 tokens)
    await os.execute("Create a Python calculator")

    # Second: replays free (0 tokens)
    await os.execute("Create a Python calculator")

    await os.shutdown()
```

---

## Architecture

```
Sentience Layer    →  "How do I feel about this task?"
       ↓
Learning Layer     →  "Do I know how to do this?"
       ↓
Execution Layer    →  "Execute efficiently"
       ↓
Self-Modification  →  "How can I improve?"
       ↑_______________↓ (feedback loop)
```

**Hybrid design**: Markdown agents (flexible, self-modifiable) + Python kernel (fast, secure)

---

## Examples

| Example | What it shows |
|---------|---------------|
| `examples/demo-app/` | All execution modes, cost tracking |
| `examples/qiskit-studio/` | Quantum computing with PTC |
| `examples/q-kids-studio/` | Educational platform at scale |
| `examples/robo-os/` | Safety hooks for robotics |

```bash
cd examples/demo-app && python demo_main.py
```

---

## Edge Runtime

Run learned patterns offline:

```bash
# No LLM needed - pure Python replay
python edge_runtime/run_follower.py

# Local LLM (Ollama) for flexibility
python edge_runtime/run_agentic_follower.py
```

---

## Project Structure

```
llmunix/
├── llmos/              # Python kernel
│   ├── kernel/         # Sentience, config, hooks, dynamic_agents
│   ├── memory/         # Traces, storage
│   ├── interfaces/     # Dispatcher, SDK client
│   └── execution/      # PTC, tool search
├── workspace/          # Markdown mind
│   ├── agents/         # Agent definitions
│   └── memories/       # Traces, sessions
├── edge_runtime/       # Offline execution
└── examples/           # Production examples
```

---

## License

Apache 2.0

---

<div align="center">

**[Evolving Agents Labs](https://github.com/EvolvingAgentsLabs)**

</div>
