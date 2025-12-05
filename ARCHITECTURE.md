# LLM OS Architecture

**Version 3.6.0**

---

## Overview

LLM OS is built on a simple premise: treat the LLM as a CPU that can learn and remember.

Four innovations make this work:

1. **Sentience Layer** - Internal state that persists and influences behavior
2. **Learning Layer** - Traces that enable free replay of learned patterns
3. **Adaptive Agents** - Subagents that evolve per-query based on state and memory
4. **Sentience Crons** - Background processes that continuously evolve artifacts across volumes

---

## The Six Layers

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
├─────────────────────────────────────────┤
│  CRON         "What to do in background"│  ← Continuous evolution
└─────────────────────────────────────────┘
         ↑________feedback_________↓
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

## 6. Sentience Cron Layer

The Cron Layer introduces **living background processes** that continuously analyze and evolve the system's artifacts. Unlike traditional cron jobs, these are "sentient" - they understand context, learn from patterns, and make intelligent decisions.

### Cron Hierarchy

```
                    ┌─────────────────────────────────────┐
                    │          SystemCron                  │
                    │  - Full read/write to all volumes    │
                    │  - Controls Team and User crons      │
                    │  - Global pattern analysis           │
                    │  - Cross-team insights               │
                    └─────────────────┬───────────────────┘
                                      │
           ┌──────────────────────────┼──────────────────────────┐
           │                          │                          │
    ┌──────▼──────────────────┐ ┌─────▼───────────────────┐ ┌────▼────────────────────┐
    │       TeamCron          │ │       TeamCron          │ │       TeamCron          │
    │  - Read/write team vol  │ │  - Read/write team vol  │ │  - Read/write team vol  │
    │  - Read system volume   │ │  - Read system volume   │ │  - Read system volume   │
    │  - Aggregate user data  │ │  - Aggregate user data  │ │  - Aggregate user data  │
    └──────────┬──────────────┘ └──────────┬──────────────┘ └──────────┬──────────────┘
               │                           │                           │
        ┌──────┼──────┐              ┌─────┼─────┐              ┌──────┼──────┐
        │      │      │              │     │     │              │      │      │
     ┌──▼──┐┌──▼──┐┌──▼──┐       ┌───▼─┐┌──▼──┐┌─▼───┐      ┌───▼─┐┌──▼──┐┌──▼──┐
     │User ││User ││User │       │User ││User ││User │      │User ││User ││User │
     │Cron ││Cron ││Cron │       │Cron ││Cron ││Cron │      │Cron ││Cron ││Cron │
     └─────┘└─────┘└─────┘       └─────┘└─────┘└─────┘      └─────┘└─────┘└─────┘
```

### Volume Architecture

Artifacts are organized into three scoped volumes:

| Volume | Owner | Contents | Access Control |
|--------|-------|----------|----------------|
| **User** | Individual user | Personal traces, tools, agents, insights | UserCron: read/write; TeamCron: read-only |
| **Team** | Team | Shared resources, promoted patterns | TeamCron: read/write; UserCron: read-only |
| **System** | Global | Universal tools, cross-team patterns | SystemCron: read/write |

### Artifact Types

Each volume contains five artifact types:

| Type | Storage | Purpose |
|------|---------|---------|
| **Traces** | `*.md` | Execution histories, tool call sequences |
| **Tools** | `*.py` | Crystallized capabilities (generated Python) |
| **Agents** | `*.md` | Agent definitions with prompts and configs |
| **Insights** | `*.md` | Analysis findings, pattern observations |
| **Suggestions** | `*.md` | Improvement opportunities |

### Cron Responsibilities

**UserCron** (runs every 30 minutes by default):
- Analyze personal traces for patterns
- Detect crystallization candidates (5+ uses, 95%+ success)
- Suggest tool improvements based on usage
- Generate personal insights
- Flag promotion candidates for team level

**TeamCron** (runs every 1 hour by default):
- Aggregate patterns across team users
- Identify team-wide optimization opportunities
- Promote successful user artifacts to team level
- Generate team insights

**SystemCron** (runs every 2 hours by default):
- Global pattern analysis across all volumes
- Coordinate and manage child crons
- System-wide optimization and maintenance
- Promote team artifacts to system level
- Cleanup old/redundant artifacts

### Evolution Engine

The Evolution Engine analyzes artifacts and proposes improvements:

```python
class EvolutionEngine:
    """Coordinates artifact evolution"""

    def __init__(self):
        self.trace_evolver = TraceEvolver()
        self.tool_evolver = ToolEvolver()
        self.agent_evolver = AgentEvolver()

    def generate_proposals(self, volume) -> List[EvolutionProposal]:
        """Generate all evolution proposals for a volume"""
        proposals = []
        proposals.extend(self.trace_evolver.propose_consolidation(volume))
        proposals.extend(self.trace_evolver.propose_crystallization(volume))
        proposals.extend(self.tool_evolver.propose_improvements(volume))
        proposals.extend(self.agent_evolver.propose_enhancements(volume))
        return proposals
```

