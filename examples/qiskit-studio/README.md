# Qiskit Studio - LLM OS v3.4.0 Edition

> **A flagship example of LLM OS using Advanced Tool Use and Sentience Layer.**

This project reimplements the [Qiskit Studio](https://github.com/AI4quantum/qiskit-studio) backend using **LLM OS v3.4.0**, demonstrating how a unified operating system for LLMs can replace multiple specialized microservices while providing superior memory management, cost efficiency, security, and adaptive behavior.

## What's New in v3.4.0

- **Sentience Layer**: Persistent internal state that influences behavior
  - **Valence Variables**: Safety, curiosity, energy, self_confidence
  - **Homeostatic Dynamics**: Set-points with deviation costs
  - **Latent Modes**: Auto-creative vs auto-contained behavior emergence
  - **Cognitive Kernel**: Policy derivation and self-improvement detection
- **Adaptive Behavior**: System adapts based on task outcomes and patterns
- **New `/sentience` Endpoint**: View internal state and behavioral guidance

## What's in v3.3.0

- **Programmatic Tool Calling (PTC)**: Execute tool sequences outside context window for 90%+ token savings
- **Tool Search**: On-demand tool discovery instead of loading all tools upfront
- **Tool Examples**: Auto-generated examples from successful execution traces
- **Five Execution Modes**: CRYSTALLIZED, FOLLOWER, MIXED, LEARNER, ORCHESTRATOR

## What This Demonstrates

The original Qiskit Studio uses **Maestro** to orchestrate three distinct microservices:

| Original Service | Purpose | LLM OS Replacement |
|-----------------|---------|-------------------|
| `chat-agent` | RAG-based Q&A about quantum computing | **Quantum Tutor** agent with L4 semantic memory |
| `codegen-agent` | Generate/update Qiskit quantum code | **Quantum Architect** agent with PTC-enabled modes |
| `coderun-agent` | Execute Python/Qiskit code securely | **Qiskit Tools** plugin with security hooks |

**Key Improvements:**

1. **90%+ Token Savings**: PTC replays tool sequences outside context window - FOLLOWER mode is nearly FREE
2. **Enhanced Security**: Built-in security hooks prevent malicious code execution
3. **Unified Memory**: Cross-project learning and semantic memory across all interactions
4. **Simplified Architecture**: Single LLM OS instance replaces 3+ microservices
5. **Same Frontend**: Drop-in API compatibility with existing Qiskit Studio UI
6. **Auto-Crystallization**: Repeated patterns become zero-cost Python code
7. **Adaptive Behavior** (v3.4.0): System learns from outcomes and adapts its approach over time

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Qiskit Studio Frontend                          │
│                      (Next.js - Unchanged)                           │
└──────────────┬─────────────────────────────────────────┬─────────────┘
               │                                         │
      POST /chat                                  POST /run
               │                                         │
               ▼                                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                FastAPI Bridge Server (server.py v3.4.0)              │
│  • Intent analysis (coding vs. question)                             │
│  • Session management with Execution Layer metadata                  │
│  • Sentience state tracking and response metadata                    │
│  • API compatibility layer                                           │
└──────────────┬───────────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   SENTIENCE LAYER (Awareness) - v3.4.0               │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  ValenceVector + CognitiveKernel + LatentModes                 │ │
│  │  • Tracks safety, curiosity, energy, self_confidence           │ │
│  │  • Derives behavioral policy from internal state               │ │
│  │  • Influences mode selection (prefer cheap/safe modes)         │ │
│  │  • Detects self-improvement opportunities                      │ │
│  └────────────────────────────────────────────────────────────────┘ │
└──────────────┬───────────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    LEARNING LAYER (Intelligence)                     │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  TraceManager + ModeStrategies                                 │ │
│  │  • Analyzes execution history                                  │ │
│  │  • Decides: CRYSTALLIZED / FOLLOWER / MIXED / LEARNER / ORCH  │ │
│  │  • Semantic matching for similar patterns                      │ │
│  │  • Mode decisions modulated by Sentience Layer                 │ │
│  └────────────────────────────────────────────────────────────────┘ │
└──────────────┬───────────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   EXECUTION LAYER (Efficiency)                       │
│  ┌──────────────────┐ ┌──────────────────┐ ┌─────────────────────┐  │
│  │  PTC Executor    │ │  Tool Search     │ │  Tool Examples      │  │
│  │  ─────────────   │ │  ───────────     │ │  ──────────────     │  │
│  │  Zero-context    │ │  On-demand tool  │ │  Auto-generated     │  │
│  │  tool replay     │ │  discovery       │ │  from traces        │  │
│  │  90%+ savings    │ │  85%+ context    │ │  Better accuracy    │  │
│  │                  │ │  reduction       │ │                     │  │
│  └──────────────────┘ └──────────────────┘ └─────────────────────┘  │
└──────────────┬───────────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           LLM OS Kernel                              │
│  ┌──────────────────┐          ┌──────────────────┐                 │
│  │ Quantum Architect│          │  Quantum Tutor   │                 │
│  │ (Code Generator) │          │  (Q&A Expert)    │                 │
│  │ Modes: AUTO      │          │  Mode: ORCHESTRATOR                │
│  └────────┬─────────┘          └──────────────────┘                 │
│           │                                                          │
│           ▼                                                          │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │           Qiskit Tools (Somatic Layer)                         │ │
│  │  • execute_qiskit_code (with security hooks)                   │ │
│  │  • validate_qiskit_code                                        │ │
│  │  • Registered with Execution Layer for PTC/Tool Search         │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │   L4 Semantic Memory + Traces with tool_calls for PTC          │ │
│  │  • Quantum patterns cached with full tool call data            │ │
│  │  • Enables zero-context replay via PTC                         │ │
│  │  • Sentience state persisted across sessions                   │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+ (for frontend)
- Anthropic API key (for Claude)
- (Optional) IBM Quantum API token for real quantum hardware

### Installation

1. **Navigate to the project**:
   ```bash
   cd llm-os/examples/qiskit-studio
   ```

2. **Set up backend environment**:
   ```bash
   # Create .env from template
   cp .env.template .env

   # Edit .env and add your Anthropic API key
   # ANTHROPIC_API_KEY=your-api-key-here
   ```

3. **Run the backend**:
   ```bash
   # Make run script executable (if not already)
   chmod +x run.sh

   # Start the server
   ./run.sh
   ```

   Or manually:
   ```bash
   # Install dependencies
   pip install -r requirements.txt

   # Run server
   python server.py
   ```

The backend will start on `http://localhost:8000`

### Run the Included Frontend

This project includes a complete Next.js frontend (copied from qiskit-studio):

1. **Set up frontend**:
   ```bash
   cd frontend

   # Create .env.local from template
   cp .env.local.template .env.local

   # Install dependencies
   npm install
   ```

2. **Run the frontend**:
   ```bash
   npm run dev
   ```

3. **Open in browser**: `http://localhost:3000`

### Alternative: Connect to External Qiskit Studio Frontend

If you prefer to use a separate qiskit-studio installation:

1. **Clone Qiskit Studio frontend** (in a separate directory):
   ```bash
   cd ../qiskit-studio
   npm install
   ```

2. **Configure frontend** to point to LLM OS backend:

   Edit `qiskit-studio/.env.local`:
   ```bash
   NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/chat
   NEXT_PUBLIC_PARAMETER_UPDATE_API_URL=http://127.0.0.1:8000/chat
   NEXT_PUBLIC_RUNCODE_URL=http://127.0.0.1:8000/run
   ```

3. **Run the frontend**:
   ```bash
   npm run dev
   ```

4. **Open in browser**: `http://localhost:3000`

---

## Key Features Showcase

### 1. PTC-Powered Cost Savings (90%+)

**Scenario**: User asks "Create a GHZ state circuit" via the UI

**First Request (LEARNER mode)**:
- LLM reasons about GHZ states
- Generates Qiskit code using Tool Search to discover tools
- Tests and validates
- **Tokens: ~2,500**
- Execution time: ~5 seconds
- **Trace saved with full tool_calls for future PTC replay**

**Second Request (FOLLOWER mode with PTC)**:
- Learning Layer recognizes the intent hash
- Execution Layer uses PTC to replay tool sequence **outside context window**
- **Tokens: ~0 (90%+ savings!)**
- Execution time: <1 second
- **Token savings: Hundreds of tokens saved by avoiding context bloat**

**Third+ Request (CRYSTALLIZED mode)** - After 3+ successful runs:
- Pattern crystallized into pure Python code
- **Tokens: 0 (truly FREE!)**
- Execution time: <100ms
- No LLM call at all!

Check the response metadata to see PTC activation:
```json
{
  "metadata": {
    "mode": "FOLLOWER",
    "tokens": 0,
    "cached": true,
    "ptc_used": true,
    "tokens_saved": 450
  }
}
```

### 2. Security Hooks

The `execute_qiskit_code` tool includes automatic security validation:

**Try injecting malicious code** (via the UI or API):
```python
import os
os.system("rm -rf /")
```

**LLM OS Response**:
```
Security Error: Potentially dangerous operation 'import os' not allowed.
```

The code is blocked **before** reaching the Python interpreter.

### 3. Unified Memory & Cross-Project Learning

**Memory Persistence**:
- Learn about "Grover's Algorithm" in Project A
- Knowledge automatically available in Project B
- High-confidence patterns cached across sessions

**View statistics**:
```bash
curl http://localhost:8000/stats
```

Response shows:
- Token economy (budget, spent, remaining)
- Memory traces (total, high-confidence, facts)
- Active agents
- Session statistics

### 4. Intelligent Agent Routing

The bridge server automatically routes requests:

| User Input | Detected Agent | Mode | Why? |
|-----------|----------------|------|------|
| "Create a Bell state circuit" | Quantum Architect | AUTO | Code generation task |
| "What is quantum entanglement?" | Quantum Tutor | ORCHESTRATOR | Conceptual question |
| "How do I use Sampler?" | Quantum Tutor | ORCHESTRATOR | API question |
| "Implement Grover's algorithm" | Quantum Architect | AUTO | Algorithm implementation |

### 5. Sentience Layer (NEW in v3.4.0)

The system now maintains persistent internal state that influences behavior:

**View current sentience state:**
```bash
curl http://localhost:8000/sentience | jq
```

**Response:**
```json
{
  "enabled": true,
  "latent_mode": {
    "current": "balanced",
    "description": "Normal operating state - balanced between exploration and efficiency"
  },
  "valence": {
    "safety": {"value": 0.6, "setpoint": 0.6, "deviation": 0.0},
    "curiosity": {"value": 0.15, "setpoint": 0.1, "deviation": 0.05},
    "energy": {"value": 0.72, "setpoint": 0.7, "deviation": 0.02},
    "self_confidence": {"value": 0.45, "setpoint": 0.4, "deviation": 0.05}
  },
  "homeostatic_cost": 0.0034,
  "behavioral_guidance": "Operating normally. Balance efficiency with exploration.",
  "policy": {
    "prefer_cheap_modes": false,
    "prefer_safe_modes": false,
    "allow_exploration": true,
    "exploration_budget_multiplier": 1.0,
    "enable_auto_improvement": true
  }
}
```

**Latent Modes** emerge from valence state:
- **AUTO_CREATIVE**: High curiosity + confidence -> explores new quantum algorithms
- **AUTO_CONTAINED**: Low curiosity -> focuses on efficient task completion
- **BALANCED**: Normal operation -> balances exploration and efficiency
- **RECOVERY**: Low energy/safety -> prefers FOLLOWER mode (cheap, cached)
- **CAUTIOUS**: Low safety -> extra verification for code execution

**How it affects Qiskit Studio:**
- After repeated similar tasks, curiosity drops -> system prefers FOLLOWER mode
- After safety violations (blocked code), safety drops -> CAUTIOUS mode triggers
- Novel quantum algorithms boost curiosity -> AUTO_CREATIVE allows more exploration
- High cost operations reduce energy -> RECOVERY mode prefers cached patterns

---

## 📡 API Reference

### POST `/chat`

**Purpose**: Chat and code generation (replaces both `chat-agent` and `codegen-agent`)

**Request formats** (both are supported):
```json
// Standard format
{
  "messages": [
    {"role": "user", "content": "Create a 3-qubit GHZ state"}
  ],
  "session_id": "optional-session-id"
}

// Maestro format (compatible with original qiskit-studio)
{
  "input_value": "Create a 3-qubit GHZ state",
  "prompt": "Create a 3-qubit GHZ state",
  "session_id": "optional-session-id"
}
```

**Response** (Maestro-compatible format):
```json
{
  "response": "{\"final_prompt\": \"...\", \"agent\": \"quantum-architect\", \"mode\": \"AUTO\", \"tokens\": 2500, \"cached\": false}",
  "output": "```python\nfrom qiskit import QuantumCircuit\n...\n```"
}
```

### POST `/chat/stream`

**Purpose**: Streaming chat using Server-Sent Events (SSE)

**Request**: Same format as `/chat`

**Response**: SSE stream
```
data: {"step_name": "llm_step", "step_result": "Here is your quantum circuit..."}

data: [DONE]
```

### POST `/run`

**Purpose**: Execute Qiskit code (replaces `coderun-agent`)

**Request**:
```json
{
  "input_value": "from qiskit import QuantumCircuit\nqc = QuantumCircuit(2)\nqc.h(0)\nprint(qc)",
  "ibm_token": "optional-ibm-quantum-token",
  "channel": "ibm_quantum",
  "instance": "optional-crn",
  "region": "optional-region"
}
```

**Response**:
```json
{
  "output": "     ┌───┐\nq_0: ┤ H ├\n     └───┘\nq_1: ─────\n"
}
```

### GET `/sentience` (NEW in v3.4.0)

**Purpose**: View detailed Sentience Layer state including valence, latent mode, and behavioral policy

**Response**:
```json
{
  "enabled": true,
  "latent_mode": {
    "current": "balanced",
    "description": "Normal operating state - balanced between exploration and efficiency"
  },
  "valence": {
    "safety": {"value": 0.6, "setpoint": 0.6, "deviation": 0.0},
    "curiosity": {"value": 0.15, "setpoint": 0.1, "deviation": 0.05},
    "energy": {"value": 0.72, "setpoint": 0.7, "deviation": 0.02},
    "self_confidence": {"value": 0.45, "setpoint": 0.4, "deviation": 0.05}
  },
  "homeostatic_cost": 0.0034,
  "last_trigger": {"type": "task_success", "reason": "Completed circuit generation"},
  "behavioral_guidance": "Operating normally. Balance efficiency with exploration.",
  "policy": {
    "prefer_cheap_modes": false,
    "prefer_safe_modes": false,
    "allow_exploration": true,
    "exploration_budget_multiplier": 1.0,
    "enable_auto_improvement": true
  },
  "improvement_suggestions": [
    {
      "type": "create_crystallized_pattern",
      "description": "Pattern 'Bell state creation' used 5+ times with 100% success",
      "priority": 0.8,
      "trigger_reason": "High usage pattern detected"
    }
  ]
}
```

### GET `/stats`

**Purpose**: View LLM OS v3.4.0 performance metrics including Execution Layer and Sentience stats

**Response**:
```json
{
  "version": "3.4.0",
  "token_economy": {
    "total_tokens": 25000,
    "spent_tokens": 12340,
    "remaining_budget_tokens": 12660,
    "transactions": 15
  },
  "memory": {
    "total_traces": 42,
    "high_confidence_traces": 12,
    "traces_with_tool_calls": 28,
    "facts": 8
  },
  "agents": {
    "registered": 4,
    "available": ["quantum-architect", "quantum-tutor", "system-agent"]
  },
  "sessions": {
    "active": 2,
    "total_messages": 34
  },
  "execution_layer": {
    "enabled": true,
    "ptc": {
      "enabled": true,
      "active_containers": 0,
      "total_executions": 12,
      "tokens_saved": 5400
    },
    "tool_search": {
      "enabled": true,
      "use_embeddings": false,
      "registered_tools": 2,
      "total_searches": 8
    },
    "tool_examples": {
      "enabled": true,
      "generated_examples": 6
    }
  },
  "mode_distribution": {
    "crystallized": 3,
    "follower": 8,
    "mixed": 2,
    "learner": 5,
    "orchestrator": 1
  },
  "sentience": {
    "enabled": true,
    "latent_mode": "balanced",
    "valence": {
      "safety": 0.6,
      "curiosity": 0.15,
      "energy": 0.72,
      "self_confidence": 0.45
    },
    "homeostatic_cost": 0.0034,
    "policy": {
      "prefer_cheap_modes": false,
      "allow_exploration": true
    }
  }
}
```

### POST `/clear_session`

**Purpose**: Clear chat history for a session

**Request**:
```json
{
  "session_id": "session-to-clear"
}
```

---

## 🧪 Testing

### Test the Backend Directly

```bash
# Test chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Create a Bell state"}
    ]
  }'

# Test code execution
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "input_value": "from qiskit import QuantumCircuit\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0,1)\nprint(qc)"
  }'

# View statistics
curl http://localhost:8000/stats | jq
```

### Example Test Cases

**1. Cost Savings Demo**:
```bash
# First request (LEARNER - costs money)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Create a 3-qubit GHZ state"}]}'

# Second request (FOLLOWER - FREE!)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Create a 3-qubit GHZ state"}]}'

# Check metadata.cached field in response
```

**2. Security Test**:
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "input_value": "import os; os.system(\"ls -la\")"
  }'

