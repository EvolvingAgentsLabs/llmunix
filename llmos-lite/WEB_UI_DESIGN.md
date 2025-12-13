# LLMos-Lite Web UI Design: Terminal-Style Interface

> **Web-Based Terminal UI with Git-Aware Volume Navigation**

**Date**: December 2025
**Version**: 1.0
**Status**: Design Specification

---

## Executive Summary

### Design Philosophy
A **web-based terminal-style interface** that combines the familiarity of CLI with the power of modern web UI:
- **Terminal aesthetic**: Monospace fonts, dark theme, terminal-like interactions
- **Web capabilities**: Interactive panels, drag-and-drop, real-time updates
- **Git-aware**: Every interaction is backed by Git, visible in the UI

### Three-Panel Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│ LLMos-Lite Web Terminal                            alice@engineering│
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────────┐  ┌──────────────────────┐  ┌──────────────────┐│
│  │   PANEL 1     │  │      PANEL 2         │  │     PANEL 3      ││
│  │   VOLUMES     │  │  SESSION/CHAT        │  │  ARTIFACT MAP    ││
│  │               │  │                      │  │                  ││
│  │ ● System      │  │  ┌────────────────┐ │  │  ┌─────────────┐ ││
│  │ ● Team: eng   │  │  │ Chat Interface │ │  │  │  Workflow   │ ││
│  │ ● User: alice │  │  │                │ │  │  │   Graph     │ ││
│  │               │  │  │ > Help me...   │ │  │  │             │ ││
│  │ Sessions:     │  │  │                │ │  │  │   [Node A]  │ ││
│  │ ● quantum-res │  │  │ ✓ Trace #48    │ │  │  │      ↓      │ ││
│  │   48 traces   │  │  │ ✓ Pattern      │ │  │  │   [Node B]  │ ││
│  │   3h ago      │  │  │   detected     │ │  │  │             │ ││
│  │               │  │  └────────────────┘ │  │  └─────────────┘ ││
│  │ Cron Updates: │  │                      │  │                  ││
│  │ ● Evolution   │  │  ┌────────────────┐ │  │  Selected Node:  ││
│  │   5 patterns  │  │  │  Artifacts     │ │  │  ┌─────────────┐ ││
│  │   2h ago      │  │  │  - skill.md    │ │  │  │ quantum-vqe │ ││
│  │               │  │  │  - code.py     │ │  │  │             │ ││
│  │ Git Status:   │  │  │  - workflow    │ │  │  │ [Edit Mode] │ ││
│  │ ● 3 uncommit  │  │  └────────────────┘ │  │  │             │ ││
│  │   [Commit]    │  │                      │  │  │ inputs:     │ ││
│  │               │  │  Cron Mode:          │  │  │ - iter: 100 │ ││
│  └───────────────┘  │  [View Evolution Log]│  │  └─────────────┘ ││
│                     └──────────────────────┘  └──────────────────┘│
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Panel 1: Volumes Navigator

### Purpose
Navigate the 3-level Git-backed hierarchy and manage sessions/cron jobs.

### Structure

```
┌─────────────────────────────────────┐
│ VOLUMES                             │
├─────────────────────────────────────┤
│                                     │
│ 📁 System (readonly)                │
│   ├── 23 skills                     │
│   ├── 0 active sessions             │
│   └── Last cron: 2h ago             │
│                                     │
│ 📁 Team: engineering                │
│   ├── 15 skills                     │
│   ├── 3 active team sessions        │
│   ├── Bob: graphql-opt (active)     │
│   ├── Carol: api-design (2h ago)    │
│   └── Last cron: 12h ago            │
│                                     │
│ 📁 User: alice ● [ACTIVE]           │
│   ├── 3 skills                      │
│   ├── 2 active sessions             │
│   └── Last activity: now            │
│                                     │
├─────────────────────────────────────┤
│ SESSIONS (User: alice)              │
├─────────────────────────────────────┤
│                                     │
│ ● quantum-research                  │
│   ├── 48 traces                     │
│   ├── Started: 3h ago               │
│   ├── Artifacts: 3                  │
│   ├── Patterns: 1 detected          │
│   └── Status: Uncommitted           │
│   [Resume] [Commit] [Share]         │
│                                     │
│ ● data-pipeline                     │
│   ├── 12 traces                     │
│   ├── Started: 2d ago               │
│   ├── Artifacts: 2                  │
│   └── Status: Committed (b7e9a2f)   │
│   [View] [Clone]                    │
│                                     │
├─────────────────────────────────────┤
│ CRON UPDATES                        │
├─────────────────────────────────────┤
│                                     │
│ 🔄 Evolution Cron (User)            │
│   ├── Status: Completed             │
│   ├── Ran: 2h ago                   │
│   ├── Analyzed: 95 traces           │
│   ├── Patterns: 5 detected          │
│   ├── Skills: 2 generated           │
│   └── Next run: 22h                 │
│   [View Log] [Run Now]              │
│                                     │
│ 🔄 Evolution Cron (Team)            │
│   ├── Status: Scheduled             │
│   ├── Last run: 12h ago             │
│   ├── Patterns: 3 promoted          │
│   └── Next run: 12h                 │
│   [View Log]                        │
│                                     │
├─────────────────────────────────────┤
│ GIT STATUS                          │
├─────────────────────────────────────┤
│                                     │
│ Branch: main                        │
│ Volume: alice@engineering           │
│                                     │
│ Uncommitted Changes (3):            │
│ M skills/quantum-optimization.md    │
│ A vqe-optimized.py                  │
│ A sessions/quantum-research.json    │
│                                     │
│ [Commit All] [View Diff]            │
│                                     │
└─────────────────────────────────────┘
```

