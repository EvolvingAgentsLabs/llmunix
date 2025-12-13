# LLMos-Lite UI/UX Proposal: Git-Aware Terminal Interface

> **Expert UX Analysis & Proposal for Multi-Level Volume-Based Interface**

**Date**: December 2025
**Version**: 1.0
**Status**: Proposal

---

## Executive Summary

### Current State
LLMos-lite currently has:
- ✅ Backend: Git-backed volumes (System/Team/User)
- ✅ Backend: Traces, skills, session storage
- ✅ Backend: Workflow execution engine
- ❌ **Missing**: Terminal/UI that exposes this power to users

### Vision
A **Git-aware terminal interface** that treats Git commits as the primary unit of work, where:
- Each commit = A complete work session (prompts + traces + results)
- Users can navigate between System/Team/User levels
- Sessions are resumable, shareable, and version-controlled
- The UI reveals the **"human-agentic process"** not just final artifacts

### Key Innovation
**Git commits become executable knowledge artifacts**, containing:
1. **Final artifacts** (code, skills, workflows)
2. **Process context** (prompts, LLM interactions, traces)
3. **Results metadata** (success rate, patterns detected)

This transforms Git from "version control" to **"cognitive time machine"** - you can replay not just what changed, but **why and how it was created**.

---

## Current State Analysis

### What Exists (Backend)

```
llmos-lite/
├── core/
│   ├── volumes.py          ✅ Git-backed storage
│   ├── skills.py           ✅ Skill management
│   ├── evolution.py        ✅ Pattern detection
│   └── workflow.py         ✅ Workflow engine
├── api/
│   ├── main.py             ✅ REST API
│   └── workflows.py        ✅ Workflow endpoints
└── ui/
    └── lib/                ✅ Execution libraries
        ├── pyodide-runner.ts
        └── workflow-executor.ts
```

### What's Missing (Frontend)

❌ No terminal interface
❌ No volume navigator
❌ No session browser
❌ No Git commit viewer
❌ No trace replay interface
❌ No multi-level context switcher

### The Gap

Users can interact via API but have **no visual interface** to:
- See what's in their volumes
- Browse and resume sessions
- Navigate commit history
- Switch between System/Team/User contexts
- Understand what the system is learning

---

## The Core UX Problem: **Context Amnesia**

### Traditional Git Problem
```
git log
commit a3f7c9e...
Author: alice
Date: Dec 13

"Update workflow"  ← What workflow? Why? What was the goal?
```

### LLMos-Lite Solution
```
llmos log --user alice

📦 Session: quantum-research-2025-12-13
├── Prompts: "Help me optimize VQE circuit for H2 molecule"
├── Traces: 47 interactions (3 patterns detected)
├── Artifacts:
│   ├── vqe-optimized.py (created)
│   ├── h2-molecule.workflow (created)
│   └── quantum-optimization.md (skill generated)
├── Results: 92% success rate, 2.3s average latency
└── Commit: a3f7c9e "Evolution: VQE optimization pattern"
```

The commit message becomes a **cognitive artifact** that captures:
1. **Intent** (prompts)
2. **Process** (traces)
3. **Outcome** (artifacts + results)

---

## Proposed UI Architecture

### Three-Panel Terminal Interface