**Evolution Types:**

| Evolver | What it does |
|---------|--------------|
| **TraceEvolver** | Summarize old traces, identify crystallization candidates |
| **ToolEvolver** | Analyze tool usage, suggest optimizations |
| **AgentEvolver** | Track agent performance, propose refinements |

### Observability Hub

All cron activity flows through the ObservabilityHub:

```python
# Event types tracked
EventType.CRON_STARTED
EventType.CRON_STOPPED
EventType.CRON_CYCLE_END
EventType.ARTIFACT_CREATED
EventType.ARTIFACT_EVOLVED
EventType.ARTIFACT_PROMOTED
EventType.ARTIFACT_DELETED
EventType.PROPOSAL_CREATED
EventType.INSIGHT_GENERATED
EventType.SUGGESTION_CREATED
EventType.SYSTEM_ALERT
```

**User-Facing Features:**

```python
# Get pending notifications
notifications = hub.get_pending_notifications()

# Get activity feed
activity = hub.get_activity_feed(since_hours=24)

# Get artifact change history
changes = hub.get_artifact_changes(volume_type="user")

# Acknowledge a notification
hub.acknowledge(event_id)
```

### Artifact Promotion Flow

```
User Volume                    Team Volume                   System Volume
┌───────────────┐             ┌───────────────┐             ┌───────────────┐
│ Traces        │             │ Traces        │             │ Traces        │
│ - calc_v1     │──promote──→│ - calc_v2     │──promote──→│ - calc_final  │
│ - calc_v2     │             │               │             │               │
│ - calc_v3     │             │ Tools         │             │ Tools         │
│               │             │ - calc_tool   │──promote──→│ - calc_tool   │
│ Tools (local) │──promote──→│               │             │               │
│ - my_tool     │             │ Agents        │             │ Agents        │
│               │             │ - researcher  │──promote──→│ - researcher  │
│ Insights      │             │               │             │               │
│ - "Pattern X" │             │ Insights      │             │               │
└───────────────┘             └───────────────┘             └───────────────┘
```

Promotion criteria:
- **User → Team**: High usage count, good success rate, team relevance
- **Team → System**: Used across multiple teams, proven value

---

## Deep Sentience v2

Version 3.6.0 introduces enhanced sentience capabilities:

### Coupled Dynamics (Maslow's Hierarchy)

Variables now follow a hierarchical gating system:

```
Safety (base need) → gates → Energy → gates → Curiosity → gates → Confidence
```

**Implementation:**

```python
def get_effective_curiosity(self) -> float:
    """Curiosity is gated by safety - unsafe states suppress exploration"""
    if self.safety < -0.3:
        return min(self.curiosity, -0.2)  # Suppress curiosity when unsafe
    return self.curiosity
```

When safety is low, the system cannot be curious - it must first address the safety concern. This mirrors biological behavior.

### Theory of Mind (UserModel)

The system maintains a model of the user's state:

```python
@dataclass
class UserModel:
    """Model of user's inferred emotional/cognitive state"""
    frustration: float = 0.0      # Inferred from corrections, repeated questions
    satisfaction: float = 0.0     # Inferred from positive feedback, task completions
    engagement: float = 0.5       # Activity level
    expertise_estimate: float = 0.5  # Technical level
    interaction_count: int = 0
```

**Empathy Gap Detection:**

```python
def get_empathy_gap(self) -> float:
    """Detect misalignment between agent confidence and user satisfaction"""
    return abs(self.valence.self_confidence - self.user_model.satisfaction)
```

When empathy gap exceeds threshold, the system proactively checks in with the user.

### Episodic Emotional Indexing

Memories can be tagged with emotional state for retrieval:

```python
@dataclass
class EmotionalMemoryTag:
    """Tag a memory with emotional state for later retrieval"""
    memory_id: str
    valence_snapshot: Dict[str, float]  # State when memory was formed
    task_outcome: str                    # success, failure, partial
    emotional_significance: float        # How salient (0.0 to 1.0)
```

This enables the "Proust Effect" - finding memories with similar emotional states:

```python
similar_memories = kernel.find_similar_emotional_memories(
    min_similarity=0.7,
    outcome_filter="success"
)
```

### Inner Monologue

Background thought processing during idle time:

```python
class InnerMonologue:
    """Background cognitive process that runs during idle time"""

    async def _generate_thought(self) -> str:
        """Generate a thought based on current state and rumination topic"""
        # Analyzes current state
        # Processes rumination topics
        # Generates priming context for next interaction
```