### Interactions

**Volume Selection**:
```typescript
// Click on volume → Updates Panel 2 & 3 context
onClick(volume: 'system' | 'team' | 'user') {
  setActiveVolume(volume);
  loadSessions(volume);
  loadArtifacts(volume);
}
```

**Session Selection**:
```typescript
// Click on session → Loads in Panel 2
onClick(sessionId: string) {
  setActiveSession(sessionId);
  loadChatHistory(sessionId);
  loadArtifacts(sessionId);
  loadWorkflowGraph(sessionId);
}
```

**Cron Selection**:
```typescript
// Click on cron update → Shows log in Panel 2
onClick(cronId: string) {
  setViewMode('cron');
  loadCronLog(cronId);
  loadDetectedPatterns(cronId);
}
```

---

## Panel 2: Session Viewer / Chat Interface

### Two Modes: Session Mode & Cron Mode

### Mode 1: Session Mode (Active Work)

```
┌──────────────────────────────────────────┐
│ SESSION: quantum-research                │
│ Status: Active | 48 traces | 3h ago      │
├──────────────────────────────────────────┤
│                                          │
│ ┌──────────────────────────────────────┐ │
│ │ CHAT INTERFACE                       │ │
│ │                                      │ │
│ │ [10:05] You:                         │ │
│ │ Help me optimize VQE circuit for H2  │ │
│ │                                      │ │
│ │ [10:06] Assistant:                   │ │
│ │ I'll help optimize the VQE circuit.  │ │
│ │ Let me start by analyzing...         │ │
│ │                                      │ │
│ │ ✓ Trace #1-15 executed               │ │
│ │ ✓ Artifact created: vqe-initial.py   │ │
│ │                                      │ │
│ │ [11:20] You:                         │ │
│ │ Add support for different molecules  │ │
│ │                                      │ │
│ │ [11:21] Assistant:                   │ │
│ │ I'll generalize the code...          │ │
│ │                                      │ │
│ │ ✓ Trace #16-35 executed              │ │
│ │ ✓ Artifact updated: vqe-optimized.py │ │
│ │                                      │ │
│ │ [13:00] You:                         │ │
│ │ Generate a reusable skill from this  │ │
│ │                                      │ │
│ │ [13:01] Assistant:                   │ │
│ │ ⭐ Pattern detected! This is the     │ │
│ │ 3rd VQE optimization task.           │ │
│ │                                      │ │
│ │ I've created:                        │ │
│ │ - quantum-optimization.md (skill)    │ │
│ │                                      │ │
│ │ ✓ Trace #36-48 executed              │ │
│ │ ✓ Pattern: VQE optimization (95%)    │ │
│ │                                      │ │
│ └──────────────────────────────────────┘ │
│                                          │
│ ┌──────────────────────────────────────┐ │
│ │ > Type your message...               │ │
│ │                                      │ │
│ │ [Send] [Attach Workflow] [Settings]  │ │
│ └──────────────────────────────────────┘ │
│                                          │
├──────────────────────────────────────────┤
│ SESSION ARTIFACTS                        │
├──────────────────────────────────────────┤
│                                          │
│ 📄 Skills (1):                           │
│ ├── quantum-optimization.md [View]       │
│                                          │
│ 📄 Code (1):                             │
│ ├── vqe-optimized.py [Edit] [Run]        │
│                                          │
│ 🔀 Workflows (1):                        │
│ ├── h2-molecule.workflow [View Graph]    │
│                                          │
│ 📊 Traces (48):                          │
│ ├── View All | Filter | Export          │
│                                          │
├──────────────────────────────────────────┤
│ EVOLUTION STATUS                         │
├──────────────────────────────────────────┤
│                                          │
│ 🧬 Patterns Detected (1):                │
│                                          │
│ VQE Optimization                         │
│ ├── Occurrence: 3rd time                 │
│ ├── Confidence: 95%                      │
│ ├── Skill: quantum-optimization.md       │
│ └── Recommend: Promote to team           │
│                                          │
│ [Promote to Team] [Ignore Pattern]       │
│                                          │
├──────────────────────────────────────────┤
│ ACTIONS                                  │
├──────────────────────────────────────────┤
│                                          │
│ [Commit Session] [Share with Team]       │
│ [Export Report] [Replay Session]         │
│                                          │
└──────────────────────────────────────────┘
```