```
┌─────────────────────────────────────────────────────────────────────┐
│ LLMos-Lite Terminal                                    alice@eng    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐  ┌──────────────────────┐  ┌────────────────┐│
│  │  VOLUME NAV     │  │   SESSION BROWSER    │  │  TRACE VIEWER  ││
│  │                 │  │                      │  │                ││
│  │  📁 System      │  │  Active Sessions     │  │  Current:      ││
│  │  📁 Team: eng   │  │  ┌──────────────┐   │  │  Session #47   ││
│  │  📁 User: alice │  │  │ quantum-res  │   │  │                ││
│  │                 │  │  │ 🟢 Active    │   │  │  Prompts (3):  ││
│  │  Current:       │  │  │ 47 traces    │   │  │  1. "Optimize  ││
│  │  👤 alice@eng   │  │  └──────────────┘   │  │     VQE..."    ││
│  │                 │  │                      │  │  2. "Add H2    ││
│  │  [Switch Level] │  │  Recent Commits      │  │     molecule"  ││
│  │                 │  │  ┌──────────────┐   │  │  3. "Generate  ││
│  │  Git Status:    │  │  │ a3f7c9e      │   │  │     skill"     ││
│  │  3 uncommitted  │  │  │ VQE optimize │   │  │                ││
│  │  changes        │  │  │ 2 hrs ago    │   │  │  Traces (47):  ││
│  │                 │  │  └──────────────┘   │  │  [View All]    ││
│  │  [Commit]       │  │                      │  │                ││
│  └─────────────────┘  └──────────────────────┘  └────────────────┘│
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│ > llmos chat "Help me with quantum circuits"                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Panel 1: Volume Navigator

**Purpose**: Navigate the 3-level hierarchy (System/Team/User)

**Features**:
- Tree view of volumes
- Current context indicator
- Git status per volume
- Quick level switching
- Uncommitted changes counter

**Interactions**:
```bash
# Switch to system level (read-only)
llmos volume --system

# Switch to team level (shared)
llmos volume --team engineering

# Switch to user level (private)
llmos volume --user alice

# View git status
llmos status
  System: 0 changes (readonly)
  Team:   5 new skills from Bob
  User:   3 uncommitted sessions
```

### Panel 2: Session Browser

**Purpose**: View and resume work sessions

**Features**:
- Active sessions (in-progress work)
- Recent commits (completed sessions)
- Session metadata (prompts, trace count, artifacts)
- Resume/Replay buttons
- Share session button (User → Team)

**Interactions**:
```bash
# List active sessions
llmos sessions --active
  quantum-research (47 traces, 3 hours ago)
  data-pipeline (12 traces, 1 day ago)

# Resume a session
llmos resume quantum-research
  ✓ Loaded 47 traces
  ✓ Restored context: VQE optimization
  ✓ Skills available: quantum-vqe, h2-molecule

# Commit a session
llmos commit --session quantum-research \
  --message "VQE optimization pattern discovered"

  Committed:
  - 47 traces
  - 2 artifacts (vqe-optimized.py, h2-molecule.workflow)
  - 1 skill (quantum-optimization.md)
  - Prompts: 3 main interactions
  - Success rate: 92%
```

### Panel 3: Trace Viewer

**Purpose**: See the cognitive process within a session

**Features**:
- Prompt history
- Trace timeline
- Artifacts created/modified
- Pattern detection status
- Success metrics

**Interactions**:
```bash
# View trace details
llmos trace show 47

  Prompt: "Optimize VQE circuit for H2 molecule"

  Execution:
  1. Tool: WebSearch (quantum VQE optimization)
  2. Tool: Read (existing VQE examples)
  3. Tool: Write (vqe-optimized.py)
  4. Tool: Bash (python vqe-optimized.py)

  Result: ✓ Success (eigenvalue: -1.137)

  Pattern Detected: "VQE optimization" (3rd occurrence)
  → Skill draft created: quantum-optimization.md

# Replay a trace (see what happened)
llmos trace replay 47
  [Shows step-by-step execution with outputs]
```

---

## Git as a "Cognitive File System"

### Traditional Git
```
Commit Message: "Update code"
Changed Files: main.py (+50, -20)
```

### LLMos Git (Cognitive Git)
```
Commit Message:
---
type: session
goal: "Optimize VQE circuit for H2 molecule"
prompts:
  - "Help me optimize VQE circuit"
  - "Add support for H2 molecule"
  - "Generate reusable skill"
traces: 47
patterns_detected: 1
skills_generated: 1
success_rate: 0.92
artifacts:
  - vqe-optimized.py (created)
  - h2-molecule.workflow (created)
  - quantum-optimization.md (skill)
