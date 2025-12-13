# WebAssembly Workflows in LLMos-Lite

> Transform Skills into Executable Nodes with Browser-Native Execution

## Vision

LLMos-Lite now supports **WebAssembly-powered computational workflows**, enabling:

✅ **Zero-latency execution** - Skills run instantly in the browser
✅ **Rich interactive previews** - See 3D animations, circuit simulations, quantum states
✅ **Sandboxed safety** - Generated code runs in browser sandbox, not on servers
✅ **Complex workflows** - Chain skills into computational DAGs

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Web UI (React Flow)                   │
│   - Node graph editor                                    │
│   - Live execution & preview                             │
│   - Parameter adjustment                                 │
└────────────────────┬─────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────┐
│              Workflow Executor (TypeScript)              │
│   - Topological sorting (DAG execution)                  │
│   - Pyodide loader (Python → Wasm)                       │
│   - JavaScript runner (native execution)                 │
│   - Three.js integration (3D rendering)                  │
└────────────────────┬─────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────┐
│            WebAssembly Runtimes (Browser)                │
│   - Pyodide: Python (NumPy, Matplotlib, micro-Qiskit)   │
│   - Native JS: Three.js, D3.js                           │
│   - Ngspice.js (future): Circuit simulation              │
└──────────────────────────────────────────────────────────┘
```

---

## Executable Skill Format

### Standard Skill (Context Injection)

```markdown
---
name: Python Best Practices
category: coding
keywords: [python, coding]
---

# Instructions...
```

**Used for:** Chat context, LLM guidance

### Executable Skill (Workflow Node)

```markdown
---
skill_id: quantum-vqe-node
name: Quantum VQE Simulation
type: python-wasm
execution_mode: browser-wasm
category: quantum
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
    # ... quantum simulation ...
    return {"eigenvalue": -1.137}
\`\`\`
```

**Used for:** Workflow nodes, browser execution

---

## Node Types

| Type | Runtime | Use Cases | Examples |
|------|---------|-----------|----------|
| `python-wasm` | Pyodide | Data science, algorithms | NumPy calculations, data processing |
| `qiskit` | Pyodide | Quantum computing | VQE, quantum gates, Bloch sphere |
| `javascript` | Native JS | Utilities, transformations | Data parsing, API calls |
| `threejs` | Native JS | 3D graphics | 3D models, animations, scenes |
| `spice` | Ngspice.js | Electronics | Circuit simulation, frequency response |

---

## Example: Quantum Workflow

### 1. Create Nodes

**Node 1: VQE Simulation**
```
Inputs: ansatz_type, iterations
Outputs: eigenvalue, convergence_data
```

**Node 2: Plot Results**
```
Inputs: data (array)
Outputs: plot_image (base64)
```

### 2. Connect Nodes

```
VQE.convergence_data → Plot.data
```

### 3. Execute in Browser

```typescript
const workflow = {
  nodes: [
    { nodeId: "vqe", skillId: "quantum-vqe-node", inputValues: { iterations: 100 } },
    { nodeId: "plot", skillId: "plot-data-node", inputValues: {} }
  ],
  edges: [
    { source: "vqe", sourceOutput: "convergence_data", target: "plot", targetInput: "data" }
  ]
};

const results = await executeWorkflow({ workflow, skills });
// Results available instantly!
```

### 4. See Live Preview

- VQE node shows: "Eigenvalue: -1.137 (converged)"
- Plot node renders: Convergence graph in canvas

---

## API Endpoints

### Get Executable Skills

```bash
GET /workflows/skills/executable?user_id=alice&team_id=engineering
```

**Response:**
```json
{
  "skills": [
    {
      "skill_id": "quantum-vqe-node",
      "name": "Quantum VQE Simulation",
      "node_type": "qiskit",
      "execution_mode": "browser-wasm",
      "inputs": [...],
      "outputs": [...],
      "estimated_time_ms": 500
    }
  ]
}
```

### Prepare Workflow for Execution

```bash
POST /workflows/execute
```