### Mode 2: Cron Mode (Evolution Log)

```
┌──────────────────────────────────────────┐
│ CRON: Evolution (User)                   │
│ Ran: 2h ago | Duration: 3m 24s           │
├──────────────────────────────────────────┤
│                                          │
│ ┌──────────────────────────────────────┐ │
│ │ EXECUTION LOG                        │ │
│ │                                      │ │
│ │ [14:00:00] Starting evolution cron   │ │
│ │ [14:00:01] Loading traces from:      │ │
│ │            /volumes/users/alice/     │ │
│ │ [14:00:05] Found 95 traces           │ │
│ │ [14:00:10] Analyzing patterns...     │ │
│ │                                      │ │
│ │ [14:01:23] Pattern detected:         │ │
│ │            "VQE optimization"        │ │
│ │            Occurrences: 3            │ │
│ │            Confidence: 95%           │ │
│ │            Traces: #12, #34, #48     │ │
│ │                                      │ │
│ │ [14:01:45] Generating skill draft... │ │
│ │ [14:02:10] Skill created:            │ │
│ │            quantum-optimization.md   │ │
│ │                                      │ │
│ │ [14:02:11] Pattern detected:         │ │
│ │            "API endpoint creation"   │ │
│ │            Occurrences: 5            │ │
│ │            Confidence: 87%           │ │
│ │            Traces: #5, #18, #29...   │ │
│ │                                      │ │
│ │ [14:02:45] Generating skill draft... │ │
│ │ [14:03:10] Skill created:            │ │
│ │            api-endpoint-pattern.md   │ │
│ │                                      │ │
│ │ [14:03:24] Evolution complete        │ │
│ │            Patterns: 5 detected      │ │
│ │            Skills: 2 created         │ │
│ │            Committed: e9f2a1c        │ │
│ │                                      │ │
│ └──────────────────────────────────────┘ │
│                                          │
├──────────────────────────────────────────┤
│ PATTERNS DETECTED (5)                    │
├──────────────────────────────────────────┤
│                                          │
│ 1. VQE Optimization                      │
│    ├── Occurrences: 3                    │
│    ├── Confidence: 95%                   │
│    ├── Skill: quantum-optimization.md    │
│    └── [View Traces] [View Skill]        │
│                                          │
│ 2. API Endpoint Creation                 │
│    ├── Occurrences: 5                    │
│    ├── Confidence: 87%                   │
│    ├── Skill: api-endpoint-pattern.md    │
│    └── [View Traces] [View Skill]        │
│                                          │
│ 3. Data Transformation Pipeline          │
│    ├── Occurrences: 4                    │
│    ├── Confidence: 82%                   │
│    ├── Skill: None (threshold not met)   │
│    └── [View Traces]                     │
│                                          │
│ ... (2 more)                             │
│                                          │
├──────────────────────────────────────────┤
│ SKILLS GENERATED (2)                     │
├──────────────────────────────────────────┤
│                                          │
│ ✨ quantum-optimization.md               │
│    [View] [Edit] [Promote to Team]       │
│                                          │
│ ✨ api-endpoint-pattern.md               │
│    [View] [Edit] [Promote to Team]       │
│                                          │
├──────────────────────────────────────────┤
│ GIT COMMIT                               │
├──────────────────────────────────────────┤
│                                          │
│ Commit: e9f2a1c                          │
│ Author: alice-cron                       │
│ Message: Evolution: 2 skills from 5      │
│          patterns detected               │
│                                          │
│ [View Commit] [View Diff]                │
│                                          │
└──────────────────────────────────────────┘
```

---

## Panel 3: Artifact Map & Node Editor

### Two Views: Graph View & Node Detail View

### View 1: Workflow Graph (React Flow)

