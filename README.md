# LLMunix: Project Aorta

**Quantum Biomedical Signal Processing with Three-Agent Cognitive Architecture**

LLMunix demonstrates the "Cognitive Trinity" approach to complex problem-solving through autonomous AI agents using pure markdown architecture. This repository showcases **Project Aorta** - recreating a university bioengineering project using quantum homomorphic analysis for arterial navigation.

> 🌐 **Part of [Evolving Agents Labs](https://evolvingagentslabs.github.io)** | 🔬 [View All Experiments](https://evolvingagentslabs.github.io#experiments) | 📖 [Project Details](https://evolvingagentslabs.github.io/experiments/llmunix.html)

## 🧬 Project Aorta: Revolutionary Medical Navigation

Project Aorta recreates a university Electronics 4 bioengineering project that aimed to navigate arterial systems without X-ray radiation by analyzing pressure wave echoes from arterial bifurcations. This implementation enhances the original concept using quantum computing techniques.

### The Medical Innovation

**Problem**: Current catheter navigation relies on X-ray imaging, exposing patients and medical staff to radiation during procedures like angioplasty and stent placement.

**Solution**: A radiation-free navigation system using:
- **Catheter length measurement** and insertion point tracking
- **Pressure wave echo analysis** from arterial bifurcations  
- **Homomorphic signal processing** to detect echo delays
- **Anatomical mapping** to correlate echoes with vascular geometry
- **Real-time stenosis detection** for diagnostic capabilities

### Quantum Enhancement

The original classical cepstral analysis is enhanced with quantum computing:
- **Quantum Fourier Transform (QFT)** for enhanced frequency resolution
- **Quantum homomorphic processing** for superior echo separation  
- **Parallel processing** of multiple reflection components
- **Noise resilience** through quantum error correction

## 🧠 Three-Agent Cognitive Architecture

LLMunix implements a "Cognitive Trinity" that mirrors human problem-solving:

### 1. VisionaryAgent 🎯
**Role**: Transforms high-level ideas into detailed scientific narratives
- Creates comprehensive project descriptions with medical context
- Explains real-world applications and clinical significance
- Provides compelling scientific storytelling

### 2. MathematicianAgent 🔬  
**Role**: Develops rigorous mathematical frameworks
- Converts narratives into formal mathematical models
- Defines signal equations: `s(t) = p(t) + α·p(t-τ)`
- Formulates quantum operations: QFT → Log Operator → IQFT

### 3. QuantumEngineerAgent ⚛️
**Role**: Implements executable quantum computing solutions
- Translates mathematical frameworks into working Qiskit code
- Creates quantum circuits for homomorphic analysis
- Validates results against classical baselines

## 🚀 Quick Start Guide

### Prerequisites

- **[Claude Code](https://anthropic.com/claude-code)** installed on your system
- **Git** for repository cloning

### Installation

```bash
# Clone the repository
git clone https://github.com/EvolvingAgentsLabs/llmunix.git
cd llmunix
```

### 1. Initialize the System

**For Unix/Linux/Mac:**
```bash
./setup_agents.sh
```

**For Windows:**
```powershell
powershell -ExecutionPolicy Bypass -File .\setup_agents.ps1
```

This copies agent definitions to `.claude/agents/` making them discoverable by Claude Code.

### 2. Understanding Permission Flags

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

### 3. Boot LLMunix

```bash
claude --dangerously-skip-permissions --verbose "boot llmunix"
```

You'll see the ASCII art welcome message confirming LLMunix is ready.

## 🧪 Example 1: Validate Project Aorta & Generate Qiskit Code

This example demonstrates the complete three-agent pipeline and generates working quantum code:

```bash
claude --dangerously-skip-permissions --verbose "llmunix execute: 'Run the Project Aorta scenario to recreate my university bioengineering project using quantum homomorphic analysis of arterial pressure wave echoes. Use the three-agent cognitive pipeline: visionary-agent creates the project description, mathematician-agent develops the formal framework, and quantum-engineer-agent implements the Qiskit solution. Execute the final quantum implementation and validate results.'"
```

### Expected Execution Flow:

1. **SystemAgent Orchestration**: 
   - Creates `workspace/project_aorta/` directory
   - Initializes state tracking and memory consultation

2. **Stage 1 - Vision (VisionaryAgent)**:
   - Generates comprehensive project description
   - Output: `workspace/project_aorta/project_vision.md`
   - Includes medical context, problem significance, and solution approach

3. **Stage 2 - Theory (MathematicianAgent)**:
   - Transforms vision into rigorous mathematics
   - Output: `workspace/project_aorta/mathematical_framework.md`
   - Defines signal models and quantum operations

4. **Stage 3 - Implementation (QuantumEngineerAgent)**:
   - Creates executable Qiskit implementation
   - Output: `workspace/project_aorta/quantum_aorta_implementation.py`
   - Includes quantum circuit construction and validation

5. **Validation & Execution**:
   - Runs the generated Python/Qiskit code
   - Compares quantum vs classical echo detection
   - Generates performance analysis report

### Expected Output Files:

```
workspace/project_aorta/
├── project_vision.md              # Scientific narrative and context
├── mathematical_framework.md      # Formal mathematical model
├── quantum_aorta_implementation.py # Complete Qiskit code
├── classical_baseline.py          # Classical comparison
├── validation_results.md          # Performance analysis
├── execution_report.md            # Complete pipeline summary
└── state/                         # Execution state tracking
```

## 📝 Example 2: Generate LinkedIn Article

This example creates a professional LinkedIn article about the Project Aorta experiment:

```bash
claude --dangerously-skip-permissions --verbose "llmunix execute: 'Create a compelling LinkedIn article about the Project Aorta experiment. Explain how I recreated my university bioengineering project using AI agents and quantum computing. The article should highlight the innovation of using quantum homomorphic analysis for arterial navigation, the three-agent cognitive architecture (Vision → Theory → Implementation), and the potential medical impact of radiation-free catheter navigation. Include technical details about pressure wave echo analysis and quantum advantages. Make it engaging for both technical and non-technical audiences. Target length: 800-1000 words. Include a call-to-action to visit the GitHub repository.'"
```

### Expected Article Sections:

1. **Hook**: Personal story about university project inspiration
2. **Problem Statement**: X-ray radiation exposure in medical procedures
3. **Original Innovation**: Pressure wave echo analysis for navigation
4. **Quantum Enhancement**: Superior signal processing capabilities
5. **AI Architecture**: Three-agent cognitive pipeline explanation
6. **Technical Innovation**: Homomorphic analysis and QFT implementation
7. **Medical Impact**: Radiation-free procedures and enhanced precision
8. **Future Vision**: Potential for revolutionizing cardiovascular medicine
9. **Call-to-Action**: Link to repository and collaboration invitation

### Article Output:
- `workspace/linkedin_article.md` - Complete article ready for publication
- `workspace/article_summary.md` - Key points and technical highlights
- `workspace/social_media_snippets.md` - Supporting social media content

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
├── .claude/agents/              # Discoverable agent definitions
├── components/agents/           # Source agent implementations
│   ├── VisionaryAgent.md       # Scientific narrative creation
│   ├── MathematicianAgent.md   # Mathematical framework development
│   └── QuantumEngineerAgent.md # Quantum implementation
├── scenarios/
│   └── ProjectAortaScenario.md # Complete scenario definition
├── system/                     # Core LLMunix components
├── workspace/                  # Execution outputs (generated)
└── setup_agents.sh             # Agent initialization script
```

## 🚀 Getting Started

Ready to experience the future of AI-driven research? Run your first Project Aorta experiment:

```bash
# 1. Initialize
./setup_agents.sh

# 2. Boot LLMunix
claude --dangerously-skip-permissions --verbose "boot llmunix"

# 3. Run Project Aorta
claude --dangerously-skip-permissions --verbose "llmunix execute: 'Run the Project Aorta scenario'"
```

## 🌟 About Evolving Agents Labs

This project demonstrates the potential of autonomous AI systems for scientific research and innovation. Project Aorta showcases how AI can enhance and reimagine existing research using cutting-edge quantum computing techniques.

**Key Innovation**: The three-agent cognitive architecture (Vision → Theory → Implementation) mirrors human scientific problem-solving while leveraging AI's computational advantages.

---

*Original Concept: Matias Molinas and Ismael Faro - Evolving Agents Labs*