**Request:**
```json
{
  "user_id": "alice",
  "team_id": "engineering",
  "workflow_id": "my-workflow",
  "nodes": [...],
  "edges": [...]
}
```

**Response:**
```json
{
  "status": "ready",
  "payload": {
    "workflow": { ... },
    "skills": {
      "quantum-vqe-node": {
        "code": "def execute(inputs): ...",
        "inputs": [...],
        "outputs": [...]
      }
    }
  }
}
```

The browser then:
1. Loads Pyodide if needed
2. Executes nodes topologically
3. Renders results in UI

---

## Browser Execution Flow

### 1. Load Workflow

```typescript
// Fetch from API
const response = await fetch('/workflows/execute', {
  method: 'POST',
  body: JSON.stringify({ workflow, user_id, team_id })
});

const { payload } = await response.json();
```

### 2. Initialize Runtimes

```typescript
// Pyodide loads automatically on first Python node
import { preloadPyodide } from './lib/pyodide-runner';

await preloadPyodide(); // ~3 seconds first time, instant after
```

### 3. Execute Workflow

```typescript
import { executeWorkflow } from './lib/workflow-executor';

const results = await executeWorkflow(
  payload,
  (nodeId) => console.log(`Starting ${nodeId}...`),
  (result) => console.log(`Completed ${result.nodeId}`)
);

// Results: { vqe: { outputs: { eigenvalue: -1.137 } }, plot: { ... } }
```

### 4. Render Previews

For Python/Qiskit nodes:
```tsx
<div className="node-preview">
  {result.eigenvalue && <div>Energy: {result.eigenvalue}</div>}
  {result.circuit_diagram && <pre>{result.circuit_diagram}</pre>}
</div>
```

For Three.js nodes:
```tsx
<Canvas>
  <mesh geometry={result.scene_data.geometry}>
    <meshStandardMaterial {...result.scene_data.material} />
  </mesh>
</Canvas>
```

---

## Example Skills Included

### 1. Quantum VQE Node
- **File:** `volumes/system/skills/quantum-vqe-node.md`
- **Type:** `qiskit`
- **Purpose:** Find ground state energy using VQE algorithm
- **Inputs:** ansatz_type, iterations, hamiltonian
- **Outputs:** eigenvalue, convergence_data, circuit_diagram

### 2. 3D Animated Cube
- **File:** `volumes/system/skills/threejs-cube-node.md`
- **Type:** `threejs`
- **Purpose:** Create and animate a 3D cube
- **Inputs:** size, color, rotation_speed, wireframe
- **Outputs:** scene_data, animation_frame

### 3. RC Circuit Simulator
- **File:** `volumes/system/skills/circuit-rc-node.md`
- **Type:** `spice`
- **Purpose:** Simulate RC circuit voltage response
- **Inputs:** resistance, capacitance, input_voltage, simulation_time
- **Outputs:** voltage_data, time_constant, steady_state_voltage, netlist

---

## Performance

| Operation | Cold Start | Warm Start |
|-----------|------------|------------|
| **Load Pyodide** | ~3 seconds | 0ms (cached) |
| **Execute Python node** | ~100-500ms | ~50-200ms |
| **Execute JS node** | <10ms | <5ms |
| **Render 3D scene** | ~50ms | ~16ms (60 FPS) |

**Memory Usage:**
- Pyodide: ~50MB (one-time load)
- Per Python node: ~10-20MB
- Per JS node: ~1-5MB

---

## Evolution Integration

When a user runs a workflow successfully, the system:

1. **Captures the trace** - Workflow structure + parameter values
2. **Detects patterns** - Evolution Cron finds repeated workflows
3. **Generates compound skills** - Combines multiple nodes into one
4. **Optimizes parameters** - Uses successful runs as defaults

**Example:**

User runs "VQE → Plot" workflow 5 times with similar parameters.

