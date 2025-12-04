# LLM OS - Examples

This directory contains comprehensive examples demonstrating LLM OS v3.5.0 capabilities.

## 🌟 NEW: Adaptive Agents (v3.5.0) - The Flagship Feature

**Per-query agent adaptation** that evolves based on sentience state and learned patterns!

### DynamicAgentManager - The Core Innovation

The **DynamicAgentManager** provides six adaptation strategies that work together:

| Strategy | What It Does |
|----------|--------------|
| **Sentience-Driven** | High curiosity → add exploration tools; Low safety → remove dangerous tools |
| **Trace-Driven** | Failure patterns → constraints; Success patterns → prompt enhancement |
| **Memory-Guided** | Select best agent based on past performance on similar tasks |
| **Model Selection** | Simple tasks → haiku; Complex/creative → opus; Default → sonnet |
| **Prompt Enhancement** | Inject successful traces as few-shot examples |
| **Agent Evolution** | After 5+ executions, evolve agents based on metrics |

**Quick Start:**
```bash
cd examples/demo-app && python demo_main.py
# Select "5. Adaptive Agents" demo
```

**All examples now include `/adaptive` endpoints** for monitoring agent metrics:
```bash
curl http://localhost:8000/adaptive
# Returns: agent metrics, evolution status, sentience-driven adaptations
```

**Why This Matters:**
- **Closes the learning loop**: Agents improve from every execution
- **Safety-first adaptation**: Low safety valence restricts dangerous tools
- **Performance tracking**: Monitor success rates and token usage per agent
- **Automatic evolution**: Agents evolve after sufficient executions

---

## 📚 Core Examples

These are the primary examples showcasing LLM OS capabilities:

### 1. Qiskit Studio (`qiskit-studio/`) - v3.5.0

**A flagship example** showing LLM OS with **Adaptive Agents and Quantum-Optimized Model Selection**.

**What it demonstrates:**
- 🧬 **Adaptive Agents (v3.5.0)**: DynamicAgentManager with quantum-optimized model selection
- 📝 **Markdown Agents**: Agents defined in `workspace/agents/*.md` files (no Python!)
- 💰 **Token Savings**: Learner → Follower caching (100% savings on repeated tasks)
- 🔒 **Enhanced Security**: Multi-layer code execution protection
- 🧠 **Unified Memory**: Cross-project learning and semantic memory
- ⚡ **Simplified Architecture**: Single process replaces 3+ microservices
- 🎨 **API Compatibility**: Works with existing Qiskit Studio frontend
- 📊 **New `/adaptive` Endpoint**: Monitor agent metrics and evolution status

**Quick Start:**
```bash
cd qiskit-studio
./run.sh
```

**Full Documentation:** See [qiskit-studio/README.md](qiskit-studio/README.md)

---

### 2. Demo App (`demo-app/`) - v3.5.0

**Rich interactive terminal application** with menu-driven scenarios.

**What it demonstrates:**
- 🧬 **Adaptive Agents (v3.5.0)**: New demo scenario for DynamicAgentManager
- 📊 **7 Real-World Scenarios**: Data pipelines, code generation, research, DevOps, etc.
- 💡 **Token Analysis**: Detailed token tracking and savings demonstrations
- 📈 **Visual Feedback**: Beautiful terminal UI using Rich library
- ⏱️  **Performance Metrics**: Execution time, steps completed, success rates
- 🎯 **Targeted Demos**: Each scenario highlights specific LLM OS features

**Quick Start:**
```bash
cd demo-app
python demo_main.py
```

**Available Scenarios:**
1. **Data Processing Pipeline** - Multi-agent orchestration (3 agents)
2. **Code Generation Workflow** - Learner → Follower savings demo
3. **Research Assistant** - Complex orchestration (⚠️ has timeouts)
4. **DevOps Automation** - Security hooks in action
5. **Cross-Project Learning** - Pattern detection across projects
6. **Token Optimization** - Run same task 5x, show savings
7. **SDK Hooks** - All Phase 2.5 hooks demonstrated

**Command-line options:**
```bash
python demo_main.py --budget 50.0          # Set budget
python demo_main.py --scenario devops      # Run specific scenario
python demo_main.py --all                  # Run all scenarios
```

**Full Documentation:** See [demo-app/README.md](demo-app/README.md)

---

### 3. Q-Kids Studio (`q-kids-studio/`)

**Educational quantum computing platform** for children ages 8-12.

