# LLMunix: WebAssembly-Powered Computational Workbench

> **llmos-lite** - Transform from Terminal OS to Browser-Native Computational Platform

[![Version](https://img.shields.io/badge/version-1.0.0--lite-blue.svg)](https://github.com/EvolvingAgentsLabs/llmunix/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-yellow.svg)](https://python.org)

---

## 🚀 Migration Notice

**We are migrating from the original llmos to llmos-lite + WebAssembly workflows.**

### What Changed

| Aspect | Original llmos | llmos-lite |
|--------|----------------|------------|
| **Interface** | Terminal UI | Web UI (React Flow + Chat) |
| **Execution** | Server (Python/Docker) | Browser (WebAssembly) |
| **Capabilities** | Python tools, 5 modes | Markdown skills, Workflows |
| **Architecture** | Complex (sentience, modes, hooks) | Simple (Git + Skills + Evolution) |
| **Latency** | 100-500ms (network) | <50ms (local) |
| **Cost** | Server compute | Free (user devices) |
| **Previews** | Text logs | Interactive (3D, plots, circuits) |
| **Scalability** | Limited by servers | Unlimited (P2P) |

### Why the Change

The original llmos was **over-engineered for a simple web app**. llmos-lite simplifies to the essentials:

- ⚡ **Zero-latency execution** - Skills run instantly in browser
- 🎨 **Rich interactive previews** - 3D animations, quantum states, circuit diagrams
- 🔒 **Sandboxed safety** - Generated code runs in browser, not on servers
- 💰 **Zero server costs** - Execution happens on user devices
- 🌍 **Infinite scalability** - P2P computational model
- 📝 **Git-backed everything** - Version control for all artifacts

---

## What is llmos-lite?

**llmos-lite** is a browser-native computational workbench where:

1. **Skills are Markdown files** - Two types:
   - **Context Skills**: LLM guidance (e.g., "Python Best Practices")
   - **Executable Skills**: Runnable nodes with inputs/outputs/code

2. **Workflows are visual DAGs** - Drag-and-drop computational graphs

3. **Execution is browser-native** - WebAssembly (Pyodide, Three.js, SPICE)

4. **Evolution is automatic** - System learns from workflow patterns

5. **Everything is Git-backed** - Version control for skills, workflows, traces

---

## Quick Start

### 1. Install

```bash
cd llmos-lite
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key"
```

### 2. Run the API

```bash
python api/main.py
# Server starts at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### 3. Try the Chat Endpoint

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "alice",
    "team_id": "engineering",
    "message": "Write a Python function to calculate Fibonacci numbers",
    "include_skills": true
  }'
```

### 4. Try Workflow Endpoints

```bash
# List executable skills
curl "http://localhost:8000/workflows/skills/executable?user_id=alice&team_id=engineering"

# Get skill categories
curl "http://localhost:8000/workflows/categories"
```

---

## Architecture

### Four-Layer Stack

```
┌──────────────────────────────────────────────────────────┐
│          PRESENTATION LAYER (Browser)                    │
│  ┌──────────────┐  ┌────────────────┐                   │
│  │ React Flow   │  │ Chat Interface │                   │
│  │ Canvas       │  │ (Skill Context)│                   │
│  └──────┬───────┘  └────────┬───────┘                   │
└─────────┼──────────────────────┼────────────────────────┘
          │                      │
┌─────────▼─────────┐  ┌────────▼────────┐
│ Workflow Executor │  │ Skills Manager  │
│ (TypeScript/Wasm) │  │ (Load/Filter)   │
└─────────┬─────────┘  └────────┬────────┘
          │                     │
┌─────────▼─────────────────────▼─────────┐
│        INTERFACE LAYER (API)            │
│  - FastAPI endpoints                    │
│  - /workflows (executable skills)       │
│  - /chat (LLM + context)                │
│  - /evolve (pattern detection)          │
└─────────┬───────────────────────────────┘
          │
┌─────────▼─────────────────────────────────┐
│         LOGIC LAYER (Core)                │
│  - WorkflowEngine: DAG execution          │
│  - SkillsManager: Load/filter skills      │
│  - EvolutionCron: Detect patterns         │
│  - PatternDetector: Analyze traces        │
└─────────┬─────────────────────────────────┘
          │
┌─────────▼─────────────────────────────────┐
│         STORAGE LAYER (Volumes)           │
│  - GitVolume: Git-backed storage          │
│  - VolumeManager: Multi-tenant access     │
│  - Hierarchy: System → Team → User        │
└───────────────────────────────────────────┘
```

---

## Key Features

### 1. Two Types of Skills

**Context Skills** - For LLM guidance:
```markdown
---
name: Python Best Practices
category: coding
keywords: [python, coding]
---

# Skill: Python Best Practices
## When to Use
[Description]
## Approach
[Steps]
```

**Executable Skills** - For workflows:
```markdown
---
skill_id: quantum-vqe-node
type: qiskit
execution_mode: browser-wasm
inputs:
  - name: iterations
    type: number
outputs:
  - name: eigenvalue
    type: number
---

\`\`\`python
def execute(inputs):
    # Runs in browser via Pyodide
    return {"eigenvalue": -1.137}
\`\`\`
```

### 2. Git-Backed Volumes

```
/volumes/
  system/         # Global skills (read-only for users)
  teams/
    {team_id}/    # Shared team skills
  users/
    {user_id}/    # Private user skills
```

**Access Control:**
| Volume | User Can | Team Cron Can | System Cron Can |
|--------|----------|---------------|-----------------|
| User   | R/W      | R             | R/W             |
| Team   | R        | R/W           | R/W             |
| System | R        | R             | R/W             |

### 3. Evolution Engine

**Automatic skill generation from patterns:**

```
Day 1-7: User runs workflows
         → Traces saved to user volume

Night 7: Evolution Cron runs
         → Detects: "VQE simulation" x 5 times
         → Generates: vqe-compound-skill.md

Day 8+:  User's future VQE tasks
         → New skill auto-loaded
         → Better guidance from LLM
```

### 4. Multi-Runtime Support

| Runtime | Language | Use Cases |
|---------|----------|-----------|
| **Pyodide** | Python | Quantum, Data Science, ML |
| **JavaScript** | JS | Utilities, Transformations |
| **Three.js** | JS | 3D Graphics, Animations |
| **Ngspice.js** | SPICE | Circuit Simulation |

---

## Example Workflows

### Quantum VQE Workflow

```
[Hamiltonian Node] → [VQE Node] → [Plot Node] → [Export Node]

1. Hamiltonian Node: Defines quantum system
2. VQE Node: Runs simulation (Pyodide)
3. Plot Node: Visualizes convergence (JavaScript)
4. Export Node: Saves results (Canvas API)

Result: Instant, interactive, in-browser execution
```

### 3D Animation Workflow

```
[Model Node] → [Material Node] → [Scene Node] → [Render Node]

1. Model Node: Creates 3D geometry (Three.js)
2. Material Node: Applies textures (Three.js)
3. Scene Node: Positions objects (Three.js)
4. Render Node: WebGL rendering (60 FPS)

Result: Real-time 3D visualization in browser
```

---

## API Endpoints

### Chat
- `POST /chat` - Chat with skill context injection

### Skills
- `GET /skills` - List skills
- `GET /skills/{skill_id}` - Get skill details
- `POST /skills` - Create skill
- `POST /skills/promote` - Promote skill (user → team)

### Evolution
- `POST /evolve` - Trigger pattern detection
- `GET /traces` - List execution traces

### Workflows
- `GET /workflows/skills/executable` - List executable skills
- `POST /workflows/execute` - Prepare workflow for browser execution
- `POST /workflows/save` - Save workflow to Git
- `GET /workflows/categories` - List skill categories

### Volumes
- `GET /volumes/stats` - Volume statistics
- `GET /volumes/history` - Git commit history

---

## Examples

### qiskit-studio (Being Migrated)

**Location:** `/examples/qiskit-studio`

React Flow-based quantum computing workflow builder:
- Drag-and-drop quantum circuit nodes
- Visual workflow canvas
- Live code generation
- Frontend: Next.js + React Flow
- Will integrate with llmos-lite API

**Run it:**
```bash
cd examples/qiskit-studio/frontend
npm install
npm run dev
# Open http://localhost:3000
```

---

## Documentation

- **[llmos-lite/README.md](llmos-lite/README.md)** - Quick start guide
- **[llmos-lite/ARCHITECTURE.md](llmos-lite/ARCHITECTURE.md)** - Technical deep dive
- **[llmos-lite/WASM_WORKFLOWS.md](llmos-lite/WASM_WORKFLOWS.md)** - WebAssembly workflow guide
- **[llmos-lite/QUICKSTART.md](llmos-lite/QUICKSTART.md)** - 5-minute getting started
- **[EXAMPLES_MIGRATION_ANALYSIS.md](EXAMPLES_MIGRATION_ANALYSIS.md)** - Why examples were removed

---

## Original llmos (Deprecated)

The original llmos architecture is preserved in the `/llmos` folder for reference but is **deprecated**.

**Original llmos featured:**
- Terminal UI
- 5 execution modes (LEARNER, FOLLOWER, MIXED, ORCHESTRATOR, CRYSTALLIZED)
- Sentience layer with valence/emotion
- Multi-agent orchestration
- Python tools
- Server-side execution

**Why deprecated:** Over-engineered for a web app. llmos-lite simplifies to essentials while adding browser-native execution.

**If you need the original llmos:** Check the Git history or the `/llmos` folder (reference only).

---

## Project Structure

```
llmunix/
├── llmos-lite/              # ⭐ New platform (active development)
│   ├── core/                # Backend logic
│   │   ├── volumes.py       # Git-backed storage
│   │   ├── skills.py        # Skills loader
│   │   ├── evolution.py     # Pattern detection
│   │   └── workflow.py      # Workflow engine
│   ├── api/                 # REST API
│   │   ├── main.py          # Main API
│   │   └── workflows.py     # Workflow endpoints
│   ├── ui/                  # Browser frontend
│   │   └── lib/             # Executors (Pyodide, workflow)
│   └── volumes/             # Git repositories
│       └── system/skills/   # Example skills
│
├── examples/
│   └── qiskit-studio/       # Quantum workflow builder (migrating)
│
├── llmos/                   # ⚠️ Original architecture (deprecated, kept for reference)
│
└── docs/                    # Documentation
```

---

## Roadmap

### Phase 1: Core llmos-lite ✅ (Complete)
- [x] Git-backed volumes
- [x] Skills loader
- [x] Evolution engine
- [x] FastAPI service

### Phase 2: WebAssembly Workflows ✅ (Complete)
- [x] Executable skill format
- [x] Workflow engine (DAG execution)
- [x] Pyodide integration
- [x] Multi-runtime support
- [x] Example skills (Quantum, 3D, Electronics)

### Phase 3: React UI (Current)
- [ ] React Flow canvas
- [ ] Node library panel
- [ ] Execution controls & progress
- [ ] Preview renderers (plots, 3D, circuits)
- [ ] Chat interface integration

### Phase 4: Advanced Features
- [ ] GPU acceleration (WebGPU)
- [ ] Workflow marketplace
- [ ] Collaborative editing
- [ ] Mobile PWA

---

## Contributing

We welcome contributions!

**Priority areas:**
1. React Flow UI development
2. New executable skills (domains: quantum, 3D, electronics, ML)
3. Runtime integrations (WebGPU, WebR, etc.)
4. Example workflows

See [llmos-lite/README.md](llmos-lite/README.md) for development setup.

---

## License

Apache 2.0

---

## Credits

Built by [Evolving Agents Labs](https://github.com/EvolvingAgentsLabs)

**Core Innovation:** Treating capabilities as **version-controlled Markdown files** that execute as **WebAssembly workflows** in the browser.

Inspired by OpenAI/Anthropic's 2025 direction toward Skills as the new paradigm for AI capabilities.

---

<div align="center">

**[Get Started](llmos-lite/QUICKSTART.md)** · **[Architecture](llmos-lite/ARCHITECTURE.md)** · **[Examples](examples/)**

</div>
