# LLMunix: Pure Markdown Operating System

> **Transform any LLM into an intelligent operating system using pure markdown**

LLMunix is a revolutionary framework where AI agents and tools are defined entirely in markdown documents. No code compilation, no complex APIs - just markdown that any LLM can interpret to become a powerful problem-solving system.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/EvolvingAgentsLabs/llmunix.git
cd llmunix

# Initialize the agent system
./setup_agents.sh    # Mac/Linux
# OR
powershell -ExecutionPolicy Bypass -File .\setup_agents.ps1  # Windows
```

## 🎯 Choose Your Runtime

### Option 1: Claude Code (Recommended)
**Best for:** Production use, complex projects
- Powered by Claude Opus 4.1
- Full tool integration
- Advanced capabilities

```bash
# Boot LLMunix
claude --dangerously-skip-permissions "boot llmunix"

# Execute any goal
claude --dangerously-skip-permissions "llmunix execute: 'Your goal here'"
```

### Option 2: Qwen Runtime (Lightweight)
**Best for:** Learning, development, resource-constrained environments
- Uses Qwen 3 4B model (free tier)
- Minimal resource requirements
- Self-hosted option available

```bash
# Install dependencies
pip install openai python-dotenv

# Run any goal
python qwen_runtime.py "Your goal here"

# Interactive mode
python qwen_runtime.py interactive
```

## 💡 Core Concept

LLMunix treats everything as either an **Agent** (decision maker) or **Tool** (executor), all defined in markdown:

```markdown
---
name: example-agent
description: An agent that solves problems
tools: Read, Write, WebFetch
---

# ExampleAgent
You are an expert problem solver...
```

The framework automatically:
- 🔍 Discovers available agents
- 🎯 Selects the best agent for each task
- 🔄 Delegates work between specialized agents
- 📝 Executes tools based on agent decisions

## 🛠️ What Can You Build?

LLMunix can handle any task by combining its agent ecosystem:

### Research & Analysis
```bash
"Research the latest AI developments and create a comprehensive report"
"Analyze this codebase and suggest improvements"
"Compare different approaches to solving this problem"
```

### Development
```bash
"Create a web application with user authentication"
"Build a data pipeline for processing CSV files"
"Implement a machine learning model for classification"
```

### Content Creation
```bash
"Write a technical blog post about quantum computing"
"Generate documentation for this API"
"Create a tutorial for beginners"
```

### Complex Projects
```bash
"Design and implement a complete system for invoice processing"
"Create a multi-agent research system for market analysis"
"Build a quantum algorithm for signal processing"
```

## 🏗️ Framework Architecture

```
llmunix/
├── system/                 # Core framework
│   ├── agents/            # System-level agents
│   └── tools/             # Framework tools
├── projects/              # Your projects
│   └── [project_name]/    # Project-specific agents
├── workspace/             # Execution outputs
└── qwen_runtime.py        # Lightweight runtime
```

## 🤝 Creating Custom Agents

1. **Define your agent** in markdown:
```markdown
---
name: my-custom-agent
description: Specialized agent for my domain
tools: Read, Write, Bash
---

# MyCustomAgent
You are an expert in [domain]...
```

2. **Place in project folder**: `projects/my_project/components/agents/`

3. **Use it immediately**:
```bash
"Use my-custom-agent to solve this problem"
```

## 📚 Advanced Features

### Interactive Mode
Explore LLMunix capabilities interactively:
```bash
python qwen_runtime.py interactive
> help                    # Show commands
> status                  # Check workspace
> Create a calculator     # Execute any goal
```

### Generic Goal Execution
The runtime interprets natural language goals without hardcoded solutions:
```python
# Any text becomes an executable goal
python qwen_runtime.py "Build a REST API with authentication"
```

### Multi-Agent Collaboration
Agents automatically collaborate on complex tasks:
```
SystemAgent → Breaks down the problem
├── ResearchAgent → Gathers information
├── DesignAgent → Creates architecture
└── ImplementationAgent → Builds solution
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file:
```env
# For Qwen Runtime (OpenRouter)
OPENROUTER_API_KEY=your_key_here

# For local Qwen (Ollama)
OLLAMA_HOST=http://localhost:11434
```

### Local Deployment with Ollama
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Download Qwen model
ollama pull qwen:4b

# Update qwen_runtime.py base_url to localhost:11434
```

## 🌟 Why LLMunix?

- **Pure Markdown**: No code compilation, just markdown interpretation
- **Universal**: Works with any LLM that can read markdown
- **Extensible**: Add new agents and tools without modifying core
- **Transparent**: See exactly what each agent is doing
- **Powerful**: Solve complex problems through agent collaboration

## 📖 Examples

### Simple Task
```bash
python qwen_runtime.py "Create a Python script that generates passwords"
```

### Complex Project
```bash
python qwen_runtime.py "Build a complete web scraping system with scheduling, data storage, and error handling"
```

### Research Task
```bash
python qwen_runtime.py "Research quantum computing applications in medicine and create a detailed report"
```

## 🤔 Getting Help

- **Documentation**: See `projects/` folder for example implementations
- **Issues**: [GitHub Issues](https://github.com/EvolvingAgentsLabs/llmunix/issues)
- **Interactive Help**: Run `python qwen_runtime.py interactive` then type `help`

## 📄 License

Apache License 2.0 - see LICENSE file for details

---

*Built with ❤️ by [Evolving Agents Labs](https://evolvingagentslabs.github.io)*