**What it demonstrates:**
- 🎮 **Kid-Friendly Learning**: Block-based programming (like Scratch for quantum!)
- 🦉 **AI Tutoring**: Professor Q agent explains quantum concepts with stories
- 🎯 **Adaptive Difficulty**: Game Master adjusts challenges based on performance
- 💰 **Token Optimization**: Learner → Follower saves 99%+ on repeated hints
- 🔒 **Safety-First**: Multiple layers protecting kids from dangerous operations
- 📊 **Progress Tracking**: Skill trees, badges, missions, leaderboards
- 🌟 **6 Progressive Missions**: Superposition → Entanglement → VQE algorithms

**Quick Start:**
```bash
cd q-kids-studio
./run.sh
```

**What Kids Learn:**
- Mission 1: Superposition ("Spinning Coin")
- Mission 2: Entanglement ("Magic Twin Telepathy")
- Mission 3: Phase & Interference ("Secret Color Codes")
- Mission 4: Quantum Teleportation ("Teleportation Beam")
- Mission 5: Error Correction ("Noise Monster Shields")
- Mission 6: VQE Algorithm ("Valley Hunter")

**Full Documentation:** See [q-kids-studio/README.md](q-kids-studio/README.md)

---

### 4. RoboOS (`robo-os/`) - v3.5.0

**LLM OS as the brain of a robotic arm** - Natural language robot control with multi-layer safety.

**What it demonstrates:**
- 🧬 **Adaptive Agents (v3.5.0)**: Safety-driven tool restriction when safety valence is low
- 🤖 **Natural Language Control**: Command robots with plain English
- 🛡️ **Multi-Layer Safety**: PreToolUse hook prevents dangerous operations
- 👥 **Multi-Agent Coordination**: Operator + Safety Officer collaboration
- 📹 **State Visualization**: ASCII cockpit view and overhead map
- 💰 **Learner → Follower**: Teach once, replay forever (100% token savings)
- 🔌 **FastAPI Backend**: Production-ready REST API
- 🌊 **WebSocket Support**: Real-time state updates with adaptive agent state
- 📊 **New `/adaptive` Endpoint**: Monitor robotics-specific safety analysis

**Quick Start:**
```bash
cd robo-os
./run.sh
```

**Key Features:**
- **Somatic Layer**: Robot controller plugin with 7 control tools
- **Cognitive Layer**: Operator agent (control) + Safety Officer (monitoring)
- **Safety Hook**: Validates workspace bounds, prohibited zones, speed limits
- **Camera Feeds**: Cockpit HUD and overhead map views
- **Emergency Systems**: Instant halt with system lock-out

**Example Commands:**
```
"Move 30cm to the right"
"Pick up object at (1.5, 1.0, 0.5)"
"Show me the cockpit view"
"Return to home position"
```

**Safety Demonstrations:**
- Workspace boundary enforcement (-2 to 2m in X/Y, 0 to 3m in Z)
- Prohibited zone avoidance (0.5m safety radius)
- Speed limiting (max 0.5m per command)
- Emergency stop with violation logging

**Full Documentation:** See [robo-os/README.md](robo-os/README.md)

---

## 📦 Legacy Examples

**Looking for programmatic agent examples?** See [legacy/README.md](legacy/README.md)

The `legacy/` directory contains examples from earlier versions (v3.1.0 and before) that demonstrate **programmatic Python agent creation**. These still work perfectly but have been superseded by the **Markdown-based Hybrid Architecture** approach.

---

## 🎯 Which Example Should I Use?

| If you want to... | Use | Why |
|------------------|-----|-----|
| **⭐ Understand Adaptive Agents (v3.5.0)** | **Demo App** | **The flagship - per-query adaptation, agent evolution** |
| See DynamicAgentManager in action | **Demo App (Scenario 5)** or **Qiskit Studio** | Full adaptive agents demo |
| See a production-ready backend | **Qiskit Studio** | Drop-in microservice replacement with FastAPI + Adaptive Agents |
| Build educational tools for kids | **Q-Kids Studio** | Kid-safe, gamified, adaptive quantum learning |
| Control robots with natural language | **RoboOS** | Safety-driven adaptation, multi-layer safety |
| Run impressive demos with visuals | **Demo App** | Rich terminal UI, 7 scenarios, perfect for stakeholders |
| Learn about quantum computing | **Qiskit Studio** or **Q-Kids Studio** | Domain-specific quantum agents and tools |
| Understand token savings | **Qiskit Studio** or **Demo App** | Learner→Follower demo with metrics |
| See multi-agent orchestration | **Demo App (Scenario 1)** or **Qiskit Studio** | Multiple agents collaborating |
| Test security hooks | **RoboOS** or **Demo App (Scenario 4)** | Safety validation in action |
| Build adaptive AI tutors | **Q-Kids Studio** | Professor Q agent with context-aware hints |
| Robot safety systems | **RoboOS** | Safety-driven tool restriction, workspace bounds |
| Monitor agent performance | **Qiskit Studio** or **RoboOS** | `/adaptive` endpoint for metrics |
| Explore Python API internals | **legacy/multi_agent_example.py** | Programmatic agent creation (archived) |