```
┌──────────────────────────────────────────┐
│ WORKFLOW GRAPH                           │
├──────────────────────────────────────────┤
│                                          │
│  Controls: [Fit] [Zoom +/-] [Layout]    │
│                                          │
│  ┌────────────────────────────────────┐  │
│  │                                    │  │
│  │    ┌──────────────┐                │  │
│  │    │ Hamiltonian  │                │  │
│  │    │   Node       │                │  │
│  │    │ ✓ Executed   │                │  │
│  │    └──────┬───────┘                │  │
│  │           │                        │  │
│  │           ▼                        │  │
│  │    ┌──────────────┐                │  │
│  │    │  VQE Node    │ ◄── Selected  │  │
│  │    │ ⏸ Running    │                │  │
│  │    └──────┬───────┘                │  │
│  │           │                        │  │
│  │           ▼                        │  │
│  │    ┌──────────────┐                │  │
│  │    │  Plot Node   │                │  │
│  │    │ ⏸ Pending    │                │  │
│  │    └──────┬───────┘                │  │
│  │           │                        │  │
│  │           ▼                        │  │
│  │    ┌──────────────┐                │  │
│  │    │ Export Node  │                │  │
│  │    │ ⏸ Pending    │                │  │
│  │    └──────────────┘                │  │
│  │                                    │  │
│  └────────────────────────────────────┘  │
│                                          │
│  Status:                                 │
│  ├── Nodes: 4 total, 1 done, 1 running  │
│  ├── Execution: 45% complete             │
│  └── Runtime: 2.3s                       │
│                                          │
│  [Run Workflow] [Pause] [Step Through]  │
│  [Export as Code] [Share]                │
│                                          │
├──────────────────────────────────────────┤
│ NODE LIBRARY                             │
├──────────────────────────────────────────┤
│                                          │
│ Search: [____________] 🔍                │
│                                          │
│ Categories:                              │
│ ├─ Quantum (3 nodes)                     │
│ │  ├── 🔬 VQE Node [Drag]                │
│ │  ├── 🔬 Hamiltonian Node [Drag]        │
│ │  └── 🔬 Bloch Sphere [Drag]            │
│ ├─ Data (5 nodes)                        │
│ │  ├── 📊 Plot Node [Drag]               │
│ │  ├── 📊 Transform Node [Drag]          │
│ │  └── ...                               │
│ ├─ 3D Graphics (4 nodes)                 │
│ └─ Electronics (3 nodes)                 │
│                                          │
└──────────────────────────────────────────┘
```

### View 2: Node Detail Viewer/Editor