The inner monologue provides "priming context" that influences the next interaction - the system has been "thinking" about the problem.

### Self-Modification Records

The system can tune its own sentience parameters:

```python
@dataclass
class SelfModificationRecord:
    """Record of a self-modification to sentience parameters"""
    timestamp: str
    parameter: str           # e.g., "curiosity_setpoint"
    old_value: float
    new_value: float
    reason: str
    performance_before: Dict[str, float]
    approval_required: bool
```

This is gated by policy - most modifications require explicit approval.

---

## Complete Data Flow

```
User Goal: "Research AI trends"
    │
    ├─[1. Sentience Layer]──────────────────────────────────┐
    │   curiosity=0.3, safety=0.5, energy=0.8               │
    │   latent_mode=AUTO_CREATIVE                           │
    │   theory_of_mind: user.frustration=0.1                │
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
    ├─[5. Evolution Layer]──────────────────────────────────┤
    │   Record execution metrics                            │
    │   Update agent performance (success=1)                │
    │   Tag memory with emotional state                     │
    │   If 5+ uses: crystallize into Python function        │
    │                                                       ↓
    └─[6. Cron Layer (Background)]──────────────────────────┤
        UserCron analyzes new trace                         │
        ├─ Detects pattern: "research" tasks                │
        ├─ Generates insight: "Optimize WebSearch usage"    │
        ├─ Proposes: Crystallize research pattern           │
        └─ Notifies user of suggestion                      │
                         │                                  │
        TeamCron aggregates                                 │
        ├─ Cross-user patterns found                        │
        └─ Promotes useful artifacts to team volume         │
                         │                                  │
        SystemCron coordinates                              │
        ├─ Global optimization                              │
        └─ Promote best patterns to system volume           │
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

### Sentience Cron Management

```python
from llmos.kernel.cognitive_kernel import CognitiveKernel

# Access crons through cognitive kernel
kernel = CognitiveKernel(sentience_manager, workspace)

# Start crons with user context
kernel.start_crons(user_id="alice", team_id="engineering")

# Run a cron cycle immediately
tasks = await kernel.run_cron_now(cron_level="user", owner_id="alice")

# Get cron status
status = kernel.get_cron_status()

# Get notifications
notifications = kernel.get_cron_notifications()

# Get activity feed
activity = kernel.get_activity_feed(since_hours=24)

# Get artifact changes
changes = kernel.get_artifact_changes(volume_type="user")

# Acknowledge a notification
kernel.acknowledge_notification(event_id="evt_00000123")

# Stop crons
kernel.stop_crons()
```

### Volume Access

```python
# Direct volume access
user_volume = kernel.get_user_volume("alice")
team_volume = kernel.get_team_volume("engineering")
system_volume = kernel.get_system_volume()

# Read/write artifacts
from llmos.kernel.volumes import ArtifactType

traces = user_volume.list_artifacts(ArtifactType.TRACE)
content = user_volume.read_artifact(ArtifactType.TRACE, traces[0])

# Get volume stats
stats = user_volume.get_stats()
print(f"Traces: {stats.trace_count}, Tools: {stats.tool_count}")

# Get recent changes
changes = user_volume.get_recent_changes(limit=10)
```

### Evolution Engine

```python
# Analyze a volume for evolution opportunities
analysis = kernel.analyze_volume("user", owner_id="alice")

# Get evolution proposals
proposals = kernel.get_evolution_proposals("user", owner_id="alice")

for proposal in proposals:
    print(f"{proposal['proposal_type']}: {proposal['description']}")
    print(f"  Target: {proposal['target_artifact_type']}:{proposal['target_artifact_id']}")
    print(f"  Confidence: {proposal['confidence']}")
```

### Observability Hub Direct Access

```python
from llmos.kernel.observability import ObservabilityHub, EventType

hub = ObservabilityHub(workspace / "observability")

# Record custom events
hub.record_artifact_created(
    cron_id="user:alice",
    artifact_type="tool",
    artifact_id="my_tool",
    volume_type="user",
    reason="Crystallized from repeated pattern"
)

# Query events
events = hub.event_store.get_events(
    event_types=[EventType.ARTIFACT_CREATED, EventType.ARTIFACT_EVOLVED],
    since=datetime.now() - timedelta(days=1),
    limit=50
)

# Get global summary
summary = hub.get_global_summary()
print(f"Artifacts created today: {summary['artifacts_created']}")
print(f"Pending notifications: {summary['pending_notifications']}")

# Subscribe to real-time events
def on_event(event):
    if event.notify_user:
        print(f"Notification: {event.title}")

hub.subscribe(on_event)
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