---

## 🚀 General Setup

All examples require:

1. **Python 3.10+**
2. **Anthropic API Key**:
   ```bash
   export ANTHROPIC_API_KEY=your-key-here
   ```
3. **Install LLM OS** (if running from repository root):
   ```bash
   # From llm-os root directory
   pip install -e .
   ```

---

## 📖 Learn More

- **LLM OS Documentation**: See [../README.md](../README.md) for architecture overview
- **Phase 1 Patterns**: Configuration, Strategy, Dependency Injection (NEW 2025-11-23)
- **Phase 2 Features**: Multi-agent orchestration, project management, memory query
- **Phase 2.5 Features**: SDK hooks, streaming, advanced options, system prompts
- **Phase 3 Features**: HOPE architecture (self-modifying kernel, crystallization)

### Version History

| Version | Date | Key Features |
|---------|------|--------------|
| **3.5.0** | 2025-12 | **Adaptive Agents**: DynamicAgentManager, per-query adaptation, agent evolution |
| 3.4.0 | 2025-11 | Sentience Layer: Valence variables, latent modes, homeostasis |
| 3.3.0 | 2025-11 | Advanced Tool Use: PTC, Tool Search, Tool Examples |
| 3.2.0 | 2025-11 | Hybrid Architecture: Markdown agents, self-modification, HOPE |
| 3.1.0 | 2025-11 | Phase 1 Patterns: Config, Strategy, DI |
| 3.0.0 | 2025-11 | Phase 3.0: HOPE Architecture (Crystallization) |
| 2.5.0 | 2025-11 | Phase 2.5: Nested Learning (Semantic Matching) |
| 2.0.0 | 2025-11 | Phase 2.0: Multi-Agent Orchestration |
| 1.0.0 | 2025-11 | Phase 1.0: Learner/Follower Pattern |

**All examples maintain backward compatibility** - examples from v1.0.0 still work in v3.5.0!

---

## 🤝 Contributing Examples

Want to add your own example? Great! Follow this structure:

```
examples/
└── your-example/
    ├── README.md           # Usage instructions
    ├── requirements.txt    # Dependencies
    ├── .env.template      # Environment variables template
    └── main.py            # Entry point
```

Make sure to:
- ✅ Include comprehensive README
- ✅ Add requirements.txt with all dependencies
- ✅ Provide .env.template for configuration
- ✅ Include error handling and helpful messages
- ✅ Document what the example demonstrates
- ✅ Add to this main examples/README.md

---

## 📊 Example Comparison

| Feature | Qiskit Studio | Q-Kids Studio | RoboOS | Demo App |
|---------|--------------|---------------|---------|----------|
| **Version** | v3.5.0 | v3.4.0 | v3.5.0 | v3.5.0 |
| **Type** | Backend application | Educational platform | Robot control system | Rich TUI demo |
| **Adaptive Agents** | ✅ Quantum-optimized | - | ✅ Safety-focused | ✅ Full demo |
| **Complexity** | High (production) | High (kid-safe) | High (safety-critical) | Medium (comprehensive) |
| **Use Case** | Backend replacement | STEM education | Robot control | Presentations |
| **UI** | REST API + `/adaptive` | REST API + Blocks | REST API + WebSocket | Rich terminal UI |
| **Best For** | Production deployment | Educational apps | Robotics | Stakeholder demos |
| **Key Feature** | Token optimization | Kid safety | Safety-driven adaptation | Visual feedback |
| **Agents** | 2 quantum specialists | 2 tutors | 2 (Operator + Safety) | 3-7 per scenario |
| **New Endpoints** | `/adaptive`, `/sentience` | `/sentience` | `/adaptive`, `/sentience` | N/A (CLI) |
| **Target Audience** | Quantum developers | Kids ages 8-12 | Roboticists | Stakeholders, managers |

---

## 🆘 Troubleshooting

**Import errors:**
```
ModuleNotFoundError: No module named 'boot'
```
Solution: Make sure you're running from the correct directory or llmos is in your Python path.

**API Key errors:**
```
Error: ANTHROPIC_API_KEY not set
```
Solution: Export your API key or add it to .env file.

**Permission errors:**
```
Permission denied: ./run.sh
```
Solution: Make script executable with `chmod +x run.sh`

**Token budget exceeded:**
```
BudgetExceededError: Token budget exhausted
```
Solution: Increase token budget when initializing LLMOS or in example configuration.

---

**Happy exploring! 🚀**

For questions or issues, please open a GitHub issue or check the main LLM OS documentation.