```
┌──────────────────────────────────────────┐
│ NODE DETAIL: VQE Node                    │
├──────────────────────────────────────────┤
│                                          │
│ [View Mode] [Edit Mode] [Code Mode]     │
│                                          │
│ ┌──────────────────────────────────────┐ │
│ │ CONFIGURATION                        │ │
│ │                                      │ │
│ │ Node ID: vqe-node-1                  │ │
│ │ Type: python-wasm                    │ │
│ │ Skill: quantum-vqe-node.md           │ │
│ │                                      │ │
│ │ Inputs:                              │ │
│ │ ┌────────────────────────────────┐   │ │
│ │ │ iterations:   [100      ]      │   │ │
│ │ │               number           │   │ │
│ │ │                                │   │ │
│ │ │ ansatz_type:  [UCCSD    ▼]     │   │ │
│ │ │               string           │   │ │
│ │ │                                │   │ │
│ │ │ hamiltonian:  [from input]     │   │ │
│ │ │               object           │   │ │
│ │ └────────────────────────────────┘   │ │
│ │                                      │ │
│ │ Outputs:                             │ │
│ │ ┌────────────────────────────────┐   │ │
│ │ │ eigenvalue:   -1.137           │   │ │
│ │ │               number           │   │ │
│ │ │                                │   │ │
│ │ │ convergence:  [View Array]     │   │ │
│ │ │               array            │   │ │
│ │ └────────────────────────────────┘   │ │
│ │                                      │ │
│ └──────────────────────────────────────┘ │
│                                          │
│ ┌──────────────────────────────────────┐ │
│ │ CODE PREVIEW                         │ │
│ │                                      │ │
│ │ ```python                            │ │
│ │ def execute(inputs):                 │ │
│ │     # VQE optimization               │ │
│ │     hamiltonian = inputs['hamilto... │ │
│ │     iterations = inputs['iteration...│ │
│ │                                      │ │
│ │     # Run VQE                        │ │
│ │     result = vqe_optimize(...)       │ │
│ │                                      │ │
│ │     return {                         │ │
│ │         "eigenvalue": result.eigv... │ │
│ │         "convergence": result.conv...│ │
│ │     }                                │ │
│ │ ```                                  │ │
│ │                                      │ │
│ │ [Edit Code] [Test Run] [Validate]    │ │
│ │                                      │ │
│ └──────────────────────────────────────┘ │
│                                          │
│ ┌──────────────────────────────────────┐ │
│ │ EXECUTION STATUS                     │ │
│ │                                      │ │
│ │ Status: ✓ Completed                  │ │
│ │ Runtime: 2.3s                        │ │
│ │ Memory: 45 MB                        │ │
│ │                                      │ │
│ │ Logs:                                │ │
│ │ [14:05:23] Starting VQE...           │ │
│ │ [14:05:25] Iteration 50/100...       │ │
│ │ [14:05:27] Converged!                │ │
│ │ [14:05:27] Eigenvalue: -1.137        │ │
│ │                                      │ │
│ └──────────────────────────────────────┘ │
│                                          │
│ ┌──────────────────────────────────────┐ │
│ │ PREVIEW                              │ │
│ │                                      │ │
│ │ [Convergence Plot]                   │ │
│ │  Energy                              │ │
│ │   0.0 ┤                              │ │
│ │       │                              │ │
│ │  -1.0 ┤        ╱───────              │ │
│ │       │    ╱───                      │ │
│ │  -2.0 ┤╱───                          │ │
│ │       └────────────────→             │ │
│ │       0    50   100  Iterations      │ │
│ │                                      │ │
│ └──────────────────────────────────────┘ │
│                                          │
│ [Save Changes] [Reset] [Delete Node]    │
│                                          │
└──────────────────────────────────────────┘
```

---

## Technical Architecture

### Tech Stack

```typescript
// Frontend
const stack = {
  framework: "Next.js 14 (App Router)",
  ui: "React 18",
  styling: "Tailwind CSS + shadcn/ui",
  terminal: "xterm.js",
  workflow: "React Flow",
  editor: "Monaco Editor (VS Code editor)",
  state: "Zustand",
  realtime: "WebSocket",
  charts: "Recharts or D3.js"
};

// Backend (already exists)
const backend = {
  api: "FastAPI",
  storage: "Git volumes",
  llm: "Anthropic Claude",
  execution: "Pyodide (browser)"
};
```

### Component Structure

```
llmos-lite/
└── ui/
    ├── app/                          # Next.js App Router
    │   ├── layout.tsx                # Root layout
    │   ├── page.tsx                  # Main terminal page
    │   └── api/                      # API routes (proxy to FastAPI)
    │
    ├── components/
    │   ├── layout/
    │   │   ├── TerminalLayout.tsx    # 3-panel layout
    │   │   ├── ThemeProvider.tsx     # Dark theme
    │   │   └── Header.tsx            # Top bar
    │   │
    │   ├── panel1-volumes/
    │   │   ├── VolumesPanel.tsx      # Main panel
    │   │   ├── VolumeTree.tsx        # System/Team/User tree
    │   │   ├── SessionList.tsx       # Active sessions
    │   │   ├── CronList.tsx          # Cron updates
    │   │   └── GitStatus.tsx         # Git status widget
    │   │
    │   ├── panel2-session/
    │   │   ├── SessionPanel.tsx      # Main panel
    │   │   ├── ChatInterface.tsx     # Chat with LLM
    │   │   ├── CronViewer.tsx        # Evolution log
    │   │   ├── ArtifactList.tsx      # Session artifacts
    │   │   └── EvolutionStatus.tsx   # Pattern detection
    │   │
    │   ├── panel3-artifacts/
    │   │   ├── ArtifactPanel.tsx     # Main panel
    │   │   ├── WorkflowGraph.tsx     # React Flow graph
    │   │   ├── NodeLibrary.tsx       # Draggable nodes
    │   │   ├── NodeEditor.tsx        # Node detail editor
    │   │   └── PreviewRenderer.tsx   # Output preview
    │   │
    │   ├── shared/
    │   │   ├── Terminal.tsx          # xterm.js wrapper
    │   │   ├── CodeEditor.tsx        # Monaco editor
    │   │   ├── MarkdownViewer.tsx    # Skill viewer
    │   │   ├── CommitDialog.tsx      # Git commit UI
    │   │   └── Button.tsx            # Terminal-style button
    │   │
    │   └── workflows/
    │       ├── nodes/                # Custom React Flow nodes
    │       │   ├── QuantumVQENode.tsx
    │       │   ├── PlotNode.tsx
    │       │   └── ...
    │       └── edges/                # Custom edges
    │
    ├── lib/
    │   ├── api-client.ts             # FastAPI client
    │   ├── websocket.ts              # WebSocket manager
    │   ├── workflow-executor.ts      # Already exists
    │   ├── pyodide-runner.ts         # Already exists
    │   └── git-utils.ts              # Git operations
    │
    ├── hooks/
    │   ├── useVolumes.ts             # Volume state
    │   ├── useSessions.ts            # Session management
    │   ├── useChat.ts                # Chat interface
    │   ├── useWorkflow.ts            # Workflow state
    │   └── useRealtime.ts            # WebSocket updates
    │
    ├── stores/
    │   ├── volumeStore.ts            # Zustand store
    │   ├── sessionStore.ts           # Zustand store
    │   └── workflowStore.ts          # Zustand store
    │
    └── styles/
        └── terminal-theme.css        # Terminal aesthetic
```

---

## Terminal Aesthetic Design System

### Colors (Dark Theme)

```css
:root {
  /* Background */
  --bg-primary: #0a0e14;      /* Deep dark blue-black */
  --bg-secondary: #131721;    /* Panel background */
  --bg-tertiary: #1c212b;     /* Hover states */

  /* Foreground */
  --fg-primary: #e6e6e6;      /* Main text */
  --fg-secondary: #8a8a8a;    /* Secondary text */
  --fg-tertiary: #4a4a4a;     /* Disabled text */

  /* Accents */
  --accent-green: #00ff88;    /* Success, active items */
  --accent-blue: #00d4ff;     /* Links, info */
  --accent-yellow: #ffcc00;   /* Warnings */
  --accent-red: #ff4444;      /* Errors */
  --accent-purple: #bb00ff;   /* Special */

  /* Terminal colors */
  --terminal-cursor: #00ff88;
  --terminal-selection: rgba(0, 255, 136, 0.3);

  /* Borders */
  --border: #2a2e3a;
  --border-focus: #00ff88;
}
```

### Typography

```css
/* Monospace fonts for terminal feel */
:root {
  --font-mono: 'JetBrains Mono', 'Fira Code', 'Menlo', 'Monaco', monospace;
  --font-sans: 'Inter', system-ui, sans-serif;
}

body {
  font-family: var(--font-mono);
  font-size: 14px;
  line-height: 1.5;
  background: var(--bg-primary);
  color: var(--fg-primary);
}

/* Headings */
h1, h2, h3 {
  font-family: var(--font-mono);
  font-weight: 600;
  letter-spacing: -0.5px;
}
```

### Component Styles

```css
/* Panel borders */
.panel {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 16px;
}

/* Terminal-style buttons */
.btn-terminal {
  background: transparent;
  border: 1px solid var(--accent-green);
  color: var(--accent-green);
  font-family: var(--font-mono);
  padding: 6px 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-terminal:hover {
  background: var(--accent-green);
  color: var(--bg-primary);
  box-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
}

/* Active indicators */
.status-active::before {
  content: '●';
  color: var(--accent-green);
  margin-right: 8px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Code blocks */
pre {
  background: var(--bg-primary);
  border: 1px solid var(--border);
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
}

code {
  font-family: var(--font-mono);
  color: var(--accent-blue);
}

/* Scrollbars */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--bg-primary);
}

::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--accent-green);
}
```

---

## Key Features Implementation

### Feature 1: Real-Time Session Updates

```typescript
// WebSocket connection for live updates
const useRealtime = (sessionId: string) => {
  const [ws, setWs] = useState<WebSocket | null>(null);

  useEffect(() => {
    const socket = new WebSocket(`ws://localhost:8000/ws/${sessionId}`);

    socket.onmessage = (event) => {
      const update = JSON.parse(event.data);

      switch (update.type) {
        case 'trace_added':
          // Update trace count in Panel 1
          // Add trace to Panel 2 chat
          break;

        case 'artifact_created':
          // Update artifact list in Panel 2
          // Update workflow graph in Panel 3
          break;

        case 'pattern_detected':
          // Show notification
          // Update evolution status in Panel 2
          break;

        case 'cron_completed':
          // Update cron status in Panel 1
          // Show notification
          break;
      }
    };

    setWs(socket);

    return () => socket.close();
  }, [sessionId]);

  return ws;
};
```

### Feature 2: Git Commit Dialog

```typescript
// Enhanced commit dialog with cognitive metadata
interface CommitDialogProps {
  sessionId: string;
  onCommit: () => void;
}

