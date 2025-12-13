# LLMunix Architecture

**Version:** 1.0.0-lite

---

## 🚀 Migration to llmos-lite

This document describes the **llmos-lite** architecture. The original llmos architecture (with sentience, modes, hooks) is **deprecated** and preserved in `/llmos` for reference only.

### Why the Migration?

The original llmos was **over-engineered** for a simple web application:
- Complex sentience layer (valence, latent modes, emotion)
- 5 execution modes (LEARNER, FOLLOWER, MIXED, ORCHESTRATOR, CRYSTALLIZED)
- Hooks system (pre/post tool use)
- Multi-agent orchestration
- Server-side execution

**llmos-lite simplifies** to the essentials while adding browser-native WebAssembly execution:
- Simple Git-backed volumes
- Two types of skills (Context + Executable)
- Pattern detection (no sentience)
- Browser-native workflows
- Zero-latency execution

---

## The Big Picture

llmos-lite is a **browser-native computational workbench** built on three core principles:

1. **Skills are Markdown** - Version-controlled, human-readable, LLM-friendly
2. **Workflows are Visual** - Drag-and-drop DAGs executed in-browser
3. **Evolution is Automatic** - System learns from usage patterns

```
┌──────────────────────────────────────────────────────────┐
│                    Web UI (Browser)                      │
│  ┌─────────────────┐  ┌────────────────────────┐        │
│  │ Workflow Canvas │  │ Chat Interface         │        │
│  │ (React Flow)    │  │ (Skill Context)        │        │
│  └────────┬────────┘  └────────┬───────────────┘        │
└───────────┼──────────────────────┼──────────────────────┘
            │                      │
┌───────────▼──────────┐  ┌────────▼────────┐
│ Workflow Executor    │  │ Skills Manager  │
│ (TypeScript/Wasm)    │  │ (Load/Filter)   │
└───────────┬──────────┘  └────────┬────────┘
            │                      │
┌───────────▼──────────────────────▼──────────────────────┐
│                    FastAPI Backend                       │
│  /workflows | /chat | /skills | /evolve | /volumes      │
└───────────┬──────────────────────────────────────────────┘
            │
┌───────────▼──────────────────────────────────────────────┐
│             Git-Backed Volumes (Storage)                 │
│  System → Team → User (Hierarchical skill management)    │
└──────────────────────────────────────────────────────────┘
```

---

## Four-Layer Architecture

### Layer 1: Presentation (Browser)

**Components:**
- React Flow Canvas - Visual workflow builder
- Chat Interface - Skill-enhanced LLM conversations
- Preview Renderers - 3D (Three.js), Plots (Matplotlib), Circuits (SVG)

**Tech Stack:**
- Next.js 14 + TypeScript
- React Flow for workflows
- shadcn/ui components
- Tailwind CSS

### Layer 2: Execution (TypeScript + WebAssembly)

**Workflow Executor** (`ui/lib/workflow-executor.ts`):
- DAG execution with topological sort
- Multi-runtime dispatch (Pyodide, JavaScript, Three.js, SPICE)
- Progress tracking and error handling

**Pyodide Runner** (`ui/lib/pyodide-runner.ts`):
- Lazy-load Pyodide (~3s first time, 0ms cached)
- Execute Python skills in WebAssembly
- Serialize results for UI

**Performance:**
| Operation | Cold Start | Warm Start |
|-----------|------------|------------|
| Load Pyodide | ~3s | 0ms (cached) |
| Execute Python | 100-500ms | 50-200ms |
| Execute JS | <10ms | <5ms |
| Render 3D | ~50ms | ~16ms (60 FPS) |

### Layer 3: API (FastAPI)

**Endpoints:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/chat` | POST | Chat with skill context injection |
| `/skills` | GET | List skills |
| `/skills/{skill_id}` | GET | Get skill details |
| `/skills` | POST | Create skill |
| `/skills/promote` | POST | Promote skill (user → team) |
| `/evolve` | POST | Trigger pattern detection |
| `/traces` | GET | List execution traces |
| `/workflows/skills/executable` | GET | List executable skills |
| `/workflows/execute` | POST | Prepare workflow for browser execution |
| `/workflows/save` | POST | Save workflow to Git |
| `/workflows/categories` | GET | List skill categories |
| `/volumes/stats` | GET | Volume statistics |
| `/volumes/history` | GET | Git commit history |

### Layer 4: Storage (Git-Backed Volumes)

**Volume Hierarchy:**
```
/volumes/
  system/
    skills/           # Global skills (read-only for users)
    traces/           # System-level execution history
  teams/
    {team_id}/
      skills/         # Shared team skills
      traces/         # Team execution history
  users/
    {user_id}/
      skills/         # Private user skills
      traces/         # User execution history