---

Evolution: VQE optimization pattern discovered

This session produced a reusable skill for VQE optimization
after detecting the pattern across 3 similar tasks.
```

**Benefits**:
1. **Searchable**: `llmos search "VQE optimization"` finds commits by intent
2. **Replayable**: `llmos replay a3f7c9e` shows the cognitive process
3. **Shareable**: `llmos share a3f7c9e --to-team` promotes session to team
4. **Learnable**: Evolution engine parses commit metadata to find patterns

### Structured Commit Format

Every commit includes YAML frontmatter:

```yaml
---
session_id: quantum-research-2025-12-13
session_type: interactive  # or "automated", "evolution"
user_id: alice
team_id: engineering
start_time: 2025-12-13T10:00:00Z
end_time: 2025-12-13T13:30:00Z
duration_hours: 3.5

# The cognitive process
prompts:
  - timestamp: 2025-12-13T10:05:00Z
    text: "Help me optimize VQE circuit for H2 molecule"
    response_summary: "Created initial VQE implementation"
  - timestamp: 2025-12-13T11:20:00Z
    text: "Add support for different molecules"
    response_summary: "Generalized to support any molecule"
  - timestamp: 2025-12-13T13:00:00Z
    text: "Generate a reusable skill for this"
    response_summary: "Created quantum-optimization.md skill"

# Execution metadata
trace_count: 47
tools_used: [WebSearch, Read, Write, Bash, mcp__ide__executeCode]
success_rate: 0.92
avg_latency_ms: 2300

# Evolution metadata
patterns_detected:
  - name: "VQE optimization"
    occurrence_count: 3
    confidence: 0.95
skills_generated:
  - skill_id: quantum-optimization
    category: quantum
    auto_promoted: false

# Artifacts
artifacts_created:
  - path: skills/quantum-optimization.md
    type: skill
    size_bytes: 2048
  - path: traces/session_quantum-research.json
    type: trace_bundle
    size_bytes: 45000

# Sharing
shared_with: []  # Can be promoted to team later
promoted_to_team: false
---

Evolution: VQE optimization pattern discovered

After 3 similar VQE tasks, the system detected a reusable
pattern and generated the quantum-optimization skill.

This session demonstrates the power of the evolution engine
to learn from repeated interactions.
```

---

## User Workflows

### Workflow 1: Daily Work (User Level)

```bash
# Morning: Start new session
llmos start "Build data pipeline"
  ✓ Session created: data-pipeline-2025-12-13
  ✓ Context: alice@engineering

# Work with LLM
llmos chat "Create ETL pipeline for customer data"
  [LLM helps, traces recorded]

# Continue working
llmos chat "Add error handling"
  [More traces recorded]

# Evening: Commit the session
llmos commit \
  --message "ETL pipeline with error handling" \
  --artifacts "etl.py, test_etl.py"

  ✓ Committed: data-pipeline-2025-12-13
  ✓ 23 traces
  ✓ 2 artifacts
  ✓ No patterns detected (first occurrence)
```

### Workflow 2: Team Collaboration (Team Level)

```bash
# Alice promotes a useful skill
llmos promote quantum-optimization --to-team \
  --reason "Useful for all quantum projects"

  ✓ Promoted to team:engineering
  ✓ Team members can now use this skill

# Bob (team member) sees new skills
llmos volume --team
llmos skills --new

  quantum-optimization (by alice, 2 hours ago)
  "VQE circuit optimization for quantum chemistry"

# Bob uses Alice's skill
llmos chat "Optimize VQE for LiH molecule"
  [LLM uses quantum-optimization skill]
  ✓ Skill quantum-optimization applied
```

### Workflow 3: System Learning (System Level)

```bash
# System cron runs nightly
llmos evolve --level system

  Analyzing team:engineering (3 teams total)

  Pattern detected: "API endpoint creation" (15 occurrences across 5 users)
  → Promoting to system level

  ✓ Skill created: api-endpoint-pattern.md
  ✓ Committed to system volume
  ✓ Available to all users