const CommitDialog: React.FC<CommitDialogProps> = ({ sessionId, onCommit }) => {
  const session = useSession(sessionId);
  const [message, setMessage] = useState('');
  const [includeMetadata, setIncludeMetadata] = useState(true);

  const handleCommit = async () => {
    const commitData = {
      session_id: sessionId,
      message: message,
      metadata: includeMetadata ? {
        prompts: session.prompts.map(p => ({
          timestamp: p.timestamp,
          text: p.text,
          summary: p.response_summary
        })),
        trace_count: session.trace_ids.length,
        success_rate: session.metrics.success_rate,
        patterns: session.evolution.patterns_detected,
        artifacts: session.artifacts.map(a => ({
          path: a.path,
          type: a.type,
          size: a.size_bytes
        }))
      } : undefined
    };

    await api.post('/sessions/commit', commitData);
    onCommit();
  };

  return (
    <Dialog>
      <DialogContent className="terminal-dialog">
        <h2>Commit Session: {session.goal}</h2>

        <div className="commit-preview">
          <h3>Commit Message</h3>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Describe what you accomplished..."
            className="terminal-input"
          />
        </div>

        <div className="metadata-preview">
          <h3>Cognitive Metadata</h3>
          <label>
            <input
              type="checkbox"
              checked={includeMetadata}
              onChange={(e) => setIncludeMetadata(e.target.checked)}
            />
            Include prompts, traces, and patterns in commit
          </label>

          {includeMetadata && (
            <pre className="metadata-yaml">
{`---
prompts: ${session.prompts.length}
traces: ${session.trace_ids.length}
success_rate: ${(session.metrics.success_rate * 100).toFixed(0)}%
patterns_detected: ${session.evolution.patterns_detected.length}
artifacts: ${session.artifacts.length}
---`}
            </pre>
          )}
        </div>

        <div className="commit-actions">
          <button onClick={handleCommit} className="btn-terminal">
            Commit
          </button>
          <button onClick={() => close()} className="btn-terminal-secondary">
            Cancel
          </button>
        </div>
      </DialogContent>
    </Dialog>
  );
};
```

### Feature 3: Workflow Graph with Live Execution

```typescript
// React Flow graph with execution state
const WorkflowGraph: React.FC = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [executionState, setExecutionState] = useState<ExecutionState>({});

  // Custom node component with execution status
  const VQENode = ({ data }: NodeProps) => {
    const status = executionState[data.id];

    return (
      <div className={`custom-node ${status?.state}`}>
        <div className="node-header">
          <span className="node-icon">🔬</span>
          <span className="node-title">{data.label}</span>
        </div>

        <div className="node-status">
          {status?.state === 'running' && (
            <span className="status-running">⏸ Running...</span>
          )}
          {status?.state === 'completed' && (
            <span className="status-completed">✓ Completed</span>
          )}
          {status?.state === 'pending' && (
            <span className="status-pending">⏸ Pending</span>
          )}
        </div>

        {status?.output && (
          <div className="node-output">
            <small>eigenvalue: {status.output.eigenvalue}</small>
          </div>
        )}
      </div>
    );
  };

  // Execute workflow
  const runWorkflow = async () => {
    const workflow = { nodes, edges };

    // Execute via existing workflow-executor.ts
    const executor = new WorkflowExecutor(workflow);

    executor.on('node_start', (nodeId) => {
      setExecutionState(prev => ({
        ...prev,
        [nodeId]: { state: 'running' }
      }));
    });

    executor.on('node_complete', (nodeId, output) => {
      setExecutionState(prev => ({
        ...prev,
        [nodeId]: { state: 'completed', output }
      }));
    });

    await executor.execute();
  };

  return (
    <div className="workflow-graph">
      <div className="graph-controls">
        <button onClick={runWorkflow} className="btn-terminal">
          Run Workflow
        </button>
      </div>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={{ vqe: VQENode }}
        fitView
      />
    </div>
  );
};
```

---

## Data Flow

### Flow 1: User Chats in Session

```
User types message
  ↓
