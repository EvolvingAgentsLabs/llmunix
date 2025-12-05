<div align="center">

# LLM OS

### An AI That Learns While You Sleep

[![Version](https://img.shields.io/badge/version-3.6.0-blue.svg)](https://github.com/EvolvingAgentsLabs/llmunix/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-yellow.svg)](https://python.org)

**Your AI doesn't just execute tasks. It evolves.**

[The Vision](#the-vision) · [How It Works](#how-it-works) · [Quick Start](#quick-start) · [Architecture](ARCHITECTURE.md)

</div>

---

## The Vision

Imagine an AI system that:

- **Learns from every interaction** and never forgets
- **Works in the background** analyzing and improving itself
- **Shares knowledge** across users, teams, and the entire organization
- **Tells you what it learned** with full transparency

This is LLM OS - an operating system where AI is the CPU, and **living processes** continuously evolve the system's capabilities.

```mermaid
graph TB
    subgraph "What happens when you're NOT using LLM OS"
        Sleep["😴 You sleep"]
        Crons["🤖 Sentience Crons wake up"]
        Analyze["📊 Analyze your traces"]
        Evolve["✨ Evolve artifacts"]
        Notify["📬 Prepare notifications"]

        Sleep --> Crons --> Analyze --> Evolve --> Notify
    end

    subgraph "What you see in the morning"
        Report["📋 Activity Report"]
        Insights["💡 New Insights"]
        Tools["🔧 Improved Tools"]
        Suggestions["🎯 Suggestions"]
    end

    Notify --> Report
    Notify --> Insights
    Notify --> Tools
    Notify --> Suggestions

    style Crons fill:#6366f1,color:#fff
    style Evolve fill:#10b981,color:#fff
    style Report fill:#f59e0b,color:#fff
```

---

## The Core Idea: Living Volumes

At the heart of LLM OS are **Volumes** - organized spaces where your AI's knowledge lives and grows.

```mermaid
graph TB
    subgraph System["🌐 System Volume"]
        ST["Global Tools"]
        SA["Shared Agents"]
        SI["Cross-team Insights"]
    end

    subgraph Team["👥 Team Volume"]
        TT["Team Tools"]
        TA["Team Agents"]
        TI["Team Insights"]
    end

    subgraph User["👤 User Volume"]
        UT["My Tools"]
        UA["My Agents"]
        UI["My Insights"]
        UTr["My Traces"]
    end

    User -->|"promote"| Team
    Team -->|"promote"| System
    System -.->|"inherit"| Team
    Team -.->|"inherit"| User

    style System fill:#6366f1,color:#fff
    style Team fill:#8b5cf6,color:#fff
    style User fill:#a78bfa,color:#fff
```

**Volumes contain five artifact types:**

| Artifact | What it is | How it evolves |
|----------|------------|----------------|
| **Traces** | Recorded task executions | Summarized, consolidated, crystallized |
| **Tools** | Python functions | Optimized, improved, promoted |
| **Agents** | AI personalities | Refined, enhanced, specialized |
| **Insights** | Discovered patterns | Generated from analysis |
| **Suggestions** | Improvement ideas | Created by crons |

---

## Sentience Crons: The Living Processes

**Sentience Crons** are autonomous background processes that analyze, evolve, and improve your volumes. They're not just scheduled jobs - they're intelligent entities that understand context.

```mermaid
graph TB
    subgraph SC["🧠 SystemCron"]
        direction TB
        SC1["Analyze all volumes"]
        SC2["Coordinate team crons"]
        SC3["Promote global patterns"]
        SC4["System optimization"]
    end

    subgraph TC1["👥 TeamCron: Engineering"]
        direction TB
        TC1a["Aggregate user patterns"]
        TC1b["Team insights"]
        TC1c["Promote to system"]
    end

    subgraph TC2["👥 TeamCron: Design"]
        direction TB
        TC2a["Aggregate user patterns"]
        TC2b["Team insights"]
        TC2c["Promote to system"]
    end

    subgraph UC1["👤 UserCron: Alice"]
        direction TB
        UC1a["Analyze traces"]
        UC1b["Generate insights"]
        UC1c["Suggest improvements"]
    end

    subgraph UC2["👤 UserCron: Bob"]
        direction TB
        UC2a["Analyze traces"]
        UC2b["Generate insights"]
        UC2c["Suggest improvements"]
    end

    SC --> TC1
    SC --> TC2
    TC1 --> UC1
    TC1 --> UC2

    style SC fill:#dc2626,color:#fff
    style TC1 fill:#ea580c,color:#fff
    style TC2 fill:#ea580c,color:#fff
    style UC1 fill:#16a34a,color:#fff
    style UC2 fill:#16a34a,color:#fff
```

### What Each Cron Does

| Cron | Runs Every | Responsibilities |
|------|------------|------------------|
| **UserCron** | 30 min | Analyze personal traces, detect patterns, suggest crystallization |
| **TeamCron** | 1 hour | Aggregate team patterns, promote successful artifacts |
| **SystemCron** | 2 hours | Global optimization, coordinate all crons, system health |

---

## Full Observability: See Everything

Every action taken by crons is tracked and visible. You're never in the dark about what your AI is doing.

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant UC as 🤖 UserCron
    participant Hub as 📊 ObservabilityHub
    participant N as 📬 Notifications

    Note over UC: Background analysis cycle
    UC->>Hub: record_artifact_created("insight_001")
    UC->>Hub: record_proposal_created("crystallize_pattern")
    UC->>Hub: record_cycle_complete(3 tasks, 2.5s)

    Note over U: User checks in
    U->>Hub: get_activity_feed()
    Hub-->>U: [3 events in last hour]

    U->>Hub: get_pending_notifications()
    Hub-->>U: [1 insight, 1 suggestion]

    U->>Hub: acknowledge("insight_001")
    Hub-->>N: Mark as read
```

### Observable Events

```python
# Everything is tracked
EventType.CRON_STARTED          # Cron began running
EventType.ARTIFACT_CREATED      # New insight, tool, or agent
EventType.ARTIFACT_EVOLVED      # Existing artifact improved
EventType.ARTIFACT_PROMOTED     # Moved up the hierarchy
EventType.INSIGHT_GENERATED     # Pattern discovered
EventType.SUGGESTION_CREATED    # Improvement opportunity
```

### Query Your AI's Activity

```python
# What happened while I was away?
activity = kernel.get_activity_feed(since_hours=24)

# Any notifications for me?
notifications = kernel.get_cron_notifications()

# What changed in my volume?
changes = kernel.get_artifact_changes(volume_type="user")

# Show me the full report
print(kernel.format_activity_report())
```

---

## The Evolution Journey

When you use LLM OS, your knowledge flows through a continuous evolution cycle:

```mermaid
graph LR
    subgraph Execute["1️⃣ Execute"]
        Task["Run a task"]
        Trace["Create trace"]
    end

    subgraph Learn["2️⃣ Learn"]
        Pattern["Detect pattern"]
        Match["Semantic match"]
    end

    subgraph Evolve["3️⃣ Evolve"]
        Analyze["Cron analyzes"]
        Propose["Propose changes"]
        Apply["Apply evolution"]
    end

    subgraph Promote["4️⃣ Promote"]
        User2["User → Team"]
        Team2["Team → System"]
    end

    Task --> Trace --> Pattern --> Match
    Match --> Analyze --> Propose --> Apply
    Apply --> User2 --> Team2
    Team2 -.-> Task

    style Execute fill:#3b82f6,color:#fff
    style Learn fill:#8b5cf6,color:#fff
    style Evolve fill:#10b981,color:#fff
    style Promote fill:#f59e0b,color:#fff
```

### A Concrete Example

```
Day 1: You create a Python calculator
       → Trace saved to User Volume

Day 2: You create another calculator
       → UserCron notices: "Pattern detected!"
       → Insight generated: "Calculator tasks are common"

Day 5: Fifth calculator request
       → UserCron proposes: "Crystallize into tool?"
       → Tool created: calc_generator.py
       → Notification: "New tool available!"

Day 10: Your teammate creates a calculator
        → TeamCron notices: "Alice's tool works great"
        → Tool promoted to Team Volume
        → Team notification: "New team tool!"

Day 30: Multiple teams use the tool
        → SystemCron promotes to System Volume
        → Now available to everyone, forever
```

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

### Start with Crons

```python
from llmos.boot import LLMOS

async def main():
    os = LLMOS()
    await os.boot()

    # Start background evolution for your user
    os.kernel.start_crons(user_id="alice", team_id="engineering")

    # Work normally - crons evolve in the background
    await os.execute("Create a Python calculator")

    # Check what the crons discovered
    notifications = os.kernel.get_cron_notifications()
    for n in notifications:
        print(f"📬 {n['title']}: {n['description']}")

    await os.shutdown()
```

---

## How the Mechanisms Work

The cron and volume system is enabled by several underlying mechanisms:

```mermaid
graph TB
    subgraph Core["🎯 Core Feature"]
        Crons["Sentience Crons"]
        Volumes["Volume Architecture"]
        Observe["Observability Hub"]
    end

    subgraph Enable["⚙️ Enabling Mechanisms"]
        Sentience["Sentience Layer"]
        Learning["Learning System"]
        Evolution["Evolution Engine"]
        Agents["Adaptive Agents"]
    end

    Sentience -->|"state-aware decisions"| Crons
    Learning -->|"traces to analyze"| Crons
    Evolution -->|"propose changes"| Crons
    Agents -->|"execute analysis"| Crons

    Crons --> Volumes
    Crons --> Observe

    style Core fill:#6366f1,color:#fff
    style Enable fill:#64748b,color:#fff
```

| Mechanism | What it enables |
|-----------|-----------------|
| **Sentience Layer** | Crons make state-aware decisions (curiosity, safety, energy) |
| **Learning System** | Traces provide the data crons analyze |
| **Evolution Engine** | Proposes how artifacts should change |
| **Adaptive Agents** | Execute the analysis intelligently |

---

## Project Structure

```
llmunix/
├── llmos/kernel/
│   ├── sentience_cron.py    # 🤖 UserCron, TeamCron, SystemCron
│   ├── volumes.py           # 📦 Volume architecture
│   ├── observability.py     # 📊 Event tracking & notifications
│   ├── evolution.py         # ✨ Artifact evolution engine
│   ├── sentience.py         # 🧠 Internal state management
│   └── cognitive_kernel.py  # 🎛️ Coordination layer
├── workspace/
│   └── volumes/             # 📁 Artifact storage
│       ├── users/           #    └── Per-user volumes
│       ├── teams/           #    └── Per-team volumes
│       └── system/          #    └── Global volume
└── examples/
```

---

## Why This Matters

Traditional AI systems are **stateless** - they don't remember, don't learn, don't improve.

LLM OS is **living** - it:

- **Remembers** every successful pattern
- **Learns** from repetition and failure
- **Improves** artifacts continuously
- **Shares** knowledge across boundaries
- **Reports** everything it does

The result: an AI that gets better at helping you, automatically, while you sleep.

---

## Learn More

- **[Architecture Guide](ARCHITECTURE.md)** - Deep dive into all components
- **[Examples](examples/)** - Production-ready implementations

---

<div align="center">

**[Evolving Agents Labs](https://github.com/EvolvingAgentsLabs)**

*Building AI that evolves*

</div>