# Next day: All users benefit
llmos chat "Create REST endpoint for users"
  [LLM uses system-level api-endpoint-pattern skill]
```

### Workflow 4: Session Replay (Learning from Others)

```bash
# Alice wants to learn how Bob solved a problem
llmos search --team "GraphQL optimization"

  Found: commit b7e9a2f by bob
  "GraphQL query optimization pattern"

# Alice views Bob's session
llmos show b7e9a2f

  Session: graphql-optimization
  User: bob@engineering

  Prompts:
  1. "Help me optimize GraphQL queries"
  2. "Add caching layer"
  3. "Benchmark performance"

  Traces: 34
  Success rate: 89%

  Artifacts:
  - graphql-cache.js
  - benchmark-results.json
  - graphql-optimization.md (skill)

# Alice can replay the session to see the process
llmos replay b7e9a2f --interactive

  [Step 1/34] Prompt: "Help me optimize GraphQL queries"
  [Tool: WebSearch] "GraphQL optimization techniques"
  ...

  [Continue] [Skip] [Stop]
```

---

## Terminal Commands (CLI Design)

### Core Commands

```bash
# Volume management
llmos volume --system              # Switch to system (readonly)
llmos volume --team <team_id>      # Switch to team (shared)
llmos volume --user <user_id>      # Switch to user (private)
llmos volume --status              # Show current volume + git status

# Session management
llmos start <session_name>         # Start new session
llmos resume <session_name>        # Resume existing session
llmos sessions --active            # List active sessions
llmos sessions --recent            # List recent commits
llmos commit [--message "..."]     # Commit current session

# Interaction
llmos chat "<prompt>"              # Chat with LLM (records trace)
llmos workflow <workflow_file>     # Execute workflow (records trace)

# Exploration
llmos skills [--new]               # List skills in current volume
llmos traces [--session <id>]      # List traces
llmos trace show <trace_id>        # View trace details
llmos trace replay <trace_id>      # Replay trace step-by-step

# Search & Discovery
llmos search "<query>"             # Search commits by prompt/goal
llmos log [--volume <vol>]         # Git log with cognitive metadata
llmos show <commit_hash>           # Show commit details (cognitive format)

# Sharing & Promotion
llmos promote <skill_id> --to-team [--reason "..."]
llmos promote <skill_id> --to-system [--reason "..."]  # Admin only
llmos share <session_id> --with <user_id>

# Evolution
llmos evolve [--level user|team|system]   # Trigger evolution
llmos patterns                            # View detected patterns
```

### Example Session

```bash
# Alice starts her day
$ llmos volume --user alice
✓ Switched to volume: alice@engineering

$ llmos status
Volume: alice@engineering
├── Skills: 12 (3 local, 5 from team, 4 from system)
├── Active sessions: 2
├── Uncommitted changes: 1 session (quantum-research)
└── Git: 3 commits behind team (run 'llmos pull')

$ llmos sessions --active
Sessions:
├── quantum-research (47 traces, 3 hours ago, uncommitted)
└── data-pipeline (12 traces, 2 days ago, committed)

$ llmos resume quantum-research
✓ Resumed session: quantum-research
✓ Loaded 47 traces
✓ Context: VQE optimization for H2 molecule
✓ Skills: quantum-vqe, h2-molecule, python-coding

$ llmos chat "Generate a reusable skill from this work"
[LLM generates quantum-optimization.md]

✓ Trace #48 recorded
✓ Artifact created: skills/quantum-optimization.md
✓ Pattern detected: "VQE optimization" (3rd occurrence)

$ llmos commit --message "VQE optimization pattern discovered"
✓ Committed: quantum-research-2025-12-13 (a3f7c9e)
├── 48 traces
├── 1 skill (quantum-optimization.md)
├── 2 artifacts (vqe-optimized.py, h2-molecule.workflow)
└── Success rate: 92%

