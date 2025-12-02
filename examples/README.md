# LLM OS - Examples

This directory contains comprehensive examples demonstrating LLM OS capabilities.

## 🌟 NEW: Hybrid Architecture (v3.2.0) - The Flagship Feature

**The future of LLM OS is here**: Markdown-defined agents that the system can create and modify on the fly!

### Hybrid Architecture Demo (`hybrid_architecture_demo.py`)

**The most important example** - demonstrates how LLM OS combines:
- **Markdown Mind**: Agents defined in simple `.md` files (flexibility + self-modification)
- **Python Kernel**: Robust tooling, security, performance (stability)
- **HOPE Pattern**: System writes its own code through crystallization

**What it demonstrates:**
- 📝 **Markdown Agents**: Define agents in `workspace/agents/*.md` (no Python!)
- 🔧 **Self-Modification**: System creates new agents using `create_agent` tool
- 🔄 **Hot-Reloading**: New agents available instantly (no restart)
- 📊 **Agent Management**: List, create, modify agents dynamically
- 🎯 **Example Flow**: Creates a haiku-poet agent and uses it immediately

**Quick Start:**
```bash
python examples/hybrid_architecture_demo.py
```

**5 Interactive Demonstrations:**
1. **List Agents** - See Markdown-defined agents
2. **Create Agent** - System creates haiku-poet agent by writing a file
3. **Use Agent** - Immediately delegate to newly created agent
4. **Modify Agent** - System improves agent capabilities
5. **Inspect Files** - View the actual Markdown files

**Why This Matters:**
- **Self-Modification**: System evolves its own capabilities
- **No Restart**: Changes take effect immediately
- **Human-Readable**: Agents are just Markdown files
- **Version Control**: Track agent evolution in git
- **LLM-Friendly**: System can read/write its own agent definitions

**Full Documentation:** See [../HYBRID_ARCHITECTURE.md](../HYBRID_ARCHITECTURE.md) (531 lines)

**Sample Markdown Agent:**
```markdown
---
name: deep-researcher
description: Expert at web research and data synthesis
tools: ["WebFetch", "Read", "Write", "Bash"]
model: sonnet
---

# Deep Researcher Agent

You are an expert researcher specializing in...
```

---

## 📚 Core Examples

These are the primary examples showcasing LLM OS capabilities:

### 1. Qiskit Studio (`qiskit-studio/`)

**A flagship example** showing LLM OS using the **Hybrid Architecture with Markdown Agents**.

**What it demonstrates:**
- 📝 **Markdown Agents**: Agents defined in `workspace/agents/*.md` files (no Python!)
- 💰 **Cost Reduction**: Learner → Follower caching (100% savings on repeated tasks)
- 🔒 **Enhanced Security**: Multi-layer code execution protection
- 🧠 **Unified Memory**: Cross-project learning and semantic memory
- ⚡ **Simplified Architecture**: Single process replaces 3+ microservices
- 🎨 **API Compatibility**: Works with existing Qiskit Studio frontend

**Quick Start:**
```bash
cd qiskit-studio
./run.sh
```

**Full Documentation:** See [qiskit-studio/README.md](qiskit-studio/README.md)

---

### 2. Demo App (`demo-app/`)

**Rich interactive terminal application** with menu-driven scenarios.

**What it demonstrates:**
- 📊 **7 Real-World Scenarios**: Data pipelines, code generation, research, DevOps, etc.
- 💡 **Cost Analysis**: Detailed cost tracking and savings demonstrations
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
6. **Cost Optimization** - Run same task 5x, show savings
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
- 💰 **Cost Optimization**: Learner → Follower saves 99%+ on repeated hints
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

### 4. RoboOS (`robo-os/`)

**LLM OS as the brain of a robotic arm** - Natural language robot control with multi-layer safety.