```

**Access Control:**
| Volume | User Can | Team Cron Can | System Cron Can |
|--------|----------|---------------|-----------------|
| User   | R/W      | R             | R/W             |
| Team   | R        | R/W           | R/W             |
| System | R        | R             | R/W             |

---

## Core Components

### 1. GitVolume (`core/volumes.py`)

**Purpose:** Git-backed storage for skills and traces.

**Key Methods:**
```python
write_skill(skill_id, content, commit_message)  # Save skill + Git commit
read_skill(skill_id)                            # Read skill content
list_skills()                                   # List all skills
commit_changes(message, author)                 # Manual Git commit
get_git_log(limit)                              # Git history
```

**Git Integration:**
- Automatic commits on skill creation
- Git history for audit trail
- Future: Branches, PRs for skill promotion

### 2. SkillsManager (`core/skills.py`)

**Purpose:** Load, filter, and inject skills into LLM context.

**Skill Types:**

**Context Skills** - For LLM guidance:
```markdown
---
name: Python Best Practices
category: coding
keywords: [python, testing, clean-code]
---

# Skill: Python Best Practices
## When to Use
When writing Python code...
## Approach
1. Follow PEP 8
2. Write docstrings
...
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
    default: 100
outputs:
  - name: eigenvalue
    type: number
---

\`\`\`python
def execute(inputs):
    iterations = inputs['iterations']
    # VQE simulation logic
    return {"eigenvalue": -1.137, "convergence_data": [...]}
\`\`\`
```

**Flow:**
```
1. load_skills_for_user(user_id, team_id)
   ↓
2. Load System + Team + User skills
   ↓
3. Parse Markdown with YAML frontmatter
   ↓
4. Return List[Skill]

5. filter_skills_by_query(skills, query)
   ↓
6. Score skills by keyword/name/category match
   ↓
7. Return top N relevant skills

8. build_context_for_query(user_id, team_id, query)
   ↓
9. Load → Filter → Format for LLM
   ↓
10. Return context string (injected into system prompt)
```

### 3. EvolutionCron (`core/evolution.py`)

**Purpose:** Analyze traces, detect patterns, generate skills.

**Components:**

- **PatternDetector:** Groups traces by goal signature, calculates success rate
- **SkillGenerator:** Generates SkillDraft from Pattern
- **EvolutionCron:** Orchestrates pattern → skill flow

**Flow:**
```
run_user_evolution(user_id, team_id)
  ↓
1. Load traces from user volume
  ↓
2. PatternDetector.analyze_traces(traces)
  ↓
3. Filter patterns (count >= 3, success >= 0.7)
  ↓
4. For each pattern:
     SkillGenerator.generate_skill_from_pattern(pattern)
  ↓
5. Save skills to user volume
  ↓
6. Git commit: "Evolution: Create skill X from N traces"
  ↓
Return stats (traces_analyzed, skills_created, etc.)
```

**Thresholds:**
- `min_pattern_count`: 3 (configurable)
- `min_success_rate`: 0.7 (configurable)

### 4. WorkflowEngine (`core/workflow.py`)

**Purpose:** Execute workflows as DAGs.

**Key Classes:**

```python
@dataclass
class ExecutableSkill:
    skill_id: str
    name: str
    node_type: NodeType  # python-wasm, javascript, threejs, spice
    execution_mode: ExecutionMode  # browser-wasm, server-python
    inputs: List[NodeInput]
    outputs: List[NodeOutput]
    code: str

@dataclass
class Workflow:
    workflow_id: str
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]
```

**Execution:**
1. Parse workflow into DAG
2. Topological sort to determine execution order
3. Execute nodes level-by-level (parallel within level)
4. Pass outputs between nodes via edges
5. Return results for all nodes

---

## Multi-Runtime Support