$ llmos promote quantum-optimization --to-team \
  --reason "Useful for quantum chemistry projects"
✓ Promoted to team:engineering
✓ All team members can now use this skill
```

---

## Web UI Design (Terminal in Browser)

### Option 1: TUI (Textual User Interface)

**Tech Stack**: Rich/Textual (Python) or Blessed (Node.js)

```
┌─────────────────────────────────────────────────────────────────┐
│ LLMos-Lite                                      alice@eng  15:42│
├─────────────────────────────────────────────────────────────────┤
│ Volume Navigator          │ Session Browser    │ Trace Viewer  │
├───────────────────────────┼────────────────────┼───────────────┤
│ 📁 System      (readonly) │ Active Sessions:   │ Session #48   │
│   ├── 23 skills           │                    │               │
│   └── 0 traces            │ ● quantum-research │ Prompt:       │
│                           │   48 traces        │ "Generate     │
│ 📁 Team: engineering      │   3 hours ago      │  reusable     │
│   ├── 15 skills           │   uncommitted      │  skill"       │
│   └── 234 traces          │                    │               │
│                           │ Recent Commits:    │ Tools Used:   │
│ 📁 User: alice   [ACTIVE] │                    │ - Write       │
│   ├── 3 skills            │ a3f7c9e            │ - Read        │
│   └── 48 traces           │ "VQE optimize"     │               │
│                           │ 2 hrs ago          │ Result:       │
│ Git Status:               │                    │ ✓ Skill       │
│ ● 1 uncommitted session   │ b7e9a2f            │   created     │
│   [Commit] [Pull]         │ "Data pipeline"    │               │
│                           │ 1 day ago          │ Pattern:      │
│                           │                    │ "VQE opt"     │
│                           │                    │ (3rd time)    │
├───────────────────────────┴────────────────────┴───────────────┤
│ > llmos chat "Help with quantum circuits"                      │
│                                                                 │
│ Assistant: I can help! I see you've been working on VQE        │
│ optimization. I'll use the quantum-optimization skill you      │
│ created earlier...                                             │
│                                                                 │
│ >_                                                              │
└─────────────────────────────────────────────────────────────────┘

[Tab] Switch Panel  [Enter] Select  [Ctrl+C] Exit  [Ctrl+S] Commit
```

### Option 2: Web Terminal (xterm.js)

**Tech Stack**: React + xterm.js + FastAPI

**Features**:
- Full terminal emulation in browser
- Copy/paste, search, themes
- Session persistence
- Mobile responsive
- Shareable URLs (e.g., `llmos.app/session/a3f7c9e`)

```typescript
// Terminal component
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';

const LLMosTerminal = () => {
  const term = new Terminal({
    theme: {
      background: '#1e1e1e',
      foreground: '#cccccc',
      cursor: '#00ff00',
    },
    fontSize: 14,
    fontFamily: 'Menlo, Monaco, monospace'
  });

  const fitAddon = new FitAddon();
  term.loadAddon(fitAddon);

  // Connect to FastAPI backend via WebSocket
  const ws = new WebSocket('ws://localhost:8000/terminal');

  ws.onmessage = (event) => {
    term.write(event.data);
  };

  term.onData((data) => {
    ws.send(data);
  });

  return <div ref={terminalRef} />;
};
```

### Option 3: Hybrid (Terminal + Panels)

**Tech Stack**: React + Monaco Editor + Custom Panels

```
┌─────────────────────────────────────────────────────────────────┐
│ LLMos-Lite Terminal                                alice@eng    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [Terminal Mode] [Panel Mode] [Workflow Mode]                  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ $ llmos chat "Optimize VQE circuit"                       │ │
│  │                                                            │ │
│  │ Assistant: I'll help optimize the VQE circuit...          │ │
│  │                                                            │ │
│  │ ✓ Trace #48 recorded                                      │ │
│  │ ✓ Pattern detected: VQE optimization (3rd occurrence)     │ │
│  │                                                            │ │
│  │ $ llmos commit                                            │ │
│  │ Commit message: VQE optimization pattern                  │ │
│  │                                                            │ │
│  │ [Metadata Panel ▼]                                        │ │
│  │ ┌────────────────────────────────────────────┐            │ │
│  │ │ Prompts: 3                                  │            │ │
│  │ │ Traces: 48                                  │            │ │
│  │ │ Success rate: 92%                           │            │ │
│  │ │ Patterns: VQE optimization                  │            │ │
│  │ │ Skills created: quantum-optimization.md     │            │ │
│  │ └────────────────────────────────────────────┘            │ │
│  │                                                            │ │
│  │ [Commit] [Cancel]                                         │ │
│  │                                                            │ │
│  │ >_                                                         │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  Sidebar:                                                       │
│  ├── Volumes (System/Team/User)                                │
│  ├── Active Sessions                                            │
│  ├── Recent Commits                                             │
│  └── Skills Library                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Enhanced Commit Messages (The Killer Feature)

