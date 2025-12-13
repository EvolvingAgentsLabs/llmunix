# LLMunix Examples

> Examples demonstrating llmos-lite's WebAssembly-powered workflow capabilities

---

## 🚀 Migration Notice

**We are migrating from llmos to llmos-lite + WebAssembly workflows.**

**What changed:**
- **Old:** Terminal UI, Python tools, LEARNER/FOLLOWER modes, multi-agent orchestration
- **New:** Web UI, executable skills, browser-native workflows (WebAssembly)

**Why:**
- ⚡ **Zero-latency execution** - Skills run instantly in browser
- 🎨 **Rich interactive previews** - 3D animations, quantum states, circuit diagrams
- 🔒 **Sandboxed safety** - Generated code runs in browser, not on servers
- 💰 **Zero server costs** - Execution happens on user devices
- 🌍 **Infinite scalability** - P2P computational model

**Impact on examples:**
- Most original llmos examples have been removed (incompatible with new architecture)
- qiskit-studio is being migrated to llmos-lite
- New examples will showcase WebAssembly workflows

See [EXAMPLES_MIGRATION_ANALYSIS.md](../EXAMPLES_MIGRATION_ANALYSIS.md) for full migration details.

---

## Current Examples

### 1. **qiskit-studio** - Quantum Computing Workflows ⚡

**Status:** 🔄 Being migrated to llmos-lite

**Location:** `/examples/qiskit-studio`

**What it is:**
- React Flow-based quantum computing workflow builder
- Visual node graph for Qiskit circuits
- Generates executable Python code
- Frontend + Backend architecture

**Features:**
- Drag-and-drop quantum circuit nodes
- Transpiler optimization nodes
- Runtime primitives (Estimator, Sampler)
- Visualization nodes (plots, graphs, circuits)
- Chemistry simulation workflows
- Live code generation

**Tech Stack:**
- Frontend: Next.js 14 + React Flow + shadcn/ui
- Backend: Python (FastAPI) - will integrate with llmos-lite
- Execution: Qiskit (Python) - will use Pyodide (WebAssembly)

**Run it:**
```bash
cd qiskit-studio/frontend
npm install
npm run dev
# Open http://localhost:3000
```

**Migration to llmos-lite:**
- Convert Qiskit nodes to llmos-lite executable skills
- Integrate with `/workflows/execute` API
- Use Pyodide for browser-based quantum simulation
- Add evolution learning from workflow patterns

---

## Removed Examples (Incompatible)

The following examples demonstrated llmos-specific features that don't apply to llmos-lite:

### ❌ demo-app
- **Why removed:** Demonstrated LEARNER/FOLLOWER/MIXED modes (llmos-specific)
- **Replacement:** New llmos-lite demos showing skill creation and workflow evolution

### ❌ hybrid_architecture_demo.py
- **Why removed:** Demonstrated Markdown agents + Python kernel (llmos architecture)
- **Replacement:** llmos-lite uses Skills (Markdown) + Workflows (WebAssembly)

### ❌ q-kids-studio
- **Why removed:** Used llmos ORCHESTRATOR mode and multi-agent system
- **Replacement:** Could be recreated as educational workflow builder (future)

### ❌ robo-os
- **Why removed:** Requires server-side execution, hooks, and hardware I/O
- **Not suitable for llmos-lite:** Browser-based execution can't control hardware

### ❌ sentience_demo.py
- **Why removed:** Demonstrated llmos sentience layer (valence, latent modes)
- **Not in llmos-lite:** Simplified to pattern detection only

---

## Planned Examples (Coming Soon)

### 1. **basic-workflow-demo**
Simple introduction to llmos-lite workflows:
- Create executable skills
- Build workflow: Python → Plot → Export
- See live previews in browser

### 2. **quantum-chemistry-workflows**
Migration of qiskit-studio to llmos-lite:
- Quantum VQE simulations
- Chemistry molecule mapping
- Interactive Bloch sphere visualization
- All running in browser via Pyodide

### 3. **3d-animation-studio**
Three.js-based workflows:
- Create 3D models
- Animate scenes
- Export as video/GIF
- Real-time WebGL rendering

### 4. **circuit-simulator**
Electronics workflows:
- RC/RLC circuit analysis
- SPICE simulation (Ngspice.js)
- Voltage/current plots
- Frequency response

### 5. **evolution-demo**
Shows llmos-lite learning capabilities:
- Run workflows multiple times
- Evolution engine detects patterns
- Auto-generates compound skills
- Promotes skills (user → team → system)

---

## Documentation

- **[llmos-lite README](../llmos-lite/README.md)** - Quick start guide
- **[llmos-lite ARCHITECTURE](../llmos-lite/ARCHITECTURE.md)** - Technical deep dive
- **[WASM_WORKFLOWS](../llmos-lite/WASM_WORKFLOWS.md)** - WebAssembly workflow guide
- **[Migration Analysis](../EXAMPLES_MIGRATION_ANALYSIS.md)** - Why examples were removed

---

## For llmos Examples (Original Architecture)

If you need examples for the **original llmos** (Terminal UI, modes, agents), see the Git history:

```bash
# Checkout before migration
git checkout <commit-before-migration>
cd examples/
```

Original llmos examples included:
- demo-app: LEARNER/FOLLOWER/MIXED mode demonstrations
- robo-os: Robot control with safety hooks
- q-kids-studio: Educational quantum computing
- hybrid_architecture_demo.py: Markdown agents + Python kernel

These are preserved in Git history but not compatible with llmos-lite.

---

## Contributing Examples

Want to create a new llmos-lite example?

**Requirements:**
1. Use executable skills (Markdown with inputs/outputs/code)
2. Build workflows using React Flow
3. Execute in browser via WebAssembly (Pyodide, Three.js, etc.)
4. Include README with setup instructions
5. Demonstrate llmos-lite strengths (zero-latency, rich previews, evolution)

**Structure:**
```
examples/
  your-example/
    README.md              # Setup and usage
    skills/                # Executable skill definitions
    workflows/             # Example workflow JSON
    frontend/              # React Flow UI (if custom)
    screenshots/           # Demo images
```

See [llmos-lite/WASM_WORKFLOWS.md](../llmos-lite/WASM_WORKFLOWS.md) for executable skill format.

---

## Quick Start

### Run qiskit-studio (only remaining example):

```bash
cd qiskit-studio/frontend
npm install
npm run dev
# Open http://localhost:3000
```

### Start llmos-lite API (for future examples):

```bash
cd llmos-lite
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key"
python api/main.py
# API at http://localhost:8000
```

---

## Questions?

- **llmos-lite architecture:** See [ARCHITECTURE.md](../llmos-lite/ARCHITECTURE.md)
- **WebAssembly workflows:** See [WASM_WORKFLOWS.md](../llmos-lite/WASM_WORKFLOWS.md)
- **Migration details:** See [EXAMPLES_MIGRATION_ANALYSIS.md](../EXAMPLES_MIGRATION_ANALYSIS.md)
- **Original llmos:** See Git history or [README.md](../llmos/README.md) (for reference only)

---

**Status:** Migration in progress - qiskit-studio being updated, new examples coming soon! 🚀