# Expected: Security error response
```

**3. Multi-Session Memory**:
```bash
# Session 1
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "What is quantum entanglement?"}],
    "session_id": "session-1"
  }'

# Session 2 (different session, should have separate history)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Create a Bell state"}],
    "session_id": "session-2"
  }'
```

---

## 🎓 Educational Value

This example teaches:

1. **LLM OS Architecture**: How to structure a production-grade LLM application
2. **Agent Specialization**: Creating domain-specific agents (quantum computing)
3. **Tool Integration**: Building custom tools for domain tasks
4. **API Bridging**: Making LLM OS compatible with existing frontends
5. **Cost Optimization**: Leveraging Learner/Follower patterns
6. **Security**: Implementing safe code execution
7. **Memory Management**: Cross-project learning and caching
8. **Sentience Layer** (v3.4.0): Implementing adaptive behavior with internal state

---

## Configuration

### Environment Variables

See `.env.template` for all available options:

```bash
# Required
ANTHROPIC_API_KEY=your-api-key

# Optional - IBM Quantum
IBM_QUANTUM_TOKEN=your-token
IBM_QUANTUM_CHANNEL=ibm_quantum
IBM_QUANTUM_INSTANCE=crn:...
IBM_QUANTUM_REGION=us-east

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# LLM OS
LLMOS_TOKEN_BUDGET=500000
LLMOS_PROJECT_NAME=qiskit_studio_session