### Standard Git Commit
```
commit a3f7c9e
Author: alice
Date: Dec 13 2025

Update VQE code
```

### LLMos Cognitive Commit
```
commit a3f7c9e
Author: alice@engineering
Date: Dec 13 2025 13:30:00
Session: quantum-research (3.5 hours)

📋 Goal: "Optimize VQE circuit for H2 molecule"

💬 Prompts (3):
  1. [10:05] "Help me optimize VQE circuit for H2 molecule"
     → Created initial VQE implementation

  2. [11:20] "Add support for different molecules"
     → Generalized to support any molecule

  3. [13:00] "Generate a reusable skill for this"
     → Created quantum-optimization.md skill

🔍 Execution (48 traces):
  - Tools used: WebSearch, Read, Write, Bash, Code
  - Success rate: 92% (44/48 successful)
  - Avg latency: 2.3s

🧬 Evolution:
  - Pattern detected: "VQE optimization" (3rd occurrence, 95% confidence)
  - Skill generated: quantum-optimization.md (auto-draft)
  - Ready for promotion: Yes (suggest team level)

📦 Artifacts:
  + skills/quantum-optimization.md (2.1 KB)
  + vqe-optimized.py (5.3 KB)
  + h2-molecule.workflow (1.2 KB)
  ~ traces/session_quantum-research.json (45 KB)

🎯 Impact:
  - New skill available for future VQE tasks
  - Reduces future token usage by ~80% (FOLLOWER mode enabled)
  - Team benefit: High (quantum chemistry is common task)

---

VQE optimization pattern discovered

This session represents the 3rd time the user has worked on
VQE optimization. The evolution engine detected the pattern
and auto-generated the quantum-optimization skill.

Recommend promoting to team:engineering for broader use.
```

### Commit Viewer UI