**What it demonstrates:**
- 🤖 **Natural Language Control**: Command robots with plain English
- 🛡️ **Multi-Layer Safety**: PreToolUse hook prevents dangerous operations
- 👥 **Multi-Agent Coordination**: Operator + Safety Officer collaboration
- 📹 **State Visualization**: ASCII cockpit view and overhead map
- 💰 **Learner → Follower**: Teach once, replay forever (100% cost savings)
- 🔌 **FastAPI Backend**: Production-ready REST API
- 🌊 **WebSocket Support**: Real-time state updates

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
| **⭐ Understand the Hybrid Architecture** | **Hybrid Architecture Demo** | **The flagship - self-modifying agents, the future** |
| See self-modification in action | **Hybrid Architecture Demo** | Watch the system create its own agents |
| See a production-ready backend | **Qiskit Studio** | Drop-in microservice replacement with FastAPI + Markdown agents |
| Build educational tools for kids | **Q-Kids Studio** | Kid-safe, gamified, adaptive quantum learning |
| Control robots with natural language | **RoboOS** | LLM as robot brain with multi-layer safety |
| Run impressive demos with visuals | **Demo App** | Rich terminal UI, 7 scenarios, perfect for stakeholders |
| Learn about quantum computing | **Qiskit Studio** or **Q-Kids Studio** | Domain-specific quantum agents and tools |
| Understand cost savings | **Qiskit Studio** or **Demo App** | Learner→Follower demo with metrics |
| See multi-agent orchestration | **Demo App (Scenario 1)** or **Qiskit Studio** | Multiple agents collaborating |
| Test security hooks | **RoboOS** or **Demo App (Scenario 4)** | Safety validation in action |
| Build adaptive AI tutors | **Q-Kids Studio** | Professor Q agent with context-aware hints |
| Robot safety systems | **RoboOS** | Workspace bounds, prohibited zones, emergency stop |
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
| **3.2.0** | 2025-11-23 | **Hybrid Architecture**: Markdown agents, self-modification, HOPE |
| 3.1.0 | 2025-11-23 | Phase 1 Patterns: Config, Strategy, DI |
| 3.0.0 | 2025-11-22 | Phase 3.0: HOPE Architecture (Crystallization) |
| 2.5.0 | 2025-11-21 | Phase 2.5: Nested Learning (Semantic Matching) |
| 2.0.0 | 2025-11-20 | Phase 2.0: Multi-Agent Orchestration |
| 1.0.0 | 2025-11-19 | Phase 1.0: Learner/Follower Pattern |

**All examples maintain backward compatibility** - examples from v1.0.0 still work in v3.2.0!

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

| Feature | Hybrid Demo | Qiskit Studio | Q-Kids Studio | RoboOS | Demo App |
|---------|-------------|--------------|---------------|---------|----------|
| **Type** | Core tech demo | Backend application | Educational platform | Robot control system | Rich TUI demo |
| **Complexity** | Low (focused) | High (production) | High (kid-safe) | High (safety-critical) | Medium (comprehensive) |
| **Use Case** | Learn architecture | Backend replacement | STEM education | Robot control | Presentations |
| **Documentation** | In HYBRID_ARCHITECTURE.md | 700+ lines README | 900+ lines README | 800+ lines README | Inline help |
| **UI** | Interactive prompts | REST API | REST API + Blocks | REST API + WebSocket | Rich terminal UI |
| **Lines of Code** | ~260 | ~3,000 | ~2,500 | ~2,000 | ~700 |
| **Best For** | Understanding v3.2.0 | Production deployment | Educational apps | Robotics | Stakeholder demos |
| **Key Feature** | **Self-modification** | Cost optimization | Kid safety | Multi-layer safety | Visual feedback |
| **Agents** | Creates haiku-poet | 2 quantum specialists | 2 tutors | 2 (Operator + Safety) | 3-7 per scenario |
| **Tools** | create_agent, modify_agent | 2 Qiskit tools | 3 kid-safe tools | 7 robot control | Standard toolkit |
| **Target Audience** | Everyone (sci-fi magic!) | Quantum developers | Kids ages 8-12 | Roboticists | Stakeholders, managers |

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

**Budget exceeded:**
```
BudgetExceededError: Remaining budget $0.00
```
Solution: Increase budget when initializing LLMOS or in example configuration.

---

**Happy exploring! 🚀**

For questions or issues, please open a GitHub issue or check the main LLM OS documentation.