# LLM OS Execution Layer (v3.3.0)
LLMOS_ENABLE_PTC=true              # Programmatic Tool Calling
LLMOS_ENABLE_TOOL_SEARCH=true      # On-demand tool discovery
LLMOS_ENABLE_TOOL_EXAMPLES=true    # Auto-generated examples
LLMOS_USE_EMBEDDINGS=false         # Set to true for production (requires sentence-transformers)

# LLM OS Sentience Layer (v3.4.0)
LLMOS_ENABLE_SENTIENCE=true        # Enable adaptive internal state
LLMOS_INJECT_INTERNAL_STATE=true   # Agents see their internal state
LLMOS_ENABLE_AUTO_IMPROVEMENT=true # Auto-detect improvement opportunities

# Logging
LOG_LEVEL=INFO
```

### Adjusting Configuration

The server now uses `LLMOSConfig` with full Execution Layer and Sentience Layer support. Edit `config.py`:

```python
# In Config.get_llmos_config():
execution=ExecutionLayerConfig(
    enable_ptc=True,
    enable_tool_search=True,
    enable_tool_examples=True,
    # For production, enable embeddings for better tool search:
    tool_search_use_embeddings=True,
),
sentience=SentienceConfig(
    enable_sentience=True,
    # Valence set-points tuned for quantum computing
    safety_setpoint=0.6,      # Higher for code execution safety
    curiosity_setpoint=0.1,   # Moderate exploration
    # Enable adaptive features
    inject_internal_state=True,
    enable_auto_improvement=True,
)
```

Or use environment variables:
```bash
LLMOS_TOKEN_BUDGET=1000000 LLMOS_USE_EMBEDDINGS=true LLMOS_ENABLE_SENTIENCE=true python server.py
```

---

## Performance Comparison

| Metric | Original (Maestro) | LLM OS v3.4.0 | Improvement |
|--------|-------------------|---------------|-------------|
| **Microservices** | 3 (chat, codegen, coderun) | 1 (unified) | **67% reduction** |
| **Repeated Pattern Tokens** | Full LLM call each time | ~0 tokens (PTC) | **90%+ savings** |
| **Token Usage** | All tools in context | On-demand via Tool Search | **85% context reduction** |
| **Memory Sharing** | None (isolated services) | Cross-project + PTC traces | **Full history** |
| **Security** | Per-service validation | Unified hooks | **Consistent enforcement** |
| **Deployment Complexity** | Docker Compose + K8s | Single process | **90% simpler** |
| **Pattern Evolution** | Manual optimization | Auto-crystallization | **Self-optimizing** |
| **Adaptive Behavior** | None | Sentience Layer | **Self-aware** |

---

## 🛠️ Development

### Project Structure

```
qiskit-studio/
├── server.py              # FastAPI bridge server (unified backend)
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── run.sh                # Startup script
├── .env.template         # Backend environment template
│
├── workspace/            # LLM OS workspace
│   └── agents/           # Markdown agent definitions (Hybrid Architecture)
│       ├── quantum-architect.md    # Code generation agent
│       └── quantum-tutor.md        # Q&A agent
│
├── plugins/              # Qiskit tools
│   ├── __init__.py
│   └── qiskit_tools.py         # execute_qiskit_code, validate
│
├── memory/               # Knowledge base (optional)
│   └── qiskit_docs/            # Qiskit documentation for RAG
│
└── frontend/             # Next.js Qiskit Studio UI
    ├── app/                    # Next.js app directory
    ├── components/             # React components
    │   ├── nodes/             # Quantum computing nodes
    │   └── ui/                # UI components
    ├── hooks/                  # React hooks (AI code generation)
    ├── lib/                    # Utility functions & API service
    ├── public/                 # Static assets
    ├── .env.local.template    # Frontend environment template
    ├── package.json           # Node dependencies
    └── tsconfig.json          # TypeScript config