```
┌─────────────────────────────────────────────────────────────────┐
│ Commit: a3f7c9e - VQE optimization pattern                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Session Timeline                                               │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  10:05          11:20          13:00          13:30             │
│  Start          Prompt 2       Prompt 3       Commit            │
│                                                                 │
│  💬 Prompts (Click to expand)                                   │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ 1. [10:05] "Help me optimize VQE circuit..."              │ │
│  │    → Created initial VQE implementation                   │ │
│  │    Tools: WebSearch, Read, Write                          │ │
│  │    Traces: #1-15                                          │ │
│  │                                                            │ │
│  │ 2. [11:20] "Add support for different molecules"         │ │
│  │    → Generalized to support any molecule                 │ │
│  │    Tools: Write, Bash                                     │ │
│  │    Traces: #16-35                                         │ │
│  │                                                            │ │
│  │ 3. [13:00] "Generate a reusable skill from this"         │ │
│  │    → Created quantum-optimization.md skill               │ │
│  │    Tools: Write                                           │ │
│  │    Traces: #36-48                                         │ │
│  │    ⭐ Pattern detected!                                    │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  📦 Artifacts                                                   │
│  ├── quantum-optimization.md [View] [Diff]                     │
│  ├── vqe-optimized.py [View] [Run]                             │
│  └── h2-molecule.workflow [View] [Execute]                     │
│                                                                 │
│  🧬 Evolution Analysis                                          │
│  Pattern: "VQE optimization" (3rd occurrence)                  │
│  Confidence: 95%                                                │
│  Recommendation: Promote to team:engineering                   │
│                                                                 │
│  [Replay Session] [Promote to Team] [Share]                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Session Storage Format

### Directory Structure
```
volumes/
├── system/
│   ├── skills/
│   ├── traces/
│   └── .git/
├── teams/
│   └── engineering/
│       ├── skills/
│       ├── traces/
│       ├── sessions/           # ← NEW
│       │   ├── alice/
│       │   │   └── quantum-research-2025-12-13.json
│       │   └── bob/
│       │       └── graphql-optimization-2025-12-10.json
│       └── .git/
└── users/
    └── alice/
        ├── skills/
        ├── traces/
        ├── sessions/           # ← NEW
        │   ├── active/
        │   │   └── quantum-research.json  # Active session
        │   └── committed/
        │       └── data-pipeline-2025-12-10.json
        └── .git/
```

### Session File Format

`sessions/active/quantum-research.json`:

```json
{
  "session_id": "quantum-research-2025-12-13",
  "user_id": "alice",
  "team_id": "engineering",
  "status": "active",
  "started_at": "2025-12-13T10:00:00Z",
  "last_activity": "2025-12-13T13:30:00Z",

  "goal": "Optimize VQE circuit for H2 molecule",

  "prompts": [
    {
      "timestamp": "2025-12-13T10:05:00Z",
      "text": "Help me optimize VQE circuit for H2 molecule",
      "response_summary": "Created initial VQE implementation",
      "trace_ids": ["trace_001", "trace_002", "..."],
      "tools_used": ["WebSearch", "Read", "Write"],
      "success": true
    },
    {
      "timestamp": "2025-12-13T11:20:00Z",
      "text": "Add support for different molecules",
      "response_summary": "Generalized to support any molecule",
      "trace_ids": ["trace_016", "trace_017", "..."],
      "tools_used": ["Write", "Bash"],
      "success": true
    }
  ],

  "trace_ids": [
    "trace_001", "trace_002", "...", "trace_048"
  ],

  "artifacts": [
    {
      "path": "skills/quantum-optimization.md",
      "type": "skill",
      "created_at": "2025-12-13T13:00:00Z",
      "size_bytes": 2048
    },
    {
      "path": "vqe-optimized.py",
      "type": "code",
      "created_at": "2025-12-13T10:30:00Z",
      "size_bytes": 5300
    }
  ],

  "evolution": {
    "patterns_detected": [
      {
        "name": "VQE optimization",
        "occurrence_count": 3,
        "confidence": 0.95,
        "skill_draft": "skills/quantum-optimization.md"
      }
    ],
    "skills_generated": ["quantum-optimization"],
    "auto_promote_suggested": true,
    "promote_to_level": "team"
  },

  "metrics": {
    "total_traces": 48,
    "successful_traces": 44,
    "success_rate": 0.92,
    "avg_latency_ms": 2300,
    "total_tokens_used": 125000,
    "tools_used": ["WebSearch", "Read", "Write", "Bash", "Code"]
  },

  "git_info": {
    "uncommitted_changes": true,
    "files_modified": ["skills/quantum-optimization.md", "vqe-optimized.py"],
    "ready_to_commit": true
  }
}
```

---

## Implementation Plan

### Phase 1: Terminal Backend (2 weeks)

**Goal**: CLI that works with existing llmos-lite backend

**Tasks**:
- [ ] Create `llmos` CLI tool (Python Click or Typer)
- [ ] Implement volume navigation (`llmos volume`)
- [ ] Implement session management (`llmos start/resume/commit`)
- [ ] Add session storage (JSON files)
- [ ] Enhanced commit messages with metadata
- [ ] Git integration for commits

**Files**:
```
llmos-lite/
├── cli/
│   ├── __init__.py
│   ├── main.py              # Main CLI entry point
│   ├── commands/
│   │   ├── volume.py        # Volume commands
│   │   ├── session.py       # Session commands
│   │   ├── chat.py          # Chat commands
│   │   └── search.py        # Search commands
│   └── formatters/
│       ├── commit.py        # Cognitive commit formatter
│       └── session.py       # Session display formatter
```

### Phase 2: Terminal UI (2 weeks)

**Goal**: Rich TUI using Textual or Rich

**Tasks**:
- [ ] Create 3-panel layout
- [ ] Volume navigator panel
- [ ] Session browser panel
- [ ] Trace viewer panel
- [ ] Keyboard shortcuts
- [ ] Theme support

**Tech**: Python Textual

**Files**:
```
llmos-lite/
├── tui/
│   ├── __init__.py
│   ├── app.py               # Main TUI app
│   ├── panels/
│   │   ├── volume_nav.py
│   │   ├── session_browser.py
│   │   └── trace_viewer.py
│   └── widgets/
│       ├── commit_card.py
│       └── session_card.py
```

### Phase 3: Web Terminal (3 weeks)

**Goal**: Browser-based terminal with xterm.js

**Tasks**:
- [ ] WebSocket backend for terminal
- [ ] xterm.js frontend
- [ ] Session persistence
- [ ] Shareable URLs
- [ ] Copy/paste support

**Tech**: FastAPI + xterm.js + React

**Files**:
```
llmos-lite/
├── api/
│   └── terminal.py          # WebSocket endpoint
└── ui/
    ├── terminal/
    │   ├── TerminalComponent.tsx
    │   ├── SessionBrowser.tsx
    │   └── CommitViewer.tsx