Panel 2: ChatInterface component
  ↓
POST /chat
  {
    user_id: "alice",
    team_id: "engineering",
    session_id: "quantum-research",
    message: "Help me..."
  }
  ↓
Backend: LLM processes
  ↓
WebSocket: Streams response
  {
    type: "message_chunk",
    content: "I'll help..."
  }
  ↓
Panel 2: Updates chat UI
  ↓
Backend: Saves trace
  {
    type: "trace_added",
    trace_id: "trace_048",
    artifacts: ["skill.md"]
  }
  ↓
Panel 1: Updates session count (48 traces)
Panel 2: Adds trace to list
Panel 3: Updates artifact graph
```

### Flow 2: Evolution Cron Runs

```
Cron trigger (scheduled or manual)
  ↓
POST /evolve
  {
    user_id: "alice",
    team_id: "engineering"
  }
  ↓
Backend: Analyzes traces
  ↓
WebSocket: Sends updates
  {
    type: "cron_progress",
    message: "Analyzing traces...",
    progress: 0.25
  }
  ↓
Panel 1: Updates cron status
  ↓
Backend: Detects patterns
  ↓
WebSocket: Pattern detected
  {
    type: "pattern_detected",
    pattern: "VQE optimization",
    confidence: 0.95
  }
  ↓