| Runtime | Language | Execution Location | Use Cases |
|---------|----------|-------------------|-----------|
| **Pyodide** | Python | Browser (Wasm) | Quantum, Data Science, ML |
| **JavaScript** | JS | Browser (Native) | Utilities, Transformations |
| **Three.js** | JS | Browser (WebGL) | 3D Graphics, Animations |
| **Ngspice.js** | SPICE | Browser (Wasm) | Circuit Simulation |

### Pyodide Integration

**Load Pyodide:**
```typescript
import { loadPyodide } from 'pyodide';

const pyodide = await loadPyodide({
  indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.24.1/full/'
});

// Install packages
await pyodide.loadPackage(['numpy', 'matplotlib']);
```

**Execute Python Skill:**
```typescript
// Set inputs
pyodide.globals.set('inputs', pyodide.toPy(inputs));

// Run code
await pyodide.runPythonAsync(skill.code);

// Get result
const result = await pyodide.runPythonAsync('execute(inputs)');
return result.toJs({ dict_converter: Object.fromEntries });
```

---

## Workflow Execution Flow

### Browser-Side Execution

```
User clicks "Run Workflow"
  ↓
1. POST /workflows/execute (API prepares payload)
  ↓
2. Browser receives {workflow, skills}
  ↓
3. Load runtimes if needed (Pyodide, Three.js, etc.)
  ↓
4. Build execution DAG via topological sort
  ↓
5. Execute level 1 nodes in parallel
  ↓
6. Pass outputs to level 2 nodes
  ↓
7. Continue until all nodes complete
  ↓
8. Render previews in UI
  ↓
9. Save trace to user volume (for evolution)
```

**Example Workflow:**

```
[VQE Node] → [Plot Node] → [Export Node]

Level 1: VQE Node executes (Pyodide, ~500ms)
         Output: {eigenvalue: -1.137, convergence_data: [...]}

Level 2: Plot Node executes (JavaScript, ~50ms)
         Input: convergence_data
         Output: {plot_image: "data:image/png;base64,..."}

Level 3: Export Node executes (Canvas API, ~10ms)
         Input: plot_image
         Output: {download_url: "blob:..."}

Total Time: ~560ms (all in-browser, no network!)
```

---

## Evolution Integration

### Trace Capture

When a workflow executes successfully:
```
1. Browser completes workflow
2. Results sent to API
3. API saves trace to user volume:
   - Workflow structure (nodes + edges)
   - Input parameters
   - Execution results
   - Success/failure status
4. Git commit
```

### Pattern Detection

Evolution Cron runs periodically:
```
1. Load all traces from user volume
2. Group by goal signature (hash of workflow structure)
3. Calculate success rate per pattern
4. Patterns with 3+ occurrences and 70%+ success rate:
   → Generate compound skill
   → Learns optimal parameters
   → Commits to user volume
```

**Example Evolution:**

```
User runs "VQE → Plot" workflow 5 times:
- Run 1: iterations=100, success
- Run 2: iterations=150, success
- Run 3: iterations=120, success
- Run 4: iterations=130, success
- Run 5: iterations=110, success

Evolution Cron detects pattern:
→ Generates vqe-with-plot.md skill
→ Learned default: iterations=130 (averaged)
→ Commits to user volume

Future runs:
→ Skill available as single node
→ Pre-filled with optimal parameters
```

---

## Skill Promotion Flow

```
Day 1-7: User creates and uses skills
         → Stored in user volume

Day 8:   User reviews skill
         → Clicks "Promote to Team"
         → API: POST /skills/promote
         → Skill copied to team volume
         → Git commit in team volume
         → Team members can now see it

Day 30:  Team uses skill successfully (3+ users)
         → Team Cron flags for promotion
         → Promoted to system volume
         → Available to everyone
```

---

## API Implementation

### Chat Flow

```
POST /chat
  ↓
1. Load skills (SkillsManager.load_skills_for_user)
  ↓
2. Filter skills (SkillsManager.filter_skills_by_query)
  ↓
3. Build context (Skill.to_context_injection)
  ↓
4. Call LLM with context + user message
  ↓
5. Get response
  ↓
6. Save trace to user volume
  ↓
Return {response, skills_used, trace_id}
```

### Workflow Execution Flow

