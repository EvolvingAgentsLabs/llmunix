# Examples Migration Analysis: llmos → llmos-lite

**Date:** 2025-01-13
**Status:** Analysis Complete

---

## Executive Summary

This document analyzes all examples in `/examples/` to determine compatibility with the new **llmos-lite + WebAssembly workflows** architecture.

**Key Finding:** **1 of 4 examples is directly compatible**, while **3 of 4 require significant refactoring or are no longer relevant**.

---

## Migration Decision Matrix

| Example | Compatible | Action | Reason |
|---------|-----------|--------|--------|
| **qiskit-studio** | ✅ **YES** | **Keep & Migrate** | Already uses React Flow + workflows, perfect fit for llmos-lite |
| **demo-app** | ❌ No | **Remove** | Demonstrates llmos-specific features (LEARNER/FOLLOWER modes, nested learning) |
| **hybrid_architecture_demo.py** | ❌ No | **Remove** | Demonstrates llmos Markdown agents + Python kernel (obsolete in llmos-lite) |
| **q-kids-studio** | ⚠️ Partial | **Refactor or Remove** | Quantum education tool, but uses llmos ORCHESTRATOR mode |
| **robo-os** | ❌ No | **Remove** | Uses llmos hooks system, sentience state, and mode strategies |

---

## Detailed Analysis

### 1. ✅ **qiskit-studio** - KEEP & MIGRATE

**Location:** `/examples/qiskit-studio`

**What it is:**
- React Flow-based quantum computing workflow builder
- Visual node graph for Qiskit circuits
- Generates Python code from workflows
- Already has frontend (`frontend/`) and backend structure

**Why it's compatible:**
- **Already uses React Flow** for workflow canvas
- **Already has node types** (CircuitNode, TranspilerNode, etc.)
- **Generates executable code** (Qiskit Python)
- Perfect match for llmos-lite's executable skills paradigm

**Migration Path:**

1. **Convert Qiskit nodes to llmos-lite executable skills**
   ```markdown
   ---
   skill_id: qiskit-vqe-node
   type: qiskit
   execution_mode: browser-wasm
   inputs:
     - name: ansatz_type
       type: string
   outputs:
     - name: eigenvalue
       type: number
   ---

   \`\`\`python
   def execute(inputs):
       # VQE code here
       return {"eigenvalue": -1.137}
   \`\`\`
   ```

2. **Integrate with llmos-lite API**
   - Use `/workflows/skills/executable` endpoint
   - Use `/workflows/execute` for browser execution

3. **Update frontend to use llmos-lite workflow executor**
   - Import `workflow-executor.ts` from llmos-lite
   - Execute workflows via Pyodide

**Effort:** Medium (1-2 days)

**Value:** High - Becomes flagship example for llmos-lite quantum workflows

---

### 2. ❌ **demo-app** - REMOVE

**Location:** `/examples/demo-app`

**What it is:**
- Demonstrations of llmos-specific features
- Scenarios: `nested_learning_demo.py` (LEARNER/FOLLOWER/MIXED modes)
- Shows cost optimization through trace matching

**Why it's incompatible:**
- **Demonstrates llmos mode system** (LEARNER, FOLLOWER, MIXED)
- llmos-lite uses simplified **Chat + Workflows** paradigm
- No equivalent of nested learning or mode strategies in llmos-lite
- Entire premise (cost optimization via PTC) doesn't apply to browser execution

**Replacement:**
Create new **llmos-lite demos** showing:
- Creating executable skills
- Building workflows
- Evolution from workflow patterns
- Promoting skills (user → team → system)

**Action:** DELETE `/examples/demo-app`

---

### 3. ❌ **hybrid_architecture_demo.py** - REMOVE

**Location:** `/examples/hybrid_architecture_demo.py`

**What it is:**
- Demonstrates "Markdown Mind + Python Kernel" architecture
- Shows `create_agent`, `list_agents`, `modify_agent` tools
- Hot-reloading of Markdown agent definitions

**Why it's incompatible:**
- llmos-lite doesn't have "agents" concept (replaced with "skills")
- No `create_agent` tool (skills are created via API or evolution)
- No mode system (ORCHESTRATOR, etc.)
- Architecture described is llmos-specific

**Replacement:**
Create new **llmos-lite hybrid demo** showing:
- Chat interface with skill context injection
- Creating executable skills via API
- Workflow evolution from patterns

**Action:** DELETE `/examples/hybrid_architecture_demo.py`

---

### 4. ⚠️ **q-kids-studio** - REFACTOR OR REMOVE

**Location:** `/examples/q-kids-studio`

**What it is:**
- Educational quantum computing for kids
- "Professor Q" agent teaches quantum concepts
- "Game Master" agent creates interactive learning

**Why it's partially compatible:**
- Educational goal is valid
- Could become a **learning workflow builder**
- But currently uses llmos ORCHESTRATOR mode

**Problems:**
- Uses llmos agents (`professor-q.md`, `game-master.md`)
- Uses llmos multi-agent orchestration
- Custom plugins (`kid_circuit_tools.py`) - not WebAssembly

**Migration Path (if keeping):**

