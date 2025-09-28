# LLMunix: Pure Markdown Operating System Framework

**A Revolutionary Framework for Multi-Project AI Development**

LLMunix is a Pure Markdown Operating System where everything is either an agent or tool defined in markdown documents.

**🎯 QUICK ANSWER**: Use **`qwen_runtime.py`** - the unified script with all features: interactive mode, sequential execution, corrected cepstral analysis, and multiple Project Aorta variants.

LLMunix can run with two different AI engines:
- **Claude Code Runtime**: Professional-grade with Claude 3.5 Sonnet (recommended for complex projects)
- **Qwen Runtime**: Lightweight with Qwen 3 4B model (perfect for local development and learning)

> 🌐 **Part of [Evolving Agents Labs](https://evolvingagentslabs.github.io)** | 🔬 [View All Experiments](https://evolvingagentslabs.github.io#experiments) | 📖 [Framework Details](https://evolvingagentslabs.github.io/experiments/llmunix.html)

## 🏗️ Framework Overview

LLMunix demonstrates autonomous AI agents working together to solve complex problems using pure markdown architecture. The framework supports multiple projects, each with their own specialized agent architectures and workflows.

### Core Architecture

**Pure Markdown Framework**: Everything is either an agent or tool defined in markdown documents
- **Markdown-Driven Execution**: LLM interpreter reads and sends full markdown specifications to LLM for interpretation and execution
- **No Code Generation**: System behavior emerges from LLM interpreting markdown documents sent at runtime
- **Agent/Tool Duality**: Every component is either an agent (decision maker) or tool (executor) defined in markdown
- **Dynamic Creation**: New tools/agents are created as markdown specifications during runtime
- **Flexible Architecture**: Projects can use any number and type of agents suited to their specific needs

### Agent Architecture Flexibility

LLMunix supports any agent configuration that fits your project needs:

**🎯 Single-Agent Projects**: Simple tasks handled by one specialized agent
**🔄 Multi-Agent Pipelines**: Sequential processing through multiple specialized agents
**🌐 Collaborative Networks**: Complex orchestration with multiple agents working in parallel
**🧠 Custom Architectures**: Project-specific agent patterns (e.g., Project Aorta's three-agent cognitive pipeline)

### System vs Project Components

**System Components** (`system/`): Framework-level agents and tools shared across all projects
- **SystemAgent**: Core orchestration and workflow management
- **MemoryAnalysisAgent**: Cross-project learning and pattern recognition
- **QueryMemoryTool**: Framework-level memory consultation
- **ClaudeCodeToolMap**: Integration with Claude Code's native tools

**Project Components** (`projects/[project]/components/`): Project-specific agents and tools
- **Custom Agents**: Tailored to project domain (e.g., VisionaryAgent, QuantumEngineerAgent)
- **Specialized Tools**: Domain-specific functionality (e.g., QuantumComputingTool, WebFetcherTool)
- **Dynamic Creation**: New components created on-demand during project execution

## 🚀 Quick Start Guide

### Prerequisites

- **[Claude Code](https://anthropic.com/claude-code)** installed on your system
- **Git** for repository cloning
- **Python 3.7+** for Qwen Runtime

### Installation

```bash
# Clone the repository
git clone https://github.com/EvolvingAgentsLabs/llmunix.git
cd llmunix
```

## 🎯 Two Ways to Use LLMunix

LLMunix can be used in two powerful ways, depending on your needs and resources:

### Option 1: 🧠 Claude Code Runtime (Recommended)
**Best for**: Professional development, complex projects, maximum capability
- Uses Claude Opus 4.1 (state-of-the-art AI)
- Full integration with native development tools
- Advanced debugging and error handling
- Real-time web access and file operations

### Option 2: 🚀 Qwen Runtime (Self-Hosted)
**Best for**: Local development, minimal resources, learning, experimentation
- Uses Qwen 3 4B model (lightweight, efficient)
- Runs on OpenRouter (free tier) or local Ollama
- Self-contained Python environment
- Minimal hardware requirements

---

## 🚀 Option 1: Claude Code Runtime

### Prerequisites
- **[Claude Code](https://anthropic.com/claude-code)** installed on your system
- **Git** for repository cloning

### Quick Start

```bash
# 1. Clone and initialize
git clone https://github.com/EvolvingAgentsLabs/llmunix.git
cd llmunix

# 2. Initialize agents (one-time setup)
./setup_agents.sh  # Unix/Linux/Mac
# OR
powershell -ExecutionPolicy Bypass -File .\setup_agents.ps1  # Windows

# 3. Boot LLMunix
claude --dangerously-skip-permissions --verbose "boot llmunix"

# 4. Execute projects
claude --dangerously-skip-permissions --verbose "llmunix execute: 'Run the Project Aorta scenario'"
```

---

## 🧠 Option 2: Qwen Runtime (Self-Hosted)

### Prerequisites
- **Python 3.7+**
- **OpenRouter API Key** (free tier available) OR **Ollama** for local hosting

### Quick Start (3 Steps)

```bash
# 1. Install dependencies
pip install openai python-dotenv requests qiskit matplotlib

# 2. Test the system
python test_qwen_runtime.py

# 3. Run Project Aorta demo (default mode)
python qwen_runtime.py
```

### Unified Qwen Runtime

**`qwen_runtime.py`** ⭐ **PURE GENERIC RUNTIME** - No hardcoded solutions:
- ✅ **Interactive Mode**: REPL-like experience for any goal
- ✅ **Generic Goal Execution**: Handles any problem through agent delegation
- ✅ **Agent-Driven Architecture**: Automatically selects and uses appropriate agents
- ✅ **Flexible Problem Solving**: Solves Project Aorta, calculators, research, or any goal
- ✅ **Command Line Flexibility**: Any text becomes an executable goal
- ✅ **Demo Mode**: Architecture testing without API calls

### Usage Modes

**🎯 Command Line Options:**

```bash
# Default: Run Project Aorta (using generic runtime)
python qwen_runtime.py

# Interactive mode with REPL interface
python qwen_runtime.py interactive

# Any goal as command line argument
python qwen_runtime.py "Create a web scraper using Python"
python qwen_runtime.py "Research quantum computing and write a report"
python qwen_runtime.py "Build a machine learning model for sentiment analysis"

# System testing
python qwen_runtime.py demo         # Architecture demo (no API calls)
python qwen_runtime.py test         # Quick functionality test
```

**🎮 Interactive Mode Commands:**
```
🎯 llmunix> help                              # Show all commands
🎯 llmunix> status                            # Check workspace status
🎯 llmunix> demo                              # Architecture demo
🎯 llmunix> clear                             # Clear workspace
🎯 llmunix> Create a Python calculator        # Any goal execution
🎯 llmunix> Execute Project Aorta using quantum cepstral analysis  # Complex projects
🎯 llmunix> Build a REST API with authentication  # Development tasks
🎯 llmunix> exit                              # Quit interactive mode
```

### Alternative: Local Ollama Setup

For completely local execution:

```bash
# Install Ollama (one-time)
curl -fsSL https://ollama.ai/install.sh | sh

# Download Qwen model
ollama pull qwen:4b

# Update qwen_runtime.py to use local endpoint
# Change base_url to "http://localhost:11434/v1"
```

### What's Included

✅ **API Key Configured**: OpenRouter API key ready in `.env`
✅ **Model Selected**: `qwen/qwen3-4b:free` (completely free)
✅ **Tools Ready**: 10+ native Python tools compiled
✅ **Agent System**: Full LLMunix agent architecture
✅ **Project Aorta**: Corrected cepstral analysis implementation

### 📖 Quick Usage Guide

**For Beginners:**
```bash
python qwen_runtime.py demo          # Test without API calls
python qwen_runtime.py test          # Quick functionality test
python qwen_runtime.py interactive   # Explore interactively
```

**For Development:**
```bash
python qwen_runtime.py               # Project Aorta (default example)
python qwen_runtime.py "Create a simple calculator"  # Custom goal
python qwen_runtime.py "Build a web scraper for news" # Development task
```

**For Complex Projects:**
```bash
python qwen_runtime.py "Execute Project Aorta using quantum-enhanced cepstral analysis for arterial navigation"
python qwen_runtime.py "Research quantum computing trends and create a comprehensive technical report"
python qwen_runtime.py "Build a machine learning pipeline for sentiment analysis with data preprocessing"
```

**For Interactive Exploration:**
```bash
python qwen_runtime.py interactive
🎯 llmunix> Create a web scraper for news articles
🎯 llmunix> Build a machine learning model for sentiment analysis
🎯 llmunix> Generate a technical report on quantum computing
🎯 llmunix> Execute Project Aorta using the three-agent pipeline
```

### Example Goals to Try

```python
# Simple tasks
"Create a Python script that generates fibonacci numbers"

# Multi-step projects
"Build a web scraper for news articles with error handling and JSON output"

# Research tasks
"Analyze latest trends in quantum computing and create a summary report"

# Project Aorta (corrected cepstral analysis)
# Automatically runs with: python qwen_runtime.py
```

### Troubleshooting

```bash
# Verify dependencies
pip list | grep -E "(openai|qiskit)"

# Check API key
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key loaded:', bool(os.getenv('OPENROUTER_API_KEY')))"

# Run test suite
python test_qwen_runtime.py
```

---

## 🔧 Advanced Claude Code Configuration

### Understanding Permission Flags

LLMunix requires comprehensive file system access. Use the `--dangerously-skip-permissions` flag to avoid permission prompts:

```bash
# Recommended approach for LLMunix
claude --dangerously-skip-permissions --verbose "boot llmunix"
```

**Why use `--dangerously-skip-permissions`?**
- **Prevents interruptions**: No permission prompts during execution
- **Enables file operations**: Create workspace directories, agent files, and outputs
- **Supports agent evolution**: SystemAgent can create new specialized agents
- **Full functionality**: Access to all LLMunix capabilities

**What it enables:**
- Create and modify files in workspace directory
- Read and write to `.claude/agents/` directory
- Execute shell scripts and quantum simulations
- Access memory logs and state management

**Security note**: Only use with trusted code like LLMunix.

### Boot Process

After setting up permissions, boot LLMunix:

```bash
claude --dangerously-skip-permissions --verbose "boot llmunix"
```

You'll see the ASCII art welcome message confirming LLMunix is ready.

## 🧪 Example Usage: Framework Execution

LLMunix can execute any type of project using the three-agent cognitive pipeline. Here are some examples:

### Example 1: Research and Development Projects

Execute complex research scenarios with autonomous agent coordination:

```bash
claude --dangerously-skip-permissions --verbose "llmunix execute: 'Research the latest developments in [your domain], create a comprehensive analysis, develop a formal framework, and implement a working prototype. Use the three-agent cognitive pipeline for complete end-to-end development.'"
```

### Example 2: Content Generation

Create professional content about your projects:

```bash
claude --dangerously-skip-permissions --verbose "llmunix execute: 'Create compelling content about [your project]. Develop a narrative that explains the innovation, the technical approach, and the potential impact. Make it engaging for both technical and non-technical audiences.'"
```

### Example 3: Project-Specific Execution

For specific projects in the `projects/` directory:

```bash
# Execute Project Aorta (biomedical quantum computing)
claude --dangerously-skip-permissions --verbose "llmunix execute: 'Run the Project Aorta scenario from projects/Project_aorta/'"

# Or any other project in the projects directory
claude --dangerously-skip-permissions --verbose "llmunix execute: 'Execute the project in projects/[project_name]/'"
```

## 🔄 Interactive Development Mode

For iterative development and refinement:

```bash
claude --dangerously-skip-permissions --verbose "./llmunix-llm interactive"
```

In interactive mode you can:
- Refine experiments with `refine` command
- Check execution status with `status`
- View history with `history`  
- Clear workspace with `clear`
- Get help with available commands

### Interactive Session Example:

```
🎯 llmunix> Run Project Aorta with enhanced quantum noise analysis
[Execution completes]

🎯 llmunix> refine
Previous goal: Run Project Aorta with enhanced quantum noise analysis
How would you like to refine this goal?
🔄 refinement> Add error correction protocols and compare with classical performance metrics

🎯 llmunix> status
Workspace: /workspace/project_aorta/
Active agents: quantum-engineer-agent
Files created: 7
Memory entries: 3 experiences logged
```

## 🏗️ How It Works: Pure Markdown Architecture

LLMunix uses a revolutionary pure markdown approach:

### Agent Definitions

All agents are defined as markdown files with YAML frontmatter:

```markdown
---
name: quantum-engineer-agent
description: Translates mathematical frameworks into executable Qiskit implementations
tools: Read, Write, Bash
---

# QuantumEngineerAgent
You are an expert quantum software engineer...
```

### Dynamic Component Creation

The SystemAgent can create new specialized agents during execution:

1. **Gap Analysis**: Identifies missing capabilities needed for task completion
2. **Agent Generation**: Creates new markdown agent definitions with proper YAML
3. **Runtime Integration**: Saves to `.claude/agents/` for immediate discovery
4. **Task Delegation**: Uses new agents via Claude Code's Task tool

### Memory-Driven Learning

Three-tier memory system enables continuous improvement:

- **Volatile Memory**: Temporary execution data
- **Task Memory**: Current goal context and decisions  
- **Permanent Memory**: Long-term patterns and successful strategies

## 🧬 Scientific Foundation

### Cardiovascular Physics

**Echo Formation**: Pressure waves reflect at arterial bifurcations due to impedance mismatches
- Geometric changes (one vessel → two vessels)
- Vessel wall property differences
- Flow dynamics alterations

**Signal Model**: `s(t) = p(t) + α * p(t - τ)`
- `p(t)`: Primary cardiac pressure pulse (~1-2 Hz)
- `α`: Attenuation factor (0 < α < 1)
- `τ`: Echo delay time (proportional to distance)

### Quantum Advantages

**Enhanced Resolution**: QFT provides superior frequency analysis for overlapping echoes
**Parallel Processing**: Quantum superposition enables simultaneous analysis
**Noise Resilience**: Quantum error correction improves signal-to-noise ratio
**Real-time Performance**: Faster processing for time-critical medical procedures

## 🎯 Expected Results

### Technical Outcomes

- **Working Qiskit Implementation**: Complete quantum circuit for homomorphic analysis
- **Validation Results**: Comparison showing quantum vs classical echo detection accuracy
- **Performance Metrics**: Processing time, accuracy, and resource utilization
- **Medical Relevance**: Demonstration of radiation-free navigation feasibility

### Content Outcomes

- **Professional Article**: LinkedIn-ready content highlighting innovation and impact
- **Technical Documentation**: Complete mathematical and implementation details
- **Execution Reports**: Detailed analysis of three-agent cognitive pipeline

## 🔬 Repository Structure

```
llmunix/
├── .claude/agents/              # Discoverable agent definitions (auto-populated)
├── system/                      # Core LLMunix framework components
│   ├── agents/                 # System-wide orchestration agents
│   ├── tools/                  # Framework-level tools
│   └── components/             # Core framework components
├── scenarios/                   # Generic task scenarios
├── projects/                    # Individual projects with their own agents/tools
│   ├── Project_aorta/          # Biomedical quantum computing project
│   │   ├── README.md           # Project documentation
│   │   ├── USAGE_GUIDE.md      # Project-specific usage examples
│   │   ├── components/         # Project-specific components
│   │   │   ├── agents/         # Project agents (VisionaryAgent, etc.)
│   │   │   └── tools/          # Project tools (QuantumComputingTool, etc.)
│   │   ├── input/              # Input docs and instructions
│   │   ├── output/             # Generated outputs
│   │   └── workspace/          # Active workspace
│   └── [Other projects]/       # Additional projects with their own components
├── workspace/                   # Global execution outputs (generated)
└── setup_agents.*              # Agent initialization scripts
```

## 🚀 Getting Started

Ready to experience the power of multi-project AI development? Here's how to get started:

```bash
# 1. Initialize the framework
./setup_agents.sh  # Unix/Linux/Mac
# OR
powershell -ExecutionPolicy Bypass -File .\setup_agents.ps1  # Windows

# 2. Boot LLMunix
claude --dangerously-skip-permissions --verbose "boot llmunix"

# 3. Execute your first project
claude --dangerously-skip-permissions --verbose "llmunix execute: 'Run the Project Aorta scenario from projects/Project_aorta/'"

# 4. Or start your own project
claude --dangerously-skip-permissions --verbose "llmunix execute: '[Describe your project goal here]'"
```

## 🌟 About LLMunix Framework

LLMunix demonstrates the potential of autonomous AI systems for multi-domain research and development. The framework showcases how AI can enhance and reimagine complex projects across different fields using specialized agent architectures.

**Key Innovation**: Flexible agent architectures that can be tailored to any domain, from single-agent solutions to complex multi-agent cognitive pipelines, all defined through pure markdown specifications.

## 📁 Featured Projects

### Project Aorta
**Domain**: Biomedical Engineering & Quantum Computing
**Architecture**: Custom three-agent cognitive pipeline (VisionaryAgent → MathematicianAgent → QuantumEngineerAgent)
**Description**: Recreates a university bioengineering project using quantum homomorphic analysis for radiation-free arterial navigation
**Location**: `projects/Project_aorta/`
**Key Technologies**: Quantum computing, signal processing, medical devices

### Your Project Here
**Domain**: Any field you choose
**Architecture**: Single agent, multi-agent pipeline, or custom pattern
**Description**: LLMunix adapts to your project's specific needs
**Location**: `projects/[your_project]/`
**Key Technologies**: Whatever fits your requirements

*Ready to add your own project? Create a new directory in `projects/` and let LLMunix help you develop it with the optimal agent architecture for your domain!*

---

*Original Concept: Matias Molinas and Ismael Faro - Evolving Agents Labs*