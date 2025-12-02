# LLM OS Examples

This directory contains example applications demonstrating LLM OS v3.4.0 capabilities, including the Sentience Layer, Advanced Tool Use (PTC, Tool Search), and Multi-Agent Orchestration.

## Examples Overview

| Example | Description | Key Features |
|---------|-------------|--------------|
| [Qiskit Studio](#qiskit-studio) | Quantum computing IDE backend | PTC, Tool Search, Sentience Layer |
| [Q-Kids Studio](#q-kids-studio) | Educational quantum computing for kids | Kid-safe execution, Adaptive teaching |
| [RoboOS](#roboos) | LLM-powered robotic arm control | Safety hooks, Multi-agent, Real-time |
| [Demo App](#demo-app) | Comprehensive feature demonstration | All v3.4.0 features, Interactive CLI |

---

## Qiskit Studio

**[View README](qiskit-studio/README.md)**

A flagship example that reimplements the Qiskit Studio backend using LLM OS, demonstrating how a unified operating system can replace multiple specialized microservices.

### Highlights

- **90%+ Cost Savings**: PTC-powered tool replay for repeated patterns
- **Unified Architecture**: Single LLM OS instance replaces 3 microservices
- **Security Hooks**: Built-in protection against malicious code execution
- **Adaptive Behavior**: Sentience Layer adjusts to task patterns
- **Drop-in Compatibility**: Works with existing Qiskit Studio frontend

### Quick Start

```bash
cd examples/qiskit-studio
cp .env.template .env
# Add your ANTHROPIC_API_KEY to .env
./run.sh
```

---

## Q-Kids Studio

**[View README](q-kids-studio/README.md)**

Educational quantum computing platform for ages 8-12, featuring Professor Q (an AI owl tutor) and block-based programming.

### Highlights

- **Kid-Safe Execution**: No raw code execution, simulator-only
- **Block-Based Programming**: Drag-and-drop quantum "spells"
- **Adaptive Teaching**: Professor Q adapts based on Sentience Layer state
- **Gamification**: Badges, levels, and leaderboards
- **6 Progressive Missions**: From coin flips to quantum algorithms

### Quick Start

```bash
cd examples/q-kids-studio
./run.sh
```

---

## RoboOS

**[View README](robo-os/README.md)**

Demonstrates LLM OS as the "brain" of a robotic arm, translating natural language commands into safe, coordinated actions.

### Highlights

- **Natural Language Control**: "Move 30cm to the right"
- **Multi-Layer Safety**: PreToolUse hooks prevent dangerous operations
- **Sentience-Aware**: High safety setpoint (0.8) for robot control
- **Multi-Agent Coordination**: Operator + Safety Officer agents
- **WebSocket Real-time Updates**: Live robot state streaming

### Quick Start

```bash
cd examples/robo-os
./run.sh
```

---

## Demo App

**[View README](demo-app/README.md)**

A comprehensive CLI application showcasing all LLM OS v3.4.0 capabilities through interactive scenarios.

### Highlights

- **Sentience Layer Demo**: Interactive valence and latent mode simulation
- **Nested Learning Demo**: Semantic trace matching with confidence scoring
- **Five Execution Modes**: CRYSTALLIZED, FOLLOWER, MIXED, LEARNER, ORCHESTRATOR
- **Multi-Agent Orchestration**: Data pipelines with coordinated agents
- **Cost Optimization**: 90%+ savings via PTC replay

### Quick Start

```bash
cd examples/demo-app
pip install -r requirements.txt
python demo_main.py
```

### Available Scenarios

1. **Sentience Layer** - Valence variables and latent modes
2. **Nested Learning** - Semantic trace matching
3. **Data Pipeline** - Multi-agent orchestration
4. **Code Generation** - Learner to Follower transition
5. **Cost Optimization** - Token savings demonstration
6. **SDK Hooks** - Security, budget, and trace capture

---

## Architecture Comparison

All examples share the LLM OS Four-Layer Stack:

```
┌─────────────────────────────────────────────────────────────┐
│  SENTIENCE LAYER (v3.4.0)                                   │
│  Valence Variables: safety, curiosity, energy, confidence   │
│  Latent Modes: AUTO_CREATIVE, BALANCED, CAUTIOUS, etc.      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  LEARNING LAYER                                              │
│  Mode Selection: CRYSTALLIZED → FOLLOWER → MIXED → LEARNER  │
│  Semantic Trace Matching + Confidence Scoring                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  EXECUTION LAYER (v3.3.0)                                   │
│  PTC: Zero-context tool replay (90%+ token savings)         │
│  Tool Search: On-demand discovery (85% context reduction)   │
│  Tool Examples: Auto-generated from successful traces       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  SELF-MODIFICATION LAYER                                     │
│  Auto-Crystallization: Patterns become pure Python           │
│  Self-Improvement: System detects optimization opportunities │
└─────────────────────────────────────────────────────────────┘
```

## Sentience Profiles by Example

| Example | Safety | Curiosity | Energy | Rationale |
|---------|--------|-----------|--------|-----------|
| Qiskit Studio | 0.6 | 0.1 | 0.7 | Code safety, moderate exploration |
| Q-Kids Studio | 0.7 | 0.35 | 0.8 | High safety for kids, energetic teaching |
| RoboOS | 0.8 | 0.1 | 0.6 | Maximum safety, precision focus |
| Demo App | 0.5 | 0.3 | 0.7 | Balanced for demonstrations |

---

## Version Requirements

All examples require:
- Python 3.10+
- LLM OS v3.4.0+
- Anthropic API key (or OpenAI for some examples)

---

## Contributing

To add a new example:

1. Create a directory under `examples/`
2. Include a comprehensive `README.md`
3. Add to this file with link and description
4. Ensure it demonstrates v3.4.0 features

---

**Built with LLM OS - The Self-Evolving LLM Operating System**
