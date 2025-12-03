# LLM OS Architecture

**Version 3.5.0**

---

## Overview

LLM OS is built on a simple premise: treat the LLM as a CPU that can learn and remember.

Three innovations make this work:

1. **Sentience Layer** - Internal state that persists and influences behavior
2. **Learning Layer** - Traces that enable free replay of learned patterns
3. **Adaptive Agents** - Subagents that evolve per-query based on state and memory

---

## The Five Layers

```
┌─────────────────────────────────────────┐
│  SENTIENCE    "How do I feel?"          │  ← Internal state
├─────────────────────────────────────────┤
│  ADAPTATION   "Who should handle this?" │  ← Dynamic agent selection
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

## 2. Adaptation Layer (Dynamic Agent Manager)

The Adaptation Layer dynamically configures agents per-query based on multiple factors:

### Six Adaptation Strategies

| Strategy | Input | Output |
|----------|-------|--------|
| **Sentience-Driven** | Curiosity, safety, energy | Add/remove tools, modify prompts |
| **Trace-Driven** | Failure patterns | New constraints, warnings |
| **Memory-Guided** | Past performance | Best agent selection |
| **Model Selection** | Task complexity | haiku/sonnet/opus |
| **Prompt Enhancement** | Successful traces | Few-shot examples |
| **Agent Evolution** | Accumulated metrics | Evolved agent version |

### How It Works

```
Goal arrives
    ↓
┌─────────────────────────────────────────────────┐
│ DynamicAgentManager.get_adapted_agent()         │
│                                                 │
│  1. Get sentience state (curiosity, safety)     │
│  2. Get similar traces from memory              │
│  3. Adapt for sentience                         │
│     - High curiosity → add exploration tools    │
│     - Low safety → remove dangerous tools       │
│     - Low energy → add conservation guidance    │
│  4. Adapt from memory                           │
│     - Add warnings from failed traces           │
│     - Add successful tool patterns              │
│  5. Select optimal model                        │
│     - Simple + high success → haiku             │
│     - Complex/creative → opus                   │
│     - Default → sonnet                          │
│  6. Enhance with examples                       │
│     - Inject successful traces as few-shot      │
└─────────────────────────────────────────────────┘
    ↓
Adapted AgentSpec → AgentDefinition → Claude SDK
```

### Sentience → Agent Behavior Mapping

| Sentience State | Agent Adaptation |
|-----------------|------------------|
| High curiosity (AUTO_CREATIVE) | Adds WebFetch, WebSearch, Glob; encourages exploration |
| Low curiosity (AUTO_CONTAINED) | Reduces to essential tools; focus mode guidance |
| Low safety (CAUTIOUS) | Removes Bash, Write, Edit; adds confirmation constraints |
| Low energy (RECOVERY) | Adds energy conservation guidance |
| Low confidence | Adds verification guidance, breaks into smaller steps |

### Agent Evolution

After sufficient executions (default: 5+), agents can be evolved based on patterns:

```python
# Automatic evolution triggers
if failure_rate > 30%:
    evolved_agent = manager.analyze_and_evolve_agent("researcher")
    # Adds constraints from failure patterns
    # Updates tools based on success sequences
    # Enhances prompt with lessons learned
```

### Integration with Claude SDK

The adapted agents are registered as subagents with the SDK:

```python
AgentDefinition(
    description="Expert researcher (adapted for current goal)",
    prompt=adapted_prompt,  # Includes sentience guidance, examples
    tools=adapted_tools,    # Modified based on state
    model=selected_model    # haiku/sonnet/opus based on complexity
)
```

---

## 3. Learning Layer

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

| Mode | When | Tokens | LLM Calls |
|------|------|--------|-----------|
| **CRYSTALLIZED** | 5+ uses, 95%+ success | 0 | 0 |
| **FOLLOWER** | >92% trace match | 0 | 0 |
| **MIXED** | 75-92% match | ~1,000 | 1 (reduced) |
| **LEARNER** | Novel task | ~2,500 | 1+ (full) |
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

## 4. Execution Layer

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

## 5. Evolution Layer (HOPE)

### Crystallization

Patterns that work become Python functions:

```
Pattern used 5 times with 95% success
→ Auto-generates: plugins/generated/create_calculator.py
→ Future calls: instant Python execution, 0 tokens
```

### Agent Creation

The system can create new agents:

```
User: "Create a haiku poet agent"
→ System writes: workspace/agents/haiku-poet.md
→ Agent available immediately (hot-reload)
```

---

## Complete Data Flow

```
User Goal: "Research AI trends"
    │
    ├─[1. Sentience Layer]──────────────────────────────────┐
    │   curiosity=0.3, safety=0.5, energy=0.8               │
    │   latent_mode=AUTO_CREATIVE                           │
    │                                                       ↓
    ├─[2. Adaptation Layer]─────────────────────────────────┤
    │   DynamicAgentManager:                                │
    │   ├─ Select agent: "researcher" (best for research)   │
    │   ├─ Adapt tools: +WebSearch (high curiosity)         │
    │   ├─ Select model: sonnet (research task)             │
    │   └─ Enhance: add 3 successful examples               │
    │                                                       ↓
    ├─[3. Learning Layer]───────────────────────────────────┤
    │   Check traces: no match (novel task)                 │
    │   Mode: LEARNER                                       │
    │                                                       ↓
    ├─[4. Execution Layer]──────────────────────────────────┤
    │   Execute via Claude SDK with adapted agent           │
    │   Tools: WebSearch, WebFetch, Read, Write             │
    │   Trace captured for future replay                    │
    │                                                       ↓
    └─[5. Evolution Layer]──────────────────────────────────┤
        Record execution metrics                            │
        Update agent performance (success=1)                │
        If 5+ uses: crystallize into Python function        │
        └───────────────────────────────────────────────────┘
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
    sentience_enabled=True,
    auto_crystallization=True
)
```

---

## API

### Core Usage

```python
from llmos.boot import LLMOS

os = LLMOS()
await os.boot()

result = await os.execute("Create a Python calculator")

await os.shutdown()
```

### Dynamic Agent Management

```python
from llmos.interfaces.dispatcher import Dispatcher

# Get adaptation statistics
stats = dispatcher.get_dynamic_agent_stats()
print(f"Total adaptations: {stats['adaptation_summary']['total_adaptations']}")
print(f"By type: {stats['adaptation_summary']['by_type']}")

# Manually trigger agent evolution
evolved = dispatcher.trigger_agent_evolution("researcher", force=True)
if evolved:
    print(f"Evolved to version {evolved.version}")

# Connect sentience for state-driven adaptation
dispatcher.set_sentience_manager(sentience_manager)
dispatcher.set_agent_factory(agent_factory)
```

### DynamicAgentManager Direct Usage

```python
from llmos.kernel.dynamic_agents import DynamicAgentManager

manager = DynamicAgentManager(
    agent_factory=factory,
    workspace=workspace,
    sentience_manager=sentience_manager,
    trace_manager=trace_manager
)

# Get adapted agent for specific goal
adapted = manager.get_adapted_agent(
    agent_name="researcher",
    goal="Research quantum computing trends"
)

# Record execution results for learning
manager.record_execution_result(
    agent_name="researcher",
    goal="Research quantum computing",
    success=True,
    tokens_used=2500,
    time_secs=12.5
)

# Get performance metrics
metrics = manager.get_agent_metrics_summary()
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
