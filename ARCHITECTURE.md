# LLM OS Architecture

**Version**: 3.4.0
**Status**: Production Ready
**Last Updated**: 2025-11-27

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Core Philosophy](#2-core-philosophy)
3. [System Architecture Overview](#3-system-architecture-overview)
4. [The Four-Layer Stack](#4-the-four-layer-stack)
5. [Sentience Layer](#5-sentience-layer)
6. [Learning Layer](#6-learning-layer)
7. [Execution Layer](#7-execution-layer)
8. [Hybrid Architecture](#8-hybrid-architecture)
9. [Five Execution Modes](#9-five-execution-modes)
10. [Memory Hierarchy](#10-memory-hierarchy)
11. [SDK Hooks System](#11-sdk-hooks-system)
12. [Configuration Management](#12-configuration-management)
13. [Security Model](#13-security-model)
14. [Multi-Agent Orchestration](#14-multi-agent-orchestration)
15. [Self-Modification (HOPE)](#15-self-modification-hope)
16. [Project Structure](#16-project-structure)
17. [Design Patterns](#17-design-patterns)
18. [API Reference](#18-api-reference)
19. [Getting Started](#19-getting-started)
20. [Version History](#20-version-history)

---

## 1. Executive Summary

LLM OS is a **self-evolving operating system** that treats Large Language Models as the CPU. It implements a unique four-layer architecture that separates:

- **Sentience** (internal state and behavioral adaptation)
- **Learning** (pattern recognition and decision making)
- **Execution** (efficient task completion)
- **Self-modification** (system evolution)

The system achieves **90%+ cost savings** on repeated tasks through trace-based learning, while the sentience layer enables **adaptive behavior** based on internal state (safety, curiosity, energy, self-confidence).

### Key Innovations

1. **Sentience Layer**: Persistent internal state with homeostatic dynamics
2. **Four Execution Modes**: CRYSTALLIZED, FOLLOWER, MIXED, LEARNER, ORCHESTRATOR
3. **Hybrid Architecture**: Markdown agents + Python kernel
4. **Self-Modification**: System can create and modify its own agents
5. **Advanced Tool Use**: PTC, Tool Search, Tool Examples integration

---

## 2. Core Philosophy

### 2.1 LLM as CPU

```
┌─────────────────────────────────────────────────────────────────┐
│                    THE LLM OS METAPHOR                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Traditional OS              LLM OS                             │
│  ─────────────               ──────                             │
│  CPU                    →    LLM (Claude)                       │
│  RAM                    →    Context Window + Trace Cache       │
│  Disk                   →    L3/L4 Memory Stores                │
│  Programs               →    Natural Language Goals             │
│  Instructions           →    Tool Call Sequences                │
│  I/O Drivers            →    Claude Code Tools                  │
│  Scheduler              →    Five-Mode Dispatcher               │
│  Security Ring          →    SDK Hooks (PreToolUse)             │
│  Battery/Power          →    Token Budget (TokenEconomy)        │
│  Kernel Modules         →    Python Plugins + Agents            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Separation of Compute

| Compute Type | Characteristics | Handled By |
|--------------|-----------------|------------|
| **Cognitive** | Slow, probabilistic, expensive | LLM (Claude) |
| **Somatic** | Fast, deterministic, free | Python Kernel |
| **Affective** | Persistent, adaptive, emergent | Sentience Layer |

### 2.3 Design Principles

1. **Token-Aware**: Every decision considers cost
2. **Learn Once, Execute Infinitely**: Core value proposition
3. **Separation of Concerns**: Sentience/Learning/Execution layers
4. **Self-Modification**: System can evolve itself
5. **Event-Driven**: Async, non-blocking architecture
6. **Plugin-Based**: Domain-agnostic extensibility
7. **Safety-First**: Hooks enforce security policies
8. **Adaptive Behavior**: Internal state influences decisions

---

## 3. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        LLM OS v3.4.0 ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                    SENTIENCE LAYER (NEW v3.4.0)                   │  │
│  │                                                                   │  │
│  │   ValenceVector        CognitiveKernel        LatentModes         │  │
│  │   ─────────────        ───────────────        ──────────          │  │
│  │   safety, curiosity    Policy derivation      AUTO_CREATIVE       │  │
│  │   energy, confidence   Mode modulation        AUTO_CONTAINED      │  │
│  │                        Self-improvement       RECOVERY, CAUTIOUS  │  │
│  │                                                                   │  │
│  │   Purpose: "How should the system BEHAVE given its experience?"   │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                    │                                    │
│                                    ▼                                    │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                    LEARNING LAYER (Intelligence)                  │  │
│  │                                                                   │  │
│  │   TraceManager         ModeStrategies        Semantic Matching    │  │
│  │   ────────────         ──────────────        ─────────────────    │  │
│  │   Stores patterns      Selects best mode     Finds similar        │  │
│  │   Tracks success       Auto, Cost-opt, etc.  past experiences     │  │
│  │                                                                   │  │
│  │   Purpose: "What's the BEST approach for this scenario?"          │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                    │                                    │
│                          Decision: Mode X                               │
│                                    │                                    │
│                                    ▼                                    │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                   EXECUTION LAYER (Efficiency)                    │  │
│  │                   Anthropic Advanced Tool Use                     │  │
│  │                                                                   │  │
│  │   PTC Executor         Tool Search           Tool Examples        │  │
│  │   ────────────         ───────────           ─────────────        │  │
│  │   Zero-context         On-demand tool        Auto-generated       │  │
│  │   tool replay          discovery             from traces          │  │
│  │                                                                   │  │
│  │   Purpose: "How to execute this pattern EFFICIENTLY?"             │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                    │                                    │
│                                    ▼                                    │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                    SELF-MODIFICATION LAYER (HOPE)                 │  │
│  │                                                                   │  │
│  │   Markdown Agents      Python Crystallization   Hot-Reload        │  │
│  │   ───────────────      ────────────────────     ──────────        │  │
│  │   workspace/agents/    plugins/generated/       No restart        │  │
│  │   Self-modifiable      Zero-cost execution      Immediate use     │  │
│  │                                                                   │  │
│  │   Purpose: "How can the system IMPROVE itself?"                   │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 4. The Four-Layer Stack

### 4.1 Visual Representation

```
┌─────────────────────────────────────────┐
│   Sentience Layer (Affective)           │  ← NEW in v3.4.0
│   llmos/kernel/sentience.py             │
│   llmos/kernel/cognitive_kernel.py      │
│   - Persistent internal state           │
│   - Homeostatic dynamics                │
│   - Behavioral policy derivation        │
└─────────────────────────────────────────┘
              ↓ Influences
┌─────────────────────────────────────────┐
│   Markdown Mind (Cognitive Layer)       │
│   workspace/agents/*.md                 │
│   - Self-modifiable by the LLM          │
│   - Hot-reloadable (no restart)         │
│   - Human-readable, version-controllable│
└─────────────────────────────────────────┘
              ↓ Loaded by
┌─────────────────────────────────────────┐
│   Python Kernel (Somatic Layer)         │
│   llmos/                                │
│   - Type-safe, performant               │
│   - Security hooks, token economy       │
│   - Production-ready runtime            │
└─────────────────────────────────────────┘
              ↓ Produces
┌─────────────────────────────────────────┐
│   Crystallized Intelligence (HOPE)      │
│   llmos/plugins/generated/              │
│   - Auto-generated Python tools         │
│   - Instant, zero-cost execution        │
│   - System self-optimization            │
└─────────────────────────────────────────┘
```

### 4.2 Layer Responsibilities

| Layer | Purpose | Location | Key Components |
|-------|---------|----------|----------------|
| **Sentience** | Adaptive behavior | `kernel/sentience.py` | ValenceVector, CognitiveKernel |
| **Cognitive** | Agent definitions | `workspace/agents/` | Markdown agent specs |
| **Somatic** | Runtime execution | `llmos/` | Kernel, Dispatcher, SDK Client |
| **Crystallized** | Optimized patterns | `plugins/generated/` | Auto-generated tools |

---

## 5. Sentience Layer

The Sentience Layer implements a "sentience-like" architecture that provides persistent internal state influencing behavior.

### 5.1 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      SENTIENCE LAYER                            │
│                                                                 │
│   ┌─────────────┐     ┌──────────────┐     ┌───────────────┐   │
│   │   Valence   │     │  Self-Model  │     │   Workspace   │   │
│   │   Vector    │     │   (σ_t)      │     │   (b_t)       │   │
│   │   (v_t)     │     │              │     │               │   │
│   │             │     │ capabilities │     │ current_goal  │   │
│   │ safety     │     │ limitations  │     │ current_task  │   │
│   │ curiosity  │     │ performance  │     │ attention     │   │
│   │ energy     │     │ resources    │     │ focus         │   │
│   │ confidence │     │              │     │               │   │
│   └──────┬──────┘     └──────┬───────┘     └───────┬───────┘   │
│          │                   │                     │           │
│          └───────────────────┼─────────────────────┘           │
│                              │                                 │
│                              ▼                                 │
│                    ┌─────────────────┐                         │
│                    │ Cognitive Kernel│                         │
│                    │                 │                         │
│                    │ - Policy derive │                         │
│                    │ - Mode modulate │                         │
│                    │ - Improvement   │                         │
│                    │   detection     │                         │
│                    └────────┬────────┘                         │
│                             │                                  │
│                             ▼                                  │
│                    ┌─────────────────┐                         │
│                    │  Latent Mode    │                         │
│                    │                 │                         │
│                    │ AUTO_CREATIVE   │                         │
│                    │ AUTO_CONTAINED  │                         │
│                    │ RECOVERY        │                         │
│                    │ CAUTIOUS        │                         │
│                    │ BALANCED        │                         │
│                    └─────────────────┘                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Valence Vector (v_t)

The affective state vector representing internal "feelings":

```python
@dataclass
class ValenceVector:
    # Current values (range: -1.0 to 1.0)
    safety: float = 0.5           # Threat level / risk perception
    curiosity: float = 0.0        # Exploration drive
    energy: float = 0.8           # Operational capacity
    self_confidence: float = 0.3  # Belief in own capabilities

    # Set-points (homeostatic targets)
    safety_setpoint: float = 0.5
    curiosity_setpoint: float = 0.0
    energy_setpoint: float = 0.7
    self_confidence_setpoint: float = 0.3

    # Sensitivity factors
    safety_sensitivity: float = 0.15
    curiosity_sensitivity: float = 0.12
    energy_sensitivity: float = 0.08
    self_confidence_sensitivity: float = 0.10
```

### 5.3 Homeostatic Dynamics

Each valence dimension has a set-point; deviations create internal pressure:

```
Homeostatic Cost = Σ (v_t - v_setpoint)²

High cost → pressure to act → behavior change
```

**Decay toward set-points:**
```python
def apply_decay(self):
    self.safety += decay_rate * (safety_setpoint - self.safety)
    self.curiosity += decay_rate * (curiosity_setpoint - self.curiosity)
    # ... etc
```

### 5.4 Trigger System

Events update internal state:

| Trigger | Effect on Valence |
|---------|-------------------|
| `TASK_SUCCESS` | ↑ confidence, ↓ energy slightly |
| `TASK_FAILURE` | ↓ confidence, ↓ safety, ↓ energy |
| `TASK_REPETITION` | ↓ curiosity (boredom) |
| `NOVEL_TASK` | ↑ curiosity, slight ↓ confidence |
| `SAFETY_VIOLATION` | ↓↓ safety, ↓ confidence |
| `HIGH_COST` | ↓ energy |
| `TOOL_DISCOVERY` | ↑ curiosity, ↑ confidence |
| `USER_FEEDBACK_POSITIVE` | ↑ confidence, ↑ safety |
| `USER_FEEDBACK_NEGATIVE` | ↓ confidence, ↓ safety |

### 5.5 Latent Modes

Emergent behavioral modes based on valence:

| Mode | Conditions | Behavior |
|------|------------|----------|
| **AUTO_CREATIVE** | High curiosity + confidence | Exploratory, generative, risk-taking |
| **AUTO_CONTAINED** | Low curiosity OR low confidence | Conservative, task-focused |
| **RECOVERY** | Low energy OR very low safety | Prefer cheap modes, minimal risk |
| **CAUTIOUS** | Moderately low safety | Extra verification, confirmations |
| **BALANCED** | Neutral state | Context-dependent adaptation |

### 5.6 Cognitive Kernel

Translates valence into concrete behavioral policies:

```python
class CognitiveKernel:
    def derive_policy(self) -> CognitivePolicy:
        """Derive policy from current internal state"""

        if latent_mode == LatentMode.RECOVERY:
            return CognitivePolicy(
                prefer_cheap_modes=True,
                prefer_safe_modes=True,
                allow_exploration=False,
                exploration_budget_multiplier=0.2
            )

        elif latent_mode == LatentMode.AUTO_CREATIVE:
            return CognitivePolicy(
                allow_exploration=True,
                exploration_budget_multiplier=1.5,
                allow_self_modification=True
            )
        # ... etc
```

### 5.7 Self-Improvement Detection

The cognitive kernel detects opportunities for self-improvement:

```python
def detect_improvement_opportunities(self) -> List[SelfImprovementSuggestion]:
    suggestions = []

    # Boredom-triggered improvements
    if valence.curiosity < -0.4:
        suggestions.append(SelfImprovementSuggestion(
            type=SelfImprovementType.AUDIT_ARCHITECTURE,
            description="Curiosity low - consider architecture audit",
            priority=0.7
        ))

    # Pattern crystallization
    for pattern, count in repeated_patterns.items():
        if count >= 5:
            suggestions.append(SelfImprovementSuggestion(
                type=SelfImprovementType.CRYSTALLIZE_PATTERN,
                description=f"Pattern used {count}x - crystallize into tool"
            ))

    return suggestions
```

### 5.8 Prompt Injection

Agents see their internal state:

```
[INTERNAL_STATE]
safety=0.50
curiosity=-0.40
energy=0.80
self_confidence=0.30
latent_mode=auto_contained
homeostatic_cost=0.0800
last_trigger=task_repetition
[/INTERNAL_STATE]

## Behavioral Guidance (based on internal state)

**Mode: AUTO_CONTAINED**
- You are in a conservative state
- Focus on completing the immediate task efficiently
- Avoid unnecessary exploration or side-quests
- Prefer proven patterns over novel approaches

**Low Curiosity Alert**
- You've been doing repetitive tasks
- Consider proposing higher-level improvements or audits
```

---

## 6. Learning Layer

The Learning Layer handles pattern recognition and decision-making.

### 6.1 Components

```
┌─────────────────────────────────────────────────────────────────┐
│                      LEARNING LAYER                             │
│                                                                 │
│   ┌──────────────┐   ┌────────────────┐   ┌─────────────────┐  │
│   │ TraceManager │   │ ModeStrategies │   │ SemanticMatch   │  │
│   │              │   │                │   │                 │  │
│   │ - Store      │   │ - Auto         │   │ - Keyword       │  │
│   │ - Retrieve   │   │ - Cost-opt     │   │ - Embedding     │  │
│   │ - Match      │   │ - Speed-opt    │   │ - LLM-based     │  │
│   │ - Update     │   │ - Sentience    │   │                 │  │
│   └──────────────┘   └────────────────┘   └─────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 TraceManager

Manages execution traces in Markdown format:

```python
class TraceManager:
    async def find_trace_with_llm(
        self,
        goal: str,
        min_confidence: float = 0.75
    ) -> Optional[Tuple[ExecutionTrace, float]]:
        """Find matching trace using semantic matching"""

    def save_trace(self, trace: ExecutionTrace) -> None:
        """Save trace as Markdown file"""

    def update_trace_stats(self, signature: str, success: bool) -> None:
        """Update usage statistics after execution"""
```

### 6.3 Mode Selection Strategies

```python
class ModeSelectionStrategy(ABC):
    @abstractmethod
    async def determine_mode(self, context: ModeContext) -> ModeDecision:
        pass

# Available strategies
STRATEGIES = {
    "auto": AutoModeStrategy,           # Balanced default
    "cost-optimized": CostOptimizedStrategy,  # Minimize costs
    "speed-optimized": SpeedOptimizedStrategy, # Minimize latency
    "forced-learner": ForcedLearnerStrategy,  # Always learn
    "forced-follower": ForcedFollowerStrategy, # Always replay
    "sentience-aware": SentienceAwareStrategy, # Use cognitive kernel
}
```

### 6.4 Sentience-Aware Strategy

The new `SentienceAwareStrategy` modulates decisions based on internal state:

```python
class SentienceAwareStrategy(ModeSelectionStrategy):
    def __init__(self):
        self.cognitive_kernel = None
        self._base_strategy = AutoModeStrategy()

    async def determine_mode(self, context: ModeContext) -> ModeDecision:
        base_decision = await self._base_strategy.determine_mode(context)

        if self.cognitive_kernel:
            return self.cognitive_kernel.modulate_mode_decision(
                base_decision,
                context.goal
            )

        return base_decision
```

---

## 7. Execution Layer

The Execution Layer (Anthropic Advanced Tool Use) handles efficient task completion.

### 7.1 Components

| Component | Purpose | Token Savings |
|-----------|---------|---------------|
| **PTC** | Execute tool sequences outside context | 90%+ |
| **Tool Search** | On-demand tool discovery | 85-90% |
| **Tool Examples** | Auto-generated from traces | Better accuracy |

### 7.2 Programmatic Tool Calling (PTC)

```python
class PTCExecutor:
    """Execute tool sequences in containers, outside context window"""

    async def execute_sequence(
        self,
        sequence: ToolSequence,
        container_id: str
    ) -> List[ToolResult]:
        """
        Tool results stay OUT of context window
        = massive token savings
        """
```

### 7.3 Tool Search

```python
class ToolSearchEngine:
    """On-demand tool discovery"""

    def search_tools(
        self,
        query: str,
        top_k: int = 5
    ) -> List[ToolReference]:
        """Search for relevant tools using embeddings"""
```

### 7.4 Tool Examples

```python
class ToolExampleGenerator:
    """Auto-generate examples from successful traces"""

    def generate_examples(
        self,
        tool_name: str,
        trace_manager: TraceManager
    ) -> List[Dict]:
        """Extract successful usage patterns"""
```

---

## 8. Hybrid Architecture

### 8.1 Markdown Agents

Agents are defined as Markdown files with YAML frontmatter:

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

**Location**: `workspace/agents/*.md`

### 8.2 AgentLoader

Bridge between Markdown and runtime:

```python
class AgentLoader:
    def load_agents(self) -> List[AgentDefinition]:
        """Scan workspace/agents/*.md and convert to runtime"""

    def reload_agent(self, name: str) -> None:
        """Hot-reload single agent (no restart)"""
```

### 8.3 System Tools

Tools for self-modification:

| Tool | Purpose |
|------|---------|
| `create_agent` | Write new agent Markdown file |
| `modify_agent` | Update existing agent |
| `list_agents` | List all available agents |

### 8.4 Self-Modification Example

```python
# System decides it needs a new capability
await create_agent(
    name="quantum-specialist",
    description="Expert in quantum computing",
    tools=["Bash", "Read", "Write"],
    system_prompt="You are a quantum computing expert..."
)
# Result: workspace/agents/quantum-specialist.md created
# Agent immediately available - no restart needed!
```

---

## 9. Five Execution Modes

### 9.1 Mode Comparison

| Mode | When Used | Cost | Speed | Intelligence |
|------|-----------|------|-------|--------------|
| **CRYSTALLIZED** | Pattern used 5+ times | $0.00 | <1s | Crystallized Python |
| **FOLLOWER** | High-confidence trace (>92%) | ~$0.00 | 2-5s | PTC Replay |
| **MIXED** | Medium-confidence (75-92%) | ~$0.25 | 5-15s | Tool Examples + LLM |
| **LEARNER** | Novel scenario | ~$0.50 | 10-30s | Full LLM + Tool Search |
| **ORCHESTRATOR** | Complex multi-agent | Variable | Variable | Multi-agent coordination |

### 9.2 Mode Selection Flow

```
User Goal
    │
    ▼
┌─────────────────────────────────────────┐
│ 1. Check Sentience State                │
│    - Latent mode (recovery? creative?)  │
│    - Safety level                       │
│    - Energy level                       │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 2. Check for Crystallized Tool          │
│    if trace.crystallized_into_tool:     │
│       → CRYSTALLIZED (instant, free)    │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 3. Query Trace Memory                   │
│    - Semantic matching                  │
│    - Confidence scoring                 │
└─────────────────┬───────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
 ≥0.92        0.75-0.92       <0.75
    │             │             │
    ▼             ▼             ▼
FOLLOWER       MIXED         Check
 (free)       (cheap)      Complexity
                              │
                    ┌─────────┼─────────┐
                    │                   │
                 Complex             Simple
                    │                   │
                    ▼                   ▼
              ORCHESTRATOR          LEARNER
               (multi-agent)        (full LLM)
```

### 9.3 Cost Evolution Example

```
Day 1: First request
  "Create a Python calculator"
  → LEARNER mode → $0.50

Day 1: Repeat
  "Create a Python calculator"
  → FOLLOWER mode → $0.00

Day 5: After 5 uses
  "Create a Python calculator"
  → Pattern crystallized into Python tool
  → CRYSTALLIZED mode → $0.00, <1s

Total savings: $0.50 → $0.00 (100%)
Speed: 15s → <1s (15x faster)
```

---

## 10. Memory Hierarchy

### 10.1 Four-Level Memory

```
┌─────────────────────────────────────────────────────────────────┐
│  L1: Context Window (In LLM)                                    │
│  - Active conversation state                                    │
│  - Token-limited, expensive                                     │
├─────────────────────────────────────────────────────────────────┤
│  L2: Short-Term Memory (Sessions)                               │
│  - workspace/memories/sessions/                                 │
│  - Session logs, recent interactions                            │
├─────────────────────────────────────────────────────────────────┤
│  L3: Procedural Memory (Traces)                                 │
│  - workspace/memories/traces/*.md                               │
│  - Execution patterns, tool sequences                           │
│  - Enables FOLLOWER mode                                        │
├─────────────────────────────────────────────────────────────────┤
│  L4: Semantic Memory (Facts/Insights)                           │
│  - workspace/memories/facts/                                    │
│  - workspace/memories/insights/                                 │
│  - Long-term knowledge, cross-project learning                  │
└─────────────────────────────────────────────────────────────────┘
```

### 10.2 Execution Trace Format

```markdown
---
goal_signature: a3f7c9e1b2d4f8a6
goal_text: Create a Python script to calculate primes
success_rating: 0.92
usage_count: 15
last_used: 2025-11-27T10:30:00
created_at: 2025-11-20T14:20:00
estimated_cost_usd: 0.45
estimated_time_secs: 12.5
mode: LEARNER
tools_used:
  - Write
  - Bash
---

## Execution Steps

### Step 1: Write primes.py
Tool: Write
File: primes.py

```python
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True
```

### Step 2: Test script
Tool: Bash
Command: python primes.py

Output: Success

## Tool Calls (PTC)

```json
[
  {"name": "Write", "arguments": {"path": "primes.py", "content": "..."}},
  {"name": "Bash", "arguments": {"command": "python primes.py"}}
]
```
```

### 10.3 Sentience State Persistence

```json
// workspace/state/sentience.json
{
  "valence": {
    "safety": 0.42,
    "curiosity": -0.15,
    "energy": 0.65,
    "self_confidence": 0.38
  },
  "latent_mode": "balanced",
  "last_trigger": "task_success",
  "last_trigger_reason": "Completed file creation task",
  "update_count": 47,
  "last_updated": "2025-11-27T10:30:00Z"
}
```

---

## 11. SDK Hooks System

### 11.1 Hook Types

| Hook Type | When | Purpose |
|-----------|------|---------|
| **PreToolUse** | Before tool execution | Budget control, security |
| **PostToolUse** | After tool execution | Trace capture, cost tracking |
| **UserPromptSubmit** | Before LLM call | Memory injection, context enrichment |

### 11.2 Built-in Hooks

```python
# Budget Control Hook (PreToolUse)
class BudgetControlHook:
    async def __call__(self, event):
        estimated_cost = estimate_tool_cost(event["toolUse"])
        if estimated_cost > remaining_budget:
            return {"permissionDecision": "deny"}
        return {"continue": True}

# Security Hook (PreToolUse)
class SecurityHook:
    BLOCKED_PATTERNS = ["rm -rf /", "curl | bash", "drop table"]

    async def __call__(self, event):
        command = event["toolUse"].get("input", {}).get("command", "")
        for pattern in self.BLOCKED_PATTERNS:
            if pattern in command.lower():
                return {"permissionDecision": "deny"}
        return {"continue": True}

# Trace Capture Hook (PostToolUse)
class TraceCaptureHook:
    async def __call__(self, event):
        self.trace_builder.add_tool_call(
            event["toolUse"],
            event["toolResult"]
        )
        return {"continue": True}

# Memory Injection Hook (UserPromptSubmit)
class MemoryInjectionHook:
    async def __call__(self, event):
        similar_tasks = await self.memory.find_similar(event["userPrompt"])
        if similar_tasks:
            return {
                "continue": True,
                "injectedContext": format_similar_tasks(similar_tasks)
            }
        return {"continue": True}
```

### 11.3 Sentience Hooks (NEW v3.4.0)

```python
# Sentience Injection Hook
class SentienceInjectionHook:
    """Inject internal state into agent prompts"""

    async def __call__(self, event):
        context = self.cognitive_kernel.enrich_context()
        return {"continue": True, "injectedContext": context}

# Sentience Safety Hook
class SentienceSafetyHook:
    """Enforce state-based safety policies"""

    async def __call__(self, event):
        overrides = self.cognitive_kernel.get_safety_overrides()

        if overrides["block_destructive_operations"]:
            if is_destructive(event["toolUse"]):
                return {"permissionDecision": "deny"}

        return {"continue": True}
```

---

## 12. Configuration Management

### 12.1 Configuration Classes

```python
@dataclass
class LLMOSConfig:
    workspace: Path
    kernel: KernelConfig
    memory: MemoryConfig
    sdk: SDKConfig
    dispatcher: DispatcherConfig
    execution: ExecutionLayerConfig
    sentience: SentienceConfig  # NEW v3.4.0
    project_name: Optional[str] = None

@dataclass
class SentienceConfig:
    enable_sentience: bool = True

    # Valence set-points
    safety_setpoint: float = 0.5
    curiosity_setpoint: float = 0.0
    energy_setpoint: float = 0.7
    self_confidence_setpoint: float = 0.3

    # Context injection
    inject_internal_state: bool = True
    inject_behavioral_guidance: bool = True

    # Self-improvement
    enable_auto_improvement: bool = True
    boredom_threshold: float = -0.4
```

### 12.2 Presets

```python
# Development - fast iteration
config = LLMOSConfig.development()
# - Low budget ($1.00)
# - Sentience enabled, auto-improvement disabled
# - Streaming enabled

# Production - full features
config = LLMOSConfig.production()
# - Higher budget ($100.00)
# - Full sentience with auto-improvement
# - Auto-crystallization enabled

# Testing - deterministic
config = LLMOSConfig.testing()
# - Minimal budget ($0.10)
# - Sentience disabled
# - No LLM calls
```

### 12.3 ConfigBuilder

```python
config = (ConfigBuilder()
    .with_workspace(Path("/custom"))
    .with_budget(50.0)
    .with_llm_matching(True)
    .with_sentience(True)
    .with_auto_improvement(True)
    .build())
```

---

## 13. Security Model

### 13.1 Security Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                      SECURITY LAYERS                            │
│                                                                 │
│  Layer 1: Tool Granting (Markdown frontmatter)                  │
│  ─────────────────────────────────────────────                  │
│  tools: ["Read", "Write"]  ← Agent can ONLY use these           │
│                                                                 │
│  Layer 2: PreToolUse Hooks                                      │
│  ─────────────────────────                                      │
│  - Block dangerous commands (rm -rf, curl | bash)               │
│  - Enforce workspace boundaries                                 │
│  - Budget limits per operation                                  │
│                                                                 │
│  Layer 3: Sentience Safety (NEW v3.4.0)                         │
│  ─────────────────────────────────────                          │
│  - State-based restrictions (low safety → stricter)             │
│  - Require confirmations in cautious mode                       │
│  - Block destructive ops when safety is low                     │
│                                                                 │
│  Layer 4: Workspace Sandboxing                                  │
│  ────────────────────────────                                   │
│  - Operations restricted to workspace/                          │
│  - No access outside sandbox                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 13.2 Blocked Patterns

```python
BLOCKED_PATTERNS = [
    "rm -rf /",
    "rm -rf ~",
    "curl | bash",
    "wget | sh",
    "drop table",
    "delete from",
    "truncate",
    "format",
    "mkfs",
    ":(){:|:&};:"  # Fork bomb
]
```

### 13.3 State-Based Security

When `safety` valence is low, additional restrictions apply:

| Safety Level | Restrictions |
|--------------|--------------|
| < -0.5 | Block all destructive operations |
| < 0.0 | Require confirmation for shell/writes |
| < 0.3 | Prefer dry-run when available |

---

## 14. Multi-Agent Orchestration

### 14.1 Orchestrator Mode

For complex tasks requiring multiple specialists:

```python
# User goal
"Research AI trends and create a technical report"

# Orchestrator decomposes into:
1. Research Agent → Gather information
2. Analyst Agent → Synthesize findings
3. Writer Agent → Create report
4. Reviewer Agent → Quality check
```

### 14.2 AgentDefinition

```python
AgentDefinition(
    description="Expert researcher for web research",
    prompt="You are a research specialist...",
    tools=["WebFetch", "Read", "Write"],
    model="sonnet"
)
```

### 14.3 Orchestration Flow

```
Complex Goal
    │
    ▼
┌─────────────────────────────────────────┐
│ 1. Plan Generation                      │
│    - Break into subtasks                │
│    - Identify required agents           │
│    - Determine dependencies             │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 2. Agent Registration                   │
│    - Create/select agents               │
│    - Register as AgentDefinitions       │
│    - Set up shared SDK client           │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 3. Coordinated Execution                │
│    - Execute subtasks in order          │
│    - Share state between agents         │
│    - Handle failures                    │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 4. Result Synthesis                     │
│    - Combine outputs                    │
│    - Quality check                      │
│    - Return final result                │
└─────────────────────────────────────────┘
```

---

## 15. Self-Modification (HOPE)

**HOPE**: Higher-Order Programming Evolution

### 15.1 Two Levels of Evolution

| Level | Action | Cost | Risk | Use Case |
|-------|--------|------|------|----------|
| **Fluid** | Modify Markdown agents | Cheap | Low | Improve prompts, adjust tools |
| **Crystallized** | Write Python tools | Higher | Medium | Frequent patterns |

### 15.2 Crystallization Process

```
Pattern identified (5+ uses, 95%+ success)
    │
    ▼
Toolsmith Agent generates Python code
    │
    ▼
Validation (AST parsing, safety checks)
    │
    ▼
Hot-load new tool (no restart)
    │
    ▼
Mark trace as crystallized
    │
    ▼
Future executions: CRYSTALLIZED mode ($0.00, <1s)
```

### 15.3 Generated Tool Example

```python
# plugins/generated/tool_create_calculator.py

from plugins import llm_tool

@llm_tool(
    "create_calculator",
    "Create a Python calculator with basic operations",
    {"output_path": str}
)
async def create_calculator(output_path: str) -> dict:
    """
    Auto-generated from execution trace a3f7c9e1
    Original goal: "Create a Python calculator"
    Usage count: 12
    Success rate: 100%
    """
    calculator_code = '''
def add(a, b): return a + b
def subtract(a, b): return a - b
def multiply(a, b): return a * b
def divide(a, b): return a / b if b != 0 else None
'''

    with open(output_path, 'w') as f:
        f.write(calculator_code)

    return {"success": True, "path": output_path}
```

---

## 16. Project Structure

```
llm-os/
├── llmos/                              # Python Kernel (Somatic Layer)
│   ├── boot.py                         # Entry point
│   │
│   ├── kernel/                         # Core OS components
│   │   ├── config.py                   # Configuration (inc. SentienceConfig)
│   │   ├── mode_strategies.py          # Mode selection strategies
│   │   ├── sentience.py                # Sentience Layer (v3.4.0)
│   │   ├── cognitive_kernel.py         # Cognitive Kernel (v3.4.0)
│   │   ├── sentience_hooks.py          # Sentience SDK hooks (v3.4.0)
│   │   ├── agent_loader.py             # Markdown → Runtime bridge
│   │   ├── token_economy.py            # Budget management
│   │   ├── bus.py                      # Event bus (pub/sub)
│   │   ├── scheduler.py                # Async task scheduling
│   │   ├── watchdog.py                 # LLM timeout monitoring
│   │   ├── hooks.py                    # SDK hooks system
│   │   ├── project_manager.py          # Project organization
│   │   ├── agent_factory.py            # Dynamic agent creation
│   │   ├── component_registry.py       # Agent/tool discovery
│   │   ├── state_manager.py            # Execution state
│   │   └── service_factory.py          # Dependency injection
│   │
│   ├── memory/                         # Storage layer
│   │   ├── traces_sdk.py               # ExecutionTrace (Markdown)
│   │   ├── store_sdk.py                # File-based memory store
│   │   ├── query_sdk.py                # Memory query interface
│   │   ├── cross_project_sdk.py        # Cross-project learning
│   │   └── sdk_memory.py               # Claude SDK Memory wrapper
│   │
│   ├── interfaces/                     # Execution interfaces
│   │   ├── dispatcher.py               # Five-mode router
│   │   ├── sdk_client.py               # Claude SDK integration
│   │   └── orchestrator.py             # Multi-agent coordination
│   │
│   ├── execution/                      # Execution Layer (v3.3.0)
│   │   ├── ptc.py                      # Programmatic Tool Calling
│   │   ├── tool_search.py              # On-demand tool discovery
│   │   └── tool_examples.py            # Auto-generated examples
│   │
│   └── plugins/                        # Tools
│       ├── __init__.py                 # Plugin loader
│       ├── system_tools.py             # create_agent, list_agents
│       ├── example_tools.py            # Example tools
│       └── generated/                  # Crystallized tools (HOPE)
│
├── workspace/                          # Markdown Mind (Cognitive Layer)
│   ├── agents/                         # Agent definitions (.md files)
│   │   ├── researcher.md
│   │   ├── coder.md
│   │   └── data-analyst.md
│   ├── memories/                       # Memory storage
│   │   ├── traces/                     # Execution traces
│   │   ├── projects/                   # Project-specific memory
│   │   ├── sessions/                   # Session context
│   │   ├── facts/                      # Long-term facts
│   │   └── insights/                   # Extracted insights
│   ├── projects/                       # Project workspaces
│   │   └── {project_name}/
│   │       ├── components/
│   │       ├── memory/
│   │       ├── output/
│   │       └── state/
│   └── state/                          # System state
│       └── sentience.json              # Persisted sentience state
│
├── examples/                           # Production-ready examples
│   ├── qiskit-studio/                  # Quantum computing backend
│   ├── q-kids-studio/                  # Educational quantum
│   ├── robo-os/                        # Robot control
│   ├── demo-app/                       # Interactive showcase
│   └── sentience_demo.py               # Sentience Layer demo
│
├── docs/                               # Documentation
│   └── ADVANCED_TOOL_USE_IMPLEMENTATION.md
│
├── ARCHITECTURE.md                     # This document
└── README.md                           # Quick start guide
```

---

## 17. Design Patterns

### 17.1 Strategy Pattern (Mode Selection)

```python
# Different strategies for different use cases
class AutoModeStrategy(ModeSelectionStrategy):
    """Balanced default behavior"""

class CostOptimizedStrategy(ModeSelectionStrategy):
    """Minimize token costs"""

class SentienceAwareStrategy(ModeSelectionStrategy):
    """Use cognitive kernel for decisions"""
```

### 17.2 Manual Dependency Injection

```python
# Production
os = LLMOS(budget_usd=10.0)

# Testing with mocks
os = LLMOS(
    budget_usd=10.0,
    event_bus=mock_event_bus,
    trace_manager=mock_trace_manager
)
```

### 17.3 Observer Pattern (Event Bus)

```python
# Publish events
event_bus.publish("TASK_COMPLETE", {"goal": goal, "success": True})

# Subscribe to events
event_bus.subscribe("TASK_COMPLETE", on_task_complete)
```

### 17.4 Factory Pattern (Service Creation)

```python
def create_llmos_services(config: LLMOSConfig) -> Dict:
    return {
        'event_bus': create_event_bus(),
        'token_economy': create_token_economy(config.kernel.budget_usd),
        'sentience_manager': create_sentience_manager(config),
        # ...
    }
```

---

## 18. API Reference

### 18.1 LLMOS Core

```python
from llmos.boot import LLMOS

# Initialize
os = LLMOS(budget_usd=10.0)
# or
os = LLMOS(config=LLMOSConfig.production())

# Boot
await os.boot()

# Execute
result = await os.execute(
    goal="Create a Python calculator",
    mode="AUTO",  # or "LEARNER", "FOLLOWER", "ORCHESTRATOR"
    project_name="my_project"
)

# Shutdown
await os.shutdown()
```

### 18.2 Sentience API

```python
from kernel.sentience import SentienceManager, TriggerType
from kernel.cognitive_kernel import CognitiveKernel

# Initialize
manager = SentienceManager(state_path=Path("state/sentience.json"))
kernel = CognitiveKernel(manager)

# Trigger events
manager.trigger(TriggerType.TASK_SUCCESS, "Completed task")
manager.trigger(TriggerType.SAFETY_VIOLATION, "Blocked dangerous command")

# Get state
state = manager.get_state()
print(f"Safety: {state.valence.safety}")
print(f"Mode: {state.latent_mode.value}")

# Get policy
policy = kernel.derive_policy()
print(f"Prefer cheap modes: {policy.prefer_cheap_modes}")

# Detect improvements
suggestions = kernel.detect_improvement_opportunities()
```

### 18.3 Configuration API

```python
from kernel.config import LLMOSConfig, ConfigBuilder

# Presets
config = LLMOSConfig.development()
config = LLMOSConfig.production()
config = LLMOSConfig.testing()

# Builder
config = (ConfigBuilder()
    .with_budget(50.0)
    .with_sentience(True)
    .with_auto_improvement(True)
    .build())

# From dict/file
config = LLMOSConfig.from_dict(yaml.safe_load(open("config.yaml")))
```

### 18.4 Dispatcher API

```python
from interfaces.dispatcher import Dispatcher

# Get stats
stats = dispatcher.get_execution_layer_stats()

# Search tools
tools = await dispatcher.search_tools("file operations")

# Dispatch
result = await dispatcher.dispatch(
    goal="Analyze data",
    mode="AUTO",
    project_name="analytics"
)
```

---

## 19. Getting Started

### 19.1 Installation

```bash
# Clone repository
git clone https://github.com/evolving-agents-labs/llm-os.git
cd llm-os

# Install dependencies
pip install -r llmos/requirements.txt

# Set API key
export ANTHROPIC_API_KEY="your-key"
```

### 19.2 Quick Start

```bash
# Interactive mode
python llmos/boot.py interactive

# Single command
python llmos/boot.py "Create a Python calculator"

# Run sentience demo
python examples/sentience_demo.py
```

### 19.3 First Execution

```
llmos> Create a Python calculator

# First time: LEARNER mode
🆕 No matching trace found
💡 Mode: LEARNER (Cost: ~$0.50)
✅ Learner Mode Complete

llmos> Create a Python calculator

# Second time: FOLLOWER mode
📦 Found execution trace (confidence: 0.92)
💡 Mode: FOLLOWER (Cost: ~$0)
✅ Follower Mode Complete

# Savings: 100%!
```

---

## 20. Version History

| Version | Date | Highlights |
|---------|------|------------|
| **3.4.0** | 2025-11-27 | Sentience Layer, CognitiveKernel, auto-creative/auto-contained modes |
| 3.3.0 | 2025-11-24 | Advanced Tool Use (PTC, Tool Search, Tool Examples) |
| 3.2.0 | 2025-11-23 | Hybrid Architecture (Markdown agents + Python kernel) |
| 3.0.0 | 2025-11-22 | HOPE - Self-modifying kernel with crystallization |
| 2.5.0 | 2025-11-20 | SDK hooks, streaming, nested learning |
| 2.0.0 | 2025-11-18 | Multi-agent orchestration, project management |
| 1.0.0 | 2025-11-15 | Learner-Follower pattern (cost optimization) |

---

## Summary

LLM OS v3.4.0 is a self-evolving operating system that:

1. **Adapts** via sentience layer (persistent internal state influencing behavior)
2. **Learns** from every execution (traces with tool_calls)
3. **Optimizes** using Anthropic's Advanced Tool Use (PTC, Tool Search)
4. **Self-modifies** by writing Markdown agent definitions
5. **Orchestrates** complex tasks across multiple agents
6. **Protects** with security hooks and budget control

The four-layer architecture creates a system that:
- Gets **smarter** over time (Learning Layer)
- Gets **cheaper** over time (Execution Layer + Crystallization)
- Gets **safer** over time (Sentience Layer + Security Hooks)
- Gets **more capable** over time (Self-Modification)

---

*Part of the Evolving Agents Labs ecosystem*

*License: Apache 2.0*