Panel 2: Shows notification
  ↓
Backend: Generates skill
  ↓
WebSocket: Skill created
  {
    type: "skill_generated",
    skill_id: "quantum-optimization"
  }
  ↓
Panel 1: Updates skill count
Panel 2: Shows new skill
  ↓
Backend: Git commit
  ↓
WebSocket: Cron completed
  {
    type: "cron_completed",
    skills_created: 2,
    commit_hash: "e9f2a1c"
  }
  ↓
Panel 1: Updates git status
Panel 1: Shows cron as completed
```

### Flow 3: User Commits Session

```
User clicks "Commit Session"
  ↓
Panel 2: CommitDialog opens
  ↓
User enters message
  ↓
POST /sessions/commit
  {
    session_id: "quantum-research",
    message: "VQE optimization pattern",
    include_metadata: true
  }
  ↓
Backend: Creates cognitive commit
  ↓
Git commit with YAML frontmatter:
  ---
  prompts: 3
  traces: 48
  patterns: 1
  ---
  VQE optimization pattern discovered
  ↓
Backend: Moves session to committed
  ↓
Response:
  {
    commit_hash: "a3f7c9e",
    status: "committed"
  }
  ↓
Panel 1: Updates session status
Panel 1: Updates git status
Panel 2: Shows success message
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2)

**Goal**: Basic 3-panel layout with static data

- [ ] Create Next.js project structure
- [ ] Implement TerminalLayout component
- [ ] Build Panel 1: VolumesPanel (static tree)
- [ ] Build Panel 2: SessionPanel (static chat)
- [ ] Build Panel 3: ArtifactPanel (static graph)
- [ ] Apply terminal theme CSS
- [ ] Connect to existing FastAPI backend

### Phase 2: Core Features (Week 3-4)

**Goal**: Dynamic data from backend

- [ ] Integrate API client
- [ ] Load real volumes/sessions/crons
- [ ] Implement chat interface with LLM
- [ ] Add WebSocket for real-time updates
- [ ] Implement session creation/resume
- [ ] Add Git commit dialog

### Phase 3: Workflow Editor (Week 5-6)

**Goal**: Interactive workflow graph

- [ ] Integrate React Flow
- [ ] Create custom node components
- [ ] Implement drag-and-drop from library
- [ ] Add node detail editor
- [ ] Connect to workflow-executor.ts
- [ ] Add live execution updates

### Phase 4: Evolution UI (Week 7-8)

**Goal**: Cron viewer and pattern exploration

- [ ] Build cron log viewer
- [ ] Show detected patterns
- [ ] Implement skill promotion flow
- [ ] Add pattern visualization
- [ ] Create commit history viewer

### Phase 5: Polish (Week 9-10)

**Goal**: Production-ready

- [ ] Add keyboard shortcuts
- [ ] Implement search/filter
- [ ] Add export functionality
- [ ] Performance optimization
- [ ] Mobile responsiveness
- [ ] Documentation
- [ ] User testing

---

## Success Metrics

### User Experience
- ✅ Can navigate all 3 levels (System/Team/User) intuitively
- ✅ Sessions are discoverable and resumable
- ✅ Real-time updates feel instant (<200ms)
- ✅ Workflow graph is interactive and live

### Technical
- ✅ <2s initial load time
- ✅ <100ms UI interaction latency
- ✅ WebSocket reconnection on disconnect
- ✅ Works on 1920x1080 and 1366x768 screens

### Business
- ✅ 90%+ user task completion rate
- ✅ <5min onboarding time
- ✅ 70%+ daily active usage

---

## Next Steps

1. **Approve this design** ✓
2. **Create Next.js project** (Phase 1 start)
3. **Build Panel 1** (Volumes navigator)
4. **Build Panel 2** (Session/chat viewer)
5. **Build Panel 3** (Artifact map/workflow graph)

**Ready to start implementation?**