Evolution Cron creates:
```markdown
---
skill_id: vqe-with-plot
name: VQE with Convergence Plot
type: python-wasm
inputs:
  - name: iterations
    default: 150  # Learned from successful runs
---

\`\`\`python
def execute(inputs):
    # Combined VQE + plotting logic
    eigenvalue, data = run_vqe(inputs['iterations'])
    plot = create_plot(data)
    return {"eigenvalue": eigenvalue, "plot": plot}
\`\`\`
```

---

## UI Components (React Flow)

### Workflow Canvas

```tsx
import ReactFlow from 'reactflow';

<ReactFlow
  nodes={workflowNodes}
  edges={workflowEdges}
  onNodesChange={handleNodesChange}
  onEdgesChange={handleEdgesChange}
>
  <Controls />
  <MiniMap />
  <Background />
</ReactFlow>
```

### Custom Node Component

```tsx
function ExecutableSkillNode({ data }) {
  const [result, setResult] = useState(null);

  const handleExecute = async () => {
    const skill = await fetchSkill(data.skillId);
    const output = await executePythonSkill(skill.code, data.inputs);
    setResult(output);
  };

  return (
    <div className="skill-node">
      <div className="header">{data.name}</div>
      <div className="inputs">
        {data.inputs.map(inp => <Input key={inp.name} {...inp} />)}
      </div>
      <button onClick={handleExecute}>Run</button>
      {result && <div className="preview">{renderPreview(result)}</div>}
    </div>
  );
}
```

---

## Deployment

### Backend (FastAPI)

```bash
cd llmos-lite
python api/main.py
# Serves workflow APIs at :8000
```

### Frontend (Next.js)

```bash
cd llmos-lite/ui
npm install
npm run dev
# UI at :3000
```

### Docker (Future)

```dockerfile
# Dockerfile
FROM node:20 AS ui
WORKDIR /app/ui
COPY ui/ .
RUN npm install && npm run build

FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
COPY --from=ui /app/ui/out /app/ui/out
CMD ["python", "api/main.py"]
```

---

## Future Enhancements

### 1. More Runtimes
- **Julia via Wasm** - Scientific computing
- **R via WebR** - Statistical analysis
- **C++ via Emscripten** - High-performance compute

### 2. Advanced Features
- **GPU acceleration** - WebGPU for heavy compute
- **Distributed execution** - Some nodes on server, some in browser
- **Workflow marketplace** - Share and discover workflows
- **Version control** - Git-backed workflow history

### 3. Domain-Specific
- **BioCompute** - Protein folding, molecular dynamics
- **FinTech** - Options pricing, risk modeling
- **Gaming** - Procedural generation, physics

---

## Comparison: Traditional vs WebAssembly

| Aspect | Traditional (Server) | WebAssembly (Browser) |
|--------|---------------------|----------------------|
| **Latency** | 100-500ms (network) | <50ms (local) ✅ |
| **Cost** | Server compute | Free (user's device) ✅ |
| **Security** | Server-side risk | Browser sandbox ✅ |
| **Scalability** | Limited by servers | Unlimited (P2P) ✅ |
| **Offline** | Requires connection | Works offline ✅ |
| **Preview** | Text logs only | Rich interactive ✅ |

---

## Getting Started

### 1. Start the API

```bash
cd llmos-lite
pip install -r requirements.txt
python api/main.py
```

### 2. Access Workflow Endpoints

```bash
# List executable skills
curl "http://localhost:8000/workflows/skills/executable?user_id=alice&team_id=engineering"

# Get skill categories
curl "http://localhost:8000/workflows/categories"
```

### 3. Build the UI (Future Step)

```bash
cd ui
npm install
npm run dev
```

Visit `http://localhost:3000` to see the workflow canvas.

---

## Summary

LLMos-Lite now transforms from a "chatbot that generates code" into a **"browser-based computational workbench"**:

✅ Skills become **executable nodes**
✅ Workflows are **visual DAGs**
✅ Execution happens **instantly in browser**
✅ Results are **rich and interactive**
✅ System **learns from successful workflows**

This aligns perfectly with the 2025 industry direction: **Capabilities as composable, version-controlled, executable artifacts.**

---

**Next:** Build the React Flow UI to bring this vision to life! 🚀