```

### Phase 4: Enhanced Features (2 weeks)

**Goal**: Advanced session features

**Tasks**:
- [ ] Session replay (step-by-step)
- [ ] Commit search by prompts/goals
- [ ] Collaborative sessions (shared team sessions)
- [ ] Session templates
- [ ] Export sessions (PDF, HTML)

---

## Success Metrics

### User Experience
- ✅ Users can navigate volumes without confusion
- ✅ Sessions are discoverable and resumable
- ✅ Commit messages capture the "why" not just "what"
- ✅ Team collaboration is seamless

### Technical
- ✅ 100% of sessions tracked in Git
- ✅ <2s to load and resume a session
- ✅ Commit messages include all cognitive metadata
- ✅ Full-text search across prompts/goals

### Business
- ✅ Reduced learning curve (onboarding <30 min)
- ✅ Increased skill reuse (70%+ of tasks use existing skills)
- ✅ Faster team collaboration (skills shared within hours)

---

## Conclusion

This UI/UX proposal transforms LLMos-lite from a **backend API** to a **cognitive workbench** where:

1. **Git becomes a cognitive file system** capturing process, not just artifacts
2. **Sessions are first-class citizens** - discoverable, resumable, shareable
3. **Commits tell the story** - prompts, traces, patterns, impact
4. **Teams collaborate naturally** - volume hierarchy enables organic knowledge sharing
5. **Learning is automatic** - evolution engine extracts patterns from rich commit metadata

The terminal interface isn't just a "UI" - it's a **window into the system's mind**, revealing how knowledge evolves from individual sessions to team skills to system-wide patterns.

**Next Steps**: Approve this proposal → Begin Phase 1 implementation

---

**Questions for Discussion**:
1. TUI vs Web Terminal vs Hybrid?
2. Default commit format (YAML vs JSON in commit message)?
3. Session auto-commit frequency (hourly? on close? manual only)?
4. Team session sharing (realtime collaboration or async only)?