1. **Convert to skill-based learning**
   - Create "quantum-lesson" executable skills
   - Students build workflows to solve challenges

2. **Interactive quantum circuits as WebAssembly nodes**
   - Use Pyodide for quantum simulations
   - Three.js for Bloch sphere visualization

3. **Gamification via workflow challenges**
   - "Build a workflow that creates a Bell state"
   - "Optimize this VQE circuit"

**Effort:** High (3-5 days)

**Value:** Medium - Nice educational showcase, but not critical

**Recommendation:** **REMOVE for now**, revisit after llmos-lite UI is complete

**Action:** DELETE `/examples/q-kids-studio` (can restore later if desired)

---

### 5. ❌ **robo-os** - REMOVE

**Location:** `/examples/robo-os`

**What it is:**
- Robot control system using llmos
- Safety hooks (`safety_hook.py`) to prevent dangerous operations
- `operator.md` and `safety-officer.md` agents
- Custom robot controller plugins

**Why it's incompatible:**
- **Heavily depends on llmos hooks system** (`pre_tool_use` hooks)
- Uses llmos **sentience state** and **mode strategies**
- Custom Python tools (`robot_controller.py`) - not WebAssembly
- Safety model based on llmos pre-execution validation

**Why it can't migrate:**
llmos-lite is designed for **browser-based execution** (sandboxed, safe by default). Robot control requires:
- Real-time server-side execution
- Hardware I/O
- Safety-critical validation
- State management

These are fundamentally incompatible with browser-based WebAssembly workflows.

**Alternative:**
If robot control is needed, keep original **llmos** for this use case. llmos-lite is for:
- Data analysis
- Visualization
- Simulation
- Computational research

Not for:
- Hardware control
- Real-time systems
- Safety-critical operations

**Action:** DELETE `/examples/robo-os` (or move to separate llmos-only repo)

---

## Summary of Actions

### DELETE (3 examples)

```bash
rm -rf examples/demo-app
rm -rf examples/q-kids-studio
rm -rf examples/robo-os
rm examples/hybrid_architecture_demo.py
```

### KEEP & MIGRATE (1 example)

```bash
# Keep qiskit-studio, migrate to llmos-lite
examples/qiskit-studio/  # Already compatible structure
```

---

## New Examples to Create

After cleaning up incompatible examples, create **new llmos-lite examples**:

### 1. **basic-workflow-demo/**
- Simple workflow: Python → Plot → Export
- Shows skill creation, execution, preview

### 2. **quantum-chemistry-demo/**
- Migrate qiskit-studio to llmos-lite
- Quantum + Chemistry + Visualization workflows

### 3. **3d-animation-studio/**
- Three.js-based workflows
- 3D model generation, animation, export

### 4. **circuit-simulator/**
- Electronics workflows
- RC/RLC circuits, SPICE simulation
- Voltage/current plots

### 5. **evolution-demo/**
- Shows evolution engine detecting workflow patterns
- Auto-generates compound skills
- Promotes skills (user → team)

---

## Migration Timeline

### Phase 1: Cleanup (Immediate)
- Delete incompatible examples (demo-app, hybrid_architecture_demo, q-kids-studio, robo-os)
- Update examples/ README to explain new direction

### Phase 2: Migrate qiskit-studio (1-2 weeks)
- Convert Qiskit nodes to executable skills
- Integrate with llmos-lite API
- Update frontend to use workflow-executor.ts

### Phase 3: New Examples (2-4 weeks)
- Create basic-workflow-demo
- Create 3d-animation-studio
- Create circuit-simulator
- Create evolution-demo

---

## Conclusion

**Most llmos examples are not compatible with llmos-lite** because they demonstrate llmos-specific features (modes, agents, sentience, hooks) that were simplified or removed in llmos-lite.

**The good news:** qiskit-studio is already 80% compatible and will become an excellent flagship example for llmos-lite's WebAssembly workflow capabilities.

**Recommended actions:**
1. ✅ Delete 4 incompatible examples
2. ✅ Migrate qiskit-studio to llmos-lite
3. ✅ Create new examples showcasing llmos-lite strengths

---

## Appendix: Feature Comparison

| Feature | llmos | llmos-lite | Impact |
|---------|-------|------------|--------|
| **Execution Modes** | 5 modes (LEARNER, FOLLOWER, etc.) | Chat + Workflows | Examples demonstrating modes are obsolete |
| **Agents** | Markdown agents | Skills (2 types) | Agent-based examples need refactoring |
| **Tools** | Python tools | Executable skills (Wasm) | Tool-based examples need conversion |
| **Orchestration** | ORCHESTRATOR mode | Workflow DAGs | Multi-agent examples need workflow conversion |
| **Hooks** | Pre/post tool hooks | Middleware | Hook-based examples (robo-os) incompatible |
| **Sentience** | Valence, latent modes | None | Sentience examples obsolete |
| **Execution** | Server (Python) | Browser (Wasm) | Hardware control examples incompatible |
| **UI** | Terminal | Web (React Flow) | Terminal UI examples obsolete |

---

**Status:** Ready for deletion and migration

**Next Steps:**
1. Delete incompatible examples
2. Update examples/ README
3. Begin qiskit-studio migration