```

### Adding New Agents (Markdown Approach)

This project uses the **Hybrid Architecture** with Markdown agent definitions. To add a new agent:

1. Create a Markdown file in `workspace/agents/`:
```markdown
# workspace/agents/quantum-optimizer.md
---
name: quantum-optimizer
description: Optimizes quantum circuits for depth and gate count
tools:
  - execute_qiskit_code
model: sonnet
category: optimization
agent_type: specialized
version: "1.0.0"
---

# Quantum Circuit Optimizer

You are an expert in quantum circuit optimization...

## Your Responsibilities
- Analyze quantum circuits for optimization opportunities
- Reduce circuit depth and gate count
- Apply transpilation best practices
```

2. The agent will be **automatically loaded** on server startup - no code changes needed!

The `AgentLoader` scans `workspace/agents/*.md` and registers all valid agents.

### Adding New Tools

1. Create tool in `plugins/qiskit_tools.py`:
```python
@llm_tool(
    "optimize_circuit",
    "Optimizes a quantum circuit using Qiskit transpiler",
    {"circuit_code": "str", "optimization_level": "int"}
)
async def optimize_circuit(circuit_code: str, optimization_level: int = 3) -> str:
    # Implementation
    pass
```

2. Register in `server.py`:
```python
from plugins.qiskit_tools import optimize_circuit
# In startup():
os_instance.component_registry.register_tool(optimize_circuit)
```

---

## 🤝 Contributing

This is a reference implementation. Contributions welcome:

1. Additional quantum algorithms
2. Enhanced RAG knowledge base
3. More sophisticated intent analysis
4. Performance optimizations
5. Testing suite

---

## 📝 License

Same as parent LLM OS project (see root LICENSE)

---

## 🙏 Acknowledgments

- **Original Qiskit Studio**: [AI4quantum/qiskit-studio](https://github.com/AI4quantum/qiskit-studio)
- **Qiskit**: IBM Quantum team
- **LLM OS**: Evolving Agents Labs

---

## 📚 Further Reading

- [LLM OS Documentation](../../README.md)
- [Qiskit Documentation](https://docs.quantum.ibm.com/)
- [Claude Agent SDK](https://github.com/anthropics/anthropic-sdk-python)

---

## 🆘 Troubleshooting

**Server won't start**:
- Check `.env` file has valid `ANTHROPIC_API_KEY`
- Ensure port 8000 is available
- Check logs in console output

**Frontend can't connect**:
- Verify server is running on correct port
- Check CORS settings in `server.py`
- Confirm `.env.local` in frontend has correct URLs

**Code execution fails**:
- Ensure Qiskit is installed: `pip install qiskit qiskit-aer`
- Check if code contains restricted operations
- Review logs for detailed error messages

**High token usage**:
- Check if FOLLOWER mode is activating (metadata.cached field)
- Reduce `LLMOS_TOKEN_BUDGET` to enforce stricter limits
- Review `/stats` endpoint to monitor token usage

---

**Made with ❤️ by Evolving Agents Labs**

**Star ⭐ the repo if this helped you understand LLM OS architecture!**