```
POST /workflows/execute
  ↓
1. Load executable skills (WorkflowEngine.load_executable_skills)
  ↓
2. Create workflow DAG from nodes + edges
  ↓
3. Validate workflow (check for cycles, missing skills)
  ↓
4. Prepare browser payload:
   {
     workflow: {nodes, edges},
     skills: {skill_id: {code, inputs, outputs}}
   }
  ↓
5. Return {status: "ready", payload: {...}}
  ↓
Browser receives and executes locally
```

---

## Comparison: llmos vs llmos-lite

| Feature | llmos | llmos-lite |
|---------|-------|------------|
| **Storage** | File-based volumes | Git-backed volumes |
| **Capabilities** | Python tools | Markdown skills (2 types) |
| **Execution** | 5 modes (LEARNER, FOLLOWER, etc.) | Chat + Workflows (hybrid) |
| **Execution Location** | Server (Python/Docker) | Browser (WebAssembly) |
| **Latency** | 100-500ms (network) | <50ms (local) |
| **Previews** | Text logs | Interactive (3D, plots, circuits) |
| **Evolution** | SentienceCron (complex) | EvolutionCron (simple) |
| **State** | Valence, emotion, theory of mind | Pattern detection only |
| **Interface** | Terminal UI | Web UI (React Flow + Chat) |
| **Collaboration** | File system | Git (commits, branches, PRs) |
| **Context Injection** | Tool search + examples | Direct markdown injection |
| **LLM Integration** | Claude SDK with agents | Direct API calls |
| **Cost** | Server compute | Free (user devices) |

---

## Scalability

### Storage

- **Git repositories:** Standard Git scalability
- **Sharding:** Teams in separate repos
- **Archiving:** Old traces can be compressed/archived

### Compute

- **Stateless API:** Horizontal scaling
- **Background jobs:** Evolution crons run async
- **Caching:** Skills manager has in-memory cache
- **Browser execution:** Infinite scalability (user devices)

### Future Optimizations

- **Vector DB:** For semantic skill search
- **Redis:** For distributed caching
- **Message Queue:** For async evolution jobs
- **WebGPU:** For GPU-accelerated workflows

---

## Security

### Current

- Volume-level isolation (user/team/system)
- Git history for audit trail
- Readonly flags for access control
- Browser sandbox for code execution

### Future

- **Authentication:** JWT tokens
- **Authorization:** RBAC (roles: user, team_admin, system_admin)
- **API Keys:** For programmatic access
- **Git signing:** GPG signatures for commits
- **CORS:** Restrict browser origins

---

## Development Roadmap

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

## Design Principles

1. **Simplicity over Features:** One clear way to do things
2. **Git as Source of Truth:** Version control everything
3. **Markdown as Interface:** Human-readable, LLM-friendly
4. **Evolution over Configuration:** Learn from usage, don't pre-configure
5. **Collaboration-First:** Built for teams, not just individuals
6. **Browser-Native:** Execution happens locally for speed and cost

---

## Original llmos Architecture

The original llmos architecture (v3.6.0) is **deprecated** but preserved in `/llmos` for reference.

**What made it complex:**
- **Sentience Layer:** Valence vector, latent modes, behavioral adaptation
- **Five Execution Modes:** LEARNER, FOLLOWER, MIXED, ORCHESTRATOR, CRYSTALLIZED
- **Hooks System:** Pre/post tool use validation
- **Multi-Agent Orchestration:** Dynamic agent creation, coordination
- **Terminal UI:** Rich terminal interface with tree views

**Why we simplified:**
- Over-engineered for a web application
- Server-side execution limited scalability
- Complex state management added unnecessary overhead
- Terminal UI not suitable for modern web apps

**What we kept:**
- Git-backed storage (improved)
- Evolution concept (simplified)
- Pattern detection (streamlined)
- Volume hierarchy (System → Team → User)

---

## Summary

llmos-lite is a **browser-native computational workbench** where:

1. **Skills are Markdown** - Version-controlled, Git-backed
2. **Workflows are Visual** - React Flow DAGs
3. **Execution is Local** - WebAssembly (Pyodide, Three.js, SPICE)
4. **Evolution is Automatic** - Pattern detection → Skill generation
5. **Collaboration is Built-in** - Skill promotion (User → Team → System)

The result: A simple, scalable platform for building and sharing computational workflows.

---

**See [README.md](README.md) for quick start.**
