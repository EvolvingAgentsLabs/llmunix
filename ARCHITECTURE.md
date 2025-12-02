# LLM OS Architecture

**Version 3.4.0**

---

## Overview

LLM OS is built on a simple premise: treat the LLM as a CPU that can learn and remember.

Two innovations make this work:

1. **Sentience Layer** - Internal state that persists and influences behavior
2. **Learning Layer** - Traces that enable free replay of learned patterns

---

## The Four Layers

```
┌─────────────────────────────────────────┐
│  SENTIENCE    "How do I feel?"          │  ← Internal state
├─────────────────────────────────────────┤
│  LEARNING     "Have I done this?"       │  ← Pattern matching
├─────────────────────────────────────────┤
│  EXECUTION    "Do it efficiently"       │  ← Tool calling
├─────────────────────────────────────────┤
│  EVOLUTION    "Can I improve?"          │  ← Self-modification
└─────────────────────────────────────────┘
         ↑_______feedback________↓
```

---

## 1. Sentience Layer

The system maintains four continuous variables (-1.0 to +1.0):

| Variable | Meaning | Effect when low | Effect when high |
|----------|---------|-----------------|------------------|
| **Safety** | Trust in environment | Extra caution, confirmations | Risk tolerance |
| **Curiosity** | Novelty drive | Task-focused, efficient | Exploratory, creative |
| **Energy** | Resource availability | Prefer cheap modes | Allow expensive ops |
| **Confidence** | Self-efficacy | Conservative choices | Bold approaches |

### Behavioral Modes

These variables combine into emergent modes:

| Mode | Trigger | Behavior |
|------|---------|----------|
| **Auto-Creative** | High curiosity + confidence | Explores, suggests improvements |
| **Auto-Contained** | Low curiosity | Efficient, stays on task |
| **Recovery** | Low energy | Uses FOLLOWER/CRYSTALLIZED when possible |
| **Cautious** | Low safety | Requests confirmation, avoids risk |

### Homeostasis

Each variable has a set-point. The system naturally drifts toward equilibrium:

```python
# Curiosity example
set_point = 0.0
current = -0.4  # bored from repetition

# System slowly restores toward set_point
# Meanwhile, low curiosity triggers: "Consider suggesting improvements"
```

### Triggers

Events update internal state:

| Event | Effect |
|-------|--------|
| Task success | +confidence, -energy (small) |
| Task failure | -confidence, -safety, -energy |
| Repetition | -curiosity |
| Novel task | +curiosity, -confidence (small) |
| High cost | -energy |

---

## 2. Learning Layer

### Traces

Every successful execution creates a trace:

```yaml
goal_signature: a7f3c9e1
goal_text: "Create a Python calculator"
success_rate: 0.95
usage_count: 7
tool_calls:
  - name: Write
    args: {path: "calc.py", content: "..."}
  - name: Bash
    args: {command: "python calc.py"}
```

### Execution Modes

| Mode | When | Cost | LLM calls |
|------|------|------|-----------|
| **CRYSTALLIZED** | 5+ uses, 95%+ success | $0.00 | 0 |
| **FOLLOWER** | >92% trace match | ~$0.00 | 0 |
| **MIXED** | 75-92% match | ~$0.25 | 1 (reduced) |
| **LEARNER** | Novel task | ~$0.50 | 1+ (full) |
| **ORCHESTRATOR** | Multi-step | Variable | Multiple |

### Semantic Matching

Goals match semantically, not literally:

```
"Create a Python calculator"
"Build a calculator in Python"
"Make a calc tool using python"
→ All match the same trace
```

---

## 3. Execution Layer

### Programmatic Tool Calling (PTC)

In FOLLOWER mode, tool calls execute **outside** the LLM context:

```
User: "Create calculator"
  → Dispatcher finds 98% match
  → PTC replays: Write(calc.py) → Bash(python calc.py)
  → Done. LLM never called.
```

### Tool Search

Instead of loading 100 tools into context, discover on-demand:

```python
# Start with one meta-tool
search_tools("file operations")
# → Returns: Write, Read, Glob (3 tools, not 100)
```

---

## 4. Evolution Layer (HOPE)

### Crystallization

Patterns that work become Python functions:

```
Pattern used 5 times with 95% success
→ Auto-generates: plugins/generated/create_calculator.py
→ Future calls: instant Python execution, $0
```

### Agent Creation

The system can create new agents:

```
User: "Create a haiku poet agent"
→ System writes: workspace/agents/haiku-poet.md
→ Agent available immediately (hot-reload)
```

---

## Hybrid Architecture

```
Markdown Mind              Python Kernel
(workspace/)               (llmos/)
─────────────              ─────────────
agents/*.md          ←→    agent_loader.py
memories/traces/     ←→    traces_sdk.py
state/sentience.json ←→    sentience.py

Benefits:
- Markdown: Human-readable, git-friendly, self-modifiable
- Python: Type-safe, fast, secure
```

---

## Memory Hierarchy

| Level | Storage | Purpose |
|-------|---------|---------|
| L1 | LLM context | Current conversation |
| L2 | Session files | Recent interactions |
| L3 | Trace files | Execution patterns |
| L4 | Facts files | Long-term knowledge |

---

## Security

Hooks intercept tool calls:

```python
@pre_tool_use
def security_check(tool_name, args):
    if "rm -rf" in args.get("command", ""):
        return BLOCK
    return ALLOW
```

Built-in protections:
- Destructive commands blocked
- Budget limits enforced
- Path restrictions
- Safety bounds (robotics)

---

## Configuration

```python
from llmos.kernel.config import LLMOSConfig

# Development
config = LLMOSConfig.development()

# Production
config = LLMOSConfig.production()

# Custom
config = LLMOSConfig(
    budget_usd=50.0,
    sentience_enabled=True,
    auto_crystallization=True
)
```

---

## API

```python
from llmos.boot import LLMOS

os = LLMOS(budget_usd=10.0)
await os.boot()

result = await os.execute("Create a Python calculator")

await os.shutdown()
```

---

## Edge Runtime

Deploy without cloud:

```bash
# Deterministic (no LLM)
python edge_runtime/run_follower.py

# Local LLM (Ollama)
python edge_runtime/run_agentic_follower.py
```

---

*See [README.md](README.md) for quick start.*
